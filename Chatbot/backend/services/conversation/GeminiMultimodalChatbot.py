import os
import uuid
import asyncio
from typing import List, Dict, Optional, Any, Union
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema.messages import SystemMessage, HumanMessage, AIMessage
from backend.services.utils.chatmessage import ChatMessage  
from backend.config import API_KEY, CHATBOT_MODEL, MAX_HISTORY, get_gemini, EXA_API_KEY
from backend.services.conversation.session_manager import SessionManager
from backend.services.models.response_types import ChatResponse
from langchain_exa import ExaSearchRetriever
import yaml
from rapidfuzz import fuzz
import json
import base64
from dotenv import load_dotenv
import uuid
import io
import asyncio
from PIL import Image
from backend.services.conversation.tools.article_retriever import article_retriever
from backend.services.conversation.tools.kb_rag import kb_retriever

load_dotenv()
EXA_API = os.getenv("EXA_API")

class GeminiMultimodalChatbot:
    """Multimodal chatbot with history awareness."""

    def __init__(self, session_id=None):
        self.session_id = session_id or str(uuid.uuid4())
        self.model_name = CHATBOT_MODEL
        self.max_history = MAX_HISTORY
        self.exa_api=EXA_API
        self.article_retriever= article_retriever()
        self.kb_retriever=kb_retriever()

        # LLM
        self.llm = get_gemini()

        # Memory
        self.memory = ConversationBufferWindowMemory(
            k=self.max_history, return_messages=True, memory_key="chat_history"
        )

        # Retriever
        self.exa_retriever = ExaSearchRetriever(exa_api_key=self.exa_api, k=5, highlights=True,
                                            livecrawl='fallback')

        # Session + Messages
        self.session_mgr = SessionManager(self.session_id)
        self.chat_messages = []

        # System prompt
        self.system_prompt = self._load_prompt()


        # Load past history
        self._rehydrate_history()


    def _load_prompt(self) -> str:
        """Load system prompt from YAML file."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "../utils/chatbot_prompt.yaml")
        prompt_path = os.path.abspath(prompt_path)

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return data.get("system_prompt", "")
        except FileNotFoundError:
            print(f"Warning: Prompt file not found at {prompt_path}")
            return "You are a helpful AI assistant."
        except Exception as e:
            print(f"Error loading prompt: {e}")
            return "You are a helpful AI assistant."

    
        
    def _prepare(self, image, max_size=(256, 256)):
        '''Encodes image to base64'''
        try:
            with Image.open(image) as img:
                img.thumbnail(max_size)
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                encoded = base64.b64encode(buffer.getvalue()).decode()
            return {"data": encoded}
        except Exception as e:
            print(f"Error processing {image}: {e}")
            return None



    def _rehydrate_history(self):
        for msg in self.session_mgr.load():
            chat_msg = ChatMessage.from_dict(msg)
            self.chat_messages.append(chat_msg)

            if chat_msg.role == "user":
                self.memory.chat_memory.add_user_message(chat_msg.content)
            elif chat_msg.role == "assistant":
                self.memory.chat_memory.add_ai_message(chat_msg.content)


    def _create_multimodal_message(self, text, images, default_mime="image/jpeg"):
        if not images:
            return HumanMessage(content=text)

        content = []
        if text:
            content.append({"type": "text", "text": text})

        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{img.get('mime_type', default_mime)};base64,{img['data']}"}
            })

        return HumanMessage(content=content)




    async def _maybe_retrieve(self, query: str, max_results: int = 5, similarity_threshold: float = 0.7):
        try:
            results, references = [], []

            # 1) Try KB search
            kb_results = await self.kb_retriever.search_kb(query, top_k=max_results, threshold=similarity_threshold)
            kb_found = False

            if kb_results:
                kb_found = True
                for r in kb_results:
                    snippet = (
                        f"- {r['content'].strip()}\n"
                        f"  Similarity: {r['similarity_score']:.3f}\n"
                        f"  Source: {r['title']}"
                    )
                    results.append(snippet)
                    references.append({
                        "title": r["title"],      
                        "content": r["content"]  
                    })
            print(f"🔍 KB search for '{query}' returned {len(kb_results) if kb_results else 0} results")


            # 2) Run Article search and include link references when available
            article_results = await self.article_retriever.get_references(query, max_results=5)
            print(f"🔍 article search for '{query}' returned {len(article_results) if article_results else 0} results")

            if article_results:
                for art in article_results:
                    references.append({
                        "title": art.get("title", "Untitled"),
                        "url": art.get("url"),
                    })

            # ✅ If KB already gave results → return (with article links appended)
            if kb_found:
                return {
                    "context": "\n".join(results),
                    "references": references,
                }

            # 3) If KB empty → fallback to Exa search
            docs = self.exa_retriever.invoke(query)
            scored_docs = []

            for d in docs:
                if not d.page_content:
                    continue
                score = fuzz.partial_ratio(query.lower(), d.page_content.lower()) / 100.0
                if score >= similarity_threshold:
                    scored_docs.append((d, score))

            scored_docs = sorted(scored_docs, key=lambda x: x[1], reverse=True)[:max_results]

            for d, score in scored_docs:
                metadata = d.metadata or {}
                title = metadata.get("title", "Untitled").strip()
                url = metadata.get("url", "").strip()
                highlights = metadata.get("highlights", "N/A")

                link = f"[{title}]({url})" if url else title
                snippet = (
                    f"- {d.page_content.strip()}\n"
                    f"  Highlights: {highlights}\n"
                    f"  Similarity: {score:.3f}\n"
                    f"  Source: {link}"
                )
                results.append(snippet)
                references.append({
                    "title": title,
                    "url": url,
                    "highlights": highlights,
                    "content": d.page_content.strip(),
                    "similarity": score,
                })

            if not results and not article_results:
                return None

            return {
                "context": "\n".join(results),
                "references": references,
            }

        except Exception as e:
            print(f"⚠️ Retrieval error: {e}")
            return None
    async def get_response_async(self, user_input: str, images=None):
        try:
            # Process images
            processed_images = [self._prepare(img) for img in (images or []) if img]
            processed_images = [p for p in processed_images if p]

            # Retrieval (🔹 optional web search)
            retrieved_data = await self._maybe_retrieve(user_input)
            retrieved_context = retrieved_data["context"] if retrieved_data else None
            references = retrieved_data["references"] if retrieved_data else []

            # Create multimodal input
            user_message = self._create_multimodal_message(user_input, processed_images)

            # Prepare messages
            history = self.memory.chat_memory.messages
            messages = [SystemMessage(content=self.system_prompt), *history]

            if retrieved_context:
                messages.append(SystemMessage(content=f"Here are relevant web search results:\n{retrieved_context}"))

            messages.append(user_message)

            response = await asyncio.to_thread(self.llm.invoke, messages)

            final_response = response.content
            if references:  # only if Exa used
                refs_formatted = "\n\n📎 References:\n" + "\n".join(
                    [
                        (f"- [{r.get('title','Untitled')}]({r.get('url')})" if r.get("url") else f"- {r.get('title','Untitled')}")
                        for r in references
                    ]
                )
                final_response += refs_formatted
            # Update memory & history
            self.memory.save_context({"input": user_input}, {"output": final_response})
            user_chat = ChatMessage("user", user_input, [i['data'] for i in processed_images])
            ai_chat = ChatMessage("assistant", final_response)
            self.chat_messages.extend([user_chat, ai_chat])

            # Trim & save
            self.chat_messages = self.chat_messages[-self.max_history * 2:]
            self.session_mgr.save(self.chat_messages)

            return {
                "success": True,
                "response": final_response,
                "session_id": self.session_id,
                "message_id": ai_chat.id,
                "timestamp": ai_chat.timestamp,
                "images_processed": len(processed_images),
                "web_search_used": retrieved_context is not None,
                "references": references  
            }
        except Exception as e:
            return {"success": False, "error": str(e), "session_id": self.session_id}

    def get_response(self, user_input: str, images=None):
        return asyncio.run(self.get_response_async(user_input, images))

    async def stream_response(self, user_input: str, images: Optional[List] = None):
        """
        Stream response tokens as they are generated and accumulate the final response.
        """
        final_response = []
        references = []

        try:
            # Process images
            processed_images = [self._prepare(img) for img in (images or []) if img]
            processed_images = [p for p in processed_images if p]

            # Retrieval (KB → Exa fallback)
            retrieved_data = await self._maybe_retrieve(user_input)
            retrieved_context = retrieved_data["context"] if retrieved_data else None
            references = retrieved_data["references"] if retrieved_data else []

            # Create multimodal input
            user_message = self._create_multimodal_message(user_input, processed_images)

            # Prepare messages
            history = self.memory.chat_memory.messages
            messages = [SystemMessage(content=self.system_prompt), *history]

            if retrieved_context:
                messages.append(
                    SystemMessage(content=f"Here are relevant web search results:\n{retrieved_context}")
                )

            messages.append(user_message)

            # 🔹 Stream from LLM
            async for chunk in self.llm.astream(messages):
                if hasattr(chunk, "content") and chunk.content:
                    # stream token-by-token
                    tokens = chunk.content.split()
                    for token in tokens:
                        final_response.append(token)
                        yield token + " "

            # Add references at the end (if Exa used)
            if references:
                refs_formatted = "\n\n📎 References:\n" + "\n".join(
                    [
                        (f"- [{r.get('title','Untitled')}]({r.get('url')})" if r.get("url") else f"- {r.get('title','Untitled')}")
                        for r in references
                    ]
                )
                final_response.append(refs_formatted)
                yield refs_formatted

        except Exception as e:
            print(f"Error in stream_response: {e}")
            yield f"Error: {str(e)}"
        finally:
            # Save context and history (same as get_response_async)
            full_text = " ".join(final_response).strip()
            if full_text:
                self.memory.save_context({"input": user_input}, {"output": full_text})
                user_chat = ChatMessage("user", user_input, [i["data"] for i in processed_images])
                ai_chat = ChatMessage("assistant", full_text)
                self.chat_messages.extend([user_chat, ai_chat])

                # Trim & persist
                self.chat_messages = self.chat_messages[-self.max_history * 2 :]
                self.session_mgr.save(self.chat_messages)

                self._last_full_response = full_text


    def get_full_response(self) -> str:
        """
        Get the full response after streaming is complete.
        """
        return getattr(self, "_last_full_response", "")
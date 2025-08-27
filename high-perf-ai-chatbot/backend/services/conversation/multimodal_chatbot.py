import os
import json
import base64
import uuid
import io
import asyncio
from PIL import Image
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema.messages import SystemMessage, HumanMessage, AIMessage
from ..utils.chatmessage import ChatMessage
from ....config import API_KEY, CHATBOT_MODEL, MAX_HISTORY, EXA_API_KEY
from langchain_exa import ExaSearchRetriever
from .session_manager import SessionManager
from ..models.gemini_model import get_gemini




class GeminiMultimodalChatbot:
    """Multimodal chatbot with history awareness."""

    def __init__(self, session_id=None):
        self.session_id = session_id or str(uuid.uuid4())
        self.model_name = CHATBOT_MODEL
        self.max_history = MAX_HISTORY
        self.exa_api= "25a0ccbd-511a-4f89-a134-8fd3dcc4dc68"

        # LLM
        self.llm = get_gemini()

        # Memory
        self.memory = ConversationBufferWindowMemory(
            k=self.max_history, return_messages=True, memory_key="chat_history"
        )

        # Retriever
        self.retriever = ExaSearchRetriever(exa_api_key=self.exa_api, k=5, highlights=True,
                                            livecrawl='fallback')

        # Session + Messages
        self.session_mgr = SessionManager(self.session_id)
        self.chat_messages = []

        # System prompt
        self.system_prompt = self._load_prompt()


        # Load past history
        self._rehydrate_history()

    def _load_prompt(self):
        with open("high-perf-ai-chatbot/backend/services/utils/chatbot_prompt.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("system_prompt", "")
        
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




    async def _maybe_retrieve(self, query: str, max_results: int = 5):
        """
        Runs web search with Exa if relevant.
        Returns both formatted context (snippets) and structured references with links.
        """
        try:
            docs = self.retriever.invoke(query)

            if not docs:
                return None

            results = []
            references = []

            for d in docs[:max_results]:
                metadata = d.metadata or {}
                title = metadata.get("title", "Untitled").strip()
                url = metadata.get("url", "").strip()

                # Handle highlights properly (can be str or list)
                raw_highlights = metadata.get("highlights", "")
                if isinstance(raw_highlights, list):
                    highlights = " | ".join(h.strip() for h in raw_highlights if isinstance(h, str))
                else:
                    highlights = str(raw_highlights).strip()

                # Markdown formatted reference
                link = f"[{title}]({url})" if url else title

                snippet = (
                    f"- {d.page_content.strip()}\n"
                    f"  Highlights: {highlights or 'N/A'}\n"
                    f"  Source: {link}"
                )
                results.append(snippet)

                references.append({
                    "title": title,
                    "url": url,
                    "highlights": highlights,
                    "content": d.page_content.strip()
                })

            return {
                "context": "\n".join(results),
                "references": references
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

            # LLM response
            response = await asyncio.to_thread(self.llm.invoke, messages)

            # Append references automatically
            final_response = response.content
            if references:
                refs_formatted = "\n\n📎 References:\n" + "\n".join(
                    [f"- [{r['title']}]({r['url']})" if r["url"] else f"- {r['title']}" for r in references]
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
import os
import uuid
import asyncio
from typing import List, Dict, Optional, Any, Union
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema.messages import SystemMessage, HumanMessage, AIMessage
from services.utils.chatmessage import ChatMessage  
from config import API_KEY, CHATBOT_MODEL, MAX_HISTORY
from services.conversation.session_manager import SessionManager
from services.conversation.KnowledgeRetriever import KnowledgeRetriever
from services.conversation.PromptLoader import PromptLoader
from services.conversation.MessageBuilder import MessageBuilder
from services.conversation.ImageProcessor import ImageProcessor
from services.models.response_types import ChatResponse


class GeminiMultimodalChatbot:
    """
    Multimodal chatbot with history awareness, knowledge retrieval, and web search.
    
    Features:
    - Conversation history management
    - Image processing and multimodal input
    - Knowledge base search with web search fallback
    - Session persistence
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.model_name = CHATBOT_MODEL
        self.max_history = MAX_HISTORY

        # Initialize components
        self._init_llm()
        self._init_memory()
        self._init_retriever()
        self._init_session()
        self._load_system_prompt()
        
        # Load conversation history
        self._rehydrate_history()

    def _init_llm(self):
        """Initialize Gemini without streaming."""
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=API_KEY,
            temperature=0.7,
        )

    def _init_memory(self):
        """Initialize conversation memory."""
        self.memory = ConversationBufferWindowMemory(
            k=self.max_history, 
            return_messages=True, 
            memory_key="chat_history"
        )

    def _init_retriever(self):
        """Initialize knowledge retriever."""
        # Use environment variable or fallback
        exa_api_key = os.getenv('EXA_API_KEY', "25a0ccbd-511a-4f89-a134-8fd3dcc4dc68")
        self.retriever = KnowledgeRetriever(exa_api_key)

    def _init_session(self):
        """Initialize session management."""
        self.session_mgr = SessionManager(self.session_id)
        self.chat_messages = []

    def _load_system_prompt(self):
        """Load system prompt and create system message."""
        self.system_prompt = PromptLoader.load_system_prompt()
        self.system_message = SystemMessage(content=self.system_prompt)

    def _rehydrate_history(self):
        """Load and restore conversation history from session."""
        for msg in self.session_mgr.load():
            chat_msg = ChatMessage.from_dict(msg)
            self.chat_messages.append(chat_msg)

            if chat_msg.role == "user":
                self.memory.chat_memory.add_user_message(chat_msg.content)
            elif chat_msg.role == "assistant":
                self.memory.chat_memory.add_ai_message(chat_msg.content)

    def _build_message_chain(self, 
                           user_message: HumanMessage, 
                           retrieved_context: Optional[str]) -> List[Union[SystemMessage, HumanMessage, AIMessage]]:
        """Build the complete message chain for the LLM."""
        history = self.memory.chat_memory.messages
        messages = [self.system_message, *history]

        if retrieved_context:
            context_message = SystemMessage(
                content=f"Here are relevant search results:\n{retrieved_context}"
            )
            messages.append(context_message)

        messages.append(user_message)
        return messages

    def _format_response_with_references(self, 
                                       response: str, 
                                       references: List[Dict]) -> str:
        """Format the final response with references if available."""
        if not references:
            return response

        refs_formatted = "\n\n📎 References:\n" + "\n".join([
            f"- [{ref['title']}]({ref['url']})" if ref.get("url") 
            else f"- {ref['title']}" 
            for ref in references
        ])
        
        return response + refs_formatted

    def _update_conversation_state(self, 
                                 user_input: str, 
                                 final_response: str, 
                                 processed_images: List[Dict[str, str]]):
        """Update memory and chat messages with new conversation turn."""
        # Update memory
        self.memory.save_context(
            {"input": user_input}, 
            {"output": final_response}
        )

        # Create chat messages
        user_chat = ChatMessage(
            "user", 
            user_input, 
            [img['data'] for img in processed_images]
        )
        ai_chat = ChatMessage("assistant", final_response)
        
        # Add to chat history
        self.chat_messages.extend([user_chat, ai_chat])

        # Trim history and save
        self.chat_messages = self.chat_messages[-self.max_history * 2:]
        self.session_mgr.save(self.chat_messages)
        
        return ai_chat

    async def get_response_async(self, 
                               user_input: str, 
                               images: Optional[List] = None) -> Dict[str, Any]:
        """
        Get complete async response from the chatbot.
        
        Args:
            user_input: User's text input
            images: Optional list of images
            
        Returns:
            ChatResponse as dictionary
        """
        try:
            # Process images
            processed_images = ImageProcessor.process_images(images)

            # Retrieve relevant context
            retrieval_result = await self.retriever.retrieve_context(user_input)
            retrieved_context = retrieval_result.context if retrieval_result else None
            references = retrieval_result.references if retrieval_result else []

            # Create user message
            user_message = MessageBuilder.create_multimodal_message(
                user_input, processed_images
            )

            # Build message chain
            messages = self._build_message_chain(user_message, retrieved_context)

            # Get LLM response
            response = await asyncio.to_thread(self.llm.invoke, messages)

            # Format final response
            final_response = self._format_response_with_references(
                response.content, references
            )

            # Update conversation state
            ai_chat = self._update_conversation_state(
                user_input, final_response, processed_images
            )

            return ChatResponse(
                success=True,
                response=final_response,
                session_id=self.session_id,
                message_id=ai_chat.id,
                timestamp=ai_chat.timestamp,
                images_processed=len(processed_images),
                web_search_used=retrieved_context is not None,
                references=references,
                is_streaming=False
            ).__dict__

        except Exception as e:
            print(f"Error in get_response_async: {e}")
            return ChatResponse(
                success=False,
                error=str(e),
                session_id=self.session_id
            ).__dict__

    def get_response(self, user_input: str, images: Optional[List] = None) -> Dict[str, Any]:
        """
        Synchronous wrapper for get_response_async.
        
        Args:
            user_input: User's text input
            images: Optional list of images
            
        Returns:
            ChatResponse as dictionary
        """
        return asyncio.run(self.get_response_async(user_input, images))

    # Utility methods for external access
    def get_session_id(self) -> str:
        """Get the current session ID."""
        return self.session_id

    def get_chat_history(self) -> List[ChatMessage]:
        """Get the current chat history."""
        return self.chat_messages.copy()

    def clear_history(self):
        """Clear conversation history."""
        self.chat_messages.clear()
        self.memory.clear()
        self.session_mgr.save(self.chat_messages)

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of current memory state."""
        return {
            "total_messages": len(self.chat_messages),
            "memory_messages": len(self.memory.chat_memory.messages),
            "session_id": self.session_id,
            "max_history": self.max_history
        }

    async def stream_response(self, user_input: str, images: Optional[List] = None):
        """
        Stream response tokens as they are generated and accumulate the final response.
        """
        final_response = []

        try:
            # Process images if provided
            processed_images = []
            if images:
                processed_images = await self.image_processor.process_images(images)

            # Build message chain (note: your current version mistakenly passes user_input directly)
            user_message = MessageBuilder.create_multimodal_message(user_input, processed_images)
            messages = self._build_message_chain(user_message, None)

            # Get streaming response from LLM
            async for chunk in self.llm.astream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    tokens = chunk.content.split()
                    for token in tokens:
                        final_response.append(token)
                        yield token + " "

        except Exception as e:
            print(f"Error in stream_response: {e}")
            yield f"Error: {str(e)}"
        finally:
            # Save the full response after streaming
            self._last_full_response = " ".join(final_response).strip()

    def get_full_response(self) -> str:
        """
        Get the full response after streaming is complete.
        """
        return getattr(self, "_last_full_response", "")
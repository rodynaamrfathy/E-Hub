import os
import json
import base64
import uuid
from PIL import Image
import io
from datetime import datetime
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, BaseMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema.messages import SystemMessage
from chatmessage import ChatMessage
from chatbot_config import API_KEY , CHATBOT_MODEL, MAX_HISTORY

class GeminiMultimodalChatbot:
    """multimodal chatbot with history awareness"""
    def __init__(self, max_history= 20, session_id = None):

        self.model_name = CHATBOT_MODEL
        self.max_history = MAX_HISTORY
        self.session_id = str(uuid.uuid4())
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True
        )
        
        # Initialize memory for conversation history
        self.memory = ConversationBufferWindowMemory(
            k=max_history,
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Chat history for serialization
        self.chat_messages = []
        
        # System prompt
        self.system_prompt = """You are a helpful AI assistant powered by Google's Gemini model. 
        You can understand and respond to text, analyze images, and maintain context from our conversation history.
        Be helpful, informative, and engaging in your responses. Keep responses concise but comprehensive."""
    


    def prepare_image(self, image, max_size=(256,256)):
        """Prepare image data (from file path or dict) as base64 + resized for efficiency"""
        
        if isinstance(image, str) and os.path.isfile(image):
            try:
                # Open and resize
                with Image.open(image) as img:
                    img.thumbnail(max_size)  # keeps aspect ratio
                    buffer = io.BytesIO()
                    img.save(buffer, format=img.format or "JPEG")
                    encoded = base64.b64encode(buffer.getvalue()).decode()
                return {"data": encoded}
            except Exception as e:
                print(f"Error processing image {image}: {e}")
                return None

        if isinstance(image, dict) and "data" in image:
            data = image["data"].split(",", 1)[-1]
            return {"data": data}

        return None



    def create_multimodal_message(self, text, images, default_mime="image/jpeg"):
        """Create a multimodal message with text and optional images (supports multiple mime types)"""
        
        if not images:
            return HumanMessage(content=text)
        
        content = []
        
        # Add text content
        if text:
            content.append({"type": "text", "text": text})
        
        # Add image content
        for image_data in images:
            mime_type = image_data.get("mime_type", default_mime) 
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_data['data']}"
                }
            })
        
        return HumanMessage(content=content)

    
    async def get_response_async(self, user_input: str, images = None) :
        """
        Get async response from the chatbot with optional images
        
        Args:
            user_input: Text input from user
            images: List of image file paths or base64 encoded image data
            
        Returns:
            Dict containing response and metadata
        """
        try:
            # Process images
            processed_images = []
            if images:
                for image in images:
                    if isinstance(image, str):
                        # Assume it's a file path
                        encoded_image = self.prepare_image(image)
                        if encoded_image:
                            processed_images.append(encoded_image)
                    elif isinstance(image, dict):
                        # Assume it's already processed image data
                        processed_images.append(image)
            
            # Create multimodal message
            user_message = self.create_multimodal_message(user_input, processed_images)
            
            # Get conversation history
            history = self.memory.chat_memory.messages
            
            # Prepare messages for the model
            messages = [SystemMessage(content=self.system_prompt)]
            messages.extend(history)
            messages.append(user_message)
            
            # Get response from model 
            response = await asyncio.to_thread(self.llm.invoke, messages)
            
            # Save to memory
            self.memory.save_context(
                {"input": user_input}, 
                {"output": response.content}
            )
            
            # Create chat messages for history
            user_chat_msg = ChatMessage("user", user_input, [img.get('data', '') for img in processed_images])
            ai_chat_msg = ChatMessage("assistant", response.content)
            
            self.chat_messages.extend([user_chat_msg, ai_chat_msg])
            
            # Trim chat messages if too long
            if len(self.chat_messages) > self.max_history * 2:
                self.chat_messages = self.chat_messages[-self.max_history * 2:]
            
            return {
                "success": True,
                "response": response.content,
                "session_id": self.session_id,
                "message_id": ai_chat_msg.id,
                "timestamp": ai_chat_msg.timestamp,
                "images_processed": len(processed_images)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": self.session_id
            }
    
    def get_response(self, user_input: str, images= None) :
        """Synchronous wrapper for get_response_async"""
        return asyncio.run(self.get_response_async(user_input, images))
    
    def clear_history(self):
        """Clear conversation history"""
        self.memory.clear()
        self.chat_messages.clear()
    
    def get_chat_history(self) :
        """Get formatted chat history"""
        return [msg.to_dict() for msg in self.chat_messages]
    
    def save_session(self, filepath: str):
        """Save current session to file"""
        session_data = {
            "session_id": self.session_id,
            "model_name": self.model_name,
            "messages": self.get_chat_history(),
            "created_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

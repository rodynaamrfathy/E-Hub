import asyncio
from typing import Optional, Dict, Any

from services.conversation.multimodal_chatbot import GeminiMultimodalChatbot


class ConversationRouter:
    """Lightweight router to handle inbound chat messages and delegate to the chatbot.

    Extend here to add intent detection, command handling, tool routing, etc.
    """

    def __init__(self):
        self.chatbot = GeminiMultimodalChatbot()

    async def handle_text(self, text: str) -> Dict[str, Any]:
        """Process a plain text message and return a structured result.

        Returns a dict in the same shape as GeminiMultimodalChatbot.get_response_async.
        """
        return await self.chatbot.get_response_async(text)

    def handle_text_sync(self, text: str) -> Dict[str, Any]:
        return asyncio.run(self.handle_text(text))



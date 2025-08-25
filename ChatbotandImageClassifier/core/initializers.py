# core/initializers.py
"""
Global AI instances
Separated to avoid circular imports between main.py and routes
"""

from ChatbotService.multimodal_chatbot import GeminiMultimodalChatbot

# ----------------------------------------------------
# Global AI instances (singleton pattern)
# ----------------------------------------------------
chatbot = GeminiMultimodalChatbot()
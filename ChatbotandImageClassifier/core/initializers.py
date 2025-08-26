# core/initializers.py
"""
Global AI instances
Separated to avoid circular imports between main.py and routes
"""

from ChatbotService.multimodal_chatbot import GeminiMultimodalChatbot
from agents.waste_mangment_agent.core.agent import WasteManagementAgent

# ----------------------------------------------------
# Global AI instances (singleton pattern)
# ----------------------------------------------------
chatbot = GeminiMultimodalChatbot()
agent = WasteManagementAgent(region="egypt")
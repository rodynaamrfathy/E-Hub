# models/gemini_model.py
from langchain_google_genai import ChatGoogleGenerativeAI
from ChatbotService.config.chatbot_config import API_KEY, CHATBOT_MODEL

def get_gemini():
    return ChatGoogleGenerativeAI(
        model=CHATBOT_MODEL,
        google_api_key=API_KEY,
        temperature=0.1
    )

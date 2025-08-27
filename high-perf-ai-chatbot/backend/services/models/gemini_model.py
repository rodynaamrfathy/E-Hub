from langchain_google_genai import ChatGoogleGenerativeAI
from ....config import CHATBOT_MODEL,API_KEY

def get_gemini():
    return ChatGoogleGenerativeAI(
        model=CHATBOT_MODEL,
        google_api_key=API_KEY,
        temperature=0.1
    )

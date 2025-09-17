
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# API Keys
API_KEY = os.getenv("API_KEY") or os.getenv("GOOGLE_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# LangSmith Configuration
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "Dawar")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")

# Chatbot Configuration
CHATBOT_MODEL = os.getenv("CHATBOT_MODEL", "gemini-2.5-pro")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "50"))

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("NEON_DATABASE_URL")
DATABASE_URL_mcp_test = os.getenv("DATABASE_URL_mcp_test") or os.getenv("NEON_DATABASE_URL")

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

def get_gemini():
    return ChatGoogleGenerativeAI(
        model=CHATBOT_MODEL,
        google_api_key=API_KEY,
        temperature=0.1,
    )

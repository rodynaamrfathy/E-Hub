#API_KEY="AIzaSyDpLH0MjHqlJ0PtL0ertJqqSuSDlmusUi4"
#API_KEY="AIzaSyCUXn2DwojUZqsxoqiaoibQsWJaMEOmEuQ"
#API_KEY="AIzaSyDVRdB4QCj_PxSSsaJtRZClxPRWHlHZg_Y"
#API_KEY="AIzaSyDB865pK1DM_glVjePxqPAhy2pkUav3PXk"
#API_KEY="AIzaSyBh5lsOXgjr90ZiJqQXXtYhTai9gGFX8pE"
API_KEY="AIzaSyCbI-EVNpCNfLtcsjyYezh4XU-9nkCcqOQ"
CHATBOT_MODEL="gemini-2.5-pro"
MAX_HISTORY=50
EXA_API_KEY ="25a0ccbd-511a-4f89-a134-8fd3dcc4dc68"
DATABASE_URL='postgresql://neondb_owner:npg_YhJoUDEH61TF@ep-empty-poetry-adnc151z-pooler.c-2.us-east-1.aws.neon.tech/Dawar?sslmode=require&channel_binding=require'
DATABASE_URL_mcp_test='postgresql://neondb_owner:npg_YhJoUDEH61TF@ep-empty-poetry-adnc151z-pooler.c-2.us-east-1.aws.neon.tech/Dawar?sslmode=require&channel_binding=require'
LANGSMITH_API_KEY="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"
LANGSMITH_PROJECT="Dawar"
LANGCHAIN_TRACING_V2="true"

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

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

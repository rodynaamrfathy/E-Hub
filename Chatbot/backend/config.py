
"""
Production-ready configuration management for the FastAPI Lambda application.
Handles environment variables, validation, and service initialization.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file (if present)
load_dotenv()

logger = logging.getLogger(__name__)

# Environment Detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"
IS_LAMBDA = bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

# API Keys with validation
API_KEY = os.getenv("API_KEY") or os.getenv("GOOGLE_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# Validate critical API keys in production
if IS_PRODUCTION and not API_KEY:
    logger.error("❌ GOOGLE_API_KEY is required in production")
    raise ValueError("Missing required API key: GOOGLE_API_KEY")

# LangSmith Configuration
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "Dawar")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")

# Chatbot Configuration
CHATBOT_MODEL = os.getenv("CHATBOT_MODEL", "gemini-2.5-pro")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "50"))

# Database Configuration with validation
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("NEON_DATABASE_URL")
DATABASE_URL_mcp_test = os.getenv("DATABASE_URL_mcp_test") or os.getenv("NEON_DATABASE_URL")

if IS_PRODUCTION and not DATABASE_URL:
    logger.error("❌ DATABASE_URL is required in production")
    raise ValueError("Missing required database URL")

# Security Configuration
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Performance Configuration
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if IS_PRODUCTION else "DEBUG").upper()

def get_gemini() -> Optional[ChatGoogleGenerativeAI]:
    """
    Create and return a configured Gemini chat instance.
    Returns None if API key is not available.
    """
    if not API_KEY:
        logger.warning("⚠️ Google API key not available, Gemini chat will be disabled")
        return None
        
    try:
        return ChatGoogleGenerativeAI(
            model=CHATBOT_MODEL,
            google_api_key=API_KEY,
            temperature=0.1,
        )
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini chat: {e}")
        if IS_PRODUCTION:
            raise
        return None

def validate_configuration() -> bool:
    """
    Validate all required configuration values.
    Returns True if configuration is valid, False otherwise.
    """
    errors = []
    
    # Check required API keys
    if IS_PRODUCTION:
        if not API_KEY:
            errors.append("GOOGLE_API_KEY is required")
        if not DATABASE_URL:
            errors.append("DATABASE_URL is required")
    
    # Check database URL format
    if DATABASE_URL and not DATABASE_URL.startswith(('postgresql://', 'postgres://')):
        errors.append("DATABASE_URL must be a valid PostgreSQL connection string")
    
    # Log validation results
    if errors:
        for error in errors:
            logger.error(f"❌ Configuration error: {error}")
        return False
    
    logger.info("✅ Configuration validation passed")
    return True

# Validate configuration on import
if not validate_configuration():
    if IS_PRODUCTION:
        raise ValueError("Invalid configuration - see logs for details")

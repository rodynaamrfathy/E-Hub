import os
from pathlib import Path

class Config:
    """Configuration settings for the waste management agent"""
    
    # Base paths
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent
    PROJECT_ROOT: Path = ROOT_DIR 
    DATA_DIR: Path = PROJECT_ROOT / "data"
    CACHE_DIR: Path = PROJECT_ROOT / "cache"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    KNOWLEDGE_BASE_DIR = ROOT_DIR / "knowledge_base"
    
    # API Keys
    EXA_API_KEY = os.getenv("EXA_API_KEY", "7b2f3660-a49f-45be-b6ff-ee4d02668f7b")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCZqvIhnBATPBu-WS9bJJ4BL8tlC0LRSR0")
    
    # Model settings
    OLLAMA_MODEL = "llama3:8b"
    classification_model= "gemini-2.5-pro"
    GEMINI_MODEL="gemini-2.5-pro"
    
    # Default settings
    DEFAULT_REGION = "egypt"
    DEFAULT_CITY = "cairo"
    MAX_SEARCH_RESULTS = 5
    
    @classmethod
    def get_knowledge_file(cls, filename: str) -> Path:
        """Get path to knowledge base file"""
        return cls.KNOWLEDGE_BASE_DIR / filename
    
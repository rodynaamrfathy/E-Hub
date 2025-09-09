from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ChatResponse:
    """Structured response from the chatbot."""
    success: bool
    response: Optional[str] = None
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    timestamp: Optional[str] = None
    images_processed: int = 0
    web_search_used: bool = False
    references: List[Dict] = None
    error: Optional[str] = None
    is_streaming: bool = False

    def __post_init__(self):
        if self.references is None:
            self.references = []


@dataclass
class RetrievalResult:
    """Structured result from knowledge retrieval."""
    context: str
    references: List[Dict]

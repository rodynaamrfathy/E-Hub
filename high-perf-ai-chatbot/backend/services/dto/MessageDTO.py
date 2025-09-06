from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from services.dto.ImageDTO import ImageDTO

class MessageCreateDTO(BaseModel):
    content: str

class MessageHistoryDTO(BaseModel):
    role: str  # "user" or "assistant"
    timestamp: datetime
    type: str  # "text" or "image"
    content: Optional[str] = None
    images: Optional[List[ImageDTO]] = None

class MessageResponseDTO(BaseModel):
    msg_id: UUID
    conv_id: UUID
    sender: str
    content: str
    created_at: datetime

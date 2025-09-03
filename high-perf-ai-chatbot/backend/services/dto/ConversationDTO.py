from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class ConversationCreateDTO(BaseModel):
    title: Optional[str] = None

class ConversationResponseDTO(BaseModel):
    conv_id: UUID
    title: Optional[str]
    created_at: datetime

class ConversationListDTO(BaseModel):
    conv_id: UUID
    title: Optional[str]
    updated_at: datetime

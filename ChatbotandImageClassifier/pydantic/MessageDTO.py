from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    msg_id: UUID
    conv_id: UUID
    sender: str
    content: str
    created_at: Optional[datetime] = None

class MessageHistoryItem(BaseModel):
    msg_id: UUID
    sender: str
    content: str
    created_at: datetime
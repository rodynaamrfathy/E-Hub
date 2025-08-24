from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class ConversationCreate(BaseModel):
    title: Optional[str] = None

class ConversationListItem(BaseModel):
    conv_id: UUID
    title: Optional[str]
    updated_at: datetime

class ConversationResponse(BaseModel):
    conv_id: UUID
    title: Optional[str]
    created_at: datetime

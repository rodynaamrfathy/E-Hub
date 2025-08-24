from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class ImageUploadResponse(BaseModel):
    image_id: UUID
    msg_id: UUID
    mime_type: str

class ImageClassificationResponse(BaseModel):
    classification_id: UUID
    image_id: UUID
    label: str
    recycle_instructions: str
    classified_at: Optional[datetime] = None

class ImageHistoryItem(BaseModel):
    image_id: UUID
    msg_id: UUID
    label: str
    recycle_instructions: str
    created_at: datetime

class ImageDetailResponse(BaseModel):
    image_base64: str
    label: str
    recycle_instructions: str
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class ImageDTO(BaseModel):
    image_id: UUID
    mime_type: str
    image_base64: str

class ImageUploadResponseDTO(BaseModel):
    image_id: UUID
    msg_id: UUID
    mime_type: str

class ImageDetailDTO(BaseModel):
    image_base64: str
    label: str
    recycle_instructions: str

class ImageHistoryDTO(BaseModel):
    image_id: UUID
    msg_id: UUID
    label: str
    recycle_instructions: str
    created_at: datetime

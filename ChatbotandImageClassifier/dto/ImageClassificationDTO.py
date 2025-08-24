from uuid import UUID
from pydantic import BaseModel

class ImageClassificationCreateDTO(BaseModel):
    image_id: UUID
    label: str
    recycle_instructions: str

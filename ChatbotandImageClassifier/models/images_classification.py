from sqlalchemy import ARRAY, Column, Enum, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from .base import Base

class ImageClassification(Base):
    __tablename__ = "image_classifications"
    __table_args__ = {"schema": "public"}

    classification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("public.images.image_id", ondelete="CASCADE"))
    label = Column(String(50))  # plastic, glass, organic, etc.
    #confidence = Column(String(10))  # e.g. "0.97"
    recycle_instructions = Column(Text)
    classified_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    image = relationship("Image", back_populates="classification")

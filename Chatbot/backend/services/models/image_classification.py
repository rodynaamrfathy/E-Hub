from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base

class ImageClassification(Base):
    __tablename__ = "image_classifications"
    __table_args__ = {"schema": "public"}

    classification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("public.images.image_id", ondelete="CASCADE"))
    label = Column(String(255))  # e.g., "plastic bottle", "glass jar", "paper"
    confidence = Column(String(10))  # e.g., "0.95"
    recycle_instructions = Column(Text)  # Instructions on how to recycle this item
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    image = relationship("Image", back_populates="classification")

    def __repr__(self):
        return f"<ImageClassification(classification_id={self.classification_id}, label={self.label}, confidence={self.confidence})>"

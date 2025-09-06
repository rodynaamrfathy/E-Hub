from sqlalchemy import ARRAY, Column, Enum, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from .base import Base

class Image(Base):
    __tablename__ = "images"
    __table_args__ = {"schema": "public"}

    image_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    msg_id = Column(UUID(as_uuid=True), ForeignKey("public.messages.msg_id", ondelete="CASCADE"))
    mime_type = Column(String(50))
    image_base64 = Column(Text)  # or URL if stored in S3/Cloud
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    message = relationship("Message", back_populates="images")
    classification = relationship("ImageClassification", back_populates="image", uselist=False)

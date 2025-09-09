from sqlalchemy import CheckConstraint, Column, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from .base import Base

class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = (
        CheckConstraint("sender IN ('user', 'assistant')", name="sender_check"),
        {'schema': 'public'}
    )

    msg_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    conv_id = Column(UUID(as_uuid=True), ForeignKey("public.conversations.conv_id", ondelete="CASCADE"))
    sender = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=func.current_timestamp(),
        server_default=func.current_timestamp()
    )

    # Relationship
    conversation = relationship("Conversation", back_populates="messages")
    images = relationship("Image", back_populates="message", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Message(msg_id={self.msg_id}, conv_id={self.conv_id}, sender={self.sender})>"
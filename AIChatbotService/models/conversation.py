from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from .base import Base

class Conversation(Base):
    __tablename__ = 'conversations'
    __table_args__ = {'schema': 'public'}

    conv_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.user_id", ondelete="CASCADE"))
    title = Column(Text)
    created_at = Column(
        DateTime(timezone=True),
        default=func.current_timestamp(),
        server_default=func.current_timestamp()
    )

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    strategies = relationship("ConversationStrategy", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(conv_id={self.conv_id}, user_id={self.user_id}, title={self.title})>"


from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from .base import Base

class Conversation(Base):
    __tablename__ = 'conversations'
    __table_args__ = {'schema': 'public'}
    
    conversation_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )
    user_id = Column(UUID(as_uuid=True))
    session_id = Column(String(255))
    title = Column(String(255))
    created_at = Column(
        DateTime(timezone=True), 
        default=func.current_timestamp(),
        server_default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime(timezone=True), 
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __init__(self, user_id=None, session_id=None, title=None):
        self.user_id = user_id
        self.session_id = session_id
        self.title = title
        self.messages = []

    def __repr__(self):
        return f"<Conversation(conversation_id={self.conversation_id}, user_id={self.user_id}, session_id={self.session_id}, title={self.title})>"

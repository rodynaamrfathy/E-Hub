from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from .base import Base

class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = {'schema': 'public'}
    
    message_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )
    conversation_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('public.conversations.conversation_id', ondelete='CASCADE'),
        nullable=False
    )
    message_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    msg_metadata = Column(JSONB, default=dict, server_default='{}')
    created_at = Column(
        DateTime(timezone=True), 
        default=func.current_timestamp(),
        server_default=func.current_timestamp()
    )
    
    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")

    def __init__(self, message_type, content, msg_metadata=None):
        self.message_type = message_type
        self.content = content
        self.msg_metadata = msg_metadata if msg_metadata is not None else {}

    def __repr__(self):
        return f"<Message(message_id={self.message_id}, conversation_id={self.conversation_id}, message_type={self.message_type})>"
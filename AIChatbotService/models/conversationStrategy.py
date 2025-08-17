from sqlalchemy import CheckConstraint, Column, Integer, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from .base import Base

class ConversationStrategy(Base):
    __tablename__ = 'conversation_strategies'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    conv_id = Column(UUID(as_uuid=True), ForeignKey("public.conversations.conv_id", ondelete="CASCADE"))
    strategy_id = Column(Integer, ForeignKey("public.strategies.strategy_id", ondelete="CASCADE"))
    started_at = Column(
        DateTime(timezone=True),
        default=func.current_timestamp(),
        server_default=func.current_timestamp()
    )

    # Relationships
    conversation = relationship("Conversation", back_populates="strategies")
    strategy = relationship("Strategy", back_populates="conversations")

    def __repr__(self):
        return f"<ConversationStrategy(id={self.id}, conv_id={self.conv_id}, strategy_id={self.strategy_id})>"


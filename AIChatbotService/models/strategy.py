from sqlalchemy import CheckConstraint, Column, Integer, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from .base import Base

class Strategy(Base):
    __tablename__ = 'strategies'
    __table_args__ = (
        CheckConstraint(
            "name IN ('chatbot', 'summarization', 'q&a', 'topic_specific_summary')",
            name="strategy_name_check"
        ),
        {'schema': 'public'}
    )

    strategy_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text)

    # Relationships
    conversations = relationship("ConversationStrategy", back_populates="strategy")

    def __repr__(self):
        return f"<Strategy(strategy_id={self.strategy_id}, name={self.name})>"


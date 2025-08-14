from .conversation import Conversation
from .message import Message
from .base import Base

__all__ = ["Conversation", "Message", "Base"]

# AIChatbotService/models/base.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

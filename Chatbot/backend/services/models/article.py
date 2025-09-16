from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from .base import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text)
    url = Column(String, unique=True, nullable=False)
    category = Column(String(80), nullable=False)
    type = Column(String(50), nullable=False)
    published_at = Column(TIMESTAMP, server_default="now()")
    created_at = Column(TIMESTAMP, server_default="now()")
    # Remove non-existent tsvector columns to match DB

import uuid
from sqlalchemy import Column, Text, JSON, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from .base import Base  

class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    embedding = Column(Vector(768))  # Requires pgvector extension

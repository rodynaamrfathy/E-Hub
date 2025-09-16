import uuid
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from pgvector.sqlalchemy import Vector
from .base import Base

class KBContent(Base):
    __tablename__ = "kb_content"
    __table_args__ = {"schema": "public"}  # Optional, default is public

    # Columns
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_type = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    # Column name in DB is 'metadata', but 'metadata' is reserved in SQLAlchemy
    metadata_json = Column('metadata', JSONB, nullable=True)
    keywords = Column(ARRAY(Text), nullable=True)

    # pgvector embedding column
    embedding = Column(Vector(768), nullable=True)

    def __repr__(self):
        return f"<KBContent(id={self.id}, title={self.title})>"

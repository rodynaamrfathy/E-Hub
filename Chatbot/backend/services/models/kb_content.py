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
    
    # IMPORTANT: The database column is named 'metadata'
    # We use Column('metadata', ...) to map to the actual DB column name
    # But access it via the attribute name 'metadata_json' to avoid Python reserved word conflicts
    metadata_json = Column('metadata', JSONB, nullable=True)
    
    keywords = Column(ARRAY(Text), nullable=True)
    
    # pgvector embedding column (768 dimensions for sentence-transformers models)
    embedding = Column(Vector(768), nullable=True)

    def __repr__(self):
        return f"<KBContent(id={self.id}, title={self.title})>"

    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": str(self.id),
            "content_type": self.content_type,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata_json,  # Return as 'metadata' key
            "keywords": self.keywords,
            "embedding": self.embedding
        }
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from uuid import UUID
import uuid

class KBEntryBaseDTO(BaseModel):
    """Base DTO for KB entries with common fields."""
    content_type: Optional[str] = Field(None, description="Type of content (faq, policy, etc.)")
    title: Optional[str] = Field(None, description="Title of the KB entry")
    content: Optional[str] = Field(None, description="Main content of the KB entry")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Keywords associated with the entry")

    class Config:
        # Allow extra fields for flexibility
        extra = "allow"


class KBEntryCreateDTO(KBEntryBaseDTO):
    """DTO for creating a new KB entry."""
    id: Optional[str] = Field(None, description="Optional ID for the entry (will be generated if not provided)")
    title: str = Field(..., description="Title of the KB entry (required)")
    content: str = Field(..., description="Main content of the KB entry (required)")
    
    @validator('id', pre=True, always=True)
    def validate_id(cls, v):
        """Validate and generate ID if not provided."""
        if v is None:
            return str(uuid.uuid4())
        if isinstance(v, str):
            try:
                # Validate that it's a valid UUID string
                UUID(v)
                return v
            except ValueError:
                raise ValueError("ID must be a valid UUID string")
        return str(v)

    @validator('keywords', pre=True)
    def validate_keywords(cls, v):
        """Ensure keywords is a list of strings."""
        if v is None:
            return []
        if isinstance(v, str):
            # If single string, convert to list
            return [v]
        if isinstance(v, list):
            return [str(item) for item in v]
        return []


class KBEntryUpdateDTO(KBEntryBaseDTO):
    """DTO for updating an existing KB entry. All fields are optional."""
    pass


class KBEntryResponseDTO(KBEntryBaseDTO):
    """DTO for KB entry responses."""
    id: str = Field(..., description="Unique identifier for the KB entry")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding for the entry")
    similarity_score: Optional[float] = Field(None, description="Similarity score (only present in search results)")

    class Config:
        # Allow ORM objects to be converted to this DTO
        from_attributes = True

    @validator('id')
    def validate_response_id(cls, v):
        """Ensure ID is returned as string."""
        return str(v)


class KBSearchRequestDTO(BaseModel):
    """DTO for search requests."""
    query: str = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum similarity score")
    content_type: Optional[str] = Field(None, description="Filter by content type")


class KBBulkOperationDTO(BaseModel):
    """DTO for bulk operations."""
    entries: List[KBEntryCreateDTO] = Field(..., description="List of KB entries to process")

    @validator('entries')
    def validate_entries_not_empty(cls, v):
        """Ensure at least one entry is provided."""
        if not v:
            raise ValueError("At least one entry must be provided")
        return v


class KBBulkResponseDTO(BaseModel):
    """DTO for bulk operation responses."""
    inserted: int = Field(..., description="Number of entries inserted")
    updated: int = Field(..., description="Number of entries updated")
    failed: int = Field(..., description="Number of entries that failed")
    total_processed: int = Field(..., description="Total number of entries processed")
    details: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed results for each entry")


class KBStatsDTO(BaseModel):
    """DTO for KB statistics."""
    total_entries: int = Field(..., description="Total number of KB entries")
    content_types: List[str] = Field(..., description="List of unique content types")
    entries_with_embeddings: int = Field(..., description="Number of entries with embeddings")


class KBListResponseDTO(BaseModel):
    """DTO for paginated list responses."""
    items: List[KBEntryResponseDTO] = Field(..., description="List of KB entries")
    total: int = Field(..., description="Total number of matching entries")
    offset: int = Field(..., description="Current offset")
    limit: int = Field(..., description="Current limit")
    has_more: bool = Field(..., description="Whether there are more entries available")

    @validator('has_more', pre=True, always=True)
    def calculate_has_more(cls, v, values):
        """Calculate if there are more entries available."""
        if 'total' in values and 'offset' in values and 'limit' in values:
            return values['offset'] + values['limit'] < values['total']
        return False


# Example usage and validation schemas
class KBEntryExampleDTO(BaseModel):
    """Example DTO showing typical KB entry structure."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "content_type": "faq",
                "title": "How to reset password",
                "content": "To reset your password, go to the login page and click 'Forgot Password'...",
                "metadata": {
                    "category": "authentication",
                    "priority": "high",
                    "last_updated": "2024-01-15"
                },
                "keywords": ["password", "reset", "login", "authentication"]
            }
        }
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from services.db.postgres import get_db_session
from services.repositories.kb_service import KBContentService
from services.dto.kbDTO import (
    KBEntryCreateDTO,
    KBEntryUpdateDTO,
    KBEntryResponseDTO
)
from services.conversation.tools.KB_ingestion_pipeline import KB_IngestionPipeline


router = APIRouter(tags=["Knowledge Base"])


@router.post("/", response_model=KBEntryResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_kb_entry(entry: KBEntryCreateDTO, db: AsyncSession = Depends(get_db_session)):
    """Create a new KB entry with automatic embedding generation."""
    try:
        kb_service = KBContentService(db)
        pipeline = KB_IngestionPipeline()
        
        # Convert DTO to dict for pipeline processing
        entry_dict = entry.dict()
        
        # Generate new ID if not provided
        if not entry_dict.get("id"):
            entry_dict["id"] = str(uuid.uuid4())
        
        # Use ingestion pipeline to handle embedding generation and upsert
        result = await pipeline.ingest_entry(entry_dict)
        
        if result["status"] == "failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create KB entry"
            )
        
        # Fetch and return the created entry
        created_entry = await kb_service.get_by_id(result["id"])
        if not created_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry created but could not be retrieved"
            )
        
        return KBEntryResponseDTO(**created_entry)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{kb_id}", response_model=KBEntryResponseDTO)
async def get_kb_entry(kb_id: str, db: AsyncSession = Depends(get_db_session)):
    """Retrieve a specific KB entry by ID."""
    try:
        kb_service = KBContentService(db)
        entry = await kb_service.get_by_id(kb_id)
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"KB entry with ID {kb_id} not found"
            )
        
        return KBEntryResponseDTO(**entry)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/", response_model=List[KBEntryResponseDTO])
async def list_kb_entries(
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip"),
    db: AsyncSession = Depends(get_db_session)
):
    """List all KB entries with optional filtering and pagination."""
    try:
        kb_service = KBContentService(db)
        entries = await kb_service.get_all(
            content_type=content_type,
            limit=limit,
            offset=offset
        )
        
        return [KBEntryResponseDTO(**entry) for entry in entries]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{kb_id}", response_model=KBEntryResponseDTO)
async def update_kb_entry(
    kb_id: str, 
    entry: KBEntryUpdateDTO, 
    db: AsyncSession = Depends(get_db_session)
):
    """Update an existing KB entry."""
    try:
        kb_service = KBContentService(db)
        
        # Check if entry exists
        existing_entry = await kb_service.get_by_id(kb_id)
        if not existing_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"KB entry with ID {kb_id} not found"
            )
        
        # Prepare update data
        update_dict = entry.dict(exclude_unset=True)  # Only include provided fields
        update_dict["id"] = kb_id
        
        # Fill in existing values for fields not provided
        for key in ["content_type", "title", "content", "metadata", "keywords"]:
            if key not in update_dict:
                update_dict[key] = existing_entry.get(key)
        
        # Use ingestion pipeline to handle embedding regeneration if content changed
        pipeline = KB_IngestionPipeline()
        result = await pipeline.ingest_entry(update_dict)
        
        if result["status"] == "failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update KB entry"
            )
        
        # Fetch and return updated entry
        updated_entry = await kb_service.get_by_id(kb_id)
        return KBEntryResponseDTO(**updated_entry)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kb_entry(kb_id: str, db: AsyncSession = Depends(get_db_session)):
    """Delete a KB entry by ID."""
    try:
        kb_service = KBContentService(db)
        
        # Check if entry exists
        existing_entry = await kb_service.get_by_id(kb_id)
        if not existing_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"KB entry with ID {kb_id} not found"
            )
        
        # Delete the entry
        success = await kb_service.delete_by_id(kb_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete KB entry"
            )
        
        return None  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/search", response_model=List[KBEntryResponseDTO])
async def search_kb_entries(
    query: str,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results to return"),
    similarity_threshold: float = Query(0.7, ge=0.0, le=1.0, description="Minimum similarity score"),
    db: AsyncSession = Depends(get_db_session)
):
    """Semantic search across KB entries using embeddings."""
    try:
        kb_service = KBContentService(db)
        
        # Perform semantic search
        results = await kb_service.semantic_search(
            query=query,
            limit=limit,
            similarity_threshold=similarity_threshold
        )
        
        return [KBEntryResponseDTO(**result) for result in results]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

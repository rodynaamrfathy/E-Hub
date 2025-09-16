from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, delete, func, and_, text
from ..models import KBContent
from ..conversation.tools.embeddermodel import embedder
import uuid
import json
from typing import List, Optional

class KBContentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedder = embedder()

    async def get_all_embeddings(self):
        """Fetch KB entries with embeddings for semantic search. Returns list of dicts."""
        result = await self.db.execute(
            select(KBContent).where(KBContent.embedding.isnot(None))
        )
        rows = result.scalars().all()
        items = []
        for row in rows:
            items.append({
                "id": str(row.id),
                "content_type": row.content_type,
                "title": row.title,
                "content": row.content,
                "metadata": row.metadata_json,  # Model attribute name
                "keywords": row.keywords,
                "embedding": row.embedding,
            })
        return items

    async def get_by_id(self, kb_id: str):
        """Fetch KB entry by ID. Returns dict or None."""
        result = await self.db.execute(
            select(KBContent).where(KBContent.id == kb_id)
        )
        row = result.scalars().first()
        if not row:
            return None
        return {
            "id": str(row.id),
            "content_type": row.content_type,
            "title": row.title,
            "content": row.content,
            "metadata": row.metadata_json,  # Model attribute name
            "keywords": row.keywords,
            "embedding": row.embedding,
        }

    async def get_all(
        self, 
        content_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """Fetch all KB entries with optional filtering and pagination."""
        query = select(KBContent)
        
        if content_type:
            query = query.where(KBContent.content_type == content_type)
        
        query = query.offset(offset).limit(limit).order_by(KBContent.title)
        
        result = await self.db.execute(query)
        rows = result.scalars().all()
        
        items = []
        for row in rows:
            items.append({
                "id": str(row.id),
                "content_type": row.content_type,
                "title": row.title,
                "content": row.content,
                "metadata": row.metadata_json,  # Model attribute name
                "keywords": row.keywords,
            })
        return items

    async def delete_by_id(self, kb_id: str) -> bool:
        """Delete KB entry by ID. Returns True if successful."""
        try:
            result = await self.db.execute(
                delete(KBContent).where(KBContent.id == kb_id)
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception:
            await self.db.rollback()
            return False

    async def semantic_search(
        self, 
        query: str, 
        limit: int = 10, 
        similarity_threshold: float = 0.7
    ) -> List[dict]:
        """
        Perform semantic search using vector similarity.
        Returns entries ordered by similarity score (highest first).
        """
        try:
            # Generate embedding for query
            query_embeddings = self.embedder.get_embeddings([query])
            if not query_embeddings:
                return []
            
            query_embedding = query_embeddings[0].tolist()
            
            # Perform vector similarity search using raw SQL for better control
            # Using cosine similarity with pgvector
            sql = text("""
                SELECT id, content_type, title, content, metadata, keywords, embedding,
                       (1 - (embedding <=> :query_embedding)) as similarity_score
                FROM kb_content 
                WHERE embedding IS NOT NULL 
                  AND (1 - (embedding <=> :query_embedding)) >= :similarity_threshold
                ORDER BY similarity_score DESC
                LIMIT :limit
            """)
            
            result = await self.db.execute(sql, {
                'query_embedding': str(query_embedding),
                'similarity_threshold': similarity_threshold,
                'limit': limit
            })
            
            rows = result.fetchall()
            items = []
            for row in rows:
                items.append({
                    "id": str(row.id),
                    "content_type": row.content_type,
                    "title": row.title,
                    "content": row.content,
                    "metadata": row.metadata,  # Direct from DB
                    "keywords": row.keywords,
                    "embedding": row.embedding,
                    "similarity_score": float(row.similarity_score),
                })
            
            return items
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []

    async def count_entries(self, content_type: Optional[str] = None) -> int:
        """Count total number of KB entries, optionally filtered by content type."""
        query = select(func.count(KBContent.id))
        
        if content_type:
            query = query.where(KBContent.content_type == content_type)
        
        result = await self.db.execute(query)
        return result.scalar()

    async def get_content_types(self) -> List[str]:
        """Get all unique content types in the KB."""
        result = await self.db.execute(
            select(KBContent.content_type).distinct().where(
                KBContent.content_type.isnot(None)
            ).order_by(KBContent.content_type)
        )
        return [row[0] for row in result.all()]

    async def upsert_kb_entry(self, entry: dict):
        """
        Insert or update a KB entry (upsert).
        Expects keys: id (optional), content_type, title, content, metadata, keywords, embedding
        """
        kb_id = entry.get("id") or str(uuid.uuid4())
        
        # Use raw SQL for the upsert to avoid column mapping issues
        sql = text("""
            INSERT INTO kb_content (id, content_type, title, content, metadata, keywords, embedding)
            VALUES (:id, :content_type, :title, :content, :metadata, :keywords, :embedding)
            ON CONFLICT (id) DO UPDATE SET
                content_type = EXCLUDED.content_type,
                title = EXCLUDED.title,
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata,
                keywords = EXCLUDED.keywords,
                embedding = EXCLUDED.embedding
            RETURNING id;
        """)
        
        try:
            result = await self.db.execute(sql, {
                'id': kb_id,
                'content_type': entry.get("content_type"),
                'title': entry.get("title"),
                'content': entry.get("content"),
                'metadata': json.dumps(entry.get("metadata", {})),  # Convert dict to JSON string
                'keywords': entry.get("keywords", []),
                'embedding': str(entry.get("embedding", []))  # Convert list to string for pgvector
            })
            
            await self.db.commit()
            return result.scalar_one_or_none()
            
        except Exception as e:
            await self.db.rollback()
            print(f"Error in upsert_kb_entry: {e}")
            return None

    async def bulk_upsert(self, entries: List[dict]) -> dict:
        """Bulk upsert multiple KB entries. Returns summary statistics."""
        inserted, updated, failed = 0, 0, 0
        
        try:
            for entry in entries:
                try:
                    # Check if entry exists
                    existing = await self.get_by_id(entry.get("id", ""))
                    
                    result = await self.upsert_kb_entry(entry)
                    if result:
                        if existing:
                            updated += 1
                        else:
                            inserted += 1
                    else:
                        failed += 1
                        
                except Exception as e:
                    print(f"Error processing entry {entry.get('title', 'Unknown')}: {e}")
                    failed += 1
            
            return {
                "inserted": inserted,
                "updated": updated,
                "failed": failed,
                "total_processed": len(entries)
            }
            
        except Exception as e:
            await self.db.rollback()
            raise e
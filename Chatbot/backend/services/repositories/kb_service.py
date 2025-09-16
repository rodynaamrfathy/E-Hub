from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from ..models import KBContent
import uuid
import json

class KBContentService:
    def __init__(self, db: AsyncSession):
        self.db = db

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
                # Model column is named meta_data
                "metadata": row.metadata_json,
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
            "metadata": row.metadata_json,
            "keywords": row.keywords,
            "embedding": row.embedding,
        }

    async def upsert_kb_entry(self, entry: dict):
        """
        Insert or update a KB entry (upsert).
        Expects keys: id (optional), content_type, title, content, metadata, keywords, embedding
        """
        kb_id = entry.get("id") or str(uuid.uuid4())
        stmt = insert(KBContent).values(
            id=kb_id,
            content_type=entry.get("content_type"),
            title=entry.get("title"),
            content=entry.get("content"),
            # Map to underlying 'metadata' column via attribute metadata_json
            metadata_json=entry.get("metadata"),
            keywords=entry.get("keywords"),
            embedding=entry.get("embedding")
        ).on_conflict_do_update(
            index_elements=[KBContent.id],
            set_={
                "content_type": entry.get("content_type"),
                "title": entry.get("title"),
                "content": entry.get("content"),
                "metadata_json": entry.get("metadata"),
                "keywords": entry.get("keywords"),
                "embedding": entry.get("embedding")
            }
        ).returning(KBContent.id)

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

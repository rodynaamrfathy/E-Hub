from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Article

class ArticleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_articles(self):
        """Fetch all articles with fields required for similarity search. Returns list of dicts."""
        result = await self.db.execute(select(Article))
        rows = result.scalars().all()
        return [
            {
                "id": row.id,
                "title": row.title,
                "url": row.url,
                "summary": row.summary,
                "content": row.content,
            }
            for row in rows
        ]

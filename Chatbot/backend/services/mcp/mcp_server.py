import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, and_, or_, func
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from contextlib import asynccontextmanager

try:
    # Try to import from services
    from services.models.article import Article
    from services.db.postgres import get_db_session
except ImportError:
    # Fallback: create our own database session and model
    print("Warning: Could not import services modules, using fallback implementation")
    
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker, DeclarativeBase
    from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
    from sqlalchemy.dialects.postgresql import TSVECTOR
    
    class Base(DeclarativeBase):
        pass
    
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
        ts_summary = Column(TSVECTOR)
        ts_content = Column(TSVECTOR)
    
    # Create database session
    DATABASE_URL = os.getenv("DATABASE_URL_mcp_test")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL_mcp_test environment variable is required")
    
    # Convert to async URL if needed
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    elif not DATABASE_URL.startswith("postgresql+asyncpg://"):
        DATABASE_URL = f"postgresql+asyncpg://{DATABASE_URL}"
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def get_db_session() -> AsyncSession:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

logger = logging.getLogger(__name__)


# Pydantic models for API
class ArticleResponse(BaseModel):
    id: int
    title: str
    summary: str
    content: Optional[str]
    url: str
    category: str
    type: str
    published_at: Optional[str]
    similarity_title: Optional[float] = None
    similarity_summary: Optional[float] = None

    class Config:
        from_attributes = True


class ArticleCreate(BaseModel):
    title: str
    summary: str
    content: Optional[str]
    url: str
    category: str
    type: str
    published_at: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    type: Optional[str] = None
    limit: int = 5


class GetArticleRequest(BaseModel):
    id: Optional[int] = None
    url: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting MCP Server...")
    yield
    # Shutdown
    logger.info("Shutting down MCP Server...")


app = FastAPI(
    title="MCP Article Server",
    description="Model Context Protocol server for sustainability articles",
    version="2.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp-server"}


@app.post("/articles/search", response_model=Dict[str, List[ArticleResponse]])
async def search_articles(
    search_req: SearchRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Search articles using full-text search and fuzzy similarity.
    """
    try:
        # Build the query dynamically
        query = select(Article).order_by(Article.published_at.desc())
        
        # Add search conditions
        search_conditions = []
        
        # Full-text search on tsvector columns if they exist
        if hasattr(Article, 'ts_summary') and hasattr(Article, 'ts_content'):
            search_conditions.extend([
                Article.ts_summary.match(search_req.query),
                Article.ts_content.match(search_req.query)
            ])
        
        # ILIKE search for title and summary
        search_pattern = f"%{search_req.query}%"
        search_conditions.extend([
            Article.title.ilike(search_pattern),
            Article.summary.ilike(search_pattern)
        ])
        
        # If PostgreSQL has pg_trgm extension, add similarity search
        try:
            similarity_conditions = [
                func.similarity(Article.title, search_req.query) > 0.3,
                func.similarity(Article.summary, search_req.query) > 0.3
            ]
            search_conditions.extend(similarity_conditions)
        except Exception:
            # pg_trgm might not be available, skip similarity search
            pass
        
        # Combine all search conditions with OR
        if search_conditions:
            query = query.where(or_(*search_conditions))
        
        # Add category filter
        if search_req.category:
            query = query.where(Article.category == search_req.category)
        
        # Add type filter
        if search_req.type:
            query = query.where(Article.type == search_req.type)
        
        # Add limit
        query = query.limit(search_req.limit)
        
        # Execute query
        result = await db.execute(query)
        articles = result.scalars().all()
        
        # Convert to response format
        article_responses = []
        for article in articles:
            response_data = {
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "content": article.content,
                "url": article.url,
                "category": article.category,
                "type": article.type,
                "published_at": article.published_at.isoformat() if article.published_at else None,
            }
            
            # Try to add similarity scores if pg_trgm is available
            try:
                sim_query = select(
                    func.similarity(Article.title, search_req.query).label('sim_title'),
                    func.similarity(Article.summary, search_req.query).label('sim_summary')
                ).where(Article.id == article.id)
                
                sim_result = await db.execute(sim_query)
                sim_row = sim_result.first()
                if sim_row:
                    response_data["similarity_title"] = float(sim_row.sim_title)
                    response_data["similarity_summary"] = float(sim_row.sim_summary)
            except Exception:
                # Similarity functions not available
                pass
            
            article_responses.append(ArticleResponse(**response_data))
        
        return {"results": article_responses}
        
    except Exception as e:
        logger.error(f"Search articles error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article_by_id(
    article_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get an article by ID."""
    try:
        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return ArticleResponse(
            id=article.id,
            title=article.title,
            summary=article.summary,
            content=article.content,
            url=article.url,
            category=article.category,
            type=article.type,
            published_at=article.published_at.isoformat() if article.published_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get article error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/articles/get", response_model=Dict[str, ArticleResponse])
async def get_article(
    get_req: GetArticleRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Get an article by ID or URL."""
    try:
        if not get_req.id and not get_req.url:
            raise HTTPException(status_code=400, detail="Either id or url must be provided")
        
        query = select(Article)
        
        if get_req.id:
            query = query.where(Article.id == get_req.id)
        elif get_req.url:
            query = query.where(Article.url == get_req.url)
        
        result = await db.execute(query)
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article_response = ArticleResponse(
            id=article.id,
            title=article.title,
            summary=article.summary,
            content=article.content,
            url=article.url,
            category=article.category,
            type=article.type,
            published_at=article.published_at.isoformat() if article.published_at else None
        )
        
        return {"article": article_response}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get article error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/articles/categories-types")
async def list_categories_types(db: AsyncSession = Depends(get_db_session)):
    """Get all available categories and types."""
    try:
        # Get distinct categories
        cat_query = select(Article.category.distinct()).where(Article.category.isnot(None))
        cat_result = await db.execute(cat_query)
        categories = [row[0] for row in cat_result.fetchall()]
        
        # Get distinct types
        type_query = select(Article.type.distinct()).where(Article.type.isnot(None))
        type_result = await db.execute(type_query)
        types = [row[0] for row in type_result.fetchall()]
        
        return {
            "categories": sorted(categories),
            "types": sorted(types)
        }
        
    except Exception as e:
        logger.error(f"List categories/types error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/articles/add", response_model=Dict[str, Any])
async def add_article(
    article_data: ArticleCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Add a new article."""
    try:
        # Create new article
        new_article = Article(
            title=article_data.title,
            summary=article_data.summary,
            content=article_data.content,
            url=article_data.url,
            category=article_data.category,
            type=article_data.type
        )
        
        if article_data.published_at:
            new_article.published_at = article_data.published_at
        
        db.add(new_article)
        await db.commit()
        await db.refresh(new_article)
        
        return {"id": new_article.id, "status": "success"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Add article error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/articles/stats")
async def get_article_stats(db: AsyncSession = Depends(get_db_session)):
    """Get basic statistics about articles."""
    try:
        # Total count
        total_query = select(func.count(Article.id))
        total_result = await db.execute(total_query)
        total_count = total_result.scalar()
        
        # Count by category
        cat_query = select(Article.category, func.count(Article.id)).group_by(Article.category)
        cat_result = await db.execute(cat_query)
        category_counts = {row[0]: row[1] for row in cat_result.fetchall()}
        
        # Count by type
        type_query = select(Article.type, func.count(Article.id)).group_by(Article.type)
        type_result = await db.execute(type_query)
        type_counts = {row[0]: row[1] for row in type_result.fetchall()}
        
        return {
            "total_articles": total_count,
            "by_category": category_counts,
            "by_type": type_counts
        }
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("MCP_PORT", "8001"))
    uvicorn.run(
        "mcp_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
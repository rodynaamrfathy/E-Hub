from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from services.db.postgres import db_manager
from services.repositories.newsletter_service import NewsletterService
from services.repositories.news_article_generator import NewsArticleGenerator
from services.dto.NewsletterDTO import (
    NewsletterSubscriberCreate,
    NewsletterSubscriberUpdate,
    NewsletterSubscriberResponse,
    NewsletterCategoryCreate,
    NewsletterCategoryUpdate,
    NewsletterCategoryResponse,
    GeneratedArticleResponse,
    GenerateArticleRequest,
    SendNewsletterRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_db():
    """Dependency to get database session"""
    async with db_manager.get_session() as session:
        yield session


# ===== Subscriber Endpoints =====

@router.post("/subscribers", response_model=NewsletterSubscriberResponse, status_code=201)
async def create_subscriber(
    subscriber: NewsletterSubscriberCreate,
    db: AsyncSession = Depends(get_db)
):
    """Subscribe to newsletter"""
    try:
        service = NewsletterService(db)
        result = await service.create_subscriber(subscriber)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating subscriber: {e}")
        raise HTTPException(status_code=500, detail="Failed to create subscription")


@router.get("/subscribers/{email}", response_model=NewsletterSubscriberResponse)
async def get_subscriber(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """Get subscriber details"""
    service = NewsletterService(db)
    subscriber = await service.get_subscriber(email)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return subscriber


@router.get("/subscribers", response_model=List[NewsletterSubscriberResponse])
async def list_subscribers(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """List all subscribers"""
    service = NewsletterService(db)
    subscribers = await service.get_all_subscribers(active_only=active_only)
    return subscribers


@router.patch("/subscribers/{email}", response_model=NewsletterSubscriberResponse)
async def update_subscriber(
    email: str,
    updates: NewsletterSubscriberUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update subscriber preferences"""
    try:
        service = NewsletterService(db)
        result = await service.update_subscriber(email, updates)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating subscriber: {e}")
        raise HTTPException(status_code=500, detail="Failed to update subscriber")


@router.post("/subscribers/{email}/unsubscribe")
async def unsubscribe(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """Unsubscribe from newsletter"""
    service = NewsletterService(db)
    success = await service.unsubscribe(email)
    if not success:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return {"message": "Successfully unsubscribed", "email": email}


# ===== Category Management =====

@router.post("/categories", response_model=NewsletterCategoryResponse, status_code=201)
async def create_category(
    category: NewsletterCategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new newsletter category"""
    try:
        service = NewsletterService(db)
        result = await service.create_category(category.name, category.description, category.topics)
        return result
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        raise HTTPException(status_code=500, detail="Failed to create category")


@router.get("/categories", response_model=List[NewsletterCategoryResponse])
async def list_categories(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """List all newsletter categories"""
    service = NewsletterService(db)
    categories = await service.get_categories(active_only=active_only)
    return categories


@router.patch("/categories/{category_id}", response_model=NewsletterCategoryResponse)
async def update_category(
    category_id: int,
    updates: NewsletterCategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a category"""
    try:
        service = NewsletterService(db)
        result = await service.update_category(
            category_id,
            name=updates.name,
            description=updates.description,
            topics=updates.topics,
            is_active=updates.is_active
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating category: {e}")
        raise HTTPException(status_code=500, detail="Failed to update category")


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete (deactivate) a category"""
    try:
        service = NewsletterService(db)
        await service.delete_category(category_id)
        return {"message": "Category deleted successfully", "category_id": category_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===== Article Generation =====

@router.post("/articles/generate", response_model=GeneratedArticleResponse, status_code=201)
async def generate_article(
    request: GenerateArticleRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate a new article from recent news with citations"""
    try:
        generator = NewsArticleGenerator(db)
        article = await generator.create_daily_article(
            category_id=request.category_id,
            custom_topic=request.topic,
            days_back=request.days_back
        )

        # Format response
        response = GeneratedArticleResponse(
            id=article.id,
            title=article.title,
            content=article.content,
            topic=article.topic,
            category_id=article.category_id,
            references=article.references,
            word_count=article.word_count,
            generated_at=article.generated_at,
            read_time_minutes=max(1, article.word_count // 125)  # ~125 words per minute
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate article: {str(e)}")


@router.get("/articles", response_model=List[GeneratedArticleResponse])
async def list_generated_articles(
    limit: int = Query(10, ge=1, le=50),
    category_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List previously generated articles"""
    generator = NewsArticleGenerator(db)
    articles = await generator.get_generated_articles(limit=limit, category_id=category_id)

    return [
        GeneratedArticleResponse(
            id=article.id,
            title=article.title,
            content=article.content,
            topic=article.topic,
            category_id=article.category_id,
            references=article.references,
            word_count=article.word_count,
            generated_at=article.generated_at,
            read_time_minutes=max(1, article.word_count // 125)
        )
        for article in articles
    ]


@router.get("/articles/{article_id}", response_model=GeneratedArticleResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific generated article"""
    from sqlalchemy import select
    from services.models.newsletter import GeneratedArticle

    result = await db.execute(
        select(GeneratedArticle).where(GeneratedArticle.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return GeneratedArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        topic=article.topic,
        category_id=article.category_id,
        references=article.references,
        word_count=article.word_count,
        generated_at=article.generated_at,
        read_time_minutes=max(1, article.word_count // 125)
    )


# ===== Newsletter Sending =====

@router.post("/send")
async def send_newsletter(
    request: SendNewsletterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send newsletter to all subscribers"""
    try:
        service = NewsletterService(db)

        if request.test_mode and request.test_email:
            # Send to test email only
            from sqlalchemy import select
            from services.models.newsletter import GeneratedArticle

            result = await db.execute(
                select(GeneratedArticle).where(GeneratedArticle.id == request.article_id)
            )
            article = result.scalar_one_or_none()

            if not article:
                raise HTTPException(status_code=404, detail="Article not found")

            # Create temporary subscriber for testing
            from services.models.newsletter import NewsletterSubscriber
            test_subscriber = NewsletterSubscriber(
                email=request.test_email,
                name="Test User",
                is_active=True,
                categories=[]
            )

            success = await service.send_article_to_subscriber(article, test_subscriber)
            return {
                "message": "Test email sent",
                "test_email": request.test_email,
                "success": success
            }
        else:
            # Send to all subscribers
            result = await service.send_article_to_all_subscribers(request.article_id)
            return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending newsletter: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send newsletter: {str(e)}")


# ===== Today's Articles =====

@router.get("/today-articles")
async def get_today_articles(
    category: Optional[str] = Query(None),
    days_back: int = Query(1, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get today's crawled articles (source material for newsletter generation)"""
    generator = NewsArticleGenerator(db)
    articles = await generator.get_todays_articles(
        category=category,
        days_back=days_back,
        limit=limit
    )

    return [
        {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "url": article.url,
            "category": article.category,
            "published_at": article.published_at.isoformat()
        }
        for article in articles
    ]

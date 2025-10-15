import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from services.models.newsletter import NewsletterSubscriber, NewsletterCategory, GeneratedArticle
from services.dto.NewsletterDTO import (
    NewsletterSubscriberCreate,
    NewsletterSubscriberUpdate,
)
import os

logger = logging.getLogger(__name__)


class NewsletterService:
    """Service for managing newsletter subscriptions and sending emails"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "E-Hub Newsletter")

    # ===== Subscriber Management =====

    async def create_subscriber(
        self, subscriber_data: NewsletterSubscriberCreate
    ) -> NewsletterSubscriber:
        """Create a new newsletter subscriber"""
        # Check if already exists
        result = await self.db.execute(
            select(NewsletterSubscriber).where(
                NewsletterSubscriber.email == subscriber_data.email
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            if not existing.is_active:
                # Re-subscribe
                existing.is_active = True
                existing.categories = subscriber_data.categories
                existing.subscribed_at = datetime.now()
                existing.unsubscribed_at = None
                await self.db.commit()
                await self.db.refresh(existing)
                return existing
            else:
                raise ValueError("Email already subscribed")

        subscriber = NewsletterSubscriber(
            email=subscriber_data.email,
            name=subscriber_data.name,
            categories=subscriber_data.categories,
        )
        self.db.add(subscriber)
        await self.db.commit()
        await self.db.refresh(subscriber)

        logger.info(f"New subscriber: {subscriber.email}")
        return subscriber

    async def update_subscriber(
        self, email: str, updates: NewsletterSubscriberUpdate
    ) -> NewsletterSubscriber:
        """Update subscriber preferences"""
        result = await self.db.execute(
            select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
        )
        subscriber = result.scalar_one_or_none()

        if not subscriber:
            raise ValueError("Subscriber not found")

        if updates.name is not None:
            subscriber.name = updates.name
        if updates.categories is not None:
            subscriber.categories = updates.categories
        if updates.is_active is not None:
            subscriber.is_active = updates.is_active
            if not updates.is_active:
                subscriber.unsubscribed_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(subscriber)
        return subscriber

    async def unsubscribe(self, email: str) -> bool:
        """Unsubscribe a user"""
        result = await self.db.execute(
            select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
        )
        subscriber = result.scalar_one_or_none()

        if not subscriber:
            return False

        subscriber.is_active = False
        subscriber.unsubscribed_at = datetime.now()
        await self.db.commit()

        logger.info(f"Unsubscribed: {email}")
        return True

    async def get_subscriber(self, email: str) -> Optional[NewsletterSubscriber]:
        """Get subscriber by email"""
        result = await self.db.execute(
            select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
        )
        return result.scalar_one_or_none()

    async def get_all_subscribers(
        self, active_only: bool = True
    ) -> List[NewsletterSubscriber]:
        """Get all subscribers"""
        query = select(NewsletterSubscriber)
        if active_only:
            query = query.where(NewsletterSubscriber.is_active == True)

        result = await self.db.execute(query)
        return result.scalars().all()

    # ===== Category Management =====

    async def create_category(self, name: str, description: str = None, topics: list = None) -> NewsletterCategory:
        """Create a new newsletter category"""
        category = NewsletterCategory(name=name, description=description, topics=topics or [])
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def get_categories(self, active_only: bool = True) -> List[NewsletterCategory]:
        """Get all categories"""
        query = select(NewsletterCategory)
        if active_only:
            query = query.where(NewsletterCategory.is_active == True)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_category(
        self, category_id: int, name: str = None, description: str = None, topics: list = None, is_active: bool = None
    ) -> NewsletterCategory:
        """Update a category"""
        result = await self.db.execute(
            select(NewsletterCategory).where(NewsletterCategory.id == category_id)
        )
        category = result.scalar_one_or_none()

        if not category:
            raise ValueError("Category not found")

        if name:
            category.name = name
        if description is not None:
            category.description = description
        if topics is not None:
            category.topics = topics
        if is_active is not None:
            category.is_active = is_active

        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete_category(self, category_id: int) -> bool:
        """Soft delete a category"""
        return await self.update_category(category_id, is_active=False)

    # ===== Email Sending =====

    def _format_article_email(self, article: GeneratedArticle, subscriber_name: str = None) -> str:
        """Format the article as an HTML email"""
        greeting = f"Hi {subscriber_name}," if subscriber_name else "Hi,"

        # Format references
        references_html = "<h3>References</h3><ol>"
        for ref in article.references:
            references_html += f'<li><a href="{ref["url"]}">{ref["title"]}</a> - {ref["published_at"]}</li>'
        references_html += "</ol>"

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                h1 {{ color: #2c5f2d; border-bottom: 3px solid #97bc62; padding-bottom: 10px; }}
                h3 {{ color: #2c5f2d; margin-top: 30px; }}
                .article-content {{ margin: 20px 0; }}
                .metadata {{ color: #666; font-size: 0.9em; margin: 10px 0; }}
                .references {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-top: 30px; }}
                .references ol {{ padding-left: 20px; }}
                .references li {{ margin: 10px 0; }}
                .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.85em; color: #666; }}
                a {{ color: #2c5f2d; }}
            </style>
        </head>
        <body>
            <p>{greeting}</p>
            <p>Here's today's article from E-Hub Newsletter:</p>

            <h1>{article.title}</h1>

            <div class="metadata">
                <strong>Topic:</strong> {article.topic}<br>
                <strong>Published:</strong> {article.generated_at.strftime('%B %d, %Y')}<br>
                <strong>Reading time:</strong> ~2 minutes ({article.word_count} words)
            </div>

            <div class="article-content">
                {article.content.replace(chr(10), '<br><br>')}
            </div>

            <div class="references">
                {references_html}
            </div>

            <div class="footer">
                <p>Thank you for subscribing to E-Hub Newsletter!</p>
                <p><a href="{{unsubscribe_link}}">Unsubscribe</a> | <a href="{{preferences_link}}">Update Preferences</a></p>
            </div>
        </body>
        </html>
        """
        return html

    async def send_article_to_subscriber(
        self, article: GeneratedArticle, subscriber: NewsletterSubscriber
    ) -> bool:
        """Send article to a single subscriber"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"E-Hub Newsletter: {article.title}"
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = subscriber.email

            html_content = self._format_article_email(article, subscriber.name)
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            # Update last_sent_at
            subscriber.last_sent_at = datetime.now()
            await self.db.commit()

            logger.info(f"Sent article {article.id} to {subscriber.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {subscriber.email}: {e}")
            return False

    async def send_article_to_all_subscribers(
        self, article_id: int, category_filter: Optional[int] = None
    ) -> dict:
        """Send article to all active subscribers"""
        # Get article
        result = await self.db.execute(
            select(GeneratedArticle).where(GeneratedArticle.id == article_id)
        )
        article = result.scalar_one_or_none()

        if not article:
            raise ValueError("Article not found")

        # Get active subscribers
        query = select(NewsletterSubscriber).where(NewsletterSubscriber.is_active == True)

        # Filter by category if specified
        if category_filter:
            # Get subscribers who are subscribed to this category
            query = query.where(
                NewsletterSubscriber.categories.contains([category_filter])
            )

        result = await self.db.execute(query)
        subscribers = result.scalars().all()

        success_count = 0
        failed_count = 0

        for subscriber in subscribers:
            if await self.send_article_to_subscriber(article, subscriber):
                success_count += 1
            else:
                failed_count += 1

        # Mark article as sent
        article.sent_to_subscribers = True
        await self.db.commit()

        return {
            "article_id": article_id,
            "total_subscribers": len(subscribers),
            "sent_successfully": success_count,
            "failed": failed_count,
        }

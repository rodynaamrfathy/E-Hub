import logging
import random
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text

from services.models.article import Article
from services.models.newsletter import NewsletterCategory, GeneratedArticle
from config import get_gemini, EXA_API_KEY

logger = logging.getLogger(__name__)

# Exa search integration
try:
    from exa_py import Exa
    EXA_AVAILABLE = True
except ImportError:
    EXA_AVAILABLE = False
    logger.warning("exa_py not installed. External article search will be disabled.")


class NewsArticleGenerator:
    """Service for generating AI-written articles from crawled news sources"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.gemini = get_gemini()
        self.exa_client = None

        # Initialize Exa if available
        if EXA_AVAILABLE:
            exa_api_key = EXA_API_KEY
            if exa_api_key:
                try:
                    self.exa_client = Exa(api_key=exa_api_key)
                    logger.info("✅ Exa search client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Exa client: {e}")
            else:
                logger.warning("EXA_API_KEY not found in environment")

    async def get_todays_articles(
        self,
        category: Optional[str] = None,
        days_back: int = 1,
        limit: int = 10
    ) -> List[Article]:
        """Fetch articles from the last N days"""
        date_threshold = datetime.now() - timedelta(days=days_back)

        query = select(Article).where(
            Article.published_at >= date_threshold
        ).order_by(Article.published_at.desc())

        if category:
            query = query.where(Article.category == category)

        query = query.limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_trending_topic(self, days_back: int = 7) -> Optional[str]:
        """Identify the most discussed topic from recent articles"""
        date_threshold = datetime.now() - timedelta(days=days_back)

        # Get most common category
        query = select(
            Article.category,
            func.count(Article.id).label('count')
        ).where(
            Article.published_at >= date_threshold
        ).group_by(Article.category).order_by(func.count(Article.id).desc()).limit(1)

        result = await self.db.execute(query)
        row = result.first()

        return row[0] if row else None

    async def select_random_category(self) -> Optional[NewsletterCategory]:
        """Select a random active category for today's article"""
        query = select(NewsletterCategory).where(
            NewsletterCategory.is_active == True
        )
        result = await self.db.execute(query)
        categories = result.scalars().all()

        if not categories:
            return None

        return random.choice(categories)

    async def search_exa_articles(
        self,
        category: NewsletterCategory,
        topic: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for external articles using Exa when local articles are not available"""
        if not self.exa_client:
            logger.warning("Exa client not initialized. Cannot search external articles.")
            return []

        try:
            # Build search query from category topics
            search_terms = []

            if topic:
                search_terms.append(topic)
            elif category.topics:
                # Use up to 3 random topics from the category
                available_topics = category.topics if isinstance(category.topics, list) else []
                search_terms = random.sample(available_topics, min(3, len(available_topics)))
            else:
                search_terms = [category.name]

            # Create search query
            query = " OR ".join(search_terms)
            logger.info(f"🔍 Searching Exa for: {query}")

            # Search using Exa
            search_results = self.exa_client.search_and_contents(
                query,
                type="neural",
                use_autoprompt=True,
                num_results=max_results,
                text={"max_characters": 2000},
                start_published_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            )

            # Convert Exa results to our format
            articles = []
            for result in search_results.results:
                articles.append({
                    "id": f"exa_{result.id}",
                    "title": result.title,
                    "summary": result.text[:500] if result.text else result.title,
                    "content": result.text or "",
                    "url": result.url,
                    "category": category.name,
                    "published_at": datetime.fromisoformat(result.published_date) if hasattr(result, 'published_date') and result.published_date else datetime.now(),
                    "source": "exa"
                })

            logger.info(f"✅ Found {len(articles)} articles from Exa")
            return articles

        except Exception as e:
            logger.error(f"Error searching Exa: {e}")
            return []

    async def generate_article_with_citations(
        self,
        topic: str,
        source_articles: List[Any],  # Can be Article objects or dicts from Exa
        target_word_count: int = 250
    ) -> Dict[str, Any]:
        """Generate a 250-word article with proper citations using Gemini"""

        if not self.gemini:
            raise ValueError("Gemini API not configured")

        if not source_articles:
            raise ValueError("No source articles provided")

        # Prepare source material
        sources_text = []
        references = []
        source_article_ids = []

        for idx, article in enumerate(source_articles, 1):
            source_ref = f"[{idx}]"

            # Handle both Article objects and dict objects (from Exa)
            if isinstance(article, dict):
                title = article.get('title', 'Untitled')
                summary = article.get('summary', '')
                url = article.get('url', '')
                published_at = article.get('published_at', datetime.now())
                category = article.get('category', '')
                article_id = article.get('id', f"external_{idx}")
            else:
                # SQLAlchemy Article object
                title = article.title
                summary = article.summary
                url = article.url
                published_at = article.published_at
                category = article.category
                article_id = article.id

            # Format published date
            if isinstance(published_at, datetime):
                pub_date_str = published_at.strftime('%Y-%m-%d')
                pub_datetime_str = published_at.strftime('%Y-%m-%d %H:%M')
            else:
                pub_date_str = str(published_at)
                pub_datetime_str = str(published_at)

            sources_text.append(
                f"{source_ref} {title}\n"
                f"Published: {pub_date_str}\n"
                f"Summary: {summary}\n"
                f"URL: {url}\n"
            )

            references.append({
                "title": title,
                "url": url,
                "published_at": pub_datetime_str,
                "category": category
            })

            source_article_ids.append(article_id)

        # Create the generation prompt
        prompt = f"""You are a professional environmental and sustainability news writer.
Write a comprehensive, well-researched article about: {topic}

TARGET: Exactly {target_word_count} words (approximately 2-minute read)

REQUIREMENTS:
1. Write in an engaging, journalistic style suitable for a newsletter
2. Include an attention-grabbing headline
3. Cite sources using [1], [2], [3] notation throughout the article
4. Base your content ONLY on the provided source articles
5. Include key facts, statistics, and quotes from the sources
6. End with a brief conclusion or call-to-action
7. DO NOT add a separate references section (it will be added automatically)

SOURCE ARTICLES:
{chr(10).join(sources_text)}

Format your response as:
HEADLINE: [Your headline here]

ARTICLE:
[Your article content with inline citations like [1], [2], etc.]

Write the article now:"""

        try:
            # Generate article using Gemini
            response = self.gemini.invoke(prompt)
            generated_text = response.content

            # Parse the response
            if "HEADLINE:" in generated_text and "ARTICLE:" in generated_text:
                parts = generated_text.split("ARTICLE:", 1)
                headline = parts[0].replace("HEADLINE:", "").strip()
                content = parts[1].strip()
            else:
                # Fallback if format not followed
                lines = generated_text.split('\n', 1)
                headline = lines[0].strip('#').strip()
                content = lines[1].strip() if len(lines) > 1 else generated_text

            # Calculate actual word count
            word_count = len(content.split())

            return {
                "title": headline,
                "content": content,
                "references": references,
                "word_count": word_count,
                "source_article_ids": source_article_ids
            }

        except Exception as e:
            logger.error(f"Error generating article: {e}")
            raise

    async def create_daily_article(
        self,
        category_id: Optional[int] = None,
        custom_topic: Optional[str] = None,
        days_back: int = 7
    ) -> GeneratedArticle:
        """Create and save a daily article based on recent news"""

        # Step 1: Select category
        if category_id:
            result = await self.db.execute(
                select(NewsletterCategory).where(NewsletterCategory.id == category_id)
            )
            category = result.scalar_one_or_none()
            if not category:
                raise ValueError(f"Category {category_id} not found")
        else:
            category = await self.select_random_category()
            if not category:
                raise ValueError("No active categories available")

        # Step 2: Fetch recent articles from database
        articles = await self.get_todays_articles(
            category=category.name,
            days_back=days_back,
            limit=10
        )

        # Step 2b: If no local articles found, search Exa for external sources
        if not articles:
            logger.warning(f"No local articles found for {category.name}. Searching Exa...")
            exa_articles = await self.search_exa_articles(
                category=category,
                topic=custom_topic,
                max_results=5
            )

            if not exa_articles:
                raise ValueError(
                    f"No articles found for category: {category.name}. "
                    f"Try adjusting the days_back parameter or check if articles exist in the database."
                )

            articles = exa_articles
            logger.info(f"✅ Using {len(articles)} articles from Exa search")

        # Step 3: Determine topic
        if custom_topic:
            topic = custom_topic
        else:
            # Use trending topic or most recent article title
            trending = await self.get_trending_topic(days_back=days_back)
            if trending:
                topic = f"Latest developments in {trending}"
            else:
                # Pick a random topic from category if available
                if category.topics and isinstance(category.topics, list) and len(category.topics) > 0:
                    topic = random.choice(category.topics)
                else:
                    topic = f"Recent news in {category.name}"

        # Step 4: Select top 5 most recent articles for generation
        source_articles = articles[:5]

        # Step 5: Generate article with citations
        generated = await self.generate_article_with_citations(
            topic=topic,
            source_articles=source_articles,
            target_word_count=250
        )

        # Step 6: Save to database
        db_article = GeneratedArticle(
            title=generated["title"],
            content=generated["content"],
            topic=topic,
            category_id=category.id,
            source_articles=generated["source_article_ids"],
            references=generated["references"],
            word_count=generated["word_count"],
            sent_to_subscribers=False
        )

        self.db.add(db_article)
        await self.db.commit()
        await self.db.refresh(db_article)

        logger.info(f"Generated article: {db_article.title} ({db_article.word_count} words)")

        return db_article

    async def get_generated_articles(
        self,
        limit: int = 10,
        category_id: Optional[int] = None
    ) -> List[GeneratedArticle]:
        """Retrieve previously generated articles"""
        query = select(GeneratedArticle).order_by(
            GeneratedArticle.generated_at.desc()
        ).limit(limit)

        if category_id:
            query = query.where(GeneratedArticle.category_id == category_id)

        result = await self.db.execute(query)
        return result.scalars().all()

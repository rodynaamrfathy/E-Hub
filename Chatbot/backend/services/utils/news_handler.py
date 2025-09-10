# services/utils/news_handler.py
import os
import asyncio
from typing import List, Dict, Optional, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from rapidfuzz import fuzz
import logging

logger = logging.getLogger(__name__)

class NewsHandler:
    """Handler for news articles from Neon database"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._init_db_connection()
    
    def _init_db_connection(self):
        """Initialize database connection"""
        try:
            # Get database URL from environment
            database_url = os.getenv("NEON_DATABASE_URL")
            if not database_url:
                # Construct from individual components
                host = os.getenv("NEON_HOST")
                database = os.getenv("NEON_DATABASE") 
                user = os.getenv("NEON_USER")
                password = os.getenv("NEON_PASSWORD")
                
                database_url = f"postgresql://{user}:{password}@{host}:5432/{database}?sslmode=require"
            
            self.engine = create_engine(database_url, pool_pre_ping=True)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            self.engine = None
            self.SessionLocal = None
    
    def _search_articles_by_content(
        self, 
        query: str, 
        max_results: int = 5,
        days_back: int = 30,
        min_similarity: int = 60
    ) -> List[Dict[str, Any]]:
        """Search articles using full-text search and fuzzy matching"""
        if not self.SessionLocal:
            logger.warning("Database connection not available")
            return []
        
        try:
            session = self.SessionLocal()
            
            # Calculate date threshold
            date_threshold = datetime.now() - timedelta(days=days_back)
            
            # PostgreSQL full-text search query
            search_query = text("""
                SELECT 
                    id,
                    title,
                    summary,
                    content,
                    url,
                    category,
                    type,
                    published_at,
                    ts_rank(ts_summary, plainto_tsquery(:query)) as summary_rank,
                    ts_rank(ts_content, plainto_tsquery(:query)) as content_rank
                FROM articles 
                WHERE 
                    (ts_summary @@ plainto_tsquery(:query) 
                     OR ts_content @@ plainto_tsquery(:query)
                     OR title ILIKE :like_query
                     OR summary ILIKE :like_query)
                    AND published_at >= :date_threshold
                ORDER BY 
                    GREATEST(summary_rank, content_rank) DESC,
                    published_at DESC
                LIMIT :limit
            """)
            
            like_pattern = f"%{query}%"
            result = session.execute(
                search_query, 
                {
                    "query": query,
                    "like_query": like_pattern,
                    "date_threshold": date_threshold,
                    "limit": max_results * 2  # Get more results for fuzzy filtering
                }
            )
            
            articles = []
            for row in result.fetchall():
                # Additional fuzzy matching for relevance
                title_similarity = fuzz.partial_ratio(query.lower(), row.title.lower())
                summary_similarity = fuzz.partial_ratio(query.lower(), row.summary.lower())
                content_similarity = fuzz.partial_ratio(query.lower(), (row.content or "").lower())
                
                max_similarity = max(title_similarity, summary_similarity, content_similarity)
                
                if max_similarity >= min_similarity:
                    articles.append({
                        "id": row.id,
                        "title": row.title,
                        "summary": row.summary,
                        "content": row.content,
                        "url": row.url,
                        "category": row.category,
                        "type": row.type,
                        "published_at": row.published_at,
                        "similarity_score": max_similarity,
                        "db_rank": float(max(row.summary_rank or 0, row.content_rank or 0))
                    })
            
            # Sort by combination of similarity and database rank
            articles.sort(key=lambda x: (x["similarity_score"] + x["db_rank"] * 10), reverse=True)
            
            session.close()
            return articles[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return []
    
    def _search_articles_by_category(
        self, 
        categories: List[str], 
        max_results: int = 5,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """Search articles by category"""
        if not self.SessionLocal:
            return []
        
        try:
            session = self.SessionLocal()
            date_threshold = datetime.now() - timedelta(days=days_back)
            
            query = text("""
                SELECT id, title, summary, content, url, category, type, published_at
                FROM articles 
                WHERE category = ANY(:categories)
                AND published_at >= :date_threshold
                ORDER BY published_at DESC
                LIMIT :limit
            """)
            
            result = session.execute(
                query, 
                {
                    "categories": categories,
                    "date_threshold": date_threshold,
                    "limit": max_results
                }
            )
            
            articles = []
            for row in result.fetchall():
                articles.append({
                    "id": row.id,
                    "title": row.title,
                    "summary": row.summary,
                    "content": row.content,
                    "url": row.url,
                    "category": row.category,
                    "type": row.type,
                    "published_at": row.published_at,
                    "similarity_score": 100  # Category matches are highly relevant
                })
            
            session.close()
            return articles
            
        except Exception as e:
            logger.error(f"Error searching articles by category: {e}")
            return []
    
    def search_news(
        self, 
        query: str, 
        max_results: int = 5,
        similarity_threshold: int = 60,
        include_categories: Optional[List[str]] = None,
        days_back: int = 30
    ) -> Optional[Dict[str, Any]]:
        """Main search method combining content and category search"""
        results = []
        references = []
        
        try:
            # 1. Content-based search
            content_results = self._search_articles_by_content(
                query, max_results, days_back, similarity_threshold
            )
            
            # 2. Category-based search (if categories specified)
            if include_categories:
                category_results = self._search_articles_by_category(
                    include_categories, max_results//2, days_back
                )
                content_results.extend(category_results)
            
            # Remove duplicates and sort
            seen_ids = set()
            unique_results = []
            for article in content_results:
                if article["id"] not in seen_ids:
                    seen_ids.add(article["id"])
                    unique_results.append(article)
            
            # Sort by relevance
            unique_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            unique_results = unique_results[:max_results]
            
            if not unique_results:
                return None
            
            # Format results for chatbot
            for article in unique_results:
                published_date = article["published_at"].strftime("%Y-%m-%d %H:%M")
                
                snippet = (
                    f"**{article['title']}**\n"
                    f"📅 Published: {published_date}\n"
                    f"🏷️ Category: {article['category']}\n"
                    f"📄 Summary: {article['summary']}\n"
                    f"🔗 URL: {article['url']}\n"
                    f"📊 Relevance: {article['similarity_score']}%"
                )
                
                results.append(snippet)
                references.append({
                    "id": article["id"],
                    "title": article["title"],
                    "url": article["url"],
                    "category": article["category"],
                    "published_at": published_date,
                    "summary": article["summary"],
                    "similarity": article["similarity_score"]
                })
            
            return {
                "context": "\n\n---\n\n".join(results),
                "references": references
            }
            
        except Exception as e:
            logger.error(f"Error in news search: {e}")
            return None

    def get_latest_news(self, category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Get latest news articles"""
        if not self.SessionLocal:
            return []
        
        try:
            session = self.SessionLocal()
            
            if category:
                query = text("""
                    SELECT id, title, summary, url, category, published_at
                    FROM articles 
                    WHERE category = :category
                    ORDER BY published_at DESC
                    LIMIT :limit
                """)
                result = session.execute(query, {"category": category, "limit": limit})
            else:
                query = text("""
                    SELECT id, title, summary, url, category, published_at
                    FROM articles 
                    ORDER BY published_at DESC
                    LIMIT :limit
                """)
                result = session.execute(query, {"limit": limit})
            
            articles = []
            for row in result.fetchall():
                articles.append({
                    "id": row.id,
                    "title": row.title,
                    "summary": row.summary,
                    "url": row.url,
                    "category": row.category,
                    "published_at": row.published_at.strftime("%Y-%m-%d %H:%M")
                })
            
            session.close()
            return articles
            
        except Exception as e:
            logger.error(f"Error getting latest news: {e}")
            return []

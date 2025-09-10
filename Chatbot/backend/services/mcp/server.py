import asyncio
import asyncpg
import json
import logging
from typing import Any, Sequence, Dict, List, Optional
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.models import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
)
from mcp.types import (
    CallToolResult,
    TextContent,
    JSONRPCMessage,
    Request,
    JSONRPCResponse,
    JSONRPCError,
)
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("neon-articles-mcp")

class NeonArticlesMCP:
    def __init__(self):
        self.server = Server("neon-articles-mcp")
        self.db_pool: Optional[asyncpg.Pool] = None
        
        # Database configuration from environment variables
        self.db_config = {
            "host": os.getenv("NEON_HOST"),
            "database": os.getenv("NEON_DATABASE"),
            "user": os.getenv("NEON_USER"),
            "password": os.getenv("NEON_PASSWORD"),
            "port": int(os.getenv("NEON_PORT", 5432)),
            "ssl": "require"
        }
        
        # Register handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Set up all MCP handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="search_articles",
                    description="Search articles using full-text search and similarity matching",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "limit": {
                                "type": "integer", 
                                "description": "Maximum number of results (default: 5)",
                                "default": 5
                            },
                            "search_type": {
                                "type": "string",
                                "enum": ["fulltext", "similarity", "hybrid"],
                                "description": "Type of search: fulltext (TSVECTOR), similarity (pg_trgm), or hybrid (both)",
                                "default": "hybrid"
                            },
                            "category": {
                                "type": "string",
                                "description": "Filter by category (optional)"
                            },
                            "type": {
                                "type": "string", 
                                "description": "Filter by article type (optional)"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_article_by_id",
                    description="Get a specific article by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "article_id": {
                                "type": "integer",
                                "description": "Article ID"
                            }
                        },
                        "required": ["article_id"]
                    }
                ),
                Tool(
                    name="get_articles_by_category",
                    description="Get articles filtered by category and/or type",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Article category"
                            },
                            "type": {
                                "type": "string",
                                "description": "Article type (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["category"]
                    }
                ),
                Tool(
                    name="get_recent_articles",
                    description="Get recently published or created articles",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            },
                            "sort_by": {
                                "type": "string",
                                "enum": ["published_at", "created_at"],
                                "description": "Sort by published_at or created_at",
                                "default": "published_at"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls"""
            try:
                if name == "search_articles":
                    return await self.search_articles(**arguments)
                elif name == "get_article_by_id":
                    return await self.get_article_by_id(**arguments)
                elif name == "get_articles_by_category":
                    return await self.get_articles_by_category(**arguments)
                elif name == "get_recent_articles":
                    return await self.get_recent_articles(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def connect_db(self):
        """Initialize database connection pool"""
        try:
            self.db_pool = await asyncpg.create_pool(**self.db_config)
            logger.info("Connected to Neon database")
            
            # Ensure extensions are available
            async with self.db_pool.acquire() as conn:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
                logger.info("pg_trgm extension ensured")
                
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def close_db(self):
        """Close database connection pool"""
        if self.db_pool:
            await self.db_pool.close()
    
    async def search_articles(
        self, 
        query: str, 
        limit: int = 5, 
        search_type: str = "hybrid",
        category: Optional[str] = None,
        type_filter: Optional[str] = None
    ) -> list[TextContent]:
        """Search articles using different search strategies"""
        
        if not self.db_pool:
            raise RuntimeError("Database not connected")
        
        async with self.db_pool.acquire() as conn:
            results = []
            
            # Build WHERE clause for filters
            where_conditions = []
            params = []
            param_idx = 1
            
            if category:
                where_conditions.append(f"category = ${param_idx}")
                params.append(category)
                param_idx += 1
            
            if type_filter:
                where_conditions.append(f"type = ${param_idx}")
                params.append(type_filter)
                param_idx += 1
            
            where_clause = ""
            if where_conditions:
                where_clause = "AND " + " AND ".join(where_conditions)
            
            if search_type == "fulltext":
                # Full-text search using TSVECTOR
                query_param = f"${param_idx}"
                params.append(query)
                
                sql = f"""
                SELECT id, title, summary, content, url, category, type, 
                       published_at, created_at,
                       ts_rank(ts_summary, plainto_tsquery($1)) + 
                       ts_rank(ts_content, plainto_tsquery($1)) as rank
                FROM articles 
                WHERE (ts_summary @@ plainto_tsquery({query_param}) OR 
                       ts_content @@ plainto_tsquery({query_param}))
                {where_clause}
                ORDER BY rank DESC
                LIMIT {limit}
                """
                
            elif search_type == "similarity":
                # Similarity search using pg_trgm
                query_param = f"${param_idx}"
                params.append(query)
                
                sql = f"""
                SELECT id, title, summary, content, url, category, type, 
                       published_at, created_at,
                       GREATEST(
                           similarity(title, {query_param}),
                           similarity(summary, {query_param}),
                           similarity(content, {query_param})
                       ) as similarity_score
                FROM articles 
                WHERE similarity(title, {query_param}) > 0.1 OR 
                      similarity(summary, {query_param}) > 0.1 OR
                      similarity(content, {query_param}) > 0.1
                {where_clause}
                ORDER BY similarity_score DESC
                LIMIT {limit}
                """
                
            else:  # hybrid
                # Combined search with weighted scoring
                query_param = f"${param_idx}"
                params.append(query)
                
                sql = f"""
                SELECT id, title, summary, content, url, category, type, 
                       published_at, created_at,
                       (COALESCE(ts_rank(ts_summary, plainto_tsquery({query_param})), 0) * 0.3 + 
                        COALESCE(ts_rank(ts_content, plainto_tsquery({query_param})), 0) * 0.2 +
                        COALESCE(similarity(title, {query_param}), 0) * 0.3 +
                        COALESCE(similarity(summary, {query_param}), 0) * 0.2) as combined_score
                FROM articles 
                WHERE (ts_summary @@ plainto_tsquery({query_param}) OR 
                       ts_content @@ plainto_tsquery({query_param}) OR
                       similarity(title, {query_param}) > 0.1 OR 
                       similarity(summary, {query_param}) > 0.1 OR
                       similarity(content, {query_param}) > 0.1)
                {where_clause}
                ORDER BY combined_score DESC
                LIMIT {limit}
                """
            
            rows = await conn.fetch(sql, *params)
            
            if not rows:
                return [TextContent(type="text", text="No articles found matching your query.")]
            
            # Format results
            articles = []
            for row in rows:
                article = {
                    "id": row["id"],
                    "title": row["title"],
                    "summary": row["summary"][:300] + "..." if len(row["summary"]) > 300 else row["summary"],
                    "url": row["url"],
                    "category": row["category"],
                    "type": row["type"],
                    "published_at": row["published_at"].isoformat() if row["published_at"] else None,
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
                
                # Add score based on search type
                if search_type == "fulltext":
                    article["relevance_score"] = float(row["rank"])
                elif search_type == "similarity":
                    article["similarity_score"] = float(row["similarity_score"])
                else:
                    article["combined_score"] = float(row["combined_score"])
                
                articles.append(article)
            
            result_text = json.dumps({
                "query": query,
                "search_type": search_type,
                "total_results": len(articles),
                "articles": articles
            }, indent=2)
            
            return [TextContent(type="text", text=result_text)]
    
    async def get_article_by_id(self, article_id: int) -> list[TextContent]:
        """Get a specific article by ID"""
        if not self.db_pool:
            raise RuntimeError("Database not connected")
        
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, title, summary, content, url, category, type, 
                       published_at, created_at
                FROM articles 
                WHERE id = $1
                """,
                article_id
            )
            
            if not row:
                return [TextContent(type="text", text=f"Article with ID {article_id} not found.")]
            
            article = {
                "id": row["id"],
                "title": row["title"],
                "summary": row["summary"],
                "content": row["content"],
                "url": row["url"],
                "category": row["category"],
                "type": row["type"],
                "published_at": row["published_at"].isoformat() if row["published_at"] else None,
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            }
            
            result_text = json.dumps(article, indent=2)
            return [TextContent(type="text", text=result_text)]
    
    async def get_articles_by_category(
        self, 
        category: str, 
        type_filter: Optional[str] = None, 
        limit: int = 10
    ) -> list[TextContent]:
        """Get articles by category and optionally by type"""
        if not self.db_pool:
            raise RuntimeError("Database not connected")
        
        async with self.db_pool.acquire() as conn:
            if type_filter:
                rows = await conn.fetch(
                    """
                    SELECT id, title, summary, url, category, type, published_at, created_at
                    FROM articles 
                    WHERE category = $1 AND type = $2
                    ORDER BY published_at DESC
                    LIMIT $3
                    """,
                    category, type_filter, limit
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT id, title, summary, url, category, type, published_at, created_at
                    FROM articles 
                    WHERE category = $1
                    ORDER BY published_at DESC
                    LIMIT $2
                    """,
                    category, limit
                )
            
            if not rows:
                filter_text = f"category '{category}'" + (f" and type '{type_filter}'" if type_filter else "")
                return [TextContent(type="text", text=f"No articles found for {filter_text}.")]
            
            articles = []
            for row in rows:
                article = {
                    "id": row["id"],
                    "title": row["title"],
                    "summary": row["summary"][:200] + "..." if len(row["summary"]) > 200 else row["summary"],
                    "url": row["url"],
                    "category": row["category"],
                    "type": row["type"],
                    "published_at": row["published_at"].isoformat() if row["published_at"] else None,
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
                articles.append(article)
            
            result_text = json.dumps({
                "category": category,
                "type": type_filter,
                "total_results": len(articles),
                "articles": articles
            }, indent=2)
            
            return [TextContent(type="text", text=result_text)]
    
    async def get_recent_articles(
        self, 
        limit: int = 10, 
        sort_by: str = "published_at"
    ) -> list[TextContent]:
        """Get recent articles"""
        if not self.db_pool:
            raise RuntimeError("Database not connected")
        
        async with self.db_pool.acquire() as conn:
            sort_column = "published_at" if sort_by == "published_at" else "created_at"
            
            rows = await conn.fetch(
                f"""
                SELECT id, title, summary, url, category, type, published_at, created_at
                FROM articles 
                ORDER BY {sort_column} DESC
                LIMIT $1
                """,
                limit
            )
            
            if not rows:
                return [TextContent(type="text", text="No articles found.")]
            
            articles = []
            for row in rows:
                article = {
                    "id": row["id"],
                    "title": row["title"],
                    "summary": row["summary"][:200] + "..." if len(row["summary"]) > 200 else row["summary"],
                    "url": row["url"],
                    "category": row["category"],
                    "type": row["type"],
                    "published_at": row["published_at"].isoformat() if row["published_at"] else None,
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
                articles.append(article)
            
            result_text = json.dumps({
                "sort_by": sort_by,
                "total_results": len(articles),
                "articles": articles
            }, indent=2)
            
            return [TextContent(type="text", text=result_text)]


async def main():
    """Main function to run the MCP server"""
    mcp = NeonArticlesMCP()
    
    # Connect to database
    await mcp.connect_db()
    
    try:
        # Import here to avoid issues if mcp package is not installed
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await mcp.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="neon-articles-mcp",
                    server_version="1.0.0",
                    capabilities=mcp.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    finally:
        await mcp.close_db()


if __name__ == "__main__":
    asyncio.run(main())
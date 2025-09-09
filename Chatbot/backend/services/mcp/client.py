import aiohttp
import asyncio
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MCPClient:
    """Async client for MCP server to query sustainability articles."""

    def __init__(self, base_url: str = "http://localhost:8001", timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def search_articles(
        self, 
        query: str, 
        category: Optional[str] = None,
        type_: Optional[str] = None, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search articles using the MCP server."""
        try:
            session = await self._get_session()
            payload = {
                "query": query,
                "category": category,
                "type": type_,
                "limit": limit
            }
            
            async with session.post(
                f"{self.base_url}/articles/search", 
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                else:
                    logger.warning(f"MCP search failed with status {response.status}")
                    return []
                    
        except asyncio.TimeoutError:
            logger.error("MCP search request timed out")
            return []
        except Exception as e:
            logger.error(f"MCP search error: {e}")
            return []

    async def get_article(
        self, 
        article_id: Optional[int] = None, 
        url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a specific article by ID or URL."""
        try:
            session = await self._get_session()
            payload = {"id": article_id, "url": url}
            
            async with session.post(
                f"{self.base_url}/articles/get", 
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("article")
                else:
                    logger.warning(f"MCP get_article failed with status {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"MCP get_article error: {e}")
            return None

    async def list_categories_types(self) -> Dict[str, List[str]]:
        """Get available categories and types."""
        try:
            session = await self._get_session()
            
            async with session.get(
                f"{self.base_url}/articles/categories-types"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"MCP categories request failed with status {response.status}")
                    return {"categories": [], "types": []}
                    
        except Exception as e:
            logger.error(f"MCP categories error: {e}")
            return {"categories": [], "types": []}

    async def health_check(self) -> bool:
        """Check if the MCP server is healthy."""
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/health") as response:
                return response.status == 200
                
        except Exception:
            return False

    # Sync wrapper methods for backward compatibility
    def search_articles_sync(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """Sync wrapper for search_articles."""
        return asyncio.run(self.search_articles(*args, **kwargs))

    def get_article_sync(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """Sync wrapper for get_article."""
        return asyncio.run(self.get_article(*args, **kwargs))

    def list_categories_types_sync(self) -> Dict[str, List[str]]:
        """Sync wrapper for list_categories_types."""
        return asyncio.run(self.list_categories_types())
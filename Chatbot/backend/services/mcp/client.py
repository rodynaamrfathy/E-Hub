import asyncio
import json
import logging
import subprocess
import sys
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class MCPClient:
    """Async MCP client for communicating with the Neon articles MCP server"""
    
    def __init__(self, server_path: str = "server.py"):
        self.server_path = server_path
        self.process: Optional[subprocess.Popen] = None
        self._connected = False
        self._request_id = 0
        
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    def _get_next_request_id(self) -> int:
        """Get next request ID"""
        self._request_id += 1
        return self._request_id
    
    async def connect(self):
        """Start the MCP server process"""
        if self._connected:
            return
            
        try:
            # Start the MCP server as a subprocess
            self.process = subprocess.Popen(
                [sys.executable, self.server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": self._get_next_request_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "langchain-mcp-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            self._send_message(init_request)
            
            # Read initialization response
            response = await self._read_message()
            if response and response.get("result"):
                self._connected = True
                logger.info("MCP client connected successfully")
            else:
                raise Exception(f"Failed to initialize MCP server: {response}")
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            if self.process:
                self.process.terminate()
                self.process = None
            raise
    
    async def disconnect(self):
        """Stop the MCP server process"""
        if self.process and self._connected:
            try:
                self.process.terminate()
                await asyncio.sleep(0.1)  # Give it time to terminate gracefully
                if self.process.poll() is None:
                    self.process.kill()
            except Exception as e:
                logger.error(f"Error disconnecting from MCP server: {e}")
            finally:
                self.process = None
                self._connected = False
    
    def _send_message(self, message: dict):
        """Send a message to the MCP server"""
        if not self.process or not self.process.stdin:
            raise Exception("MCP server not connected")
        
        message_str = json.dumps(message) + "\n"
        self.process.stdin.write(message_str)
        self.process.stdin.flush()
    
    async def _read_message(self) -> Optional[dict]:
        """Read a message from the MCP server"""
        if not self.process or not self.process.stdout:
            return None
        
        try:
            # Read line from stdout
            line = await asyncio.to_thread(self.process.stdout.readline)
            if line.strip():
                return json.loads(line.strip())
        except Exception as e:
            logger.error(f"Error reading message from MCP server: {e}")
        
        return None
    
    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a tool on the MCP server"""
        if not self._connected:
            await self.connect()
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        self._send_message(request)
        response = await self._read_message()
        
        if response and "result" in response:
            return response["result"]["content"]
        elif response and "error" in response:
            raise Exception(f"MCP tool call error: {response['error']}")
        else:
            raise Exception("No response from MCP server")
    
    async def search_articles(
        self, 
        query: str, 
        limit: int = 5, 
        search_type: str = "hybrid",
        category: Optional[str] = None,
        article_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search articles using the MCP server
        
        Args:
            query: Search query
            limit: Maximum number of results
            search_type: "fulltext", "similarity", or "hybrid"
            category: Filter by category (optional)
            article_type: Filter by article type (optional)
        
        Returns:
            List of articles with metadata
        """
        arguments = {
            "query": query,
            "limit": limit,
            "search_type": search_type
        }
        
        if category:
            arguments["category"] = category
        if article_type:
            arguments["type"] = article_type
        
        try:
            result = await self.call_tool("search_articles", arguments)
            
            # Parse the JSON response
            if result and len(result) > 0:
                response_data = json.loads(result[0]["text"])
                return response_data.get("articles", [])
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return []
    
    async def get_article_by_id(self, article_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific article by ID"""
        try:
            result = await self.call_tool("get_article_by_id", {"article_id": article_id})
            
            if result and len(result) > 0:
                return json.loads(result[0]["text"])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting article by ID: {e}")
            return None
    
    async def get_articles_by_category(
        self, 
        category: str, 
        article_type: Optional[str] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get articles by category and optionally by type"""
        arguments = {"category": category, "limit": limit}
        if article_type:
            arguments["type"] = article_type
        
        try:
            result = await self.call_tool("get_articles_by_category", arguments)
            
            if result and len(result) > 0:
                response_data = json.loads(result[0]["text"])
                return response_data.get("articles", [])
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting articles by category: {e}")
            return []
    
    async def get_recent_articles(
        self, 
        limit: int = 10, 
        sort_by: str = "published_at"
    ) -> List[Dict[str, Any]]:
        """Get recent articles"""
        arguments = {"limit": limit, "sort_by": sort_by}
        
        try:
            result = await self.call_tool("get_recent_articles", arguments)
            
            if result and len(result) > 0:
                response_data = json.loads(result[0]["text"])
                return response_data.get("articles", [])
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting recent articles: {e}")
            return []


# Example usage and testing
async def test_mcp_client():
    """Test the MCP client"""
    async with MCPClient("server.py") as client:
        # Test search
        print("Testing search...")
        articles = await client.search_articles("machine learning", limit=3, search_type="hybrid")
        print(f"Found {len(articles)} articles")
        for article
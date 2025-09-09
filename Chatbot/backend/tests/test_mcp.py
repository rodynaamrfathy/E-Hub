#!/usr/bin/env python3
"""
Test script for MCP (Model Context Protocol) functionality in the chatbot.
Updated with async support and better error handling.
"""

import asyncio
import sys
import os
import json
import aiohttp
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mcp.client import MCPClient
from services.conversation.GeminiMultimodalChatbot import GeminiMultimodalChatbot


async def test_mcp_server_health():
    """Test if MCP server is accessible."""
    print("🔹 Testing MCP Server Health...")
    
    try:
        # Use aiohttp for async health check
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8001/health", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ MCP Server is running and accessible")
                    print(f"   Status: {data.get('status', 'unknown')}")
                    print(f"   Service: {data.get('service', 'unknown')}")
                    return True
                else:
                    print(f"⚠️ MCP Server responded with status: {response.status}")
                    return False
                    
    except aiohttp.ClientConnectorError:
        print("❌ Cannot connect to MCP Server on localhost:8001")
        print("   Make sure to start the MCP server first:")
        print("   python -m services.mcp.mcp_server")
        return False
    except asyncio.TimeoutError:
        print("❌ MCP Server health check timed out")
        return False
    except Exception as e:
        print(f"❌ MCP Server health check failed: {e}")
        return False


async def test_mcp_client_direct():
    """Test MCP client directly with async methods."""
    print("\n🔹 Testing Async MCP Client Direct Connection...")
    
    try:
        async with MCPClient("http://localhost:8001") as mcp_client:
            
            # Test search functionality
            test_queries = [
                "climate change",
                "renewable energy", 
                "artificial intelligence",
                "sustainability",
                "carbon emissions"
            ]
            
            for query in test_queries:
                print(f"\n📝 Testing query: '{query}'")
                try:
                    start_time = time.time()
                    articles = await mcp_client.search_articles(query, limit=3)
                    end_time = time.time()
                    
                    if articles:
                        print(f"✅ Found {len(articles)} articles in {end_time - start_time:.2f}s:")
                        for i, article in enumerate(articles[:2], 1):
                            print(f"   {i}. {article['title']}")
                            print(f"      Category: {article.get('category', 'N/A')}")
                            print(f"      Type: {article.get('type', 'N/A')}")
                            print(f"      URL: {article.get('url', 'N/A')[:60]}...")
                            if 'similarity_title' in article:
                                print(f"      Similarity: {article['similarity_title']:.2f}")
                    else:
                        print("⚠️ No articles found")
                        
                except Exception as e:
                    print(f"❌ Error searching for '{query}': {e}")
                    
            # Test categories and types
            print(f"\n📝 Testing categories and types listing...")
            try:
                cat_types = await mcp_client.list_categories_types()
                categories = cat_types.get("categories", [])
                types = cat_types.get("types", [])
                
                print(f"✅ Found {len(categories)} categories: {categories[:5]}")
                print(f"✅ Found {len(types)} types: {types[:5]}")
                
            except Exception as e:
                print(f"❌ Error getting categories/types: {e}")
                
    except Exception as e:
        print(f"❌ MCP Client connection failed: {e}")


async def test_chatbot_mcp_integration():
    """Test MCP integration within the chatbot."""
    print("\n🔹 Testing MCP Integration in Chatbot...")
    
    try:
        # Create a test chatbot instance
        async with GeminiMultimodalChatbot() as chatbot:
            
            # Test the internal _maybe_retrieve method
            test_queries = [
                "latest climate research",
                "AI developments",
                "sustainable technology",
                "renewable energy innovations",
                "carbon capture methods"
            ]
            
            for query in test_queries:
                print(f"\n📝 Testing chatbot retrieval for: '{query}'")
                try:
                    start_time = time.time()
                    result = await chatbot._maybe_retrieve(query, max_results=3)
                    end_time = time.time()
                    
                    if result:
                        print(f"✅ Retrieved data successfully in {end_time - start_time:.2f}s:")
                        print(f"   Context length: {len(result['context'])} chars")
                        print(f"   References: {len(result['references'])} items")
                        print(f"   Sources used: {result.get('sources_used', [])}")
                        
                        # Show first reference
                        if result['references']:
                            first_ref = result['references'][0]
                            print(f"   First reference: {first_ref.get('title', 'N/A')}")
                            print(f"   Source: {first_ref.get('source', 'N/A')}")
                    else:
                        print("⚠️ No data retrieved")
                        
                except Exception as e:
                    print(f"❌ Error in chatbot retrieval: {e}")
                    
    except Exception as e:
        print(f"❌ Chatbot initialization failed: {e}")


async def test_full_chatbot_response():
    """Test full chatbot response with MCP integration."""
    print("\n🔹 Testing Full Chatbot Response...")
    
    try:
        async with GeminiMultimodalChatbot() as chatbot:
            
            test_messages = [
                "Tell me about recent developments in renewable energy",
                "What are the latest climate change impacts?",
                "How can AI help with sustainability?"
            ]
            
            for test_message in test_messages:
                print(f"\n📝 Test message: '{test_message}'")
                
                try:
                    start_time = time.time()
                    response = await chatbot.get_response_async(test_message)
                    end_time = time.time()
                    
                    if response.get("success"):
                        print(f"✅ Full response successful in {end_time - start_time:.2f}s:")
                        print(f"   Response length: {len(response['response'])} chars")
                        print(f"   Web search used: {response['web_search_used']}")
                        print(f"   References: {len(response.get('references', []))} items")
                        print(f"   Sources used: {response.get('sources_used', [])}")
                        print(f"   First 200 chars: {response['response'][:200]}...")
                    else:
                        print(f"❌ Response failed: {response.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"❌ Full chatbot test failed for '{test_message}': {e}")
                    
    except Exception as e:
        print(f"❌ Full chatbot test initialization failed: {e}")


async def test_streaming_response():
    """Test streaming response functionality."""
    print("\n🔹 Testing Streaming Response...")
    
    try:
        async with GeminiMultimodalChatbot() as chatbot:
            
            test_message = "Explain the benefits of solar energy"
            print(f"📝 Test streaming message: '{test_message}'")
            
            try:
                print("🔄 Streaming response:")
                token_count = 0
                start_time = time.time()
                
                async for token in chatbot.stream_response(test_message):
                    print(token, end="", flush=True)
                    token_count += 1
                    
                end_time = time.time()
                print(f"\n✅ Streaming completed:")
                print(f"   Tokens streamed: {token_count}")
                print(f"   Time taken: {end_time - start_time:.2f}s")
                
                # Get full response
                full_response = chatbot.get_full_response()
                print(f"   Full response length: {len(full_response)} chars")
                
            except Exception as e:
                print(f"❌ Streaming test failed: {e}")
                
    except Exception as e:
        print(f"❌ Streaming test initialization failed: {e}")


async def test_mcp_performance():
    """Test MCP performance with multiple concurrent requests."""
    print("\n🔹 Testing MCP Performance...")
    
    try:
        async with MCPClient("http://localhost:8001") as mcp_client:
            
            # Test concurrent searches
            queries = [
                "renewable energy",
                "climate change",
                "sustainability",
                "carbon footprint",
                "green technology"
            ]
            
            print(f"📝 Testing {len(queries)} concurrent searches...")
            
            start_time = time.time()
            
            # Run searches concurrently
            tasks = [mcp_client.search_articles(query, limit=2) for query in queries]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            
            successful_results = [r for r in results if not isinstance(r, Exception)]
            failed_results = [r for r in results if isinstance(r, Exception)]
            
            print(f"✅ Concurrent search completed in {end_time - start_time:.2f}s:")
            print(f"   Successful: {len(successful_results)}/{len(queries)}")
            print(f"   Failed: {len(failed_results)}/{len(queries)}")
            
            total_articles = sum(len(r) for r in successful_results if r)
            print(f"   Total articles found: {total_articles}")
            
            if failed_results:
                print("   Errors:")
                for i, error in enumerate(failed_results):
                    print(f"     {i+1}. {error}")
                    
    except Exception as e:
        print(f"❌ Performance test failed: {e}")


async def main():
    """Run all MCP tests."""
    print("=" * 60)
    print("🧪 MCP TESTING SUITE (Async Version)")
    print("=" * 60)
    
    # 1. Check server health first
    server_healthy = await test_mcp_server_health()
    
    if not server_healthy:
        print("\n❌ MCP Server is not accessible. Please start it first.")
        print("\nTo start MCP server:")
        print("cd /path/to/your/backend")
        print("python -m services.mcp.mcp_server")
        return
    
    # 2. Test MCP client direct
    await test_mcp_client_direct()
    
    # 3. Test performance
    await test_mcp_performance()
    
    # 4. Test chatbot integration
    await test_chatbot_mcp_integration()
    
    # 5. Test full response
    await test_full_chatbot_response()
    
    # 6. Test streaming
    await test_streaming_response()
    
    print("\n" + "=" * 60)
    print("🏁 MCP TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)
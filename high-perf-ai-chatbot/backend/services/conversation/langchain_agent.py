"""
LangChain agent that orchestrates multiple services including MCP, RAG, and web search
"""
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory

from ..mcp.langchain_tools import create_mcp_tools
from ..rag.retriever import RAGRetriever
from ..websearch.search import WebSearchTool
from ..db.redis_cache import RedisCache
from config import settings

@dataclass
class ChatResponse:
    message: str
    sources: Optional[List[Dict[str, Any]]] = None
    session_id: Optional[str] = None
    tool_calls: Optional[List[str]] = None

class HighPerfAIChatbot:
    """High-performance AI chatbot with RAG, MCP, and web search capabilities"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{asyncio.get_event_loop().time()}"
        
        # Initialize components
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=0.1,
            streaming=True
        )
        
        # Initialize services
        self.rag_retriever = RAGRetriever()
        self.web_search = WebSearchTool()
        self.redis_cache = RedisCache()
        
        # Set up memory
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10
        )
        
        # Create tools
        self.tools = self._create_all_tools()
        
        # Create agent
        self.agent = self._create_agent()
    
    def _create_all_tools(self) -> List[Tool]:
        """Create all available tools for the agent"""
        tools = []
        
        # MCP Database tools
        tools.extend(create_mcp_tools())
        
        # RAG tools
        tools.append(Tool(
            name="search_knowledge_base",
            description="Search the knowledge base for relevant information using vector similarity",
            func=self._search_rag
        ))
        
        # Web search tools
        tools.append(Tool(
            name="web_search",
            description="Search the web for current information and recent news",
            func=self._web_search
        ))
        
        # Session management tools
        tools.append(Tool(
            name="get_session_context",
            description="Retrieve previous conversation context for this session",
            func=self._get_session_context
        ))
        
        return tools
    
    def _search_rag(self, query: str) -> str:
        """Search RAG knowledge base"""
        try:
            results = self.rag_retriever.retrieve(query, k=5)
            if not results:
                return "No relevant information found in knowledge base"
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result.page_content[:500],  # Truncate for context
                    "score": result.metadata.get("score", 0),
                    "source": result.metadata.get("source", "unknown")
                })
            
            return json.dumps(formatted_results, indent=2)
        except Exception as e:
            return f"RAG search error: {str(e)}"
    
    def _web_search(self, query: str) -> str:
        """Perform web search"""
        try:
            results = self.web_search.search(query, max_results=5)
            if not results:
                return "No web search results found"
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", "")[:300],
                    "url": result.get("url", ""),
                    "source": "web_search"
                })
            
            return json.dumps(formatted_results, indent=2)
        except Exception as e:
            return f"Web search error: {str(e)}"
    
    def _get_session_context(self, context_type: str = "recent") -> str:
        """Get session context from Redis cache"""
        try:
            if context_type == "recent":
                context = self.redis_cache.get_recent_context(self.session_id)
            else:
                context = self.redis_cache.get_full_context(self.session_id)
            
            return json.dumps(context, indent=2) if context else "No session context found"
        except Exception as e:
            return f"Session context error: {str(e)}"
    
    def _create_agent(self):
        """Create the LangChain agent"""
        system_prompt = """You are a high-performance AI assistant with access to multiple information sources:

1. **Database Access (MCP)**: Query and modify a PostgreSQL database with news and content
2. **Knowledge Base (RAG)**: Search vector-indexed documents for relevant information  
3. **Web Search**: Get current information from the internet
4. **Session Context**: Access previous conversation history

Your capabilities:
- Answer questions using the most appropriate information source
- Combine information from multiple sources when helpful
- Provide source attributions and references
- Maintain conversation context across sessions
- Execute database operations when requested

Guidelines:
- Always cite your sources when providing information
- Use the most current and relevant information available
- For news or recent events, prefer web search over stored data
- For historical or factual information, use the knowledge base
- For user-specific data, use the database
- Be precise with database operations and confirm before modifications
- Maintain conversation context and reference previous exchanges when relevant

Remember: You have access to real-time data through multiple channels. Use them wisely to provide the most accurate and helpful responses."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=settings.DEBUG,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    async def chat(self, message: str) -> ChatResponse:
        """Process chat message with streaming support"""
        try:
            # Store message in session context
            await self.redis_cache.add_to_context(
                self.session_id, 
                "user", 
                message
            )
            
            # Execute agent
            response = await asyncio.to_thread(
                self.agent.invoke,
                {"input": message}
            )
            
            # Store response in session context
            await self.redis_cache.add_to_context(
                self.session_id,
                "assistant", 
                response["output"]
            )
            
            # Extract tool calls for monitoring
            tool_calls = self._extract_tool_calls(response)
            
            return ChatResponse(
                message=response["output"],
                session_id=self.session_id,
                tool_calls=tool_calls
            )
            
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}"
            await self.redis_cache.add_to_context(
                self.session_id,
                "error",
                error_msg
            )
            return ChatResponse(
                message=error_msg,
                session_id=self.session_id
            )
    
    def _extract_tool_calls(self, response: Dict) -> List[str]:
        """Extract tool calls from agent response for monitoring"""
        # Implementation depends on  monitoring needs
        return []

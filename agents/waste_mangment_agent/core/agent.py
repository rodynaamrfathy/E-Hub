from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType
from typing import List
from .config import Config
from ..tools.search.exa_search import ExaSearch
from ..tools.sorting.sorting import SortingRules

class WasteManagementAgent:
    """Main waste management agent orchestrator"""
    
    def __init__(self, region: str = Config.DEFAULT_REGION):
        self.region = region
        self.llm = ChatOllama(model=Config.OLLAMA_MODEL)
        
        # Initialize tools
        # self.waste_classifier = WasteClassifier()
        # self.sorting_rules = SortingRules()
        # self.eco_tips = EcoTips()
        # self.web_search = ExaSearch()
        
        # Initialize agent
        self._setup_agent()
    
    def _setup_agent(self):
        """Setup the LangChain agent with tools"""
        tools = [
            # self.waste_classifier.get_tool(),
            self.sorting_rules.get_tool(),
            # # self.eco_tips.get_tool(),
            # self.web_search.get_tool()
        ]
        
        # Custom prompt to guide the agent better
        system_prompt = """You are a helpful waste management assistant. Your goal is to provide clear, actionable advice about waste disposal and recycling.

            When using tools:
            Use sorting_rules to get regional disposal guidelines 
            

            Always provide a final answer even if you don't find complete information. Be concise and practical."""
            # 1. Start with waste_classifier to identify the waste type
            # 3. Use eco_tips for sustainable alternatives
            #Only use web_search if the knowledge base doesn't have sufficient information

        self.agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=5,
            max_execution_time=80, 
            early_stopping_method="generate",
            handle_parsing_errors=True,
            agent_kwargs={
                "prefix": system_prompt
            }
        )
    
    def process_query(self, query: str) -> str:
        """Process user query and return response"""
  
        # Add context about the user's region
        enhanced_query = f"[User is in {self.region}] {query}"
            
        # Try to get a response from the agent
        response = self.agent.run(enhanced_query)
        return response
            

    
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return [
            "waste_classifier - Classify waste items",
            "sorting_rules - Get regional sorting rules", 
            "eco_tips - Get eco-friendly alternatives",
            "web_search - Search for current information"
        ]

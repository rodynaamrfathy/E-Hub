from langchain_core.tools import Tool
from exa_py import Exa
from .config import Config
class EcoTips:
    """Tool for providing eco-friendly alternatives and tips"""
    
    def __init__(self):
        self.alternatives = KnowledgeLoader.load_yaml(
            Config.get_knowledge_file("eco_alternatives.yaml")
        )
    
    def get_tip(self, item: str) -> str:
        """Get eco-friendly alternatives for waste items"""
        item_lower = item.lower()
        
        # Direct match first
        if item_lower in self.alternatives:
            tip_data = self.alternatives[item_lower]
            return self._format_tip(item, tip_data)
        
        # Partial match
        for key, tip_data in self.alternatives.items():
            if key in item_lower or any(keyword in item_lower for keyword in key.split()):
                return self._format_tip(item, tip_data)
        
        # Generic advice
        generic_tips = self.alternatives.get('generic', {})
        if generic_tips:
            return self._format_tip(item, generic_tips)
        
        return f"No specific eco-friendly alternative found for {item}. Consider reducing, reusing, or finding creative ways to repurpose the item."
    
    def _format_tip(self, item: str, tip_data: Dict) -> str:
        """Format tip data into readable text"""
        if isinstance(tip_data, str):
            return f"Eco-friendly tip for {item}: {tip_data}"
        
        tip_text = f"Eco-friendly alternatives for {item}:\n"
        
        if 'alternatives' in tip_data:
            alternatives = tip_data['alternatives']
            if isinstance(alternatives, list):
                for alt in alternatives:
                    tip_text += f"• {alt}\n"
            else:
                tip_text += f"• {alternatives}\n"
        
        if 'impact' in tip_data:
            tip_text += f"Environmental impact: {tip_data['impact']}\n"
        
        if 'difficulty' in tip_data:
            tip_text += f"Difficulty level: {tip_data['difficulty']}"
        
        return tip_text.strip()
    
    def get_tool(self) -> Tool:
        """Return LangChain Tool"""
        return Tool.from_function(
            name="eco_tips",
            description="Suggest eco-friendly alternatives and behavioral changes for waste items.",
            func=self.get_tip
        )


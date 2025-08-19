class WasteClassifier:
    """Tool for classifying waste items into categories"""
    
    def __init__(self):
        self.categories = KnowledgeLoader.load_yaml(
            Config.get_knowledge_file("waste_categories.yaml")
        )
    
    def classify(self, item: str) -> str:
        """Classify waste item into category"""
        item_lower = item.lower()
        
        for category, data in self.categories.items():
            keywords = data.get('keywords', [])
            if any(keyword in item_lower for keyword in keywords):
                description = data.get('description', '')
                return f"{item} is classified as {category} waste. {description}"
        
        return f"Unknown category for {item}. Please check local sorting rules or provide more details."
    
    def get_tool(self) -> Tool:
        """Return LangChain Tool"""
        return Tool.from_function(
            name="waste_classifier",
            description="Classify waste items into recycling categories with detailed guidance.",
            func=self.classify
        )

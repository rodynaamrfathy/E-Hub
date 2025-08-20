from rapidfuzz import process, fuzz
import json
import os
from langchain_core.tools import Tool

class EcoTips:
    def __init__(self):
        self.alternatives_db = self._load_KB()
        self.keyword_map = self._build_keyword_map()

    def _load_KB(self):
        kb_path = 'agents/waste_mangment_agent/tools/eco_friendly_alt/eco_alternatives_knowledge_base.json'
        if not os.path.exists(kb_path):
            raise FileNotFoundError(f"KB not found: {kb_path}")
        with open(kb_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _build_keyword_map(self):
        """Flatten KB into {keyword → metadata} for fast lookup."""
        keyword_map = {}
        for category, items in self.alternatives_db.items():
            for item_name, details in items.items():
                for keyword in details.get("keywords", []):
                    keyword_map[keyword.lower()] = {
                        "category": category,
                        "item": item_name,
                        "alternatives": details.get("alternatives", []),
                    }
        return keyword_map

    def find_best_alternative(self, waste_item: str, threshold: int = 70):
        """Fast keyword search using fuzzy matching."""
        waste_item = waste_item.lower().strip()

        # Fuzzy match against all keywords
        best_match, score, _ = process.extractOne(
            waste_item,
            self.keyword_map.keys(),
            scorer=fuzz.WRatio  
        )

        if score < threshold:
            return {"error": f"No good match found (best score {score})."}

        meta = self.keyword_map[best_match]
        return {
            "category": meta["category"],
            "item": meta["item"],
            "alternatives": meta["alternatives"],
            "matched_keyword": best_match,
            "similarity_score": score,
        }
    def get_tool(self):
         return Tool(
            name="eco_friendly_alternatives",
            description="Find eco-friendly alternatives for a given waste item using fast keyword search.",
            func=lambda query: self.find_best_alternative(query)
        )



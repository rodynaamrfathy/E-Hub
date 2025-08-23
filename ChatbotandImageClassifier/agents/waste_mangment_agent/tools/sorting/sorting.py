import os
import yaml
import logging
from typing import Dict, Tuple, Optional, Any
from fuzzywuzzy import process, fuzz
from langchain.tools import StructuredTool
from langchain.tools import Tool

logger = logging.getLogger(__name__)

class SortingRules:
    """Tool for retrieving Egypt-specific waste sorting and disposal rules."""
    ITEM_MAPPINGS = {
        # Plastic variations
        "plastic bottle": ("plastic", "PET_1"),
        "water bottle": ("plastic", "PET_1"),
        "soda bottle": ("plastic", "PET_1"),
        "soft drink bottle": ("plastic", "PET_1"),
        "cooking oil bottle": ("plastic", "PET_1"),
        "milk jug": ("plastic", "HDPE_2"),
        "detergent bottle": ("plastic", "HDPE_2"),
        "yogurt cup": ("plastic", "PP_5"),
        "takeaway container": ("plastic", "PP_5"),
        "bottle cap": ("plastic", "PP_5"),
        "plastic bag": ("plastic", "LDPE_4_and_film"),
        "shopping bag": ("plastic", "LDPE_4_and_film"),
        
        # Paper variations
        "newspaper": ("paper_cardboard", "clean_paper"),
        "magazine": ("paper_cardboard", "clean_paper"),
        "office paper": ("paper_cardboard", "clean_paper"),
        "cardboard box": ("paper_cardboard", "cardboard"),
        "cardboard": ("paper_cardboard", "cardboard"),
        "pizza box": ("paper_cardboard", "soiled_paper"),
        
        # Glass variations
        "glass bottle": ("glass", "bottles_and_jars"),
        "wine bottle": ("glass", "bottles_and_jars"),
        "jar": ("glass", "bottles_and_jars"),
        "broken glass": ("glass", "broken_glass"),
        
        # Metal variations
        "aluminum can": ("metal", "aluminum_cans"),
        "soda can": ("metal", "aluminum_cans"),
        "coke can": ("metal", "aluminum_cans"),
        "beer can": ("metal", "aluminum_cans"),
        "tin can": ("metal", "steel_tins"),
        "food can": ("metal", "steel_tins"),
        
        # Organic variations
        "food scraps": ("organic", "food_waste"),
        "food waste": ("organic", "food_waste"),
        "vegetable peels": ("organic", "food_waste"),
        "fruit peels": ("organic", "food_waste"),
        "garden waste": ("organic", "garden_waste"),
        "leaves": ("organic", "garden_waste"),
        
        # E-waste variations
        "old phone": ("e_waste", "small_it_phones"),
        "mobile phone": ("e_waste", "small_it_phones"),
        "smartphone": ("e_waste", "small_it_phones"),
        "laptop": ("e_waste", "small_it_phones"),
        "computer": ("e_waste", "small_it_phones"),
        "battery": ("e_waste", "batteries_small"),
        "batteries": ("e_waste", "batteries_small"),
        "refrigerator": ("e_waste", "large_appliances"),
        "washing machine": ("e_waste", "large_appliances"),
        "tv": ("e_waste", "large_appliances"),
        "fluorescent bulb": ("e_waste", "lamps"),
        "cfl bulb": ("e_waste", "lamps"),
        
        # Hazardous variations
        "expired medicine": ("hazardous", "medical_pharmaceuticals"),
        "medication": ("hazardous", "medical_pharmaceuticals"),
        "paint": ("hazardous", "household_chemicals_paint"),
        "chemicals": ("hazardous", "household_chemicals_paint"),
        "cleaning products": ("hazardous", "household_chemicals_paint"),
    }
    def __init__(self):
        """Load YAML rules from knowledge base and build keyword map."""
        self.rules = self._load_KB()
        self.keyword_map = self._build_keyword_map()
        logger.info(f"Loaded {len(self.keyword_map)} keywords into map")

    def _load_KB(self):
        # Get directory of this file (sorting.py)
        base_dir = os.path.dirname(__file__)
        kb_path = os.path.join(base_dir, "sortingegypt_sorting_rules.yaml")

        if not os.path.exists(kb_path):
            raise FileNotFoundError(f"KB not found: {kb_path}")

        with open(kb_path, "r", encoding="utf-8") as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def _build_keyword_map(self) -> Dict[str, Dict[str, Any]]:
        """Build keyword → details map for fast lookup."""
        keyword_map = {}
        egypt_rules = self.rules.get("egypt", {})

        for category, subcategories in egypt_rules.items():
            for subcategory, details in subcategories.items():
                keywords = [category, subcategory]

                if "examples" in details:
                    for example in details["examples"]:
                        keywords.extend([example, f"example {example}"])

                for field in ["do", "dont", "route", "note"]:
                    if field in details:
                        if isinstance(details[field], list):
                            keywords.extend(details[field])
                        else:
                            keywords.append(details[field])

                for kw in keywords:
                    keyword_map[kw.lower()] = {
                        "category": category,
                        "subcategory": subcategory,
                        "details": details,
                        "label": f"{category}_{subcategory}"
                    }
        return keyword_map

    def _normalize_query(self, query: str) -> str:
        return query.lower().strip()

    def _check_direct_mapping(self, query: str) -> Tuple[Optional[Dict], float]:
        """Check if query matches ITEM_MAPPINGS directly."""
        processed_query = self._normalize_query(query)

        if processed_query in self.ITEM_MAPPINGS:
            category, subcategory = self.ITEM_MAPPINGS[processed_query]
            return {
                "category": category,
                "subcategory": subcategory,
                "label": f"{category}_{subcategory}",
                "details": self.rules.get("egypt", {}).get(category, {}).get(subcategory, {})
            }, 1.0

        for mapping_key, (category, subcategory) in self.ITEM_MAPPINGS.items():
            if mapping_key in processed_query or processed_query in mapping_key:
                return {
                    "category": category,
                    "subcategory": subcategory,
                    "label": f"{category}_{subcategory}",
                    "details": self.rules.get("egypt", {}).get(category, {}).get(subcategory, {})
                }, 0.95

        return None, 0.0

    def find_best_alternative(self, waste_item: str, threshold: int = 70):
        """Fast keyword search with fuzzy matching."""
        waste_item = self._normalize_query(waste_item)

        if not self.keyword_map:
            return {"error": "Keyword map is empty."}

        best_match, score = process.extractOne(
            waste_item,
            self.keyword_map.keys(),
            scorer=fuzz.WRatio
        )

        if score < threshold:
            return None, 0.0

        meta = self.keyword_map[best_match]
        return meta, ( score / 100.0 )

    def get_sorting_guidance(self, item: str) -> str:
        """
        Get sorting guidance with priority workflow:
        1. Check predefined ITEM_MAPPINGS (direct rules)
        2. Fall back to fuzzy keyword map search
        """
        if not item or not item.strip():
            return "❌ Please provide an item to get sorting guidance."

        # Step 1: direct mapping
        match, similarity = self._check_direct_mapping(item)

        # Step 2: fuzzy keyword map if no direct match
        if not match:
            match, similarity = self.find_best_alternative(item)

        if not match:
            return f"❌ Sorry, no sorting rules found for '{item}'."

        details = match["details"]
        category = match["category"].replace("_", " ").title()
        subcategory = match["subcategory"].replace("_", " ").title()
        match_type = "Direct Rule" if similarity >= 0.95 else "Fuzzy Match"

        response = [
            f"♻️ **Sorting guidance for '{item}'**",
            f"📂 Category: {category} → {subcategory}",
            f"🎯 Match: {match_type} ({similarity:.1%})",
            ""
        ]

        if "examples" in details:
            response.append("📝 **Examples:**")
            response.extend([f"- {ex}" for ex in details["examples"]])
            response.append("")

        if "do" in details:
            response.append("✅ **What to do:**")
            response.extend([f"- {d}" for d in details["do"]])
            response.append("")

        if "dont" in details:
            response.append("🚫 **What NOT to do:**")
            response.extend([f"- {d}" for d in details["dont"]])
            response.append("")

        if "route" in details:
            response.append(f"📍 **Disposal route:** {details['route']}")
            response.append("")

        if "note" in details:
            response.append(f"💡 **Note:** {details['note']}")
            response.append("")

        return "\n".join(response)
    def get_tool(self) -> Tool:
        """Return LangChain Tool for integration."""
        return Tool.from_function(
            name="waste_sorting_rules",
            description=(
                "Get comprehensive Egypt-specific waste sorting and disposal guidance. "
                "Input should be the name of a waste item (e.g., 'plastic bottle', 'old phone', 'expired medicine'). "
                "Returns detailed sorting instructions including preparation steps, disposal routes, and drop-off locations."
            ),
            func=self.get_sorting_guidance
        )
from langchain_core.tools import Tool
from ...core.config import Config
from ...core.knowledge_loader import KnowledgeLoader
import numpy as np
from numpy.linalg import norm
from ...embedding_module.embedding_config import agent_embedding_module
import torch

class SortingRules:
    """Tool for retrieving Egypt-specific waste sorting and disposal rules."""
    ITEM_MAPPINGS = {
        "plastic bottle": ("plastic", "PET_1"),
        "water bottle": ("plastic", "PET_1"),
        "milk jug": ("plastic", "HDPE_2"),
        "yogurt cup": ("plastic", "PP_5"),
        "newspaper": ("paper_cardboard", "clean_paper"),
        "cardboard box": ("paper_cardboard", "cardboard"),
        "broken glass": ("glass", "broken_glass"),
        "coke can": ("metal", "aluminum_cans"),
        "food scraps": ("organic", "food_waste"),
        "old phone": ("e_waste", "small_it_phones"),
        "battery": ("e_waste", "batteries_small"),
        "expired medicine": ("hazardous", "medical_pharmaceuticals"),
    }

    def __init__(self):
        """Load YAML rules from knowledge base."""
        self.rules = KnowledgeLoader.load_yaml(Config.get_knowledge_file("/Users/maryamsaad/Documents/Agentic_Rag/agents/waste_mangment_agent/tools/sorting/sortingegypt_sorting_rules.yaml"))
        self.embedder = agent_embedding_module()
        self.index = self._build_index()

    def _flatten_entry(self,entry: dict) -> str:
        """Convert a dict entry into a readable text string for embeddings."""
        parts = []
        for k, v in entry.items():
            if isinstance(v, dict):
                parts.append(self._flatten_entry(v))
            elif isinstance(v, list):
                parts.append(" ".join(map(str, v)))
            else:
                parts.append(str(v))
        return " ".join(parts)


    def _build_index(self):
        index = {}
        for category, subs in self.rules.get("egypt", {}).items():
            if isinstance(subs, dict):
                for sub, details in subs.items():
                    if isinstance(details, dict):
                        text = self._flatten_entry(details)
                    else:
                        text = str(details)
                    index[f"{category}:{sub}".lower()] = text
            else:
                index[category.lower()] = str(subs)
        return index



    def _find_best_match(self, query, threshold=0.75):
        """Find best matching rule for query using cosine similarity"""
    
        q_emb = self.embedder.embed([query])
        # Convert to numpy if it's a tensor
        if isinstance(q_emb, torch.Tensor):
            q_emb = q_emb.cpu().numpy()[0]  # Get first (and only) embedding
        
        sims = []
        for entry in self.index:
            # Calculate cosine similarity
            sim = np.dot(q_emb, entry["embedding"]) / (
                norm(q_emb) * norm(entry["embedding"]) + 1e-9  
            )
            sims.append((sim, entry))

        best_sim, best_entry = max(sims, key=lambda x: x[0])
        if best_sim >= threshold:
            return best_entry, best_sim
        return None, 0.0

    def get_rules(self, waste_category: str, region: str = Config.DEFAULT_REGION) -> str:
        """Get raw sorting rules for a category in a given region."""
        region_rules = self.rules.get(region, {})
        category_rules = region_rules.get(waste_category.lower(), {})

        if not category_rules:
            return (
                f"No specific sorting rules found for '{waste_category}' in {region}. "
                f"Please check with local authorities."
            )

        # Format simple rules if available
        rules_text = [f"Sorting rules for {waste_category} in {region}:"]
        if "disposal_method" in category_rules:
            rules_text.append(f"• Disposal: {category_rules['disposal_method']}")
        if "preparation" in category_rules:
            rules_text.append(f"• Preparation: {category_rules['preparation']}")
        if "locations" in category_rules:
            rules_text.append(
                f"• Drop-off locations: {', '.join(category_rules['locations'])}"
            )
        if "notes" in category_rules:
            rules_text.append(f"• Note: {category_rules['notes']}")

        return "\n".join(rules_text)

    def get_sorting_guidance(self, item: str, country="egypt") -> str:
        """Semantic search for item and return guidance"""
        match, similarity = self._find_best_match(item)
        if not match:
            return f"❌ Sorry, I couldn't find a rule for '{item}'. Please try again with more specific terms."

        details = match["details"]
        response = [
            f"♻️ Sorting guidance for **{item}** ({match['category']} → {match['sub']}):",
            f"🎯 Confidence: {similarity:.2%}"
        ]

        if "do" in details:
            response.append("✅ Do:\n- " + "\n- ".join(details["do"]))
        if "dont" in details:
            response.append("🚫 Don't:\n- " + "\n- ".join(details["dont"]))
        if "route" in details:
            response.append(f"📍 Route: {details['route']}")
        if "dropoff" in details:
            response.append("📦 Drop-off points:\n- " + "\n- ".join(details["dropoff"]))
        if "policy_reference" in details:
            response.append("⚖️ Policy References:\n- " + "\n- ".join(details["policy_reference"]))

        return "\n\n".join(response)

    def get_similar_items(self, item: str, top_k=3) -> list:
        """Get top-k most similar items for suggestions"""
        q_emb = self.embedder.embed([item])
        
        if isinstance(q_emb, torch.Tensor):
            q_emb = q_emb.cpu().numpy()[0]
        
        similarities = []
        for entry in self.index:
            sim = np.dot(q_emb, entry["embedding"]) / (
                norm(q_emb) * norm(entry["embedding"]) + 1e-9
            )
            similarities.append((sim, entry["label"], entry))
        
        # Sort by similarity and return top-k
        similarities.sort(key=lambda x: x[0], reverse=True)
        return similarities[:top_k]

    def get_tool(self) -> Tool:
        """Return LangChain Tool for integration."""
        return Tool.from_function(
            name="sorting_rules",
            description="Get region-specific waste sorting and disposal guidance using semantic search.",
            func=self.get_sorting_guidance
        )
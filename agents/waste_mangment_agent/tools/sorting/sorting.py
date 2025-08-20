from langchain_core.tools import Tool
from ...core.config import Config
from ...core.knowledge_loader import KnowledgeLoader
import numpy as np
from numpy.linalg import norm
from ...embedding_module.embedding_config import agent_embedding_module
import torch
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

class SortingRules:
    """Tool for retrieving Egypt-specific waste sorting and disposal rules."""
    
    # Enhanced item mappings with synonyms and variations
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
        """Load YAML rules from knowledge base and build semantic index."""
        try:
            self.rules = KnowledgeLoader.load_yaml(
                Config.get_knowledge_file(
                    "/Users/maryamsaad/Documents/Agentic_Rag/agents/waste_mangment_agent/tools/sorting/sortingegypt_sorting_rules.yaml"
                )
            )
            self.embedder = agent_embedding_module()
            self.index = self._build_semantic_index()
            logger.info(f"Loaded {len(self.index)} sorting rules")
        except Exception as e:
            logger.error(f"Error initializing SortingRules: {e}")
            self.rules = {}
            self.index = []

    def _flatten_entry(self, entry: dict) -> str:
        """Convert a dict entry into a readable text string for embeddings."""
        parts = []
        for k, v in entry.items():
            if k == "examples" and isinstance(v, list):
                parts.extend([f"example: {ex}" for ex in v])
            elif isinstance(v, dict):
                parts.append(self._flatten_entry(v))
            elif isinstance(v, list):
                parts.extend([str(item) for item in v])
            else:
                parts.append(str(v))
        return " ".join(parts)

    def _build_semantic_index(self) -> List[Dict[str, Any]]:
        """Build semantic index with embeddings for all waste categories."""
        index = []
        
        egypt_rules = self.rules.get("egypt", {})
        
        for category, subcategories in egypt_rules.items():
            if not isinstance(subcategories, dict):
                continue
                
            for subcategory, details in subcategories.items():
                if not isinstance(details, dict):
                    continue
                
                # Create searchable text
                search_text_parts = []
                
                # Add category and subcategory names
                search_text_parts.extend([category, subcategory])
                
                # Add examples with higher weight
                if "examples" in details:
                    for example in details["examples"]:
                        search_text_parts.extend([example, f"example {example}"])
                
                # Add other relevant fields
                for field in ["do", "dont", "route", "note"]:
                    if field in details:
                        if isinstance(details[field], list):
                            search_text_parts.extend(details[field])
                        else:
                            search_text_parts.append(details[field])
                
                search_text = " ".join(search_text_parts).lower()
                
                # Generate embedding
                try:
                    embedding = self.embedder.embed([search_text])
                    if isinstance(embedding, torch.Tensor):
                        embedding = embedding.cpu().numpy()[0]
                    elif isinstance(embedding, list) and len(embedding) > 0:
                        embedding = np.array(embedding[0])
                    
                    index.append({
                        "category": category,
                        "subcategory": subcategory,
                        "details": details,
                        "search_text": search_text,
                        "embedding": embedding,
                        "label": f"{category}_{subcategory}"
                    })
                except Exception as e:
                    logger.warning(f"Failed to embed {category}:{subcategory}: {e}")
                    continue
        
        return index

    def _preprocess_query(self, query: str) -> str:
        """Preprocess user query to improve matching."""
        query = query.lower().strip()
        
        # Handle common variations and typos
        replacements = {
            "bottel": "bottle",
            "botlle": "bottle",
            "platic": "plastic",
            "aluminun": "aluminum",
            "aluminium": "aluminum",
            "magazin": "magazine",
            "newspapper": "newspaper",
            "phon": "phone",
            "btery": "battery",
            "baterry": "battery",
            "medicin": "medicine",
            "medecine": "medicine",
        }
        
        for wrong, correct in replacements.items():
            query = query.replace(wrong, correct)
        
        return query

    def _check_direct_mapping(self, query: str) -> Tuple[Optional[Dict], float]:
        """Check if query matches any predefined item mappings."""
        processed_query = self._preprocess_query(query)
        
        # Exact match in mappings
        if processed_query in self.ITEM_MAPPINGS:
            category, subcategory = self.ITEM_MAPPINGS[processed_query]
            for entry in self.index:
                if entry["category"] == category and entry["subcategory"] == subcategory:
                    logger.info(f"Direct mapping found: {query} -> {category}:{subcategory}")
                    return entry, 1.0
        
        # Partial match in mappings (if query contains mapping key)
        for mapping_key, (category, subcategory) in self.ITEM_MAPPINGS.items():
            if mapping_key in processed_query or processed_query in mapping_key:
                for entry in self.index:
                    if entry["category"] == category and entry["subcategory"] == subcategory:
                        logger.info(f"Partial mapping found: {query} -> {category}:{subcategory}")
                        return entry, 0.95  # High confidence but not perfect
        
        return None, 0.0

    def _find_semantic_match(self, query: str, threshold: float = 0.6) -> Tuple[Optional[Dict], float]:
        """Find best matching rule using semantic similarity search."""
        if not self.index:
            return None, 0.0
        
        try:
            processed_query = self._preprocess_query(query)
            
            # Generate query embedding
            q_embedding = self.embedder.embed([processed_query])
            if isinstance(q_embedding, torch.Tensor):
                q_embedding = q_embedding.cpu().numpy()[0]
            elif isinstance(q_embedding, list) and len(q_embedding) > 0:
                q_embedding = np.array(q_embedding[0])
            else:
                return None, 0.0
            
            # Calculate similarities
            similarities = []
            for entry in self.index:
                try:
                    # Cosine similarity
                    dot_product = np.dot(q_embedding, entry["embedding"])
                    norm_product = norm(q_embedding) * norm(entry["embedding"])
                    
                    if norm_product == 0:
                        similarity = 0.0
                    else:
                        similarity = dot_product / norm_product
                    
                    similarities.append((similarity, entry))
                except Exception as e:
                    logger.warning(f"Error calculating similarity for {entry['label']}: {e}")
                    continue
            
            if not similarities:
                return None, 0.0
            
            # Find best match
            best_similarity, best_entry = max(similarities, key=lambda x: x[0])
            
            if best_similarity >= threshold:
                logger.info(f"Semantic match found: {query} -> {best_entry['category']}:{best_entry['subcategory']} (similarity: {best_similarity:.3f})")
                return best_entry, best_similarity
            else:
                logger.info(f"No semantic match above threshold for: {query} (best similarity: {best_similarity:.3f})")
                return None, best_similarity
                
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return None, 0.0

    def _find_best_match(self, query: str, threshold: float = 0.6) -> Tuple[Optional[Dict], float]:
        """Find best matching rule - prioritize direct mappings, fall back to semantic search."""
        if not query or not query.strip():
            return None, 0.0
        
        # Step 1: Try direct mapping first
        match, confidence = self._check_direct_mapping(query)
        if match:
            return match, confidence
        
        # Step 2: Fall back to semantic similarity search
        logger.info(f"No direct mapping found for '{query}', trying semantic search...")
        return self._find_semantic_match(query, threshold)

    def get_sorting_guidance(self, item: str, country: str = "egypt") -> str:
        """
        Get sorting guidance with priority workflow:
        1. Check predefined ITEM_MAPPINGS (direct rules)
        2. Fall back to semantic similarity search if not found
        3. Provide suggestions if no good match
        """
        if not item or not item.strip():
            return "❌ Please provide an item to get sorting guidance."
        
        # Try to find match using our prioritized workflow
        match, similarity = self._find_best_match(item)
        
        if not match:
            # No good match found - provide suggestions
            logger.info(f"No match found for '{item}', providing suggestions...")
            suggestions = self.get_similar_items(item, top_k=3)
            if suggestions:
                suggestion_text = "\n".join([f"- {s[1]} (similarity: {s[0]:.1%})" for s in suggestions])
                return (f"❌ No exact match found for '{item}'. "
                       f"Did you mean one of these?\n{suggestion_text}\n\n"
                       f"💡 Try being more specific or check available categories.")
            else:
                return (f"❌ Sorry, I couldn't find sorting rules for '{item}'. "
                       "Please try with more specific terms or check with local authorities.")

        # Format the response
        details = match["details"]
        category = match["category"].replace("_", " ").title()
        subcategory = match["subcategory"].replace("_", " ").title()
        
        # Indicate match type in confidence display
        match_type = "Direct Rule" if similarity >= 0.95 else "Semantic Match"
        
        response = [
            f"♻️ **Sorting guidance for '{item}'**",
            f"📂 Category: {category} → {subcategory}",
            f"🎯 Match: {match_type} ({similarity:.1%})",
            ""
        ]

        # Add examples if available
        if "examples" in details:
            response.append("📝 **Examples:**")
            response.append("- " + "\n- ".join(details["examples"]))
            response.append("")

        # Add preparation steps
        if "do" in details:
            response.append("✅ **What to do:**")
            response.append("- " + "\n- ".join(details["do"]))
            response.append("")
        
        if "dont" in details:
            response.append("🚫 **What NOT to do:**")
            response.append("- " + "\n- ".join(details["dont"]))
            response.append("")
        
        # Add disposal route
        if "route" in details:
            response.append(f"📍 **Disposal route:** {details['route']}")
            response.append("")
        
        # Add drop-off locations
        if "dropoff" in details:
            response.append("📦 **Drop-off points:**")
            response.append("- " + "\n- ".join(details["dropoff"]))
            response.append("")
        
        # Add additional notes
        if "note" in details:
            response.append(f"💡 **Note:** {details['note']}")
            response.append("")
        
        # Add policy references
        if "policy_reference" in details:
            response.append("⚖️ **Legal/Policy References:**")
            response.append("- " + "\n- ".join(details["policy_reference"]))
            response.append("")
        
        # Add general rules reference for context
        general_rules = self.rules.get("egypt", {}).get("general_rules", {})
        if general_rules and similarity < 0.95:  # Only show for semantic matches
            response.append("📋 **General Guidelines:**")
            for rule_name, rule_text in general_rules.items():
                response.append(f"- {rule_name.replace('_', ' ').title()}: {rule_text}")

        return "\n".join(response)

    def get_similar_items(self, item: str, top_k: int = 3) -> List[Tuple[float, str, Dict]]:
        """Get top-k most similar items for suggestions."""
        if not self.index:
            return []
        
        try:
            processed_query = self._preprocess_query(item)
            q_embedding = self.embedder.embed([processed_query])
            
            if isinstance(q_embedding, torch.Tensor):
                q_embedding = q_embedding.cpu().numpy()[0]
            elif isinstance(q_embedding, list) and len(q_embedding) > 0:
                q_embedding = np.array(q_embedding[0])
            else:
                return []
            
            similarities = []
            for entry in self.index:
                try:
                    dot_product = np.dot(q_embedding, entry["embedding"])
                    norm_product = norm(q_embedding) * norm(entry["embedding"])
                    
                    if norm_product == 0:
                        similarity = 0.0
                    else:
                        similarity = dot_product / norm_product
                    
                    # Create readable label
                    label = f"{entry['category'].replace('_', ' ').title()}: {entry['subcategory'].replace('_', ' ').title()}"
                    if "examples" in entry["details"]:
                        label += f" (e.g., {entry['details']['examples'][0]})"
                    
                    similarities.append((similarity, label, entry))
                except Exception as e:
                    logger.warning(f"Error calculating similarity for suggestions: {e}")
                    continue
            
            # Sort by similarity and return top-k
            similarities.sort(key=lambda x: x[0], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error getting similar items: {e}")
            return []

    def get_category_overview(self, category: str) -> str:
        """Get overview of all items in a category."""
        egypt_rules = self.rules.get("egypt", {})
        category_data = egypt_rules.get(category.lower(), {})
        
        if not category_data:
            available_categories = list(egypt_rules.keys())
            return (f"Category '{category}' not found. "
                   f"Available categories: {', '.join(available_categories)}")
        
        response = [f"📂 **{category.title()} Waste Category Overview**", ""]
        
        for subcategory, details in category_data.items():
            if isinstance(details, dict):
                response.append(f"🔹 **{subcategory.replace('_', ' ').title()}**")
                
                if "examples" in details:
                    response.append(f"   Examples: {', '.join(details['examples'])}")
                
                if "route" in details:
                    response.append(f"   Route: {details['route']}")
                elif "do" in details and details["do"]:
                    response.append(f"   Action: {details['do'][0]}")
                
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
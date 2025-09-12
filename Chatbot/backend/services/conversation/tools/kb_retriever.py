##create schema
## embed current KB into DB
## set up retreiver logic
from Chatbot.backend.services.mcp.db_adapter import run_query, run_query_params
from Chatbot.backend.services.utils.kb_handler import KB_handler
from Chatbot.backend.services.conversation.tools.rag_handler import article_retriever
import yaml
import json
import uuid
from typing import List, Dict, Any, Optional
import os
import time
import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

class embedder:
    def __init__(self):
        """Initialize the processor with API configuration."""
        self.api_key = os.getenv("GOOGLE_API_KEY_M")
        genai.configure(api_key=self.api_key)
        self.model = "models/gemini-embedding-exp-03-07"

    def get_embeddings(self, texts):
        """Get embeddings for a list of texts."""
        embeddings = []    
        for i, text in enumerate(texts):
            try:
                response = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="SEMANTIC_SIMILARITY",
                    output_dimensionality=768
                )
                if "embedding" in response:
                    embeddings.append(response["embedding"])
                if i < len(texts) - 1:
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error processing text {i + 1}: {e}")
                continue
        
        return np.array(embeddings)

class KB_Retriever:
    def __init__(self):
        self.embedder = embedder()
        self.kb_path = "/Users/maryamsaad/Documents/E-Hub/Chatbot/backend/services/utils/KB.yaml"
    
    def load_yaml_kb(self):
        """Load and parse the YAML KB file properly."""
        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if not data or 'kb_entries' not in data:
                print("⚠️ No kb_entries found in YAML file")
                return []
            
            return data['kb_entries']
        except Exception as e:
            print(f"Error loading YAML file: {e}")
            return []
    
    def create_parent_id_mapping(self, entries):
        """Create a mapping from old IDs to new UUIDs for parent_id references."""
        id_mapping = {}
        
        # First pass: create UUIDs for all entries
        for entry in entries:
            old_id = entry.get('id')
            if old_id:
                id_mapping[old_id] = str(uuid.uuid4())
        
        return id_mapping
    
    def insert_kb_entry(self, entry, id_mapping):
        """Insert a single KB entry into the database."""
        try:
            # Get the new UUID for this entry
            old_id = entry.get('id')
            new_id = id_mapping.get(old_id, str(uuid.uuid4()))
            
            # Prepare data
            content_type = entry.get('content_type', 'unknown')
            title = entry.get('title', '')
            content = entry.get('content', '')
            metadata = entry.get('metadata', {})
            keywords = entry.get('keywords', [])
            parent_id = entry.get('parent_id')
            
            # Convert parent_id to new UUID if it exists
            if parent_id and parent_id in id_mapping:
                parent_id = id_mapping[parent_id]
            else:
                parent_id = None
            
            # Generate embedding
            embedding_text = f"{title}. {content}"
            embeddings = self.embedder.get_embeddings([embedding_text])
            
            if len(embeddings) == 0:
                print(f"Failed to generate embedding for: {title}")
                return None
            
            embedding = embeddings[0].tolist()
            
            # Prepare SQL query with proper parameterization
            sql = """
                INSERT INTO kb_content (id, content_type, title, content, metadata, keywords, parent_id, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """
            
            # Execute the query with parameters
            result = run_query_params(
                sql, 
                params=(
                    new_id,
                    content_type,
                    title,
                    content,
                    json.dumps(metadata),
                    keywords,
                    parent_id,
                    json.dumps(embedding)
                ),
                fetch=True
            )
            
            if result:
                print(f"✅ Successfully inserted: {title} (ID: {new_id})")
                return new_id
            else:
                print(f"❌ Failed to insert: {title}")
                return None
                
        except Exception as e:
            print(f"Error inserting entry {entry.get('title', 'Unknown')}: {e}")
            return None
    
    def populate_database(self):
        """Load YAML KB and populate the database."""
        print(" Loading YAML KB file...")
        entries = self.load_yaml_kb()
        
        if not entries:
            print("❌ No entries found to insert")
            return False
        
        print(f" Found {len(entries)} entries to process")
        
        # Create ID mapping for parent_id references
        id_mapping = self.create_parent_id_mapping(entries)
        print(f"🆔 Created {len(id_mapping)} ID mappings")
        
        # Clear existing data (optional - remove if you want to keep existing data)
        print("🗑️ Clearing existing KB data...")
        run_query("DELETE FROM kb_content", fetch=False)
        
        # Insert entries
        successful_inserts = 0
        failed_inserts = 0
        
        for i, entry in enumerate(entries, 1):
            print(f"📝 Processing entry {i}/{len(entries)}: {entry.get('title', 'Unknown')}")
            
            result = self.insert_kb_entry(entry, id_mapping)
            if result:
                successful_inserts += 1
            else:
                failed_inserts += 1
        
        print(f"\n Summary:")
        print(f"✅ Successfully inserted: {successful_inserts}")
        print(f"❌ Failed inserts: {failed_inserts}")
        print(f"📊 Total processed: {len(entries)}")
        
        return successful_inserts > 0
    
    def search_kb(self, query, top_k=5, threshold=0.7):
        """Search the KB using semantic similarity."""
        try:
            # Get all entries with embeddings
            sql = """
                SELECT id, content_type, title, content, metadata, keywords, parent_id, embedding
                FROM kb_content 
                WHERE embedding IS NOT NULL
            """
            rows = run_query(sql, fetch=True)
            
            if not rows:
                print("No entries found in database")
                return []
            
            # Parse embeddings
            parsed_embeddings, valid_rows = [], []
            for row in rows:
                embedding = self._parse_embedding(row["embedding"])
                if embedding is not None:
                    parsed_embeddings.append(embedding)
                    valid_rows.append(row)
            
            if not parsed_embeddings:
                print("No valid embeddings found")
                return []
            
            # Get query embedding
            query_emb = self.embedder.get_embeddings([query])
            if len(query_emb) == 0:
                print("Failed to generate query embedding")
                return []
            
            query_emb = np.array(query_emb[0], dtype=float).reshape(1, -1)
            embeddings_matrix = np.vstack(parsed_embeddings).astype(float)
            
            # Calculate similarities
            similarities = cosine_similarity(query_emb, embeddings_matrix)[0]
            top_indices = np.argsort(similarities)[::-1]
            
            # Return top results
            results = []
            for i in top_indices[:top_k]:
                if similarities[i] < threshold:
                    continue
                    
                row = valid_rows[i]
                results.append({
                    "id": row["id"],
                    "content_type": row["content_type"],
                    "title": row["title"],
                    "content": row["content"],
                    "metadata": row["metadata"],
                    "keywords": row["keywords"],
                    "parent_id": row["parent_id"],
                    "similarity_score": float(similarities[i])
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching KB: {e}")
            return []
    
    def _parse_embedding(self, embedding_data):
        """Parse embedding data from database."""
        try:
            if isinstance(embedding_data, str):
                return np.array(json.loads(embedding_data), dtype=float)
            elif isinstance(embedding_data, (list, tuple)):
                return np.array(embedding_data, dtype=float)
            else:
                return None
        except Exception:
            return None

# Usage example
if __name__ == "__main__":
    retriever = KB_Retriever()
    
    # Populate database from YAML
    print(" Starting KB population...")
    success = retriever.populate_database()
    
    if success:
        print("\n🔍 Testing search functionality...")
        # Test search
        results = retriever.search_kb("waste management solutions", top_k=3)
        for result in results:
            print(f"📄 {result['title']} (Score: {result['similarity_score']:.3f})")
    else:
        print("❌ Failed to populate database")
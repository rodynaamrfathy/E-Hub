## this script populates the db with the original yaml file kb
from Chatbot.backend.services.mcp.db_adapter import run_query, run_query_params
from Chatbot.backend.services.conversation.tools.embeddermodel import embedder
import yaml
import json
import uuid
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()
run_query("CREATE EXTENSION IF NOT EXISTS vector;")
run_query("""
CREATE TABLE IF NOT EXISTS kb_content (
    id UUID PRIMARY KEY,
    content_type TEXT,
    title TEXT,
    content TEXT,
    metadata JSONB,
    keywords TEXT[],
    embedding VECTOR(768)
);
""")

class KB_Retriever:
    def __init__(self):
        self.embedder = embedder()
        self.kb_path = "/Users/maryamsaad/Documents/E-Hub/Chatbot/backend/services/utils/KB.yaml"

    def load_yaml_kb(self):
        """Load and parse the YAML KB file properly."""
        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return data["kb_entries"]
        except Exception as e:
            print(f"Error loading YAML file: {e}")
            return []

    def create_id_mapping(self, entries):
        """Create a mapping from old IDs to new UUIDs."""
        id_mapping = {}
        for entry in entries:
            old_id = entry.get("id")
            if old_id:
                id_mapping[old_id] = str(uuid.uuid4())
        return id_mapping

    def insert_kb_entry(self, entry, id_mapping):
        """Insert a single KB entry into the database."""
        try:
            old_id = entry.get("id")
            new_id = id_mapping.get(old_id, str(uuid.uuid4()))

            # Prepare data
            content_type = entry.get("content_type", "unknown")
            title = entry.get("title", "")
            content = entry.get("content", "")
            metadata = entry.get("metadata", {})
            keywords = entry.get("keywords", [])

            # Generate embedding
            embedding_text = f"{title}. {content}"
            embeddings = self.embedder.get_embeddings([embedding_text])

            if len(embeddings) == 0:
                print(f"⚠️ Failed to generate embedding for: {title}")
                return None

            embedding = embeddings[0].tolist()

            # Insert into DB
            sql = """
                INSERT INTO kb_content (id, content_type, title, content, metadata, keywords, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """

            result = run_query_params(
                sql,
                params=(
                    new_id,
                    content_type,
                    title,
                    content,
                    json.dumps(metadata),
                    keywords,
                    json.dumps(embedding),
                ),
                fetch=True,
            )

            if result:
                print(f"✅ Successfully inserted: {title} (ID: {new_id})")
                return new_id
            else:
                print(f"❌ Failed to insert: {title}")
                return None

        except Exception as e:
            print(f"❌ Error inserting entry {entry.get('title', 'Unknown')}: {e}")
            return None

    def populate_database(self):
        """Load YAML KB and populate the database."""
        print("📂 Loading YAML KB file...")
        entries = self.load_yaml_kb()

        print(f"🔎 Found {len(entries)} entries to process")

        # Create ID mapping
        id_mapping = self.create_id_mapping(entries)
        print(f"🆔 Created {len(id_mapping)} ID mappings")

        # Clear existing data
        print("🗑️ Clearing existing KB data...")
        run_query("DELETE FROM kb_content", fetch=False)

        successful_inserts, failed_inserts = 0, 0
        for i, entry in enumerate(entries, 1):
            print(f"📝 Processing entry {i}/{len(entries)}: {entry.get('title', 'Unknown')}")
            result = self.insert_kb_entry(entry, id_mapping)
            if result:
                successful_inserts += 1
            else:
                failed_inserts += 1

        print("\n📊 Summary:")
        print(f"✅ Successfully inserted: {successful_inserts}")
        print(f"❌ Failed inserts: {failed_inserts}")
        print(f"📦 Total processed: {len(entries)}")

        return successful_inserts > 0

    def search_kb(self, query, top_k=5, threshold=0.7):
        """Search the KB using semantic similarity."""
        try:
            sql = """
                SELECT id, content_type, title, content, metadata, keywords, embedding
                FROM kb_content
                WHERE embedding IS NOT NULL
            """
            rows = run_query(sql, fetch=True)

            if not rows:
                print("⚠️ No entries found in database")
                return []

            parsed_embeddings, valid_rows = [], []
            for row in rows:
                embedding = self._parse_embedding(row["embedding"])
                if embedding is not None:
                    parsed_embeddings.append(embedding)
                    valid_rows.append(row)

            if not parsed_embeddings:
                print("⚠️ No valid embeddings found")
                return []

            # Encode query
            query_emb = self.embedder.get_embeddings([query])
            if len(query_emb) == 0:
                print("⚠️ Failed to generate query embedding")
                return []

            query_emb = np.array(query_emb[0], dtype=float).reshape(1, -1)
            embeddings_matrix = np.vstack(parsed_embeddings).astype(float)

            # Similarity scores
            similarities = cosine_similarity(query_emb, embeddings_matrix)[0]
            top_indices = np.argsort(similarities)[::-1]

            results = []
            for i in top_indices[:top_k]:
                if similarities[i] < threshold:
                    continue

                row = valid_rows[i]
                results.append(
                    {
                        "id": row["id"],
                        "content_type": row["content_type"],
                        "title": row["title"],
                        "content": row["content"],
                        "metadata": row["metadata"],
                        "keywords": row["keywords"],
                        "similarity_score": float(similarities[i]),
                    }
                )

            return results

        except Exception as e:
            print(f"❌ Error searching KB: {e}")
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
# if __name__ == "__main__":
#     retriever = KB_Retriever()
#     print("🚀 Starting KB population...")
#     success = retriever.populate_database()
#     print("\n🔍 Testing search functionality...")
#     prompt="does dawar recycle carpets?"
#     results = retriever.search_kb(prompt, top_k=5)
#     for result in results:
#         print(f"📄 {result['title']} (Score: {result['similarity_score']:.3f})")
#         print(f'content= {result['content']}')
#     else:
#         print("❌ Failed to populate database")

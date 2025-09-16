from operator import imod
from services.conversation.tools.embeddermodel import embedder
from services.mcp.db_adapter import run_query
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

class kb_retriever:
    def __init__(self) :
        self.embedder= embedder()

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


        except Exception as e:
            print(f"❌ Error searching KB: {e}")
            return []


# search=kb_retriever()
# result=search.search_kb("what is the diffrence between environ and dawar?")
# print(result)
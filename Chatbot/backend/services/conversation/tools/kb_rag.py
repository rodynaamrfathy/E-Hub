from operator import imod
from services.conversation.tools.embeddermodel import embedder
from services.db.postgres import db_manager
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from services.repositories.kb_service import KBContentService

class kb_retriever:
    def __init__(self) :
        self.embedder= embedder()
        

    async def _get_service(self):
        """Context manager that yields a KBContentService bound to a fresh session."""
        class _SvcCtx:
            async def __aenter__(self_inner):
                self_inner._session_ctx = db_manager.get_session()
                self_inner._session = await self_inner._session_ctx.__aenter__()
                self_inner.service = KBContentService(self_inner._session)
                return self_inner.service
            async def __aexit__(self_inner, exc_type, exc, tb):
                await self_inner._session_ctx.__aexit__(exc_type, exc, tb)
        return _SvcCtx()

    async def search_kb(self, query, top_k=5, threshold=0.7):
        """Search the KB using semantic similarity."""

        try:
            async with await self._get_service() as service:
                rows = await service.get_all_embeddings()

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
            # Already a numpy array or list-like
            if hasattr(embedding_data, "tolist"):
                return np.asarray(embedding_data, dtype=float).reshape(-1)
            if isinstance(embedding_data, (list, tuple)):
                return np.asarray(embedding_data, dtype=float).reshape(-1)

            # Memoryview / bytes containing JSON text or comma-separated values
            if isinstance(embedding_data, (memoryview, bytes, bytearray)):
                text = bytes(embedding_data).decode("utf-8", errors="ignore").strip()
                if text:
                    try:
                        return np.asarray(json.loads(text), dtype=float).reshape(-1)
                    except Exception:
                        parts = [p for p in text.replace("[", "").replace("]", "").split(",") if p.strip()]
                        return np.asarray([float(x) for x in parts], dtype=float).reshape(-1)
                return None

            # String with JSON array or comma-separated numbers
            if isinstance(embedding_data, str):
                s = embedding_data.strip()
                if s.startswith("["):
                    return np.asarray(json.loads(s), dtype=float).reshape(-1)
                parts = [p for p in s.split(",") if p.strip()]
                return np.asarray([float(x) for x in parts], dtype=float).reshape(-1)

            return None
        except Exception:
            return None


        except Exception as e:
            print(f"❌ Error searching KB: {e}")
            return []


# search=kb_retriever()
# result=search.search_kb("what is the diffrence between environ and dawar?")
# print(result)
import os
import time
import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from services.db.postgres import db_manager
from services.repositories.article_service import ArticleService

import json

load_dotenv()

class article_retriever:
    
    def __init__(self):
        """Initialize the processor with API configuration."""
        self.api_key = os.getenv("GOOGLE_API_KEY_MM")
        genai.configure(api_key=self.api_key)
        self.model = "models/gemini-embedding-exp-03-07"
        self.service = None

    async def init_service(self):
        """Initialize Article service with async DB session."""
        self._session_ctx = db_manager.get_session()
        self._session = await self._session_ctx.__aenter__()
        self.service = ArticleService(self._session)

    async def _close(self):
        if hasattr(self, "_session_ctx"):
            await self._session_ctx.__aexit__(None, None, None)
    
    def get_embeddings(self, texts):
        """Get embeddings for a list of texts."""
        embeddings = []
        print(f"Processing prompt ...")
        
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

    def _to_float_array(self,val, expected_dim=768):
        if val is None:
            return None
        try:
            if isinstance(val, (list, tuple, np.ndarray)):
                arr = np.asarray(val, dtype=float)
            elif isinstance(val, (bytes, bytearray)):
                s = val.decode("utf-8", errors="ignore").strip()
                arr = np.asarray(json.loads(s), dtype=float)
            elif isinstance(val, str):
                s = val.strip()
                if s.startswith("["):
                    arr = np.asarray(json.loads(s), dtype=float)
                else:
                    arr = np.asarray([float(x) for x in s.split(",")], dtype=float)
            else:
                return None
            arr = arr.reshape(-1)
            if expected_dim is not None and arr.size != expected_dim:
                return None
            return arr
        except Exception:
            return None

        
    def get_similarity(self, query, rows, embeddings, top_k=3, threshold=0.90):
        """Return top-k similar articles with metadata and query prompt."""
        query_emb = self.get_embeddings([query]) 
        query_emb = np.array(query_emb, dtype=float).reshape(1, -1)

        sims = cosine_similarity(query_emb, embeddings)[0]
        top_idx = np.argsort(sims)[::-1]

        results = []
        for i in top_idx[:top_k]:
            if sims[i] < threshold:
                continue
            row = rows[i]
            results.append({
                "title": row["title"],
                "url": row["url"],
                "summary": row["summary"],
                "similarity_score": float(sims[i]),
                "prompt": query
            })
        return results

    async def article_search(self,prompt):
        if self.service is None:
            await self.init_service()

        rows = await self.service.get_all_articles()

        if not rows:
            print("⚠️ No articles found")
            return []
        # Build embeddings on the fly from article summaries (or content)
        texts = []
        valid_rows = []
        for row in rows:
            text = row.get("summary") or row.get("content") or row.get("title")
            if text:
                texts.append(text)
                valid_rows.append(row)

        if not texts:
            return []

        embeddings = self.get_embeddings(texts)
        if embeddings is None or len(embeddings) == 0:
            return []

        embeddings = np.asarray(embeddings, dtype=float)
        results = self.get_similarity(prompt, valid_rows, embeddings)
        return results

    async def get_references(self, prompt, max_results=5):
        article_results = await self.article_search(prompt)

        references = []
        for art in article_results[:max_results]:
            title = art.get("title")
            url = art.get("url")
            # Fallback: try to infer a URL from content if missing (very naive)
            if not url and art.get("content"):
                text = art.get("content")
                start = text.find("http")
                if start != -1:
                    end = text.find(" ", start)
                    url = text[start:end] if end != -1 else text[start:]
            references.append({
                "title": title or "Untitled",
                "url": url
            })
        return references




  
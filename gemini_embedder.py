import os
import time
import google.generativeai as genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from Chatbot.backend.services.mcp.db_adapter import run_query
import json

load_dotenv()

class EmbeddingProcessor:
    
    def __init__(self):
        """Initialize the processor with API configuration."""
        self.api_key = os.getenv("GOOGLE_API_KEY_M")
        genai.configure(api_key=self.api_key)
        self.model = "models/gemini-embedding-exp-03-07"
    
    def get_embeddings(self, texts):
        """Get embeddings for a list of texts."""
        embeddings = []
        print(f"Processing {len(texts)} texts...")
        
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
    
    def get_similarity(self, query, rows, embeddings, top_k=3, threshold=0.70):
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


def _to_float_array(val, expected_dim=768):
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


# === Example Usage ===
queries = [
    "Irrigation techniques used by farmers",
    "solar energy in Egypt",
    "Renewable energy capacity improvements",
    "Waste-to-energy power plants"
]

embedder_model = EmbeddingProcessor()
rows = run_query("SELECT id, title, url, summary, embeddings FROM articles", fetch=True)

parsed_embeddings, valid_rows = [], []
for row in rows:
    arr = _to_float_array(row["embeddings"], expected_dim=768)
    if arr is not None:
        parsed_embeddings.append(arr)
        valid_rows.append(row)

embeddings = np.vstack(parsed_embeddings).astype(float)

for query in queries:
    results = embedder_model.get_similarity(query, valid_rows, embeddings)
    print(f"\nQuery: {query}")
    for r in results:
        print(f"{r['similarity_score']:.3f} -> {r['title']} ({r['url']})")
        print(f"Summary: {r['summary']}")
        print(f"Prompt: {r['prompt']}")
        print("-" * 80)

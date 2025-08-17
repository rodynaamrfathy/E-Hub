from sentence_transformers import CrossEncoder
import logging as logger
from tqdm import tqdm
from langchain.schema import Document
from rag_pipeline.config.settings import DEFAULT_RERANKER_MODEL, RERANKER_CACHE_DIR
from more_itertools import chunked

class Reranker:
    def __init__(self, model_name=None):
        if model_name is None:
            model_name = DEFAULT_RERANKER_MODEL
        self.reranker = CrossEncoder(model_name, cache_folder=str(RERANKER_CACHE_DIR))
        logger.info("✅ Reranker model loaded successfully")
    def truncate(self,text):
        return text[:max_chars]

    def rerank_chunks(self, query, chunks, max_chars=1000, batch_size=8):
        """
        Rerank the retrieved chunks using BGE reranker.
        Returns chunks sorted by relevance score.
        """
        logger.info(f"🔄 Reranking {len(chunks)} chunks...")


        # Prepare query-passage pairs
        pairs = [(self.truncate(query), self.truncate(chunk.page_content)) for chunk in chunks]
        # Batch predict 
        scores = []
        with tqdm(desc=f"🎯 Reranking {len(pairs)} query-chunk pairs", bar_format="{desc} | {elapsed}"):
            for batch in chunked(pairs, batch_size):
                scores.extend(self.reranker.predict(batch))

        # Combine chunks with scores and sort
        scored_chunks = list(zip(chunks, scores))
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        # Update metadata
        reranked_chunks = []
        for i, (chunk, score) in enumerate(scored_chunks):
            enhanced_metadata = chunk.metadata.copy() if chunk.metadata else {}
            enhanced_metadata["rerank_score"] = float(score)
            enhanced_metadata["rerank_position"] = i + 1

            enhanced_chunk = Document(
                page_content=chunk.page_content,
                metadata=enhanced_metadata
            )
            reranked_chunks.append(enhanced_chunk)

        logger.info(f"✅ Chunks reranked - Best score: {max(scores):.3f}")
        return reranked_chunks

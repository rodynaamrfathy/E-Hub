from langchain_exa import ExaSearchRetriever
from services.utils.kb_handler import KB_handler
from services.models.response_types import RetrievalResult
from rapidfuzz import fuzz
from typing import Optional

class KnowledgeRetriever:
    """Handles knowledge base and web search retrieval."""
    
    def __init__(self, exa_api_key: str):
        self.exa_api_key = exa_api_key
        self.retriever = ExaSearchRetriever(
            exa_api_key=exa_api_key, 
            k=5, 
            highlights=True,
            livecrawl='fallback'
        )
        self.kb = KB_handler._load_kb()

    async def retrieve_context(self, 
                             query: str, 
                             max_results: int = 5, 
                             similarity_threshold: int = 70) -> Optional[RetrievalResult]:
        """
        Retrieve relevant context from knowledge base or web search.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score for web results
            
        Returns:
            RetrievalResult with context and references, or None if no results
        """
        try:
            # Try KB search first
            kb_results = KB_handler._search_kb(query, max_results=max_results, threshold=65)
            
            if kb_results:
                return RetrievalResult(
                    context=kb_results,
                    references=[]  # KB results don't have external references
                )

            # Fallback to Exa search
            return await self._search_web(query, max_results, similarity_threshold)
            
        except Exception as e:
            print(f"⚠️ Retrieval error: {e}")
            return None

    async def _search_web(self, 
                         query: str, 
                         max_results: int, 
                         similarity_threshold: int) -> Optional[RetrievalResult]:
        """Perform web search using Exa retriever."""
        docs = self.retriever.invoke(query)
        
        scored_docs = []
        for doc in docs:
            if not doc.page_content:
                continue

            # Fuzzy partial match (query vs doc content)
            score = fuzz.partial_ratio(query.lower(), doc.page_content.lower())
            
            if score >= similarity_threshold:
                scored_docs.append((doc, score))

        if not scored_docs:
            return None

        # Sort by fuzzy score and limit results
        scored_docs = sorted(scored_docs, key=lambda x: x[1], reverse=True)[:max_results]

        results = []
        references = []
        
        for doc, score in scored_docs:
            metadata = doc.metadata or {}
            title = metadata.get("title", "Untitled").strip()
            url = metadata.get("url", "").strip()
            highlights = metadata.get("highlights", "N/A")

            link = f"[{title}]({url})" if url else title
            snippet = (
                f"- {doc.page_content.strip()}\n"
                f"  Highlights: {highlights}\n"
                f"  Fuzzy similarity: {score}\n"
                f"  Source: {link}"
            )
            
            results.append(snippet)
            references.append({
                "title": title,
                "url": url,
                "highlights": highlights,
                "content": doc.page_content.strip(),
                "similarity": score
            })

        return RetrievalResult(
            context="\n".join(results),
            references=references
        )


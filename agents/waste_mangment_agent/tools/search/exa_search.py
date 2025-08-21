from langchain_core.tools import Tool
from exa_py import Exa
from ...core.config import Config

class ExaSearch:
    """
    A wrapper class for performing web searches using the Exa API.
    This class integrates Exa's search API and formats the results
    for use in applications such as LangChain tools. It supports both
    human-readable (Markdown) and structured (JSON-like) output formats.
    """

    def __init__(self):
        """
        Initialize the ExaSearch instance.
        """
        self.exa = Exa(api_key=Config.EXA_API_KEY)


    def search(self, query: str, structured: bool = False):
        """
        Perform a web search using the Exa API.

        Args:
            query (str): The search query string.
            structured (bool, optional): 
                If True, return results as a list of dictionaries (machine-readable).
                If False, return results formatted as Markdown text (human-readable).
                Defaults to False.
        """
        try:
            # Perform search via Exa API
            results = self.exa.search(query, num_results=Config.MAX_SEARCH_RESULTS)

            # Handle no results case
            if not results.results:
                return (
                    {"message": "No relevant information found."}
                    if structured else "No relevant information found."
                )

            output = []
            for result in results.results:
                # Try to get a similarity or relevance score if available
                score = getattr(result, "score", None) or getattr(result, "relevance", None)

                # Build structured entry for each result
                entry = {
                    "title": result.title,
                    "url": getattr(result, "url", None),
                    "snippet": (
                        result.text[:200] + "..."
                        if getattr(result, "text", None) and len(result.text) > 200
                        else getattr(result, "text", None)
                    ),
                    "similarity_score": round(score, 4) if score is not None else None
                }
                output.append(entry)

            # Return structured JSON-like output
            if structured:
                return output
            else:
                # Return Markdown-formatted output
                formatted = "Here's what I found:\n\n"
                for i, r in enumerate(output, 1):
                    formatted += f"{i}. **{r['title']}** (score: {r['similarity_score']})\n"
                    if r["snippet"]:
                        formatted += f"   {r['snippet']}\n"
                    if r["url"]:
                        formatted += f"   🔗 {r['url']}\n\n"
                return formatted

        except Exception as e:
            # Handle unexpected errors gracefully
            return (
                {"error": str(e)} if structured else f"Search error: {str(e)}"
            )

    def get_tool(self) -> Tool:
        """
        Convert this class into a LangChain-compatible Tool.

        This allows an LLM (via LangChain) to invoke the `search` method
        as a tool for retrieving up-to-date web search results.

        Returns:
            Tool: A LangChain Tool object that wraps the `search` function.
        """
        return Tool.from_function(
            name="web_search",
            description= "Use this tool to search the web for real-time waste management, recycling and sustainability information",
        
            func=self.search)
        
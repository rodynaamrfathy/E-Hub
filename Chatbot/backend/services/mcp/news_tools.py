import requests
from langchain.tools import tool

MCP_BASE_URL = "http://localhost:8001"  # Your MCP server

# --- Tools ---

@tool("list_categories_types", return_direct=True)
def list_categories_types(_) -> str:
    """
    Get the available categories and types of articles from the database.
    Useful to know valid filters for sustainability/recycling articles.
    """
    resp = requests.get(f"{MCP_BASE_URL}/articles/categories_types")
    if resp.status_code != 200:
        return f"Error: {resp.text}"
    return resp.json()


@tool("search_articles", return_direct=True)
def search_articles(query: str, category: str = None, type: str = None, limit: int = 5) -> str:
    """
    Search for articles by query text with optional category and type filters.
    """
    payload = {"query": query, "category": category, "type": type, "limit": limit}
    resp = requests.post(f"{MCP_BASE_URL}/articles/search", json=payload)
    if resp.status_code != 200:
        return f"Error: {resp.text}"
    return resp.json()


@tool("get_article", return_direct=True)
def get_article(article_id: int) -> str:
    """
    Retrieve the full details of a specific article by ID.
    """
    resp = requests.get(f"{MCP_BASE_URL}/articles/{article_id}")
    if resp.status_code != 200:
        return f"Error: {resp.text}"
    return resp.json()

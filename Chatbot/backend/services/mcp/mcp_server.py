from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
from typing import List, Optional

app = FastAPI()

# Database connection
def get_connection():
    db_url = os.getenv("DATABASE_URL_mcp_test")
    if not db_url:
        raise RuntimeError("DATABASE_URL_mcp_test is not set in environment variables")

    # Neon requires sslmode=require
    return psycopg2.connect(db_url, sslmode="require")

# Request/Response models
class Article(BaseModel):
    id: Optional[int]
    title: str
    summary: str
    content: Optional[str]
    url: str
    category: str
    type: str
    published_at: Optional[str]

class QueryRequest(BaseModel):
    query: str
    category: Optional[str] = None
    type: Optional[str] = None
    limit: int = 5


# --- MCP FUNCTIONS ---

@app.post("/articles/search")
def search_articles(query_req: QueryRequest):
    """
    Search articles using full-text and fuzzy trigram similarity.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        sql = """
            SELECT id, title, summary, url, category, type, published_at,
                   similarity(title, %s) AS sim_title,
                   similarity(summary, %s) AS sim_summary
            FROM articles
            WHERE (ts_summary @@ plainto_tsquery(%s)
                   OR ts_content @@ plainto_tsquery(%s)
                   OR title ILIKE %s
                   OR summary ILIKE %s
                   OR similarity(title, %s) > 0.3
                   OR similarity(summary, %s) > 0.3)
        """
        params = [
            query_req.query, query_req.query,  # similarity(title, query), similarity(summary, query)
            query_req.query, query_req.query,  # tsvector match
            f"%{query_req.query}%", f"%{query_req.query}%",  # ILIKE fallback
            query_req.query, query_req.query   # trigram fuzzy matching
        ]

        if query_req.category:
            sql += " AND category = %s"
            params.append(query_req.category)

        if query_req.type:
            sql += " AND type = %s"
            params.append(query_req.type)

        sql += " ORDER BY sim_title DESC, sim_summary DESC, published_at DESC LIMIT %s"
        params.append(query_req.limit)

        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

        articles = [
            {
                "id": r[0],
                "title": r[1],
                "summary": r[2],
                "url": r[3],
                "category": r[4],
                "type": r[5],
                "published_at": r[6],
                "similarity_title": float(r[7]),
                "similarity_summary": float(r[8]),
            }
            for r in rows
        ]

        cur.close()
        conn.close()
        return {"results": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/articles/{article_id}")
def get_article(article_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, summary, content, url, category, type, published_at
            FROM articles
            WHERE id = %s
        """, (article_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Article not found")

        return {
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "content": row[3],
            "url": row[4],
            "category": row[5],
            "type": row[6],
            "published_at": row[7],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/articles/categories_types")
def list_categories_types():
    """
    Return distinct categories and types available in the articles table.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT DISTINCT category FROM articles;")
        categories = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT DISTINCT type FROM articles;")
        types = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        return {
            "categories": categories,
            "types": types
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/articles/add")
def add_article(article: Article):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO articles (title, summary, content, url, category, type, published_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            article.title, article.summary, article.content,
            article.url, article.category, article.type, article.published_at
        ))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {"id": new_id, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

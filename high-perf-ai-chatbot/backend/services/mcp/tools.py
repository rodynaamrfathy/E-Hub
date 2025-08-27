from .db_adapter import run_query

# get new post summ ti match it with the query, and id or link whatever in DB to refrence it in the ai ans just like how chatgbt and gemini does 

def query_db(sql: str) -> list[dict]:
    """Run a SELECT query on the Neon DB and return rows as a list of dicts."""
    return run_query(sql, fetch=True)

def execute_db(sql: str) -> str:
    """Run an INSERT, UPDATE, or DELETE query on the Neon DB."""
    run_query(sql, fetch=False)
    return "Query executed successfully"

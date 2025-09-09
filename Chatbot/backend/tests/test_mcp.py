import os
import pytest
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock
from services.mcp import server
from services.mcp.tools import query_db, execute_db

load_dotenv()
# Make sure NEON_DB_URL is set in your environment
NEON_DB_URL = os.getenv("NEON_DB_URL")

@pytest.mark.skipif(not NEON_DB_URL, reason="No Neon DB URL configured")
def test_query_db():
    # Create a test table if not exists
    execute_db("CREATE TABLE IF NOT EXISTS test_users (id SERIAL PRIMARY KEY, name TEXT);")

    # Insert sample data
    execute_db("INSERT INTO test_users (name) VALUES ('Alice'), ('Bob');")

    # Query it back
    results = query_db("SELECT * FROM test_users;")
    assert isinstance(results, list)
    assert any(user["name"] == "Alice" for user in results)
    assert any(user["name"] == "Bob" for user in results)

@patch('services.mcp.tools.run_query')
def test_execute_db_returns_message(mock_run_query):
    # Mock the run_query function to avoid database connection
    mock_run_query.return_value = None
    
    result = execute_db("CREATE TABLE IF NOT EXISTS dummy (id SERIAL PRIMARY KEY);")
    assert result == "Query executed successfully"
    mock_run_query.assert_called_once_with("CREATE TABLE IF NOT EXISTS dummy (id SERIAL PRIMARY KEY);", fetch=False)

@patch('services.mcp.tools.run_query')
def test_query_db_mocked(mock_run_query):
    # Mock the run_query function to return test data
    mock_data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    mock_run_query.return_value = mock_data
    
    results = query_db("SELECT * FROM test_users;")
    assert isinstance(results, list)
    assert any(user["name"] == "Alice" for user in results)
    assert any(user["name"] == "Bob" for user in results)
    mock_run_query.assert_called_once_with("SELECT * FROM test_users;", fetch=True)

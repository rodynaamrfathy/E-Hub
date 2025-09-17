-- Initialize database with pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create any initial tables or configurations if needed
-- (The application will handle table creation via SQLAlchemy)

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;

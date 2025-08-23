# database.py
import os
import asyncio
import re
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.async_session_factory = None
        
    async def initialize(self):
        """Initialize the async database engine"""
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
            
        # Convert postgresql to postgresql+asyncpg for async support
        async_database_url = re.sub(r'^postgresql:', 'postgresql+asyncpg:', database_url)
        
        self.engine = create_async_engine(
            async_database_url,
            echo=True,  # Set to False in production
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Create async session factory
        self.async_session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
    async def create_tables(self):
        """Create all tables defined in models"""
        from AIChatbotService.models.conversation import Base as ConversationBase
        from AIChatbotService.models.message import Base as MessageBase
        
        # Since both models use the same Base, we only need to import one
        async with self.engine.begin() as conn:
            await conn.run_sync(ConversationBase.metadata.create_all)
            
    async def get_session(self):
        """Get an async database session"""
        if not self.async_session_factory:
            await self.initialize()
        return self.async_session_factory()
        
    async def close(self):
        """Close the database engine"""
        if self.engine:
            await self.engine.dispose()

# Global database manager instance
db_manager = DatabaseManager()

async def get_db_session():
    """Dependency function to get database session"""
    async with db_manager.get_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Test function
async def test_connection():
    """Test the database connection"""
    try:
        await db_manager.initialize()
        
        async with db_manager.engine.connect() as conn:
            result = await conn.execute(text("SELECT 'Hello World' as message"))
            print("Database connection successful!")
            print(result.fetchall())
            
        # Test table creation
        await db_manager.create_tables()
        print("Tables created successfully!")
        
    except Exception as e:
        print(f"Database connection failed: {e}")
    finally:
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(test_connection())
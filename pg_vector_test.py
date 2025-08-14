# Test script (continued)
from rag_pipeline.src.vectorstores.pgvector_vectorstore import PgVector_VS
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from rag_pipeline.src.models.multilingual_embedder import MultilingualEmbedder
from rag_pipeline.config.settings import (
    DEFAULT_EMBEDDING_MODEL, DEFAULT_BATCH_SIZE
)
from AIChatbotService.services.database_service import DatabaseService
from AIChatbotService.database import db_manager
import uuid



load_dotenv()

#connection_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

multilingual_embedder = MultilingualEmbedder(
            model_name=DEFAULT_EMBEDDING_MODEL, 
            batch_size=DEFAULT_BATCH_SIZE
        )
# Initialize and test
#vector_store = PgVector_VS(
#    connection_string=connection_string,
#    embedder_model=multilingual_embedder
#)

# Test with sample documents
test_docs = [
    Document(page_content="This is a test document about machine learning", metadata={"source": "test1"}),
    Document(page_content="Another document discussing artificial intelligence", metadata={"source": "test2"}),
]

# Create vector store
#vector_store.create_vectorstore(test_docs)

# Test search
#results = vector_store.get_relevant_documents("machine learning", top_k=2)
#print(f"Found {len(results)} results")

# Clean up
#vector_store.close()


from AIChatbotService.database import async_session_maker
from AIChatbotService.models.embedding import Embedding  # Adjust import path if needed

async def example_usage():
    """Example of how to use the database service"""
    
    # Initialize database
    await db_manager.initialize()
    await db_manager.create_tables()
    
    service = DatabaseService()
    
    try:
        # Create a conversation
        user_id = str(uuid.uuid4())
        session_id = "session_123"
        conversation = await service.create_conversation(
            user_id=user_id,
            session_id=session_id,
            title="Test Conversation"
        )
        print(f"Created conversation: {conversation}")
        
        # Add messages
        await service.add_message(
            conversation_id=str(conversation.conversation_id),
            message_type="user",
            content="Hello, how are you?",
            msg_metadata={"timestamp": "2024-01-01T10:00:00Z"}
        )

        await service.add_message(
            conversation_id=str(conversation.conversation_id),
            message_type="assistant",
            content="I'm doing well, thank you for asking!",
            msg_metadata={"model": "claude-3", "tokens": 50}
        )
        
        # Get conversation with messages
        full_conversation = await service.get_conversation(str(conversation.conversation_id))
        print(f"Full conversation: {full_conversation}")
        print(f"Messages: {full_conversation.messages}")
        
        # Get user conversations
        user_conversations = await service.get_user_conversations(user_id)
        print(f"User conversations: {user_conversations}")
        
        # --- Add embeddings ---
        texts = [doc.page_content for doc in test_docs]
        metadatas = [doc.metadata for doc in test_docs]

        # Generate embeddings using your MultilingualEmbedder
        vectors = multilingual_embedder.embed_documents(texts)  # Should return List[List[float]]

        async with async_session_maker() as session:
            for content, meta, vector in zip(texts, metadatas, vectors):
                embedding_row = Embedding(
                    content=content,
                    meta_data=meta,
                    embedding=vector
                )
                session.add(embedding_row)
            await session.commit()

        print("Inserted embeddings into the database.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await db_manager.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
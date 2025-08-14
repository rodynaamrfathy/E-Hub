from rag_pipeline.src.vectorstores.pgvector_vectorstore import PgVector_VS
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from rag_pipeline.src.models.multilingual_embedder import MultilingualEmbedder
from rag_pipeline.config.settings import (
    DEFAULT_EMBEDDING_MODEL, DEFAULT_BATCH_SIZE
)
import asyncio

load_dotenv()

async def example_usage():
    """Fixed example usage focusing on vector store functionality"""
    
    # Initialize embedder
    multilingual_embedder = MultilingualEmbedder(
        model_name=DEFAULT_EMBEDDING_MODEL,
        batch_size=DEFAULT_BATCH_SIZE
    )
    
    # Initialize vector store
    vector_store = PgVector_VS(
        connection_string=os.getenv("DATABASE_URL"),
        table_name="test_embeddings",  # Use a specific table name
        embedder_model=multilingual_embedder
    )
    
    # Test documents
    test_docs = [
        Document(
            page_content="This is a test document about machine learning", 
            metadata={"source": "test1", "category": "AI"}
        ),
        Document(
            page_content="Another document discussing artificial intelligence", 
            metadata={"source": "test2", "category": "AI"}
        ),
        Document(
            page_content="Deep learning is a subset of machine learning", 
            metadata={"source": "test3", "category": "AI"}
        ),
    ]
    
    try:
        print("Creating vector store...")
        # Create vector store (this handles both embedding generation and storage)
        vector_store.create_vectorstore(test_docs, normalize_embeddings=True)
        
        print("Testing search...")
        # Test search
        results = vector_store.get_relevant_documents("machine learning", top_k=2)
        
        print(f"Found {len(results)} results:")
        for i, doc in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Content: {doc.page_content}")
            print(f"Metadata: {doc.metadata}")
            if 'similarity' in doc.metadata:
                print(f"Similarity: {doc.metadata['similarity']:.4f}")
        
        # Test with different query
        print("\n" + "="*50)
        print("Testing with 'artificial intelligence' query...")
        results2 = vector_store.get_relevant_documents("artificial intelligence", top_k=2)
        
        for i, doc in enumerate(results2, 1):
            print(f"\nResult {i}:")
            print(f"Content: {doc.page_content}")
            if 'similarity' in doc.metadata:
                print(f"Similarity: {doc.metadata['similarity']:.4f}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        vector_store.close()

if __name__ == "__main__":
    asyncio.run(example_usage())
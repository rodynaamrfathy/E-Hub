# Test script (continued)
from rag_pipeline.src.vectorstores.pgvector_vectorstore import PgVector_VS
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from rag_pipeline.src.models.multilingual_embedder import MultilingualEmbedder
from rag_pipeline.config.settings import (
    DEFAULT_EMBEDDING_MODEL, DEFAULT_BATCH_SIZE
)

load_dotenv()

connection_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

multilingual_embedder = MultilingualEmbedder(
            model_name=DEFAULT_EMBEDDING_MODEL, 
            batch_size=DEFAULT_BATCH_SIZE
        )
# Initialize and test
vector_store = PgVector_VS(
    connection_string=connection_string,
    embedder_model=multilingual_embedder
)

# Test with sample documents
test_docs = [
    Document(page_content="This is a test document about machine learning", metadata={"source": "test1"}),
    Document(page_content="Another document discussing artificial intelligence", metadata={"source": "test2"}),
]

# Create vector store
vector_store.create_vectorstore(test_docs)

# Test search
results = vector_store.get_relevant_documents("machine learning", top_k=2)
print(f"Found {len(results)} results")

# Clean up
vector_store.close()
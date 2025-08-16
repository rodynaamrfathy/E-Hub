from rag_pipeline.src.vectorstores.pgvector_vectorstore import PgVector_VS
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from rag_pipeline.src.models.multilingual_embedder import MultilingualEmbedder
from rag_pipeline.config.settings import (
    DEFAULT_EMBEDDING_MODEL, DEFAULT_BATCH_SIZE
)
from tqdm import tqdm
import logging
import time
# Internal imports
from rag_pipeline.src.models.multilingual_embedder import MultilingualEmbedder
from rag_pipeline.src.models.llm_models import OLLAMA_LLM , Hugging_Face_LLM
from rag_pipeline.src.vectorstores.faiss_vectorstore import Fais_VS
from rag_pipeline.src.strategies.chat_strategy import ChattingStrategy
from rag_pipeline.src.strategies.question_strategy import QuestionStrategy
from rag_pipeline.src.strategies.summarization_strategy import SummarizationStrategy, Summarization_Rag_Strategy
from rag_pipeline.src.core.task_processor import TaskProcessor
from rag_pipeline.src.processors.json_processor import JSONPreprocessor
from rag_pipeline.config.settings import (
    DEFAULT_EMBEDDING_MODEL, DEFAULT_BATCH_SIZE, OLLAMA_MODELS, 
    LOG_LEVEL, LLM_CACHE_DIR
)
import asyncio

load_dotenv()


def setup_logging():
    """Configure logging for the pipeline."""
    os.makedirs("logs", exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/document_processing.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)



def load_and_process_documents(logger,files_paths):
    """Load and process  documents into chunks."""
    logger.info("📁 Loading documents...")
    paths = [files_paths]
    docs = JSONPreprocessor()

    data = docs.process_documents_from_files(paths)


    logger.info(f"✅ Loaded {len(data)} documents")

    logger.info("📄 Creating individual documents...")
    individual_documents = [
        Document(page_content=pdf.page_content, metadata={"pdf_id": i})
        for i, pdf in enumerate(tqdm(data, desc="🔨 Creating documents", unit="doc"))
        if pdf.page_content
    ]
    logger.info(f"✅ Created {len(individual_documents)} individual documents")

    logger.info("✂️ Chunking documents...")
    chunked_docs = docs.chunk_documents(individual_documents)
    logger.info(f"✅ Document chunking completed - {len(chunked_docs)} chunks created")

    return chunked_docs , individual_documents

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
        table_name="embeddings", 
        embedder_model=multilingual_embedder
    )
    

    
    try:
        pipeline_start_time = time.time()
        logger = setup_logging()
        logger.info("🚀 Starting document processing pipeline...")
        chunked_docs , individual_documents = load_and_process_documents(logger,'/Users/maryamsaad/Documents/app/data/PMS Market Research.pdf')
        print("Creating vector store...")
        # Create vector store (this handles both embedding generation and storage)
        vector_store.create_vectorstore(individual_documents)
        
        print("Testing search...")
        # Test search
        results = vector_store.get_relevant_documents("machine learning", top_k=5)
        
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
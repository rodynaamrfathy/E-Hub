import os
import asyncio
import logging
import traceback
import time
from dotenv import load_dotenv
from tqdm import tqdm

# Core langchain imports
from langchain_core.documents import Document

# Internal imports - models
from rag_pipeline.src.models.multilingual_embedder import MultilingualEmbedder
from rag_pipeline.src.models.llm_models import OLLAMA_LLM, Hugging_Face_LLM

# Internal imports - vectorstores
from rag_pipeline.src.vectorstores.pgvector_vectorstore import PgVector_VS
from rag_pipeline.src.vectorstores.faiss_vectorstore import Fais_VS

# Internal imports - strategies
from rag_pipeline.src.strategies.chat_strategy import ChattingStrategy
from rag_pipeline.src.strategies.question_strategy import QuestionStrategy
from rag_pipeline.src.strategies.summarization_strategy import (
    SummarizationStrategy, 
    Summarization_Rag_Strategy
)

# Internal imports - core and processors
from rag_pipeline.src.core.task_processor import TaskProcessor
from rag_pipeline.src.processors.json_processor import JSONPreprocessor

# Configuration imports
from rag_pipeline.config.settings import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_BATCH_SIZE,
    OLLAMA_MODELS,
    LOG_LEVEL,
    LLM_CACHE_DIR
)

# External service imports
from AIChatbotService.services.database_service import DatabaseService
from AIChatbotService.models import *
from AIChatbotService.database import *

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


def initialize_models(logger):
    """Initialize embedder and LLM models."""
    logger.info("🧠 Initializing multilingual embedder model...")

    multilingual_embedder = MultilingualEmbedder(
        model_name=DEFAULT_EMBEDDING_MODEL,
        batch_size=DEFAULT_BATCH_SIZE
    )

    logger.info(f"✅ Embedder model loaded")
    logger.info("🤖 Loading OLLAMA LLM model...")
    
    llm = OLLAMA_LLM(OLLAMA_MODELS['llama8b'], str(LLM_CACHE_DIR)).load_model()
    # llm = Hugging_Face_LLM(
    #     model_name="Qwen/Qwen3-8B",
    #     cache_folder=str(LLM_CACHE_DIR)
    # )

    logger.info(f"✅ LLM model loaded")
    return multilingual_embedder, llm


def initialize_strategies(logger, llm, vector_store, multilingual_embedder):
    """Initialize all processing strategies."""
    logger.info("⚙️ Initializing processing strategies...")
    strategies_progress = tqdm(total=5, desc="🔧 Initializing strategies", unit="strategy")

    logger.info("💬 Initializing Chatting Strategy...")
    chatting_strategy = ChattingStrategy(llm, vector_store, multilingual_embedder)
    strategies_progress.update(1)

    logger.info("📝 Initializing Summarization Strategy...")
    summarization_strategy = SummarizationStrategy(llm)
    strategies_progress.update(1)

    logger.info("❓ Initializing Question Strategy...")
    question_strategy = QuestionStrategy(llm)
    strategies_progress.update(1)

    logger.info("🔍 Initializing RAG Summary Strategy...")
    rag_summary = Summarization_Rag_Strategy(llm, vector_store)
    strategies_progress.update(1)

    logger.info("🎯 Initializing Task Processor...")
    processor = TaskProcessor()
    strategies_progress.update(1)
    strategies_progress.close()

    return chatting_strategy, summarization_strategy, question_strategy, rag_summary, processor


def load_and_process_documents(logger, files_paths):
    """Load and process documents into chunks."""
    logger.info("📁 Loading documents...")

    paths = files_paths if isinstance(files_paths, list) else [files_paths]

    docs = JSONPreprocessor()
    data = docs.process_documents_from_files(paths)

    logger.info(f"✅ Loaded {len(data)} documents")
    logger.info("📄 Creating individual documents...")

    individual_documents = []
    for i, pdf in enumerate(tqdm(data, desc="🔨 Creating documents", unit="doc", 
                                leave=True, dynamic_ncols=True)):
        if pdf.page_content:
            # Match file name to document index if possible
            file_name = os.path.basename(paths[i]) if i < len(paths) else "unknown"
            individual_documents.append(
                Document(page_content=pdf.page_content, 
                        metadata={"pdf_id": i, "file_name": file_name})
            )

    logger.info(f"✅ Created {len(individual_documents)} individual documents")
    logger.info("✂️ Chunking documents...")
    
    chunked_docs = docs.chunk_documents(individual_documents)
    logger.info(f"✅ Document chunking completed - {len(chunked_docs)} chunks created")

    return chunked_docs, individual_documents


async def example_usage():
    """Fixed example usage focusing on vector store functionality"""
    logger = setup_logging()

    await db_manager.initialize()
    db_service = DatabaseService()

    try:
        user_id = '34bd67d3-1fb4-4084-a37b-870aaccb361e'
        title = "tester"

        conv = await db_service.create_conversation(user_id, title, "summarization")
        print(conv)

        logger.info("🚀 Starting document processing pipeline...")

        # Initialize models
        multilingual_embedder, llm = initialize_models(logger)

        # Initialize vector store
        vector_store = PgVector_VS(
            connection_string=os.getenv("DATABASE_URL"),
            embedder_model=multilingual_embedder
        )

        # Load and process documents
        file_path = "/Users/maryamsaad/Documents/Graduation_Proj/junk/2 Chatting with PDF copy.pdf"
        chunked_docs, individual_documents = load_and_process_documents(logger, file_path)

        # Create vector store
        vector_store.create_vectorstore(individual_documents)

        # Initialize strategies
        chatting_strategy, summarization_strategy, question_strategy, TS_summary, processor = initialize_strategies(
            logger, llm, vector_store, multilingual_embedder
        )

        # Strategies EXECUTION
        # Execute summarization
        processor.strategy = summarization_strategy
        summary = processor.execute_task(  # await can be added
            individual_documents[0].page_content,
            length="medium",
            verbose=False,
            overview_level="low_level"
        )

        await db_service.add_message(str(conv.conv_id), 'assistant', summary)

        processor.strategy = chatting_strategy
        prompt = "\nWhat tranlation platforms are in the document\n"
        answer = processor.execute_task(
            prompt, str(conv.conv_id)
        )
        print("ANSWER", answer)
        await db_service.add_message(str(conv.conv_id), 'user', prompt)
        await db_service.add_message(str(conv.conv_id), 'assistant', answer)

        processor.strategy = question_strategy
        results = processor.execute_task(individual_documents[0], 20, 'hard')
        print(results['qa_output'])
        await db_service.add_message(str(conv.conv_id), 'bot', results['qa_output'])

        processor.strategy = TS_summary
        results = processor.execute_task("Translation Platform")
        print(results)
        await db_service.add_message(str(conv.conv_id), 'bot', results)

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        traceback.print_exc()

    finally:
        vector_store.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
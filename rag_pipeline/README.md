# Key Features

## Multilingual Support:
+ Automatic language detection
+ Language-specific prompt formatting
### RAG Pipeline:
+ Document ingestion and chunking
+ Vector embedding and storage
+ Semantic search with optional reranking
+ LLM generation with retrieved context
### Conversation Management:
+ Persistent chat history
+ Context-aware responses
### Flexible Configuration:
+ Supports different LLM backends (Ollama, HuggingFace)
+ Multiple vector store options
+ Configurable chunking and retrieval parameters

## Usage Patterns

### The system appears designed to:

1. Process documents (PDFs, text) into chunks
2. Store chunk embeddings in a vector database
3. Handle different types of queries through specialized strategies
4. Maintain conversation context across interactions

## Technical Stack

Python
LangChain (for LLM integration)
FAISS/pgvector (vector storage)
PyPDF (document processing)
Sentence Transformers (embeddings)
CrossEncoder (reranking)

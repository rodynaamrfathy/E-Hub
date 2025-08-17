import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from langchain.schema import Document
import pickle
import json
from more_itertools import chunked
import logging
from tqdm import tqdm
from rag_pipeline.src.abstracts.abstract_vector_db import VectorStoreBase
from rag_pipeline.src.models.reranker import Reranker


logger = logging.getLogger(__name__)

class PgVector_VS(VectorStoreBase):
    def __init__(self, connection_string , table_name = "chatbot_service" , embedder_model=None):
        """Initialize pgvector vector store with optional reranking capabilities.
        
        Args:
            connection_string: PostgreSQL connection string
            table_name: Name of the table to store embeddings
            embedder_model: Model for generating embeddings
            reranker_model: Model for reranking results
        """
        logger.info("🗄️ Initializing pgvector VectorStore...")
        
        self.connection_string = connection_string
        self.table_name = table_name
        self.embedder_model = embedder_model
        self.enable_reranking = True
        self.reranker = Reranker()
        self.dimension = None
        self.total_vectors = 0
        
        # Initialize database connection
        self._init_connection()
        self._create_table()
        
        if embedder_model:
            logger.info("✅ pgvector VectorStore initialized with embedder model")
        else:
            logger.info("⚠️ pgvector VectorStore initialized without embedder model")

    def _init_connection(self):
        """Initialize database connection and test it."""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            self.conn.autocommit = True
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            raise

    def _create_table(self):
        """Create the embeddings table if it doesn't exist."""
        with self.conn.cursor() as cur:
            # Check if table exists and get dimension if it does
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = 'embedding'
            """, (self.table_name,))
            
            result = cur.fetchone()
            
            if result:
                logger.info(f"📋 Table '{self.table_name}' already exists")
                # Get current vector count
                cur.execute(f"SELECT COUNT(*) FROM {self.table_name}")
                self.total_vectors = cur.fetchone()[0]
                logger.info(f"📊 Current vector count: {self.total_vectors}")
            else:
                # Create table - we'll add the vector column later when we know the dimension
                create_table_sql = f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                cur.execute(create_table_sql)
                logger.info(f"✅ Created table '{self.table_name}'")

    def _add_vector_column(self, dimension: int):
        """Add vector column with specified dimension."""
        with self.conn.cursor() as cur:
            # Check if embedding column exists
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = 'embedding'
            """, (self.table_name,))
            
            if not cur.fetchone():
                cur.execute(f"ALTER TABLE {self.table_name} ADD COLUMN embedding vector({dimension})")
                logger.info(f"✅ Added vector column with dimension {dimension}")
                
                # Create index for better performance
                index_name = f"{self.table_name}_embedding_idx"
                cur.execute(f"CREATE INDEX {index_name} ON {self.table_name} USING ivfflat (embedding vector_cosine_ops)")
                logger.info(f"✅ Created vector index '{index_name}'")
            
            self.dimension = dimension



    def create_vectorstore(self, docs, normalize_embeddings=True):
        """Create enhanced pgvector store from Document objects with metadata."""
        logger.info(f"🚀 Creating enhanced vectorstore from {len(docs)} Document objects...")
        logger.info(f"⚙️ Normalization: {'enabled' if normalize_embeddings else 'disabled'}")
        
        if not self.embedder_model:
            logger.error("❌ No embedder model available")
            raise ValueError("Embedder model is required. Set it during initialization or call set_embedder_model()")
        
        # Extract texts from Document objects
        logger.info("📝 Extracting texts from Document objects...")
        texts = [doc.page_content for doc in tqdm(docs, desc="📄 Processing docs", unit="doc")]
        
        # Generate embeddings
        logger.info(f"🧠 Generating embeddings for {len(texts)} documents...")
        with tqdm(total=1, desc="⚡ Creating embeddings", unit="batch") as pbar:
            embeddings = self.embedder_model.batch_embed(texts)
            pbar.update(1)
            
        embeddings = np.array(embeddings).astype("float32")
        logger.info(f"✅ Embeddings generated - Shape: {embeddings.shape}")
        
        # Ensure embeddings are 2D
        if embeddings.ndim == 1:
            logger.debug("🔄 Reshaping 1D embeddings to 2D...")
            embeddings = embeddings.reshape(1, -1)
        
        # Normalize embeddings for cosine similarity if requested
        if normalize_embeddings:
            logger.info("🎯 Normalizing embeddings for cosine similarity...")
            with tqdm(total=1, desc="🔍 Normalizing", unit="operation") as pbar:
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                embeddings = embeddings / (norms + 1e-12)  # Add small epsilon to avoid division by zero
                pbar.update(1)
        
        # Set up vector column
        self.dimension = embeddings.shape[1]
        self._add_vector_column(self.dimension)
        
        # # Clear existing data
        # with self.conn.cursor() as cur:
        #     cur.execute(f"TRUNCATE TABLE {self.table_name}")
        #     logger.info("🗑️ Cleared existing data")
        
        # Insert documents and embeddings
        logger.info("💾 Inserting documents into database...")
        with self.conn.cursor() as cur:
            for i, (doc, embedding) in enumerate(tqdm(zip(docs, embeddings), 
                                                     desc="💾 Inserting", 
                                                     unit="doc", 
                                                     total=len(docs))):
                metadata = doc.metadata if doc.metadata else {}
                metadata['normalized'] = normalize_embeddings  # Track normalization status
                
                cur.execute(f"""
                    INSERT INTO {self.table_name} (content, metadata, embedding) 
                    VALUES (%s, %s, %s)
                """, (doc.page_content, json.dumps(metadata), embedding.tolist()))
        
        # Update total count
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            self.total_vectors = cur.fetchone()[0]
        
        logger.info(f"✅ Enhanced vectorstore created successfully!")
        logger.info(f"📊 Statistics: {self.total_vectors} documents, dim {self.dimension}")
        print(f"[pgvector] Created vectorstore with {self.total_vectors} documents of dim {self.dimension}")
        print(f"[pgvector] Normalization: {'enabled' if normalize_embeddings else 'disabled'}")
        
        return self
    def get_relevant_documents(self, query, top_k=5):
        """Search and retrieve the most relevant documents for a query with optional reranking."""
        
        # Get query embedding
        logger.debug("🧠 Generating query embedding...")
        with tqdm(total=1, desc="⚡ Embedding query", unit="query", leave=False) as pbar:
            if isinstance(query, str):
                if hasattr(self.embedder_model, 'embed_query'):
                    query_embedding = self.embedder_model.embed_query(query)
                else:
                    query_embedding = self.embedder_model.batch_embed([query])
                    if isinstance(query_embedding, list) and len(query_embedding) > 0:
                        query_embedding = query_embedding[0]
                    elif isinstance(query_embedding, np.ndarray) and query_embedding.ndim > 1:
                        query_embedding = query_embedding[0]
            else:
                query_embedding = self.embedder_model.batch_embed(query)
            pbar.update(1)
        
        # Ensure query_embedding is numpy array
        query_embedding = np.array(query_embedding, dtype="float32").tolist()
        
        # Search for similar vectors
        logger.debug("🔍 Searching for similar documents...")
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Use cosine similarity with explicit cast to pgvector
            cur.execute(f"""
                SELECT id, content, metadata, 
                    1 - (embedding <=> %s::vector) as similarity
                FROM {self.table_name}
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, query_embedding, top_k * 2))  # Get more candidates for reranking
            
            results = cur.fetchall()
        
        # Convert to Document objects
        candidates = []
        for row in results:
            metadata = row['metadata'] if row['metadata'] else {}
            metadata['similarity'] = float(row['similarity'])
            metadata['retrieval_index'] = row['id']
            
            doc = Document(
                page_content=row['content'],
                metadata=metadata
            )
            candidates.append(doc)
        
        if self.enable_reranking and candidates:
            logger.info(f"🎯 Applying reranking to {len(candidates)} candidates...")

        candidates = self.reranker.rerank_chunks(query, candidates)

        # Return top_k results
        results = candidates[:top_k]
        rerank_status = "with reranking" if self.enable_reranking else "without reranking"
        logger.info(f"✅ Retrieved {len(results)} relevant documents {rerank_status}")
        
        return results

    def set_embedder_model(self, embedder_model):
        """Set or update the embedder model."""
        logger.info("🔧 Setting embedder model...")
        self.embedder_model = embedder_model
        logger.info("✅ Embedder model updated successfully")
        return self

    def save_index(self, file_path):
        """Save vectorstore metadata (database contains the actual vectors)."""
        logger.info(f"💾 Saving vectorstore metadata to {file_path}...")
        
        metadata = {
            'connection_string': self.connection_string,
            'table_name': self.table_name,
            'dimension': self.dimension,
            'total_vectors': self.total_vectors,
            'enable_reranking': self.enable_reranking
        }
        
        # Create vectorstores directory if it doesn't exist
        import os
        os.makedirs('vectorstores', exist_ok=True)
        
        with open(f'vectorstores/{file_path}_metadata.pkl', 'wb') as f:
            pickle.dump(metadata, f)
        
        logger.info(f"✅ Metadata saved to vectorstores/{file_path}_metadata.pkl")
        logger.info("ℹ️ Vector data is stored in the PostgreSQL database")
        print(f"[pgvector] Metadata saved to vectorstores/{file_path}_metadata.pkl")
        print(f"[pgvector] Vector data is in PostgreSQL table '{self.table_name}'")

    def load_index(self, file_path, embedder_model=None):
        """Load vectorstore metadata and reconnect to database."""
        logger.info(f"📂 Loading vectorstore metadata from {file_path}...")
        
        metadata_path = f'vectorstores/{file_path}_metadata.pkl'
        if not os.path.exists(metadata_path):
            logger.error(f"❌ Metadata file not found: {metadata_path}")
            raise FileNotFoundError(f"Metadata file {metadata_path} not found")
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        # Restore attributes
        self.connection_string = metadata['connection_string']
        self.table_name = metadata['table_name']
        self.dimension = metadata['dimension']
        self.total_vectors = metadata['total_vectors']
        self.enable_reranking = metadata['enable_reranking']
        
        # Re-initialize connection
        self._init_connection()
        
        # Set embedder model if provided
        if embedder_model:
            logger.info("🔧 Setting embedder model...")
            self.embedder_model = embedder_model
        
        # Verify database state
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            current_count = cur.fetchone()[0]
            if current_count != self.total_vectors:
                logger.warning(f"⚠️ Vector count mismatch: expected {self.total_vectors}, found {current_count}")
                self.total_vectors = current_count
        
        reranking_status = "enabled" if self.enable_reranking else "disabled"
        logger.info(f"✅ Vectorstore loaded successfully: {self.total_vectors} vectors, dim {self.dimension}")
        logger.info(f"🎯 Reranking: {reranking_status}")
        
        print(f"[pgvector] Loaded vectorstore: {self.total_vectors} vectors, dim {self.dimension}")
        print(f"[pgvector] Connected to table '{self.table_name}'")
        if self.enable_reranking:
            print(f"[pgvector] Reranking enabled")
        
        return self

    def close(self):
        """Close database connection."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            logger.info("🔒 Database connection closed")

    def __del__(self):
        """Cleanup database connection on deletion."""
        self.close()
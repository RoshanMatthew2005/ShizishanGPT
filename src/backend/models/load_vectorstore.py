"""
VectorStore Loader
Loads and manages the RAG vectorstore (ChromaDB)
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
import os

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("chromadb not installed. RAG functionality disabled.")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Using fallback embeddings.")


class VectorStore:
    """
    Wrapper for ChromaDB vectorstore
    """
    
    def __init__(self, persist_directory: str):
        self.persist_directory = Path(persist_directory)
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.loaded = False
        self.collection_name = "knowledge_base"
    
    def load(self):
        """Load the vectorstore"""
        if not CHROMADB_AVAILABLE:
            logger.error("ChromaDB not available")
            return False
        
        try:
            # Initialize embedding model
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✓ Loaded sentence-transformers embedding model")
            
            # Check if persist directory exists
            if not self.persist_directory.exists():
                logger.warning(f"Vectorstore directory not found: {self.persist_directory}")
                logger.warning("Creating empty vectorstore")
                self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                count = self.collection.count()
                logger.info(f"✓ Loaded vectorstore with {count} documents")
            except Exception:
                logger.warning(f"Collection '{self.collection_name}' not found. Creating new one.")
                self.collection = self.client.create_collection(name=self.collection_name)
            
            self.loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to load vectorstore: {e}")
            self.loaded = False
            return False
    
    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            Dictionary with documents and metadata
        """
        if not self.loaded:
            raise RuntimeError("Vectorstore not loaded. Call load() first.")
        
        try:
            # Check if collection is empty
            if self.collection.count() == 0:
                logger.warning("Vectorstore is empty")
                return {
                    "documents": [],
                    "metadatas": [],
                    "distances": [],
                    "context": "",
                    "avg_relevance": 0.0,
                    "num_results": 0
                }
            
            # Perform search
            results = self.collection.query(
                query_texts=[query],
                n_results=min(top_k, self.collection.count())
            )
            
            # Extract results
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            # Convert distances to relevance scores (1 - distance)
            relevances = [1.0 - min(d, 1.0) for d in distances]
            avg_relevance = sum(relevances) / len(relevances) if relevances else 0.0
            
            # Format documents
            formatted_docs = []
            for i, (doc, meta, rel) in enumerate(zip(documents, metadatas, relevances)):
                formatted_docs.append({
                    "text": doc,
                    "metadata": meta,
                    "relevance": rel,
                    "rank": i + 1
                })
            
            # Create context string
            context = "\n\n".join([doc["text"] for doc in formatted_docs[:3]])
            
            result = {
                "documents": formatted_docs,
                "context": context,
                "avg_relevance": avg_relevance,
                "num_results": len(formatted_docs)
            }
            
            logger.info(f"RAG search: Found {len(formatted_docs)} documents, avg relevance: {avg_relevance:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            raise
    
    def add_documents(self, documents: List[str], metadatas: List[Dict] = None, ids: List[str] = None):
        """
        Add documents to vectorstore
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dicts
            ids: List of document IDs
        """
        if not self.loaded:
            raise RuntimeError("Vectorstore not loaded. Call load() first.")
        
        try:
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]
            
            if metadatas is None:
                metadatas = [{} for _ in documents]
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to vectorstore")
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise


def load_vectorstore(persist_directory: str) -> VectorStore:
    """
    Factory function to load vectorstore
    """
    store = VectorStore(persist_directory)
    store.load()
    return store

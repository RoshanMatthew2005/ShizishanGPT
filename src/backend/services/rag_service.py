"""
RAG Service
Handles RAG document retrieval
"""

import logging
import time
from typing import Dict, Any, List
from ..dependencies import model_registry

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service for RAG operations
    """
    
    def __init__(self):
        self.vectorstore = None
    
    def initialize(self):
        """Initialize service with loaded vectorstore"""
        self.vectorstore = model_registry.get("vectorstore")
    
    async def retrieve(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Retrieve relevant documents
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
        
        Returns:
            Dictionary with documents and metadata
        """
        start_time = time.time()
        
        try:
            if self.vectorstore is None:
                self.initialize()
            
            logger.info(f"Processing RAG query: {query[:100]}...")
            
            # Search vectorstore
            results = self.vectorstore.search(query, top_k=top_k)
            
            execution_time = time.time() - start_time
            
            logger.info(f"RAG query completed in {execution_time:.2f}s")
            logger.info(f"Retrieved {results['num_results']} documents")
            
            return results
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            raise


# Global service instance
rag_service = RAGService()

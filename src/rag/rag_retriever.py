"""
RAG Retriever
Retrieves relevant information from agricultural knowledge base
"""

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import yaml
import os
from typing import List, Tuple


class RAGRetriever:
    """
    Retrieval-Augmented Generation Retriever
    Uses embeddings and FAISS for efficient similarity search
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize RAG Retriever
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.rag_config = self.config['rag']
        
        # Initialize embedding model
        print(f"📚 Loading embedding model: {self.rag_config['embedding_model']}")
        self.embedding_model = SentenceTransformer(self.rag_config['embedding_model'])
        
        # Initialize FAISS index
        self.index = None
        self.documents = []
        self.embeddings = []
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Input text
            
        Returns:
            List of text chunks
        """
        chunk_size = self.rag_config['chunk_size']
        chunk_overlap = self.rag_config['chunk_overlap']
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap
        
        return chunks
    
    def add_documents(self, documents: List[str]):
        """
        Add documents to the knowledge base
        
        Args:
            documents: List of document texts
        """
        print(f"📄 Adding {len(documents)} documents to knowledge base...")
        
        # Chunk documents
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_text(doc)
            all_chunks.extend(chunks)
        
        self.documents = all_chunks
        
        # Generate embeddings
        print("🔄 Generating embeddings...")
        self.embeddings = self.embedding_model.encode(
            all_chunks,
            show_progress_bar=True
        )
        
        # Build FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(self.embeddings).astype('float32'))
        
        print(f"✅ Added {len(all_chunks)} chunks to index")
    
    def retrieve(self, query: str, top_k: int = None) -> List[Tuple[str, float]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        if self.index is None:
            raise ValueError("No documents in knowledge base! Add documents first.")
        
        if top_k is None:
            top_k = self.rag_config['top_k']
        
        # Encode query
        query_embedding = self.embedding_model.encode([query])
        
        # Search
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'),
            top_k
        )
        
        # Filter by threshold
        threshold = self.rag_config['similarity_threshold']
        results = []
        
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            similarity = 1 - (dist / 2)  # Convert L2 distance to similarity
            
            if similarity >= threshold:
                results.append((self.documents[idx], similarity))
        
        return results
    
    def save_index(self, filepath: str = None):
        """
        Save FAISS index to disk
        
        Args:
            filepath: Path to save index
        """
        if filepath is None:
            filepath = self.config['models']['rag_index']
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        faiss.write_index(self.index, filepath)
        
        # Save documents separately
        doc_path = filepath + "_documents.npy"
        np.save(doc_path, self.documents)
        
        print(f"💾 RAG index saved to {filepath}")
    
    def load_index(self, filepath: str = None):
        """
        Load FAISS index from disk
        
        Args:
            filepath: Path to load index from
        """
        if filepath is None:
            filepath = self.config['models']['rag_index']
        
        self.index = faiss.read_index(filepath)
        
        # Load documents
        doc_path = filepath + "_documents.npy"
        self.documents = np.load(doc_path, allow_pickle=True).tolist()
        
        print(f"✅ RAG index loaded from {filepath}")


def main():
    """Example usage of RAGRetriever"""
    retriever = RAGRetriever()
    
    # Example documents
    sample_docs = [
        "Rice requires adequate water supply during growing season. Optimal temperature is 20-35°C.",
        "Nitrogen deficiency in crops shows yellowing of older leaves. Apply urea fertilizer.",
        "Pest control: Use neem oil spray for organic pest management in vegetables."
    ]
    
    retriever.add_documents(sample_docs)
    
    # Example query
    query = "How to treat nitrogen deficiency?"
    results = retriever.retrieve(query, top_k=2)
    
    print(f"\n🔍 Query: {query}")
    print(f"📋 Results:")
    for doc, score in results:
        print(f"   Score: {score:.4f} - {doc[:100]}...")


if __name__ == "__main__":
    main()

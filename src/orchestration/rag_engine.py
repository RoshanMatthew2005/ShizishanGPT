"""
RAG Engine
Retrieval-Augmented Generation engine using ChromaDB and sentence transformers.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
import re
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class RAGEngine:
    """RAG engine for retrieving relevant agricultural knowledge."""
    
    def __init__(self, 
                 vectorstore_path: str = "models/vectorstore",
                 collection_name: str = "agricultural_knowledge_base",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the RAG Engine.
        
        Args:
            vectorstore_path: Path to ChromaDB vectorstore
            collection_name: Name of the ChromaDB collection
            embedding_model: Name of the sentence transformer model
        """
        self.name = "rag_retrieval"
        self.description = "Retrieves relevant agricultural knowledge from PDF documents"
        self.vectorstore_path = Path(vectorstore_path)
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.is_loaded = False
        
    def load(self) -> bool:
        """Load the vectorstore and embedding model."""
        try:
            if not self.vectorstore_path.exists():
                print(f"❌ Vectorstore not found: {self.vectorstore_path}")
                print(f"❌ Please build knowledge base using: python src/build_knowledge_base.py")
                return False
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.vectorstore_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get collection
            self.collection = self.client.get_collection(self.collection_name)
            
            # Load embedding model
            print(f"Loading embedding model: {self.embedding_model_name}...")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            
            # Get collection stats
            count = self.collection.count()
            
            self.is_loaded = True
            print(f"✓ RAG Engine loaded successfully")
            print(f"✓ Collection: {self.collection_name}")
            print(f"✓ Total vectors: {count}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading RAG engine: {e}")
            return False
    
    def clean_document_text(self, text: str) -> str:
        """
        Clean retrieved document text by removing headings, subheadings, 
        page numbers, source citations, and other formatting artifacts.
        
        Args:
            text: Raw document text
            
        Returns:
            Cleaned text containing only domain content
        """
        if not text:
            return ""
        
        # First, remove source citations and page references
        # Pattern: (Source: "...", pg. 123), (Source: "..."), etc.
        text = re.sub(r'\(Source:\s*[^)]+\)', '', text, flags=re.IGNORECASE)
        
        # Remove page references: "pg. 123", "page 123", "p. 123", "pp. 123-456"
        text = re.sub(r'\b(?:pg|page|p|pp)\.?\s*\d+(?:\s*-\s*\d+)?\b', '', text, flags=re.IGNORECASE)
        
        # Remove chapter references: "Chapter 5", "Ch. 5", "Ch 5"
        text = re.sub(r'\b(?:Chapter|Ch)\.?\s*\d+\b', '', text, flags=re.IGNORECASE)
        
        # Remove section references: "Section 2.1", "Sec. 2.1"
        text = re.sub(r'\b(?:Section|Sec)\.?\s*[\d.]+\b', '', text, flags=re.IGNORECASE)
        
        # Remove watermarks and copyright notices
        text = re.sub(r'©\s*\d{4}.*?(?:\.|$)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(c\)\s*\d{4}.*?(?:\.|$)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Copyright\s*\d{4}.*?(?:\.|$)', '', text, flags=re.IGNORECASE)
        
        # Remove common header/footer patterns
        text = re.sub(r'\b(?:All rights reserved|Confidential|Draft|Internal use only)\b', '', text, flags=re.IGNORECASE)
        
        # Split into lines for processing
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Remove page numbers (various formats)
            # Pattern: "Page 5", "5", "- 5 -", "Page 5 of 10", etc.
            if re.match(r'^(?:Page\s*)?\d+(?:\s*of\s*\d+)?$', line, re.IGNORECASE):
                continue
            if re.match(r'^-?\s*\d+\s*-?$', line):
                continue
            
            # Remove standalone numbers that look like page numbers
            if re.match(r'^\d{1,3}$', line):
                continue
            
            # Skip lines that are likely headings/subheadings
            # - All caps (but keep if it's part of a sentence)
            # - Very short lines (< 5 words) that end without punctuation
            # - Lines with only numbers and dots (like "1.2.3")
            if len(line) < 50:  # Short lines might be headings
                # Skip if all caps and no sentence-ending punctuation
                if line.isupper() and not line.endswith(('.', '!', '?', ':')):
                    continue
                
                # Skip numbered headings like "1.2", "2.1.3", "Chapter 5"
                if re.match(r'^(?:Chapter|Section|Part)?\s*[\d.]+\s*$', line, re.IGNORECASE):
                    continue
                
                # Skip lines that are just heading numbers with short text
                if re.match(r'^[\d.]+\s+[A-Z][^.!?]*$', line) and len(line.split()) < 5:
                    continue
            
            # Remove chapter/section markers embedded in text
            # Pattern: "Chapter 5:", "Section 2.1:", etc.
            line = re.sub(r'^(?:Chapter|Section|Part)\s+[\d.]+\s*:?\s*', '', line, flags=re.IGNORECASE)
            
            # Remove header/footer patterns
            # Common patterns: "Agricultural Manual | Page 5", "© 2023", etc.
            if re.search(r'(?:©|\(c\)|copyright|\|)', line, re.IGNORECASE):
                if len(line.split()) < 10:  # Only skip short lines with these markers
                    continue
            
            # Remove lines that are just dotted leaders (table of contents)
            # Pattern: "Introduction ............. 5"
            if re.match(r'^.+?\.{3,}.+$', line):
                continue
            
            # Remove lines that look like titles of documents
            # Pattern: Lines ending with title-like format (all caps, short)
            if line.isupper() and len(line.split()) <= 8:
                continue
            
            # Keep the line if it passed all filters
            cleaned_lines.append(line)
        
        # Join cleaned lines with space
        cleaned_text = ' '.join(cleaned_lines)
        
        # Remove multiple spaces
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Remove isolated numbers surrounded by spaces (likely page numbers in text)
        cleaned_text = re.sub(r'\s+\d{1,3}\s+', ' ', cleaned_text)
        
        # Clean up punctuation spacing
        cleaned_text = re.sub(r'\s+([.,!?;:])', r'\1', cleaned_text)
        cleaned_text = re.sub(r'([.,!?;:])\s*([.,!?;:])', r'\1', cleaned_text)
        
        # Remove any remaining parentheses with just spaces
        cleaned_text = re.sub(r'\(\s*\)', '', cleaned_text)
        
        return cleaned_text.strip()
    
    def query(self, 
              query_text: str, 
              top_k: int = 3,
              include_metadata: bool = True) -> Dict[str, Any]:
        """
        Query the knowledge base for relevant information.
        
        Args:
            query_text: The query string
            top_k: Number of top results to return (default: 3)
            include_metadata: Whether to include metadata (default: True)
        
        Returns:
            Dictionary with query results
        """
        try:
            # Load if not already loaded
            if not self.is_loaded:
                if not self.load():
                    return {
                        "success": False,
                        "error": "Failed to load RAG engine",
                        "tool": self.name
                    }
            
            if not query_text or not query_text.strip():
                return {
                    "success": False,
                    "error": "Query text cannot be empty",
                    "tool": self.name
                }
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query_text).tolist()
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results and clean document text
            retrieved_docs = []
            for i in range(len(results['documents'][0])):
                # Clean the document text to remove headings, page numbers, etc.
                raw_content = results['documents'][0][i]
                cleaned_content = self.clean_document_text(raw_content)
                
                doc = {
                    "content": cleaned_content,  # Use cleaned content
                    "raw_content": raw_content,  # Keep raw for reference if needed
                    "distance": float(results['distances'][0][i]),
                    "relevance_score": 1.0 - float(results['distances'][0][i])  # Convert distance to similarity
                }
                
                if include_metadata and results['metadatas'][0][i]:
                    doc["metadata"] = results['metadatas'][0][i]
                
                retrieved_docs.append(doc)
            
            # Create context from cleaned documents
            context = "\n\n".join([doc['content'] for doc in retrieved_docs if doc['content']])
            
            return {
                "success": True,
                "tool": self.name,
                "query": query_text,
                "context": context,
                "num_results": len(retrieved_docs),
                "documents": retrieved_docs,
                "avg_relevance": sum(d['relevance_score'] for d in retrieved_docs) / len(retrieved_docs) if retrieved_docs else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"RAG query failed: {str(e)}",
                "tool": self.name
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary with statistics
        """
        try:
            if not self.is_loaded:
                if not self.load():
                    return {
                        "success": False,
                        "error": "Failed to load RAG engine"
                    }
            
            count = self.collection.count()
            
            return {
                "success": True,
                "tool": self.name,
                "collection_name": self.collection_name,
                "total_vectors": count,
                "embedding_model": self.embedding_model_name,
                "vectorstore_path": str(self.vectorstore_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get stats: {str(e)}"
            }
    
    def __call__(self, query_text: str, top_k: int = 3) -> Dict[str, Any]:
        """Allow the engine to be called directly."""
        return self.query(query_text, top_k)


# Example usage
if __name__ == "__main__":
    engine = RAGEngine()
    
    # Test query
    query = "What fertilizers should be used for rice cultivation?"
    result = engine.query(query, top_k=3)
    
    print("\n" + "="*70)
    print("RAG ENGINE TEST")
    print("="*70)
    print(f"Query: {query}")
    print(f"Success: {result['success']}")
    
    if result['success']:
        print(f"Number of results: {result['num_results']}")
        print(f"Average relevance: {result['avg_relevance']:.2%}")
        print("\nTop Results:")
        for i, doc in enumerate(result['documents'], 1):
            print(f"\n{i}. Relevance: {doc['relevance_score']:.2%}")
            print(f"   Content: {doc['content'][:200]}...")
            if 'metadata' in doc:
                print(f"   Source: {doc['metadata'].get('source', 'N/A')}")
    else:
        print(f"Error: {result['error']}")
    
    print("="*70)
    
    # Test stats
    stats = engine.get_stats()
    if stats['success']:
        print(f"\nKnowledge Base Stats:")
        print(f"  Total vectors: {stats['total_vectors']}")
        print(f"  Embedding model: {stats['embedding_model']}")

"""
Query Knowledge Base - Interactive Testing Script
=================================================
This script allows you to interactively query the built knowledge base.

Usage:
    python query_knowledge_base.py

Requirements:
    - The vector store must be built first (run build_knowledge_base.py)
"""

import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings
import os

# Configuration
VECTORSTORE_FOLDER = "models/vectorstore"
COLLECTION_NAME = "agricultural_knowledge_base"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_knowledge_base():
    """Load the pre-built vector store and embedding model."""
    
    if not os.path.exists(VECTORSTORE_FOLDER):
        print(f"❌ Error: Vector store not found at {VECTORSTORE_FOLDER}")
        print("Please run build_knowledge_base.py first to create the knowledge base.")
        return None, None
    
    print("Loading knowledge base...")
    
    # Load ChromaDB
    client = chromadb.PersistentClient(
        path=VECTORSTORE_FOLDER,
        settings=Settings(anonymized_telemetry=False)
    )
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"✓ Loaded collection: {COLLECTION_NAME}")
        print(f"✓ Total chunks in database: {collection.count()}")
    except Exception as e:
        print(f"❌ Error loading collection: {e}")
        return None, None
    
    # Load embedding model
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("✓ Embedding model loaded\n")
    
    return collection, model


def query_knowledge_base(collection, model, query, top_k=5):
    """
    Query the knowledge base and return relevant chunks.
    
    Args:
        collection: ChromaDB collection
        model: Sentence transformer model
        query: Query string
        top_k: Number of results to return
        
    Returns:
        Query results
    """
    # Generate query embedding
    query_embedding = model.encode([query])[0].tolist()
    
    # Retrieve similar chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    return results


def display_results(results, query):
    """Display search results in a readable format."""
    
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)
    
    if not results['documents'][0]:
        print("\n❌ No results found.")
        return
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        similarity = 1 - distance  # Convert distance to similarity score
        
        print(f"\n📄 Result {i+1}")
        print(f"   Source: {metadata.get('source', 'Unknown')}")
        print(f"   Page: {metadata.get('page', 'N/A')} of {metadata.get('total_pages', 'N/A')}")
        print(f"   Relevance: {similarity:.2%}")
        print(f"   Chunk ID: {metadata.get('chunk_id', 'N/A')}")
        print(f"\n   Content:")
        print(f"   {'-' * 76}")
        
        # Display content with word wrapping
        content = doc.strip()
        words = content.split()
        line = "   "
        for word in words:
            if len(line) + len(word) + 1 > 80:
                print(line)
                line = "   " + word
            else:
                line += (" " + word) if line.strip() else word
        if line.strip():
            print(line)
        
        print(f"   {'-' * 76}")
    
    print("\n" + "=" * 80 + "\n")


def interactive_mode(collection, model):
    """Run interactive query mode."""
    
    print("\n" + "=" * 80)
    print("INTERACTIVE QUERY MODE")
    print("=" * 80)
    print("\nEnter your questions about agriculture. Type 'quit' or 'exit' to stop.")
    print("Type 'examples' to see sample queries.\n")
    
    while True:
        query = input("🔍 Your question: ").strip()
        
        if not query:
            continue
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if query.lower() == 'examples':
            show_examples()
            continue
        
        # Get number of results
        try:
            num_results = input("   Number of results (default 3): ").strip()
            top_k = int(num_results) if num_results else 3
        except ValueError:
            top_k = 3
        
        # Query and display results
        results = query_knowledge_base(collection, model, query, top_k=top_k)
        display_results(results, query)


def show_examples():
    """Display example queries."""
    
    print("\n" + "=" * 80)
    print("EXAMPLE QUERIES")
    print("=" * 80)
    
    examples = [
        "What fertilizer should be used for maize?",
        "How to manage pests in organic farming?",
        "What are the best practices for soil conservation?",
        "Tell me about crop rotation techniques",
        "What is integrated pest management?",
        "How to improve soil fertility?",
        "What are the common diseases in solanaceous crops?",
        "Explain rainfed agriculture practices",
        "What is the recommended seed rate for maize?",
        "How to handle drought conditions in agriculture?"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i:2d}. {example}")
    
    print("=" * 80 + "\n")


def batch_query_mode(collection, model):
    """Run predefined queries for testing."""
    
    print("\n" + "=" * 80)
    print("BATCH QUERY MODE - Testing with Sample Questions")
    print("=" * 80)
    
    test_queries = [
        "What fertilizer should be used for maize?",
        "How to manage pests in organic farming?",
        "What are the best practices for soil conservation?"
    ]
    
    for query in test_queries:
        results = query_knowledge_base(collection, model, query, top_k=3)
        display_results(results, query)
        input("Press Enter to continue to next query...")


def main():
    """Main execution function."""
    
    # Load knowledge base
    collection, model = load_knowledge_base()
    
    if collection is None or model is None:
        return
    
    # Show menu
    print("\nSelect mode:")
    print("1. Interactive Query Mode (recommended)")
    print("2. Batch Test Mode (run predefined queries)")
    print("3. Single Query")
    
    choice = input("\nYour choice (1-3): ").strip()
    
    if choice == "1":
        interactive_mode(collection, model)
    elif choice == "2":
        batch_query_mode(collection, model)
    elif choice == "3":
        query = input("\nEnter your query: ").strip()
        if query:
            results = query_knowledge_base(collection, model, query, top_k=5)
            display_results(results, query)
    else:
        print("Invalid choice. Running interactive mode by default...")
        interactive_mode(collection, model)


if __name__ == "__main__":
    main()

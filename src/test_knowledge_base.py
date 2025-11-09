"""
Quick Test Script - Verify RAG Knowledge Base
==============================================
This script quickly tests if the knowledge base was built successfully.
"""

import os
import chromadb
from chromadb.config import Settings

# Configuration
VECTORSTORE_FOLDER = "models/vectorstore"
COLLECTION_NAME = "agricultural_knowledge_base"

def test_knowledge_base():
    """Quick test to verify the knowledge base exists and is queryable."""
    
    print("\n" + "=" * 70)
    print("RAG KNOWLEDGE BASE - QUICK TEST")
    print("=" * 70 + "\n")
    
    # Check if vectorstore exists
    if not os.path.exists(VECTORSTORE_FOLDER):
        print(f"[ERROR] Vector store not found at {VECTORSTORE_FOLDER}")
        print("Please run build_knowledge_base.py first!")
        return False
    
    print(f"[OK] Vector store folder found: {VECTORSTORE_FOLDER}")
    
    try:
        # Load ChromaDB
        client = chromadb.PersistentClient(
            path=VECTORSTORE_FOLDER,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get collection
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"[OK] Collection loaded: {COLLECTION_NAME}")
        
        # Get collection stats
        count = collection.count()
        print(f"[OK] Total chunks in database: {count:,}")
        
        # Get a sample
        sample = collection.get(limit=1, include=["documents", "metadatas"])
        
        if sample['documents']:
            print(f"\n[OK] Sample chunk retrieved successfully")
            print(f"     Source: {sample['metadatas'][0].get('source', 'Unknown')}")
            print(f"     Page: {sample['metadatas'][0].get('page', 'N/A')}")
            print(f"     Content preview: {sample['documents'][0][:150]}...")
        
        print("\n" + "=" * 70)
        print("[SUCCESS] Knowledge base is working correctly!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Run: python query_knowledge_base.py")
        print("  2. Ask agricultural questions interactively")
        print("  3. Integrate with LLM for answer generation")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Failed to load knowledge base: {str(e)}")
        print("Please check the build log for errors.")
        return False


if __name__ == "__main__":
    success = test_knowledge_base()
    exit(0 if success else 1)

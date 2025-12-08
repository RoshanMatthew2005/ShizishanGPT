#!/usr/bin/env python3
"""Direct test of RAG functionality"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backend.models.load_vectorstore import load_vectorstore
from backend.dependencies import ModelRegistry
from backend.config import settings

async def test_rag():
    """Test RAG retrieval functionality"""
    try:
        print("Loading vectorstore...")
        
        # Load vectorstore directly
        vectorstore = load_vectorstore(settings.VECTORSTORE_PATH)
        registry = ModelRegistry()
        registry.register("vectorstore", vectorstore)
        print(f"✓ Loaded vectorstore with {vectorstore.collection.count()} documents")
        
        # Now import RAG service after vectorstore is loaded
        from backend.services.rag_service import rag_service
        
        print("Testing RAG retrieval...")
        
        # Test query
        query = "crop diseases"
        result = await rag_service.retrieve(query, top_k=3)
        
        print(f"✓ RAG Test Results:")
        print(f"  Query: {query}")
        print(f"  Number of results: {result['num_results']}")
        print(f"  Average relevance: {result['avg_relevance']:.4f}")
        print(f"  Context length: {len(result['context'])} chars")
        
        print("\n  Top documents:")
        for i, doc in enumerate(result['documents'][:2]):
            print(f"    {i+1}. Relevance: {doc['relevance']:.4f}")
            print(f"       Text: {doc['text'][:150]}...")
            print(f"       Source: {doc['metadata'].get('source', 'unknown')}")
            print()
        
        return True
        
    except Exception as e:
        print(f"✗ RAG test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_rag())
    if success:
        print("✅ RAG functionality working correctly!")
    else:
        print("❌ RAG functionality failed!")
        sys.exit(1)
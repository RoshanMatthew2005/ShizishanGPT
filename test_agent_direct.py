#!/usr/bin/env python3
"""Test ReAct Agent functionality"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backend.services.agent_service import agent_service
from backend.models.load_vectorstore import load_vectorstore
from backend.models.load_mini_llm import load_mini_llm
from backend.dependencies import ModelRegistry
from backend.config import settings

async def test_agent():
    """Test ReAct agent functionality"""
    try:
        print("="*60)
        print("TESTING REACT AGENT FUNCTIONALITY")
        print("="*60)
        
        # Load required models
        print("Loading models...")
        registry = ModelRegistry()
        
        # Load vectorstore
        vectorstore = load_vectorstore(settings.VECTORSTORE_PATH)
        registry.register("vectorstore", vectorstore)
        print(f"✓ Vectorstore: {vectorstore.collection.count()} documents")
        
        # Load mini LLM
        mini_llm = load_mini_llm(settings.MINI_LLM_PATH)
        registry.register("mini_llm", mini_llm)
        print(f"✓ Mini LLM: {mini_llm.model.config.vocab_size} vocab")
        
        print("\nTesting agent modes...")
        
        # Test queries for different agent modes
        test_cases = [
            {
                "query": "What are the best fertilizers for maize crops?",
                "mode": "auto",
                "description": "Auto mode - let agent choose tools"
            },
            {
                "query": "How do I identify tomato diseases?", 
                "mode": "react",
                "description": "ReAct mode - full reasoning loop"
            },
            {
                "query": "Tell me about crop rotation benefits",
                "mode": "direct",
                "description": "Direct LLM mode - no tools"
            }
        ]
        
        results = []
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n--- Test {i}: {test['description']} ---")
            print(f"Query: {test['query']}")
            
            try:
                result = await agent_service.process_query(
                    query=test['query'],
                    mode=test['mode'],
                    max_iterations=3,
                    verbose=False
                )
                
                print(f"✓ Mode: {test['mode']}")
                print(f"✓ Answer: {result['answer'][:200]}...")
                print(f"✓ Tools used: {result.get('tools_used', [])}")
                print(f"✓ Execution time: {result.get('execution_time', 0):.2f}s")
                
                results.append({
                    "mode": test['mode'],
                    "success": True,
                    "tools": result.get('tools_used', []),
                    "time": result.get('execution_time', 0)
                })
                
            except Exception as e:
                print(f"✗ Failed: {e}")
                results.append({
                    "mode": test['mode'],
                    "success": False,
                    "error": str(e)
                })
        
        print("\n" + "="*60)
        print("REACT AGENT TEST SUMMARY")
        print("="*60)
        
        success_count = sum(1 for r in results if r['success'])
        print(f"Tests passed: {success_count}/{len(results)}")
        
        for result in results:
            status = "✅" if result['success'] else "❌"
            mode = result['mode'].upper()
            if result['success']:
                tools = result.get('tools', [])
                time = result.get('time', 0)
                print(f"{status} {mode} mode - Tools: {tools} - Time: {time:.2f}s")
            else:
                error = result.get('error', 'Unknown error')
                print(f"{status} {mode} mode - Error: {error}")
        
        if success_count == len(results):
            print("\n🎉 All ReAct agent modes working correctly!")
            return True
        else:
            print(f"\n⚠️ {len(results) - success_count} agent modes failed")
            return False
        
    except Exception as e:
        print(f"✗ Agent test setup failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agent())
    sys.exit(0 if success else 1)
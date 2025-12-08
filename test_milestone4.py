"""
Test Suite for Milestone 4 - Mini LangChain + ReAct Agent
Tests all components of the orchestration system.
"""
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestration.main_orchestrator import ShizishanGPTOrchestrator


def test_individual_tools():
    """Test each tool individually."""
    from orchestration.tool_registry import get_registry
    
    print("\n" + "="*70)
    print("TEST 1: INDIVIDUAL TOOLS")
    print("="*70)
    
    registry = get_registry()
    
    # Test RAG tool
    print("\n1. Testing RAG Engine...")
    rag_tool = registry.get_tool("rag_retrieval")
    if rag_tool:
        result = rag_tool.query("What fertilizers for rice?", top_k=2)
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   Retrieved {result['num_results']} documents")
            print(f"   Context: {result['context'][:150]}...")
    
    # Test LLM tool
    print("\n2. Testing LLM Engine...")
    llm_tool = registry.get_tool("llm_generation")
    if llm_tool:
        result = llm_tool.generate("Rice cultivation requires")
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   Generated: {result['generated_text'][:150]}...")
    
    # Test Translation tool
    print("\n3. Testing Translation Tool...")
    trans_tool = registry.get_tool("translation")
    if trans_tool:
        result = trans_tool.run("Rice is important", target_lang="hi")
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   Translation: {result.get('translated_text', 'N/A')}")
    
    print("\n" + "="*70)


def test_router():
    """Test the tool router."""
    from orchestration.tool_router import ToolRouter
    
    print("\n" + "="*70)
    print("TEST 2: TOOL ROUTER")
    print("="*70)
    
    router = ToolRouter()
    
    test_queries = [
        "What fertilizers should be used for rice?",
        "How much rainfall is needed for corn?",
        "Translate this to Hindi: Rice farming",
        "What is nitrogen fertilizer?"
    ]
    
    for query in test_queries:
        result = router.route(query)
        print(f"\nQuery: {query}")
        print(f"  Selected: {result.get('selected_tool', 'N/A')}")
        print(f"  Confidence: {result.get('confidence', 0):.0%}")
        print(f"  Reasons: {', '.join(result.get('reasoning', [])[:2])}")
    
    print("\n" + "="*70)


def test_pipeline():
    """Test the pipeline system."""
    from orchestration.mini_langchain import Pipeline
    
    print("\n" + "="*70)
    print("TEST 3: PIPELINE")
    print("="*70)
    
    # Create a simple test pipeline
    def step1(value: int = 0, **kwargs):
        return {"success": True, "value": value + 10}
    
    def step2(value: int = 0, **kwargs):
        return {"success": True, "value": value * 2}
    
    pipeline = Pipeline("Test Pipeline")
    pipeline.add_step("add_10", step1, "Add 10")
    pipeline.add_step("multiply_2", step2, "Multiply by 2")
    
    result = pipeline.execute({"value": 5})
    
    print(f"\nPipeline Success: {result['success']}")
    print(f"Final Value: {result['final_result']['value']}")
    print(f"Expected: 30 (5 + 10 = 15, 15 * 2 = 30)")
    
    print("\n" + "="*70)


def test_history():
    """Test the history manager."""
    from orchestration.history_manager import HistoryManager
    
    print("\n" + "="*70)
    print("TEST 4: HISTORY MANAGER")
    print("="*70)
    
    history = HistoryManager(max_history=5)
    
    # Add some turns
    history.add_turn("What is rice?", "Rice is a cereal grain", {"tool": "llm"})
    history.add_turn("Best fertilizer?", "Use NPK 4:2:1", {"tool": "rag"})
    history.add_turn("Translate to Hindi", "चावल महत्वपूर्ण है", {"tool": "translation"})
    
    print(f"\nTotal turns: {len(history)}")
    print(f"\nFormatted history:")
    print(history.format_history(n=3, include_metadata=True))
    
    stats = history.get_stats()
    print(f"Stats: {stats['total_turns']} turns, {stats['session_duration_seconds']:.1f}s session")
    
    print("\n" + "="*70)


def test_react_agent():
    """Test the ReAct agent."""
    from orchestration.react_agent import ReActAgent
    
    print("\n" + "="*70)
    print("TEST 5: REACT AGENT")
    print("="*70)
    
    agent = ReActAgent(max_iterations=3, verbose=True)
    
    query = "What are the best practices for wheat farming?"
    
    result = agent.run(query)
    
    print(f"\n{'='*70}")
    print("AGENT RESULT")
    print(f"{'='*70}")
    print(f"Query: {result['query']}")
    print(f"Success: {result['success']}")
    print(f"Answer: {result.get('final_answer', 'N/A')[:200]}...")
    print(f"Tools Used: {', '.join(result.get('tools_used', []))}")
    print(f"Iterations: {result.get('total_iterations', 0)}")
    print(f"Time: {result.get('execution_time', 0):.2f}s")
    print(f"{'='*70}")


def test_orchestrator():
    """Test the main orchestrator."""
    print("\n" + "="*70)
    print("TEST 6: MAIN ORCHESTRATOR")
    print("="*70)
    
    orchestrator = ShizishanGPTOrchestrator(
        enable_mongo=False,
        verbose=False
    )
    
    test_queries = [
        "What is the best fertilizer for maize?",
        "How to control pests in tomatoes?",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = orchestrator.query(query, mode="auto")
        
        print(f"Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"Answer: {result.get('final_answer', '')[:150]}...")
            print(f"Tools: {', '.join(result.get('tools_used', []))}")
    
    orchestrator.shutdown()
    
    print("\n" + "="*70)


def run_all_tests():
    """Run all tests."""
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "  MILESTONE 4 - MINI LANGCHAIN + REACT AGENT TEST SUITE".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    tests = [
        ("Individual Tools", test_individual_tools),
        ("Tool Router", test_router),
        ("Pipeline System", test_pipeline),
        ("History Manager", test_history),
        ("ReAct Agent", test_react_agent),
        ("Main Orchestrator", test_orchestrator)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n\n{'#'*70}")
            print(f"# Running: {test_name}")
            print(f"{'#'*70}")
            
            test_func()
            
            passed += 1
            print(f"\n✅ {test_name} PASSED")
            
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} FAILED")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "  TEST SUMMARY".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    print(f"\nTotal Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {passed/len(tests)*100:.1f}%")
    print("\n" + "#"*70 + "\n")


if __name__ == "__main__":
    run_all_tests()

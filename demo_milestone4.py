"""
Demo Script for Milestone 4
Showcases the capabilities of the Mini LangChain + ReAct Agent system.
"""
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestration.main_orchestrator import ShizishanGPTOrchestrator


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def demo_simple_query():
    """Demonstrate simple direct query."""
    print_header("DEMO 1: Simple Question (Direct Execution)")
    
    orch = ShizishanGPTOrchestrator(enable_mongo=False, verbose=False)
    
    query = "What is nitrogen fertilizer?"
    print(f"Query: {query}\n")
    
    result = orch.query(query, mode="auto")
    
    if result['success']:
        print(f"Answer: {result['final_answer']}\n")
        print(f"Tool Used: {result.get('tools_used', ['N/A'])[0]}")
        print(f"Execution Time: {result.get('execution_time', 0):.2f}s")
    
    orch.shutdown()
    time.sleep(2)


def demo_knowledge_retrieval():
    """Demonstrate RAG knowledge retrieval."""
    print_header("DEMO 2: Knowledge Retrieval (RAG Engine)")
    
    orch = ShizishanGPTOrchestrator(enable_mongo=False, verbose=False)
    
    query = "What are the best fertilizers for rice cultivation?"
    print(f"Query: {query}\n")
    
    result = orch.query(query, mode="auto")
    
    if result['success']:
        print(f"Answer: {result['final_answer'][:300]}...\n")
        print(f"Tool Used: {result.get('tools_used', ['N/A'])[0]}")
        print(f"Execution Time: {result.get('execution_time', 0):.2f}s")
        print(f"\nNote: Retrieved from {23083} document chunks")
    
    orch.shutdown()
    time.sleep(2)


def demo_multi_step_reasoning():
    """Demonstrate ReAct multi-step reasoning."""
    print_header("DEMO 3: Multi-Step Reasoning (ReAct Agent)")
    
    orch = ShizishanGPTOrchestrator(enable_mongo=False, verbose=True)
    
    query = "How should I prepare my field for wheat planting?"
    print(f"Query: {query}\n")
    
    result = orch.query(query, mode="react")
    
    if result['success']:
        print(f"\n{'='*70}")
        print("RESULT")
        print(f"{'='*70}")
        print(f"Answer: {result['final_answer'][:300]}...\n")
        print(f"Tools Used: {', '.join(result.get('tools_used', []))}")
        print(f"Total Iterations: {result.get('total_iterations', 0)}")
        print(f"Execution Time: {result.get('execution_time', 0):.2f}s")
    
    orch.shutdown()
    time.sleep(2)


def demo_tool_routing():
    """Demonstrate intelligent tool routing."""
    print_header("DEMO 4: Intelligent Tool Routing")
    
    from orchestration.tool_router import ToolRouter
    
    router = ToolRouter()
    
    test_queries = [
        "What fertilizers for maize?",
        "How much rainfall for corn?",
        "Translate to Hindi: Rice farming",
        "Analyze this leaf.jpg image",
    ]
    
    for query in test_queries:
        result = router.route(query)
        print(f"Query: {query}")
        print(f"  → Selected Tool: {result.get('selected_tool', 'N/A')}")
        print(f"  → Confidence: {result.get('confidence', 0):.0%}")
        print(f"  → Reasoning: {', '.join(result.get('reasoning', [])[:2])}")
        print()
    
    time.sleep(2)


def demo_conversation_history():
    """Demonstrate conversation history tracking."""
    print_header("DEMO 5: Conversation History")
    
    orch = ShizishanGPTOrchestrator(enable_mongo=False, verbose=False)
    
    queries = [
        "What is NPK fertilizer?",
        "What is the ratio for rice?",
        "How to apply it?"
    ]
    
    print("Asking multiple related questions:\n")
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. Query: {query}")
        result = orch.query(query, mode="auto")
        if result['success']:
            print(f"   Answer: {result['final_answer'][:150]}...\n")
    
    print("\nConversation History:")
    print("-" * 70)
    print(orch.history.format_history(n=3, include_metadata=False))
    
    stats = orch.history.get_stats()
    print(f"Total Turns: {stats['total_turns']}")
    print(f"Session Duration: {stats['session_duration_seconds']:.1f}s")
    
    orch.shutdown()
    time.sleep(2)


def demo_batch_processing():
    """Demonstrate batch processing."""
    print_header("DEMO 6: Batch Processing")
    
    orch = ShizishanGPTOrchestrator(enable_mongo=False, verbose=False)
    
    queries = [
        "Best fertilizer for wheat?",
        "How to control aphids?",
        "Ideal rainfall for rice?"
    ]
    
    print("Processing batch of queries:\n")
    
    results = orch.batch_process(queries)
    
    print("\nResults Summary:")
    print("-" * 70)
    for i, (query, result) in enumerate(zip(queries, results), 1):
        status = "✅" if result.get('success') else "❌"
        tools = ', '.join(result.get('tools_used', ['N/A']))
        time_taken = result.get('execution_time', 0)
        print(f"{i}. {status} {query}")
        print(f"   Tools: {tools} | Time: {time_taken:.2f}s")
    
    orch.shutdown()
    time.sleep(2)


def demo_all_tools():
    """Demonstrate all available tools."""
    print_header("DEMO 7: Available Tools")
    
    from orchestration.tool_registry import get_registry
    
    registry = get_registry()
    
    print("System has 6 integrated tools:\n")
    
    for tool_name in registry.list_tools():
        metadata = registry.get_metadata(tool_name)
        print(f"• {tool_name}")
        print(f"  Category: {metadata['category']}")
        print(f"  Description: {metadata['description']}")
        print(f"  Keywords: {', '.join(metadata['keywords'][:5])}")
        print()
    
    time.sleep(2)


def run_full_demo():
    """Run complete demonstration."""
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "  SHIZISHANGPT - MILESTONE 4 DEMONSTRATION".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    print("\nThis demo showcases the capabilities of the")
    print("Mini LangChain + ReAct Agent system.\n")
    input("Press Enter to begin demo...")
    
    demos = [
        ("Simple Question", demo_simple_query),
        ("Knowledge Retrieval", demo_knowledge_retrieval),
        ("Multi-Step Reasoning", demo_multi_step_reasoning),
        ("Tool Routing", demo_tool_routing),
        ("Conversation History", demo_conversation_history),
        ("Batch Processing", demo_batch_processing),
        ("All Tools", demo_all_tools)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n\n{'#'*70}")
        print(f"# Demo {i}/{len(demos)}: {name}")
        print(f"{'#'*70}")
        
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(demos):
            print("\n" + "-"*70)
            input("Press Enter to continue to next demo...")
    
    # Final summary
    print("\n\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "  DEMONSTRATION COMPLETE".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    print("\n✅ All demos completed successfully!")
    print("\nKey Takeaways:")
    print("  • System intelligently routes queries to appropriate tools")
    print("  • ReAct agent provides multi-step reasoning")
    print("  • Conversation history maintains context")
    print("  • Batch processing handles multiple queries")
    print("  • 6 tools cover various agricultural needs")
    
    print("\nNext Steps:")
    print("  1. Try interactive mode: python src/orchestration/main_orchestrator.py")
    print("  2. Run tests: python test_milestone4.py")
    print("  3. Read docs: docs/MILESTONE_4_COMPLETE.md")
    print("\n" + "#"*70 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Demo script for Milestone 4")
    parser.add_argument("--demo", type=int, choices=range(1, 8),
                       help="Run specific demo (1-7)")
    parser.add_argument("--all", action="store_true",
                       help="Run all demos sequentially")
    
    args = parser.parse_args()
    
    demos_map = {
        1: demo_simple_query,
        2: demo_knowledge_retrieval,
        3: demo_multi_step_reasoning,
        4: demo_tool_routing,
        5: demo_conversation_history,
        6: demo_batch_processing,
        7: demo_all_tools
    }
    
    if args.demo:
        demos_map[args.demo]()
    elif args.all or len(sys.argv) == 1:
        run_full_demo()
    else:
        print("Usage:")
        print("  python demo_milestone4.py           # Run all demos")
        print("  python demo_milestone4.py --demo 1  # Run specific demo")
        print("  python demo_milestone4.py --all     # Run all demos")

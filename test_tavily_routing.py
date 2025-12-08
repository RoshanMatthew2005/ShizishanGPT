"""
Quick test to verify Tavily tool is registered and routing works
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.orchestration.tool_registry import get_registry
from src.orchestration.tool_router import ToolRouter


def test_tavily_registration():
    """Test if Tavily tool is registered"""
    print("\n" + "="*70)
    print("TEST 1: TAVILY TOOL REGISTRATION")
    print("="*70)
    
    registry = get_registry()
    tools = registry.list_tools()
    
    print(f"\nTotal tools registered: {len(tools)}")
    print(f"Available tools: {', '.join(tools)}")
    
    if "tavily_search" in tools:
        print("\n✅ Tavily tool is registered!")
        
        # Get metadata
        metadata = registry.get_metadata("tavily_search")
        print(f"\nTavily Tool Details:")
        print(f"  Description: {metadata['description']}")
        print(f"  Category: {metadata['category']}")
        print(f"  Keywords: {', '.join(metadata['keywords'][:10])}...")
        
        # Get tool instance
        tool = registry.get_tool("tavily_search")
        print(f"  Tool instance: {tool}")
        print(f"  Tool name: {tool.name}")
        
        return True
    else:
        print("\n❌ Tavily tool NOT registered!")
        return False


def test_routing():
    """Test if router selects Tavily for appropriate queries"""
    print("\n" + "="*70)
    print("TEST 2: ROUTING LOGIC")
    print("="*70)
    
    router = ToolRouter()
    
    test_queries = [
        "What is the best pesticide for whitefly in cotton in 2025?",
        "Where can I buy neem oil?",
        "Latest fertilizer subsidy scheme",
        "Recommended fungicide for tomato blight",
        "How to treat rust disease in wheat?",
        "What is photosynthesis?",  # Should route to RAG
        "Predict yield for wheat in Punjab"  # Should route to yield_prediction
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: \"{query}\"")
        result = router.route(query)
        
        if result.get("success"):
            selected_tool = result.get("selected_tool")
            confidence = result.get("confidence", 0)
            print(f"   ➜ Selected tool: {selected_tool}")
            print(f"   ➜ Confidence: {confidence:.2f}")
            
            # Check if Tavily queries route to Tavily
            if any(keyword in query.lower() for keyword in ["best", "pesticide", "where", "buy", "latest", "recommended", "treat"]):
                if selected_tool == "tavily_search":
                    print(f"   ✅ Correct! Routed to Tavily")
                else:
                    print(f"   ⚠️  Warning: Should route to Tavily but got {selected_tool}")
        else:
            print(f"   ❌ Routing failed: {result.get('error')}")


def test_tool_call():
    """Test calling the Tavily tool directly"""
    print("\n" + "="*70)
    print("TEST 3: DIRECT TOOL CALL")
    print("="*70)
    
    registry = get_registry()
    tool = registry.get_tool("tavily_search")
    
    if not tool:
        print("❌ Cannot get Tavily tool from registry")
        return
    
    print("\n🔍 Testing Tavily search...")
    print("Query: 'best pesticide for whitefly in cotton 2025'")
    
    try:
        result = tool.search("best pesticide for whitefly in cotton 2025", max_results=3)
        
        if result.get("success"):
            print(f"\n✅ Search successful!")
            print(f"   Results count: {result.get('results_count', 0)}")
            print(f"   Response time: {result.get('response_time', 0):.2f}s")
            
            if result.get("answer"):
                print(f"\n   Quick Answer: {result['answer'][:200]}...")
            
            print(f"\n   Summary (first 500 chars):")
            summary = result.get("summary", "")
            print(f"   {summary[:500]}...")
            
        else:
            print(f"\n❌ Search failed: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TAVILY INTEGRATION VERIFICATION")
    print("="*70)
    
    # Run tests
    registered = test_tavily_registration()
    
    if registered:
        test_routing()
        test_tool_call()
    else:
        print("\n⚠️  Skipping other tests because Tavily is not registered")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE")
    print("="*70 + "\n")

"""
Direct test of Tavily tool to see what it actually returns
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.model_tools.tavily_tool import TavilyTool


def test_tavily_direct():
    """Test Tavily tool directly to see results"""
    print("\n" + "="*70)
    print("DIRECT TAVILY TOOL TEST")
    print("="*70)
    
    tool = TavilyTool()
    
    query = "best pesticide for whitefly in cotton 2025"
    print(f"\n📝 Query: {query}")
    print("\n🔍 Calling Tavily...")
    
    result = tool.search(query, max_results=5)
    
    print(f"\n{'='*70}")
    print("FULL RESULT:")
    print('='*70)
    
    import json
    print(json.dumps(result, indent=2))
    
    print(f"\n{'='*70}")
    print("SUMMARY FIELD (what agent sees):")
    print('='*70)
    
    if result.get("success"):
        summary = result.get("summary", "")
        print(summary)
    else:
        print(f"ERROR: {result.get('error')}")


if __name__ == "__main__":
    test_tavily_direct()

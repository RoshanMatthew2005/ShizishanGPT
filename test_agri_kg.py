"""
Test Agriculture Knowledge Graph
Test script for AgriKG queries.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.knowledge_graph.query_engine import AgriKGQueryEngine


def test_queries():
    """Test various knowledge graph queries."""
    print("\n" + "="*70)
    print("🌾 AgriKG Query Test Suite")
    print("="*70 + "\n")
    
    # Initialize engine
    engine = AgriKGQueryEngine()
    
    if not engine.load():
        print("❌ Failed to connect to knowledge graph")
        print("   Make sure Neo4j is running and AgriKG is built")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "Diseases affecting Rice",
            "function": lambda: engine.get_diseases_for_crop("rice")
        },
        {
            "name": "Pests affecting Wheat",
            "function": lambda: engine.get_pests_for_crop("wheat")
        },
        {
            "name": "Fertilizers for Maize",
            "function": lambda: engine.get_fertilizers_for_crop("maize")
        },
        {
            "name": "Ideal Soil for Rice",
            "function": lambda: engine.get_ideal_soil_for_crop("rice")
        },
        {
            "name": "Natural Language: What diseases affect rice?",
            "function": lambda: engine.natural_language_query("What diseases affect rice?")
        },
        {
            "name": "Natural Language: Which pests attack wheat?",
            "function": lambda: engine.natural_language_query("Which pests attack wheat?")
        },
        {
            "name": "Complete Crop Info: Rice",
            "function": lambda: engine.get_complete_crop_info("rice")
        },
    ]
    
    # Run tests
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*70}")
        print(f"Test {i}: {test['name']}")
        print('─'*70)
        
        try:
            result = test['function']()
            
            if result['success']:
                print(f"✅ Success - Found {result['count']} results")
                
                if result['count'] > 0:
                    print("\nResults:")
                    formatted = engine.format_results(result)
                    # Print first 5 results
                    lines = formatted.split('\n')[:5]
                    for line in lines:
                        print(f"  {line}")
                    total_lines = len(formatted.split('\n'))
                    if total_lines > 5:
                        print(f"  ... and {total_lines - 5} more")
                else:
                    print("  No results found (knowledge base may need more data)")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n{'='*70}")
    print("Test Suite Complete")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    test_queries()

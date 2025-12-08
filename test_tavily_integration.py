"""
Test Tavily Integration
Tests the complete Tavily search integration through middleware
"""

import requests
import json
from typing import Dict, Any

MIDDLEWARE_URL = "http://localhost:5000"

# Test queries covering different agricultural use cases
TEST_QUERIES = [
    # Pest Management
    {
        "query": "best pesticide for whitefly in cotton crops India 2025",
        "category": "Pest Management",
        "expected": "Product names, chemical compositions, application rates, brands"
    },
    
    # Government Schemes
    {
        "query": "latest fertilizer subsidy scheme for farmers India 2025",
        "category": "Government Policy",
        "expected": "Policy details, eligibility, application process, subsidy amounts"
    },
    
    # Disease Treatment
    {
        "query": "how to treat rust disease in wheat organic methods",
        "category": "Disease Treatment",
        "expected": "Treatment protocols, fungicide recommendations, cultural practices"
    },
    
    # Product Availability
    {
        "query": "where to buy neem oil pesticide near me Maharashtra",
        "category": "Product Availability",
        "expected": "Supplier information, online availability, pricing"
    },
    
    # Recent Research
    {
        "query": "latest research on biopesticides for tomato cultivation",
        "category": "Research",
        "expected": "Recent studies, new products, efficacy data"
    },
    
    # Chemical Information
    {
        "query": "imidacloprid dosage for aphid control in potato",
        "category": "Chemical Info",
        "expected": "Dosage rates, application timing, safety precautions"
    },
    
    # Fertilizer Recommendations
    {
        "query": "NPK fertilizer ratio for rice paddy pre-monsoon application",
        "category": "Fertilizer",
        "expected": "Fertilizer grades, application rates, timing recommendations"
    },
    
    # Market Intelligence
    {
        "query": "current urea fertilizer prices in India December 2025",
        "category": "Market Info",
        "expected": "Current prices, market trends, availability status"
    },
    
    # Outbreak Alerts
    {
        "query": "fall armyworm outbreak alert India 2025",
        "category": "Pest Alert",
        "expected": "Current outbreak information, affected regions, control measures"
    },
    
    # Integrated Pest Management
    {
        "query": "integrated pest management protocol for brinjal fruit borer",
        "category": "IPM",
        "expected": "IPM strategies, monitoring methods, chemical and biological controls"
    }
]

def test_tavily_search(query: str, category: str = "General", use_agricultural: bool = False) -> Dict[str, Any]:
    """Test Tavily search through middleware"""
    
    endpoint = "/api/tavily_search/agricultural" if use_agricultural else "/api/tavily_search"
    
    try:
        response = requests.post(
            f"{MIDDLEWARE_URL}{endpoint}",
            json={
                "query": query,
                "max_results": 3
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n{'='*80}")
            print(f"✅ [{category}] {query}")
            print(f"{'='*80}")
            print(f"   📊 Results: {result['results_count']}")
            print(f"   ⏱️  Time: {result['response_time']}s")
            
            if result.get('answer'):
                print(f"\n   💡 AI Answer:")
                print(f"   {result['answer'][:200]}...")
            
            print(f"\n   🔗 Top Sources:")
            for i, item in enumerate(result.get('results', [])[:3], 1):
                print(f"   {i}. {item['title'][:60]}...")
                print(f"      Score: {item['score']:.2f} | {item['url'][:60]}...")
                print(f"      {item['content'][:100]}...")
                print()
            
            return result
        else:
            print(f"\n❌ [{category}] Error {response.status_code}")
            print(f"   Query: {query}")
            print(f"   Response: {response.text[:200]}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Is middleware running on {MIDDLEWARE_URL}?")
        return None
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None

def test_direct_backend():
    """Test direct FastAPI backend endpoint"""
    backend_url = "http://localhost:8000"
    
    print(f"\n{'='*80}")
    print("Testing Direct Backend Connection")
    print(f"{'='*80}")
    
    try:
        response = requests.post(
            f"{backend_url}/api/tavily_search",
            json={
                "query": "organic pest control methods",
                "max_results": 2
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Backend connection successful")
            result = response.json()
            print(f"   Results: {result['results_count']}")
            return True
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def run_all_tests():
    """Run all test queries"""
    print("\n" + "="*80)
    print("🧪 TAVILY INTEGRATION TEST SUITE")
    print("="*80)
    
    # Test backend first
    backend_ok = test_direct_backend()
    
    if not backend_ok:
        print("\n⚠️  Skipping middleware tests (backend not available)")
        return
    
    # Test regular endpoint
    print("\n\n" + "="*80)
    print("Testing Regular Tavily Endpoint")
    print("="*80)
    
    success_count = 0
    for test in TEST_QUERIES[:3]:  # Test first 3
        result = test_tavily_search(test["query"], test["category"])
        if result:
            success_count += 1
    
    # Test agricultural endpoint
    print("\n\n" + "="*80)
    print("Testing Agricultural-Optimized Endpoint")
    print("="*80)
    
    agricultural_test = TEST_QUERIES[0]  # Use first query
    result = test_tavily_search(
        agricultural_test["query"], 
        agricultural_test["category"], 
        use_agricultural=True
    )
    if result:
        success_count += 1
    
    # Summary
    print("\n" + "="*80)
    print(f"📈 TEST SUMMARY: {success_count}/{len(TEST_QUERIES[:3])+1} tests passed")
    print("="*80)
    
    if success_count == len(TEST_QUERIES[:3]) + 1:
        print("✅ All tests passed! Tavily integration working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    run_all_tests()

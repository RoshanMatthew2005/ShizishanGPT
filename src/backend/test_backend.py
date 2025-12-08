"""
FastAPI Backend Test Suite
Tests all endpoints to verify functionality
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health():
    """Test health check endpoint"""
    print_section("Testing Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_root():
    """Test root endpoint"""
    print_section("Testing Root Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_ask():
    """Test /api/ask endpoint"""
    print_section("Testing /api/ask (Mini LLM)")
    
    queries = [
        "What is crop rotation?",
        "How to improve soil fertility?",
        "What is NPK fertilizer?"
    ]
    
    for query in queries:
        try:
            print(f"\nQuery: {query}")
            response = requests.post(
                f"{BASE_URL}/api/ask",
                json={"query": query, "mode": "auto"}
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Answer: {data['data']['answer'][:200]}...")
                print(f"Execution time: {data['data'].get('execution_time', 0):.2f}s")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True


def test_rag():
    """Test /api/rag endpoint"""
    print_section("Testing /api/rag (VectorStore)")
    
    queries = [
        "wheat cultivation",
        "rice farming techniques",
        "pest control methods"
    ]
    
    for query in queries:
        try:
            print(f"\nQuery: {query}")
            response = requests.post(
                f"{BASE_URL}/api/rag",
                json={"query": query, "top_k": 3}
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Documents found: {data['data']['num_results']}")
                if data['data']['documents']:
                    print(f"Top document: {data['data']['documents'][0]['content'][:100]}...")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True


def test_predict_yield():
    """Test /api/predict_yield endpoint"""
    print_section("Testing /api/predict_yield (Yield Model)")
    
    test_cases = [
        {
            "crop": "Wheat",
            "season": "Rabi",
            "state": "Punjab",
            "rainfall": 800.0,
            "fertilizer": 120.0,
            "pesticide": 0.5,
            "area": 2.0
        },
        {
            "crop": "Rice",
            "season": "Kharif",
            "state": "West Bengal",
            "rainfall": 1200.0,
            "fertilizer": 150.0,
            "pesticide": 0.8,
            "area": 1.5
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\nTest Case {i}: {test_case['crop']} in {test_case['state']}")
            response = requests.post(
                f"{BASE_URL}/api/predict_yield",
                json=test_case
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Predicted Yield: {data['data']['prediction']:.2f} tonnes/hectare")
                print(f"Total Production: {data['data'].get('total_production', 0):.2f} tonnes")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True


def test_detect_pest():
    """Test /api/detect_pest endpoint"""
    print_section("Testing /api/detect_pest (Pest Model)")
    
    # Look for test images
    image_dirs = [
        Path("Data/images/PlantVillage"),
        Path("Data/images")
    ]
    
    test_image = None
    for image_dir in image_dirs:
        if image_dir.exists():
            for img_file in image_dir.rglob("*.jpg"):
                test_image = img_file
                break
            if test_image:
                break
    
    if not test_image:
        print("⚠️  No test images found, skipping pest detection test")
        return True
    
    try:
        print(f"\nUsing test image: {test_image}")
        
        with open(test_image, "rb") as f:
            files = {"file": (test_image.name, f, "image/jpeg")}
            data = {"top_k": 3}
            
            response = requests.post(
                f"{BASE_URL}/api/detect_pest",
                files=files,
                data=data
            )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Predictions:")
            for pred in data['data']['predictions'][:3]:
                print(f"  - {pred['class']}: {pred['confidence']:.2%}")
            
            if data['data'].get('recommendation'):
                print(f"\nRecommendation: {data['data']['recommendation'][:200]}...")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return True


def test_translate():
    """Test /api/translate endpoint"""
    print_section("Testing /api/translate (Translation)")
    
    test_cases = [
        {"text": "Hello farmer", "source_lang": "en", "target_lang": "hi"},
        {"text": "Good morning", "source_lang": "en", "target_lang": "es"},
        {"text": "Thank you", "source_lang": "en", "target_lang": "fr"}
    ]
    
    for test_case in test_cases:
        try:
            print(f"\nTranslating '{test_case['text']}' "
                  f"({test_case['source_lang']} -> {test_case['target_lang']})")
            
            response = requests.post(
                f"{BASE_URL}/api/translate",
                json=test_case
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Translation: {data['data']['translated_text']}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True


def test_agent():
    """Test /api/agent endpoint"""
    print_section("Testing /api/agent (ReAct Agent)")
    
    queries = [
        "What is the best fertilizer for wheat?",
        "How to control aphids in cotton?",
        "Predict yield for rice in Kerala with 2000mm rainfall"
    ]
    
    for query in queries:
        try:
            print(f"\nQuery: {query}")
            response = requests.post(
                f"{BASE_URL}/api/agent",
                json={
                    "query": query,
                    "mode": "auto",
                    "max_iterations": 5
                }
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Answer: {data['data']['answer'][:200]}...")
                print(f"Tools used: {data['data'].get('tools_used', [])}")
                print(f"Execution time: {data['data'].get('execution_time', 0):.2f}s")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  ShizishanGPT FastAPI Backend - Test Suite")
    print("=" * 60)
    print(f"  Backend URL: {BASE_URL}")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
    except Exception as e:
        print(f"\n❌ Backend server not running at {BASE_URL}")
        print(f"   Error: {e}")
        print(f"\n   Please start the server first:")
        print(f"   python src/backend/main.py")
        return
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Ask LLM", test_ask),
        ("RAG Query", test_rag),
        ("Predict Yield", test_predict_yield),
        ("Detect Pest", test_detect_pest),
        ("Translate", test_translate),
        ("Agent Query", test_agent)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    run_all_tests()

#!/usr/bin/env python3
"""
Quick Test - Tavily Integration
Run this to verify Tavily is working correctly
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env():
    """Check if API key is configured"""
    api_key = os.getenv("TAVILY_API_KEY")
    
    print("=" * 70)
    print("🔍 TAVILY INTEGRATION CHECK")
    print("=" * 70)
    
    if not api_key:
        print("❌ TAVILY_API_KEY not found in .env file")
        print("\n📝 To fix this:")
        print("1. Copy .env.example to .env")
        print("2. Get your API key from https://tavily.com")
        print("3. Add: TAVILY_API_KEY=tvly-xxxxxxxxxx")
        return False
    
    if api_key == "your_tavily_api_key_here":
        print("⚠️  TAVILY_API_KEY is using placeholder value")
        print("\n📝 To fix this:")
        print("1. Get your real API key from https://tavily.com")
        print("2. Replace placeholder in .env file")
        return False
    
    print(f"✅ TAVILY_API_KEY configured: {api_key[:10]}...")
    return True

def test_backend():
    """Test FastAPI backend Tavily endpoint"""
    print("\n" + "=" * 70)
    print("Testing Backend Connection...")
    print("=" * 70)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/tavily_search",
            json={"query": "organic farming techniques", "max_results": 2},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Backend working! Found {result['results_count']} results")
            print(f"   Response time: {result['response_time']}s")
            if result.get('results'):
                print(f"   Top result: {result['results'][0]['title'][:50]}...")
            return True
        else:
            print(f"❌ Backend error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend (http://localhost:8000)")
        print("   Make sure backend is running:")
        print("   python -m uvicorn src.backend.main:app --port 8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_middleware():
    """Test middleware Tavily endpoint"""
    print("\n" + "=" * 70)
    print("Testing Middleware Connection...")
    print("=" * 70)
    
    try:
        response = requests.post(
            "http://localhost:5000/api/tavily_search",
            json={"query": "sustainable agriculture", "max_results": 2},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Middleware working! Found {result['results_count']} results")
            return True
        else:
            print(f"❌ Middleware error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to middleware (http://localhost:5000)")
        print("   Make sure middleware is running:")
        print("   cd middleware && npm start")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all checks"""
    
    # Check environment
    if not check_env():
        print("\n" + "=" * 70)
        print("⚠️  Please configure TAVILY_API_KEY before testing")
        print("=" * 70)
        return
    
    # Test backend
    backend_ok = test_backend()
    
    # Test middleware
    middleware_ok = test_middleware()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Environment: {'✅' if check_env() else '❌'}")
    print(f"Backend:     {'✅' if backend_ok else '❌'}")
    print(f"Middleware:  {'✅' if middleware_ok else '❌'}")
    
    if backend_ok and middleware_ok:
        print("\n🎉 All tests passed! Tavily integration is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Try the full test suite: python test_tavily_integration.py")
        print("   2. Test with agent: Ask questions that need real-time info")
        print("   3. Monitor usage at: https://tavily.com/dashboard")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("=" * 70)

if __name__ == "__main__":
    main()

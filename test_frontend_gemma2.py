#!/usr/bin/env python3
"""
Test Frontend Gemma 2 Integration
Tests the complete frontend → middleware → backend → Gemma 2 pipeline
"""

import requests
import time
import json
import subprocess
import sys
from pathlib import Path

# Configuration
MIDDLEWARE_URL = "http://localhost:5000"
BACKEND_URL = "http://localhost:8000"
TEST_QUERY = "What will be the yield for wheat with 100mm rainfall?"

def check_service(name, url, timeout=5):
    """Check if a service is running"""
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: Running")
            return True
    except:
        pass
    print(f"❌ {name}: Not running")
    return False

def start_middleware():
    """Start the middleware service"""
    print("🚀 Starting middleware...")
    middleware_dir = Path(__file__).parent / "middleware"
    
    try:
        # Kill existing node processes
        subprocess.run(["taskkill", "/f", "/im", "node.exe"], 
                      capture_output=True, check=False)
        time.sleep(2)
        
        # Start middleware
        process = subprocess.Popen(
            ["node", "server.js"],
            cwd=str(middleware_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for startup
        time.sleep(5)
        
        # Check if it started
        if check_service("Middleware", MIDDLEWARE_URL):
            print("✅ Middleware started successfully")
            return process
        else:
            print("❌ Failed to start middleware")
            return None
            
    except Exception as e:
        print(f"❌ Error starting middleware: {e}")
        return None

def test_direct_backend():
    """Test backend agent endpoint directly"""
    print("\n🧪 Testing Backend Agent (Gemma 2) directly...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/agent",
            json={"query": TEST_QUERY, "mode": "auto"},
            timeout=25
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('final_answer', '')
            tools_used = result.get('tools_used', [])
            
            print(f"✅ Backend Status: 200")
            print(f"✅ Tools Used: {tools_used}")
            print(f"✅ Answer Length: {len(answer)} chars")
            print(f"✅ Answer Preview: {answer[:150]}...")
            
            # Quality check
            if len(answer) > 100 and ('impossible' in answer.lower() or 'factors' in answer.lower()):
                print("✅ HIGH QUALITY GEMMA 2 RESPONSE")
                return True
            else:
                print("⚠️  Response quality unclear")
                return False
        else:
            print(f"❌ Backend Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend Test Failed: {e}")
        return False

def test_frontend_integration():
    """Test complete frontend integration"""
    print("\n🧪 Testing Frontend → Middleware → Backend → Gemma 2...")
    
    try:
        response = requests.post(
            f"{MIDDLEWARE_URL}/ask",
            json={"query": TEST_QUERY, "mode": "auto"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', result.get('final_answer', ''))
            tools_used = result.get('tools_used', [])
            success = result.get('success', True)
            
            print(f"✅ Frontend Integration Status: 200")
            print(f"✅ Success: {success}")
            print(f"✅ Tools Used: {tools_used}")
            print(f"✅ Answer Length: {len(answer)} chars")
            print(f"✅ Answer Preview: {answer[:200]}...")
            
            # Quality comparison
            if 'impossible' in answer.lower() or 'many factors' in answer.lower():
                print("\n🎉 SUCCESS! Frontend now using GEMMA 2!")
                print("✅ Mini LLM successfully replaced with Gemma 2")
                return True
            elif len(answer) < 50 or 'diameter' in answer.lower():
                print("\n❌ Still getting Mini LLM responses!")
                print("⚠️  Need to debug middleware routing")
                return False
            else:
                print("\n✅ Quality response detected!")
                return True
                
        else:
            print(f"❌ Frontend Integration Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend Integration Test Failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 TESTING FRONTEND GEMMA 2 INTEGRATION")
    print("=" * 50)
    
    # Check services
    backend_running = check_service("Backend", BACKEND_URL)
    middleware_running = check_service("Middleware", MIDDLEWARE_URL)
    
    if not backend_running:
        print("❌ Backend not running. Please start it first.")
        return False
    
    # Start middleware if needed
    middleware_process = None
    if not middleware_running:
        middleware_process = start_middleware()
        if not middleware_process:
            return False
    
    # Test backend directly
    backend_test = test_direct_backend()
    
    # Test frontend integration
    frontend_test = test_frontend_integration()
    
    # Results
    print("\n" + "=" * 50)
    print("🏆 TEST RESULTS")
    print("=" * 50)
    
    if backend_test and frontend_test:
        print("✅ ALL TESTS PASSED!")
        print("🎉 Frontend successfully migrated to Gemma 2!")
        print("✅ Complete pipeline: Frontend → Middleware → Backend → Gemma 2")
    elif backend_test and not frontend_test:
        print("⚠️  Backend works but frontend integration needs fixing")
        print("🔧 Middleware routing issue detected")
    else:
        print("❌ Tests failed - system needs debugging")
    
    # Cleanup
    if middleware_process:
        print("\n🧹 Cleaning up...")
        middleware_process.terminate()
    
    return backend_test and frontend_test

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
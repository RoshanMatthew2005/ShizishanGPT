"""
Test ReAct agent with Tavily integration
Send actual query through the agent to verify Tavily is called
"""
import requests
import json


MIDDLEWARE_URL = "http://localhost:5000/ask"
BACKEND_URL = "http://localhost:8000/api/agent"


def test_via_middleware():
    """Test through middleware (full stack)"""
    print("\n" + "="*70)
    print("TEST: Full Stack (React → Middleware → Backend → Agent)")
    print("="*70)
    
    query = "What is the best pesticide for whitefly in cotton in 2025?"
    print(f"\n📝 Query: {query}")
    
    try:
        response = requests.post(
            MIDDLEWARE_URL,
            json={"query": query},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success!")
            print(f"\nResponse:")
            print(json.dumps(data, indent=2))
        else:
            print(f"\n❌ Error {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")


def test_via_backend():
    """Test directly via backend"""
    print("\n" + "="*70)
    print("TEST: Backend Direct (Backend → Agent)")
    print("="*70)
    
    query = "What is the best pesticide for whitefly in cotton in 2025?"
    print(f"\n📝 Query: {query}")
    
    try:
        response = requests.post(
            BACKEND_URL,
            json={"query": query, "mode": "react"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success!")
            
            # Extract key information
            print(f"\n📊 Agent Response:")
            print(f"   Status: {data.get('status')}")
            print(f"   Mode: {data.get('mode')}")
            
            if data.get('tools_used'):
                print(f"   Tools Used: {', '.join(data['tools_used'])}")
                
                # Check if Tavily was used
                if 'tavily_search' in data['tools_used']:
                    print(f"   ✅ TAVILY WAS CALLED!")
                else:
                    print(f"   ⚠️  Warning: Tavily was NOT called")
                    print(f"   Tools that were called: {data['tools_used']}")
            
            print(f"\n📝 Final Answer:")
            answer = data.get('final_answer', data.get('answer', 'No answer'))
            print(f"   {answer[:500]}...")
            
            print(f"\n⏱️  Execution Time: {data.get('execution_time', 'N/A')}s")
            
        else:
            print(f"\n❌ Error {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TESTING REACT AGENT WITH TAVILY")
    print("="*70)
    
    # Test backend first (simpler)
    test_via_backend()
    
    # Then test full stack
    # test_via_middleware()
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70 + "\n")

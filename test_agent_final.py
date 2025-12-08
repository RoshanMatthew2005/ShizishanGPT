"""
Test the ReAct agent with Gemma 2 after import fixes
"""
import requests
import json
import time

# Wait for backend to start
print("⏳ Waiting 15 seconds for backend to fully load...")
time.sleep(15)

# Test query
query = "What will be the yield for wheat with 100mm rainfall?"

print(f"\n{'='*70}")
print("TESTING REACT AGENT WITH GEMMA 2")
print(f"{'='*70}")
print(f"Query: {query}")
print(f"{'='*70}\n")

try:
    response = requests.post(
        "http://localhost:8000/api/agent",
        json={"query": query},
        timeout=60
    )
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"📦 Response Size: {len(response.content)} bytes")
    
    result = response.json()
    
    print(f"\n{'='*70}")
    print("RESPONSE DATA")
    print(f"{'='*70}")
    print(json.dumps(result, indent=2))
    print(f"{'='*70}\n")
    
    # Check if it's a proper response
    final_answer = result.get("final_answer", "")
    tools_used = result.get("tools_used", [])
    exec_time = result.get("execution_time", 0)
    
    if final_answer and len(final_answer) > 50:
        print("✅ SUCCESS: Got substantial response from Gemma 2!")
        print(f"   Answer length: {len(final_answer)} characters")
        print(f"   Tools used: {tools_used}")
        print(f"   Execution time: {exec_time:.2f}s")
    else:
        print("❌ FAIL: Response too short or empty")
        print(f"   Answer: {final_answer}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

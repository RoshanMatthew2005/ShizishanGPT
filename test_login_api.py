"""
Quick test to verify superadmin login works via API
"""
import requests
import json

API_URL = "http://localhost:8000"

print("=" * 60)
print("Testing Superadmin Login via FastAPI Backend")
print("=" * 60)

# Test 1: Login with superadmin credentials
print("\n1. Testing login endpoint...")
print(f"   URL: {API_URL}/api/auth/login")
print(f"   Email: admin@shizishangpt.com")
print(f"   Password: Admin@123456")

try:
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json={
            "email": "admin@shizishangpt.com",
            "password": "Admin@123456"
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ LOGIN SUCCESSFUL!")
        data = response.json()
        print(f"\n   Response:")
        print(f"   - Token Type: {data.get('token_type')}")
        print(f"   - Access Token: {data.get('access_token', '')[:50]}...")
        print(f"   - User Email: {data.get('user', {}).get('email')}")
        print(f"   - User Name: {data.get('user', {}).get('full_name')}")
        print(f"   - User Role: {data.get('user', {}).get('role')}")
        
        # Test 2: Verify token works
        token = data.get('access_token')
        print(f"\n2. Testing /api/auth/me endpoint with token...")
        
        me_response = requests.get(
            f"{API_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"   Status Code: {me_response.status_code}")
        
        if me_response.status_code == 200:
            print("   ✅ TOKEN VERIFICATION SUCCESSFUL!")
            me_data = me_response.json()
            print(f"\n   User Info:")
            print(f"   - Email: {me_data.get('email')}")
            print(f"   - Name: {me_data.get('full_name')}")
            print(f"   - Role: {me_data.get('role')}")
        else:
            print(f"   ❌ TOKEN VERIFICATION FAILED")
            print(f"   Error: {me_response.text}")
            
    else:
        print(f"   ❌ LOGIN FAILED")
        print(f"   Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("   ❌ CONNECTION ERROR")
    print("   Make sure the backend is running on http://localhost:8000")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

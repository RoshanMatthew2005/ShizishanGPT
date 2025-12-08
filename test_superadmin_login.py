"""
Test script to verify superadmin account and test login
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from src.backend.services.auth_service import AuthService

def main():
    print("=" * 60)
    print("Testing Superadmin Authentication")
    print("=" * 60)
    
    # Connect to MongoDB
    mongo_client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
    
    try:
        # Test connection
        mongo_client.admin.command('ping')
        print("✓ MongoDB connection successful")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return
    
    # Create auth service
    auth_service = AuthService(mongo_client, "shizishangpt")
    
    # Check if superadmin exists
    db = mongo_client["shizishangpt"]
    users_collection = db["users"]
    
    superadmin = users_collection.find_one({"email": "admin@shizishangpt.com"})
    
    if superadmin:
        print(f"✓ Superadmin account found")
        print(f"  Email: {superadmin['email']}")
        print(f"  Name: {superadmin['full_name']}")
        print(f"  Role: {superadmin['role']}")
        print(f"  Active: {superadmin['is_active']}")
        print(f"  Has password: {bool(superadmin.get('hashed_password'))}")
    else:
        print("✗ Superadmin account NOT found")
        print("Creating superadmin account...")
        # The AuthService constructor should have created it
        superadmin = users_collection.find_one({"email": "admin@shizishangpt.com"})
        if superadmin:
            print("✓ Superadmin created successfully")
        else:
            print("✗ Failed to create superadmin")
            return
    
    print("\n" + "=" * 60)
    print("Testing Login")
    print("=" * 60)
    
    # Test authentication
    email = "admin@shizishangpt.com"
    password = "Admin@123456"
    
    print(f"Attempting login with:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    
    try:
        user = auth_service.authenticate_user(email, password)
        
        if user:
            print("\n✓ Authentication SUCCESSFUL!")
            print(f"  User ID: {user['id']}")
            print(f"  Email: {user['email']}")
            print(f"  Name: {user['full_name']}")
            print(f"  Role: {user['role']}")
            
            # Test token creation
            token = auth_service.create_access_token(
                data={"sub": user["id"], "email": user["email"], "role": user["role"]}
            )
            print(f"\n✓ JWT Token created successfully")
            print(f"  Token: {token[:50]}...")
            
            # Verify token
            payload = auth_service.verify_token(token)
            if payload:
                print(f"\n✓ Token verification successful")
                print(f"  User ID: {payload.get('sub')}")
                print(f"  Email: {payload.get('email')}")
                print(f"  Role: {payload.get('role')}")
            else:
                print(f"\n✗ Token verification failed")
                
        else:
            print("\n✗ Authentication FAILED!")
            print("  Incorrect email or password")
            
    except Exception as e:
        print(f"\n✗ Authentication error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()

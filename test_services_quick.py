"""Quick service test - checks if all services are running"""
import requests
import time

services = {
    "MongoDB": "http://localhost:27017",
    "Backend": "http://localhost:8000/health",
    "Middleware": "http://localhost:5000/health", 
    "Frontend": "http://localhost:3000"
}

print("=" * 60)
print("Service Health Check")
print("=" * 60)

for name, url in services.items():
    try:
        if "27017" in url:
            # MongoDB doesn't have HTTP endpoint, skip
            print(f"{name:15} SKIPPED (MongoDB uses different protocol)")
            continue
            
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            print(f"{name:15} ✓ RUNNING (Status: {response.status_code})")
        else:
            print(f"{name:15} ⚠ RESPONDING (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"{name:15} ✗ NOT ACCESSIBLE")
    except Exception as e:
        print(f"{name:15} ✗ ERROR: {str(e)[:40]}")

print("=" * 60)

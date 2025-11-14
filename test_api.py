"""
Test script for ShizishanGPT API endpoints
"""
import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_yield_prediction():
    """Test the /predict_yield endpoint"""
    print("\n" + "="*70)
    print("TESTING: POST /predict_yield")
    print("="*70)
    
    payload = {
        "crop": "Rice",
        "state": "Punjab",
        "season": "Kharif",
        "rainfall": 820,
        "fertilizer": 180,
        "pesticide": 90,
        "area": 5000
    }
    
    print(f"\nRequest payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(f"{API_BASE_URL}/predict_yield", json=payload)
        response.raise_for_status()
        
        print(f"\nResponse (Status {response.status_code}):")
        print(json.dumps(response.json(), indent=2))
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_weather_analysis():
    """Test the /analyze_weather endpoint"""
    print("\n" + "="*70)
    print("TESTING: POST /analyze_weather")
    print("="*70)
    
    payload = {
        "rainfall": 800,
        "fertilizer": 150,
        "pesticide": 75
    }
    
    print(f"\nRequest payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(f"{API_BASE_URL}/analyze_weather", json=payload)
        response.raise_for_status()
        
        print(f"\nResponse (Status {response.status_code}):")
        print(json.dumps(response.json(), indent=2))
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_root():
    """Test the root endpoint"""
    print("\n" + "="*70)
    print("TESTING: GET /")
    print("="*70)
    
    try:
        response = requests.get(f"{API_BASE_URL}/")
        response.raise_for_status()
        
        print(f"\nResponse (Status {response.status_code}):")
        print(json.dumps(response.json(), indent=2))
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SHIZISHANGPT API TEST SUITE")
    print("="*70)
    
    results = {
        "Root Endpoint": test_root(),
        "Yield Prediction": test_yield_prediction(),
        "Weather Analysis": test_weather_analysis()
    }
    
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:25s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        exit(130)

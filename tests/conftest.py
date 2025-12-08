"""
Pytest configuration and fixtures for ShizishanGPT testing
"""
import pytest
import requests
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Base URLs for testing
REACT_URL = "http://localhost:3000"
MIDDLEWARE_URL = "http://localhost:5000"
BACKEND_URL = "http://localhost:8000"


@pytest.fixture(scope="session")
def check_services():
    """Check if all required services are running"""
    services = {
        "React Frontend": REACT_URL,
        "Node.js Middleware": f"{MIDDLEWARE_URL}/health",
        "FastAPI Backend": f"{BACKEND_URL}/health"
    }
    
    failed_services = []
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                failed_services.append(name)
        except:
            failed_services.append(name)
    
    if failed_services:
        pytest.skip(f"Required services not running: {', '.join(failed_services)}")
    
    return True


@pytest.fixture(scope="session")
def api_client():
    """Returns a configured requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def sample_queries():
    """Sample test queries for various categories"""
    return {
        "rag": [
            "What are NPK fertilizers?",
            "How to do crop rotation?",
            "Best irrigation methods?"
        ],
        "llm": [
            "Explain crop rotation in simple terms",
            "What are the benefits of organic farming?",
            "How does weather affect crops?"
        ],
        "yield": {
            "crop": "wheat",
            "area": 10,
            "rainfall": 800,
            "temperature": 25,
            "humidity": 60
        },
        "weather": {
            "rainfall": 2000,
            "temperature": 35,
            "humidity": 80
        }
    }


@pytest.fixture
def wait_for_response():
    """Helper to wait for async operations"""
    def _wait(max_seconds=10):
        time.sleep(max_seconds)
    return _wait


@pytest.fixture(scope="session")
def performance_thresholds():
    """Performance thresholds for validation"""
    return {
        "llm_response": 5.0,  # seconds
        "rag_retrieval": 4.0,
        "model_inference": 2.0,
        "image_processing": 4.0,
        "translation": 3.0,
        "health_check": 0.5
    }


@pytest.fixture
def test_image_path():
    """Path to test images"""
    return os.path.join(os.path.dirname(__file__), '..', 'Data', 'images', 'PlantVillage')


def pytest_configure(config):
    """Pytest configuration hook"""
    config.addinivalue_line(
        "markers", "requires_services: mark test as requiring all services to be running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add markers automatically based on test file names
    for item in items:
        if "test_e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        elif "test_rag" in item.nodeid:
            item.add_marker(pytest.mark.rag)
        elif "test_llm" in item.nodeid:
            item.add_marker(pytest.mark.llm)
        elif "test_models" in item.nodeid:
            item.add_marker(pytest.mark.models)
        elif "test_agent" in item.nodeid:
            item.add_marker(pytest.mark.agent)
        elif "test_translation" in item.nodeid:
            item.add_marker(pytest.mark.translation)
        elif "test_images" in item.nodeid:
            item.add_marker(pytest.mark.images)
        elif "test_errors" in item.nodeid:
            item.add_marker(pytest.mark.errors)
        elif "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        elif "test_security" in item.nodeid:
            item.add_marker(pytest.mark.security)

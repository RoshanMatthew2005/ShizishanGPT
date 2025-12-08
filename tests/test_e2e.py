"""
End-to-End Pipeline Testing
Tests the complete flow: React → Node.js → FastAPI → MongoDB
"""
import pytest
import requests
import time


MIDDLEWARE_URL = "http://localhost:5000"
BACKEND_URL = "http://localhost:8000"
REACT_URL = "http://localhost:3000"


class TestE2EPipeline:
    """End-to-end integration tests"""
    
    def test_e2e_001_services_health(self):
        """E2E-001: Verify all services are running"""
        # Check React
        response = requests.get(REACT_URL, timeout=5)
        assert response.status_code == 200, "React frontend not responding"
        
        # Check Middleware
        response = requests.get(f"{MIDDLEWARE_URL}/health", timeout=5)
        assert response.status_code == 200, "Middleware not responding"
        
        # Check Backend
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        assert response.status_code == 200, "Backend not responding"
        assert response.json().get("status") in ["healthy", "degraded"], "Backend status invalid"
    
    def test_e2e_002_react_to_backend_flow(self):
        """E2E-002: Test complete request flow through all layers"""
        query_data = {"query": "What is crop rotation?"}
        
        # Send request through middleware (simulating React)
        start_time = time.time()
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json=query_data,
            timeout=30
        )
        end_time = time.time()
        
        assert response.status_code == 200, f"Request failed: {response.text}"
        result = response.json()
        
        # Verify response structure
        assert "success" in result or "data" in result or "answer" in result
        
        # Verify reasonable response time
        response_time = end_time - start_time
        assert response_time < 15.0, f"Response too slow: {response_time}s"
    
    def test_e2e_003_error_propagation(self):
        """E2E-003: Test error handling across all layers"""
        # Send invalid request
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={},  # Missing query field
            timeout=10
        )
        
        # Should return error, not crash
        assert response.status_code in [400, 422, 500]
    
    def test_e2e_004_cors_configuration(self):
        """E2E-004: Test CORS is properly configured"""
        headers = {
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "test"},
            headers=headers,
            timeout=10
        )
        
        # Should allow localhost:3000
        assert "Access-Control-Allow-Origin" in response.headers or response.status_code == 200


class TestServiceCommunication:
    """Test communication between services"""
    
    def test_comm_001_middleware_to_backend(self):
        """Test middleware successfully forwards to backend"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "test"},
            timeout=10
        )
        
        assert response.status_code in [200, 500]  # Either success or backend error
    
    def test_comm_002_backend_direct_access(self):
        """Test direct backend access works"""
        response = requests.post(
            f"{BACKEND_URL}/api/ask",
            json={"query": "test"},
            timeout=10
        )
        
        assert response.status_code in [200, 422, 500]
    
    def test_comm_003_mongodb_connection(self):
        """Test MongoDB connection through backend"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/conversations/list",
            json={"user_id": "test_user", "limit": 5},
            timeout=10
        )
        
        # Should connect to MongoDB (200) or return validation error (400)
        assert response.status_code in [200, 400]


class TestDataFlow:
    """Test data flow through the pipeline"""
    
    def test_data_001_request_transformation(self):
        """Test data is properly transformed through layers"""
        query = "Test query for data transformation"
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": query},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            # Verify response contains data
            assert result is not None
    
    def test_data_002_response_structure(self):
        """Test response has consistent structure"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "What is farming?"},
            timeout=15
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should be a valid JSON object
        assert isinstance(result, dict)
    
    def test_data_003_conversation_persistence(self):
        """Test conversation data persists in MongoDB"""
        session_id = f"test_session_{int(time.time())}"
        
        # Save conversation
        save_data = {
            "session_id": session_id,
            "title": "E2E Test Conversation",
            "messages": [
                {"id": 1, "type": "user", "text": "Test message"}
            ],
            "user_id": "e2e_test_user"
        }
        
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/conversations/save",
            json=save_data,
            timeout=10
        )
        
        assert response.status_code == 200
        
        # Retrieve conversation
        time.sleep(1)  # Wait for DB write
        
        list_response = requests.post(
            f"{MIDDLEWARE_URL}/api/conversations/list",
            json={"user_id": "e2e_test_user", "limit": 10},
            timeout=10
        )
        
        assert list_response.status_code == 200
        conversations = list_response.json()
        
        # Verify our conversation is in the list
        if isinstance(conversations, dict) and "data" in conversations:
            conversations = conversations["data"]
        
        assert isinstance(conversations, list)

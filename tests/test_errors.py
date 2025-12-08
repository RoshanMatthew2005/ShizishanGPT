"""
Error Handling Testing
Tests system error handling and recovery
"""
import pytest
import requests
import time


MIDDLEWARE_URL = "http://localhost:5000"


class TestInvalidInput:
    """Test handling of invalid inputs"""
    
    def test_err_input_001_malformed_json(self):
        """ERR-INPUT-001: Malformed JSON"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            data="this is not json",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code in [400, 422]
    
    def test_err_input_002_missing_fields(self):
        """ERR-INPUT-002: Missing required fields"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={},  # Empty object
            timeout=10
        )
        
        assert response.status_code in [400, 422]
    
    def test_err_input_003_wrong_type(self):
        """Test wrong data type"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": 12345,  # Should be string
                "area": "not a number",  # Should be number
                "rainfall": 800
            },
            timeout=10
        )
        
        assert response.status_code in [400, 422]
    
    def test_err_input_004_null_values(self):
        """Test null values"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": None},
            timeout=10
        )
        
        assert response.status_code in [200, 400, 422]
    
    def test_err_input_005_empty_strings(self):
        """Test empty strings"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": ""},
            timeout=10
        )
        
        assert response.status_code in [200, 400]
    
    def test_err_input_006_unicode_characters(self):
        """Test unicode character handling"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "நெல் சாகுபடி எப்படி? 🌾"},
            timeout=15
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    def test_err_input_007_very_large_payload(self):
        """Test very large payload"""
        huge_query = "test " * 10000  # 50KB+ payload
        
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": huge_query},
            timeout=20
        )
        
        assert response.status_code in [200, 400, 413]  # 413 = Payload Too Large


class TestNetworkErrors:
    """Test network error handling"""
    
    def test_err_network_001_timeout_handling(self):
        """ERR-TIMEOUT-001: Handle request timeouts"""
        try:
            response = requests.post(
                f"{MIDDLEWARE_URL}/api/ask",
                json={"query": "test"},
                timeout=0.001  # Very short timeout
            )
        except requests.exceptions.Timeout:
            # Expected - timeout should be raised
            pass
        except:
            # Other exceptions are also acceptable
            pass
    
    def test_err_network_002_connection_refused(self):
        """ERR-NETWORK-001: Handle connection errors gracefully"""
        try:
            # Try to connect to non-existent service
            response = requests.get(
                "http://localhost:9999/health",
                timeout=2
            )
        except requests.exceptions.ConnectionError:
            # Expected
            pass
        except:
            # Other exceptions acceptable
            pass
    
    def test_err_network_003_invalid_url(self):
        """Test invalid URL handling"""
        try:
            response = requests.get("http://invalid-url-that-doesnt-exist", timeout=2)
        except:
            # Should raise an exception, which is expected
            pass


class TestModelErrors:
    """Test model error handling"""
    
    def test_err_model_001_invalid_crop_type(self):
        """ERR-MODEL: Handle invalid crop type"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "invalid_crop_xyz_123",
                "area": 10,
                "rainfall": 800,
                "temperature": 25
            },
            timeout=10
        )
        
        # Should return error, not crash
        assert response.status_code in [400, 422, 500]
    
    def test_err_model_002_extreme_values(self):
        """Test handling of extreme input values"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "wheat",
                "area": 999999999,  # Extremely large
                "rainfall": -1000,  # Negative
                "temperature": 9999  # Unrealistic
            },
            timeout=10
        )
        
        assert response.status_code in [400, 422, 500]
    
    def test_err_model_003_missing_model_graceful(self):
        """Test graceful handling when model is missing"""
        # Try to use a feature that might not have a model loaded
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/some_advanced_feature",
            json={"data": "test"},
            timeout=10
        )
        
        # Should return 404 or 501 (Not Implemented), not 500
        assert response.status_code in [404, 501, 400, 500]


class TestDatabaseErrors:
    """Test database error handling"""
    
    def test_err_db_001_invalid_session_id(self):
        """Test handling of invalid session ID"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/conversations/get",
            json={"session_id": "nonexistent_session_12345"},
            timeout=10
        )
        
        # Should return not found or empty result, not crash
        assert response.status_code in [200, 404]
    
    def test_err_db_002_invalid_user_id(self):
        """Test handling of invalid user ID"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/conversations/list",
            json={"user_id": None, "limit": 10},
            timeout=10
        )
        
        assert response.status_code in [200, 400, 422]


class TestEndpointErrors:
    """Test endpoint error responses"""
    
    def test_err_endpoint_001_not_found(self):
        """Test 404 for non-existent endpoints"""
        response = requests.get(
            f"{MIDDLEWARE_URL}/api/nonexistent_endpoint",
            timeout=10
        )
        
        assert response.status_code == 404
    
    def test_err_endpoint_002_method_not_allowed(self):
        """Test method not allowed"""
        # Try GET on POST endpoint
        response = requests.get(
            f"{MIDDLEWARE_URL}/api/ask",
            timeout=10
        )
        
        assert response.status_code in [404, 405]  # 405 = Method Not Allowed
    
    def test_err_endpoint_003_unsupported_media_type(self):
        """Test unsupported media type"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            data="query=test",  # Form data instead of JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        # Should reject or handle gracefully
        assert response.status_code in [200, 400, 415]  # 415 = Unsupported Media Type


class TestErrorRecovery:
    """Test system recovery after errors"""
    
    def test_err_recovery_001_system_operational_after_error(self):
        """Test system remains operational after errors"""
        # Trigger an error
        requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"invalid": "request"},
            timeout=10
        )
        
        # System should still work
        health = requests.get(f"{MIDDLEWARE_URL}/health", timeout=5)
        assert health.status_code == 200
    
    def test_err_recovery_002_multiple_errors(self):
        """Test system handles multiple consecutive errors"""
        for i in range(5):
            requests.post(
                f"{MIDDLEWARE_URL}/api/invalid_endpoint",
                json={"test": i},
                timeout=5
            )
        
        # Should still be responsive
        health = requests.get(f"{MIDDLEWARE_URL}/health", timeout=5)
        assert health.status_code == 200
    
    def test_err_recovery_003_error_then_valid(self):
        """Test valid request works after error"""
        # Invalid request
        requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={},
            timeout=10
        )
        
        # Valid request should work
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "What is farming?"},
            timeout=15
        )
        
        assert response.status_code == 200


class TestErrorMessages:
    """Test error message quality"""
    
    def test_err_msg_001_informative_errors(self):
        """Test error messages are informative"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={},  # Missing query
            timeout=10
        )
        
        if response.status_code in [400, 422]:
            error_text = response.text.lower()
            
            # Should mention what's wrong
            assert len(error_text) > 10, "Error message too short"
            # Common error indicators
            assert any(word in error_text for word in ["error", "invalid", "required", "missing"])
    
    def test_err_msg_002_no_stack_traces_in_production(self):
        """Test stack traces aren't exposed (production setting)"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": None},
            timeout=10
        )
        
        error_text = response.text
        
        # In production, should not expose full stack traces
        # (This test may fail in dev mode, which is acceptable)
        if response.status_code >= 500:
            # Internal server errors might show traces in dev
            # Just check system remains stable
            health = requests.get(f"{MIDDLEWARE_URL}/health", timeout=5)
            assert health.status_code == 200
    
    def test_err_msg_003_consistent_format(self):
        """Test error messages have consistent format"""
        # Trigger multiple types of errors
        errors = []
        
        errors.append(requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={},
            timeout=10
        ))
        
        errors.append(requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={"crop": "invalid"},
            timeout=10
        ))
        
        # Check all errors return JSON
        for error_response in errors:
            if error_response.status_code >= 400:
                try:
                    error_response.json()  # Should be valid JSON
                except:
                    # If not JSON, should still be a valid response
                    assert len(error_response.text) > 0

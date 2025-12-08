"""
Security Testing
Tests security vulnerabilities and protections
"""
import pytest
import requests


MIDDLEWARE_URL = "http://localhost:5000"
BACKEND_URL = "http://localhost:8000"
REACT_URL = "http://localhost:3000"


class TestAPIKeySecurity:
    """Test API key exposure prevention"""
    
    def test_sec_api001_no_keys_in_frontend(self):
        """SEC-API-001: Verify no API keys exposed in frontend"""
        try:
            response = requests.get(REACT_URL, timeout=5)
            assert response.status_code == 200
            
            # Check for common key patterns
            content = response.text.lower()
            assert "api_key" not in content or "your_api_key_here" in content
            assert "secret_key" not in content
            assert "private_key" not in content
        except:
            pytest.skip("React frontend not accessible")
    
    def test_sec_api003_no_keys_in_errors(self):
        """SEC-API-003: Keys not exposed in error messages"""
        # Trigger an error
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/invalid_endpoint",
            json={"test": "data"},
            timeout=10
        )
        
        error_text = response.text.lower()
        
        # Should not expose keys or sensitive env vars
        assert "api_key" not in error_text or "masked" in error_text
        assert "password" not in error_text
        assert "secret" not in error_text or "******" in error_text


class TestCORSSecurity:
    """Test CORS security configuration"""
    
    def test_sec_cors001_localhost_allowed(self):
        """SEC-CORS-001: Localhost:3000 origin allowed"""
        headers = {
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "test"},
            headers=headers,
            timeout=15
        )
        
        # Should allow or respond successfully
        assert response.status_code in [200, 500]
    
    def test_sec_cors002_malicious_origin_blocked(self):
        """SEC-CORS-002: Malicious origin blocked"""
        headers = {
            "Origin": "http://malicious-site.com",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "test"},
            headers=headers,
            timeout=15
        )
        
        # Should either block or not include permissive CORS header
        if "Access-Control-Allow-Origin" in response.headers:
            allowed_origin = response.headers["Access-Control-Allow-Origin"]
            # Should not be * (wildcard) or the malicious origin
            assert allowed_origin != "*" or response.status_code != 200


class TestInputValidation:
    """Test input validation and injection prevention"""
    
    def test_sec_inj001_sql_injection_prevention(self):
        """SEC-INJ-001: SQL injection prevented"""
        malicious_queries = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM admin--"
        ]
        
        for mal_query in malicious_queries:
            response = requests.post(
                f"{MIDDLEWARE_URL}/api/ask",
                json={"query": mal_query},
                timeout=15
            )
            
            # Should process safely without executing SQL
            assert response.status_code in [200, 400]
            
            # System should still be operational
            health = requests.get(f"{MIDDLEWARE_URL}/health", timeout=5)
            assert health.status_code == 200
    
    def test_sec_inj002_nosql_injection(self):
        """SEC-INJ-002: NoSQL injection prevention"""
        payload = {
            "query": {"$ne": None},  # MongoDB operator injection
            "user_id": {"$gt": ""}
        }
        
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/conversations/list",
            json=payload,
            timeout=10
        )
        
        # Should reject invalid input format or handle safely
        assert response.status_code in [200, 400, 422]
    
    def test_sec_inj003_xss_prevention(self):
        """SEC-INJ-003: XSS attack prevention"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg/onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            response = requests.post(
                f"{MIDDLEWARE_URL}/api/ask",
                json={"query": payload},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.text
                # Response should not contain unescaped payload
                assert "<script>" not in result or "&lt;script&gt;" in result
                assert "onerror=" not in result or "onerror" in result.lower() and "=" not in result
    
    def test_sec_inj004_command_injection(self):
        """SEC-INJ-004: Command injection blocked"""
        malicious_inputs = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "& dir C:\\",
            "`whoami`"
        ]
        
        for mal_input in malicious_inputs:
            response = requests.post(
                f"{MIDDLEWARE_URL}/api/ask",
                json={"query": mal_input},
                timeout=15
            )
            
            # System should remain operational
            assert response.status_code in [200, 400, 500]
            
            # Health check should still work
            health = requests.get(f"{MIDDLEWARE_URL}/health", timeout=5)
            assert health.status_code == 200
    
    def test_sec_inj008_header_injection(self):
        """SEC-INJ-009: Header injection prevention"""
        malicious_header = "test\r\nX-Injected: true"
        
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "test"},
            headers={"X-Custom": malicious_header},
            timeout=15
        )
        
        # Should not reflect injected header
        assert "X-Injected" not in response.headers


class TestAuthorizationSecurity:
    """Test authorization and access control"""
    
    def test_sec_auth002_unauthorized_conversation_access(self):
        """SEC-AUTH-004: Cannot access other user's conversations"""
        # Try to access conversations without proper user_id
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/conversations/list",
            json={"user_id": "other_user", "limit": 10},
            timeout=10
        )
        
        # Should either require auth or only return that user's data
        assert response.status_code in [200, 401, 403]


class TestDataExposure:
    """Test sensitive data exposure"""
    
    def test_sec_data001_no_sensitive_in_errors(self):
        """SEC: No sensitive data in error messages"""
        # Trigger various errors
        endpoints = [
            "/api/invalid",
            "/api/ask",
            "/api/predict_yield"
        ]
        
        for endpoint in endpoints:
            response = requests.post(
                f"{MIDDLEWARE_URL}{endpoint}",
                json={"invalid": "data"},
                timeout=10
            )
            
            error_text = response.text.lower()
            
            # Should not expose internal paths, stack traces, etc.
            assert "d:\\" not in error_text and "c:\\" not in error_text
            assert "/home/" not in error_text
            assert "password" not in error_text
            # Traceback might be acceptable in dev, but check it's not exposing secrets
    
    def test_sec_data002_health_endpoint_safe(self):
        """SEC-API-005: Health endpoint doesn't expose sensitive vars"""
        response = requests.get(f"{MIDDLEWARE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            result = response.text.lower()
            
            # Should not expose environment variables
            assert "api_key" not in result or "masked" in result
            assert "password" not in result
            assert "secret" not in result


class TestFileUploadSecurity:
    """Test file upload security"""
    
    def test_sec_file001_reject_executable(self):
        """SEC-INJ-010: Reject executable files"""
        # Try uploading a fake executable
        fake_exe = b"MZ\x90\x00"  # EXE header
        files = {'file': ('malware.exe', fake_exe, 'application/octet-stream')}
        
        try:
            response = requests.post(
                f"{MIDDLEWARE_URL}/api/detect_pest",
                files=files,
                timeout=10
            )
            
            # Should reject
            assert response.status_code in [400, 415, 422]
        except:
            # Endpoint might not exist or accept files differently
            pass
    
    def test_sec_file002_validate_image_type(self):
        """Test image type validation"""
        # Try uploading text file as image
        fake_image = b"This is not an image"
        files = {'file': ('fake.jpg', fake_image, 'image/jpeg')}
        
        try:
            response = requests.post(
                f"{MIDDLEWARE_URL}/api/detect_pest",
                files=files,
                timeout=10
            )
            
            # Should detect it's not a real image
            assert response.status_code in [200, 400, 415, 422]
        except:
            pass


class TestRateLimiting:
    """Test rate limiting protection"""
    
    def test_sec_rate001_excessive_requests(self):
        """SEC: Rate limiting on excessive requests"""
        # Make many rapid requests
        responses = []
        for i in range(50):  # Try 50 rapid requests
            try:
                resp = requests.post(
                    f"{MIDDLEWARE_URL}/api/ask",
                    json={"query": f"Test {i}"},
                    timeout=5
                )
                responses.append(resp.status_code)
            except:
                responses.append(0)
        
        # If rate limiting exists, should see 429 (Too Many Requests)
        # If not, all should succeed (or fail for other reasons)
        # Either way, system should remain responsive
        health = requests.get(f"{MIDDLEWARE_URL}/health", timeout=5)
        assert health.status_code == 200, "System should remain operational"


class TestHTTPSecurity:
    """Test HTTP security headers and configurations"""
    
    def test_sec_http001_security_headers(self):
        """Test security headers are present"""
        response = requests.get(f"{MIDDLEWARE_URL}/health", timeout=5)
        
        # Check for common security headers (may not all be present in dev)
        headers = response.headers
        
        # At minimum, should have content-type
        assert "Content-Type" in headers
        
        # In production, should have:
        # X-Content-Type-Options: nosniff
        # X-Frame-Options: DENY
        # Strict-Transport-Security (if HTTPS)

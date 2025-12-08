## 10. Performance Testing

### 10.1 Latency Tests

| Test ID | Endpoint | Expected Latency | Acceptable Range | Test Method |
|---------|----------|------------------|------------------|-------------|
| PERF-L-001 | POST /api/ask (LLM) | < 3s | < 5s | Single query benchmark |
| PERF-L-002 | POST /api/rag | < 2s | < 4s | RAG retrieval time |
| PERF-L-003 | POST /api/predict_yield | < 1s | < 2s | Model inference time |
| PERF-L-004 | POST /api/detect_pest | < 2s | < 4s | Image processing time |
| PERF-L-005 | POST /api/translate | < 1.5s | < 3s | Translation time |
| PERF-L-006 | POST /api/agent | < 5s | < 10s | Agent reasoning time |
| PERF-L-007 | GET /health | < 100ms | < 500ms | Health check speed |
| PERF-L-008 | POST /api/conversations/save | < 500ms | < 1s | MongoDB write |
| PERF-L-009 | POST /api/conversations/list | < 300ms | < 800ms | MongoDB read |
| PERF-L-010 | Frontend page load | < 2s | < 4s | React initial load |

### 10.2 Load Testing

| Test ID | Scenario | Concurrent Users | Expected Behavior | Success Criteria |
|---------|----------|------------------|-------------------|------------------|
| PERF-LOAD-001 | Normal load | 10 | All requests succeed | 100% success rate |
| PERF-LOAD-002 | Medium load | 50 | <5% failure rate | >95% success |
| PERF-LOAD-003 | High load | 100 | <10% failure rate | >90% success |
| PERF-LOAD-004 | Stress test | 200 | System remains responsive | No crashes |
| PERF-LOAD-005 | Spike test | 0→100 in 10s | Graceful scaling | <20% errors |

### 10.3 Memory Usage Tests

| Test ID | Component | Expected Memory | Max Acceptable | Test Duration |
|---------|-----------|-----------------|----------------|---------------|
| PERF-MEM-001 | FastAPI Backend | < 2GB | < 4GB | 1 hour continuous |
| PERF-MEM-002 | Node.js Middleware | < 500MB | < 1GB | 1 hour continuous |
| PERF-MEM-003 | React Frontend | < 200MB | < 500MB | Client-side monitoring |
| PERF-MEM-004 | MongoDB | < 1GB | < 2GB | With 1000 conversations |
| PERF-MEM-005 | LLM Model Loading | < 1.5GB | < 3GB | At startup |
| PERF-MEM-006 | Pest Detection Model | < 500MB | < 1GB | Per inference |
| PERF-MEM-007 | VectorStore | < 1GB | < 2GB | Loaded in memory |
| PERF-MEM-008 | Full System | < 6GB | < 10GB | All services running |

### 10.4 Parallel Query Tests

**Test Configuration: 10 Simultaneous Queries**

| Query ID | Query Text | Expected Tool | Priority |
|----------|-----------|---------------|----------|
| PQ-001 | "What is crop rotation?" | LLM | Normal |
| PQ-002 | "Search docs for NPK info" | RAG | Normal |
| PQ-003 | "Predict wheat yield 10ha" | Yield Model | Normal |
| PQ-004 | "Impact of 2000mm rain" | Weather Model | Normal |
| PQ-005 | "Best monsoon crops" | LLM | Normal |
| PQ-006 | "Find irrigation methods in KB" | RAG | Normal |
| PQ-007 | "Estimate rice output" | Yield Model | Normal |
| PQ-008 | "Effect of 45°C heat" | Weather Model | Normal |
| PQ-009 | "Organic farming benefits" | LLM | Normal |
| PQ-010 | "Retrieve pest control docs" | RAG | Normal |

**Success Criteria:**
- All 10 queries complete within 15 seconds
- No query fails
- Average response time < 6 seconds
- No memory leaks
- No rate limit errors

### 10.5 Performance Test Scripts

```python
"""
Performance Testing Suite
tests/test_performance.py
"""

import pytest
import requests
import time
import statistics
import concurrent.futures
import psutil
import os

class TestPerformance:
    
    BASE_URL = "http://localhost:5000/api"
    
    def test_perf_l001_llm_latency(self):
        """Test LLM response latency"""
        query = {"query": "What is crop rotation?", "mode": "direct"}
        
        # Warm-up request
        requests.post(f"{self.BASE_URL}/ask", json=query)
        
        # Measure latency over 5 requests
        latencies = []
        for _ in range(5):
            start = time.time()
            response = requests.post(f"{self.BASE_URL}/ask", json=query)
            latency = time.time() - start
            latencies.append(latency)
            assert response.status_code == 200
        
        avg_latency = statistics.mean(latencies)
        print(f"Average LLM latency: {avg_latency:.2f}s")
        
        assert avg_latency < 5.0  # Should be under 5 seconds
        assert max(latencies) < 10.0  # No request over 10 seconds
    
    def test_perf_l002_rag_latency(self):
        """Test RAG retrieval latency"""
        query = {"query": "Information about NPK fertilizers", "top_k": 5}
        
        latencies = []
        for _ in range(5):
            start = time.time()
            response = requests.post(f"{self.BASE_URL}/rag", json=query)
            latency = time.time() - start
            latencies.append(latency)
            assert response.status_code == 200
        
        avg_latency = statistics.mean(latencies)
        print(f"Average RAG latency: {avg_latency:.2f}s")
        
        assert avg_latency < 4.0  # Should be under 4 seconds
    
    def test_perf_load001_concurrent_requests(self):
        """Test concurrent request handling"""
        
        def make_request(query_id):
            start = time.time()
            response = requests.post(
                f"{self.BASE_URL}/ask",
                json={"query": f"Test query {query_id}"}
            )
            latency = time.time() - start
            return {
                "id": query_id,
                "status": response.status_code,
                "latency": latency,
                "success": response.status_code == 200
            }
        
        # Execute 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        success_count = sum(1 for r in results if r["success"])
        avg_latency = statistics.mean([r["latency"] for r in results])
        max_latency = max([r["latency"] for r in results])
        
        print(f"Concurrent test: {success_count}/10 succeeded")
        print(f"Average latency: {avg_latency:.2f}s, Max: {max_latency:.2f}s")
        
        # Success criteria
        assert success_count >= 9  # At least 90% success
        assert avg_latency < 15.0  # Average under 15s
        assert max_latency < 30.0  # No request over 30s
    
    def test_perf_mem001_memory_usage(self):
        """Monitor memory usage during operations"""
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform multiple operations
        for i in range(10):
            requests.post(f"{self.BASE_URL}/ask", json={"query": f"Query {i}"})
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory increase: {memory_increase:.2f} MB")
        
        # Memory should not increase dramatically
        assert memory_increase < 100  # Less than 100MB increase
    
    def test_perf_throughput(self):
        """Test system throughput (requests per second)"""
        
        num_requests = 50
        start_time = time.time()
        
        for i in range(num_requests):
            requests.post(f"{self.BASE_URL}/ask", json={"query": "Quick test"})
        
        duration = time.time() - start_time
        throughput = num_requests / duration
        
        print(f"Throughput: {throughput:.2f} requests/second")
        
        # Should handle at least 2 requests per second
        assert throughput >= 2.0
    
    def test_perf_cold_start(self):
        """Test cold start performance (first request after startup)"""
        # This test should be run first after system restart
        
        start = time.time()
        response = requests.post(f"{self.BASE_URL}/ask", json={"query": "Test"})
        cold_start_time = time.time() - start
        
        print(f"Cold start time: {cold_start_time:.2f}s")
        
        # First request may be slower due to model loading
        assert cold_start_time < 30.0  # Should still complete in 30s
    
    def test_perf_database_operations(self):
        """Test MongoDB operation performance"""
        
        # Save conversation
        conv_data = {
            "session_id": f"perf_test_{time.time()}",
            "title": "Performance Test",
            "messages": [{"id": 1, "type": "user", "text": "Test"}],
            "user_id": "test_user"
        }
        
        start = time.time()
        save_response = requests.post(
            f"{self.BASE_URL}/conversations/save",
            json=conv_data
        )
        save_time = time.time() - start
        
        # List conversations
        start = time.time()
        list_response = requests.post(
            f"{self.BASE_URL}/conversations/list",
            json={"user_id": "test_user", "limit": 20}
        )
        list_time = time.time() - start
        
        print(f"Save time: {save_time:.3f}s, List time: {list_time:.3f}s")
        
        assert save_time < 1.0  # Save should be under 1 second
        assert list_time < 0.8  # List should be under 800ms
```

### 10.6 Performance Benchmarking Script

```bash
#!/bin/bash
# performance_benchmark.sh

echo "=== ShizishanGPT Performance Benchmark ==="
echo "Starting benchmark at $(date)"
echo ""

# Check if all services are running
echo "1. Checking service health..."
curl -s http://localhost:3000 > /dev/null && echo "✓ React Frontend running" || echo "✗ React not responding"
curl -s http://localhost:5000/health > /dev/null && echo "✓ Node.js Middleware running" || echo "✗ Middleware not responding"
curl -s http://localhost:8000/health > /dev/null && echo "✓ FastAPI Backend running" || echo "✗ Backend not responding"
echo ""

# Run latency tests
echo "2. Testing endpoint latencies..."
echo "Testing /api/ask..."
time curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is crop rotation?"}' > /dev/null 2>&1

echo "Testing /api/rag..."
time curl -X POST http://localhost:5000/api/rag \
  -H "Content-Type: application/json" \
  -d '{"query": "NPK fertilizers", "top_k": 5}' > /dev/null 2>&1

echo ""

# Run load test
echo "3. Running load test (10 concurrent requests)..."
for i in {1..10}; do
  curl -X POST http://localhost:5000/api/ask \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"Test query $i\"}" > /dev/null 2>&1 &
done
wait
echo "✓ Load test complete"
echo ""

echo "Benchmark completed at $(date)"
```

---

## 11. Security Testing

### 11.1 API Key Exposure Tests

| Test ID | Vulnerability | Test Method | Expected Result |
|---------|--------------|-------------|-----------------|
| SEC-API-001 | API keys in frontend code | Source code inspection | No keys in React bundle |
| SEC-API-002 | Keys in Git history | `git log --all --full-history --source -- **/*.env` | .env files in .gitignore |
| SEC-API-003 | Keys in error messages | Trigger errors, check output | No keys exposed |
| SEC-API-004 | Keys in logs | Check log files | Keys redacted/masked |
| SEC-API-005 | Environment variable leakage | Check `/health` endpoint | No sensitive vars exposed |

### 11.2 Unauthorized Access Tests

| Test ID | Attack Vector | Test Case | Expected Protection |
|---------|--------------|-----------|---------------------|
| SEC-AUTH-001 | Direct backend access | Access FastAPI without middleware | CORS blocks request |
| SEC-AUTH-002 | MongoDB injection | Pass MongoDB operators in queries | Input sanitization |
| SEC-AUTH-003 | Path traversal | `GET ../../../etc/passwd` | Path validation |
| SEC-AUTH-004 | Unauthorized conversation access | Request other user's chats | User ID validation |
| SEC-AUTH-005 | Admin endpoint access | Try `/admin` routes | 404 or authentication required |

### 11.3 CORS Security Tests

| Test ID | Origin | Method | Expected Result |
|---------|--------|--------|-----------------|
| SEC-CORS-001 | http://localhost:3000 | GET/POST | Allowed |
| SEC-CORS-002 | http://malicious-site.com | GET/POST | Blocked |
| SEC-CORS-003 | http://localhost:5000 | GET/POST | Allowed |
| SEC-CORS-004 | Different port (8080) | GET/POST | Blocked |
| SEC-CORS-005 | Null origin | GET/POST | Blocked |

### 11.4 Input Validation Tests

| Test ID | Attack Type | Malicious Input | Expected Handling |
|---------|------------|-----------------|-------------------|
| SEC-INJ-001 | SQL Injection | `' OR '1'='1` | Escaped/sanitized |
| SEC-INJ-002 | NoSQL Injection | `{"$ne": null}` | Type validation |
| SEC-INJ-003 | XSS | `<script>alert(1)</script>` | HTML escaped |
| SEC-INJ-004 | Command Injection | `; rm -rf /` | Shell commands blocked |
| SEC-INJ-005 | Path Traversal | `../../secret.txt` | Path sanitization |
| SEC-INJ-006 | LDAP Injection | `*)(uid=*))(|(uid=*` | Input validation |
| SEC-INJ-007 | XML Injection | `<?xml version="1.0"?><!DOCTYPE>` | XML parsing disabled |
| SEC-INJ-008 | Template Injection | `{{7*7}}` | Template escaping |
| SEC-INJ-009 | Header Injection | `\r\nSet-Cookie: admin=true` | Header validation |
| SEC-INJ-010 | File Upload Malware | Upload .exe as .jpg | File type validation |

### 11.5 Security Test Script

```python
"""
Security Testing Suite
tests/test_security.py
"""

import pytest
import requests

class TestSecurity:
    
    MIDDLEWARE_URL = "http://localhost:5000/api"
    BACKEND_URL = "http://localhost:8000/api"
    
    def test_sec_api001_no_keys_in_frontend(self):
        """Verify no API keys exposed in frontend"""
        # Check React bundle
        response = requests.get("http://localhost:3000")
        assert response.status_code == 200
        
        # Check for common key patterns
        content = response.text.lower()
        assert "api_key" not in content
        assert "secret_key" not in content
        assert "private_key" not in content
    
    def test_sec_auth001_cors_protection(self):
        """Test CORS blocks unauthorized origins"""
        headers = {
            "Origin": "http://malicious-site.com",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.MIDDLEWARE_URL}/ask",
            json={"query": "test"},
            headers=headers
        )
        
        # Should be blocked or not include CORS headers
        assert "Access-Control-Allow-Origin" not in response.headers or \
               response.headers["Access-Control-Allow-Origin"] != "http://malicious-site.com"
    
    def test_sec_inj001_sql_injection_prevention(self):
        """Test SQL injection is prevented"""
        malicious_queries = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM admin--"
        ]
        
        for mal_query in malicious_queries:
            response = requests.post(
                f"{self.MIDDLEWARE_URL}/ask",
                json={"query": mal_query}
            )
            
            # Should process safely without executing SQL
            assert response.status_code in [200, 400]
            
            # System should still be operational
            health = requests.get("http://localhost:5000/health")
            assert health.status_code == 200
    
    def test_sec_inj003_xss_prevention(self):
        """Test XSS attack prevention"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg/onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            response = requests.post(
                f"{self.MIDDLEWARE_URL}/ask",
                json={"query": payload}
            )
            
            if response.status_code == 200:
                result = response.json()
                # Response should not contain raw payload
                if result.get("success"):
                    answer = str(result.get("data", {}))
                    assert "<script>" not in answer
                    assert "onerror=" not in answer
    
    def test_sec_inj002_nosql_injection(self):
        """Test NoSQL injection prevention"""
        payload = {
            "query": {"$ne": None},  # MongoDB operator injection
            "user_id": {"$gt": ""}
        }
        
        response = requests.post(
            f"{self.MIDDLEWARE_URL}/conversations/list",
            json=payload
        )
        
        # Should reject invalid input format
        assert response.status_code == 400
    
    def test_sec_file_upload_validation(self):
        """Test file upload security"""
        # Try uploading a .exe file disguised as .jpg
        fake_image = b"MZ\x90\x00"  # EXE header
        files = {'file': ('malware.jpg', fake_image, 'image/jpeg')}
        
        response = requests.post(
            f"{self.MIDDLEWARE_URL}/detect_pest",
            files=files
        )
        
        # Should reject or detect it's not a real image
        assert response.status_code in [400, 415]  # Bad Request or Unsupported Media Type
    
    def test_sec_rate_limiting(self):
        """Test rate limiting protection"""
        # Make rapid requests
        responses = []
        for i in range(150):  # Exceed rate limit (usually 100 req/15min)
            resp = requests.post(
                f"{self.MIDDLEWARE_URL}/ask",
                json={"query": f"Test {i}"}
            )
            responses.append(resp.status_code)
        
        # Should eventually get rate limited
        assert 429 in responses  # Too Many Requests
    
    def test_sec_header_injection(self):
        """Test header injection prevention"""
        malicious_header = "test\r\nX-Injected: true"
        
        response = requests.post(
            f"{self.MIDDLEWARE_URL}/ask",
            json={"query": "test"},
            headers={"X-Custom": malicious_header}
        )
        
        # Should not reflect injected header
        assert "X-Injected" not in response.headers
    
    def test_sec_sensitive_data_exposure(self):
        """Test no sensitive data in error messages"""
        # Trigger an error
        response = requests.post(
            f"{self.MIDDLEWARE_URL}/invalid_endpoint",
            json={"test": "data"}
        )
        
        error_text = response.text.lower()
        
        # Should not expose internal paths, stack traces, etc.
        assert "/home/" not in error_text
        assert "c:\\" not in error_text
        assert "traceback" not in error_text
        assert "password" not in error_text
```

### 11.6 Security Checklist

**Pre-Deployment Security Audit:**

- [ ] No API keys in source code
- [ ] .env files in .gitignore
- [ ] CORS properly configured
- [ ] Input validation on all endpoints
- [ ] SQL injection protection
- [ ] XSS prevention (HTML escaping)
- [ ] File upload validation
- [ ] Rate limiting enabled
- [ ] HTTPS in production (TLS/SSL)
- [ ] Error messages don't expose internals
- [ ] Dependencies updated (no known vulnerabilities)
- [ ] MongoDB authentication enabled
- [ ] Sensitive logs redacted
- [ ] Security headers (Helmet.js)
- [ ] Content Security Policy configured

---


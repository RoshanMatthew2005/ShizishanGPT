"""
Performance Testing
Tests system performance, latency, and load handling
"""
import pytest
import requests
import time
import concurrent.futures
import statistics


MIDDLEWARE_URL = "http://localhost:5000"
BACKEND_URL = "http://localhost:8000"


class TestLatency:
    """Test endpoint latency"""
    
    def test_perf_l001_llm_latency(self):
        """PERF-L-001: LLM response latency"""
        query = {"query": "What is crop rotation?", "mode": "direct"}
        
        # Warm-up request
        requests.post(f"{MIDDLEWARE_URL}/api/ask", json=query, timeout=20)
        
        # Measure latency over 5 requests
        latencies = []
        for _ in range(5):
            start = time.time()
            response = requests.post(f"{MIDDLEWARE_URL}/api/ask", json=query, timeout=20)
            latency = time.time() - start
            latencies.append(latency)
            assert response.status_code == 200
        
        avg_latency = statistics.mean(latencies)
        print(f"\nAverage LLM latency: {avg_latency:.2f}s")
        
        assert avg_latency < 10.0, f"LLM too slow: {avg_latency:.2f}s (target < 10s)"
        assert max(latencies) < 20.0, f"Max latency too high: {max(latencies):.2f}s"
    
    def test_perf_l002_rag_latency(self):
        """PERF-L-002: RAG retrieval latency"""
        query = {"query": "Information about NPK fertilizers", "top_k": 5}
        
        latencies = []
        for _ in range(5):
            start = time.time()
            response = requests.post(f"{MIDDLEWARE_URL}/api/rag", json=query, timeout=15)
            latency = time.time() - start
            latencies.append(latency)
            assert response.status_code == 200
        
        avg_latency = statistics.mean(latencies)
        print(f"\nAverage RAG latency: {avg_latency:.2f}s")
        
        assert avg_latency < 4.0, f"RAG too slow: {avg_latency:.2f}s (target < 4s)"
    
    def test_perf_l003_yield_model_latency(self):
        """PERF-L-003: Yield model inference latency"""
        query = {
            "crop": "wheat",
            "area": 10,
            "rainfall": 800,
            "temperature": 25
        }
        
        latencies = []
        for _ in range(5):
            start = time.time()
            response = requests.post(f"{MIDDLEWARE_URL}/api/predict_yield", json=query, timeout=10)
            latency = time.time() - start
            latencies.append(latency)
            if response.status_code == 200:
                pass  # Model available
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            print(f"\nAverage Yield model latency: {avg_latency:.2f}s")
            assert avg_latency < 2.0, f"Yield model too slow: {avg_latency:.2f}s (target < 2s)"
    
    def test_perf_l004_health_check_latency(self):
        """PERF-L-007: Health check speed"""
        latencies = []
        for _ in range(10):
            start = time.time()
            response = requests.get(f"{MIDDLEWARE_URL}/health", timeout=5)
            latency = time.time() - start
            latencies.append(latency)
            assert response.status_code == 200
        
        avg_latency = statistics.mean(latencies)
        print(f"\nAverage health check latency: {avg_latency:.3f}s")
        
        assert avg_latency < 0.5, f"Health check too slow: {avg_latency:.3f}s (target < 0.5s)"


class TestLoadTesting:
    """Test system under load"""
    
    def test_perf_load001_concurrent_requests(self):
        """PERF-LOAD-001: 10 concurrent requests"""
        
        def make_request(query_id):
            start = time.time()
            try:
                response = requests.post(
                    f"{MIDDLEWARE_URL}/api/ask",
                    json={"query": f"Test query {query_id}"},
                    timeout=30
                )
                latency = time.time() - start
                return {
                    "id": query_id,
                    "status": response.status_code,
                    "latency": latency,
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "id": query_id,
                    "status": 0,
                    "latency": time.time() - start,
                    "success": False,
                    "error": str(e)
                }
        
        # Execute 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        success_count = sum(1 for r in results if r["success"])
        avg_latency = statistics.mean([r["latency"] for r in results])
        max_latency = max([r["latency"] for r in results])
        
        print(f"\nConcurrent test: {success_count}/10 succeeded")
        print(f"Average latency: {avg_latency:.2f}s, Max: {max_latency:.2f}s")
        
        # Success criteria - at least 70% should succeed (some may timeout under load)
        assert success_count >= 7, f"Too many failures: {success_count}/10"
        assert avg_latency < 30.0, f"Average latency too high: {avg_latency:.2f}s"
    
    def test_perf_load002_sequential_requests(self):
        """Test handling sequential requests"""
        success_count = 0
        latencies = []
        
        for i in range(20):
            start = time.time()
            response = requests.post(
                f"{MIDDLEWARE_URL}/api/ask",
                json={"query": f"Quick test {i}"},
                timeout=15
            )
            latency = time.time() - start
            latencies.append(latency)
            
            if response.status_code == 200:
                success_count += 1
        
        print(f"\nSequential test: {success_count}/20 succeeded")
        print(f"Average latency: {statistics.mean(latencies):.2f}s")
        
        # Most should succeed
        assert success_count >= 15, f"Too many failures: {success_count}/20"


class TestThroughput:
    """Test system throughput"""
    
    def test_perf_throughput_001(self):
        """Test requests per second"""
        num_requests = 20
        start_time = time.time()
        
        success_count = 0
        for i in range(num_requests):
            try:
                response = requests.post(
                    f"{MIDDLEWARE_URL}/api/ask",
                    json={"query": "Quick test"},
                    timeout=10
                )
                if response.status_code == 200:
                    success_count += 1
            except:
                pass
        
        duration = time.time() - start_time
        throughput = success_count / duration
        
        print(f"\nThroughput: {throughput:.2f} successful requests/second")
        print(f"Success rate: {success_count}/{num_requests}")
        
        # Should handle at least 0.5 requests per second
        assert throughput >= 0.5, f"Throughput too low: {throughput:.2f} req/s"


class TestDatabasePerformance:
    """Test database operation performance"""
    
    def test_perf_db_001_save_conversation(self):
        """PERF-L-008: MongoDB write performance"""
        conv_data = {
            "session_id": f"perf_test_{time.time()}",
            "title": "Performance Test",
            "messages": [{"id": 1, "type": "user", "text": "Test"}],
            "user_id": "test_user"
        }
        
        latencies = []
        for _ in range(5):
            start = time.time()
            response = requests.post(
                f"{MIDDLEWARE_URL}/api/conversations/save",
                json=conv_data,
                timeout=10
            )
            latency = time.time() - start
            latencies.append(latency)
        
        avg_latency = statistics.mean(latencies)
        print(f"\nAverage MongoDB write latency: {avg_latency:.3f}s")
        
        assert avg_latency < 1.0, f"DB writes too slow: {avg_latency:.3f}s (target < 1s)"
    
    def test_perf_db_002_list_conversations(self):
        """PERF-L-009: MongoDB read performance"""
        latencies = []
        for _ in range(5):
            start = time.time()
            response = requests.post(
                f"{MIDDLEWARE_URL}/api/conversations/list",
                json={"user_id": "test_user", "limit": 20},
                timeout=10
            )
            latency = time.time() - start
            latencies.append(latency)
        
        avg_latency = statistics.mean(latencies)
        print(f"\nAverage MongoDB read latency: {avg_latency:.3f}s")
        
        assert avg_latency < 0.8, f"DB reads too slow: {avg_latency:.3f}s (target < 0.8s)"


class TestSystemResources:
    """Test system resource usage"""
    
    def test_perf_resource_001_no_memory_leaks(self):
        """Test for memory leaks during repeated operations"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform multiple operations
            for i in range(10):
                requests.post(
                    f"{MIDDLEWARE_URL}/api/ask",
                    json={"query": f"Memory test {i}"},
                    timeout=15
                )
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"\nMemory increase: {memory_increase:.2f} MB")
            
            # Memory should not increase dramatically
            assert memory_increase < 200, f"Possible memory leak: {memory_increase:.2f} MB increase"
        except ImportError:
            pytest.skip("psutil not installed")

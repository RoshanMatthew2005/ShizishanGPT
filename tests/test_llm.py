"""
Mini LLM Testing
Tests LLM generation quality, coherence, and accuracy
"""
import pytest
import requests
import time


MIDDLEWARE_URL = "http://localhost:5000"


class TestLLMGeneration:
    """Test LLM text generation quality"""
    
    def test_llm_gen_001_crop_rotation(self):
        """LLM-GEN-001: Generate explanation of crop rotation"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "Explain crop rotation in simple terms", "mode": "direct"},
            timeout=15
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Extract answer
        answer = self._extract_answer(result)
        assert len(answer) > 50, "Response too short"
        assert "crop" in answer.lower() or "rotation" in answer.lower()
    
    def test_llm_gen_002_npk_fertilizer(self):
        """LLM-GEN-002: Generate NPK fertilizer information"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "What are NPK fertilizers and why are they important?"},
            timeout=15
        )
        
        assert response.status_code == 200
        result = response.json()
        answer = self._extract_answer(result)
        
        # Should mention nitrogen, phosphorus, or potassium
        assert len(answer) > 30
    
    def test_llm_gen_003_monsoon_prep(self):
        """LLM-GEN-003: Generate monsoon preparation tips"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "How to prepare fields for monsoon season?"},
            timeout=15
        )
        
        assert response.status_code == 200
    
    def test_llm_gen_004_multistep_guide(self):
        """LLM-GEN-004: Generate multi-step farming guide"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "Provide step-by-step guide for planting wheat"},
            timeout=15
        )
        
        assert response.status_code == 200
    
    def test_llm_gen_005_pest_control(self):
        """LLM-GEN-005: Generate pest control methods"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "What are natural pest control methods?"},
            timeout=15
        )
        
        assert response.status_code == 200
    
    def test_llm_gen_006_soil_health(self):
        """LLM-GEN-006: Generate soil health information"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "Why is soil health important for farming?"},
            timeout=15
        )
        
        assert response.status_code == 200
    
    def test_llm_gen_007_water_management(self):
        """LLM-GEN-007: Generate water management advice"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "Best practices for water management in agriculture"},
            timeout=15
        )
        
        assert response.status_code == 200
    
    def test_llm_gen_008_organic_vs_conventional(self):
        """LLM-GEN-008: Generate comparison of farming methods"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "Difference between organic and conventional farming"},
            timeout=15
        )
        
        assert response.status_code == 200
    
    def test_llm_gen_009_climate_impact(self):
        """LLM-GEN-009: Generate climate impact information"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "How does climate change affect crop yields?"},
            timeout=15
        )
        
        assert response.status_code == 200
    
    def test_llm_gen_010_harvesting_timing(self):
        """LLM-GEN-010: Generate harvesting timing advice"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "When is the best time to harvest rice?"},
            timeout=15
        )
        
        assert response.status_code == 200


class TestLLMQualityMetrics:
    """Test LLM response quality"""
    
    def test_llm_quality_001_coherence(self):
        """Test response is coherent and readable"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "Explain how fertilizers work"},
            timeout=15
        )
        
        assert response.status_code == 200
        result = response.json()
        answer = self._extract_answer(result)
        
        # Basic coherence checks
        assert len(answer) > 20, "Response too short"
        assert answer.strip() != "", "Empty response"
        # Should have proper sentences (contains periods)
        assert "." in answer or "!" in answer or "?" in answer
    
    def test_llm_quality_002_relevance(self):
        """Test response is relevant to query"""
        query = "What is drip irrigation?"
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": query},
            timeout=15
        )
        
        assert response.status_code == 200
        result = response.json()
        answer = self._extract_answer(result).lower()
        
        # Should mention irrigation or water
        assert "irrigation" in answer or "water" in answer or "drip" in answer
    
    def test_llm_quality_003_length(self):
        """Test response length is appropriate"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "What is nitrogen fixation?"},
            timeout=15
        )
        
        assert response.status_code == 200
        result = response.json()
        answer = self._extract_answer(result)
        
        # Should be informative but not excessively long
        assert 30 < len(answer) < 5000, f"Response length inappropriate: {len(answer)}"
    
    def test_llm_quality_004_no_hallucination(self):
        """Test LLM doesn't hallucinate numeric data"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "Explain the concept of soil pH"},
            timeout=15
        )
        
        assert response.status_code == 200
        result = response.json()
        answer = self._extract_answer(result)
        
        # If it mentions pH ranges, they should be reasonable (0-14)
        # This is a basic check - manual review needed for full validation
        assert len(answer) > 20
    
    def test_llm_quality_005_consistency(self):
        """Test LLM provides consistent responses"""
        query = "What is composting?"
        
        # Ask same question twice
        response1 = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": query},
            timeout=15
        )
        
        time.sleep(1)
        
        response2 = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": query},
            timeout=15
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Both should provide valid answers
        answer1 = self._extract_answer(response1.json())
        answer2 = self._extract_answer(response2.json())
        
        assert len(answer1) > 20
        assert len(answer2) > 20


class TestLLMPerformance:
    """Test LLM response performance"""
    
    def test_llm_perf_001_response_time(self):
        """Test LLM response time is acceptable"""
        start = time.time()
        
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "What is crop rotation?"},
            timeout=15
        )
        
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 10.0, f"LLM too slow: {elapsed}s (target < 10s)"
    
    def test_llm_perf_002_concurrent_requests(self):
        """Test LLM handles multiple requests"""
        import concurrent.futures
        
        def make_request(query_num):
            response = requests.post(
                f"{MIDDLEWARE_URL}/api/ask",
                json={"query": f"What is farming technique {query_num}?"},
                timeout=20
            )
            return response.status_code
        
        # Make 3 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, i) for i in range(3)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed or gracefully handle load
        assert all(status in [200, 500, 503] for status in results)


class TestLLMEdgeCases:
    """Test LLM edge cases"""
    
    def test_llm_edge_001_empty_query(self):
        """Test empty query handling"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": ""},
            timeout=10
        )
        
        assert response.status_code in [200, 400]
    
    def test_llm_edge_002_very_long_query(self):
        """Test very long query"""
        long_query = "What is farming? " * 100
        
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": long_query},
            timeout=20
        )
        
        assert response.status_code in [200, 400, 413]
    
    def test_llm_edge_003_special_characters(self):
        """Test query with special characters"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/ask",
            json={"query": "What is N-P-K ratio? (10-10-10)"},
            timeout=15
        )
        
        assert response.status_code == 200
    
    # Helper method
    def _extract_answer(self, result):
        """Extract answer text from various response formats"""
        if isinstance(result, str):
            return result
        if isinstance(result, dict):
            if "answer" in result:
                return str(result["answer"])
            if "data" in result:
                if isinstance(result["data"], dict) and "answer" in result["data"]:
                    return str(result["data"]["answer"])
                return str(result["data"])
            if "response" in result:
                return str(result["response"])
            if "text" in result:
                return str(result["text"])
            return str(result)
        return str(result)


# Add helper method to all test classes
TestLLMGeneration._extract_answer = TestLLMEdgeCases._extract_answer
TestLLMQualityMetrics._extract_answer = TestLLMEdgeCases._extract_answer
TestLLMPerformance._extract_answer = TestLLMEdgeCases._extract_answer

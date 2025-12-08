"""
RAG Retrieval Testing
Tests knowledge base retrieval accuracy and relevance
"""
import pytest
import requests
import time


MIDDLEWARE_URL = "http://localhost:5000"


class TestRAGRetrieval:
    """Test RAG knowledge base retrieval"""
    
    def test_rag_001_fertilizer_query(self):
        """RAG-001: Search for NPK fertilizer information"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "What are NPK fertilizers?", "top_k": 5},
            timeout=10
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify chunks returned
        if "chunks" in result or "data" in result:
            chunks = result.get("chunks") or result.get("data", [])
            assert len(chunks) > 0, "No chunks retrieved"
            
            # Verify relevance - should mention nitrogen, phosphorus, or potassium
            relevant_terms = ["nitrogen", "phosphorus", "potassium", "npk", "fertilizer"]
            chunks_text = str(chunks).lower()
            assert any(term in chunks_text for term in relevant_terms)
    
    def test_rag_002_crop_rotation(self):
        """RAG-002: Search for crop rotation practices"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "How to do crop rotation?", "top_k": 5},
            timeout=10
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should retrieve relevant info about crop rotation
        result_text = str(result).lower()
        assert "crop" in result_text or "rotation" in result_text
    
    def test_rag_003_pest_management(self):
        """RAG-003: Search for pest management strategies"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "Pest management strategies", "top_k": 5},
            timeout=10
        )
        
        assert response.status_code == 200
        result = response.json()
        
        result_text = str(result).lower()
        assert "pest" in result_text or "control" in result_text or "management" in result_text
    
    def test_rag_004_irrigation(self):
        """RAG-004: Search for irrigation techniques"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "Best irrigation methods", "top_k": 5},
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_rag_005_monsoon_crops(self):
        """RAG-005: Search for monsoon season crops"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "What crops to plant during monsoon?", "top_k": 5},
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_rag_006_soil_health(self):
        """RAG-006: Search for soil health indicators"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "Soil health indicators", "top_k": 5},
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_rag_007_organic_farming(self):
        """RAG-007: Search for organic farming methods"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "Organic farming techniques", "top_k": 5},
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_rag_008_water_conservation(self):
        """RAG-008: Search for water conservation"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "Water conservation in agriculture", "top_k": 5},
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_rag_009_seed_varieties(self):
        """RAG-009: Search for seed varieties"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "Different seed varieties for wheat", "top_k": 5},
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_rag_010_harvesting(self):
        """RAG-010: Search for harvesting best practices"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "Best practices for harvesting crops", "top_k": 5},
            timeout=10
        )
        
        assert response.status_code == 200


class TestRAGEdgeCases:
    """Test RAG edge cases and error handling"""
    
    def test_rag_edge_001_out_of_domain(self):
        """RAG-011: Test out-of-domain query"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "How to build a rocket ship?", "top_k": 5},
            timeout=10
        )
        
        # Should still return response (may be empty or irrelevant)
        assert response.status_code in [200, 404]
    
    def test_rag_edge_002_very_short_query(self):
        """RAG-012: Test very short query"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "NPK", "top_k": 5},
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_rag_edge_003_very_long_query(self):
        """RAG-013: Test very long query"""
        long_query = "What are the best agricultural practices for sustainable farming in tropical regions with high rainfall and humid climate conditions considering soil types and crop rotation methods? " * 5
        
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": long_query, "top_k": 5},
            timeout=10
        )
        
        assert response.status_code in [200, 400, 413]  # 413 = Payload Too Large
    
    def test_rag_edge_004_empty_query(self):
        """RAG-014: Test empty query"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "", "top_k": 5},
            timeout=10
        )
        
        assert response.status_code in [200, 400]
    
    def test_rag_edge_005_missing_query(self):
        """RAG-015: Test missing query field"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"top_k": 5},
            timeout=10
        )
        
        assert response.status_code in [400, 422]


class TestRAGPerformance:
    """Test RAG retrieval performance"""
    
    def test_rag_perf_001_response_time(self):
        """Test RAG retrieval is fast enough"""
        start = time.time()
        
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/rag",
            json={"query": "What are NPK fertilizers?", "top_k": 5},
            timeout=10
        )
        
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 4.0, f"RAG too slow: {elapsed}s (target < 4s)"
    
    def test_rag_perf_002_multiple_queries(self):
        """Test RAG handles multiple consecutive queries"""
        queries = [
            "crop rotation",
            "irrigation methods",
            "soil health",
            "pest control",
            "fertilizers"
        ]
        
        for query in queries:
            response = requests.post(
                f"{MIDDLEWARE_URL}/api/rag",
                json={"query": query, "top_k": 3},
                timeout=10
            )
            assert response.status_code == 200
    
    def test_rag_perf_003_varying_top_k(self):
        """Test RAG with different top_k values"""
        for k in [1, 3, 5, 10]:
            response = requests.post(
                f"{MIDDLEWARE_URL}/api/rag",
                json={"query": "farming techniques", "top_k": k},
                timeout=10
            )
            assert response.status_code == 200

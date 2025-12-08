# ShizishanGPT - Milestone 8: Complete System Testing & Debugging

**Project:** ShizishanGPT - Agricultural AI Assistant  
**Version:** 1.0.0  
**Date:** December 1, 2025  
**Milestone:** 8 - Full System Testing & Quality Assurance

---

## Table of Contents

1. [End-to-End Pipeline Testing](#1-end-to-end-pipeline-testing)
2. [RAG Retrieval Testing](#2-rag-retrieval-testing)
3. [Mini LLM Testing](#3-mini-llm-testing)
4. [Yield Model Testing](#4-yield-model-testing)
5. [Weather Model Testing](#5-weather-model-testing)
6. [ReAct Agent Reasoning Testing](#6-react-agent-reasoning-testing)
7. [Translation Pipeline Testing](#7-translation-pipeline-testing)
8. [Image Handling Testing](#8-image-handling-testing)
9. [Error Handling Testing](#9-error-handling-testing)
10. [Performance Testing](#10-performance-testing)
11. [Security Testing](#11-security-testing)
12. [Test Deliverables](#12-test-deliverables)

---

## 1. End-to-End Pipeline Testing

### 1.1 Pipeline Architecture

```
User (Browser)
    ↓
React Frontend (Port 3000)
    ↓ [HTTP POST /api/*]
Node.js Middleware (Port 5000)
    ↓ [Validation, Logging, Rate Limiting]
FastAPI Backend (Port 8000)
    ↓
ReAct Agent Orchestrator
    ↓ [Tool Selection]
    ├─→ RAG (VectorStore + Retrieval)
    ├─→ Mini LLM (DistilGPT-2)
    ├─→ Yield Model (RandomForest)
    ├─→ Weather Model (LSTM)
    └─→ Pest Detection (ResNet18)
    ↓
Response Generation
    ↓
FastAPI → Node.js → React → User
```

### 1.2 Complete Test Flow

#### Test Case E2E-001: Basic Chat Query
**Steps:**
1. Open React app at http://localhost:3000
2. Enter query: "What are the best crops for monsoon season?"
3. Click Send button
4. Observe response

**Expected Behavior:**
- Frontend displays typing indicator
- Message appears in chat within 3-5 seconds
- Response contains relevant agricultural advice
- No console errors in browser DevTools
- Middleware logs show request/response (check terminal)
- Backend logs show agent reasoning

**Failure Points & Fixes:**

| Failure | Symptom | Fix |
|---------|---------|-----|
| Frontend 404 | "Cannot POST /api/ask" | Check middleware is running on port 5000 |
| CORS Error | "Access blocked by CORS" | Verify middleware CORS config allows localhost:3000 |
| Timeout | Request hangs >30s | Check FastAPI backend is running, check model loading |
| Empty Response | Response is blank | Check LLM service initialization, verify model files exist |
| Connection Refused | "ECONNREFUSED" | Ensure all 3 services (React, Node, FastAPI) are running |

#### Test Case E2E-002: RAG Query
**Steps:**
1. Enter query: "What does the agricultural document say about NPK fertilizers?"
2. Send query
3. Verify RAG is used

**Expected Behavior:**
- Agent selects RAG tool
- Response includes document citations
- Response contains "📚 Sources:" section
- Backend logs show "Using RAG retrieval"

**Validation:**
```javascript
// Check response structure
{
  "success": true,
  "data": {
    "answer": "...",
    "documents": [
      {"content": "...", "metadata": {...}}
    ],
    "tool_used": "rag"
  }
}
```

#### Test Case E2E-003: Model Prediction
**Steps:**
1. Enter query: "Predict yield for wheat with 800mm rainfall in Punjab"
2. Send query
3. Verify yield model is used

**Expected Behavior:**
- Agent selects yield prediction tool
- Response contains numerical prediction
- Response format: "Predicted yield: X tons/hectare"

#### Test Case E2E-004: Image Upload (Pest Detection)
**Steps:**
1. Click attachment button
2. Select a plant disease image (e.g., tomato leaf blight)
3. Type: "What disease is this?"
4. Send

**Expected Behavior:**
- Image preview appears before sending
- Response shows disease classification
- Top 3 predictions with confidence scores
- Recommendation included

**Sample Response:**
```
🔍 Plant Disease Detection Results:

1. Tomato_Late_blight - 97.3% confidence
2. Tomato_Early_blight - 2.1% confidence
3. Tomato_Bacterial_spot - 0.6% confidence

📋 Recommendation:
Apply copper-based fungicide immediately...
```

### 1.3 Pipeline Verification Checklist

- [ ] React UI renders without errors
- [ ] Chat input accepts text
- [ ] File upload works for images
- [ ] Messages display in chat history
- [ ] Typing indicator shows during processing
- [ ] Node.js middleware logs requests
- [ ] FastAPI backend responds within timeout
- [ ] Agent selects appropriate tools
- [ ] RAG retrieves relevant documents
- [ ] LLM generates coherent responses
- [ ] Models return valid predictions
- [ ] Errors display user-friendly messages
- [ ] Conversation saves to MongoDB
- [ ] Previous chats load from sidebar
- [ ] New conversation button works

### 1.4 Integration Points Testing

#### React ↔ Node.js
```javascript
// Test API call
const response = await fetch('http://localhost:5000/api/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: "Test", mode: "auto" })
});

// Expected: 200 OK
// Expected: Valid JSON response
```

#### Node.js ↔ FastAPI
```javascript
// Middleware forwards to backend
const backendResponse = await axios.post(
  'http://localhost:8000/api/ask',
  req.body
);

// Expected: Backend responds in <5s
// Expected: Response has correct structure
```

#### FastAPI ↔ Models
```python
# Check model registry
assert model_registry.has("mini_llm") == True
assert model_registry.has("vectorstore") == True
assert model_registry.has("yield_model") == True

# Expected: All models loaded successfully
```

---

## 2. RAG Retrieval Testing

### 2.1 Test Query Set (20 Queries)

| ID | Query | Expected Chunk Topic | Embedding Check | Relevance Validation |
|----|-------|---------------------|-----------------|---------------------|
| RAG-001 | "How to apply NPK fertilizers?" | Fertilizer application methods | Cosine similarity > 0.7 | Contains "NPK", "nitrogen", "phosphorus" |
| RAG-002 | "Best irrigation techniques for paddy" | Irrigation systems | Similarity > 0.65 | Mentions "water management", "rice" |
| RAG-003 | "Organic pest control methods" | Pest management | Similarity > 0.7 | Contains "neem", "organic", "pesticide alternatives" |
| RAG-004 | "Soil pH management for crops" | Soil science | Similarity > 0.68 | Mentions "pH", "acidity", "lime application" |
| RAG-005 | "Crop rotation benefits" | Sustainable farming | Similarity > 0.72 | Contains "rotation", "soil health", "nutrients" |
| RAG-006 | "Drip irrigation advantages" | Water conservation | Similarity > 0.75 | Mentions "drip", "water efficiency" |
| RAG-007 | "Vermicomposting process" | Organic farming | Similarity > 0.7 | Contains "earthworms", "compost", "organic matter" |
| RAG-008 | "Monsoon crop selection" | Seasonal farming | Similarity > 0.68 | Mentions "kharif", "rain-fed", "monsoon crops" |
| RAG-009 | "Mulching techniques" | Soil management | Similarity > 0.7 | Contains "mulch", "soil moisture", "weed control" |
| RAG-010 | "Integrated pest management" | IPM strategies | Similarity > 0.73 | Mentions "IPM", "biological control", "monitoring" |
| RAG-011 | "Greenhouse farming basics" | Protected cultivation | Similarity > 0.68 | Contains "greenhouse", "controlled environment" |
| RAG-012 | "Cover crop benefits" | Soil health | Similarity > 0.7 | Mentions "green manure", "nitrogen fixation" |
| RAG-013 | "Precision agriculture tools" | Modern farming tech | Similarity > 0.65 | Contains "sensors", "GPS", "data-driven" |
| RAG-014 | "Post-harvest loss prevention" | Storage techniques | Similarity > 0.7 | Mentions "storage", "drying", "preservation" |
| RAG-015 | "Hydroponics system setup" | Soilless cultivation | Similarity > 0.72 | Contains "nutrient solution", "hydroponic" |
| RAG-016 | "Companion planting guide" | Intercropping | Similarity > 0.68 | Mentions specific plant combinations |
| RAG-017 | "Soil erosion prevention" | Conservation practices | Similarity > 0.7 | Contains "terracing", "contour farming" |
| RAG-018 | "Biofertilizer application" | Biological inputs | Similarity > 0.7 | Mentions "rhizobium", "azotobacter", "beneficial microbes" |
| RAG-019 | "Water quality for irrigation" | Irrigation water | Similarity > 0.68 | Contains "salinity", "EC", "water testing" |
| RAG-020 | "Seed treatment methods" | Seed technology | Similarity > 0.7 | Mentions "seed priming", "fungicide treatment" |

### 2.2 RAG Validation Test Script

```python
"""
RAG Retrieval Validation Test
tests/test_rag_retrieval.py
"""

import pytest
from src.services.rag_service import rag_service

class TestRAGRetrieval:
    
    def test_rag_001_npk_fertilizers(self):
        """Test NPK fertilizer query retrieval"""
        query = "How to apply NPK fertilizers?"
        result = rag_service.query(query, top_k=3)
        
        # Validate structure
        assert "documents" in result
        assert len(result["documents"]) > 0
        
        # Check relevance
        top_doc = result["documents"][0]
        assert "score" in top_doc
        assert top_doc["score"] > 0.7  # Minimum similarity
        
        # Check content keywords
        content = top_doc["content"].lower()
        assert any(kw in content for kw in ["npk", "nitrogen", "phosphorus", "fertilizer"])
    
    def test_rag_embedding_quality(self):
        """Test embedding generation consistency"""
        query = "Organic pest control"
        
        # Generate embedding twice
        emb1 = rag_service.generate_embedding(query)
        emb2 = rag_service.generate_embedding(query)
        
        # Should be identical
        import numpy as np
        assert np.allclose(emb1, emb2, rtol=1e-5)
    
    def test_rag_top_k_parameter(self):
        """Test top_k parameter works correctly"""
        query = "Irrigation methods"
        
        for k in [1, 3, 5, 10]:
            result = rag_service.query(query, top_k=k)
            assert len(result["documents"]) == k
    
    def test_rag_no_results(self):
        """Test behavior with irrelevant query"""
        query = "quantum physics and blockchain"
        result = rag_service.query(query, top_k=3)
        
        # Should still return docs but with low scores
        assert len(result["documents"]) > 0
        assert result["documents"][0]["score"] < 0.5
```

### 2.3 Embedding Quality Checks

**Test Embedding Dimensions:**
```python
def test_embedding_dimensions():
    embedding = rag_service.generate_embedding("test query")
    assert len(embedding) == 384  # sentence-transformers default
    assert all(isinstance(x, float) for x in embedding)
```

**Test Embedding Normalization:**
```python
def test_embedding_normalized():
    embedding = rag_service.generate_embedding("test")
    import numpy as np
    norm = np.linalg.norm(embedding)
    assert 0.9 < norm < 1.1  # Should be approximately unit length
```

### 2.4 Relevance Validation Metrics

**Cosine Similarity Threshold:**
- Excellent: > 0.8
- Good: 0.7 - 0.8
- Acceptable: 0.6 - 0.7
- Poor: < 0.6

**Keyword Overlap:**
```python
def calculate_keyword_overlap(query, retrieved_doc):
    query_keywords = set(query.lower().split())
    doc_keywords = set(retrieved_doc.lower().split())
    overlap = len(query_keywords & doc_keywords)
    return overlap / len(query_keywords)

# Expected: > 30% overlap for relevant docs
```

---


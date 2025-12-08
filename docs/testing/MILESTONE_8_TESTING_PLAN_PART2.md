## 3. Mini LLM Testing

### 3.1 Domain-Specific Generation Tests (10 Tests)

| ID | Prompt | Expected Output Characteristics | Quality Criteria |
|----|--------|-------------------------------|------------------|
| LLM-G-001 | "Explain nitrogen cycle in soil" | 2-3 sentences, mentions bacteria, conversion process | Contains: nitrogen, bacteria, nitrate, ammonia |
| LLM-G-002 | "Describe drip irrigation benefits" | Lists 3-4 advantages, water conservation focus | Coherent sentences, mentions water efficiency |
| LLM-G-003 | "What is crop rotation?" | Definition + example crops | Mentions alternating crops, soil health |
| LLM-G-004 | "How does mulching work?" | Explains process and benefits | Contains: soil moisture, temperature, weeds |
| LLM-G-005 | "Define integrated pest management" | IPM concept with methods | Mentions biological, cultural, chemical control |
| LLM-G-006 | "Explain vermicomposting" | Process description with earthworms | Contains: worms, organic matter, compost |
| LLM-G-007 | "What is precision agriculture?" | Technology-based farming definition | Mentions: sensors, data, GPS, efficiency |
| LLM-G-008 | "Describe companion planting" | Beneficial plant combinations | Examples of crop pairs, mutual benefits |
| LLM-G-009 | "What are biofertilizers?" | Biological fertilizer definition | Mentions: microorganisms, nitrogen fixation |
| LLM-G-010 | "Explain soil pH importance" | pH impact on nutrient availability | Contains: acidity, nutrients, crop growth |

### 3.2 Summarization Tests (10 Tests)

**Test Format:** Provide long text → Expect concise summary

| ID | Input Text (Sample) | Expected Summary Length | Key Points to Preserve |
|----|---------------------|------------------------|------------------------|
| LLM-S-001 | 500-word NPK fertilizer guide | 2-3 sentences | N-P-K ratios, application timing |
| LLM-S-002 | Detailed irrigation methods article | 2-3 sentences | Main irrigation types, advantages |
| LLM-S-003 | Pest control strategies document | 2-3 sentences | Control methods, safety |
| LLM-S-004 | Soil preparation guidelines | 2-3 sentences | Key steps, tools needed |
| LLM-S-005 | Organic farming principles text | 2-3 sentences | Core principles, practices |
| LLM-S-006 | Crop disease management guide | 2-3 sentences | Disease types, prevention |
| LLM-S-007 | Water conservation techniques | 2-3 sentences | Main techniques, benefits |
| LLM-S-008 | Seed selection criteria article | 2-3 sentences | Selection factors, quality indicators |
| LLM-S-009 | Post-harvest handling procedures | 2-3 sentences | Critical steps, storage |
| LLM-S-010 | Greenhouse management guide | 2-3 sentences | Temperature, humidity control |

### 3.3 Q&A Tests (10 Tests)

| ID | Question | Expected Answer Pattern | Validation Method |
|----|----------|------------------------|-------------------|
| LLM-QA-001 | "What crops grow in monsoon?" | List of kharif crops | Check for: rice, maize, cotton, soybean |
| LLM-QA-002 | "Why is crop rotation important?" | Benefits explanation | Mentions: soil health, pest control, nutrients |
| LLM-QA-003 | "How often to water tomato plants?" | Frequency guidance | Contains: 2-3 times/week, soil moisture |
| LLM-QA-004 | "What causes yellowing leaves?" | Possible causes list | Mentions: nitrogen deficiency, overwatering |
| LLM-QA-005 | "Best time to plant wheat?" | Seasonal timing | Contains: October-November, rabi season |
| LLM-QA-006 | "How to prevent soil erosion?" | Prevention methods | Mentions: terracing, cover crops, mulching |
| LLM-QA-007 | "What is farmyard manure?" | Definition and use | Contains: organic, animal waste, nutrients |
| LLM-QA-008 | "How to test soil pH?" | Testing methods | Mentions: pH meter, test kit, lab testing |
| LLM-QA-009 | "What is green manuring?" | Explanation of practice | Contains: cover crops, plowed under, nitrogen |
| LLM-QA-010 | "Benefits of organic farming?" | List of advantages | Mentions: health, environment, sustainability |

### 3.4 Quality Measurement Framework

#### 3.4.1 Automated Quality Metrics

```python
"""
Mini LLM Quality Metrics
tests/test_llm_quality.py
"""

import re
from typing import Dict
from transformers import pipeline

class LLMQualityTester:
    
    def __init__(self):
        self.sentiment = pipeline("sentiment-analysis")
    
    def measure_coherence(self, text: str) -> float:
        """
        Measure text coherence (0-1)
        Checks for complete sentences, proper grammar
        """
        sentences = text.split('.')
        complete_sentences = sum(1 for s in sentences if len(s.strip().split()) > 3)
        score = complete_sentences / max(len(sentences), 1)
        return min(score, 1.0)
    
    def measure_relevance(self, query: str, response: str, keywords: list) -> float:
        """
        Measure relevance based on keyword presence
        """
        response_lower = response.lower()
        keyword_count = sum(1 for kw in keywords if kw.lower() in response_lower)
        return keyword_count / len(keywords)
    
    def measure_length_appropriateness(self, text: str, min_words: int = 20, max_words: int = 150) -> bool:
        """
        Check if response length is appropriate
        """
        word_count = len(text.split())
        return min_words <= word_count <= max_words
    
    def detect_repetition(self, text: str) -> bool:
        """
        Detect excessive repetition (hallucination indicator)
        """
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        unique_sentences = set(sentences)
        repetition_ratio = len(sentences) / max(len(unique_sentences), 1)
        return repetition_ratio > 1.5  # True if too much repetition
    
    def check_factual_consistency(self, text: str) -> Dict:
        """
        Basic factual consistency checks
        """
        issues = []
        
        # Check for contradictions
        if "always" in text.lower() and "never" in text.lower():
            issues.append("Potential contradiction detected")
        
        # Check for vague language
        vague_words = ["maybe", "possibly", "might be", "could be"]
        vague_count = sum(1 for word in vague_words if word in text.lower())
        if vague_count > 2:
            issues.append("Too much uncertainty")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues
        }
    
    def comprehensive_quality_check(self, query: str, response: str, expected_keywords: list) -> Dict:
        """
        Complete quality assessment
        """
        return {
            "coherence_score": self.measure_coherence(response),
            "relevance_score": self.measure_relevance(query, response, expected_keywords),
            "length_appropriate": self.measure_length_appropriateness(response),
            "has_repetition": self.detect_repetition(response),
            "factual_check": self.check_factual_consistency(response),
            "word_count": len(response.split()),
            "sentence_count": len([s for s in response.split('.') if s.strip()])
        }

# Usage Example
tester = LLMQualityTester()
query = "What is crop rotation?"
response = llm_service.generate(query)
quality = tester.comprehensive_quality_check(
    query, 
    response, 
    expected_keywords=["crops", "soil", "rotation", "nutrients"]
)

# Assert quality thresholds
assert quality["coherence_score"] > 0.7
assert quality["relevance_score"] > 0.5
assert quality["length_appropriate"] == True
assert quality["has_repetition"] == False
```

#### 3.4.2 Hallucination Detection

**Red Flags for Hallucinations:**

1. **Numeric Hallucinations**
```python
def detect_numeric_hallucinations(text: str) -> bool:
    """
    Check for unrealistic numbers
    """
    # Extract all numbers
    numbers = re.findall(r'\d+', text)
    
    # Check for suspicious patterns
    for num in numbers:
        val = int(num)
        # Unrealistic yield (>100 tons/hectare)
        if "yield" in text.lower() and val > 100:
            return True
        # Unrealistic rainfall (>5000mm)
        if "rain" in text.lower() and val > 5000:
            return True
    
    return False
```

2. **Factual Inconsistencies**
```python
def check_agricultural_facts(text: str) -> list:
    """
    Verify agricultural facts
    """
    errors = []
    
    # Check crop seasons
    if "wheat" in text.lower() and "kharif" in text.lower():
        errors.append("Wheat is rabi, not kharif crop")
    
    if "rice" in text.lower() and "rabi" in text.lower():
        errors.append("Rice is kharif, not rabi crop")
    
    # Check temperature ranges
    if re.search(r'temperature.*200', text):
        errors.append("Unrealistic temperature value")
    
    return errors
```

3. **Contradiction Detection**
```python
def detect_contradictions(text: str) -> bool:
    """
    Find self-contradicting statements
    """
    sentences = text.split('.')
    
    # Look for opposite statements
    contradictory_pairs = [
        ("increase", "decrease"),
        ("beneficial", "harmful"),
        ("always", "never"),
        ("required", "not needed")
    ]
    
    for sent1 in sentences:
        for sent2 in sentences:
            if sent1 != sent2:
                for pair in contradictory_pairs:
                    if pair[0] in sent1.lower() and pair[1] in sent2.lower():
                        # Check if referring to same subject
                        words1 = set(sent1.lower().split())
                        words2 = set(sent2.lower().split())
                        overlap = words1 & words2
                        if len(overlap) > 2:  # Same subject
                            return True
    
    return False
```

### 3.5 LLM Test Execution Script

```python
"""
Complete LLM Testing Script
tests/test_mini_llm_comprehensive.py
"""

import pytest
from src.services.llm_service import llm_service

class TestMiniLLM:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize LLM service"""
        llm_service.initialize()
        self.quality_tester = LLMQualityTester()
    
    # Domain-Specific Generation Tests
    def test_llm_g001_nitrogen_cycle(self):
        response = llm_service.generate("Explain nitrogen cycle in soil")
        quality = self.quality_tester.comprehensive_quality_check(
            "nitrogen cycle",
            response,
            ["nitrogen", "bacteria", "soil", "conversion"]
        )
        assert quality["relevance_score"] > 0.5
        assert not quality["has_repetition"]
    
    def test_llm_g002_drip_irrigation(self):
        response = llm_service.generate("Describe drip irrigation benefits")
        assert "water" in response.lower()
        assert len(response.split()) >= 20  # Minimum response length
        assert not self.quality_tester.detect_repetition(response)
    
    # Summarization Tests
    def test_llm_s001_npk_summarization(self):
        long_text = """
        NPK fertilizers contain nitrogen, phosphorus, and potassium...
        [500 words of detailed content]
        """
        summary = llm_service.summarize(long_text, max_length=50)
        assert len(summary.split()) < 60  # Should be concise
        assert any(kw in summary.lower() for kw in ["npk", "nitrogen", "fertilizer"])
    
    # Q&A Tests
    def test_llm_qa001_monsoon_crops(self):
        response = llm_service.answer("What crops grow in monsoon?")
        monsoon_crops = ["rice", "maize", "cotton", "soybean", "millet"]
        found_crops = sum(1 for crop in monsoon_crops if crop in response.lower())
        assert found_crops >= 2  # Should mention at least 2 crops
    
    # Hallucination Detection
    def test_llm_no_hallucinations(self):
        response = llm_service.generate("What is the typical wheat yield?")
        assert not detect_numeric_hallucinations(response)
        assert not detect_contradictions(response)
        assert len(check_agricultural_facts(response)) == 0
    
    # Response Quality
    def test_llm_response_completeness(self):
        response = llm_service.generate("What is crop rotation?")
        assert len(response) > 50  # Not too short
        assert len(response) < 500  # Not too long
        assert response.endswith('.')  # Complete sentences
    
    # Consistency Test
    def test_llm_consistency(self):
        """Same query should give similar responses"""
        query = "Benefits of organic farming"
        response1 = llm_service.generate(query)
        response2 = llm_service.generate(query)
        
        # Responses should overlap in keywords
        words1 = set(response1.lower().split())
        words2 = set(response2.lower().split())
        overlap = len(words1 & words2) / len(words1 | words2)
        assert overlap > 0.3  # At least 30% similarity
```

---


## 6. ReAct Agent Reasoning Testing

### 6.1 Tool Selection Test Cases (30 Prompts)

| Test ID | User Query | Expected Tool | Reasoning | Validation Method |
|---------|-----------|---------------|-----------|-------------------|
| RA-001 | "What does the agricultural document say about NPK?" | RAG | Document retrieval needed | Check `tool_used: "rag"` in response |
| RA-002 | "Explain crop rotation" | Mini LLM | General knowledge question | Check `tool_used: "llm"` |
| RA-003 | "Predict yield for wheat, 10ha, 600mm rain" | Yield Model | Numerical prediction needed | Check `tool_used: "yield_prediction"` |
| RA-004 | "How will 2000mm rainfall affect rice?" | Weather Model | Weather impact analysis | Check `tool_used: "weather_analysis"` |
| RA-005 | "Find information about organic farming in docs" | RAG | Explicit document search | Check RAG tool selected |
| RA-006 | "What is mulching?" | Mini LLM | Definition request | Check LLM tool selected |
| RA-007 | "Estimate cotton production for 15ha with 700mm rain" | Yield Model | Yield calculation needed | Check yield model selected |
| RA-008 | "Impact of 45°C temperature on crops" | Weather Model | Temperature impact query | Check weather model selected |
| RA-009 | "Search knowledge base for pest control" | RAG | Knowledge base query | Check RAG selected |
| RA-010 | "Describe drip irrigation" | Mini LLM | Explanation needed | Check LLM selected |
| RA-011 | "How much maize will 8 hectares produce?" | Yield Model | Production estimate | Check yield model selected |
| RA-012 | "Effect of drought on wheat" | Weather Model | Weather condition impact | Check weather model selected |
| RA-013 | "What do documents say about soil pH?" | RAG | Document-specific query | Check RAG selected |
| RA-014 | "Define integrated pest management" | Mini LLM | Definition | Check LLM selected |
| RA-015 | "Yield prediction: sugarcane, 5ha, 1500mm rainfall" | Yield Model | Explicit prediction request | Check yield model selected |
| RA-016 | "How does high humidity affect tomatoes?" | Weather Model | Humidity impact | Check weather model selected |
| RA-017 | "Retrieve PDF information on biofertilizers" | RAG | Document retrieval | Check RAG selected |
| RA-018 | "What are the benefits of vermicomposting?" | Mini LLM | Benefits listing | Check LLM selected |
| RA-019 | "Calculate rice yield for 20ha, 1200mm rain, 28°C" | Yield Model | Calculation needed | Check yield model selected |
| RA-020 | "Analyze weather: 35°C, 200mm rain, 40% humidity" | Weather Model | Weather analysis | Check weather model selected |
| RA-021 | "Find document sections about fertilizers" | RAG | Section search | Check RAG selected |
| RA-022 | "Explain nitrogen cycle" | Mini LLM | Process explanation | Check LLM selected |
| RA-023 | "Expected potato yield, 3ha, 650mm rainfall" | Yield Model | Yield expectation | Check yield model selected |
| RA-024 | "Will 90% humidity cause problems?" | Weather Model | Humidity assessment | Check weather model selected |
| RA-025 | "What information is in PDFs about irrigation?" | RAG | PDF content query | Check RAG selected |
| RA-026 | "How does composting work?" | Mini LLM | Process description | Check LLM selected |
| RA-027 | "Forecast soybean output: 10ha, 750mm rain" | Yield Model | Output forecast | Check yield model selected |
| RA-028 | "Is 100mm rainfall sufficient for crops?" | Weather Model | Rainfall sufficiency | Check weather model selected |
| RA-029 | "Search knowledge base for crop rotation" | RAG | Explicit KB search | Check RAG selected |
| RA-030 | "What is precision agriculture?" | Mini LLM | Concept definition | Check LLM selected |

### 6.2 Multi-Step Reasoning Tests

| Test ID | Complex Query | Expected Tool Chain | Reasoning Steps |
|---------|---------------|--------------------|-----------------| 
| RA-M-001 | "Find organic farming docs and explain benefits" | RAG → LLM | 1. Retrieve docs 2. Summarize |
| RA-M-002 | "Predict wheat yield and assess weather impact" | Yield Model → Weather Model | 1. Calculate yield 2. Analyze weather |
| RA-M-003 | "Search for irrigation methods and predict water needs" | RAG → Yield Model | 1. Get irrigation info 2. Calculate requirements |
| RA-M-004 | "Explain crop rotation from docs and recommend crops" | RAG → LLM | 1. Retrieve rotation info 2. Generate recommendations |
| RA-M-005 | "Analyze rainfall data and suggest suitable crops" | Weather Model → Mini LLM | 1. Assess rainfall 2. Suggest crops |

### 6.3 Reasoning Verification Methods

#### 6.3.1 Tool Selection Accuracy

```python
"""
ReAct Agent Tool Selection Validation
tests/test_react_agent.py
"""

import pytest
import requests

class TestReActAgent:
    
    BASE_URL = "http://localhost:5000/api"
    
    def test_ra001_rag_selection(self):
        """Verify RAG tool selection for document queries"""
        payload = {
            "query": "What does the agricultural document say about NPK?",
            "mode": "auto"
        }
        
        response = requests.post(f"{self.BASE_URL}/agent", json=payload)
        data = response.json()
        
        assert data["success"] == True
        # Check tool used
        assert "tool_used" in data["data"] or "tools_used" in data["data"]
        tools = data["data"].get("tool_used") or data["data"].get("tools_used", [])
        assert "rag" in str(tools).lower()
    
    def test_ra002_llm_selection(self):
        """Verify LLM tool selection for general questions"""
        payload = {
            "query": "Explain crop rotation",
            "mode": "auto"
        }
        
        response = requests.post(f"{self.BASE_URL}/agent", json=payload)
        data = response.json()
        
        assert data["success"] == True
        tools = data["data"].get("tool_used") or data["data"].get("tools_used", [])
        assert "llm" in str(tools).lower() or "generate" in str(tools).lower()
    
    def test_ra003_yield_model_selection(self):
        """Verify yield model selection for predictions"""
        payload = {
            "query": "Predict yield for wheat, 10ha, 600mm rain",
            "mode": "auto"
        }
        
        response = requests.post(f"{self.BASE_URL}/agent", json=payload)
        data = response.json()
        
        tools = data["data"].get("tool_used") or data["data"].get("tools_used", [])
        assert "yield" in str(tools).lower()
    
    def test_ra004_weather_model_selection(self):
        """Verify weather model selection for weather queries"""
        payload = {
            "query": "How will 2000mm rainfall affect rice?",
            "mode": "auto"
        }
        
        response = requests.post(f"{self.BASE_URL}/agent", json=payload)
        data = response.json()
        
        tools = data["data"].get("tool_used") or data["data"].get("tools_used", [])
        assert "weather" in str(tools).lower()
    
    def test_reasoning_transparency(self):
        """Verify agent provides reasoning trace"""
        payload = {
            "query": "What does the document say about irrigation?",
            "mode": "auto"
        }
        
        response = requests.post(f"{self.BASE_URL}/agent", json=payload)
        data = response.json()
        
        # Should include reasoning steps
        assert "reasoning" in data["data"] or "thought" in data["data"] or "steps" in data["data"]
    
    def test_multi_tool_reasoning(self):
        """Test queries requiring multiple tools"""
        payload = {
            "query": "Find irrigation methods in docs and predict water needs for 10ha wheat",
            "mode": "auto"
        }
        
        response = requests.post(f"{self.BASE_URL}/agent", json=payload)
        data = response.json()
        
        # Should use multiple tools
        tools_used = data["data"].get("tools_used", [])
        assert len(tools_used) >= 2 or "rag" in str(tools_used).lower() and "yield" in str(tools_used).lower()
```

#### 6.3.2 Reasoning Quality Metrics

```python
"""
Reasoning Quality Assessment
"""

class ReasoningValidator:
    
    def validate_tool_choice(self, query: str, tool_used: str) -> dict:
        """
        Validate if the chosen tool is appropriate
        """
        query_lower = query.lower()
        
        # Define tool triggers
        rag_triggers = ["document", "pdf", "knowledge base", "retrieve", "search for"]
        llm_triggers = ["explain", "what is", "describe", "define", "how does"]
        yield_triggers = ["predict yield", "production", "estimate", "forecast", "how much"]
        weather_triggers = ["weather", "rainfall", "temperature", "humidity", "impact of"]
        
        expected_tool = None
        if any(trigger in query_lower for trigger in rag_triggers):
            expected_tool = "rag"
        elif any(trigger in query_lower for trigger in yield_triggers):
            expected_tool = "yield"
        elif any(trigger in query_lower for trigger in weather_triggers):
            expected_tool = "weather"
        elif any(trigger in query_lower for trigger in llm_triggers):
            expected_tool = "llm"
        
        is_correct = expected_tool and expected_tool in tool_used.lower()
        
        return {
            "query": query,
            "expected_tool": expected_tool,
            "actual_tool": tool_used,
            "is_correct": is_correct,
            "confidence": 1.0 if is_correct else 0.0
        }
    
    def evaluate_reasoning_steps(self, reasoning_trace: list) -> dict:
        """
        Evaluate quality of reasoning steps
        """
        if not reasoning_trace:
            return {"valid": False, "reason": "No reasoning trace provided"}
        
        # Check for thought → action → observation pattern
        has_thought = any("thought" in str(step).lower() for step in reasoning_trace)
        has_action = any("action" in str(step).lower() for step in reasoning_trace)
        has_observation = any("observation" in str(step).lower() or "result" in str(step).lower() for step in reasoning_trace)
        
        valid = has_thought and has_action
        
        return {
            "valid": valid,
            "has_thought": has_thought,
            "has_action": has_action,
            "has_observation": has_observation,
            "step_count": len(reasoning_trace),
            "quality_score": sum([has_thought, has_action, has_observation]) / 3.0
        }
```

### 6.4 Agent Performance Benchmarks

| Metric | Target | Acceptance Threshold |
|--------|--------|---------------------|
| Tool Selection Accuracy | > 90% | > 80% |
| Average Response Time | < 5 seconds | < 10 seconds |
| Reasoning Step Count | 2-5 steps | 1-8 steps |
| Multi-tool Success Rate | > 85% | > 70% |
| Error Recovery Rate | > 95% | > 90% |

---

## 7. Translation Pipeline Testing

### 7.1 Tamil Test Queries (10 Tests)

| Test ID | Tamil Query | English Translation | Expected Behavior |
|---------|-------------|---------------------|-------------------|
| TR-TA-001 | "நெல் சாகுபடி குறித்த தகவல்" | "Information about rice cultivation" | Translate → Process → Translate back Tamil |
| TR-TA-002 | "NPK உரத்தை எவ்வாறு பயன்படுத்துவது?" | "How to use NPK fertilizer?" | Correct translation, relevant answer |
| TR-TA-003 | "மழைக்காலத்தில் வளரும் பயிர்கள் எவை?" | "What crops grow in monsoon?" | List crops in Tamil |
| TR-TA-004 | "கரிம விவசாயம் என்றால் என்ன?" | "What is organic farming?" | Definition in Tamil |
| TR-TA-005 | "சொட்டு நீர்ப்பாசன முறை" | "Drip irrigation method" | Explain method in Tamil |
| TR-TA-006 | "மண் pH அளவை எப்படி சோதிப்பது?" | "How to test soil pH?" | Testing steps in Tamil |
| TR-TA-007 | "பயிர் சுழற்சியின் நன்மைகள்" | "Benefits of crop rotation" | Benefits list in Tamil |
| TR-TA-008 | "கோடை பயிர்கள் பட்டியல்" | "List of summer crops" | Crop names in Tamil |
| TR-TA-009 | "இயற்கை பூச்சி கட்டுப்பாடு முறைகள்" | "Natural pest control methods" | Methods in Tamil |
| TR-TA-010 | "கோதுமை விளைச்சல் மதிப்பீடு 10 ஹெக்டருக்கு" | "Wheat yield estimate for 10 hectares" | Numerical result in Tamil |

### 7.2 Hindi Test Queries (10 Tests)

| Test ID | Hindi Query | English Translation | Expected Behavior |
|---------|-------------|---------------------|-------------------|
| TR-HI-001 | "धान की खेती के बारे में जानकारी" | "Information about rice farming" | Translate → Process → Hindi response |
| TR-HI-002 | "NPK उर्वरक कैसे डालें?" | "How to apply NPK fertilizer?" | Application guide in Hindi |
| TR-HI-003 | "मानसून में कौन सी फसलें उगती हैं?" | "Which crops grow in monsoon?" | Crop list in Hindi |
| TR-HI-004 | "जैविक खेती क्या है?" | "What is organic farming?" | Definition in Hindi |
| TR-HI-005 | "ड्रिप सिंचाई के फायदे" | "Benefits of drip irrigation" | Benefits in Hindi |
| TR-HI-006 | "मिट्टी का pH कैसे जांचें?" | "How to check soil pH?" | Testing method in Hindi |
| TR-HI-007 | "फसल चक्र के लाभ" | "Benefits of crop rotation" | Benefits list in Hindi |
| TR-HI-008 | "गर्मी की फसलें कौन सी हैं?" | "What are summer crops?" | Crop names in Hindi |
| TR-HI-009 | "प्राकृतिक कीट नियंत्रण विधियां" | "Natural pest control methods" | Methods in Hindi |
| TR-HI-010 | "10 हेक्टेयर के लिए गेहूं की उपज का अनुमान" | "Wheat yield estimate for 10 hectares" | Yield prediction in Hindi |

### 7.3 Telugu Test Queries (10 Tests)

| Test ID | Telugu Query | English Translation | Expected Behavior |
|---------|-------------|---------------------|-------------------|
| TR-TE-001 | "వరి సాగు గురించి సమాచారం" | "Information about rice cultivation" | Translate → Process → Telugu response |
| TR-TE-002 | "NPK ఎరువులు ఎలా వాడాలి?" | "How to use NPK fertilizers?" | Usage guide in Telugu |
| TR-TE-003 | "వర్షాకాలంలో ఏ పంటలు పండుతాయి?" | "Which crops grow in rainy season?" | Crop list in Telugu |
| TR-TE-004 | "సేంద్రీయ వ్యవసాయం అంటే ఏమిటి?" | "What is organic farming?" | Definition in Telugu |
| TR-TE-005 | "డ్రిప్ నీటిపారుదల ప్రయోజనాలు" | "Benefits of drip irrigation" | Benefits in Telugu |
| TR-TE-006 | "నేల pH ఎలా పరీక్షించాలి?" | "How to test soil pH?" | Testing steps in Telugu |
| TR-TE-007 | "పంట మార్పిడి లాభాలు" | "Crop rotation benefits" | Benefits in Telugu |
| TR-TE-008 | "వేసవి పంటల జాబితా" | "List of summer crops" | Crop names in Telugu |
| TR-TE-009 | "సహజ చీడ నియంత్రణ పద్ధతులు" | "Natural pest control methods" | Methods in Telugu |
| TR-TE-010 | "10 హెక్టార్లకు గోధుమ దిగుబడి అంచనా" | "Wheat yield estimate for 10 hectares" | Yield in Telugu |

### 7.4 Translation Validation Framework

```python
"""
Translation Pipeline Testing
tests/test_translation.py
"""

import pytest
import requests
from deep_translator import GoogleTranslator

class TestTranslation:
    
    BASE_URL = "http://localhost:5000/api"
    
    def test_tr_ta001_tamil_rice_cultivation(self):
        """Test Tamil query translation and response"""
        payload = {
            "query": "நெல் சாகுபடி குறித்த தகவல்",
            "source_lang": "ta",
            "target_lang": "en"
        }
        
        # Step 1: Translate query to English
        translate_response = requests.post(f"{self.BASE_URL}/translate", json=payload)
        translated = translate_response.json()
        
        assert "rice" in translated["data"]["translated_text"].lower()
        
        # Step 2: Process in English
        english_query = translated["data"]["translated_text"]
        agent_response = requests.post(f"{self.BASE_URL}/ask", json={"query": english_query})
        answer = agent_response.json()["data"]["answer"]
        
        # Step 3: Translate back to Tamil
        back_translate_payload = {
            "text": answer,
            "source_lang": "en",
            "target_lang": "ta"
        }
        final_response = requests.post(f"{self.BASE_URL}/translate", json=back_translate_payload)
        tamil_answer = final_response.json()["data"]["translated_text"]
        
        # Validation
        assert len(tamil_answer) > 0
        assert tamil_answer != answer  # Should be in Tamil
    
    def test_semantic_preservation(self):
        """Test if meaning is preserved after translation"""
        original_en = "What crops grow in monsoon season?"
        
        # Translate to Hindi
        to_hindi = GoogleTranslator(source='en', target='hi').translate(original_en)
        
        # Translate back to English
        back_to_en = GoogleTranslator(source='hi', target='en').translate(to_hindi)
        
        # Check semantic similarity
        original_words = set(original_en.lower().split())
        back_words = set(back_to_en.lower().split())
        overlap = len(original_words & back_words) / len(original_words)
        
        assert overlap > 0.5  # At least 50% word overlap
    
    def test_multilingual_consistency(self):
        """Test same query in multiple languages gives consistent answer"""
        queries = {
            "en": "What is crop rotation?",
            "hi": "फसल चक्र क्या है?",
            "ta": "பயிர் சுழற்சி என்றால் என்ன?"
        }
        
        answers = {}
        for lang, query in queries.items():
            # Translate to English if needed
            if lang != "en":
                translated = GoogleTranslator(source=lang, target='en').translate(query)
            else:
                translated = query
            
            # Get answer
            response = requests.post(f"{self.BASE_URL}/ask", json={"query": translated})
            answers[lang] = response.json()["data"]["answer"]
        
        # All answers should contain similar keywords
        keywords = ["rotation", "crops", "soil"]
        for answer in answers.values():
            assert any(kw in answer.lower() for kw in keywords)
```

### 7.5 Semantic Accuracy Validation

**Method 1: Keyword Preservation**
```python
def validate_keyword_preservation(original, translated_back):
    """Check if key agricultural terms are preserved"""
    agri_terms = ["crop", "soil", "fertilizer", "yield", "irrigation", "pest", "seed"]
    
    preserved = 0
    for term in agri_terms:
        if term in original.lower() and term in translated_back.lower():
            preserved += 1
    
    return preserved / len([t for t in agri_terms if t in original.lower()])
```

**Method 2: BLEU Score**
```python
from nltk.translate.bleu_score import sentence_bleu

def calculate_translation_quality(original, translated_back):
    """Calculate BLEU score for translation quality"""
    reference = [original.lower().split()]
    candidate = translated_back.lower().split()
    score = sentence_bleu(reference, candidate)
    return score  # > 0.5 is acceptable
```

---


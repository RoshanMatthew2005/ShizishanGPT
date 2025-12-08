"""
Tool Router
Intelligent router that selects the appropriate tool based on query analysis.
"""
from typing import Dict, Any, List, Optional, Tuple
import re
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.orchestration.tool_registry import get_registry


class ToolRouter:
    """Routes queries to the most appropriate tool based on content analysis."""
    
    def __init__(self):
        """Initialize the tool router."""
        self.registry = get_registry()
        
        # Routing rules (priority order)
        self.routing_rules = [
            # Tavily Search (HIGHEST PRIORITY for real-time info)
            {
                "name": "tavily_search",
                "patterns": [
                    r"\b(best|recommend|top|which|what).*(pesticide|fungicide|insecticide|herbicide|fertilizer|chemical)\b",
                    r"\b(where|buy|purchase|get|available|supplier|market)\b",
                    r"\b(price|cost|rate|cheap|expensive)\b",
                    r"\b(latest|current|new|2024|2025)\b",
                    r"\b(subsidy|scheme|government|policy)\b",
                    r"\b(how to|treat|cure|control).*(disease|pest|infestation)\b"
                ],
                "keywords": ["pesticide", "fungicide", "insecticide", "best", "recommended", 
                           "where", "buy", "price", "latest", "subsidy", "scheme",
                           "2024", "2025", "current", "new", "available", "treatment",
                           "chemical", "fertilizer", "herbicide", "product", "brand"],
                "priority": 1  # Highest priority
            },
            
            # Image-based queries
            {
                "name": "pest_detection",
                "patterns": [r"\bimage\b", r"\bphoto\b", r"\bpicture\b", r"\.jpg", r"\.png", r"\.jpeg"],
                "keywords": ["image", "photo", "picture", "leaf", "show"],
                "priority": 2
            },
            
            # Yield prediction
            {
                "name": "yield_prediction",
                "patterns": [r"\byield\b", r"\bproduction\b", r"\bharvest\b", r"\btonnes\b"],
                "keywords": ["yield", "production", "harvest", "predict", "crop output"],
                "requires_params": True,
                "priority": 3
            },
            
            # Weather realtime (current conditions)
            {
                "name": "weather_realtime",
                "patterns": [r"\b(weather|temperature|rain|forecast).*(today|now|current)\b", 
                           r"\b(current|today).*(weather|temperature|rain)\b"],
                "keywords": ["weather today", "current weather", "forecast", "temperature today", 
                           "rain today", "soil moisture", "humidity now"],
                "priority": 3
            },
            
            # Weather prediction (impacts)
            {
                "name": "weather_prediction",
                "patterns": [r"\bweather\b", r"\brainfall\b", r"\btemperature\b", r"\bclimate\b", r"\bdrought\b", r"\bflood\b"],
                "keywords": ["weather", "rainfall", "temperature", "climate", "drought", "flood", "season"],
                "priority": 4
            },
            
            # Translation
            {
                "name": "translation",
                "patterns": [r"\btranslate\b", r"\bhindi\b", r"\bspanish\b", r"\bfrench\b", r"\blanguage\b"],
                "keywords": ["translate", "language", "hindi", "spanish", "french", "chinese"],
                "priority": 4
            },
            
            # RAG retrieval (general knowledge - LOWER PRIORITY than Tavily)
            {
                "name": "rag_retrieval",
                "patterns": [r"\bwhat is\b", r"\bexplain\b", r"\bdescribe\b"],
                "keywords": ["what is", "explain", "describe", "define", "concept", "theory"],
                "min_length": 30,
                "priority": 5  # Lower than Tavily
            },
            
            # LLM generation (fallback)
            {
                "name": "llm_generation",
                "patterns": [r"\btell me\b", r"\bsummarize\b"],
                "keywords": ["tell me", "summarize", "explain briefly"],
                "max_length": 100,
                "priority": 6  # Lowest priority
            }
        ]
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze query characteristics.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with query analysis
        """
        query_lower = query.lower()
        
        analysis = {
            "length": len(query),
            "word_count": len(query.split()),
            "is_question": any(q in query_lower for q in ["what", "how", "why", "when", "which", "where"]),
            "has_numbers": bool(re.search(r'\d+', query)),
            "is_image_path": any(ext in query_lower for ext in ['.jpg', '.jpeg', '.png', '.bmp']),
            "detected_keywords": []
        }
        
        # Detect keywords from all tools
        for tool_name, metadata in self.registry.get_all_metadata().items():
            for keyword in metadata['keywords']:
                if keyword.lower() in query_lower:
                    analysis["detected_keywords"].append((tool_name, keyword))
        
        return analysis
    
    def route(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route a query to the most appropriate tool.
        
        Args:
            query: User query
            context: Optional context (e.g., previous conversation, user preferences)
            
        Returns:
            Dictionary with routing decision
        """
        try:
            if not query or not query.strip():
                return {
                    "success": False,
                    "error": "Query cannot be empty"
                }
            
            query_lower = query.lower()
            analysis = self.analyze_query(query)
            
            # Score each tool based on routing rules
            scores = {}
            reasons = {}
            
            for rule in self.routing_rules:
                tool_name = rule["name"]
                score = 0
                matched_reasons = []
                
                # Check pattern matches
                for pattern in rule.get("patterns", []):
                    if re.search(pattern, query_lower):
                        score += 3
                        matched_reasons.append(f"matched pattern: {pattern}")
                
                # Check keyword matches
                for keyword in rule.get("keywords", []):
                    if keyword.lower() in query_lower:
                        score += 2
                        matched_reasons.append(f"matched keyword: {keyword}")
                
                # Check length constraints
                if "min_length" in rule and analysis["length"] >= rule["min_length"]:
                    score += 1
                    matched_reasons.append(f"meets min length")
                
                if "max_length" in rule and analysis["length"] <= rule["max_length"]:
                    score += 1
                    matched_reasons.append(f"within max length")
                
                # Check if tool requires parameters (lower score if no params detected)
                if rule.get("requires_params") and not analysis["has_numbers"]:
                    score -= 2
                
                # Apply priority (lower number = higher priority)
                score = score / rule["priority"]
                
                if score > 0:
                    scores[tool_name] = score
                    reasons[tool_name] = matched_reasons
            
            # Select best tool
            if scores:
                best_tool = max(scores, key=scores.get)
                best_score = scores[best_tool]
                
                return {
                    "success": True,
                    "selected_tool": best_tool,
                    "confidence": min(best_score / 5.0, 1.0),  # Normalize to 0-1
                    "score": best_score,
                    "reasoning": reasons[best_tool],
                    "alternatives": {
                        name: score for name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[1:4]
                    },
                    "query_analysis": analysis
                }
            else:
                # Default to RAG for general queries
                return {
                    "success": True,
                    "selected_tool": "rag_retrieval",
                    "confidence": 0.5,
                    "score": 1.0,
                    "reasoning": ["default routing to RAG for general query"],
                    "alternatives": {},
                    "query_analysis": analysis
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Routing failed: {str(e)}"
            }
    
    def route_with_fallback(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Route query with automatic fallback.
        
        Args:
            query: User query
            
        Returns:
            (tool_name, routing_info)
        """
        routing_result = self.route(query)
        
        if routing_result["success"]:
            return routing_result["selected_tool"], routing_result
        else:
            # Fallback to RAG
            return "rag_retrieval", {
                "success": True,
                "selected_tool": "rag_retrieval",
                "confidence": 0.3,
                "reasoning": ["fallback routing"],
                "original_error": routing_result.get("error")
            }
    
    def explain_routing(self, query: str) -> str:
        """
        Get human-readable explanation of routing decision.
        
        Args:
            query: User query
            
        Returns:
            Explanation string
        """
        result = self.route(query)
        
        if not result["success"]:
            return f"❌ Routing failed: {result['error']}"
        
        explanation = f"🎯 Selected Tool: {result['selected_tool']}\n"
        explanation += f"📊 Confidence: {result['confidence']:.0%}\n"
        explanation += f"💡 Reasoning:\n"
        for reason in result["reasoning"]:
            explanation += f"   • {reason}\n"
        
        if result["alternatives"]:
            explanation += f"\n🔄 Alternative tools considered:\n"
            for tool, score in list(result["alternatives"].items())[:3]:
                explanation += f"   • {tool} (score: {score:.2f})\n"
        
        return explanation


# Example usage
if __name__ == "__main__":
    router = ToolRouter()
    
    # Test queries
    test_queries = [
        "What fertilizers should be used for rice?",
        "Predict yield for wheat with 800mm rainfall",
        "Analyze this leaf image: data/leaf.jpg",
        "What is the weather impact on corn?",
        "Translate this to Hindi: Rice is important",
        "How to control pests in tomatoes?"
    ]
    
    print("\n" + "="*70)
    print("TOOL ROUTER TEST")
    print("="*70)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 70)
        result = router.route(query)
        if result["success"]:
            print(f"Selected: {result['selected_tool']}")
            print(f"Confidence: {result['confidence']:.0%}")
            print(f"Reasons: {', '.join(result['reasoning'][:2])}")
        else:
            print(f"Error: {result['error']}")
    
    print("\n" + "="*70)

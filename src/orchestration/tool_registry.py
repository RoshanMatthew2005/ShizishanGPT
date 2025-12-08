"""
Tool Registry
Central registry for all available tools in the system.
"""
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.model_tools.yield_tool import YieldTool
from src.model_tools.pest_tool import PestTool
from src.model_tools.weather_tool import WeatherTool
from src.model_tools.translation_tool import TranslationTool
from src.model_tools.tavily_tool import TavilyTool
from src.orchestration.rag_engine import RAGEngine
from src.orchestration.llm_engine import LLMEngine
from src.orchestration.tools.weather_realtime_tool import weather_realtime_sync, TOOL_METADATA


class ToolRegistry:
    """Registry that manages all available tools and engines."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self.tools = {}
        self.tool_metadata = {}
        self._initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize and register all tools.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print("="*70)
            print("INITIALIZING TOOL REGISTRY")
            print("="*70)
            
            # Register prediction tools
            self._register_tool(
                name="yield_prediction",
                tool=YieldTool(),
                description="Predicts crop yield based on agricultural parameters (crop type, rainfall, fertilizer, etc.)",
                category="prediction",
                input_type="structured",
                keywords=["yield", "prediction", "crop production", "harvest", "tonnes"]
            )
            
            self._register_tool(
                name="pest_detection",
                tool=PestTool(),
                description="Detects plant diseases and pests from leaf images",
                category="prediction",
                input_type="image",
                keywords=["pest", "disease", "plant health", "leaf", "infection", "image"]
            )
            
            self._register_tool(
                name="weather_prediction",
                tool=WeatherTool(),
                description="Predicts weather patterns and impacts on agriculture",
                category="prediction",
                input_type="structured",
                keywords=["weather", "temperature", "rainfall", "climate", "drought", "flood"]
            )
            
            # Register translation tool
            self._register_tool(
                name="translation",
                tool=TranslationTool(),
                description="Translates agricultural content between languages",
                category="utility",
                input_type="text",
                keywords=["translate", "language", "hindi", "spanish", "french"]
            )
            
            # Register weather realtime tool
            self._register_tool(
                name="weather_realtime",
                tool=weather_realtime_sync,
                description="Fetches real-time weather data and forecast for Indian agricultural regions with current conditions and multi-day forecasts",
                category="prediction",
                input_type="structured",
                keywords=["weather", "current weather", "forecast", "temperature today", "rain today", "soil moisture", "humidity", "wind"]
            )
            
            # Register Tavily search tool (HIGHEST PRIORITY for real-time web info)
            self._register_tool(
                name="tavily_search",
                tool=TavilyTool(),
                description="Search the web for real-time agricultural information: pesticide recommendations, fertilizer info, government schemes, product availability, chemical names, treatment protocols, pricing, market data, latest research",
                category="search",
                input_type="text",
                keywords=["pesticide", "fungicide", "insecticide", "herbicide", "fertilizer", "chemical", 
                         "best", "recommended", "top", "which", "what to use", "suggest",
                         "latest", "current", "new", "recent", "2024", "2025", "now", "today",
                         "where", "buy", "purchase", "available", "get", "supplier", "store",
                         "price", "cost", "rate", "market",
                         "subsidy", "scheme", "government", "policy", "support",
                         "treat", "cure", "control", "manage", "prevent", "solution",
                         "brand", "company", "manufacturer", "product"]
            )
            
            # Register RAG engine
            self._register_tool(
                name="rag_retrieval",
                tool=RAGEngine(),
                description="Retrieves relevant agricultural knowledge from document database",
                category="knowledge",
                input_type="text",
                keywords=["retrieve", "search", "knowledge", "document", "information"]
            )
            
            # Register LLM engine
            self._register_tool(
                name="llm_generation",
                tool=LLMEngine(),
                description="Generates agricultural text and answers questions using fine-tuned language model",
                category="generation",
                input_type="text",
                keywords=["generate", "explain", "answer", "what is", "describe"]
            )
            
            self._initialized = True
            
            print(f"\n✓ Successfully registered {len(self.tools)} tools")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing tool registry: {e}")
            return False
    
    def _register_tool(self, 
                       name: str, 
                       tool: Any, 
                       description: str,
                       category: str,
                       input_type: str,
                       keywords: List[str]) -> None:
        """
        Register a tool with metadata.
        
        Args:
            name: Unique tool name
            tool: Tool instance
            description: Tool description
            category: Tool category (prediction, knowledge, generation, utility)
            input_type: Input type (text, structured, image)
            keywords: Keywords for routing
        """
        self.tools[name] = tool
        self.tool_metadata[name] = {
            "description": description,
            "category": category,
            "input_type": input_type,
            "keywords": keywords
        }
        print(f"  ✓ Registered: {name} ({category})")
    
    def get_tool(self, name: str) -> Optional[Any]:
        """
        Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        if not self._initialized:
            self.initialize()
        
        return self.tools.get(name)
    
    def get_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a tool.
        
        Args:
            name: Tool name
            
        Returns:
            Metadata dictionary or None if not found
        """
        return self.tool_metadata.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """
        List all registered tools, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of tool names
        """
        if not self._initialized:
            self.initialize()
        
        if category:
            return [
                name for name, meta in self.tool_metadata.items()
                if meta['category'] == category
            ]
        
        return list(self.tools.keys())
    
    def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all tools.
        
        Returns:
            Dictionary mapping tool names to metadata
        """
        return self.tool_metadata.copy()
    
    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete information about a tool.
        
        Args:
            name: Tool name
            
        Returns:
            Dictionary with tool and metadata
        """
        tool = self.get_tool(name)
        metadata = self.get_metadata(name)
        
        if tool and metadata:
            return {
                "name": name,
                "tool": tool,
                "metadata": metadata
            }
        
        return None
    
    def __repr__(self) -> str:
        """String representation of registry."""
        return f"<ToolRegistry: {len(self.tools)} tools registered>"


# Singleton instance
_registry = None


def get_registry() -> ToolRegistry:
    """
    Get the singleton tool registry instance.
    
    Returns:
        ToolRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
        _registry.initialize()
    return _registry


# Example usage
if __name__ == "__main__":
    registry = get_registry()
    
    print("\n" + "="*70)
    print("TOOL REGISTRY TEST")
    print("="*70)
    
    # List all tools
    print(f"\nAll Tools ({len(registry.list_tools())}):")
    for tool_name in registry.list_tools():
        metadata = registry.get_metadata(tool_name)
        print(f"  • {tool_name} - {metadata['description'][:60]}...")
    
    # List by category
    print(f"\nPrediction Tools:")
    for tool_name in registry.list_tools(category="prediction"):
        print(f"  • {tool_name}")
    
    # Get specific tool
    print(f"\nTesting Yield Tool:")
    yield_tool = registry.get_tool("yield_prediction")
    if yield_tool:
        print(f"  ✓ Tool loaded: {yield_tool.name}")
        print(f"  Description: {yield_tool.description}")
    
    print("="*70)

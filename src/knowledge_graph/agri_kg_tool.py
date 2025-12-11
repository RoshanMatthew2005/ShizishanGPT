"""
AgriKG Tool Wrapper
Tool wrapper for integrating Knowledge Graph with ReAct agent.
"""

from typing import Dict, Any
from src.knowledge_graph.query_engine import AgriKGQueryEngine


class AgriKGTool:
    """Tool wrapper for Agriculture Knowledge Graph."""
    
    def __init__(self):
        """Initialize AgriKG tool."""
        self.name = "agri_kg_query"
        self.description = """Query the Agriculture Knowledge Graph for structured information about:
- Diseases affecting crops
- Pests affecting crops
- Fertilizers required for crops
- Ideal soil types for crops
- Treatments for diseases
- Pesticides for pests
- Complete crop information

Use this tool when the user asks about relationships between agricultural entities.
Examples:
- "What diseases affect rice?"
- "Which pests attack wheat?"
- "What fertilizers does maize need?"
- "What is the ideal soil for rice?"
"""
        self.engine = AgriKGQueryEngine()
        self.is_loaded = False
    
    def load(self) -> bool:
        """Load the knowledge graph connection."""
        if not self.is_loaded:
            self.is_loaded = self.engine.load()
        return self.is_loaded
    
    def predict(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Standard predict interface for compatibility with other tools.
        
        Args:
            query: Natural language query or user input
            **kwargs: Additional parameters
            
        Returns:
            Query results
        """
        return self.run(query=query, **kwargs)
    
    def run(self, query: str = None, input: str = None, cypher: str = None, **kwargs) -> Dict[str, Any]:
        """
        Run a knowledge graph query.
        
        Args:
            query: Natural language query
            input: Alternative input parameter (for compatibility)
            cypher: Cypher query (optional)
            **kwargs: Additional parameters
            
        Returns:
            Query results
        """
        try:
            # Handle different input parameter names
            actual_query = query or input or kwargs.get('tool_input')
            
            # Load if not loaded
            if not self.is_loaded:
                if not self.load():
                    return {
                        "success": False,
                        "error": "Knowledge graph not available. Please ensure Neo4j is running.",
                        "tool": self.name,
                        "guidance": {
                            "message": "The knowledge graph service is currently unavailable.",
                            "options": [
                                "Try using RAG retrieval for general agricultural information",
                                "Use Tavily search for current information"
                            ]
                        }
                    }
            
            # Execute query
            if cypher:
                result = self.engine.execute_cypher(cypher, kwargs)
            elif actual_query:
                result = self.engine.natural_language_query(actual_query)
            else:
                return {
                    "success": False,
                    "error": "Either 'query' or 'cypher' parameter is required",
                    "tool": self.name
                }
            
            # Format results for better readability
            if result.get("success") and result.get("count", 0) > 0:
                result["formatted_result"] = self.engine.format_results(result)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Knowledge graph query failed: {str(e)}",
                "tool": self.name
            }
    
    def __call__(self, query: str = None, input: str = None, cypher: str = None, **kwargs) -> Dict[str, Any]:
        """Allow tool to be called directly."""
        return self.run(query=query, input=input, cypher=cypher, **kwargs)


# LangChain Tool Definition
def get_langchain_tool():
    """
    Get LangChain tool definition for AgriKG.
    
    Returns:
        Tool configuration dict
    """
    return {
        "name": "agri_kg_query",
        "description": """Query the Agriculture Knowledge Graph for structured information about crops, diseases, pests, fertilizers, soil types, and their relationships.

Use this tool when you need to answer questions about:
- What diseases affect a specific crop
- What pests attack a specific crop  
- What fertilizers a crop needs
- What soil type is ideal for a crop
- How to treat a specific disease
- What pesticides control a specific pest

Input: Natural language query or Cypher query
Output: Structured JSON results with relationships

Examples:
- Input: "What diseases affect rice?"
  Output: List of diseases with severity and symptoms
  
- Input: "What fertilizers does wheat need?"
  Output: List of fertilizers with NPK ratios and application stages
  
- Input: "What is the ideal soil for maize?"
  Output: Soil types with suitability ratings""",
        
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language query about crops, diseases, pests, etc."
                },
                "cypher": {
                    "type": "string",
                    "description": "Optional Cypher query for advanced users"
                }
            },
            "anyOf": [
                {"required": ["query"]},
                {"required": ["cypher"]}
            ]
        },
        
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "tool": {"type": "string"},
                "results": {
                    "type": "array",
                    "description": "Array of result objects"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of results"
                },
                "formatted_result": {
                    "type": "string",
                    "description": "Human-readable formatted results"
                }
            }
        },
        
        "function": AgriKGTool()
    }

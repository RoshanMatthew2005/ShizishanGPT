"""
Tavily Search Tool
Wrapper for Tavily web search API integration with ReAct agent
"""

import os
import logging
from typing import Dict, Any, Optional
from tavily import TavilyClient

logger = logging.getLogger(__name__)


class TavilyTool:
    """Tool for executing Tavily web searches for agricultural information"""
    
    def __init__(self):
        """Initialize Tavily tool with direct API access"""
        self.name = "tavily_search"
        self.description = "Search the web for real-time agricultural information"
        
        # Get API key from environment
        from pathlib import Path
        import sys
        project_root = Path(__file__).resolve().parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from src.backend.config import settings
        api_key = settings.TAVILY_API_KEY
        
        if not api_key:
            logger.warning("⚠️ TAVILY_API_KEY not found in settings")
            self.client = None
        else:
            self.client = TavilyClient(api_key=api_key)
            logger.info(f"✓ Tavily tool initialized with direct API access")
    
    def predict(self, query: str, max_results: int = 5, search_depth: str = "basic") -> Dict[str, Any]:
        """
        Execute Tavily search (using 'predict' interface to match other tools)
        
        Args:
            query: Search query string
            max_results: Number of results (1-10)
            search_depth: "basic" (fast) or "advanced" (thorough)
        
        Returns:
            Dictionary with search results
        """
        return self.search(query, max_results, search_depth)
    
    def search(self, query: str, max_results: int = 5, search_depth: str = "basic") -> Dict[str, Any]:
        """
        Execute Tavily search using Tavily SDK directly
        
        Args:
            query: Search query string
            max_results: Number of results (1-10)
            search_depth: "basic" or "advanced"
        
        Returns:
            {
                "success": bool,
                "tool": str,
                "query": str,
                "summary": str,  # Formatted text for LLM
                "results": list,  # Raw results
                "answer": str,  # AI-generated answer
                "results_count": int
            }
        """
        try:
            if not self.client:
                return {
                    "success": False,
                    "tool": self.name,
                    "query": query,
                    "error": "Tavily API key not configured"
                }
            
            logger.info(f"🔍 Tavily search: {query}")
            
            # Call Tavily API directly
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=True
            )
            
            # Format results for LLM consumption
            results_text = self._format_results_for_llm(query, response)
            
            return {
                "success": True,
                "tool": self.name,
                "query": query,
                "summary": results_text,
                "results": response.get("results", []),
                "answer": response.get("answer", ""),
                "results_count": len(response.get("results", [])),
                "response_time": response.get("response_time", 0)
            }
            
        except Exception as e:
            logger.error(f"Tavily API error: {e}")
            return {
                "success": False,
                "tool": self.name,
                "query": query,
                "error": f"Search failed: {str(e)}"
            }
    
    def _format_results_for_llm(self, query: str, data: Dict[str, Any]) -> str:
        """
        Format Tavily results into readable text for LLM
        
        Args:
            query: Original search query
            data: Raw Tavily API response
        
        Returns:
            Formatted text string (content only, no URLs)
        """
        results_text = f"Search results for: \"{query}\"\n\n"
        
        # Add AI-generated quick answer if available
        if data.get("answer"):
            results_text += f"Quick Answer: {data['answer']}\n\n"
        
        # Add detailed content (NO URLs or sources)
        results_text += "Relevant Information:\n\n"
        results = data.get("results", [])
        
        if not results:
            results_text += "No results found.\n"
        else:
            for i, result in enumerate(results[:5], 1):
                # Add content snippet only (NO title, NO URL)
                content = result.get('content', '')
                if content:
                    # Truncate long content
                    snippet = content[:500] + "..." if len(content) > 500 else content
                    results_text += f"{snippet}\n\n"
        
        return results_text
    
    def run(self, query: str = "", **kwargs) -> Dict[str, Any]:
        """
        Standard run method for tool registry compatibility
        
        Args:
            query: Search query
            **kwargs: Additional parameters
        
        Returns:
            Search results
        """
        max_results = kwargs.get('max_results', 5)
        search_depth = kwargs.get('search_depth', 'basic')
        return self.search(query, max_results, search_depth)
    
    def __call__(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Allow calling tool as function
        
        Args:
            query: Search query
            **kwargs: Additional parameters
        
        Returns:
            Search results
        """
        return self.run(query, **kwargs)


# Example usage
if __name__ == "__main__":
    tool = TavilyTool()
    
    print("\n" + "="*70)
    print("TAVILY TOOL TEST")
    print("="*70)
    
    # Test search
    result = tool.search("best pesticide for whitefly in cotton 2025")
    
    if result["success"]:
        print(f"\n✅ Search successful!")
        print(f"Query: {result['query']}")
        print(f"Results: {result['results_count']}")
        print(f"\n{result['summary']}")
    else:
        print(f"\n❌ Search failed: {result.get('error')}")
    
    print("="*70)

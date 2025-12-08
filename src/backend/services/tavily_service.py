"""
Tavily Search Service
Provides real-time web search capability for agricultural information
"""

import os
import time
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class TavilyService:
    """Service for Tavily AI-powered web search"""
    
    def __init__(self):
        """Initialize Tavily client"""
        api_key = settings.TAVILY_API_KEY
        if not api_key:
            logger.warning("⚠️ TAVILY_API_KEY not found in environment")
            self.client = None
        else:
            self.client = TavilyClient(api_key=api_key)
            logger.info("✓ Tavily client initialized")
    
    async def search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        include_answer: bool = True
    ) -> Dict[str, Any]:
        """
        Execute Tavily search
        
        Args:
            query: Search query string
            search_depth: "basic" (fast) or "advanced" (thorough)
            max_results: Number of results to return (1-10)
            include_domains: Optional list of domains to prioritize
            include_answer: Whether to include AI-generated answer
            
        Returns:
            {
                "success": bool,
                "query": str,
                "results": [{"title", "content", "url", "score"}],
                "answer": str (optional),
                "response_time": float
            }
        """
        if not self.client:
            return {
                "success": False,
                "error": "Tavily API key not configured",
                "query": query,
                "results": [],
                "response_time": 0.0,
                "results_count": 0
            }
        
        try:
            start_time = time.time()
            
            # Execute Tavily search
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains,
                include_answer=include_answer,
                include_raw_content=False  # We don't need full HTML
            )
            
            response_time = time.time() - start_time
            
            # Format results
            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),
                    "url": item.get("url", ""),
                    "score": item.get("score", 0.0),
                    "published_date": item.get("published_date")
                })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "answer": response.get("answer", ""),
                "response_time": round(response_time, 2),
                "results_count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": [],
                "response_time": 0.0,
                "results_count": 0
            }
    
    async def search_agricultural(
        self,
        query: str,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Optimized search for agricultural queries
        Automatically prioritizes trusted agricultural domains
        """
        trusted_domains = [
            "agritech.tnau.ac.in",  # Tamil Nadu Agricultural University
            "icar.org.in",          # Indian Council of Agricultural Research
            "farmer.gov.in",        # Government farmer portal
            "agricoop.nic.in",      # Ministry of Agriculture
            "apeda.gov.in",         # Agricultural Export Development
            "extension.org",        # Cooperative Extension
            "fao.org",              # UN Food & Agriculture
            "cropscience.bayer.com",# Crop science research
        ]
        
        return await self.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_domains=trusted_domains,
            include_answer=True
        )

# Global instance
tavily_service = TavilyService()

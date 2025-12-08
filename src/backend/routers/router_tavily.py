"""
Tavily Search Router
Handles real-time web search requests
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ..models.schemas import TavilySearchRequest, TavilySearchResponse
from ..services.tavily_service import tavily_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["search"])

@router.post("/tavily_search", response_model=TavilySearchResponse)
async def search_web(request: TavilySearchRequest) -> Dict[str, Any]:
    """
    Execute Tavily web search for agricultural information
    
    **Use Cases:**
    - Latest pesticide/fungicide information
    - Government schemes and subsidies
    - Current disease outbreak alerts
    - Product availability and pricing
    - Recent research findings
    
    **Example Query:**
    ```json
    {
        "query": "best organic treatment for whitefly in cotton 2025",
        "search_depth": "basic",
        "max_results": 5
    }
    ```
    """
    try:
        logger.info(f"🔍 Tavily search request: {request.query}")
        
        result = await tavily_service.search(
            query=request.query,
            search_depth=request.search_depth,
            max_results=request.max_results,
            include_domains=request.include_domains
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Search failed")
            )
        
        logger.info(f"✓ Tavily search completed: {result['results_count']} results in {result['response_time']}s")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tavily search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tavily_search/agricultural", response_model=TavilySearchResponse)
async def search_agricultural(request: TavilySearchRequest) -> Dict[str, Any]:
    """
    Optimized Tavily search for agricultural queries
    Automatically prioritizes trusted agricultural domains
    """
    try:
        logger.info(f"🌾 Agricultural search: {request.query}")
        
        result = await tavily_service.search_agricultural(
            query=request.query,
            max_results=request.max_results
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Agricultural search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

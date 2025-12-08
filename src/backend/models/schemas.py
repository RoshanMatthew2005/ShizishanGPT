"""
Pydantic Schemas for API Request/Response Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# ===== Tavily Search Schemas =====

class TavilySearchRequest(BaseModel):
    """Request model for Tavily search"""
    query: str = Field(..., description="Search query", min_length=3, max_length=500)
    search_depth: str = Field("basic", description="Search depth: basic or advanced", pattern="^(basic|advanced)$")
    max_results: int = Field(5, ge=1, le=10, description="Maximum results to return")
    include_domains: Optional[List[str]] = Field(None, description="Prioritize specific domains")

class TavilySearchResult(BaseModel):
    """Individual search result"""
    title: str
    content: str
    url: str
    score: float
    published_date: Optional[str] = None

class TavilySearchResponse(BaseModel):
    """Response model for Tavily search"""
    success: bool
    query: str
    results: List[TavilySearchResult]
    answer: Optional[str] = None
    response_time: float
    results_count: int
    error: Optional[str] = None

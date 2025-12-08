"""
Weather Router
FastAPI endpoints for weather data retrieval
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import logging

from src.backend.schemas.weather_schemas import (
    WeatherRequest, WeatherResponse, WeatherError
)
from src.backend.services.weather_service import weather_service
from src.backend.utils.geocoding import is_valid_location, search_location


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.post("/", response_model=WeatherResponse)
async def get_weather(request: WeatherRequest) -> WeatherResponse:
    """
    Get current weather and forecast for a location
    
    Args:
        request: WeatherRequest with location and days
        
    Returns:
        WeatherResponse with current conditions and forecast
        
    Raises:
        HTTPException: If location not found or API error
    """
    try:
        # Validate location
        if not is_valid_location(request.location):
            # Try to find similar locations
            suggestions = search_location(request.location)
            error_msg = f"Location '{request.location}' not found."
            
            if suggestions:
                error_msg += f" Did you mean: {', '.join(suggestions[:3])}?"
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        
        # Fetch weather data
        weather_data = await weather_service.fetch_weather(
            location=request.location,
            days=request.days
        )
        
        if not weather_data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Weather service temporarily unavailable. Please try again later."
            )
        
        logger.info(f"Weather data retrieved for {request.location}")
        return weather_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_weather endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching weather data"
        )


@router.get("/locations")
async def get_supported_locations() -> Dict[str, Any]:
    """
    Get list of all supported locations
    
    Returns:
        Dictionary with location list
    """
    from src.backend.utils.geocoding import get_all_locations
    
    locations = get_all_locations()
    
    return {
        "count": len(locations),
        "locations": sorted(locations)
    }


@router.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get weather cache statistics
    
    Returns:
        Cache statistics
    """
    from src.backend.utils.weather_cache import weather_cache
    
    return weather_cache.get_stats()


@router.post("/cache/clear")
async def clear_cache() -> Dict[str, str]:
    """
    Clear weather cache
    
    Returns:
        Success message
    """
    from src.backend.utils.weather_cache import weather_cache
    
    weather_cache.clear()
    logger.info("Weather cache cleared")
    
    return {"message": "Weather cache cleared successfully"}

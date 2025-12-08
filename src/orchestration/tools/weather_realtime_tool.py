"""
Weather Realtime Tool for ReAct Agent
Fetches current weather and forecast data for agricultural decision-making
"""

import asyncio
from typing import Dict, Any
import logging

from src.backend.services.weather_service import weather_service
from src.backend.utils.geocoding import is_valid_location, search_location


logger = logging.getLogger(__name__)


async def weather_realtime_tool(location: str, days: int = 7) -> str:
    """
    Fetch real-time weather data for a location
    
    This tool retrieves current weather conditions and forecast data
    from Open-Meteo API, optimized for agricultural use cases.
    
    Args:
        location: State or district name in India (e.g., "Maharashtra", "Punjab", "Pune")
        days: Number of forecast days (1-16, default: 7)
        
    Returns:
        Formatted string with weather data or error message
        
    Examples:
        >>> await weather_realtime_tool("Maharashtra", 7)
        >>> await weather_realtime_tool("Punjab", 3)
        >>> await weather_realtime_tool("Pune", 14)
    """
    try:
        # Validate inputs
        if not isinstance(location, str) or not location.strip():
            return "Error: Location must be a non-empty string"
        
        if not isinstance(days, int) or days < 1 or days > 16:
            return "Error: Days must be an integer between 1 and 16"
        
        # Check if location exists
        if not is_valid_location(location):
            suggestions = search_location(location)
            error_msg = f"Location '{location}' not found in database."
            
            if suggestions:
                error_msg += f" Did you mean: {', '.join(suggestions[:3])}?"
            else:
                error_msg += " Please use a valid Indian state or district name."
            
            return error_msg
        
        # Fetch weather data
        weather_data = await weather_service.fetch_weather(location, days)
        
        if not weather_data:
            return f"Error: Could not fetch weather data for {location}. Weather service may be temporarily unavailable."
        
        # Format response
        result = f"Weather Data for {weather_data.location}\n"
        result += f"Coordinates: {weather_data.coordinates['latitude']:.4f}°N, {weather_data.coordinates['longitude']:.4f}°E\n\n"
        
        # Current conditions
        current = weather_data.current
        result += "CURRENT CONDITIONS:\n"
        result += f"- Temperature: {current.temperature}°C\n"
        result += f"- Humidity: {current.humidity}%\n"
        result += f"- Rainfall: {current.rainfall} mm\n"
        result += f"- Wind Speed: {current.wind_speed} km/h\n"
        
        if current.soil_temperature is not None:
            result += f"- Soil Temperature (0-7cm): {current.soil_temperature}°C\n"
        
        if current.soil_moisture is not None:
            result += f"- Soil Moisture (0-7cm): {current.soil_moisture:.3f} m³/m³\n"
        
        result += f"- Description: {current.description}\n\n"
        
        # Forecast summary (first 3 days for brevity)
        result += f"FORECAST (Next {min(3, len(weather_data.forecast))} days):\n"
        for i, day in enumerate(weather_data.forecast[:3]):
            result += f"\n{day.date}:\n"
            result += f"  Temperature: {day.temperature_min}°C - {day.temperature_max}°C\n"
            result += f"  Rainfall: {day.rainfall_sum} mm"
            
            if day.rainfall_probability is not None:
                result += f" ({day.rainfall_probability}% chance)\n"
            else:
                result += "\n"
            
            result += f"  Wind: {day.wind_speed_max} km/h max\n"
            
            if day.et0_sum is not None:
                result += f"  Evapotranspiration (ET0): {day.et0_sum:.2f} mm\n"
        
        # Add agricultural insights
        result += "\n" + _generate_agricultural_insights(weather_data)
        
        logger.info(f"Weather data retrieved for {location} ({days} days)")
        return result
        
    except Exception as e:
        logger.error(f"Error in weather_realtime_tool: {e}")
        return f"Error: Failed to fetch weather data. {str(e)}"


def _generate_agricultural_insights(weather_data) -> str:
    """
    Generate agricultural insights from weather data
    
    Args:
        weather_data: WeatherResponse object
        
    Returns:
        Formatted insights string
    """
    insights = "AGRICULTURAL INSIGHTS:\n"
    
    current = weather_data.current
    forecast = weather_data.forecast
    
    # Temperature insights
    if current.temperature > 35:
        insights += "⚠️ High temperature alert - Consider irrigation and heat stress management\n"
    elif current.temperature < 10:
        insights += "⚠️ Cold weather alert - Protect sensitive crops from frost\n"
    
    # Rainfall insights
    upcoming_rainfall = sum(day.rainfall_sum for day in forecast[:3])
    if upcoming_rainfall > 50:
        insights += f"🌧️ Heavy rainfall expected ({upcoming_rainfall:.1f}mm in 3 days) - Adjust irrigation schedules\n"
    elif upcoming_rainfall < 5 and current.rainfall < 0.1:
        insights += "☀️ Dry conditions - Ensure adequate irrigation\n"
    
    # Soil moisture insights
    if current.soil_moisture is not None:
        if current.soil_moisture < 0.15:
            insights += "💧 Low soil moisture detected - Irrigation recommended\n"
        elif current.soil_moisture > 0.35:
            insights += "💧 High soil moisture - Reduce irrigation to prevent waterlogging\n"
    
    # Wind insights
    if current.wind_speed > 30:
        insights += "💨 High wind speed - Delay pesticide/fertilizer application\n"
    
    # Evapotranspiration insights
    avg_et0 = sum(day.et0_sum for day in forecast[:3] if day.et0_sum) / max(1, len([d for d in forecast[:3] if d.et0_sum]))
    if avg_et0 > 5:
        insights += f"📊 High evapotranspiration ({avg_et0:.1f}mm/day) - Increase irrigation frequency\n"
    
    return insights


# Tool metadata for ReAct agent
TOOL_METADATA = {
    "name": "weather_realtime",
    "description": "Fetch real-time weather data and forecast for Indian agricultural regions. Provides current conditions, multi-day forecast, and agricultural insights.",
    "parameters": {
        "location": {
            "type": "string",
            "description": "State or district name in India (e.g., Maharashtra, Punjab, Pune)",
            "required": True
        },
        "days": {
            "type": "integer",
            "description": "Number of forecast days (1-16)",
            "required": False,
            "default": 7
        }
    },
    "examples": [
        {"location": "Maharashtra", "days": 7},
        {"location": "Punjab", "days": 3},
        {"location": "Pune", "days": 14}
    ]
}


def weather_realtime_sync(location: str, days: int = 7) -> str:
    """
    Synchronous wrapper for weather_realtime_tool
    Used by ReAct agent in synchronous context
    """
    return asyncio.run(weather_realtime_tool(location, days))

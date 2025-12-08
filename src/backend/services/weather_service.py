"""
Weather Service - Open-Meteo API Integration
Fetches real-time and forecast weather data for Indian agricultural regions
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from src.backend.schemas.weather_schemas import (
    WeatherResponse, CurrentWeather, DailyForecast
)
from src.backend.utils.geocoding import get_coordinates
from src.backend.utils.weather_cache import weather_cache


logger = logging.getLogger(__name__)


class WeatherService:
    """
    Service for fetching weather data from Open-Meteo API
    Free tier: unlimited requests, no API key required
    """
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    # Agricultural-focused weather parameters
    CURRENT_PARAMS = [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "soil_temperature_0_to_7cm",
        "soil_moisture_0_to_7cm"
    ]
    
    DAILY_PARAMS = [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "precipitation_probability_max",
        "wind_speed_10m_max",
        "et0_fao_evapotranspiration"  # Reference evapotranspiration
    ]
    
    async def fetch_weather(
        self, 
        location: str, 
        days: int = 7
    ) -> Optional[WeatherResponse]:
        """
        Fetch weather data for a location
        
        Args:
            location: State or district name
            days: Number of forecast days (1-16)
            
        Returns:
            WeatherResponse object or None if error
        """
        try:
            # Check cache first
            cached_data = weather_cache.get(location, days)
            if cached_data:
                logger.info(f"Cache hit for {location} ({days} days)")
                return WeatherResponse(**cached_data)
            
            # Get coordinates
            coords = get_coordinates(location)
            if not coords:
                logger.error(f"Location not found: {location}")
                return None
            
            lat, lon, formatted_name = coords
            
            # Build API request
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": ",".join(self.CURRENT_PARAMS),
                "daily": ",".join(self.DAILY_PARAMS),
                "forecast_days": days,
                "timezone": "Asia/Kolkata"
            }
            
            # Fetch from Open-Meteo
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
            
            # Parse response
            weather_response = self._parse_weather_data(
                data, formatted_name, lat, lon
            )
            
            # Cache the result
            weather_cache.set(location, days, weather_response.dict())
            logger.info(f"Fetched and cached weather for {location} ({days} days)")
            
            return weather_response
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching weather: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
    
    def _parse_weather_data(
        self, 
        data: Dict[str, Any], 
        location_name: str,
        lat: float,
        lon: float
    ) -> WeatherResponse:
        """
        Parse Open-Meteo API response into WeatherResponse
        
        Args:
            data: Raw API response
            location_name: Formatted location name
            lat: Latitude
            lon: Longitude
            
        Returns:
            WeatherResponse object
        """
        # Parse current weather
        current_data = data.get("current", {})
        current = CurrentWeather(
            temperature=current_data.get("temperature_2m", 0.0),
            humidity=int(current_data.get("relative_humidity_2m", 0)),
            rainfall=current_data.get("precipitation", 0.0),
            wind_speed=current_data.get("wind_speed_10m", 0.0),
            soil_temperature=current_data.get("soil_temperature_0_to_7cm"),
            soil_moisture=current_data.get("soil_moisture_0_to_7cm"),
            description=self._get_weather_description(
                current_data.get("precipitation", 0.0),
                current_data.get("temperature_2m", 0.0)
            )
        )
        
        # Parse daily forecast
        daily_data = data.get("daily", {})
        forecast = []
        
        dates = daily_data.get("time", [])
        temp_max = daily_data.get("temperature_2m_max", [])
        temp_min = daily_data.get("temperature_2m_min", [])
        rain_sum = daily_data.get("precipitation_sum", [])
        rain_prob = daily_data.get("precipitation_probability_max", [])
        wind_max = daily_data.get("wind_speed_10m_max", [])
        et0 = daily_data.get("et0_fao_evapotranspiration", [])
        
        for i in range(len(dates)):
            daily_forecast = DailyForecast(
                date=dates[i],
                temperature_max=temp_max[i] if i < len(temp_max) else 0.0,
                temperature_min=temp_min[i] if i < len(temp_min) else 0.0,
                rainfall_sum=rain_sum[i] if i < len(rain_sum) else 0.0,
                rainfall_probability=int(rain_prob[i]) if i < len(rain_prob) and rain_prob[i] is not None else None,
                wind_speed_max=wind_max[i] if i < len(wind_max) else 0.0,
                humidity_avg=None,  # Not provided by Open-Meteo in daily
                et0_sum=et0[i] if i < len(et0) else None
            )
            forecast.append(daily_forecast)
        
        return WeatherResponse(
            location=location_name,
            coordinates={"latitude": lat, "longitude": lon},
            current=current,
            forecast=forecast,
            timestamp=datetime.now()
        )
    
    def _get_weather_description(self, rainfall: float, temperature: float) -> str:
        """
        Generate simple weather description
        
        Args:
            rainfall: Current rainfall in mm
            temperature: Current temperature in Celsius
            
        Returns:
            Weather description string
        """
        if rainfall > 5.0:
            return "Heavy rain"
        elif rainfall > 1.0:
            return "Light rain"
        elif rainfall > 0.1:
            return "Drizzle"
        elif temperature > 35:
            return "Hot and dry"
        elif temperature > 28:
            return "Warm"
        elif temperature > 20:
            return "Pleasant"
        elif temperature > 15:
            return "Cool"
        else:
            return "Cold"


# Global service instance
weather_service = WeatherService()

"""
Weather API Schemas for ShizishanGPT
Pydantic models for weather request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class WeatherRequest(BaseModel):
    """Request schema for weather data"""
    location: str = Field(..., description="State or District name in India", example="Maharashtra")
    days: Optional[int] = Field(7, description="Number of days for forecast (1-16)", ge=1, le=16)
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": "Maharashtra",
                "days": 7
            }
        }


class CurrentWeather(BaseModel):
    """Current weather conditions"""
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: int = Field(..., description="Relative humidity in percentage")
    rainfall: float = Field(..., description="Rainfall in mm")
    wind_speed: float = Field(..., description="Wind speed in km/h")
    soil_temperature: Optional[float] = Field(None, description="Soil temperature at 0-7cm depth in Celsius")
    soil_moisture: Optional[float] = Field(None, description="Soil moisture at 0-7cm depth in m³/m³")
    description: str = Field(..., description="Weather description")


class DailyForecast(BaseModel):
    """Daily weather forecast"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    temperature_max: float = Field(..., description="Maximum temperature in Celsius")
    temperature_min: float = Field(..., description="Minimum temperature in Celsius")
    rainfall_sum: float = Field(..., description="Total rainfall in mm")
    rainfall_probability: Optional[int] = Field(None, description="Probability of precipitation in percentage")
    wind_speed_max: float = Field(..., description="Maximum wind speed in km/h")
    humidity_avg: Optional[int] = Field(None, description="Average relative humidity in percentage")
    et0_sum: Optional[float] = Field(None, description="Reference evapotranspiration (ET0) in mm")


class WeatherResponse(BaseModel):
    """Complete weather response"""
    location: str = Field(..., description="Location name")
    coordinates: Dict[str, float] = Field(..., description="Latitude and longitude")
    current: CurrentWeather = Field(..., description="Current weather conditions")
    forecast: list[DailyForecast] = Field(..., description="Daily weather forecast")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": "Maharashtra",
                "coordinates": {"latitude": 19.7515, "longitude": 75.7139},
                "current": {
                    "temperature": 28.5,
                    "humidity": 65,
                    "rainfall": 0.0,
                    "wind_speed": 12.5,
                    "soil_temperature": 26.3,
                    "soil_moisture": 0.25,
                    "description": "Partly cloudy"
                },
                "forecast": [
                    {
                        "date": "2025-12-02",
                        "temperature_max": 32.0,
                        "temperature_min": 22.0,
                        "rainfall_sum": 0.0,
                        "rainfall_probability": 10,
                        "wind_speed_max": 15.0,
                        "humidity_avg": 60,
                        "et0_sum": 4.5
                    }
                ],
                "timestamp": "2025-12-02T10:30:00"
            }
        }


class WeatherError(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

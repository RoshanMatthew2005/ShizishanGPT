"""
Weather Cache Utility
In-memory cache with TTL for weather API responses
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import threading


class WeatherCache:
    """
    Simple in-memory cache with time-to-live (TTL)
    Thread-safe implementation for concurrent access
    """
    
    def __init__(self, ttl_minutes: int = 30):
        """
        Initialize weather cache
        
        Args:
            ttl_minutes: Time-to-live in minutes (default: 30)
        """
        self.ttl_minutes = ttl_minutes
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def _generate_key(self, location: str, days: int) -> str:
        """
        Generate cache key from location and days
        
        Args:
            location: Location name
            days: Number of forecast days
            
        Returns:
            Cache key string
        """
        return f"{location.lower().strip()}:{days}"
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """
        Check if cache entry has expired
        
        Args:
            timestamp: Cache entry timestamp
            
        Returns:
            True if expired, False otherwise
        """
        expiry_time = timestamp + timedelta(minutes=self.ttl_minutes)
        return datetime.now() > expiry_time
    
    def get(self, location: str, days: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached weather data
        
        Args:
            location: Location name
            days: Number of forecast days
            
        Returns:
            Cached data or None if not found/expired
        """
        key = self._generate_key(location, days)
        
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if self._is_expired(entry["timestamp"]):
                    # Remove expired entry
                    del self.cache[key]
                    return None
                
                # Return cached data
                return entry["data"]
        
        return None
    
    def set(self, location: str, days: int, data: Dict[str, Any]) -> None:
        """
        Store weather data in cache
        
        Args:
            location: Location name
            days: Number of forecast days
            data: Weather data to cache
        """
        key = self._generate_key(location, days)
        
        with self.lock:
            self.cache[key] = {
                "data": data,
                "timestamp": datetime.now()
            }
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
    
    def clear_expired(self) -> int:
        """
        Remove all expired cache entries
        
        Returns:
            Number of entries removed
        """
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if self._is_expired(entry["timestamp"])
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        with self.lock:
            total_entries = len(self.cache)
            expired_count = sum(
                1 for entry in self.cache.values()
                if self._is_expired(entry["timestamp"])
            )
            
            return {
                "total_entries": total_entries,
                "valid_entries": total_entries - expired_count,
                "expired_entries": expired_count,
                "ttl_minutes": self.ttl_minutes
            }


# Global cache instance (30-minute TTL)
weather_cache = WeatherCache(ttl_minutes=30)

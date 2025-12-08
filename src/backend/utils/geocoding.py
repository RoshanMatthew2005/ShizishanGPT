"""
Geocoding Utility for Indian Agricultural Regions
Maps state/district names to coordinates for weather API calls
"""

from typing import Optional, Dict, Tuple


# Comprehensive India location database (10 major agricultural states + 40+ districts)
INDIA_LOCATIONS = {
    # Major States (state capitals/centroid)
    "maharashtra": {"lat": 19.7515, "lon": 75.7139, "name": "Maharashtra"},
    "uttar pradesh": {"lat": 26.8467, "lon": 80.9462, "name": "Uttar Pradesh"},
    "punjab": {"lat": 31.1471, "lon": 75.3412, "name": "Punjab"},
    "haryana": {"lat": 29.0588, "lon": 76.0856, "name": "Haryana"},
    "madhya pradesh": {"lat": 22.9734, "lon": 78.6569, "name": "Madhya Pradesh"},
    "karnataka": {"lat": 15.3173, "lon": 75.7139, "name": "Karnataka"},
    "rajasthan": {"lat": 27.0238, "lon": 74.2179, "name": "Rajasthan"},
    "andhra pradesh": {"lat": 15.9129, "lon": 79.7400, "name": "Andhra Pradesh"},
    "telangana": {"lat": 18.1124, "lon": 79.0193, "name": "Telangana"},
    "gujarat": {"lat": 22.2587, "lon": 71.1924, "name": "Gujarat"},
    "west bengal": {"lat": 22.9868, "lon": 87.8550, "name": "West Bengal"},
    "tamil nadu": {"lat": 11.1271, "lon": 78.6569, "name": "Tamil Nadu"},
    "bihar": {"lat": 25.0961, "lon": 85.3131, "name": "Bihar"},
    
    # Maharashtra Districts
    "pune": {"lat": 18.5204, "lon": 73.8567, "name": "Pune"},
    "nashik": {"lat": 19.9975, "lon": 73.7898, "name": "Nashik"},
    "nagpur": {"lat": 21.1458, "lon": 79.0882, "name": "Nagpur"},
    "solapur": {"lat": 17.6599, "lon": 75.9064, "name": "Solapur"},
    "ahmednagar": {"lat": 19.0948, "lon": 74.7480, "name": "Ahmednagar"},
    "kolhapur": {"lat": 16.7050, "lon": 74.2433, "name": "Kolhapur"},
    
    # Punjab Districts
    "ludhiana": {"lat": 30.9010, "lon": 75.8573, "name": "Ludhiana"},
    "amritsar": {"lat": 31.6340, "lon": 74.8723, "name": "Amritsar"},
    "jalandhar": {"lat": 31.3260, "lon": 75.5762, "name": "Jalandhar"},
    "patiala": {"lat": 30.3398, "lon": 76.3869, "name": "Patiala"},
    "bathinda": {"lat": 30.2110, "lon": 74.9455, "name": "Bathinda"},
    
    # Uttar Pradesh Districts
    "lucknow": {"lat": 26.8467, "lon": 80.9462, "name": "Lucknow"},
    "kanpur": {"lat": 26.4499, "lon": 80.3319, "name": "Kanpur"},
    "agra": {"lat": 27.1767, "lon": 78.0081, "name": "Agra"},
    "varanasi": {"lat": 25.3176, "lon": 82.9739, "name": "Varanasi"},
    "meerut": {"lat": 28.9845, "lon": 77.7064, "name": "Meerut"},
    "allahabad": {"lat": 25.4358, "lon": 81.8463, "name": "Allahabad"},
    
    # Haryana Districts
    "gurugram": {"lat": 28.4595, "lon": 77.0266, "name": "Gurugram"},
    "faridabad": {"lat": 28.4089, "lon": 77.3178, "name": "Faridabad"},
    "karnal": {"lat": 29.6857, "lon": 76.9905, "name": "Karnal"},
    "hisar": {"lat": 29.1492, "lon": 75.7217, "name": "Hisar"},
    
    # Karnataka Districts
    "bengaluru": {"lat": 12.9716, "lon": 77.5946, "name": "Bengaluru"},
    "mysuru": {"lat": 12.2958, "lon": 76.6394, "name": "Mysuru"},
    "hubli": {"lat": 15.3647, "lon": 75.1240, "name": "Hubli"},
    "mangaluru": {"lat": 12.9141, "lon": 74.8560, "name": "Mangaluru"},
    
    # Gujarat Districts
    "ahmedabad": {"lat": 23.0225, "lon": 72.5714, "name": "Ahmedabad"},
    "surat": {"lat": 21.1702, "lon": 72.8311, "name": "Surat"},
    "vadodara": {"lat": 22.3072, "lon": 73.1812, "name": "Vadodara"},
    "rajkot": {"lat": 22.3039, "lon": 70.8022, "name": "Rajkot"},
    
    # Rajasthan Districts
    "jaipur": {"lat": 26.9124, "lon": 75.7873, "name": "Jaipur"},
    "jodhpur": {"lat": 26.2389, "lon": 73.0243, "name": "Jodhpur"},
    "kota": {"lat": 25.2138, "lon": 75.8648, "name": "Kota"},
    "udaipur": {"lat": 24.5854, "lon": 73.7125, "name": "Udaipur"},
    
    # Tamil Nadu Districts
    "chennai": {"lat": 13.0827, "lon": 80.2707, "name": "Chennai"},
    "coimbatore": {"lat": 11.0168, "lon": 76.9558, "name": "Coimbatore"},
    "madurai": {"lat": 9.9252, "lon": 78.1198, "name": "Madurai"},
    "salem": {"lat": 11.6643, "lon": 78.1460, "name": "Salem"},
    
    # West Bengal Districts
    "kolkata": {"lat": 22.5726, "lon": 88.3639, "name": "Kolkata"},
    "howrah": {"lat": 22.5958, "lon": 88.2636, "name": "Howrah"},
    "siliguri": {"lat": 26.7271, "lon": 88.3953, "name": "Siliguri"},
    
    # Madhya Pradesh Districts
    "indore": {"lat": 22.7196, "lon": 75.8577, "name": "Indore"},
    "bhopal": {"lat": 23.2599, "lon": 77.4126, "name": "Bhopal"},
    "jabalpur": {"lat": 23.1815, "lon": 79.9864, "name": "Jabalpur"},
    "gwalior": {"lat": 26.2183, "lon": 78.1828, "name": "Gwalior"},
}


def normalize_location_name(location: str) -> str:
    """
    Normalize location name for lookup
    
    Args:
        location: Raw location string from user
        
    Returns:
        Normalized location name (lowercase, trimmed)
    """
    return location.lower().strip()


def get_coordinates(location: str) -> Optional[Tuple[float, float, str]]:
    """
    Get latitude and longitude for a location
    
    Args:
        location: State or district name
        
    Returns:
        Tuple of (latitude, longitude, formatted_name) or None if not found
    """
    normalized = normalize_location_name(location)
    
    if normalized in INDIA_LOCATIONS:
        loc_data = INDIA_LOCATIONS[normalized]
        return (loc_data["lat"], loc_data["lon"], loc_data["name"])
    
    return None


def is_valid_location(location: str) -> bool:
    """
    Check if location is in the database
    
    Args:
        location: Location name to validate
        
    Returns:
        True if location exists, False otherwise
    """
    return normalize_location_name(location) in INDIA_LOCATIONS


def get_all_locations() -> list[str]:
    """
    Get list of all supported locations
    
    Returns:
        List of location names
    """
    return [data["name"] for data in INDIA_LOCATIONS.values()]


def search_location(query: str) -> list[str]:
    """
    Search for locations matching query
    
    Args:
        query: Search query (partial match supported)
        
    Returns:
        List of matching location names
    """
    query_lower = query.lower().strip()
    matches = []
    
    for key, data in INDIA_LOCATIONS.items():
        if query_lower in key or query_lower in data["name"].lower():
            matches.append(data["name"])
    
    return matches

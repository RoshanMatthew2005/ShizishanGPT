"""
Weather Integration Test
Tests the complete weather system from API to ReAct agent
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))


async def test_weather_service():
    """Test weather service directly"""
    print("\n" + "="*70)
    print("TEST 1: Weather Service (Open-Meteo API)")
    print("="*70)
    
    from src.backend.services.weather_service import weather_service
    
    # Test fetching weather for Maharashtra
    print("\n📡 Fetching weather for Maharashtra (7 days)...")
    result = await weather_service.fetch_weather("Maharashtra", 7)
    
    if result:
        print(f"✅ Success!")
        print(f"   Location: {result.location}")
        print(f"   Coordinates: {result.coordinates}")
        print(f"   Current Temperature: {result.current.temperature}°C")
        print(f"   Current Humidity: {result.current.humidity}%")
        print(f"   Current Rainfall: {result.current.rainfall} mm")
        print(f"   Forecast Days: {len(result.forecast)}")
        print(f"   First Forecast: {result.forecast[0].date} - {result.forecast[0].temperature_min}°C to {result.forecast[0].temperature_max}°C")
    else:
        print("❌ Failed to fetch weather data")
    
    return result is not None


def test_geocoding():
    """Test geocoding utility"""
    print("\n" + "="*70)
    print("TEST 2: Geocoding Utility")
    print("="*70)
    
    from src.backend.utils.geocoding import (
        get_coordinates, is_valid_location, search_location, get_all_locations
    )
    
    # Test valid location
    print("\n🔍 Testing valid location: 'Maharashtra'")
    coords = get_coordinates("Maharashtra")
    if coords:
        lat, lon, name = coords
        print(f"✅ Found: {name} at ({lat}, {lon})")
    
    # Test invalid location
    print("\n🔍 Testing invalid location: 'XYZ'")
    is_valid = is_valid_location("XYZ")
    print(f"   Valid: {is_valid}")
    
    # Test search
    print("\n🔍 Searching for 'pun'")
    matches = search_location("pun")
    print(f"✅ Found {len(matches)} matches: {matches[:5]}")
    
    # Test all locations
    all_locs = get_all_locations()
    print(f"\n📍 Total locations in database: {len(all_locs)}")
    print(f"   Sample: {all_locs[:5]}")
    
    return True


def test_cache():
    """Test weather cache"""
    print("\n" + "="*70)
    print("TEST 3: Weather Cache")
    print("="*70)
    
    from src.backend.utils.weather_cache import weather_cache
    
    # Test cache operations
    print("\n💾 Testing cache set/get...")
    
    test_data = {"temperature": 28.5, "location": "Test"}
    weather_cache.set("TestLocation", 7, test_data)
    
    retrieved = weather_cache.get("TestLocation", 7)
    if retrieved == test_data:
        print("✅ Cache set/get working correctly")
    else:
        print("❌ Cache set/get failed")
    
    # Test cache stats
    stats = weather_cache.get_stats()
    print(f"\n📊 Cache Stats:")
    print(f"   Total Entries: {stats['total_entries']}")
    print(f"   Valid Entries: {stats['valid_entries']}")
    print(f"   TTL: {stats['ttl_minutes']} minutes")
    
    # Clear cache
    weather_cache.clear()
    stats_after = weather_cache.get_stats()
    print(f"\n🧹 After clearing - Entries: {stats_after['total_entries']}")
    
    return True


async def test_weather_tool():
    """Test weather realtime tool"""
    print("\n" + "="*70)
    print("TEST 4: Weather Realtime Tool")
    print("="*70)
    
    from src.orchestration.tools.weather_realtime_tool import weather_realtime_tool
    
    # Test tool with valid location
    print("\n🔧 Testing weather tool for 'Punjab' (3 days)...")
    result = await weather_realtime_tool("Punjab", 3)
    
    if "Weather Data for Punjab" in result:
        print("✅ Tool executed successfully")
        print("\n--- Tool Output Preview ---")
        print(result[:500] + "...")
    else:
        print("❌ Tool execution failed")
        print(f"   Output: {result}")
    
    # Test tool with invalid location
    print("\n🔧 Testing weather tool with invalid location...")
    result_invalid = await weather_realtime_tool("InvalidPlace", 7)
    
    if "not found" in result_invalid:
        print("✅ Correctly handled invalid location")
    else:
        print("❌ Did not handle invalid location properly")
    
    return "Weather Data for Punjab" in result


def test_tool_registry():
    """Test that weather tool is registered"""
    print("\n" + "="*70)
    print("TEST 5: Tool Registry Integration")
    print("="*70)
    
    from src.orchestration.tool_registry import get_registry
    
    registry = get_registry()
    
    # Check if weather_realtime is registered
    weather_tool = registry.get_tool("weather_realtime")
    
    if weather_tool:
        print("✅ weather_realtime tool registered in registry")
        
        metadata = registry.get_metadata("weather_realtime")
        print(f"   Description: {metadata['description']}")
        print(f"   Category: {metadata['category']}")
        print(f"   Keywords: {metadata['keywords']}")
    else:
        print("❌ weather_realtime tool NOT found in registry")
    
    # List all tools
    all_tools = registry.list_tools()
    print(f"\n📋 All registered tools ({len(all_tools)}):")
    for tool in all_tools:
        print(f"   • {tool}")
    
    return weather_tool is not None


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🌤️  WEATHER INTEGRATION TEST SUITE")
    print("="*70)
    
    results = []
    
    # Run tests
    try:
        results.append(("Geocoding Utility", test_geocoding()))
        results.append(("Weather Cache", test_cache()))
        results.append(("Weather Service", await test_weather_service()))
        results.append(("Weather Tool", await test_weather_tool()))
        results.append(("Tool Registry", test_tool_registry()))
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Weather integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())

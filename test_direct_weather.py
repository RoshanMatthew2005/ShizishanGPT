"""Test weather tool directly"""
from src.orchestration.tools.weather_realtime_tool import weather_realtime_sync

# Test with Punjab
result = weather_realtime_sync("Punjab", 3)
print("="*70)
print("DIRECT WEATHER TOOL TEST: Punjab")
print("="*70)
print(result[:500])

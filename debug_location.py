"""Debug weather location extraction"""
import re
from src.backend.utils.geocoding import is_valid_location, search_location

query_text = 'What is the weather in Punjab?'
print(f"Query: {query_text}\n")

# Try multiple patterns to find location
location = None
patterns = [
    r'weather\s+(?:in|at|for)\s+([A-Za-z\s]+?)(?:\s+(?:today|this week|forecast|now|\d+\s*days?)|[?,.]|$)',
    r'(?:in|at|for)\s+([A-Za-z\s]+?)(?:\s+(?:weather|today|this week|forecast|\d+\s*days?)|[?,.]|$)',
    r'([A-Za-z\s]+?)(?:\s+weather|\s+today)',
]

for i, pattern in enumerate(patterns, 1):
    location_match = re.search(pattern, query_text, re.IGNORECASE)
    print(f"Pattern {i}: {pattern}")
    if location_match:
        location = location_match.group(1).strip()
        print(f"  Match found: '{location}'")
        
        # Validate it's a known location
        if is_valid_location(location):
            print(f"  ✓ Valid location!")
            break
        else:
            print(f"  ✗ Not a valid location")
            
        # Try searching for similar
        matches = search_location(location)
        if matches:
            location = matches[0]
            print(f"  Found similar: {location}")
            break
    else:
        print(f"  No match")

print(f"\nFinal location: {location if location else 'Maharashtra (fallback)'}")

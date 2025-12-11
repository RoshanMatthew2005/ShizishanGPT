"""
Quick Test Script for New Agricultural Models
Tests all 4 new tools with sample data.
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("="*80)
print(" "*20 + "MODEL INTEGRATION TEST")
print("="*80)

# Test 1: Soil Moisture Classification
print("\n1. Testing Soil Moisture Classification...")
print("-"*80)
from src.model_tools.soil_moisture_tool import SoilMoistureTool

moisture_tool = SoilMoistureTool()
result1 = moisture_tool.predict({
    'temperature': 30,
    'pressure': 1013,
    'altitude': 500,
    'soil_moisture': 300
})

if result1['success']:
    print(f"✓ Classification: {result1['classification']}")
    print(f"  Confidence: {result1['confidence']:.1%}")
    print(f"  Recommendations: {result1['recommendations'][0]}")
else:
    print(f"✗ Error: {result1['error']}")


# Test 2: Crop Nutrient Recommendation
print("\n2. Testing Crop Nutrient Recommendation...")
print("-"*80)
from src.model_tools.crop_nutrient_tool import CropNutrientTool

nutrient_tool = CropNutrientTool()
result2 = nutrient_tool.predict({
    'N': 200, 'P': 50, 'K': 300,
    'ph': 6.5, 'EC': 1.2, 'S': 30,
    'Cu': 5, 'Fe': 40, 'Mn': 20,
    'Zn': 8, 'B': 2
})

if result2['success']:
    print(f"✓ Recommended Crop: {result2['recommended_crop']}")
    print(f"  Confidence: {result2['confidence']:.1%}")
    print(f"  Top 3: {', '.join([c['crop'] for c in result2['top_3_crops']])}")
else:
    print(f"✗ Error: {result2['error']}")


# Test 3: Crop Climate Recommendation
print("\n3. Testing Crop Climate Recommendation...")
print("-"*80)
from src.model_tools.crop_climate_tool import CropClimateTool

climate_tool = CropClimateTool()
result3 = climate_tool.predict({
    'N': 120, 'P': 60, 'K': 180,
    'temperature': 25, 'humidity': 75,
    'ph': 6.8, 'rainfall': 150
})

if result3['success']:
    print(f"✓ Recommended Crop: {result3['recommended_crop']}")
    print(f"  Confidence: {result3['confidence']:.1%}")
    print(f"  Top 5: {', '.join([c['crop'] for c in result3['top_5_crops'][:5]])}")
else:
    print(f"✗ Error: {result3['error']}")


# Test 4: Soil Fertility Classification
print("\n4. Testing Soil Fertility Classification...")
print("-"*80)
from src.model_tools.soil_fertility_tool import SoilFertilityTool

fertility_tool = SoilFertilityTool()
result4 = fertility_tool.predict({
    'N': 180, 'P': 45, 'K': 220,
    'pH': 6.5, 'EC': 1.5, 'OC': 0.8,
    'S': 25, 'Zn': 6, 'Fe': 35,
    'Cu': 4, 'Mn': 15, 'B': 1.5
})

if result4['success']:
    print(f"✓ Fertility Level: {result4['fertility_level']}")
    print(f"  Confidence: {result4['confidence']:.1%}")
    print(f"  Deficiencies: {result4['deficiencies'][0]}")
else:
    print(f"✗ Error: {result4['error']}")


# Summary
print("\n" + "="*80)
print(" "*25 + "TEST SUMMARY")
print("="*80)
print(f"Soil Moisture:        {'✓ PASS' if result1['success'] else '✗ FAIL'}")
print(f"Crop Nutrient:        {'✓ PASS' if result2['success'] else '✗ FAIL'}")
print(f"Crop Climate:         {'✓ PASS' if result3['success'] else '✗ FAIL'}")
print(f"Soil Fertility:       {'✓ PASS' if result4['success'] else '✗ FAIL'}")
print("="*80)

all_passed = all([result1['success'], result2['success'], result3['success'], result4['success']])
if all_passed:
    print("\n🎉 ALL TESTS PASSED! Models are ready for integration.")
    print("\n📝 Next Steps:")
    print("  1. Restart your backend: python src/main.py")
    print("  2. Test queries like:")
    print("     • 'Check soil moisture: temp 30°C, pressure 1013, altitude 500, moisture 300'")
    print("     • 'Recommend crop for soil with N=200, P=50, K=300, pH=6.5, EC=1.2'")
    print("     • 'Which crop for 25°C, 75% humidity, 150mm rainfall?'")
    print("     • 'What is my soil fertility with N=180, P=45, pH=6.5?'")
else:
    print("\n⚠️  Some tests failed. Check errors above.")

print("\n" + "="*80)

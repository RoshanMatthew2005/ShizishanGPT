"""
Test Improved Yield Prediction with Natural Language Parsing
"""
from src.model_tools.yield_tool import YieldTool

def test_yield_tool():
    print("\n" + "="*70)
    print("TESTING IMPROVED YIELD PREDICTION TOOL")
    print("="*70)
    
    tool = YieldTool()
    
    # Test 1: Natural language query
    print("\n🧪 Test 1: Natural Language Query")
    print("Query: 'Predict yield for wheat in Punjab with 800mm rainfall'")
    result1 = tool.run(query="Predict yield for wheat in Punjab with 800mm rainfall")
    print(f"Success: {result1.get('success')}")
    if result1.get('success'):
        print(f"Prediction: {result1['prediction']:.2f} {result1['unit']}")
        print(f"Crop: {result1.get('crop')}")
        print(f"State: {result1.get('state')}")
        print(f"Season: {result1.get('season')}")
        print(f"Inputs: {result1.get('inputs')}")
    else:
        print(f"Error: {result1.get('error')}")
    
    # Test 2: Different crop and state
    print("\n🧪 Test 2: Rice in West Bengal")
    print("Query: 'What is the expected yield for rice in West Bengal with 1200mm rainfall'")
    result2 = tool.run(query="What is the expected yield for rice in West Bengal with 1200mm rainfall")
    print(f"Success: {result2.get('success')}")
    if result2.get('success'):
        print(f"Prediction: {result2['prediction']:.2f} {result2['unit']}")
        print(f"Crop: {result2.get('crop')}")
        print(f"State: {result2.get('state')}")
    
    # Test 3: Maize in Karnataka
    print("\n🧪 Test 3: Maize in Karnataka during Kharif")
    print("Query: 'Predict maize yield in Karnataka kharif season 600mm'")
    result3 = tool.run(query="Predict maize yield in Karnataka kharif season 600mm rainfall")
    print(f"Success: {result3.get('success')}")
    if result3.get('success'):
        print(f"Prediction: {result3['prediction']:.2f} {result3['unit']}")
        print(f"Crop: {result3.get('crop')}")
        print(f"State: {result3.get('state')}")
        print(f"Season: {result3.get('season')}")
    
    # Test 4: With explicit parameters
    print("\n🧪 Test 4: Explicit Parameters")
    result4 = tool.run(
        crop_encoded=53,  # wheat
        season_encoded=2,  # rabi
        state_encoded=21,  # punjab
        annual_rainfall=800.0,
        fertilizer=60000.0,
        pesticide=250.0,
        area=1500.0
    )
    print(f"Success: {result4.get('success')}")
    if result4.get('success'):
        print(f"Prediction: {result4['prediction']:.2f} {result4['unit']}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)

if __name__ == "__main__":
    test_yield_tool()

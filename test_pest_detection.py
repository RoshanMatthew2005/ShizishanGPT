"""
Test Pest Detection with Different Query Types
"""
from src.model_tools.pest_tool import PestTool

def test_pest_detection():
    print("\n" + "="*70)
    print("TESTING PEST DETECTION TOOL")
    print("="*70)
    
    tool = PestTool()
    
    # Test 1: No image provided
    print("\n🧪 Test 1: No Image (Should provide guidance)")
    print("Query: 'Detect plant disease'")
    result1 = tool.run(query="Detect plant disease")
    print(f"Success: {result1.get('success')}")
    if not result1.get('success'):
        print(f"Error: {result1.get('error')}")
        if result1.get('guidance'):
            print(f"Guidance: {result1['guidance']['message']}")
            for option in result1['guidance']['options']:
                print(f"  {option}")
    
    # Test 2: Request sample image (tomato)
    print("\n🧪 Test 2: Sample Image Request - Tomato")
    print("Query: 'Analyze sample tomato bacterial spot image'")
    result2 = tool.run(query="Analyze sample tomato bacterial spot image")
    print(f"Success: {result2.get('success')}")
    if result2.get('success'):
        print(f"Image: {result2['image']}")
        print(f"Top Prediction: {result2['top_prediction']}")
        print(f"Confidence: {result2['confidence']:.4f}")
        print("\nAll Predictions:")
        for i, pred in enumerate(result2['all_predictions'], 1):
            print(f"  {i}. {pred['disease']} - {pred['percentage']}")
    else:
        print(f"Error: {result2.get('error')}")
    
    # Test 3: Sample potato disease
    print("\n🧪 Test 3: Sample Image Request - Potato")
    print("Query: 'Show me sample potato late blight detection'")
    result3 = tool.run(query="Show me sample potato late blight detection")
    print(f"Success: {result3.get('success')}")
    if result3.get('success'):
        print(f"Image: {result3['image']}")
        print(f"Top Prediction: {result3['top_prediction']}")
        print(f"Confidence: {result3['confidence']:.4f}")
    else:
        print(f"Error: {result3.get('error')}")
    
    # Test 4: Sample pepper (any disease)
    print("\n🧪 Test 4: Sample Image Request - Pepper (Generic)")
    print("Query: 'Test pest detection with pepper sample'")
    result4 = tool.run(query="Test pest detection with pepper sample")
    print(f"Success: {result4.get('success')}")
    if result4.get('success'):
        print(f"Image: {result4['image']}")
        print(f"Top Prediction: {result4['top_prediction']}")
        print(f"Confidence: {result4['confidence']:.4f}")
    else:
        print(f"Error: {result4.get('error')}")
    
    # Test 5: Direct image path
    print("\n🧪 Test 5: Direct Image Path")
    import glob
    sample_files = glob.glob("Data/images/PlantVillage/Potato___healthy/*.jpg")
    if sample_files:
        sample_path = sample_files[0]
        print(f"Image Path: {sample_path}")
        result5 = tool.run(image_path=sample_path)
        print(f"Success: {result5.get('success')}")
        if result5.get('success'):
            print(f"Top Prediction: {result5['top_prediction']}")
            print(f"Confidence: {result5['confidence']:.4f}")
    else:
        print("No sample images found")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)

if __name__ == "__main__":
    test_pest_detection()

"""
Test image upload to middleware
"""
import requests

# Find a sample image
import glob
sample_images = glob.glob("Data/images/PlantVillage/Pepper__bell___healthy/*.jpg")

if sample_images:
    sample_path = sample_images[0]
    print(f"Testing with: {sample_path}")
    
    # Test upload
    with open(sample_path, 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        data = {'top_k': 3}
        
        try:
            response = requests.post('http://localhost:5000/detect_pest', 
                                   files=files, data=data, timeout=30)
            print(f"\nStatus: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
else:
    print("No sample images found")

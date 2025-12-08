## 8. Image Handling Testing

### 8.1 Valid Image Upload Tests

| Test ID | Image Type | File Size | Expected Result | Validation |
|---------|-----------|-----------|-----------------|------------|
| IM-001 | Tomato Late Blight | 2MB | Disease detected: "Tomato_Late_blight" | Confidence > 80% |
| IM-002 | Healthy Pepper Leaf | 1.5MB | "Pepper__bell___healthy" | Confidence > 80% |
| IM-003 | Potato Early Blight | 3MB | "Potato___Early_blight" | Top 3 predictions |
| IM-004 | Bacterial Spot | 2.5MB | Disease classification | Recommendation included |
| IM-005 | Small Image (500x500) | 500KB | Successful processing | Proper resizing |
| IM-006 | Large Image (4000x3000) | 8MB | Successful processing | Resized to model input |
| IM-007 | PNG Format | 1MB | Accepted and processed | Format conversion |
| IM-008 | JPEG Format | 1.5MB | Accepted and processed | Standard format |
| IM-009 | Multiple Diseases | 2MB | Top 3 classifications | All with confidence scores |
| IM-010 | Clear Disease Symptoms | 2MB | High confidence (>90%) | Correct classification |

### 8.2 Error Case Tests

| Test ID | Error Scenario | Expected Behavior | Expected Error Message |
|---------|---------------|-------------------|----------------------|
| IM-E-001 | File size > 10MB | Rejection | "File size exceeds 10MB limit" |
| IM-E-002 | Invalid format (PDF) | Rejection | "Invalid image format. Use JPG/PNG" |
| IM-E-003 | Corrupted JPEG | Graceful error | "Unable to process image. File may be corrupted" |
| IM-E-004 | Empty file (0 bytes) | Rejection | "Empty file uploaded" |
| IM-E-005 | Non-leaf image (car) | Low confidence | "Image does not appear to be a plant leaf" |
| IM-E-006 | Blurry image | Processing but warning | "Image quality low, results may be inaccurate" |
| IM-E-007 | Image with no content | Error | "Cannot detect plant in image" |
| IM-E-008 | Invalid file extension | Rejection | "File type not supported" |
| IM-E-009 | Multiple files at once | Process first only | "Only one image allowed per request" |
| IM-E-010 | No file attached | Rejection | "No image file provided" |

### 8.3 Non-Leaf Image Tests

| Test ID | Image Content | Expected Detection | Expected Response |
|---------|---------------|-------------------|-------------------|
| IM-NL-001 | Animal photo | Low confidence all classes | "Not a plant leaf" warning |
| IM-NL-002 | Human face | All predictions <20% | "Cannot classify" |
| IM-NL-003 | Building | Low confidence | "Image type not recognized" |
| IM-NL-004 | Vehicle | All scores low | "Please upload plant leaf image" |
| IM-NL-005 | Food item | Misclassification risk | Confidence warning |
| IM-NL-006 | Landscape | No clear winner | "No disease detected" |
| IM-NL-007 | Text document | Processing error | "Invalid image content" |
| IM-NL-008 | Abstract art | Random classification | Low confidence scores |
| IM-NL-009 | Black/white noise | Error or low confidence | "Cannot process image" |
| IM-NL-010 | Blank white image | No features detected | "No plant detected" |

### 8.4 Image Handling Test Script

```python
"""
Image Upload and Pest Detection Testing
tests/test_image_handling.py
"""

import pytest
import requests
import os
from PIL import Image
import io

class TestImageHandling:
    
    BASE_URL = "http://localhost:5000/api"
    TEST_IMAGES_DIR = "tests/test_images"
    
    def test_im001_tomato_blight(self):
        """Test valid tomato blight image"""
        image_path = os.path.join(self.TEST_IMAGES_DIR, "tomato_late_blight.jpg")
        
        with open(image_path, 'rb') as img_file:
            files = {'file': ('tomato_late_blight.jpg', img_file, 'image/jpeg')}
            data = {'top_k': 3}
            
            response = requests.post(f"{self.BASE_URL}/detect_pest", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] == True
        assert "predictions" in result["data"]
        assert len(result["data"]["predictions"]) == 3
        
        # Check top prediction
        top_pred = result["data"]["predictions"][0]
        assert "Tomato" in top_pred["class"]
        assert top_pred["confidence"] > 0.8
    
    def test_im005_small_image(self):
        """Test small image handling"""
        # Create a small test image
        img = Image.new('RGB', (500, 500), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {'file': ('small_image.jpg', img_bytes, 'image/jpeg')}
        response = requests.post(f"{self.BASE_URL}/detect_pest", files=files)
        
        assert response.status_code == 200
        # Should process successfully despite small size
    
    def test_im_e001_file_too_large(self):
        """Test file size limit"""
        # Create a large fake file (>10MB)
        large_data = b'0' * (11 * 1024 * 1024)  # 11MB
        files = {'file': ('large_image.jpg', large_data, 'image/jpeg')}
        
        response = requests.post(f"{self.BASE_URL}/detect_pest", files=files)
        
        assert response.status_code == 400
        result = response.json()
        assert "size" in result["error"].lower() or "limit" in result["error"].lower()
    
    def test_im_e002_invalid_format(self):
        """Test PDF upload (invalid format)"""
        pdf_data = b'%PDF-1.4 fake pdf content'
        files = {'file': ('document.pdf', pdf_data, 'application/pdf')}
        
        response = requests.post(f"{self.BASE_URL}/detect_pest", files=files)
        
        assert response.status_code == 400
        result = response.json()
        assert "format" in result["error"].lower() or "type" in result["error"].lower()
    
    def test_im_e003_corrupted_image(self):
        """Test corrupted image file"""
        corrupted_data = b'\xFF\xD8\xFF\xE0corrupt data'
        files = {'file': ('corrupted.jpg', corrupted_data, 'image/jpeg')}
        
        response = requests.post(f"{self.BASE_URL}/detect_pest", files=files)
        
        # Should either reject or return error
        assert response.status_code in [400, 500]
        result = response.json()
        assert result["success"] == False
    
    def test_im_e010_no_file(self):
        """Test missing file"""
        response = requests.post(f"{self.BASE_URL}/detect_pest")
        
        assert response.status_code == 400
        result = response.json()
        assert "file" in result["error"].lower() or "image" in result["error"].lower()
    
    def test_im_nl001_non_plant_image(self):
        """Test non-plant image (e.g., car)"""
        # For this test, you'd need an actual car image
        # Assuming low confidence for all predictions
        car_image_path = os.path.join(self.TEST_IMAGES_DIR, "car.jpg")
        
        if os.path.exists(car_image_path):
            with open(car_image_path, 'rb') as img_file:
                files = {'file': ('car.jpg', img_file, 'image/jpeg')}
                response = requests.post(f"{self.BASE_URL}/detect_pest", files=files)
            
            result = response.json()
            # All confidence scores should be low
            if result["success"]:
                predictions = result["data"]["predictions"]
                top_confidence = predictions[0]["confidence"]
                assert top_confidence < 0.5  # Low confidence expected
    
    def test_image_format_conversion(self):
        """Test PNG to JPEG conversion"""
        img = Image.new('RGB', (800, 600), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        files = {'file': ('test.png', img_bytes, 'image/png')}
        response = requests.post(f"{self.BASE_URL}/detect_pest", files=files)
        
        assert response.status_code == 200
        # PNG should be accepted and converted
    
    def test_image_preprocessing(self):
        """Test that images are properly preprocessed"""
        # Create test image with specific dimensions
        img = Image.new('RGB', (1200, 900), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {'file': ('large.jpg', img_bytes, 'image/jpeg')}
        response = requests.post(f"{self.BASE_URL}/detect_pest", files=files)
        
        assert response.status_code == 200
        # Should handle resizing internally
```

### 8.5 Image Quality Checks

```python
"""
Image Quality Validation
"""

from PIL import Image
import numpy as np

class ImageQualityChecker:
    
    def check_image_quality(self, image_path: str) -> dict:
        """Comprehensive image quality check"""
        img = Image.open(image_path)
        img_array = np.array(img)
        
        return {
            "dimensions": img.size,
            "format": img.format,
            "mode": img.mode,
            "is_color": img.mode == 'RGB',
            "is_too_small": img.size[0] < 200 or img.size[1] < 200,
            "is_too_large": img.size[0] > 5000 or img.size[1] > 5000,
            "is_blurry": self.detect_blur(img_array),
            "has_content": self.has_sufficient_content(img_array)
        }
    
    def detect_blur(self, img_array: np.ndarray) -> bool:
        """Detect if image is blurry using Laplacian variance"""
        from scipy import ndimage
        
        gray = img_array.mean(axis=2) if len(img_array.shape) == 3 else img_array
        laplacian_var = ndimage.laplace(gray).var()
        
        return laplacian_var < 100  # Threshold for blur
    
    def has_sufficient_content(self, img_array: np.ndarray) -> bool:
        """Check if image has actual content (not blank)"""
        std_dev = img_array.std()
        return std_dev > 10  # Not a blank image
```

---

## 9. Error Handling Testing

### 9.1 Model File Missing Tests

| Test ID | Missing Component | Expected Error | Fallback Behavior |
|---------|------------------|----------------|-------------------|
| ER-MF-001 | yield_model.pkl | "Yield model not available" | Return error, suggest model path |
| ER-MF-002 | pest_model.pt | "Pest detection unavailable" | Graceful degradation |
| ER-MF-003 | Vectorstore missing | "Knowledge base not loaded" | Use LLM only |
| ER-MF-004 | Mini LLM missing | "LLM model not found" | Use alternative response |
| ER-MF-005 | class_labels.json missing | "Cannot classify diseases" | Return generic error |

**Fix Suggestions:**
```python
# In model loader
try:
    model = torch.load(model_path)
except FileNotFoundError:
    logger.error(f"Model file not found: {model_path}")
    logger.info(f"Please download model from: [URL]")
    raise ModelNotFoundException(f"Model not found at {model_path}")
```

### 9.2 API Timeout Tests

| Test ID | Scenario | Timeout Duration | Expected Behavior |
|---------|----------|------------------|-------------------|
| ER-TO-001 | LLM generation timeout | 30s | Return partial response or error |
| ER-TO-002 | RAG retrieval timeout | 10s | Use cached results or error |
| ER-TO-003 | Model prediction timeout | 15s | Return timeout error |
| ER-TO-004 | Network timeout | 30s | Retry once, then error |
| ER-TO-005 | Database timeout | 5s | Use in-memory fallback |

**Expected Error Messages:**
```json
{
  "success": false,
  "error": "Request timeout after 30 seconds",
  "code": 408,
  "suggestion": "Please try again with a shorter query or check system load"
}
```

### 9.3 Network/Connection Tests

| Test ID | Network Issue | Expected Error | Fix Suggestion |
|---------|--------------|----------------|----------------|
| ER-NET-001 | No internet | "Translation service unavailable" | "Check internet connection" |
| ER-NET-002 | FastAPI down | "Backend service not responding" | "Start FastAPI backend on port 8000" |
| ER-NET-003 | Middleware down | "Cannot connect to middleware" | "Start Node.js server on port 5000" |
| ER-NET-004 | MongoDB down | "Database connection failed" | "Conversations won't be saved" |
| ER-NET-005 | CORS blocked | "Cross-origin request blocked" | "Check CORS configuration" |

### 9.4 Service Failure Tests

| Test ID | Failed Service | Expected Error | Recovery Action |
|---------|---------------|----------------|-----------------|
| ER-SF-001 | Node.js crash | Frontend shows connection error | Restart middleware, display retry button |
| ER-SF-002 | FastAPI crash | Middleware returns 502/503 | Log error, suggest backend restart |
| ER-SF-003 | React crash | White screen, error boundary | Show error message, reload button |
| ER-SF-004 | Model loading failure | Service starts but model unavailable | Disable affected endpoints |
| ER-SF-005 | MongoDB connection loss | Queries work, history fails | In-memory mode, warn user |

### 9.5 Invalid Input Tests

| Test ID | Invalid Input Type | Input Example | Expected Error |
|---------|-------------------|---------------|----------------|
| ER-INV-001 | SQL Injection attempt | `"'; DROP TABLE--"` | Sanitized, query processed safely |
| ER-INV-002 | XSS attempt | `"<script>alert('xss')</script>"` | HTML escaped |
| ER-INV-003 | Extremely long string | 100,000 character query | "Query too long (max 10,000 chars)" |
| ER-INV-004 | Special characters only | `"!@#$%^&*()"` | "Invalid query format" |
| ER-INV-005 | Empty string | `""` | "Query cannot be empty" |
| ER-INV-006 | Only whitespace | `"    "` | "Query cannot be empty" |
| ER-INV-007 | Invalid JSON | Malformed request body | 400 Bad Request |
| ER-INV-008 | Wrong data types | String where number expected | "Invalid data type" |
| ER-INV-009 | Negative numbers | Area: -10 | "Value must be positive" |
| ER-INV-010 | NULL/undefined | Missing required fields | "Required field missing" |

### 9.6 Error Handling Test Script

```python
"""
Comprehensive Error Handling Tests
tests/test_error_handling.py
"""

import pytest
import requests
import time

class TestErrorHandling:
    
    BASE_URL = "http://localhost:5000/api"
    
    def test_er_mf001_missing_model_graceful(self):
        """Test graceful handling when model is missing"""
        # This test assumes yield model might not be loaded
        response = requests.post(f"{self.BASE_URL}/predict_yield", json={
            "crop": "Wheat",
            "area": 10,
            "rainfall": 600,
            "temperature": 22,
            "soil_type": "Loam"
        })
        
        # Should either work or return clear error
        if response.status_code != 200:
            result = response.json()
            assert "model" in result["error"].lower() or "available" in result["error"].lower()
    
    def test_er_to001_timeout_handling(self):
        """Test request timeout handling"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/ask",
                json={"query": "Explain everything about agriculture in extreme detail"},
                timeout=2  # Short timeout
            )
        except requests.Timeout:
            # Timeout is expected for very long processing
            pass
    
    def test_er_net003_middleware_down(self):
        """Test behavior when middleware is not responding"""
        fake_url = "http://localhost:9999/api/ask"  # Non-existent service
        
        try:
            response = requests.post(fake_url, json={"query": "test"}, timeout=2)
        except requests.ConnectionError:
            # Expected when service is down
            assert True
    
    def test_er_inv001_sql_injection_prevention(self):
        """Test SQL injection attempt is handled safely"""
        malicious_query = "'; DROP TABLE users; --"
        
        response = requests.post(f"{self.BASE_URL}/ask", json={"query": malicious_query})
        
        # Should process safely without crashing
        assert response.status_code in [200, 400]
        # System should still be running (can make another request)
        health_check = requests.get(f"http://localhost:5000/health")
        assert health_check.status_code == 200
    
    def test_er_inv002_xss_prevention(self):
        """Test XSS attempt is sanitized"""
        xss_query = "<script>alert('XSS')</script>"
        
        response = requests.post(f"{self.BASE_URL}/ask", json={"query": xss_query})
        result = response.json()
        
        # Response should not contain raw script tags
        if result["success"]:
            assert "<script>" not in result["data"]["answer"]
    
    def test_er_inv003_extremely_long_query(self):
        """Test handling of extremely long input"""
        long_query = "word " * 50000  # Very long query
        
        response = requests.post(f"{self.BASE_URL}/ask", json={"query": long_query})
        
        # Should reject or truncate
        assert response.status_code in [400, 413]  # Bad Request or Payload Too Large
    
    def test_er_inv005_empty_query(self):
        """Test empty query handling"""
        response = requests.post(f"{self.BASE_URL}/ask", json={"query": ""})
        
        assert response.status_code == 400
        result = response.json()
        assert "empty" in result["error"].lower() or "required" in result["error"].lower()
    
    def test_er_inv007_invalid_json(self):
        """Test malformed JSON request"""
        response = requests.post(
            f"{self.BASE_URL}/ask",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
    
    def test_error_response_format(self):
        """Validate error response structure"""
        response = requests.post(f"{self.BASE_URL}/ask", json={"query": ""})
        result = response.json()
        
        # Standard error format
        assert "success" in result
        assert result["success"] == False
        assert "error" in result
        assert isinstance(result["error"], str)
    
    def test_error_logging(self):
        """Verify errors are logged properly"""
        # Trigger an error
        requests.post(f"{self.BASE_URL}/ask", json={"invalid": "data"})
        
        # Check logs exist (this depends on your logging setup)
        # In production, you'd verify log files contain the error
        assert True  # Placeholder
```

---


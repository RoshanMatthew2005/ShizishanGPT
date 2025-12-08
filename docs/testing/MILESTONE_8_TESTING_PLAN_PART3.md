## 4. Yield Model Testing

### 4.1 Valid Input Tests

| Test ID | Crop | Area (ha) | Rainfall (mm) | Temperature (°C) | Soil Type | Expected Yield Range (tons/ha) |
|---------|------|-----------|---------------|------------------|-----------|-------------------------------|
| YM-001 | Wheat | 10 | 600 | 22 | Loam | 3.5 - 5.5 |
| YM-002 | Rice | 15 | 1200 | 28 | Clay | 4.0 - 6.0 |
| YM-003 | Maize | 8 | 800 | 25 | Sandy Loam | 5.0 - 7.0 |
| YM-004 | Cotton | 12 | 700 | 30 | Black Soil | 1.5 - 2.5 |
| YM-005 | Soybean | 20 | 900 | 26 | Loam | 2.0 - 3.5 |
| YM-006 | Sugarcane | 5 | 1500 | 27 | Clay | 60 - 80 |
| YM-007 | Potato | 3 | 650 | 20 | Sandy Loam | 20 - 30 |
| YM-008 | Tomato | 2 | 700 | 24 | Loam | 40 - 60 |
| YM-009 | Onion | 4 | 600 | 23 | Alluvial | 15 - 25 |
| YM-010 | Groundnut | 10 | 750 | 28 | Sandy | 1.5 - 2.5 |

### 4.2 Edge Case Tests

| Test ID | Scenario | Input Values | Expected Behavior |
|---------|----------|--------------|-------------------|
| YM-E-001 | Minimum rainfall | Rainfall = 200mm | Low yield prediction with warning |
| YM-E-002 | Maximum rainfall | Rainfall = 3000mm | Adjusted yield, flood warning |
| YM-E-003 | Very high temperature | Temperature = 45°C | Reduced yield, heat stress warning |
| YM-E-004 | Very low temperature | Temperature = 5°C | Minimal/zero yield, frost warning |
| YM-E-005 | Tiny area | Area = 0.1 ha | Valid prediction, small output |
| YM-E-006 | Large area | Area = 10000 ha | Valid prediction, scaled output |
| YM-E-007 | Border values | All parameters at model limits | Valid prediction |
| YM-E-008 | Desert conditions | Rainfall=50mm, Temp=42°C | Very low yield + irrigation recommendation |
| YM-E-009 | Monsoon excess | Rainfall=2500mm, high humidity | Moderate yield + drainage advice |
| YM-E-010 | Optimal conditions | All parameters ideal | Maximum yield prediction |

### 4.3 Invalid Data Tests

| Test ID | Invalid Input | Expected Error Message | HTTP Code |
|---------|---------------|------------------------|-----------|
| YM-I-001 | Negative area | "Area must be positive" | 400 |
| YM-I-002 | Negative rainfall | "Rainfall cannot be negative" | 400 |
| YM-I-003 | Temperature > 60°C | "Temperature out of realistic range" | 400 |
| YM-I-004 | Temperature < -20°C | "Temperature out of realistic range" | 400 |
| YM-I-005 | Missing crop type | "Crop type is required" | 400 |
| YM-I-006 | Invalid crop name | "Unknown crop type" | 400 |
| YM-I-007 | Area = 0 | "Area must be greater than zero" | 400 |
| YM-I-008 | String instead of number | "Invalid data type for area" | 400 |
| YM-I-009 | Missing required fields | "Missing required parameters" | 400 |
| YM-I-010 | Null values | "Null values not allowed" | 400 |

### 4.4 Yield Model Test Script

```python
"""
Yield Model Comprehensive Testing
tests/test_yield_model.py
"""

import pytest
import requests
import json

class TestYieldModel:
    
    BASE_URL = "http://localhost:5000/api"
    
    def test_ym001_wheat_prediction(self):
        """Test wheat yield prediction"""
        payload = {
            "crop": "Wheat",
            "area": 10,
            "rainfall": 600,
            "temperature": 22,
            "soil_type": "Loam"
        }
        
        response = requests.post(f"{self.BASE_URL}/predict_yield", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "yield" in data["data"]
        
        yield_value = data["data"]["yield"]
        assert 3.5 <= yield_value <= 5.5  # Expected range
    
    def test_ym002_rice_prediction(self):
        """Test rice yield prediction"""
        payload = {
            "crop": "Rice",
            "area": 15,
            "rainfall": 1200,
            "temperature": 28,
            "soil_type": "Clay"
        }
        
        response = requests.post(f"{self.BASE_URL}/predict_yield", json=payload)
        data = response.json()
        
        yield_value = data["data"]["yield"]
        assert 4.0 <= yield_value <= 6.0
    
    def test_ym_e001_minimum_rainfall(self):
        """Test prediction with minimum rainfall"""
        payload = {
            "crop": "Wheat",
            "area": 10,
            "rainfall": 200,  # Very low
            "temperature": 22,
            "soil_type": "Loam"
        }
        
        response = requests.post(f"{self.BASE_URL}/predict_yield", json=payload)
        data = response.json()
        
        # Should predict low yield
        assert data["data"]["yield"] < 2.0
        # Should include warning
        if "warnings" in data["data"]:
            assert any("rainfall" in w.lower() for w in data["data"]["warnings"])
    
    def test_ym_e003_high_temperature(self):
        """Test prediction with extreme heat"""
        payload = {
            "crop": "Wheat",
            "area": 10,
            "rainfall": 600,
            "temperature": 45,  # Very high
            "soil_type": "Loam"
        }
        
        response = requests.post(f"{self.BASE_URL}/predict_yield", json=payload)
        data = response.json()
        
        # Yield should be reduced
        assert data["data"]["yield"] < 3.0
    
    def test_ym_i001_negative_area(self):
        """Test invalid negative area"""
        payload = {
            "crop": "Wheat",
            "area": -10,  # Invalid
            "rainfall": 600,
            "temperature": 22,
            "soil_type": "Loam"
        }
        
        response = requests.post(f"{self.BASE_URL}/predict_yield", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert data["success"] == False
        assert "area" in data["error"].lower()
    
    def test_ym_i006_invalid_crop(self):
        """Test unknown crop type"""
        payload = {
            "crop": "InvalidCrop123",
            "area": 10,
            "rainfall": 600,
            "temperature": 22,
            "soil_type": "Loam"
        }
        
        response = requests.post(f"{self.BASE_URL}/predict_yield", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "crop" in data["error"].lower() or "unknown" in data["error"].lower()
    
    def test_ym_i009_missing_fields(self):
        """Test missing required parameters"""
        payload = {
            "crop": "Wheat",
            "area": 10
            # Missing rainfall, temperature, soil_type
        }
        
        response = requests.post(f"{self.BASE_URL}/predict_yield", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "missing" in data["error"].lower() or "required" in data["error"].lower()
    
    def test_ym_output_format(self):
        """Validate response format"""
        payload = {
            "crop": "Wheat",
            "area": 10,
            "rainfall": 600,
            "temperature": 22,
            "soil_type": "Loam"
        }
        
        response = requests.post(f"{self.BASE_URL}/predict_yield", json=payload)
        data = response.json()
        
        # Check structure
        assert "success" in data
        assert "data" in data
        assert "yield" in data["data"]
        assert "unit" in data["data"]
        
        # Check data types
        assert isinstance(data["data"]["yield"], (int, float))
        assert isinstance(data["data"]["unit"], str)
    
    def test_ym_performance(self):
        """Test response time"""
        import time
        
        payload = {
            "crop": "Wheat",
            "area": 10,
            "rainfall": 600,
            "temperature": 22,
            "soil_type": "Loam"
        }
        
        start = time.time()
        response = requests.post(f"{self.BASE_URL}/predict_yield", json=payload)
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 2.0  # Should respond within 2 seconds
```

---

## 5. Weather Model Testing

### 5.1 Weather Scenario Tests

| Test ID | Scenario | Temperature (°C) | Rainfall (mm) | Humidity (%) | Expected Impact | Recommendation |
|---------|----------|------------------|---------------|--------------|-----------------|----------------|
| WM-001 | Drought | 38 | 100 | 30 | Severe yield reduction | Irrigation urgently needed |
| WM-002 | Heavy Rain | 26 | 2000 | 90 | Moderate reduction, disease risk | Install drainage, fungicide |
| WM-003 | High Humidity | 28 | 800 | 95 | Disease outbreak risk | Preventive spray, ventilation |
| WM-004 | Heat Wave | 42 | 400 | 40 | Crop stress, wilting | Mulching, shade nets |
| WM-005 | Cold Stress | 8 | 300 | 60 | Frost damage risk | Cover crops, smoke method |
| WM-006 | Optimal Monsoon | 27 | 1200 | 75 | Positive impact | Normal cultivation |
| WM-007 | Erratic Rain | 29 | 50-200 (variable) | 65 | Uneven growth | Supplemental irrigation |
| WM-008 | Cyclone Conditions | 30 | 3000 | 98 | Severe damage | Harvest early, secure structures |
| WM-009 | Dry Spell | 35 | 200 | 35 | Water stress | Drip irrigation, drought-resistant varieties |
| WM-010 | Foggy Conditions | 15 | 600 | 100 | Disease, poor pollination | Improve air circulation |

### 5.2 Weather Model Edge Cases

| Test ID | Edge Condition | Input Parameters | Expected Output |
|---------|----------------|------------------|-----------------|
| WM-E-001 | Zero rainfall | Rain=0mm | Critical drought warning |
| WM-E-002 | Extreme heat | Temp=50°C | Emergency heat stress alert |
| WM-E-003 | Freezing | Temp=-5°C | Frost warning, crop damage high |
| WM-E-004 | Flooding | Rain=5000mm | Flood alert, total loss risk |
| WM-E-005 | 100% humidity | Humidity=100% | Maximum disease risk |
| WM-E-006 | Desert dry | Humidity=10% | Extreme water requirement |
| WM-E-007 | Rapid temperature swing | Day=40°C, Night=15°C | Stress warning |
| WM-E-008 | Hail conditions | Rain=500mm in 1 hour | Physical damage alert |
| WM-E-009 | Extended drought | No rain for 60 days | Critical intervention needed |
| WM-E-010 | Ideal conditions | All parameters optimal | Maximum yield potential |

### 5.3 Weather Model Error Handling

| Test ID | Invalid Input | Expected Error | HTTP Code |
|---------|---------------|----------------|-----------|
| WM-I-001 | Temp > 60°C | "Temperature unrealistic" | 400 |
| WM-I-002 | Temp < -30°C | "Temperature too low" | 400 |
| WM-I-003 | Negative rainfall | "Rainfall cannot be negative" | 400 |
| WM-I-004 | Humidity > 100% | "Humidity must be 0-100%" | 400 |
| WM-I-005 | Humidity < 0% | "Humidity must be 0-100%" | 400 |
| WM-I-006 | Missing parameters | "Required weather data missing" | 400 |
| WM-I-007 | String values | "Invalid data type" | 400 |
| WM-I-008 | Future date | "Historical data only" | 400 |
| WM-I-009 | Invalid location | "Location not supported" | 400 |
| WM-I-010 | Null values | "Null values not allowed" | 400 |

### 5.4 Weather Model Test Script

```python
"""
Weather Model Testing
tests/test_weather_model.py
"""

import pytest
import requests

class TestWeatherModel:
    
    BASE_URL = "http://localhost:5000/api"
    
    def test_wm001_drought_scenario(self):
        """Test drought condition impact"""
        payload = {
            "temperature": 38,
            "rainfall": 100,
            "humidity": 30,
            "crop": "Wheat"
        }
        
        response = requests.post(f"{self.BASE_URL}/analyze_weather", json=payload)
        data = response.json()
        
        assert data["success"] == True
        assert data["data"]["impact"] in ["severe", "high", "critical"]
        assert "irrigation" in data["data"]["recommendation"].lower()
    
    def test_wm002_heavy_rain(self):
        """Test heavy rainfall impact"""
        payload = {
            "temperature": 26,
            "rainfall": 2000,
            "humidity": 90,
            "crop": "Rice"
        }
        
        response = requests.post(f"{self.BASE_URL}/analyze_weather", json=payload)
        data = response.json()
        
        # Should warn about disease or drainage
        rec = data["data"]["recommendation"].lower()
        assert any(kw in rec for kw in ["drainage", "disease", "fungicide"])
    
    def test_wm004_heat_wave(self):
        """Test extreme heat conditions"""
        payload = {
            "temperature": 42,
            "rainfall": 400,
            "humidity": 40,
            "crop": "Maize"
        }
        
        response = requests.post(f"{self.BASE_URL}/analyze_weather", json=payload)
        data = response.json()
        
        assert "stress" in data["data"]["impact"].lower() or "heat" in data["data"]["recommendation"].lower()
    
    def test_wm_e002_extreme_heat(self):
        """Test temperature at upper limit"""
        payload = {
            "temperature": 50,
            "rainfall": 200,
            "humidity": 30,
            "crop": "Wheat"
        }
        
        response = requests.post(f"{self.BASE_URL}/analyze_weather", json=payload)
        data = response.json()
        
        # Should indicate severe stress
        assert data["data"]["severity"] in ["high", "critical", "severe"]
    
    def test_wm_i001_temp_too_high(self):
        """Test invalid temperature"""
        payload = {
            "temperature": 70,  # Unrealistic
            "rainfall": 600,
            "humidity": 60,
            "crop": "Wheat"
        }
        
        response = requests.post(f"{self.BASE_URL}/analyze_weather", json=payload)
        assert response.status_code == 400
    
    def test_wm_i004_humidity_invalid(self):
        """Test humidity out of range"""
        payload = {
            "temperature": 25,
            "rainfall": 600,
            "humidity": 150,  # Invalid
            "crop": "Wheat"
        }
        
        response = requests.post(f"{self.BASE_URL}/analyze_weather", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "humidity" in data["error"].lower()
```

---


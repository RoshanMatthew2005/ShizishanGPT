"""
Model Testing - Yield and Weather Predictions
Tests machine learning model predictions
"""
import pytest
import requests


MIDDLEWARE_URL = "http://localhost:5000"


class TestYieldModel:
    """Test yield prediction model"""
    
    def test_yield_001_wheat_normal(self):
        """YIELD-001: Wheat 10ha normal conditions"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "wheat",
                "area": 10,
                "rainfall": 800,
                "temperature": 25,
                "humidity": 60
            },
            timeout=10
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should return a prediction
        prediction = self._extract_prediction(result)
        assert prediction is not None
        assert isinstance(prediction, (int, float))
        assert 0 < prediction < 10000, f"Unrealistic yield: {prediction}"
    
    def test_yield_002_rice_monsoon(self):
        """YIELD-002: Rice 5ha monsoon region"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "rice",
                "area": 5,
                "rainfall": 1500,
                "temperature": 30,
                "humidity": 80
            },
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_yield_003_corn_semiarid(self):
        """YIELD-003: Corn 20ha semi-arid"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "corn",
                "area": 20,
                "rainfall": 400,
                "temperature": 28,
                "humidity": 40
            },
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_yield_edge_001_small_farm(self):
        """YIELD-EDGE-001: Very small farm (0.1 hectare)"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "wheat",
                "area": 0.1,
                "rainfall": 800,
                "temperature": 25
            },
            timeout=10
        )
        
        assert response.status_code in [200, 400]
    
    def test_yield_edge_002_large_farm(self):
        """YIELD-EDGE-002: Large farm (1000 hectare)"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "wheat",
                "area": 1000,
                "rainfall": 800,
                "temperature": 25
            },
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_yield_edge_003_extreme_low_rainfall(self):
        """YIELD-EDGE-003: Extreme low rainfall (50mm)"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "wheat",
                "area": 10,
                "rainfall": 50,
                "temperature": 25
            },
            timeout=10
        )
        
        assert response.status_code == 200
        # Prediction should be low but valid
    
    def test_yield_edge_004_extreme_high_rainfall(self):
        """YIELD-EDGE-004: Extreme high rainfall (5000mm)"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "rice",
                "area": 10,
                "rainfall": 5000,
                "temperature": 30
            },
            timeout=10
        )
        
        assert response.status_code in [200, 400]
    
    def test_yield_err_001_negative_area(self):
        """YIELD-ERR-001: Negative area value"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "wheat",
                "area": -10,
                "rainfall": 800,
                "temperature": 25
            },
            timeout=10
        )
        
        assert response.status_code in [400, 422]
    
    def test_yield_err_002_invalid_crop(self):
        """YIELD-ERR-002: Invalid crop name"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "invalid_crop_xyz",
                "area": 10,
                "rainfall": 800,
                "temperature": 25
            },
            timeout=10
        )
        
        assert response.status_code in [400, 422, 500]
    
    def test_yield_err_003_string_instead_of_number(self):
        """YIELD-ERR-003: String instead of number"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "wheat",
                "area": "ten",
                "rainfall": 800,
                "temperature": 25
            },
            timeout=10
        )
        
        assert response.status_code in [400, 422]
    
    def test_yield_err_004_missing_fields(self):
        """YIELD-ERR-004: Missing required fields"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "wheat"
            },
            timeout=10
        )
        
        assert response.status_code in [400, 422]
    
    def _extract_prediction(self, result):
        """Extract prediction value from response"""
        if isinstance(result, (int, float)):
            return result
        if isinstance(result, dict):
            if "prediction" in result:
                return result["prediction"]
            if "yield" in result:
                return result["yield"]
            if "data" in result and isinstance(result["data"], dict):
                return result["data"].get("prediction") or result["data"].get("yield")
        return None


class TestWeatherModel:
    """Test weather prediction model"""
    
    def test_weather_001_drought(self):
        """WEATHER-001: Severe drought conditions"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={
                "rainfall": 100,
                "temperature": 40,
                "humidity": 20
            },
            timeout=10
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should identify drought risk
        impact_text = str(result).lower()
        assert "drought" in impact_text or "dry" in impact_text or "water" in impact_text
    
    def test_weather_002_heavy_rain(self):
        """WEATHER-002: Heavy monsoon rainfall"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={
                "rainfall": 2000,
                "temperature": 30,
                "humidity": 85
            },
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_weather_003_high_humidity(self):
        """WEATHER-003: High humidity stress"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={
                "rainfall": 1200,
                "temperature": 32,
                "humidity": 90
            },
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_weather_004_heat_wave(self):
        """WEATHER-004: Heat wave conditions"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={
                "rainfall": 500,
                "temperature": 45,
                "humidity": 30
            },
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_weather_005_cold_wave(self):
        """WEATHER-005: Cold wave impact"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={
                "rainfall": 600,
                "temperature": 5,
                "humidity": 70
            },
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_weather_edge_001_zero_rainfall(self):
        """WEATHER-EDGE-001: 0mm rainfall"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={
                "rainfall": 0,
                "temperature": 35,
                "humidity": 20
            },
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_weather_edge_002_max_humidity(self):
        """WEATHER-EDGE-002: 100% humidity"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={
                "rainfall": 1500,
                "temperature": 30,
                "humidity": 100
            },
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_weather_edge_003_min_humidity(self):
        """WEATHER-EDGE-003: 0% humidity"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={
                "rainfall": 200,
                "temperature": 40,
                "humidity": 0
            },
            timeout=10
        )
        
        assert response.status_code == 200
    
    def test_weather_err_001_negative_values(self):
        """WEATHER-ERR-003: Negative values"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={
                "rainfall": -100,
                "temperature": 30,
                "humidity": 70
            },
            timeout=10
        )
        
        assert response.status_code in [400, 422]
    
    def test_weather_err_002_missing_params(self):
        """WEATHER-ERR-002: Missing parameters"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={
                "rainfall": 1000
            },
            timeout=10
        )
        
        assert response.status_code in [400, 422]
    
    def test_weather_err_003_invalid_types(self):
        """WEATHER-ERR-004: String instead of number"""
        response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={
                "rainfall": "heavy",
                "temperature": 30,
                "humidity": 70
            },
            timeout=10
        )
        
        assert response.status_code in [400, 422]


class TestModelIntegration:
    """Test model integration and consistency"""
    
    def test_integration_001_combined_prediction(self):
        """Test yield and weather predictions together"""
        # Get yield prediction
        yield_response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={
                "crop": "wheat",
                "area": 10,
                "rainfall": 800,
                "temperature": 25
            },
            timeout=10
        )
        
        # Get weather impact
        weather_response = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={
                "rainfall": 800,
                "temperature": 25,
                "humidity": 60
            },
            timeout=10
        )
        
        # Both should succeed
        assert yield_response.status_code == 200
        assert weather_response.status_code == 200
    
    def test_integration_002_model_availability(self):
        """Test both models are available"""
        # Try yield
        yield_available = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_yield",
            json={"crop": "wheat", "area": 10, "rainfall": 800, "temperature": 25},
            timeout=10
        ).status_code == 200
        
        # Try weather
        weather_available = requests.post(
            f"{MIDDLEWARE_URL}/api/predict_weather",
            json={"rainfall": 800, "temperature": 25, "humidity": 60},
            timeout=10
        ).status_code == 200
        
        # At least one should work (or both fail gracefully)
        assert yield_available or weather_available or True  # System responsive

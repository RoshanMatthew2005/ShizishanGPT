"""
Crop Climate Recommendation Tool
Recommends crops based on climate conditions (NPK + weather parameters).
"""

import pickle
import numpy as np
import pandas as pd
import re
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class CropClimateTool:
    """Tool for recommending crops based on climate and soil NPK."""
    
    def __init__(self):
        self.name = "crop_climate_recommendation"
        self.description = "Recommends suitable crops based on climate conditions and soil NPK"
        self.model_path = Path("models/crop_climate_model.pkl")
        self.model_data = None
        self.load_model()
        
        # Valid ranges for input parameters
        self.valid_ranges = {
            'N': (0, 200),           # Nitrogen (kg/ha)
            'P': (0, 150),           # Phosphorus (kg/ha)
            'K': (0, 250),           # Potassium (kg/ha)
            'temperature': (5, 50),  # Celsius
            'humidity': (10, 100),   # Percentage
            'ph': (4.0, 9.0),        # pH
            'rainfall': (20, 300)    # mm
        }
    
    def load_model(self):
        """Load the trained crop climate recommendation model."""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    self.model_data = pickle.load(f)
                print(f"✓ Crop climate model loaded from {self.model_path}")
            else:
                print(f"⚠ Model not found at {self.model_path}")
                self.model_data = None
        except Exception as e:
            print(f"❌ Error loading crop climate model: {e}")
            self.model_data = None
    
    def validate_inputs(self, params: Dict[str, Any]) -> tuple[bool, str]:
        """Validate input parameters."""
        required = list(self.valid_ranges.keys())
        
        # Check required fields
        missing = [f for f in required if f not in params]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        # Validate numeric ranges
        for field in required:
            try:
                value = float(params[field])
                min_val, max_val = self.valid_ranges[field]
                if not (min_val <= value <= max_val):
                    return False, f"{field} must be between {min_val} and {max_val}"
            except (ValueError, TypeError):
                return False, f"{field} must be a numeric value"
        
        return True, "Valid"
    
    def predict(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict suitable crop based on climate and soil conditions.
        
        Args:
            params: Dictionary with keys:
                - N, P, K: Soil nutrients (kg/ha)
                - temperature: Average temperature (°C)
                - humidity: Average humidity (%)
                - ph: Soil pH
                - rainfall: Expected rainfall (mm)
        
        Returns:
            Dictionary with crop recommendation and climate analysis
        """
        try:
            # Validate inputs
            is_valid, message = self.validate_inputs(params)
            if not is_valid:
                return {
                    'success': False,
                    'error': message,
                    'timestamp': datetime.now().isoformat()
                }
            
            if not self.model_data:
                return {
                    'success': False,
                    'error': 'Model not loaded. Please train the model first.',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Prepare features (must match training column order)
            features = pd.DataFrame([{
                'N': float(params['N']),
                'P': float(params['P']),
                'K': float(params['K']),
                'temperature': float(params['temperature']),
                'humidity': float(params['humidity']),
                'ph': float(params['ph']),
                'rainfall': float(params['rainfall'])
            }])
            
            # Scale features
            scaler = self.model_data['scaler']
            features_scaled = scaler.transform(features)
            
            # Make prediction
            model = self.model_data['model']
            prediction = model.predict(features_scaled)[0]
            probabilities = model.predict_proba(features_scaled)[0]
            
            # Get class labels
            label_encoder = self.model_data['label_encoder']
            recommended_crop = label_encoder.inverse_transform([prediction])[0]
            
            # Get top 5 recommendations
            top_indices = np.argsort(probabilities)[::-1][:5]
            top_crops = [
                {
                    'crop': label_encoder.inverse_transform([idx])[0],
                    'suitability': float(probabilities[idx])
                }
                for idx in top_indices
            ]
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                recommended_crop,
                params,
                top_crops
            )
            
            return {
                'success': True,
                'recommended_crop': recommended_crop,
                'confidence': float(max(probabilities)),
                'top_5_crops': top_crops,
                'recommendations': recommendations,
                'climate_analysis': self._analyze_climate(params),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Prediction failed: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_climate(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Analyze climate conditions."""
        analysis = {}
        
        temp = params['temperature']
        if temp < 15:
            analysis['temperature'] = f"{temp}°C (Cool climate - suitable for temperate crops)"
        elif temp > 35:
            analysis['temperature'] = f"{temp}°C (Hot climate - suitable for tropical crops)"
        else:
            analysis['temperature'] = f"{temp}°C (Moderate - wide crop selection)"
        
        humidity = params['humidity']
        if humidity < 40:
            analysis['humidity'] = f"{humidity}% (Low - irrigation may be needed)"
        elif humidity > 80:
            analysis['humidity'] = f"{humidity}% (High - watch for fungal diseases)"
        else:
            analysis['humidity'] = f"{humidity}% (Optimal range)"
        
        rainfall = params['rainfall']
        if rainfall < 50:
            analysis['rainfall'] = f"{rainfall}mm (Low - drought-resistant crops recommended)"
        elif rainfall > 200:
            analysis['rainfall'] = f"{rainfall}mm (High - ensure good drainage)"
        else:
            analysis['rainfall'] = f"{rainfall}mm (Adequate for most crops)"
        
        return analysis
    
    def _generate_recommendations(
        self,
        recommended_crop: str,
        params: Dict[str, Any],
        top_crops: list
    ) -> list:
        """Generate crop recommendations and climate management advice."""
        recommendations = []
        
        recommendations.append(f"🌾 Best crop for your climate: {recommended_crop.upper()}")
        recommendations.append(f"Top alternatives: {', '.join([c['crop'] for c in top_crops[1:4]])}")
        
        # Temperature-based advice
        temp = params['temperature']
        if temp < 15:
            recommendations.append("❄️ Cool climate detected - consider wheat, barley, or potato")
        elif temp > 35:
            recommendations.append("☀️ Hot climate - millet, cotton, or sorghum work well")
        
        # Rainfall management
        rainfall = params['rainfall']
        if rainfall < 50:
            recommendations.append("💧 Low rainfall - install drip irrigation system")
            recommendations.append("🌵 Consider drought-resistant crops: pearl millet, chickpea")
        elif rainfall > 200:
            recommendations.append("🌧️ High rainfall - ensure field drainage")
            recommendations.append("🌾 Rice, jute, or banana are suitable for wet conditions")
        
        # Humidity considerations
        humidity = params['humidity']
        if humidity > 80:
            recommendations.append("🍄 High humidity - monitor for fungal diseases")
            recommendations.append("Use fungicide sprays as preventive measure")
        elif humidity < 40:
            recommendations.append("🏜️ Low humidity - mulching recommended to retain moisture")
        
        # Soil pH advice
        ph = params['ph']
        if ph < 5.5:
            recommendations.append("⚗️ Acidic soil - good for tea, coffee, or potato")
        elif ph > 7.5:
            recommendations.append("⚗️ Alkaline soil - suitable for barley, beet, or cotton")
        
        # NPK recommendations
        if params['N'] < 80:
            recommendations.append("🌿 Add nitrogen fertilizer before planting")
        if params['P'] < 40:
            recommendations.append("🌿 Boost phosphorus for better root development")
        if params['K'] < 100:
            recommendations.append("🌿 Apply potassium for improved disease resistance")
        
        return recommendations
    
    def run(self, text: str = "", query: str = "", **kwargs) -> Dict[str, Any]:
        """Run method for ReAct agent compatibility."""
        # Use query text if provided
        query_text = text or query or ""
        
        # Extract parameters from kwargs or parse from text
        if 'params' in kwargs:
            params = kwargs['params']
        else:
            # Parse parameters from text query
            params = self._extract_params_from_text(query_text, kwargs)
        
        return self.predict(params)
    
    def _extract_params_from_text(self, text: str, kwargs: Dict) -> Dict[str, Any]:
        """Extract numerical parameters from query text."""
        params = {}
        text_lower = text.lower()
        
        # Extract N (Nitrogen)
        n_match = re.search(r'\bn\s*[=:]\s*(\d+(?:\.\d+)?)', text_lower)
        params['N'] = float(n_match.group(1)) if n_match else kwargs.get('N', 100)
        
        # Extract P (Phosphorus)
        p_match = re.search(r'\bp\s*[=:]\s*(\d+(?:\.\d+)?)', text_lower)
        params['P'] = float(p_match.group(1)) if p_match else kwargs.get('P', 50)
        
        # Extract K (Potassium)
        k_match = re.search(r'\bk\s*[=:]\s*(\d+(?:\.\d+)?)', text_lower)
        params['K'] = float(k_match.group(1)) if k_match else kwargs.get('K', 150)
        
        # Extract temperature
        temp_match = re.search(r'(\d+(?:\.\d+)?)\s*[°]?c', text_lower)
        if not temp_match:
            temp_match = re.search(r'temperature[:\s]+(\d+(?:\.\d+)?)', text_lower)
        params['temperature'] = float(temp_match.group(1)) if temp_match else kwargs.get('temperature', 25)
        
        # Extract humidity
        humid_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*humidity', text_lower)
        if not humid_match:
            humid_match = re.search(r'humidity[:\s]+(\d+(?:\.\d+)?)', text_lower)
        params['humidity'] = float(humid_match.group(1)) if humid_match else kwargs.get('humidity', 70)
        
        # Extract pH
        ph_match = re.search(r'ph[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['ph'] = float(ph_match.group(1)) if ph_match else kwargs.get('ph', 6.5)
        
        # Extract rainfall
        rain_match = re.search(r'(\d+(?:\.\d+)?)\s*mm\s*rainfall', text_lower)
        if not rain_match:
            rain_match = re.search(r'rainfall[:\s]+(\d+(?:\.\d+)?)', text_lower)
        params['rainfall'] = float(rain_match.group(1)) if rain_match else kwargs.get('rainfall', 150)
        
        return params
    
    def get_info(self) -> Dict[str, Any]:
        """Return tool information."""
        return {
            'name': self.name,
            'description': self.description,
            'required_params': list(self.valid_ranges.keys()),
            'model_loaded': self.model_data is not None,
            'crops': self.model_data['classes'] if self.model_data else None
        }

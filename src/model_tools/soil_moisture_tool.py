"""
Soil Moisture Classification Tool
Classifies soil moisture status based on IoT sensor data.
"""

import pickle
import numpy as np
import pandas as pd
import re
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class SoilMoistureTool:
    """Tool for classifying soil moisture status from IoT sensor readings."""
    
    def __init__(self):
        self.name = "soil_moisture_classification"
        self.description = "Classifies soil moisture status (Very Dry/Dry/Wet/Very Wet) from IoT sensors"
        self.model_path = Path("models/soil_moisture_model.pkl")
        self.model_data = None
        self.load_model()
        
        # Valid ranges for input validation (IoT sensor data)
        self.valid_ranges = {
            'temperature': (-10, 60),  # Celsius
            'pressure': (900, 1100),   # hPa
            'altitude': (-500, 5000),  # meters
            'soil_moisture': (0, 1024) # Sensor reading
        }
    
    def load_model(self):
        """Load the trained soil moisture classification model."""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    self.model_data = pickle.load(f)
                print(f"✓ Soil moisture model loaded from {self.model_path}")
            else:
                print(f"⚠ Model not found at {self.model_path}")
                self.model_data = None
        except Exception as e:
            print(f"❌ Error loading soil moisture model: {e}")
            self.model_data = None
    
    def validate_inputs(self, params: Dict[str, Any]) -> tuple[bool, str]:
        """Validate input parameters for IoT sensor data."""
        required = ['temperature', 'pressure', 'altitude', 'soil_moisture']
        
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
        Predict soil moisture classification from IoT sensor data.
        
        Args:
            params: Dictionary with keys:
                - temperature: Ambient temperature in Celsius
                - pressure: Atmospheric pressure in hPa
                - altitude: Altitude in meters
                - soil_moisture: Soil moisture sensor reading (0-1024)
        
        Returns:
            Dictionary with classification and irrigation recommendations
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
            
            # Prepare features
            features = pd.DataFrame([{
                'temperature': float(params['temperature']),
                'pressure': float(params['pressure']),
                'altitude': float(params['altitude']),
                'soilmiosture': float(params['soil_moisture'])  # Note: matches dataset typo
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
            predicted_class = label_encoder.inverse_transform([prediction])[0]
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                predicted_class,
                params,
                probabilities
            )
            
            return {
                'success': True,
                'classification': predicted_class,
                'confidence': float(max(probabilities)),
                'probabilities': {
                    label_encoder.inverse_transform([i])[0]: float(prob)
                    for i, prob in enumerate(probabilities)
                },
                'recommendations': recommendations,
                'sensor_readings': {
                    'temperature': f"{params['temperature']}°C",
                    'pressure': f"{params['pressure']} hPa",
                    'altitude': f"{params['altitude']}m",
                    'soil_moisture_raw': params['soil_moisture']
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Prediction failed: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_recommendations(
        self,
        predicted_class: str,
        params: Dict[str, Any],
        probabilities: np.ndarray
    ) -> list:
        """Generate irrigation recommendations based on soil moisture classification."""
        recommendations = []
        
        moisture = params['soil_moisture']
        temperature = params['temperature']
        confidence = float(max(probabilities))
        
        if predicted_class == 'Very Dry':
            recommendations.append("🚨 URGENT: Soil is very dry - immediate irrigation required")
            recommendations.append(f"Sensor reading: {moisture} (critical level)")
            recommendations.append("Action: Apply water immediately to prevent crop stress")
            
            if temperature > 30:
                recommendations.append("⚠ High temperature detected - irrigate during cooler hours")
            
            recommendations.append("Monitor soil moisture every 2-4 hours after irrigation")
        
        elif predicted_class == 'Dry':
            recommendations.append("⚠ Soil moisture is low - irrigation recommended soon")
            recommendations.append(f"Sensor reading: {moisture} (below optimal)")
            recommendations.append("Action: Schedule irrigation within 12-24 hours")
            recommendations.append("Prepare irrigation system and check water availability")
        
        elif predicted_class == 'Wet':
            recommendations.append("✓ Soil moisture is adequate")
            recommendations.append(f"Sensor reading: {moisture} (good level)")
            recommendations.append("Action: No irrigation needed at this time")
            recommendations.append("Continue regular monitoring (check every 24 hours)")
        
        elif predicted_class == 'Very Wet':
            recommendations.append("💧 Soil is saturated - no irrigation needed")
            recommendations.append(f"Sensor reading: {moisture} (high level)")
            recommendations.append("Action: Stop irrigation, ensure good drainage")
            recommendations.append("⚠ Monitor for waterlogging and root diseases")
        
        # Add confidence-based notes
        if confidence < 0.7:
            recommendations.append(f"ℹ️ Moderate confidence ({confidence:.1%}) - verify with manual check")
        
        # Temperature-based suggestions
        if temperature > 35:
            recommendations.append("🌡 Extreme heat - increase monitoring frequency")
        elif temperature < 5:
            recommendations.append("❄ Low temperature - adjust irrigation schedule")
        
        return recommendations
    
    def run(self, text: str = "", query: str = "", **kwargs) -> Dict[str, Any]:
        """Run method for ReAct agent compatibility."""
        query_text = text or query or ""
        
        if 'params' in kwargs:
            params = kwargs['params']
        else:
            params = self._extract_params_from_text(query_text, kwargs)
        
        return self.predict(params)
    
    def _extract_params_from_text(self, text: str, kwargs: Dict) -> Dict[str, Any]:
        """Extract IoT sensor parameters from query text."""
        params = {}
        text_lower = text.lower()
        
        # Extract temperature
        temp_match = re.search(r'(?:temperature|temp)[:\s]+(\d+(?:\.\d+)?)', text_lower)
        if not temp_match:
            temp_match = re.search(r'(\d+(?:\.\d+)?)\s*[°]?c', text_lower)
        params['temperature'] = float(temp_match.group(1)) if temp_match else kwargs.get('temperature', 25)
        
        # Extract pressure
        press_match = re.search(r'pressure[:\s]+(\d+(?:\.\d+)?)', text_lower)
        params['pressure'] = float(press_match.group(1)) if press_match else kwargs.get('pressure', 1013)
        
        # Extract altitude
        alt_match = re.search(r'altitude[:\s]+(\d+(?:\.\d+)?)', text_lower)
        if not alt_match:
            alt_match = re.search(r'(\d+(?:\.\d+)?)\s*m(?:eters)?', text_lower)
        params['altitude'] = float(alt_match.group(1)) if alt_match else kwargs.get('altitude', 500)
        
        # Extract soil moisture
        moist_match = re.search(r'(?:soil\s*)?moisture[:\s]+(\d+(?:\.\d+)?)', text_lower)
        if not moist_match:
            moist_match = re.search(r'moisture[:\s]+(\d+(?:\.\d+)?)', text_lower)
        params['soil_moisture'] = float(moist_match.group(1)) if moist_match else kwargs.get('soil_moisture', 350)
        
        return params
    
    def get_info(self) -> Dict[str, Any]:
        """Return tool information."""
        return {
            'name': self.name,
            'description': self.description,
            'required_params': list(self.valid_ranges.keys()),
            'model_loaded': self.model_data is not None,
            'classes': self.model_data['classes'] if self.model_data else None
        }

"""
Crop Nutrient Recommendation Tool
Recommends crops based on soil nutrient composition (11 parameters).
"""

import pickle
import numpy as np
import pandas as pd
import re
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class CropNutrientTool:
    """Tool for recommending crops based on soil nutrient analysis."""
    
    def __init__(self):
        self.name = "crop_nutrient_recommendation"
        self.description = "Recommends suitable crops based on detailed soil nutrient analysis"
        self.model_path = Path("models/crop_nutrient_model.pkl")
        self.model_data = None
        self.load_model()
        
        # Valid ranges for soil nutrient parameters
        self.valid_ranges = {
            'N': (0, 500),      # Nitrogen (kg/ha)
            'P': (0, 200),      # Phosphorus (kg/ha)
            'K': (0, 500),      # Potassium (kg/ha)
            'ph': (4.0, 9.0),   # pH (lowercase to match dataset)
            'EC': (0, 10),      # Electrical Conductivity (dS/m)
            'S': (0, 100),      # Sulfur (ppm)
            'Cu': (0, 20),      # Copper (ppm)
            'Fe': (0, 100),     # Iron (ppm)
            'Mn': (0, 50),      # Manganese (ppm)
            'Zn': (0, 30),      # Zinc (ppm)
            'B': (0, 10)        # Boron (ppm)
        }
    
    def load_model(self):
        """Load the trained crop nutrient recommendation model."""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    self.model_data = pickle.load(f)
                print(f"✓ Crop nutrient model loaded from {self.model_path}")
            else:
                print(f"⚠ Model not found at {self.model_path}")
                self.model_data = None
        except Exception as e:
            print(f"❌ Error loading crop nutrient model: {e}")
            self.model_data = None
    
    def validate_inputs(self, params: Dict[str, Any]) -> tuple[bool, str]:
        """Validate input parameters for soil nutrients."""
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
        Predict suitable crop based on soil nutrient composition.
        
        Args:
            params: Dictionary with 11 soil nutrient parameters:
                - N, P, K: Macro nutrients
                - ph: Soil pH
                - EC: Electrical conductivity
                - S, Cu, Fe, Mn, Zn, B: Micro nutrients
        
        Returns:
            Dictionary with crop recommendation and soil analysis
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
                'ph': float(params['ph']),
                'EC': float(params['EC']),
                'S': float(params['S']),
                'Cu': float(params['Cu']),
                'Fe': float(params['Fe']),
                'Mn': float(params['Mn']),
                'Zn': float(params['Zn']),
                'B': float(params['B'])
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
            
            # Get top 3 recommendations
            top_indices = np.argsort(probabilities)[::-1][:3]
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
                'top_3_crops': top_crops,
                'recommendations': recommendations,
                'soil_analysis': self._analyze_soil(params),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Prediction failed: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_soil(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Analyze soil nutrient levels."""
        analysis = {}
        
        # pH analysis
        ph = params['ph']
        if ph < 5.5:
            analysis['pH'] = f"{ph} (Acidic - may need lime application)"
        elif ph > 7.5:
            analysis['pH'] = f"{ph} (Alkaline - may affect nutrient availability)"
        else:
            analysis['pH'] = f"{ph} (Optimal range)"
        
        # NPK analysis
        npk_levels = []
        if params['N'] < 150:
            npk_levels.append("N is low")
        elif params['N'] > 350:
            npk_levels.append("N is high")
        
        if params['P'] < 30:
            npk_levels.append("P is low")
        elif params['P'] > 120:
            npk_levels.append("P is high")
        
        if params['K'] < 150:
            npk_levels.append("K is low")
        elif params['K'] > 350:
            npk_levels.append("K is high")
        
        analysis['NPK'] = ", ".join(npk_levels) if npk_levels else "Balanced"
        
        # Micronutrient check
        micro_issues = []
        if params['Zn'] < 5:
            micro_issues.append("Zinc deficiency")
        if params['Fe'] < 20:
            micro_issues.append("Iron deficiency")
        if params['B'] < 1:
            micro_issues.append("Boron deficiency")
        
        analysis['Micronutrients'] = ", ".join(micro_issues) if micro_issues else "Adequate"
        
        return analysis
    
    def _generate_recommendations(
        self,
        recommended_crop: str,
        params: Dict[str, Any],
        top_crops: list
    ) -> list:
        """Generate crop recommendations and soil management advice."""
        recommendations = []
        
        recommendations.append(f"🌱 Best crop recommendation: {recommended_crop.upper()}")
        recommendations.append(f"Alternative options: {', '.join([c['crop'] for c in top_crops[1:]])}")
        
        # Soil-specific advice
        ph = params['ph']
        if ph < 5.5:
            recommendations.append("🔬 Apply agricultural lime to raise pH")
        elif ph > 7.5:
            recommendations.append("🔬 Apply sulfur or gypsum to lower pH")
        
        # NPK management
        if params['N'] < 150:
            recommendations.append("🌿 Apply nitrogen fertilizer (urea or ammonium sulfate)")
        if params['P'] < 30:
            recommendations.append("🌿 Apply phosphate fertilizer (DAP or SSP)")
        if params['K'] < 150:
            recommendations.append("🌿 Apply potassium fertilizer (MOP or SOP)")
        
        # Micronutrient advice
        if params['Zn'] < 5:
            recommendations.append("💊 Apply zinc sulfate as foliar spray")
        if params['Fe'] < 20:
            recommendations.append("💊 Apply iron chelate for iron deficiency")
        if params['B'] < 1:
            recommendations.append("💊 Apply borax for boron deficiency")
        
        # EC (salinity) check
        if params['EC'] > 4:
            recommendations.append("⚠️ High soil salinity - improve drainage and leaching")
        
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
        """Extract soil nutrient parameters from query text."""
        params = {}
        text_lower = text.lower()
        
        # Extract NPK
        n_match = re.search(r'\bn\s*[=:]\s*(\d+(?:\.\d+)?)', text_lower)
        params['N'] = float(n_match.group(1)) if n_match else kwargs.get('N', 150)
        
        p_match = re.search(r'\bp\s*[=:]\s*(\d+(?:\.\d+)?)', text_lower)
        params['P'] = float(p_match.group(1)) if p_match else kwargs.get('P', 40)
        
        k_match = re.search(r'\bk\s*[=:]\s*(\d+(?:\.\d+)?)', text_lower)
        params['K'] = float(k_match.group(1)) if k_match else kwargs.get('K', 200)
        
        # Extract pH (lowercase to match dataset)
        ph_match = re.search(r'ph[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['ph'] = float(ph_match.group(1)) if ph_match else kwargs.get('ph', 6.5)
        
        # Extract EC
        ec_match = re.search(r'ec[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['EC'] = float(ec_match.group(1)) if ec_match else kwargs.get('EC', 1.5)
        
        # Extract micronutrients
        s_match = re.search(r'\bs[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['S'] = float(s_match.group(1)) if s_match else kwargs.get('S', 25)
        
        cu_match = re.search(r'cu[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['Cu'] = float(cu_match.group(1)) if cu_match else kwargs.get('Cu', 5)
        
        fe_match = re.search(r'fe[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['Fe'] = float(fe_match.group(1)) if fe_match else kwargs.get('Fe', 35)
        
        mn_match = re.search(r'mn[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['Mn'] = float(mn_match.group(1)) if mn_match else kwargs.get('Mn', 18)
        
        zn_match = re.search(r'zn[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['Zn'] = float(zn_match.group(1)) if zn_match else kwargs.get('Zn', 7)
        
        b_match = re.search(r'\bb[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['B'] = float(b_match.group(1)) if b_match else kwargs.get('B', 2)
        
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

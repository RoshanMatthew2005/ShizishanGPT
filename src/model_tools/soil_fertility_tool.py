"""
Soil Fertility Classification Tool
Classifies soil fertility level (Low/Medium/High) based on nutrient analysis.
"""

import pickle
import numpy as np
import pandas as pd
import re
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class SoilFertilityTool:
    """Tool for classifying soil fertility based on comprehensive nutrient analysis."""
    
    def __init__(self):
        self.name = "soil_fertility_classification"
        self.description = "Classifies soil fertility level (Low/Medium/High) from 12 soil parameters"
        self.model_path = Path("models/soil_fertility_model.pkl")
        self.model_data = None
        self.load_model()
        
        # Valid ranges for soil parameters
        self.valid_ranges = {
            'N': (0, 500),       # Nitrogen (kg/ha)
            'P': (0, 200),       # Phosphorus (kg/ha)
            'K': (0, 500),       # Potassium (kg/ha)
            'pH': (4.0, 9.0),    # Uppercase pH for this dataset
            'EC': (0, 10),       # Electrical Conductivity (dS/m)
            'OC': (0, 5),        # Organic Carbon (%)
            'S': (0, 100),       # Sulfur (ppm)
            'Zn': (0, 30),       # Zinc (ppm)
            'Fe': (0, 100),      # Iron (ppm)
            'Cu': (0, 20),       # Copper (ppm)
            'Mn': (0, 50),       # Manganese (ppm)
            'B': (0, 10)         # Boron (ppm)
        }
        
        self.fertility_map = {0: 'Low', 1: 'Medium', 2: 'High'}
    
    def load_model(self):
        """Load the trained soil fertility classification model."""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    self.model_data = pickle.load(f)
                print(f"✓ Soil fertility model loaded from {self.model_path}")
            else:
                print(f"⚠ Model not found at {self.model_path}")
                self.model_data = None
        except Exception as e:
            print(f"❌ Error loading soil fertility model: {e}")
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
        Classify soil fertility level based on nutrient composition.
        
        Args:
            params: Dictionary with 12 soil parameters:
                - N, P, K: Macro nutrients
                - pH, EC, OC: Soil properties
                - S, Zn, Fe, Cu, Mn, B: Micro nutrients
        
        Returns:
            Dictionary with fertility classification and improvement recommendations
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
                'pH': float(params['pH']),
                'EC': float(params['EC']),
                'OC': float(params['OC']),
                'S': float(params['S']),
                'Zn': float(params['Zn']),
                'Fe': float(params['Fe']),
                'Cu': float(params['Cu']),
                'Mn': float(params['Mn']),
                'B': float(params['B'])
            }])
            
            # Scale features
            scaler = self.model_data['scaler']
            features_scaled = scaler.transform(features)
            
            # Make prediction
            model = self.model_data['model']
            prediction = model.predict(features_scaled)[0]
            probabilities = model.predict_proba(features_scaled)[0]
            
            # Map to fertility label
            fertility_level = self.fertility_map[prediction]
            
            # Get probabilities for all classes
            fertility_probs = {
                self.fertility_map[i]: float(prob)
                for i, prob in enumerate(probabilities)
            }
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                fertility_level,
                params,
                prediction,
                probabilities
            )
            
            return {
                'success': True,
                'fertility_level': fertility_level,
                'confidence': float(max(probabilities)),
                'probabilities': fertility_probs,
                'recommendations': recommendations,
                'deficiencies': self._identify_deficiencies(params),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Prediction failed: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def _identify_deficiencies(self, params: Dict[str, Any]) -> list:
        """Identify nutrient deficiencies."""
        deficiencies = []
        
        # Macro nutrients
        if params['N'] < 150:
            deficiencies.append(f"Nitrogen: {params['N']} kg/ha (Low - target 150+)")
        if params['P'] < 30:
            deficiencies.append(f"Phosphorus: {params['P']} kg/ha (Low - target 30+)")
        if params['K'] < 150:
            deficiencies.append(f"Potassium: {params['K']} kg/ha (Low - target 150+)")
        
        # Organic carbon
        if params['OC'] < 0.5:
            deficiencies.append(f"Organic Carbon: {params['OC']}% (Very Low - target 0.5%+)")
        
        # Micro nutrients
        if params['Zn'] < 5:
            deficiencies.append(f"Zinc: {params['Zn']} ppm (Deficient - target 5+ ppm)")
        if params['Fe'] < 20:
            deficiencies.append(f"Iron: {params['Fe']} ppm (Deficient - target 20+ ppm)")
        if params['Cu'] < 2:
            deficiencies.append(f"Copper: {params['Cu']} ppm (Deficient - target 2+ ppm)")
        if params['Mn'] < 10:
            deficiencies.append(f"Manganese: {params['Mn']} ppm (Deficient - target 10+ ppm)")
        if params['B'] < 0.5:
            deficiencies.append(f"Boron: {params['B']} ppm (Deficient - target 0.5+ ppm)")
        if params['S'] < 10:
            deficiencies.append(f"Sulfur: {params['S']} ppm (Deficient - target 10+ ppm)")
        
        return deficiencies if deficiencies else ["No major deficiencies detected"]
    
    def _generate_recommendations(
        self,
        fertility_level: str,
        params: Dict[str, Any],
        prediction: int,
        probabilities: np.ndarray
    ) -> list:
        """Generate soil improvement recommendations."""
        recommendations = []
        
        # Overall assessment
        if fertility_level == 'High':
            recommendations.append("✨ Excellent soil fertility! Maintain current practices")
            recommendations.append("Continue regular soil testing to monitor nutrient levels")
            recommendations.append("Organic matter management is key to sustained fertility")
        
        elif fertility_level == 'Medium':
            recommendations.append("✓ Moderate soil fertility - room for improvement")
            recommendations.append("Focus on targeted nutrient amendments")
            
            # Specific improvements
            if params['OC'] < 1.0:
                recommendations.append("🌿 Increase organic carbon: add compost or farmyard manure")
            
            if params['N'] < 150:
                recommendations.append("Add nitrogen: urea (50-100 kg/ha) or ammonium sulfate")
            
            if params['P'] < 40:
                recommendations.append("Add phosphorus: DAP (50-75 kg/ha) or SSP")
            
            if params['K'] < 150:
                recommendations.append("Add potassium: MOP (40-60 kg/ha) or potassium sulfate")
        
        else:  # Low fertility
            recommendations.append("⚠️ Low soil fertility - comprehensive improvement needed")
            recommendations.append("🔧 Implement integrated soil fertility management:")
            
            # Critical actions
            recommendations.append("1. Add organic matter: 5-10 tons/ha of compost or FYM")
            recommendations.append("2. Apply balanced NPK fertilizer: 100:50:50 kg/ha")
            recommendations.append("3. Lime application if pH < 5.5, gypsum if pH > 7.5")
            recommendations.append("4. Add micronutrient mixture for deficiencies")
            
            # Organic carbon is critical
            if params['OC'] < 0.5:
                recommendations.append("🚨 CRITICAL: Very low organic carbon - priority action required")
                recommendations.append("   Apply green manure crops (Dhaincha, Sunhemp) or compost")
        
        # pH management
        ph = params['pH']
        if ph < 5.5:
            recommendations.append(f"🔬 Acidic soil (pH {ph}) - apply lime: 2-4 tons/ha")
        elif ph > 7.5:
            recommendations.append(f"🔬 Alkaline soil (pH {ph}) - apply gypsum: 1-2 tons/ha")
        
        # EC (salinity) check
        if params['EC'] > 4:
            recommendations.append(f"⚠️ High salinity (EC {params['EC']}) - improve drainage and leaching")
        
        # Micronutrient sprays
        deficient_micros = []
        if params['Zn'] < 5:
            deficient_micros.append("Zn (zinc sulfate 0.5%)")
        if params['Fe'] < 20:
            deficient_micros.append("Fe (ferrous sulfate 0.5%)")
        if params['B'] < 0.5:
            deficient_micros.append("B (borax 0.1%)")
        
        if deficient_micros:
            recommendations.append(f"💊 Foliar spray: {', '.join(deficient_micros)}")
        
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
        """Extract soil fertility parameters from query text."""
        params = {}
        text_lower = text.lower()
        
        # Extract NPK
        n_match = re.search(r'\bn\s*[=:]\s*(\d+(?:\.\d+)?)', text_lower)
        params['N'] = float(n_match.group(1)) if n_match else kwargs.get('N', 150)
        
        p_match = re.search(r'\bp\s*[=:]\s*(\d+(?:\.\d+)?)', text_lower)
        params['P'] = float(p_match.group(1)) if p_match else kwargs.get('P', 40)
        
        k_match = re.search(r'\bk\s*[=:]\s*(\d+(?:\.\d+)?)', text_lower)
        params['K'] = float(k_match.group(1)) if k_match else kwargs.get('K', 200)
        
        # Extract pH (uppercase for this dataset)
        ph_match = re.search(r'ph[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['pH'] = float(ph_match.group(1)) if ph_match else kwargs.get('pH', 6.5)
        
        # Extract EC
        ec_match = re.search(r'ec[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['EC'] = float(ec_match.group(1)) if ec_match else kwargs.get('EC', 1.5)
        
        # Extract OC (Organic Carbon)
        oc_match = re.search(r'oc[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['OC'] = float(oc_match.group(1)) if oc_match else kwargs.get('OC', 0.8)
        
        # Extract micronutrients
        s_match = re.search(r'\bs[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['S'] = float(s_match.group(1)) if s_match else kwargs.get('S', 25)
        
        zn_match = re.search(r'zn[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['Zn'] = float(zn_match.group(1)) if zn_match else kwargs.get('Zn', 7)
        
        fe_match = re.search(r'fe[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['Fe'] = float(fe_match.group(1)) if fe_match else kwargs.get('Fe', 35)
        
        cu_match = re.search(r'cu[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['Cu'] = float(cu_match.group(1)) if cu_match else kwargs.get('Cu', 4)
        
        mn_match = re.search(r'mn[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['Mn'] = float(mn_match.group(1)) if mn_match else kwargs.get('Mn', 15)
        
        b_match = re.search(r'\bb[:\s=]+(\d+(?:\.\d+)?)', text_lower)
        params['B'] = float(b_match.group(1)) if b_match else kwargs.get('B', 1.5)
        
        return params
    
    def get_info(self) -> Dict[str, Any]:
        """Return tool information."""
        return {
            'name': self.name,
            'description': self.description,
            'required_params': list(self.valid_ranges.keys()),
            'model_loaded': self.model_data is not None,
            'fertility_levels': list(self.fertility_map.values())
        }

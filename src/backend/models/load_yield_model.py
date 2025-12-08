"""
Yield Model Loader
Loads and manages the crop yield prediction model
"""

import joblib
import numpy as np
from pathlib import Path
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class YieldModel:
    """
    Wrapper for yield prediction model
    """
    
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.model = None
        self.loaded = False
    
    def load(self):
        """Load the yield model"""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            self.model = joblib.load(self.model_path)
            self.loaded = True
            logger.info(f"✓ Yield model loaded from {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load yield model: {e}")
            self.loaded = False
            return False
    
    def predict(self, 
                crop_encoded: int,
                season_encoded: int,
                state_encoded: int,
                annual_rainfall: float,
                fertilizer: float,
                pesticide: float,
                area: float) -> Dict[str, Any]:
        """
        Predict crop yield
        
        Args:
            crop_encoded: Encoded crop type
            season_encoded: Encoded season
            state_encoded: Encoded state
            annual_rainfall: Annual rainfall in mm
            fertilizer: Fertilizer amount in kg
            pesticide: Pesticide amount in kg
            area: Cultivation area in hectares
        
        Returns:
            Dictionary with prediction and metadata
        """
        if not self.loaded:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        try:
            # Prepare input features
            features = np.array([[
                crop_encoded,
                season_encoded,
                state_encoded,
                annual_rainfall,
                fertilizer,
                pesticide,
                area
            ]])
            
            # Make prediction
            prediction = self.model.predict(features)[0]
            
            # Calculate confidence (if model supports predict_proba)
            confidence = None
            if hasattr(self.model, 'score'):
                # For regression models, we can't get probability
                # but we can return R² score as a proxy for confidence
                confidence = 0.95  # Placeholder - actual model R² from training
            
            result = {
                "prediction": float(prediction),
                "unit": "tonnes per hectare",
                "confidence": confidence,
                "inputs": {
                    "crop_encoded": crop_encoded,
                    "season_encoded": season_encoded,
                    "state_encoded": state_encoded,
                    "annual_rainfall": annual_rainfall,
                    "fertilizer": fertilizer,
                    "pesticide": pesticide,
                    "area": area
                }
            }
            
            logger.info(f"Yield prediction: {prediction:.2f} tonnes/hectare")
            return result
            
        except Exception as e:
            logger.error(f"Yield prediction failed: {e}")
            raise


def load_yield_model(model_path: str) -> YieldModel:
    """
    Factory function to load yield model
    """
    model = YieldModel(model_path)
    model.load()
    return model

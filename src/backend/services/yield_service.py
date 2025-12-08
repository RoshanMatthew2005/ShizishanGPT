"""
Yield Prediction Service
Handles crop yield predictions
"""

import logging
import time
from typing import Dict, Any
from ..dependencies import model_registry

logger = logging.getLogger(__name__)


class YieldService:
    """
    Service for yield prediction operations
    """
    
    def __init__(self):
        self.yield_model = None
    
    def initialize(self):
        """Initialize service with loaded model"""
        self.yield_model = model_registry.get("yield_model")
    
    async def predict(self,
                     crop: str,
                     season: str,
                     state: str,
                     rainfall: float,
                     fertilizer: float,
                     pesticide: float,
                     area: float) -> Dict[str, Any]:
        """
        Predict crop yield
        
        Args:
            crop: Crop name
            season: Season name
            state: State name
            rainfall: Annual rainfall in mm
            fertilizer: Fertilizer usage in kg/hectare
            pesticide: Pesticide usage in kg/hectare
            area: Area in hectares
        
        Returns:
            Dictionary with prediction and metadata
        """
        start_time = time.time()
        
        try:
            if self.yield_model is None:
                self.initialize()
            
            logger.info(f"Predicting yield for {crop} in {state}")
            
            # Validate inputs
            if rainfall < 0 or fertilizer < 0 or pesticide < 0 or area <= 0:
                raise ValueError("Invalid input values: must be non-negative")
            
            # Make prediction
            result = self.yield_model.predict(
                crop=crop,
                season=season,
                state=state,
                rainfall=rainfall,
                fertilizer=fertilizer,
                pesticide=pesticide,
                area=area
            )
            
            execution_time = time.time() - start_time
            
            # Add metadata
            result["execution_time"] = execution_time
            result["inputs"] = {
                "crop": crop,
                "season": season,
                "state": state,
                "rainfall": rainfall,
                "fertilizer": fertilizer,
                "pesticide": pesticide,
                "area": area
            }
            
            logger.info(f"Yield prediction: {result['prediction']:.2f} tonnes/hectare")
            logger.info(f"Prediction completed in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Yield prediction failed: {e}")
            raise


# Global service instance
yield_service = YieldService()

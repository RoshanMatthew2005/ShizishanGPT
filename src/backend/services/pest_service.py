"""
Pest Detection Service
Handles pest and disease detection from images
"""

import logging
import time
from typing import Dict, Any
from PIL import Image
import io
from ..dependencies import model_registry

logger = logging.getLogger(__name__)


class PestService:
    """
    Service for pest detection operations
    """
    
    def __init__(self):
        self.pest_model = None
    
    def initialize(self):
        """Initialize service with loaded model"""
        self.pest_model = model_registry.get("pest_model")
    
    async def detect(self, 
                    image_bytes: bytes,
                    top_k: int = 3) -> Dict[str, Any]:
        """
        Detect pest/disease from image
        
        Args:
            image_bytes: Image file bytes
            top_k: Number of top predictions to return
        
        Returns:
            Dictionary with predictions and recommendations
        """
        start_time = time.time()
        
        try:
            if self.pest_model is None:
                self.initialize()
            
            logger.info("Processing pest detection image")
            
            # Load image
            try:
                image = Image.open(io.BytesIO(image_bytes))
                image = image.convert("RGB")
            except Exception as e:
                raise ValueError(f"Invalid image file: {e}")
            
            # Validate image
            if image.width < 50 or image.height < 50:
                raise ValueError("Image too small (minimum 50x50 pixels)")
            
            if image.width > 4096 or image.height > 4096:
                raise ValueError("Image too large (maximum 4096x4096 pixels)")
            
            # Make prediction - pass Image object directly
            result = self.pest_model.predict(image, top_k=top_k)
            
            execution_time = time.time() - start_time
            
            # Add metadata
            result["execution_time"] = execution_time
            result["image_info"] = {
                "width": image.width,
                "height": image.height,
                "format": image.format
            }
            
            logger.info(f"Top prediction: {result['predictions'][0]['class']} "
                       f"({result['predictions'][0]['confidence']:.2%})")
            logger.info(f"Detection completed in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Pest detection failed: {e}")
            raise


# Global service instance
pest_service = PestService()

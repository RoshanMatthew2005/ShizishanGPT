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
                    top_k: int = 3,
                    use_agent: bool = False,
                    agent_service = None,
                    query: str = "") -> Dict[str, Any]:
        """
        Detect pest/disease from image
        
        Args:
            image_bytes: Image file bytes
            top_k: Number of top predictions to return
            use_agent: Whether to use ReAct agent for analysis
            agent_service: Agent service instance
            query: User query text for agent context
        
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
            
            # If agent is enabled, process through ReAct agent for detailed analysis
            if use_agent and agent_service:
                try:
                    logger.info("🤖 Processing pest detection through ReAct agent...")
                    
                    # Create comprehensive query for agent
                    disease_name = result.get('disease', 'Unknown')
                    confidence = result.get('confidence', 0)
                    recommendations = result.get('recommendations', [])
                    
                    agent_query = f"""
                    Image analysis detected: {disease_name} with {confidence*100:.1f}% confidence.
                    Basic recommendations: {', '.join(recommendations[:3])}
                    
                    User query: {query if query else 'Please provide detailed information about this plant disease.'}
                    
                    Provide comprehensive information including:
                    1. Detailed disease description and symptoms
                    2. Complete treatment and control measures
                    3. Prevention strategies
                    4. Best products available (search for current recommendations)
                    """
                    
                    # Process through agent
                    agent_result = agent_service.process_query(
                        query=agent_query,
                        mode="react",
                        max_iterations=5
                    )
                    
                    agent_execution_time = agent_result.get("execution_time", 0)
                    
                    # Add agent analysis to result
                    result["agent_analysis"] = agent_result.get("final_answer", "")
                    result["agent_tools_used"] = agent_result.get("tools_used", [])
                    result["agent_sources"] = agent_result.get("sources", [])
                    result["total_execution_time"] = execution_time + agent_execution_time
                    
                    logger.info(f"✅ Agent analysis complete. Tools used: {result['agent_tools_used']}")
                    
                except Exception as agent_error:
                    logger.error(f"Agent processing failed: {agent_error}")
                    # Continue without agent analysis if it fails
                    result["agent_analysis"] = None
                    result["agent_error"] = str(agent_error)
            
            return result
            
        except Exception as e:
            logger.error(f"Pest detection failed: {e}")
            raise


# Global service instance
pest_service = PestService()

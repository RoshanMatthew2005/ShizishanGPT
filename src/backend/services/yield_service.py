"""
Yield Prediction Service
Handles crop yield predictions
"""

import logging
import time
from typing import Dict, Any, Optional
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
                     area: float,
                     use_agent: bool = False,
                     agent_service=None) -> Dict[str, Any]:
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
            use_agent: Whether to process results through ReAct agent
            agent_service: AgentService instance for processing
        
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
            
            # Process through ReAct agent if requested
            if use_agent and agent_service:
                try:
                    logger.info("🤖 Processing yield prediction through ReAct agent...")
                    
                    # Ensure agent service is initialized
                    if not agent_service.initialized:
                        logger.info("Initializing agent service...")
                        agent_service.initialize()
                    
                    # Create comprehensive query for the agent
                    agent_query = f"""
                    Analyze this crop yield prediction and provide detailed insights:
                    
                    Crop: {crop}
                    Season: {season}
                    State: {state}
                    Predicted Yield: {result['prediction']:.2f} tonnes/hectare
                    Total Production: {result['prediction'] * area:.2f} tonnes
                    
                    Input Parameters:
                    - Area: {area} hectares
                    - Rainfall: {rainfall} mm
                    - Fertilizer: {fertilizer} kg/hectare
                    - Pesticide: {pesticide} kg/hectare
                    
                    Please provide:
                    1. Analysis of the predicted yield (is it good/average/poor for this crop?)
                    2. How the input parameters affect the yield
                    3. Specific recommendations to improve yield
                    4. Best practices for {crop} cultivation in {season}
                    5. Market insights and economic considerations
                    """
                    
                    logger.info(f"Agent query: {agent_query[:200]}...")
                    
                    # Get agent analysis
                    agent_result = await agent_service.process_query(
                        query=agent_query,
                        mode="react",
                        max_iterations=5,
                        verbose=False
                    )
                    
                    # Add agent insights to result
                    result["agent_analysis"] = agent_result.get("final_answer", "")
                    result["agent_tools_used"] = agent_result.get("tools_used", [])
                    result["agent_sources"] = agent_result.get("sources")
                    result["agent_execution_time"] = agent_result.get("execution_time", 0)
                    
                    logger.info(f"Agent analysis completed using tools: {result['agent_tools_used']}")
                    
                except Exception as e:
                    logger.error(f"Agent processing failed: {e}")
                    result["agent_analysis"] = None
                    result["agent_error"] = str(e)
            
            total_time = time.time() - start_time
            result["total_execution_time"] = total_time
            
            logger.info(f"Prediction completed in {total_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Yield prediction failed: {e}")
            raise


# Global service instance
yield_service = YieldService()

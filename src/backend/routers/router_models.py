"""
Models Router
Handles ML model endpoints: /predict_yield, /detect_pest
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Dict, Any
import logging

from ..utils.schema_validator import (
    YieldPredictionRequest, YieldPredictionResponse,
    PestDetectionResponse
)
from ..utils.response_formatter import (
    format_prediction_response,
    format_error
)
from ..services.yield_service import yield_service
from ..services.pest_service import pest_service
from ..services.history_service import history_service
from ..services.agent_service import agent_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["models"])


@router.post("/predict_yield", response_model=YieldPredictionResponse)
async def predict_yield(
    request: YieldPredictionRequest,
    use_agent: bool = True  # Enable agent analysis by default
) -> Dict[str, Any]:
    """
    Predict crop yield with AI-powered insights
    
    Uses RandomForest model to predict yield based on agricultural parameters.
    Results are processed through ReAct agent for detailed analysis and recommendations.
    
    Args:
        request: Yield prediction parameters
        use_agent: Enable ReAct agent for detailed analysis (default: True)
    """
    try:
        logger.info(f"POST /predict_yield - crop: {request.crop}, state: {request.state}, agent: {use_agent}")
        
        # Validate inputs
        if request.area <= 0:
            raise HTTPException(status_code=400, detail="Area must be positive")
        
        if request.rainfall < 0 or request.fertilizer < 0 or request.pesticide < 0:
            raise HTTPException(status_code=400, detail="Values cannot be negative")
        
        # Make prediction with optional agent analysis
        result = await yield_service.predict(
            crop=request.crop,
            season=request.season,
            state=request.state,
            rainfall=request.rainfall,
            fertilizer=request.fertilizer,
            pesticide=request.pesticide,
            area=request.area,
            use_agent=use_agent,
            agent_service=agent_service if use_agent else None
        )
        
        # Log result for debugging
        logger.info(f"Prediction result keys: {list(result.keys())}")
        if "agent_analysis" in result:
            logger.info(f"✅ Agent analysis present: {result['agent_analysis'][:100]}...")
        else:
            logger.info("⚠️ No agent analysis in result")
        
        # Log to history
        await history_service.log_query(
            endpoint="/predict_yield",
            query_data=result.get("inputs", {}),
            response_data=result,
            execution_time=result.get("execution_time", 0)
        )
        
        # Format response
        return format_prediction_response(result, "yield")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /predict_yield: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect_pest", response_model=PestDetectionResponse)
async def detect_pest(
    file: UploadFile = File(...),
    top_k: int = Form(default=3),
    use_agent: bool = Form(default=True),
    query: str = Form(default="")
) -> Dict[str, Any]:
    """
    Detect plant disease from image
    
    Uses ResNet18 model trained on PlantVillage dataset
    Accepts: JPG, PNG (max 10MB)
    Optional: ReAct agent for detailed analysis (enabled by default)
    """
    try:
        logger.info(f"POST /detect_pest - file: {file.filename}")
        
        # Validate file
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Validate size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(image_bytes) > max_size:
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Detect pest (with optional agent analysis)
        result = await pest_service.detect(
            image_bytes=image_bytes,
            top_k=top_k,
            use_agent=use_agent,
            agent_service=agent_service if use_agent else None,
            query=query
        )
        
        logger.info(f"Pest detection result keys: {result.keys()}")
        if use_agent:
            logger.info(f"Agent analysis present: {bool(result.get('agent_analysis'))}")
        
        # Log to history (without storing image bytes)
        await history_service.log_query(
            endpoint="/detect_pest",
            query_data={
                "filename": file.filename,
                "top_k": top_k,
                "use_agent": use_agent,
                "query": query,
                "image_info": result.get("image_info", {})
            },
            response_data={
                "predictions": result.get("predictions", []),
                "recommendations": result.get("recommendations"),
                "agent_analysis": result.get("agent_analysis") if use_agent else None
            },
            execution_time=result.get("total_execution_time", result.get("execution_time", 0))
        )
        
        # Return data directly (not wrapped) to match PestDetectionResponse schema
        response_data = {
            "top_prediction": result.get("disease", "Unknown"),
            "confidence": result.get("confidence", 0.0),
            "all_predictions": result.get("predictions", []),
            "recommendations": result.get("recommendations", [])
        }
        
        # Add agent fields if available
        if use_agent and result.get("agent_analysis"):
            response_data["agent_analysis"] = result.get("agent_analysis")
            response_data["agent_tools_used"] = result.get("agent_tools_used", [])
            response_data["agent_sources"] = result.get("agent_sources", [])
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /detect_pest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

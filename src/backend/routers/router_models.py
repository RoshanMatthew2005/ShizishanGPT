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

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["models"])


@router.post("/predict_yield", response_model=YieldPredictionResponse)
async def predict_yield(request: YieldPredictionRequest) -> Dict[str, Any]:
    """
    Predict crop yield
    
    Uses RandomForest model to predict yield based on agricultural parameters
    """
    try:
        logger.info(f"POST /predict_yield - crop: {request.crop}, state: {request.state}")
        
        # Validate inputs
        if request.area <= 0:
            raise HTTPException(status_code=400, detail="Area must be positive")
        
        if request.rainfall < 0 or request.fertilizer < 0 or request.pesticide < 0:
            raise HTTPException(status_code=400, detail="Values cannot be negative")
        
        # Make prediction
        result = await yield_service.predict(
            crop=request.crop,
            season=request.season,
            state=request.state,
            rainfall=request.rainfall,
            fertilizer=request.fertilizer,
            pesticide=request.pesticide,
            area=request.area
        )
        
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
    top_k: int = Form(default=3)
) -> Dict[str, Any]:
    """
    Detect plant disease from image
    
    Uses ResNet18 model trained on PlantVillage dataset
    Accepts: JPG, PNG (max 10MB)
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
        
        # Detect pest
        result = await pest_service.detect(
            image_bytes=image_bytes,
            top_k=top_k
        )
        
        # Log to history (without storing image bytes)
        await history_service.log_query(
            endpoint="/detect_pest",
            query_data={
                "filename": file.filename,
                "top_k": top_k,
                "image_info": result.get("image_info", {})
            },
            response_data={
                "predictions": result.get("predictions", []),
                "recommendation": result.get("recommendation")
            },
            execution_time=result.get("execution_time", 0)
        )
        
        # Format response
        return format_prediction_response(result, "pest")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /detect_pest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

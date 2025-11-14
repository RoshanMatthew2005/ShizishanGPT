"""
FastAPI Backend for ShizishanGPT Agricultural Knowledge Assistant
Provides three main endpoints:
1. /predict_yield - Crop yield prediction
2. /analyze_weather - Weather impact analysis
3. /detect_pest - Pest/disease detection from leaf images
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any
import io
from PIL import Image
import joblib
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ShizishanGPT Agricultural API",
    description="AI-Powered Agricultural Knowledge Assistant - Milestone 2",
    version="2.0.0"
)

# Define paths
PROJECT_ROOT = Path(__file__).parent.parent
YIELD_MODEL_PATH = PROJECT_ROOT / "models" / "trained_models" / "yield_model.pkl"
WEATHER_MODEL_PATH = PROJECT_ROOT / "models" / "trained_models" / "weather_model.pkl"
PEST_MODEL_PATH = PROJECT_ROOT / "models" / "trained_models" / "pest_model.pt"
CLASS_LABELS_PATH = PROJECT_ROOT / "models" / "trained_models" / "class_labels.json"

# Global variables for loaded models
yield_model_package = None
weather_model_package = None
pest_model = None
pest_class_labels = None
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


# Pydantic models for request validation
class YieldPredictionRequest(BaseModel):
    """Request model for crop yield prediction."""
    crop: str = Field(..., description="Crop type (e.g., Rice, Wheat, Maize)")
    state: str = Field(..., description="State name (e.g., Punjab, Kerala)")
    season: str = Field(..., description="Growing season (e.g., Kharif, Rabi)")
    rainfall: float = Field(..., description="Annual rainfall in mm", gt=0)
    fertilizer: float = Field(..., description="Fertilizer used in kg", ge=0)
    pesticide: float = Field(..., description="Pesticide used in kg", ge=0)
    area: float = Field(..., description="Cultivated area in hectares", gt=0)
    
    class Config:
        schema_extra = {
            "example": {
                "crop": "Rice",
                "state": "Punjab",
                "season": "Kharif",
                "rainfall": 820,
                "fertilizer": 180,
                "pesticide": 90,
                "area": 5000
            }
        }


class YieldPredictionResponse(BaseModel):
    """Response model for crop yield prediction."""
    predicted_yield: float = Field(..., description="Predicted yield value")
    unit: str = Field(default="tons per hectare", description="Unit of measurement")
    model: str = Field(default="Crop Yield Prediction v1.0", description="Model version")


class WeatherAnalysisRequest(BaseModel):
    """Request model for weather impact analysis."""
    rainfall: float = Field(..., description="Annual rainfall in mm", gt=0)
    fertilizer: float = Field(..., description="Fertilizer used in kg", ge=0)
    pesticide: float = Field(..., description="Pesticide used in kg", ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "rainfall": 800,
                "fertilizer": 150,
                "pesticide": 75
            }
        }


class WeatherAnalysisResponse(BaseModel):
    """Response model for weather impact analysis."""
    predicted_yield: float = Field(..., description="Predicted yield based on weather factors")
    result: str = Field(..., description="Correlation analysis insight")
    model: str = Field(default="Weather Impact Model v1.0", description="Model version")


def load_yield_model():
    """Load the crop yield prediction model and encoders."""
    global yield_model_package
    
    if yield_model_package is not None:
        return yield_model_package
    
    try:
        logger.info(f"Loading yield prediction model from: {YIELD_MODEL_PATH}")
        if not YIELD_MODEL_PATH.exists():
            raise FileNotFoundError(f"Yield model not found at {YIELD_MODEL_PATH}")
        
        yield_model_package = joblib.load(YIELD_MODEL_PATH)
        logger.info("✓ Yield prediction model loaded successfully")
        return yield_model_package
    
    except Exception as e:
        logger.error(f"Failed to load yield model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")


def load_weather_model():
    """Load the weather impact model."""
    global weather_model_package
    
    if weather_model_package is not None:
        return weather_model_package
    
    try:
        logger.info(f"Loading weather impact model from: {WEATHER_MODEL_PATH}")
        if not WEATHER_MODEL_PATH.exists():
            raise FileNotFoundError(f"Weather model not found at {WEATHER_MODEL_PATH}")
        
        weather_model_package = joblib.load(WEATHER_MODEL_PATH)
        logger.info("✓ Weather impact model loaded successfully")
        return weather_model_package
    
    except Exception as e:
        logger.error(f"Failed to load weather model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")


def load_pest_model():
    """Load the pest/disease detection model and class labels."""
    global pest_model, pest_class_labels
    
    if pest_model is not None:
        return pest_model, pest_class_labels
    
    try:
        logger.info(f"Loading pest detection model from: {PEST_MODEL_PATH}")
        
        if not PEST_MODEL_PATH.exists():
            raise FileNotFoundError(f"Pest model not found at {PEST_MODEL_PATH}")
        
        if not CLASS_LABELS_PATH.exists():
            raise FileNotFoundError(f"Class labels not found at {CLASS_LABELS_PATH}")
        
        # Load class labels
        with open(CLASS_LABELS_PATH, 'r') as f:
            pest_class_labels = json.load(f)
        
        num_classes = len(pest_class_labels)
        logger.info(f"Loaded {num_classes} disease classes")
        
        # Build model architecture (same as training)
        pest_model = models.resnet18(pretrained=False)
        num_features = pest_model.fc.in_features
        pest_model.fc = nn.Linear(num_features, num_classes)
        
        # Load trained weights
        pest_model.load_state_dict(torch.load(PEST_MODEL_PATH, map_location=device))
        pest_model = pest_model.to(device)
        pest_model.eval()
        
        logger.info("✓ Pest detection model loaded successfully")
        return pest_model, pest_class_labels
    
    except Exception as e:
        logger.error(f"Failed to load pest model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")


def get_image_transform():
    """Get image preprocessing transform for pest detection."""
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])


@app.on_event("startup")
async def startup_event():
    """Load models on API startup."""
    logger.info("="*70)
    logger.info("Starting ShizishanGPT Agricultural API")
    logger.info("="*70)
    
    try:
        load_yield_model()
        load_weather_model()
        # Pest model is loaded on-demand to save memory
        # load_pest_model()
        logger.info("✅ All models loaded successfully")
        logger.info("API is ready to accept requests")
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "ShizishanGPT Agricultural API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "/predict_yield": "POST - Predict crop yield",
            "/analyze_weather": "POST - Analyze weather impact",
            "/detect_pest": "POST - Detect pest/disease from leaf image",
            "/docs": "GET - API documentation"
        }
    }


@app.post("/predict_yield", response_model=YieldPredictionResponse)
async def predict_yield(request: YieldPredictionRequest) -> YieldPredictionResponse:
    """
    Predict crop yield based on agricultural parameters.
    
    Args:
        request: YieldPredictionRequest containing crop, state, season, and other features
        
    Returns:
        YieldPredictionResponse with predicted yield value
    """
    try:
        logger.info(f"Received yield prediction request for {request.crop} in {request.state}")
        
        # Load model package
        model_pkg = load_yield_model()
        model = model_pkg['model']
        encoders = model_pkg['encoders']
        
        # Encode categorical features
        try:
            crop_encoded = encoders['Crop'].transform([request.crop.strip()])[0]
        except ValueError:
            # If crop not in training data, use most common crop encoding
            logger.warning(f"Crop '{request.crop}' not found in training data, using default")
            crop_encoded = 0
        
        try:
            state_encoded = encoders['State'].transform([request.state.strip()])[0]
        except ValueError:
            logger.warning(f"State '{request.state}' not found in training data, using default")
            state_encoded = 0
        
        try:
            season_encoded = encoders['Season'].transform([request.season.strip()])[0]
        except ValueError:
            logger.warning(f"Season '{request.season}' not found in training data, using default")
            season_encoded = 0
        
        # Prepare features array
        features = np.array([[
            crop_encoded,
            season_encoded,
            state_encoded,
            request.rainfall,
            request.fertilizer,
            request.pesticide,
            request.area
        ]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        
        # Ensure non-negative prediction
        prediction = max(0, prediction)
        
        logger.info(f"Predicted yield: {prediction:.4f} tons/hectare")
        
        return YieldPredictionResponse(
            predicted_yield=round(prediction, 2),
            unit="tons per hectare",
            model="Crop Yield Prediction v1.0"
        )
    
    except Exception as e:
        logger.error(f"Yield prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/analyze_weather", response_model=WeatherAnalysisResponse)
async def analyze_weather(request: WeatherAnalysisRequest) -> WeatherAnalysisResponse:
    """
    Analyze weather impact on crop yield.
    
    Args:
        request: WeatherAnalysisRequest containing rainfall, fertilizer, and pesticide data
        
    Returns:
        WeatherAnalysisResponse with prediction and correlation insight
    """
    try:
        logger.info(f"Received weather analysis request (rainfall: {request.rainfall}mm)")
        
        # Load model package
        model_pkg = load_weather_model()
        model = model_pkg['model']
        insight = model_pkg.get('insight', 'Weather analysis complete')
        correlations = model_pkg.get('correlations', {})
        
        # Prepare features array
        features = np.array([[
            request.rainfall,
            request.fertilizer,
            request.pesticide
        ]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        
        # Ensure non-negative prediction
        prediction = max(0, prediction)
        
        logger.info(f"Weather-based yield prediction: {prediction:.4f} tons/hectare")
        
        # Generate correlation insight
        rainfall_corr = correlations.get('Annual_Rainfall', 0)
        fertilizer_corr = correlations.get('Fertilizer', 0)
        
        if rainfall_corr != 0 and fertilizer_corr != 0:
            result_text = f"Rainfall and fertilizer show {'strong' if abs(rainfall_corr) > 0.5 else 'moderate'} positive correlation with yield ({rainfall_corr:+.2f}). "
            result_text += f"Fertilizer correlation: {fertilizer_corr:+.2f}. "
            result_text += f"Predicted yield: {prediction:.2f} tons/hectare."
        else:
            result_text = insight
        
        return WeatherAnalysisResponse(
            predicted_yield=round(prediction, 2),
            result=result_text,
            model="Weather Impact Model v1.0"
        )
    
    except Exception as e:
        logger.error(f"Weather analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/detect_pest")
async def detect_pest(file: UploadFile = File(...)):
    """
    Detect pest/disease from uploaded crop leaf image.
    
    Accepts an uploaded crop leaf image and returns:
    - Predicted disease name
    - Confidence score
    - Top 3 predictions
    
    Args:
        file: Uploaded image file (JPG, PNG, etc.)
        
    Returns:
        JSON with disease prediction and confidence
    """
    try:
        logger.info(f"Received pest detection request for file: {file.filename}")
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type: {file.content_type}. Please upload an image file."
            )
        
        # Load model if not already loaded
        model, class_labels = load_pest_model()
        
        # Read and preprocess image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Apply transforms
        transform = get_image_transform()
        image_tensor = transform(image).unsqueeze(0).to(device)
        
        # Make prediction
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
            
            # Get top 3 predictions
            top3_prob, top3_idx = torch.topk(probabilities, 3, dim=1)
        
        # Get predicted class
        predicted_class_idx = str(predicted_idx.item())
        predicted_disease = class_labels.get(predicted_class_idx, "Unknown")
        confidence_score = confidence.item()
        
        # Get top 3 predictions
        top_predictions = []
        for i in range(3):
            idx = str(top3_idx[0][i].item())
            disease_name = class_labels.get(idx, "Unknown")
            prob = top3_prob[0][i].item()
            top_predictions.append({
                "disease": disease_name,
                "confidence": round(prob, 4)
            })
        
        logger.info(f"Prediction: {predicted_disease} (confidence: {confidence_score:.4f})")
        
        return {
            "predicted_disease": predicted_disease,
            "confidence": round(confidence_score, 4),
            "top_3_predictions": top_predictions,
            "model": "ResNet18 Disease Detection v1.0",
            "device": str(device)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pest detection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": {
            "yield_model": yield_model_package is not None,
            "weather_model": weather_model_package is not None,
            "pest_model": pest_model is not None
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting FastAPI server...")
    logger.info("API will be available at: http://localhost:8000")
    logger.info("Interactive docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


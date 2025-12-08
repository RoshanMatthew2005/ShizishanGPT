"""
Pydantic Schema Models for Request/Response Validation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


# ==========================================
# REQUEST SCHEMAS
# ==========================================

class QueryRequest(BaseModel):
    """LLM/RAG Query Request"""
    query: str = Field(..., min_length=1, max_length=5000, description="User query")
    mode: str = Field(default="auto", description="Query mode: auto, react, direct, pipeline")
    
    @validator('mode')
    def validate_mode(cls, v):
        allowed = ['auto', 'react', 'direct', 'pipeline']
        if v not in allowed:
            raise ValueError(f"Mode must be one of {allowed}")
        return v


class RAGRequest(BaseModel):
    """RAG Retrieval Request"""
    query: str = Field(..., min_length=1, max_length=5000, description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")


class YieldPredictionRequest(BaseModel):
    """Yield Prediction Request"""
    crop_encoded: int = Field(..., ge=0, le=100, description="Encoded crop type")
    season_encoded: int = Field(..., ge=0, le=10, description="Encoded season")
    state_encoded: int = Field(..., ge=0, le=50, description="Encoded state")
    annual_rainfall: float = Field(..., ge=0, le=5000, description="Annual rainfall in mm")
    fertilizer: float = Field(..., ge=0, description="Fertilizer amount in kg")
    pesticide: float = Field(..., ge=0, description="Pesticide amount in kg")
    area: float = Field(..., ge=0, description="Cultivation area in hectares")


class PestDetectionRequest(BaseModel):
    """Pest Detection Request"""
    image_path: str = Field(..., min_length=1, max_length=500, description="Path to uploaded image")
    top_k: int = Field(default=3, ge=1, le=5, description="Number of predictions")


class TranslationRequest(BaseModel):
    """Translation Request"""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to translate")
    target_lang: str = Field(..., min_length=2, max_length=2, description="Target language code")
    source_lang: str = Field(default="auto", description="Source language code")
    
    @validator('target_lang', 'source_lang')
    def validate_lang(cls, v):
        if v != "auto" and len(v) != 2:
            raise ValueError("Language code must be 2 characters")
        return v.lower()


class AgentRequest(BaseModel):
    """ReAct Agent Request"""
    query: str = Field(..., min_length=1, max_length=5000, description="User query for agent")
    mode: str = Field(default="auto", description="Agent mode: auto, react, direct, pipeline")
    max_iterations: int = Field(default=5, ge=1, le=10, description="Maximum agent iterations")
    verbose: bool = Field(default=False, description="Enable verbose logging")
    
    @validator('mode')
    def validate_mode(cls, v):
        allowed = ['auto', 'react', 'direct', 'pipeline']
        if v not in allowed:
            raise ValueError(f"Mode must be one of {allowed}")
        return v


class HistoryRequest(BaseModel):
    """History Retrieval Request"""
    session_id: Optional[str] = Field(None, description="Session ID")
    limit: int = Field(default=10, ge=1, le=100, description="Number of records to retrieve")


# ==========================================
# RESPONSE SCHEMAS
# ==========================================

class StandardResponse(BaseModel):
    """Standard API Response"""
    success: bool
    message: str
    data: Any
    timestamp: str


class ErrorResponseSchema(BaseModel):
    """Error Response"""
    success: bool = False
    error: str
    status_code: int
    details: Optional[Dict] = None
    timestamp: str


class LLMResponse(BaseModel):
    """LLM Query Response"""
    final_answer: str
    tools_used: List[str] = []
    execution_time: float = 0.0
    sources: Optional[List[Dict]] = None
    confidence: Optional[float] = None


class RAGResponse(BaseModel):
    """RAG Retrieval Response"""
    documents: List[Dict]
    num_results: int
    context: str
    avg_relevance: float


class YieldPredictionResponse(BaseModel):
    """Yield Prediction Response"""
    predicted_yield: float
    unit: str = "tonnes per hectare"
    confidence: Optional[float] = None
    inputs: Dict


class PestDetectionResponse(BaseModel):
    """Pest Detection Response"""
    top_prediction: str
    confidence: float
    all_predictions: List[Dict]
    recommendations: List[str] = []


class TranslationResponse(BaseModel):
    """Translation Response"""
    translated_text: str
    source_language: str
    target_language: str
    original_text: str


class HealthResponse(BaseModel):
    """Health Check Response"""
    status: str
    version: str
    models_loaded: Dict[str, bool]
    timestamp: str

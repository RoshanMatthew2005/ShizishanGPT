"""
FastAPI Backend - Main Application
ShizishanGPT Milestone 6
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from .config import settings
from .dependencies import model_registry
from .utils.logger import setup_logging, get_logger
from .utils.error_handler import (
    validation_exception_handler,
    general_exception_handler,
    http_exception_handler
)
from .utils.response_formatter import format_success, format_error
from .utils.schema_validator import HealthResponse

# Import routers
from .routers.router_general import router as general_router
from .routers.router_models import router as models_router
from .routers.router_agent import router as agent_router  # ReAct agent enabled
from .routers.router_conversations import router as conversations_router
from .routers.router_weather import router as weather_router
from .routers.router_tavily import router as tavily_router  # Tavily search integration
from .routers.router_auth import router as auth_router  # Authentication

# Import model loaders
from .models.load_yield_model import load_yield_model
from .models.load_pest_model import load_pest_model
from .models.load_vectorstore import load_vectorstore
from .models.load_mini_llm import load_mini_llm
from .models.load_translator import load_translator

# Import services
from .services.llm_service import llm_service
from .services.rag_service import rag_service
# from .services.agent_service import agent_service  # Temporarily disabled - transformers loading issue
from .services.translate_service import translate_service
from .services.yield_service import yield_service
from .services.pest_service import pest_service
from .services.history_service import history_service
from .services.conversation_service import conversation_service

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    logger.info("=" * 60)
    logger.info("🚀 Starting ShizishanGPT FastAPI Backend")
    logger.info("=" * 60)
    
    try:
        # Load models
        logger.info("📦 Loading AI models...")
        
        # 1. Load Yield Model
        try:
            yield_model = load_yield_model(settings.YIELD_MODEL_PATH)
            model_registry.register("yield_model", yield_model)
            logger.info("✓ Yield model loaded")
        except Exception as e:
            logger.warning(f"✗ Yield model not loaded: {e}")
        
        # 2. Load Pest Model
        try:
            pest_model = load_pest_model(settings.PEST_MODEL_PATH, settings.PEST_CLASSES_PATH)
            model_registry.register("pest_model", pest_model)
            logger.info("✓ Pest model loaded")
        except Exception as e:
            logger.warning(f"✗ Pest model not loaded: {e}")
        
        # 3. Load VectorStore
        try:
            vectorstore = load_vectorstore(settings.VECTORSTORE_PATH)
            model_registry.register("vectorstore", vectorstore)
            logger.info("✓ VectorStore loaded")
        except Exception as e:
            logger.warning(f"✗ VectorStore not loaded: {e}")
        
        # 4. Load Mini LLM
        try:
            mini_llm = load_mini_llm(settings.MINI_LLM_PATH)
            model_registry.register("mini_llm", mini_llm)
            logger.info("✓ Mini LLM loaded")
        except Exception as e:
            logger.warning(f"✗ Mini LLM not loaded: {e}")
        
        # 5. Load Translator
        try:
            translator = load_translator()
            model_registry.register("translator", translator)
            logger.info("✓ Translator loaded")
        except Exception as e:
            logger.warning(f"✗ Translator not loaded: {e}")
        
        # Mark models as initialized
        model_registry.set_initialized()
        
        # Initialize MongoDB
        from .db.mongo_client import initialize_mongo
        if settings.MONGODB_ENABLED:
            try:
                initialize_mongo(
                    settings.MONGODB_URL,
                    settings.MONGODB_DB_NAME,
                    settings.MONGODB_COLLECTION,
                    settings.MONGODB_ENABLED
                )
                logger.info("✓ MongoDB initialized")
            except Exception as e:
                logger.warning(f"✗ MongoDB initialization failed: {e}")
        
        # Initialize services
        logger.info("🔧 Initializing services...")
        llm_service.initialize()
        rag_service.initialize()
        translate_service.initialize()
        yield_service.initialize()
        pest_service.initialize()
        history_service.initialize()
        conversation_service.initialize()
        logger.info("✓ Services initialized")
        
        logger.info("=" * 60)
        logger.info(f"✅ Backend ready on http://localhost:{settings.PORT}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ShizishanGPT Backend")


# Create FastAPI app
app = FastAPI(
    title="ShizishanGPT Backend",
    description="FastAPI backend for ShizishanGPT - Agricultural AI Assistant",
    version="1.0.0",
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"📨 {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = time.time() - start_time
    logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} ({duration:.2f}s)")
    
    return response


# Register routers
app.include_router(general_router)
app.include_router(models_router)
app.include_router(agent_router)  # ReAct agent enabled
app.include_router(conversations_router)
app.include_router(weather_router)  # Weather API
app.include_router(tavily_router)  # Tavily Search API
app.include_router(auth_router)  # Authentication API


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return format_success({
        "message": "ShizishanGPT Backend API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "ask": "/api/ask",
            "rag": "/api/rag",
            "agent": "/api/agent",
            "predict_yield": "/api/predict_yield",
            "detect_pest": "/api/detect_pest",
            "translate": "/api/translate",
            "weather": "/api/weather"
        }
    })


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns service status and loaded models
    """
    models_loaded = {
        "yield_model": model_registry.has("yield_model"),
        "pest_model": model_registry.has("pest_model"),
        "vectorstore": model_registry.has("vectorstore"),
        "mini_llm": model_registry.has("mini_llm"),
        "translator": model_registry.has("translator")
    }
    
    all_loaded = all(models_loaded.values())
    
    return {
        "status": "healthy" if all_loaded else "degraded",
        "version": "1.0.0",
        "models_loaded": models_loaded,
        "timestamp": str(time.time())
    }


# Register exception handlers
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on port {settings.PORT}")
    
    uvicorn.run(
        "src.backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # Disable reload to avoid file watch issues
        log_level="info"
    )

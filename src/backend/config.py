"""
Configuration Module for FastAPI Backend
Centralized settings and environment variables
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # API Configuration
    API_TITLE: str = "ShizishanGPT Backend API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "FastAPI backend for ShizishanGPT Agricultural AI System"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # React frontend
        "http://localhost:5000",  # Node.js middleware
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000"
    ]
    
    # Model Paths
    YIELD_MODEL_PATH: str = str(BASE_DIR / "models" / "trained_models" / "yield_model.pkl")
    PEST_MODEL_PATH: str = str(BASE_DIR / "models" / "trained_models" / "pest_model.pt")
    PEST_CLASSES_PATH: str = str(BASE_DIR / "models" / "trained_models" / "class_labels.json")
    MINI_LLM_PATH: str = str(BASE_DIR / "models" / "mini_llm")
    VECTORSTORE_PATH: str = str(BASE_DIR / "vectorstore" / "knowledge_base")
    
    # RAG Configuration
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.3
    
    # LLM Configuration
    LLM_MAX_LENGTH: int = 150
    LLM_TEMPERATURE: float = 0.9
    LLM_REPETITION_PENALTY: float = 1.5
    LLM_NO_REPEAT_NGRAM_SIZE: int = 4
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    
    # Tavily Search API Configuration
    TAVILY_API_KEY: Optional[str] = None
    
    # Neo4j Configuration (Agriculture Knowledge Graph)
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: Optional[str] = None
    
    # Gemma 2 / Ollama Configuration
    USE_GEMMA_FALLBACK: bool = False
    GEMMA_MODEL: str = "gemma2:9b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Agent Configuration
    AGENT_MAX_ITERATIONS: int = 5
    AGENT_TIMEOUT: int = 60
    
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "shizishangpt"
    MONGODB_COLLECTION: str = "query_logs"
    MONGODB_CONVERSATIONS_COLLECTION: str = "conversations"
    MONGODB_ENABLED: bool = True  # Set to True if MongoDB is available
    
    # Authentication Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production-use-env-variable"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Translation Configuration
    TRANSLATION_ENABLED: bool = True
    SUPPORTED_LANGUAGES: list = ["en", "hi", "es", "fr", "zh", "ar", "pt", "bn", "ru"]
    
    # Upload Configuration
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/jpg"]
    TEMP_UPLOAD_DIR: str = str(BASE_DIR / "temp" / "uploads")
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = str(BASE_DIR / "logs" / "backend.log")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Create necessary directories
def initialize_directories():
    """Create required directories if they don't exist"""
    dirs = [
        Path(settings.TEMP_UPLOAD_DIR),
        Path(settings.LOG_FILE).parent,
        Path(settings.VECTORSTORE_PATH).parent
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)

initialize_directories()

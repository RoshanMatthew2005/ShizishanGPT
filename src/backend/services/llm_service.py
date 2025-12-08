"""
LLM Service
Handles LLM query processing with OpenAI fallback
"""

import logging
import time
import os
from typing import Dict, Any
from ..dependencies import model_registry

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for LLM operations
    """
    
    def __init__(self):
        self.llm = None
    
    def initialize(self):
        """Initialize service with loaded model"""
        if model_registry.has("mini_llm"):
            self.llm = model_registry.get("mini_llm")
        else:
            logger.warning("mini_llm model not available in registry")
            self.llm = None
    
    async def query(self, query: str, mode: str = "auto") -> Dict[str, Any]:
        """
        Process LLM query
        
        Args:
            query: User query
            mode: Query mode (auto, direct, etc.)
        
        Returns:
            Dictionary with answer and metadata
        """
        start_time = time.time()
        
        try:
            # Check if Gemma 2 is enabled first (priority over mini_llm)
            use_gemma = os.getenv("USE_GEMMA_FALLBACK", "false").lower() == "true"
            
            if use_gemma:
                logger.info("Using Gemma 2 via Ollama (priority over mini_llm)")
                return await self._openai_fallback(query, start_time)
            
            # Fallback to mini_llm if available
            if self.llm is None:
                try:
                    self.initialize()
                except Exception as e:
                    logger.warning(f"LLM model not available: {e}")
                    return await self._openai_fallback(query, start_time)
            
            # Check if model is available after initialization
            if self.llm is None:
                # Try Gemma 2 fallback
                return await self._openai_fallback(query, start_time)
            
            logger.info(f"Processing LLM query: {query[:100]}...")
            
            # Generate answer
            answer = self.llm.generate(query)
            
            execution_time = time.time() - start_time
            
            result = {
                "final_answer": answer,
                "answer": answer,
                "tools_used": ["llm"],
                "execution_time": execution_time,
                "sources": None,
                "confidence": None
            }
            
            logger.info(f"LLM query completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            raise
    
    async def _openai_fallback(self, query: str, start_time: float) -> Dict[str, Any]:
        """Fallback to Gemma 2 9B via Ollama when local model unavailable"""
        try:
            import requests
            use_gemma = os.getenv("USE_GEMMA_FALLBACK", "false").lower() == "true"
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            model = os.getenv("GEMMA_MODEL", "gemma2:9b")
            
            if not use_gemma:
                return {
                    "final_answer": "🌱 Welcome to ShizishanGPT! I'm ready to help with agriculture. Currently running in basic mode - enable Gemma 2 in .env file or use other tools like yield prediction!",
                    "tools_used": [],
                    "execution_time": time.time() - start_time,
                    "sources": None
                }
            
            # Check if Ollama is running
            try:
                requests.get(f"{ollama_url}/api/tags", timeout=5)
            except:
                return {
                    "final_answer": "🌱 ShizishanGPT is ready! Gemma 2 9B model available but Ollama service is not running. Start Ollama to enable AI chat, or use other agricultural tools!",
                    "tools_used": [],
                    "execution_time": time.time() - start_time,
                    "sources": None
                }
            
            # Prepare agricultural prompt
            agricultural_prompt = f"""You are ShizishanGPT, an expert agricultural AI assistant. Please provide helpful, accurate, and practical information about farming, crops, weather, pests, soil management, and agricultural practices.

User question: {query}

Please provide a concise, helpful response focused on agriculture."""
            
            # Call Ollama API with GPU-optimized settings
            payload = {
                "model": model,
                "prompt": agricultural_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 300,
                    "num_gpu": 32,  # Use GPU layers
                    "num_thread": 4
                }
            }
            
            response = requests.post(
                f"{ollama_url}/api/generate", 
                json=payload, 
                timeout=45  # Increased timeout for GPU warmup
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                
                return {
                    "final_answer": answer,
                    "tools_used": ["gemma2"],
                    "execution_time": time.time() - start_time,
                    "sources": None
                }
            else:
                return {
                    "final_answer": f"🌱 ShizishanGPT is ready! Gemma 2 model error (status {response.status_code}). Please check Ollama setup or use other agricultural tools.",
                    "tools_used": [],
                    "execution_time": time.time() - start_time,
                    "sources": None
                }
                
        except Exception as e:
            logger.warning(f"Gemma 2 fallback failed: {e}")
            return {
                "final_answer": "🌱 ShizishanGPT is ready for agriculture! Gemma 2 9B available but not accessible. Check Ollama service or use yield predictions, pest detection, and other farming tools.",
                "tools_used": [],
                "execution_time": time.time() - start_time,
                "sources": None
            }


# Global instance
llm_service = LLMService()

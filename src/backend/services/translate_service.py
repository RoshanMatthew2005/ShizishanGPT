"""
Translation Service
Handles translation operations
"""

import logging
import time
from typing import Dict, Any
from ..dependencies import model_registry

logger = logging.getLogger(__name__)


class TranslateService:
    """
    Service for translation operations
    """
    
    def __init__(self):
        self.translator = None
    
    def initialize(self):
        """Initialize service with loaded translator"""
        self.translator = model_registry.get("translator")
    
    async def translate(self, 
                       text: str, 
                       source_lang: str = "auto",
                       target_lang: str = "en") -> Dict[str, Any]:
        """
        Translate text
        
        Args:
            text: Text to translate
            source_lang: Source language code (auto for auto-detect)
            target_lang: Target language code
        
        Returns:
            Dictionary with translation and metadata
        """
        start_time = time.time()
        
        try:
            if self.translator is None:
                self.initialize()
            
            logger.info(f"Translating text ({source_lang} -> {target_lang})")
            
            # Translate
            result = self.translator.translate(text, source_lang, target_lang)
            
            execution_time = time.time() - start_time
            
            # Add metadata
            result["execution_time"] = execution_time
            
            logger.info(f"Translation completed in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise


# Global service instance
translate_service = TranslateService()

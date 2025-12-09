"""
Translation Service Loader
Handles text translation using googletrans
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    logger.warning("googletrans not installed. Translation will return original text.")


class TranslationService:
    """
    Wrapper for translation service
    """
    
    def __init__(self):
        self.translator = None
        self.loaded = False
        self.supported_languages = [
            "en", "hi", "es", "fr", "zh", "ar", "pt", "bn", "ru"
        ]
    
    def load(self):
        """Load the translation service"""
        try:
            if GOOGLETRANS_AVAILABLE:
                self.translator = Translator()
                self.loaded = True
                logger.info("✓ Translation service loaded (googletrans)")
            else:
                self.loaded = False
                logger.warning("Translation service not available")
            
            return self.loaded
            
        except Exception as e:
            logger.error(f"Failed to load translation service: {e}")
            self.loaded = False
            return False
    
    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "en") -> Dict[str, Any]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code (auto-detect if 'auto')
            target_lang: Target language code
        
        Returns:
            Dictionary with translation results
        """
        try:
            if not self.loaded or not GOOGLETRANS_AVAILABLE:
                # Fallback: return original text
                logger.warning("Translation service not available, returning original text")
                return {
                    "translated_text": text,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "original_text": text,
                    "detected_language": source_lang
                }
            
            # Validate language codes
            if target_lang not in self.supported_languages and target_lang != "auto":
                logger.warning(f"Unsupported target language: {target_lang}")
            
            # Perform translation
            logger.info(f"🔵 Attempting translation: text_length={len(text)}, src={source_lang}, dest={target_lang}")
            result = self.translator.translate(
                text,
                dest=target_lang,
                src=source_lang if source_lang != "auto" else "auto"
            )
            
            detected_source = result.src if hasattr(result, 'src') else source_lang
            logger.info(f"🟢 Translation result: translated_length={len(result.text)}, detected_src={detected_source}")
            
            translation_result = {
                "translated_text": result.text,
                "source_language": detected_source,
                "target_language": target_lang,
                "original_text": text,
                "detected_language": detected_source
            }
            
            logger.info(f"Translated from {detected_source} to {target_lang}")
            return translation_result
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Return original text on error
            return {
                "translated_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "original_text": text,
                "detected_language": source_lang,
                "error": str(e)
            }


def load_translator() -> TranslationService:
    """
    Factory function to load translation service
    """
    service = TranslationService()
    service.load()
    return service

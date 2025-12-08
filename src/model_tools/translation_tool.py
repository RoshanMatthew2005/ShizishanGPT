"""
Translation Tool
Provides translation capabilities for agricultural content.
Uses Google Translate API or fallback methods.
"""
from typing import Dict, Any, Optional
import re


class TranslationTool:
    """Tool for translating agricultural content between languages."""
    
    def __init__(self):
        """Initialize the Translation Tool."""
        self.name = "translation"
        self.description = "Translates agricultural text between different languages"
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'es': 'Spanish',
            'fr': 'French',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'pt': 'Portuguese',
            'bn': 'Bengali',
            'ru': 'Russian'
        }
        
        # Try to import googletrans
        self.translator = None
        self.translation_available = False
        
        try:
            from googletrans import Translator
            self.translator = Translator()
            self.translation_available = True
            print("✓ Google Translate API available")
        except ImportError:
            print("⚠ googletrans not installed. Install with: pip install googletrans==4.0.0-rc1")
            print("⚠ Translation tool will use fallback mode")
    
    def validate_input(self, text: str, target_lang: str) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters.
        
        Args:
            text: Text to translate
            target_lang: Target language code
            
        Returns:
            (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Text cannot be empty"
        
        if not target_lang:
            return False, "Target language code is required"
        
        if target_lang not in self.supported_languages:
            return False, f"Unsupported language: {target_lang}. Supported: {', '.join(self.supported_languages.keys())}"
        
        return True, None
    
    def run(self, text: str, target_lang: str = 'en', source_lang: str = 'auto') -> Dict[str, Any]:
        """
        Execute translation.
        
        Args:
            text: Text to translate
            target_lang: Target language code (default: 'en')
            source_lang: Source language code (default: 'auto' for auto-detect)
        
        Returns:
            Dictionary with translation results
        """
        try:
            # Validate input
            is_valid, error_msg = self.validate_input(text, target_lang)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "tool": self.name
                }
            
            # Use Google Translate if available
            if self.translation_available:
                try:
                    result = self.translator.translate(
                        text,
                        src=source_lang,
                        dest=target_lang
                    )
                    
                    return {
                        "success": True,
                        "tool": self.name,
                        "original_text": text,
                        "translated_text": result.text,
                        "source_language": result.src,
                        "target_language": target_lang,
                        "target_language_name": self.supported_languages[target_lang]
                    }
                except Exception as e:
                    # Fall back to simple mode if API fails
                    print(f"Translation API error: {e}, using fallback")
            
            # Fallback: Return original text with message
            return {
                "success": True,
                "tool": self.name,
                "original_text": text,
                "translated_text": text,  # No translation, return original
                "source_language": source_lang,
                "target_language": target_lang,
                "message": "Translation API not available, returning original text",
                "suggestion": "Install googletrans: pip install googletrans==4.0.0-rc1"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Translation failed: {str(e)}",
                "tool": self.name
            }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of input text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with detected language
        """
        try:
            if not self.translation_available:
                return {
                    "success": False,
                    "error": "Language detection requires googletrans library",
                    "tool": self.name
                }
            
            detection = self.translator.detect(text)
            
            return {
                "success": True,
                "tool": self.name,
                "text": text,
                "detected_language": detection.lang,
                "language_name": self.supported_languages.get(detection.lang, "Unknown"),
                "confidence": detection.confidence
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Language detection failed: {str(e)}",
                "tool": self.name
            }
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """
        Get list of supported languages.
        
        Returns:
            Dictionary with supported languages
        """
        return {
            "success": True,
            "tool": self.name,
            "languages": self.supported_languages,
            "total": len(self.supported_languages)
        }
    
    def __call__(self, text: str, target_lang: str = 'en', source_lang: str = 'auto') -> Dict[str, Any]:
        """Allow the tool to be called directly."""
        return self.run(text, target_lang, source_lang)


# Example usage
if __name__ == "__main__":
    tool = TranslationTool()
    
    # Test 1: Translation
    text = "Rice is the most important cereal crop for feeding the world's population."
    result1 = tool.run(text, target_lang='hi')
    
    print("\n" + "="*70)
    print("TRANSLATION TEST")
    print("="*70)
    print(f"Original: {result1.get('original_text', '')[:80]}...")
    print(f"Success: {result1['success']}")
    if result1['success']:
        print(f"Target Language: {result1.get('target_language_name', 'N/A')}")
        print(f"Translated: {result1.get('translated_text', '')[:80]}...")
        if 'message' in result1:
            print(f"Note: {result1['message']}")
    print("="*70)
    
    # Test 2: Supported languages
    result2 = tool.get_supported_languages()
    print("\n" + "="*70)
    print("SUPPORTED LANGUAGES")
    print("="*70)
    print(f"Total: {result2['total']} languages")
    for code, name in list(result2['languages'].items())[:5]:
        print(f"  {code}: {name}")
    print("  ...")
    print("="*70)

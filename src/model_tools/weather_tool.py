"""
Weather Prediction Tool
Loads weather model and predicts weather impacts on agriculture.
"""
import pickle
import joblib
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np


class WeatherTool:
    """Tool for predicting weather impacts and patterns for agriculture."""
    
    def __init__(self, model_path: str = "models/trained_models/weather_model.pkl"):
        """
        Initialize the Weather Prediction Tool.
        
        Args:
            model_path: Path to the trained weather model
        """
        self.name = "weather_prediction"
        self.description = "Predicts weather patterns and impacts on crop growth"
        self.model_path = Path(model_path)
        self.model = None
        self.correlations = None
        self.insight = None
        self.feature_names = None
        self.is_loaded = False
        
    def load_model(self) -> bool:
        """Load the trained model from disk."""
        try:
            if not self.model_path.exists():
                print(f"⚠ Weather model not found: {self.model_path}")
                print(f"⚠ Please train the model using: python src/train_weather_model.py")
                return False
            
            # Load model package (contains model, correlations, insight)
            model_package = joblib.load(self.model_path)
            self.model = model_package['model']
            self.correlations = model_package.get('correlations', {})
            self.insight = model_package.get('insight', '')
            self.feature_names = model_package.get('feature_names', ['Annual_Rainfall', 'Fertilizer', 'Pesticide'])
            
            self.is_loaded = True
            print(f"✓ Weather model loaded from {self.model_path}")
            print(f"✓ Rainfall-Yield correlation: {self.correlations.get('Annual_Rainfall', 0):+.4f}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading weather model: {e}")
            return False
    
    def validate_input(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters.
        
        Args:
            params: Dictionary with weather parameters
            
        Returns:
            (is_valid, error_message)
        """
        # If model is not trained, provide placeholder validation
        if not self.is_loaded:
            # Basic validation for weather query
            if 'query' not in params and 'temperature' not in params and 'rainfall' not in params:
                return False, "Must provide weather query or parameters (temperature, rainfall, etc.)"
        
        return True, None
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Execute weather prediction or analysis.
        
        Args:
            **kwargs: Weather parameters or query
                - query: str (natural language weather question)
                - temperature: float (optional)
                - rainfall: float (optional)
                - humidity: float (optional)
        
        Returns:
            Dictionary with prediction results
        """
        try:
            # Load model if not already loaded
            if not self.is_loaded:
                if not self.load_model():
                    # Model not trained - provide informative fallback
                    return {
                        "success": False,
                        "error": "Weather model not trained yet",
                        "suggestion": "Train the model using: python src/train_weather_model.py",
                        "tool": self.name,
                        "fallback_message": "Weather prediction requires trained LSTM model. Please train the model first."
                    }
            
            # Validate input
            is_valid, error_msg = self.validate_input(kwargs)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "tool": self.name
                }
            
            # TODO: Implement actual model inference once model is trained
            # For now, return placeholder structure
            
            return {
                "success": True,
                "tool": self.name,
                "message": "Weather model inference not yet implemented",
                "inputs": kwargs
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Weather prediction failed: {str(e)}",
                "tool": self.name
            }
    
    def get_weather_advice(self, query: str) -> Dict[str, Any]:
        """
        Get weather-related agricultural advice based on query.
        
        Args:
            query: Natural language weather question
            
        Returns:
            Dictionary with advice
        """
        # Fallback knowledge-based responses when model not available
        advice_map = {
            "rainfall": "Adequate rainfall (600-1200mm annually) is crucial for most crops. Monitor soil moisture and use irrigation during dry periods.",
            "temperature": "Optimal temperature varies by crop. Most crops thrive between 20-30°C. Extreme temperatures affect photosynthesis and yield.",
            "drought": "During drought: use mulching, drip irrigation, drought-resistant varieties, and reduce fertilizer application.",
            "flood": "Prevent waterlogging with proper drainage, avoid over-irrigation, and plant flood-tolerant varieties in prone areas.",
            "heat": "Heat stress mitigation: adequate watering, shade nets, heat-tolerant varieties, and adjust planting dates.",
            "frost": "Protect from frost: row covers, windbreaks, frost-resistant varieties, and avoid planting in frost-prone periods."
        }
        
        query_lower = query.lower()
        for key, advice in advice_map.items():
            if key in query_lower:
                return {
                    "success": True,
                    "tool": self.name,
                    "query": query,
                    "advice": advice,
                    "source": "knowledge_base"
                }
        
        return {
            "success": True,
            "tool": self.name,
            "query": query,
            "advice": "Weather significantly impacts agriculture. Monitor local forecasts and adjust farming practices accordingly.",
            "source": "general"
        }
    
    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Allow the tool to be called directly."""
        if 'query' in kwargs and isinstance(kwargs['query'], str):
            return self.get_weather_advice(kwargs['query'])
        return self.run(**kwargs)


# Example usage
if __name__ == "__main__":
    tool = WeatherTool()
    
    # Test 1: Query-based advice
    result1 = tool(query="What are the effects of drought on crops?")
    print("\n" + "="*70)
    print("WEATHER ADVICE TEST")
    print("="*70)
    print(f"Query: {result1.get('query')}")
    print(f"Success: {result1['success']}")
    if result1['success']:
        print(f"Advice: {result1['advice']}")
    print("="*70)
    
    # Test 2: Model prediction (will show not trained message)
    result2 = tool.run(temperature=25.0, rainfall=800.0)
    print("\n" + "="*70)
    print("WEATHER PREDICTION TEST")
    print("="*70)
    print(f"Success: {result2['success']}")
    if not result2['success']:
        print(f"Message: {result2.get('fallback_message', result2.get('error'))}")
    print("="*70)

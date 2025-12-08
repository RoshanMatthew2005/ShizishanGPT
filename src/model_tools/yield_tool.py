"""
Yield Prediction Tool
Loads the trained Random Forest model and predicts crop yield.
"""
import joblib
import re
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

try:
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ scikit-learn not installed. Yield prediction will be limited.")

# Crop name to encoding mapping (based on training data)
CROP_MAPPING = {
    'wheat': 53, 'rice': 40, 'maize': 24, 'bajra': 2, 'jowar': 20,
    'ragi': 38, 'barley': 4, 'gram': 16, 'arhar': 1, 'tur': 1,
    'moong': 27, 'urad': 52, 'masoor': 25, 'groundnut': 17,
    'soyabean': 45, 'sunflower': 47, 'safflower': 41, 'cotton': 11,
    'jute': 21, 'sugarcane': 46, 'potato': 37, 'onion': 31,
    'garlic': 14, 'ginger': 15, 'turmeric': 51, 'coriander': 10,
    'rapeseed': 39, 'mustard': 39, 'linseed': 23, 'castor': 8,
    'sesamum': 43, 'coconut': 9, 'arecanut': 0, 'cashewnut': 7,
    'banana': 3, 'tapioca': 49, 'sweet potato': 48
}

# State name to encoding mapping
STATE_MAPPING = {
    'andhra pradesh': 0, 'andhra': 0, 'ap': 0,
    'arunachal pradesh': 1, 'arunachal': 1,
    'assam': 2,
    'bihar': 3,
    'chhattisgarh': 4,
    'delhi': 5,
    'goa': 6,
    'gujarat': 7,
    'haryana': 8,
    'himachal pradesh': 9, 'himachal': 9, 'hp': 9,
    'jammu and kashmir': 10, 'j&k': 10, 'jammu': 10, 'kashmir': 10,
    'jharkhand': 11,
    'karnataka': 12,
    'kerala': 13,
    'madhya pradesh': 14, 'madhya': 14, 'mp': 14,
    'maharashtra': 15,
    'manipur': 16,
    'meghalaya': 17,
    'mizoram': 18,
    'nagaland': 19,
    'odisha': 20, 'orissa': 20,
    'punjab': 21,
    'rajasthan': 22,
    'sikkim': 23,
    'tamil nadu': 24, 'tamilnadu': 24, 'tn': 24,
    'telangana': 25,
    'tripura': 26,
    'uttar pradesh': 27, 'up': 27,
    'uttarakhand': 28,
    'west bengal': 29, 'bengal': 29, 'wb': 29
}

# Season name to encoding mapping
SEASON_MAPPING = {
    'kharif': 1, 'monsoon': 1, 'rainy': 1,
    'rabi': 2, 'winter': 2,
    'summer': 3, 'zaid': 3,
    'autumn': 0,
    'whole year': 4, 'year round': 4, 'perennial': 4,
    'spring': 5
}


class YieldTool:
    """Tool for predicting crop yield based on various agricultural parameters."""
    
    def __init__(self, model_path: str = "models/trained_models/yield_model.pkl"):
        """
        Initialize the Yield Prediction Tool.
        
        Args:
            model_path: Path to the trained yield model
        """
        self.name = "yield_prediction"
        self.description = "Predicts crop yield based on crop type, location, rainfall, fertilizer, and pesticide usage"
        self.model_path = Path(model_path)
        self.model = None
        self.encoders = {}
        self.feature_names = []
        self.is_loaded = False
        
    def load_model(self) -> bool:
        """Load the trained model from disk."""
        try:
            if not SKLEARN_AVAILABLE:
                print(f"❌ scikit-learn not available for yield model")
                return False
                
            if not self.model_path.exists():
                print(f"❌ Model not found: {self.model_path}")
                return False
            
            # Load model package using joblib (includes model + encoders)
            model_package = joblib.load(self.model_path)
            
            # Extract model from package
            if isinstance(model_package, dict):
                self.model = model_package.get('model')
                self.encoders = model_package.get('encoders', {})
                self.feature_names = model_package.get('feature_names', [])
            else:
                # Old format - just the model
                self.model = model_package
                self.encoders = {}
                self.feature_names = []
            
            self.is_loaded = True
            print(f"✓ Yield model loaded from {self.model_path}")
            return True
            
        except ModuleNotFoundError as e:
            print(f"❌ Error loading yield model (missing module): {e}")
            print(f"ℹ️ Using rule-based fallback for yield predictions")
            self.is_loaded = False
            return False
        except Exception as e:
            print(f"❌ Error loading yield model: {e}")
            print(f"ℹ️ Using rule-based fallback for yield predictions")
            self.is_loaded = False
            return False
    
    def parse_natural_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Parse natural language query and extract parameters.
        
        Args:
            query: Natural language query
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with parsed parameters
        """
        query_lower = query.lower()
        params = {}
        
        # Extract crop
        crop_encoded = kwargs.get('crop_encoded') or kwargs.get('crop')
        if crop_encoded is None or isinstance(crop_encoded, str):
            for crop_name, code in CROP_MAPPING.items():
                if crop_name in query_lower:
                    crop_encoded = code
                    print(f"✓ Detected crop: {crop_name} (code: {code})")
                    break
        params['crop_encoded'] = int(crop_encoded) if crop_encoded is not None else 53  # Default: wheat
        
        # Extract state
        state_encoded = kwargs.get('state_encoded') or kwargs.get('state')
        if state_encoded is None or isinstance(state_encoded, str):
            for state_name, code in STATE_MAPPING.items():
                if state_name in query_lower:
                    state_encoded = code
                    print(f"✓ Detected state: {state_name} (code: {code})")
                    break
        params['state_encoded'] = int(state_encoded) if state_encoded is not None else 21  # Default: Punjab
        
        # Extract season
        season_encoded = kwargs.get('season_encoded') or kwargs.get('season')
        if season_encoded is None or isinstance(season_encoded, str):
            for season_name, code in SEASON_MAPPING.items():
                if season_name in query_lower:
                    season_encoded = code
                    print(f"✓ Detected season: {season_name} (code: {code})")
                    break
        params['season_encoded'] = int(season_encoded) if season_encoded is not None else 2  # Default: Rabi
        
        # Extract rainfall
        rainfall_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:mm|millimeter)?\s*rainfall', query_lower)
        if rainfall_match:
            params['annual_rainfall'] = float(rainfall_match.group(1))
            print(f"✓ Detected rainfall: {params['annual_rainfall']}mm")
        else:
            params['annual_rainfall'] = float(kwargs.get('annual_rainfall', 800.0))
        
        # Extract or use defaults for other parameters
        params['fertilizer'] = float(kwargs.get('fertilizer', 50000.0))  # Default: 50kg/ha
        params['pesticide'] = float(kwargs.get('pesticide', 200.0))  # Default: 200g/ha
        params['area'] = float(kwargs.get('area', 1000.0))  # Default: 1000 ha
        
        return params
    
    def validate_input(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters.
        
        Args:
            params: Dictionary with prediction parameters
            
        Returns:
            (is_valid, error_message)
        """
        required_fields = ['crop_encoded', 'season_encoded', 'state_encoded', 
                          'annual_rainfall', 'fertilizer', 'pesticide', 'area']
        
        for field in required_fields:
            if field not in params:
                return False, f"Missing required field: {field}"
        
        # Validate numeric fields
        numeric_fields = ['annual_rainfall', 'fertilizer', 'pesticide', 'area']
        for field in numeric_fields:
            try:
                float(params[field])
            except (ValueError, TypeError):
                return False, f"Field '{field}' must be numeric"
        
        # Validate encoded fields are integers
        encoded_fields = ['crop_encoded', 'season_encoded', 'state_encoded']
        for field in encoded_fields:
            try:
                int(params[field])
            except (ValueError, TypeError):
                return False, f"Field '{field}' must be an integer"
        
        return True, None
    
    def run(self, query: str = "", **kwargs) -> Dict[str, Any]:
        """
        Execute yield prediction.
        
        Args:
            query: Natural language query (e.g., "Predict yield for wheat in Punjab with 800mm rainfall")
            **kwargs: Prediction parameters (optional, will auto-extract from query)
                - crop / crop_encoded: str or int
                - state / state_encoded: str or int
                - season / season_encoded: str or int
                - annual_rainfall: float
                - fertilizer: float
                - pesticide: float
                - area: float
        
        Returns:
            Dictionary with prediction results
        """
        try:
            # Load model if not already loaded
            if not self.is_loaded:
                if not self.load_model():
                    # Provide fallback response with general guidance
                    rainfall = kwargs.get('annual_rainfall', 100)
                    
                    if rainfall < 200:
                        yield_estimate = "Low (1-2 tonnes/ha) due to insufficient rainfall"
                    elif rainfall < 600:
                        yield_estimate = "Moderate (2-4 tonnes/ha) with adequate rainfall"
                    else:
                        yield_estimate = "Good (3-6 tonnes/ha) with sufficient rainfall"
                    
                    return {
                        "success": True,
                        "tool": self.name,
                        "prediction": yield_estimate,
                        "unit": "estimated range",
                        "note": "Fallback estimation (model not available)",
                        "rainfall": rainfall,
                        "recommendation": f"With {rainfall}mm rainfall, consider drought-resistant varieties and efficient irrigation."
                    }
            
            # Parse query and merge with kwargs
            if query:
                parsed_params = self.parse_natural_query(query, **kwargs)
            else:
                parsed_params = kwargs
            
            # Validate input
            is_valid, error_msg = self.validate_input(parsed_params)
            if not is_valid:
                # Try to parse from query if validation fails
                if query and not is_valid:
                    print(f"⚠️ Initial validation failed: {error_msg}")
                    print(f"🔄 Attempting to parse query: '{query}'")
                    parsed_params = self.parse_natural_query(query, **kwargs)
                    is_valid, error_msg = self.validate_input(parsed_params)
                
                if not is_valid:
                    return {
                        "success": False,
                        "error": error_msg,
                        "tool": self.name,
                        "suggestion": "Please provide: crop name, state, and rainfall amount"
                    }
            
            # Prepare features in correct order
            features = np.array([[
                parsed_params['crop_encoded'],
                parsed_params['season_encoded'],
                parsed_params['state_encoded'],
                parsed_params['annual_rainfall'],
                parsed_params['fertilizer'],
                parsed_params['pesticide'],
                parsed_params['area']
            ]])
            
            # Make prediction
            prediction = self.model.predict(features)[0]
            
            # Get crop/state names for better output
            crop_name = next((k for k, v in CROP_MAPPING.items() if v == parsed_params['crop_encoded']), 'Unknown')
            state_name = next((k for k, v in STATE_MAPPING.items() if v == parsed_params['state_encoded']), 'Unknown')
            season_name = next((k for k, v in SEASON_MAPPING.items() if v == parsed_params['season_encoded']), 'Unknown')
            
            return {
                "success": True,
                "tool": self.name,
                "prediction": float(prediction),
                "unit": "tonnes per hectare",
                "crop": crop_name.title(),
                "state": state_name.title(),
                "season": season_name.title(),
                "inputs": {
                    "crop_encoded": parsed_params['crop_encoded'],
                    "season_encoded": parsed_params['season_encoded'],
                    "state_encoded": parsed_params['state_encoded'],
                    "rainfall": parsed_params['annual_rainfall'],
                    "fertilizer": parsed_params['fertilizer'],
                    "pesticide": parsed_params['pesticide'],
                    "area": parsed_params['area']
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Yield prediction failed: {str(e)}",
                "tool": self.name
            }
    
    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Allow the tool to be called directly."""
        return self.run(**kwargs)


# Example usage
if __name__ == "__main__":
    tool = YieldTool()
    
    # Test prediction
    result = tool.run(
        crop_encoded=0,
        season_encoded=2,
        state_encoded=15,
        annual_rainfall=800.0,
        fertilizer=50000.0,
        pesticide=200.0,
        area=1000.0
    )
    
    print("\n" + "="*70)
    print("YIELD PREDICTION TEST")
    print("="*70)
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Predicted Yield: {result['prediction']:.2f} {result['unit']}")
    else:
        print(f"Error: {result['error']}")
    print("="*70)

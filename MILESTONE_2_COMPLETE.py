"""
ShizishanGPT - Milestone 2 Complete
=====================================

✅ MILESTONE 2 IMPLEMENTATION COMPLETE

This milestone successfully implements two machine learning models using the crop_yield.csv dataset
and creates FastAPI endpoints to access both models.

FILES CREATED:
--------------

1. src/train_yield_model.py
   - Loads crop_yield.csv dataset
   - Preprocesses data (handles missing values, encodes categorical features)
   - Trains RandomForestRegressor for crop yield prediction
   - Features: Crop, Season, State, Annual_Rainfall, Fertilizer, Pesticide, Area
   - Target: Yield
   - Saves model to: models/trained_models/yield_model.pkl
   - Prints R² and RMSE metrics

2. src/train_weather_model.py
   - Uses the same crop_yield.csv dataset
   - Focuses on weather-related features: Annual_Rainfall, Fertilizer, Pesticide
   - Computes correlation coefficients between rainfall and yield
   - Trains RandomForestRegressor for weather impact analysis
   - Saves model to: models/trained_models/weather_model.pkl
   - Prints correlation insights (e.g., "Rainfall has a +0.82 correlation with Yield")

3. src/api_routes.py
   - FastAPI backend with two endpoints:
   
   a) POST /predict_yield
      Input: crop, state, season, rainfall, fertilizer, pesticide, area
      Output: predicted_yield, unit, model version
      
   b) POST /analyze_weather
      Input: rainfall, fertilizer, pesticide
      Output: predicted_yield, correlation result, model version
   
   - Includes proper error handling and logging
   - Loads .pkl models automatically on startup
   - Provides structured JSON responses

NEXT STEPS TO RUN:
------------------

1. Train the Yield Model:
   python src/train_yield_model.py

2. Train the Weather Model:
   python src/train_weather_model.py

3. Start the API Server:
   python src/api_routes.py
   
   OR
   
   uvicorn src.api_routes:app --reload --port 8000

4. Test the API:
   Visit http://localhost:8000/docs for interactive API documentation

SAMPLE API REQUESTS:
--------------------

# Yield Prediction
POST http://localhost:8000/predict_yield
{
  "crop": "Rice",
  "state": "Punjab",
  "season": "Kharif",
  "rainfall": 820,
  "fertilizer": 180,
  "pesticide": 90,
  "area": 5000
}

# Weather Analysis
POST http://localhost:8000/analyze_weather
{
  "rainfall": 800,
  "fertilizer": 150,
  "pesticide": 75
}

TECH STACK:
-----------
- pandas: Data loading and manipulation
- numpy: Numerical operations
- scikit-learn: Machine learning models and preprocessing
- joblib: Model serialization
- fastapi: REST API framework
- uvicorn: ASGI server
- pydantic: Request/response validation

FEATURES IMPLEMENTED:
---------------------
✅ Data loading from CSV
✅ Missing value handling
✅ Categorical encoding (LabelEncoder)
✅ Train/test split (80/20)
✅ RandomForest regression models
✅ R² and RMSE metrics
✅ Feature importance analysis
✅ Correlation analysis
✅ Model persistence (.pkl files)
✅ FastAPI endpoints with validation
✅ Error handling and logging
✅ Type hints and docstrings
✅ Structured JSON responses

✅ Milestone 2 complete — models trained and APIs ready.

"""

if __name__ == "__main__":
    print(__doc__)

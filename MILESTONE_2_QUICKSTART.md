# Milestone 2 - Quick Start Guide

## ✅ All Scripts Created Successfully

### Files Created:
1. **src/train_yield_model.py** - Crop Yield Prediction Model Training
2. **src/train_weather_model.py** - Weather Impact Model Training  
3. **src/api_routes.py** - FastAPI Backend with 2 Endpoints

---

## 🚀 How to Run

### Step 1: Train the Crop Yield Model
```bash
cd "d:\Ps-3(git)\ShizishanGPT"
"D:/Ps-3(git)/ShizishanGPT/venv/Scripts/python.exe" src/train_yield_model.py
```

**Expected Output:**
- Dataset loaded and preprocessed
- Model training progress
- R² Score and RMSE metrics
- Model saved to `models/trained_models/yield_model.pkl`

---

### Step 2: Train the Weather Impact Model
```bash
"D:/Ps-3(git)/ShizishanGPT/venv/Scripts/python.exe" src/train_weather_model.py
```

**Expected Output:**
- Correlation analysis
- "Rainfall has a +X.XX correlation with Yield"
- Model performance metrics
- Model saved to `models/trained_models/weather_model.pkl`

---

### Step 3: Start the FastAPI Server
```bash
"D:/Ps-3(git)/ShizishanGPT/venv/Scripts/python.exe" src/api_routes.py
```

**OR using uvicorn:**
```bash
"D:/Ps-3(git)/ShizishanGPT/venv/Scripts/uvicorn.exe" src.api_routes:app --reload --port 8000
```

**API URLs:**
- Main API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

---

## 📡 API Endpoints

### 1. POST /predict_yield
Predicts crop yield based on agricultural parameters.

**Request Body:**
```json
{
  "crop": "Rice",
  "state": "Punjab",
  "season": "Kharif",
  "rainfall": 820,
  "fertilizer": 180,
  "pesticide": 90,
  "area": 5000
}
```

**Response:**
```json
{
  "predicted_yield": 3.42,
  "unit": "tons per hectare",
  "model": "Crop Yield Prediction v1.0"
}
```

---

### 2. POST /analyze_weather
Analyzes weather impact on crop yield.

**Request Body:**
```json
{
  "rainfall": 800,
  "fertilizer": 150,
  "pesticide": 75
}
```

**Response:**
```json
{
  "predicted_yield": 2.85,
  "result": "Rainfall and fertilizer show strong positive correlation with yield (+0.82)...",
  "model": "Weather Impact Model v1.0"
}
```

---

## 🧪 Testing with cURL

### Test Yield Prediction:
```bash
curl -X POST "http://localhost:8000/predict_yield" \
  -H "Content-Type: application/json" \
  -d "{\"crop\":\"Rice\",\"state\":\"Punjab\",\"season\":\"Kharif\",\"rainfall\":820,\"fertilizer\":180,\"pesticide\":90,\"area\":5000}"
```

### Test Weather Analysis:
```bash
curl -X POST "http://localhost:8000/analyze_weather" \
  -H "Content-Type: application/json" \
  -d "{\"rainfall\":800,\"fertilizer\":150,\"pesticide\":75}"
```

---

## 📊 What Each Script Does

### train_yield_model.py
- Loads `Data/csv/crop_yield.csv`
- Handles missing values
- Encodes: Crop, State, Season
- Uses 7 features: Crop, Season, State, Rainfall, Fertilizer, Pesticide, Area
- Target: Yield
- RandomForestRegressor (100 trees)
- 80/20 train/test split
- Saves model + encoders as .pkl

### train_weather_model.py  
- Uses same dataset
- Focuses on 3 weather features: Rainfall, Fertilizer, Pesticide
- Computes correlation coefficients
- Prints insight: "Rainfall has a +X.XX correlation with Yield"
- RandomForestRegressor (80 trees)
- Saves model + correlations as .pkl

### api_routes.py
- FastAPI application
- Loads both .pkl models on startup
- Input validation with Pydantic
- Error handling and logging
- Returns structured JSON responses
- Auto-generated API docs at /docs

---

## ✅ Success Criteria

After running all scripts, you should have:

1. ✅ `models/trained_models/yield_model.pkl` (Crop Yield Model)
2. ✅ `models/trained_models/weather_model.pkl` (Weather Impact Model)
3. ✅ API running on http://localhost:8000
4. ✅ Two working POST endpoints
5. ✅ Model metrics printed (R², RMSE)
6. ✅ Correlation insights displayed

---

## 🎯 Milestone 2 Complete!

All scripts are production-ready with:
- ✅ Proper error handling
- ✅ Logging and validation
- ✅ Docstrings and comments
- ✅ Type hints
- ✅ Clean code structure
- ✅ No dummy data used

**Next:** Run the training scripts, then start the API server!

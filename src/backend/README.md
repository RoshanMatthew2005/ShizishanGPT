# FastAPI Backend - Installation & Setup Guide

## Overview
Complete FastAPI backend for ShizishanGPT agricultural AI assistant, connecting all AI components with RESTful API endpoints.

## Architecture
```
FastAPI Backend (Port 8000)
├── Routers (API Endpoints)
│   ├── /api/ask - Mini LLM queries
│   ├── /api/rag - RAG document retrieval
│   ├── /api/agent - ReAct agent orchestration
│   ├── /api/predict_yield - Yield prediction
│   ├── /api/detect_pest - Pest detection
│   └── /api/translate - Translation service
├── Services (Business Logic)
│   ├── llm_service - LLM processing
│   ├── rag_service - Vector search
│   ├── agent_service - ReAct orchestration
│   ├── yield_service - Yield prediction
│   ├── pest_service - Pest detection
│   ├── translate_service - Translation
│   └── history_service - Query logging
├── Models (AI Model Loaders)
│   ├── load_mini_llm - DistilGPT-2
│   ├── load_vectorstore - ChromaDB
│   ├── load_yield_model - RandomForest
│   ├── load_pest_model - ResNet18
│   └── load_translator - Translation API
├── Utils (Utilities)
│   ├── logger - Logging setup
│   ├── response_formatter - JSON responses
│   ├── error_handler - Exception handling
│   └── schema_validator - Pydantic models
├── Database (MongoDB)
│   └── mongo_client - Query logging
└── Config (Settings)
    ├── config.py - Configuration
    └── dependencies.py - ModelRegistry
```

## Installation

### Prerequisites
- Python 3.8+
- Completed Milestone 3 (Mini LLM)
- Completed Milestone 4 (Mini LangChain)
- Trained models available

### Step 1: Install Dependencies
```powershell
cd d:\Ps-3(git)\ShizishanGPT
pip install -r src/backend/requirements.txt
```

### Step 2: Configure Environment
Create `.env` file in project root:
```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Model Paths
YIELD_MODEL_PATH=models/yield_model.pkl
PEST_MODEL_PATH=Model/best_plant_disease_model.pth
VECTORSTORE_PATH=vectorstore
LLM_MODEL_PATH=fine_tuned_agri_mini_llm

# MongoDB (Optional)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=shizishangpt
MONGODB_COLLECTION=query_logs

# LLM Configuration
MAX_LENGTH=150
TEMPERATURE=0.9

# Upload Limits
MAX_UPLOAD_SIZE=10485760
```

### Step 3: Verify Model Files
Ensure these files exist:
- `models/yield_model.pkl` - RandomForest yield model
- `Model/best_plant_disease_model.pth` - ResNet18 pest model
- `vectorstore/` - ChromaDB vectorstore
- `fine_tuned_agri_mini_llm/` - DistilGPT-2 LLM

### Step 4: Start Backend Server
```powershell
cd src/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Or use the main.py directly:
```powershell
python src/backend/main.py
```

## API Endpoints

### 1. Health Check
```http
GET /health
```
Returns service status and loaded models.

### 2. Ask LLM
```http
POST /api/ask
Content-Type: application/json

{
  "query": "What is crop rotation?",
  "mode": "auto"
}
```

### 3. RAG Query
```http
POST /api/rag
Content-Type: application/json

{
  "query": "wheat cultivation",
  "top_k": 5
}
```

### 4. ReAct Agent
```http
POST /api/agent
Content-Type: application/json

{
  "query": "Predict yield for wheat in Punjab with 800mm rainfall",
  "mode": "auto",
  "max_iterations": 5
}
```

### 5. Predict Yield
```http
POST /api/predict_yield
Content-Type: application/json

{
  "crop": "Wheat",
  "season": "Rabi",
  "state": "Punjab",
  "rainfall": 800.0,
  "fertilizer": 120.0,
  "pesticide": 0.5,
  "area": 2.0
}
```

### 6. Detect Pest
```http
POST /api/detect_pest
Content-Type: multipart/form-data

file: <image_file>
top_k: 3
```

### 7. Translate
```http
POST /api/translate
Content-Type: application/json

{
  "text": "Hello farmer",
  "source_lang": "en",
  "target_lang": "hi"
}
```

## Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    "answer": "...",
    "execution_time": 0.5
  },
  "timestamp": "2025-12-01T10:30:00"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "timestamp": "2025-12-01T10:30:00"
}
```

## Testing

### Using cURL
```powershell
# Health check
curl http://localhost:8000/health

# Ask LLM
curl -X POST http://localhost:8000/api/ask `
  -H "Content-Type: application/json" `
  -d '{\"query\":\"What is NPK?\"}'

# Predict yield
curl -X POST http://localhost:8000/api/predict_yield `
  -H "Content-Type: application/json" `
  -d '{\"crop\":\"Wheat\",\"season\":\"Rabi\",\"state\":\"Punjab\",\"rainfall\":800,\"fertilizer\":120,\"pesticide\":0.5,\"area\":2}'
```

### Using Python
```python
import requests

# Ask LLM
response = requests.post(
    "http://localhost:8000/api/ask",
    json={"query": "What is crop rotation?"}
)
print(response.json())

# Predict yield
response = requests.post(
    "http://localhost:8000/api/predict_yield",
    json={
        "crop": "Wheat",
        "season": "Rabi",
        "state": "Punjab",
        "rainfall": 800.0,
        "fertilizer": 120.0,
        "pesticide": 0.5,
        "area": 2.0
    }
)
print(response.json())
```

## Integration with Node.js Middleware

The FastAPI backend is designed to work with the Node.js middleware (Milestone 5):

```
React Frontend (3000) → Node.js Middleware (5000) → FastAPI Backend (8000)
```

Update Node.js middleware `.env`:
```env
FASTAPI_BASE_URL=http://localhost:8000
```

## Troubleshooting

### Models Not Loading
- Check model file paths in `.env`
- Verify model files exist
- Check logs in `logs/backend.log`

### MongoDB Connection Failed
- MongoDB is optional, backend will work without it
- To disable: Set `MONGODB_URI=` (empty)

### Translation Service Unavailable
- Translation uses googletrans API
- Will fallback to returning original text if unavailable

### Port Already in Use
```powershell
# Change port in .env
PORT=8001
```

## Project Structure
```
src/backend/
├── main.py                 # FastAPI application
├── config.py              # Configuration
├── dependencies.py        # ModelRegistry
├── requirements.txt       # Dependencies
├── routers/
│   ├── router_general.py  # /ask, /rag, /translate
│   ├── router_models.py   # /predict_yield, /detect_pest
│   └── router_agent.py    # /agent
├── services/
│   ├── llm_service.py
│   ├── rag_service.py
│   ├── agent_service.py
│   ├── translate_service.py
│   ├── yield_service.py
│   ├── pest_service.py
│   └── history_service.py
├── models/
│   ├── load_mini_llm.py
│   ├── load_vectorstore.py
│   ├── load_yield_model.py
│   ├── load_pest_model.py
│   └── load_translator.py
├── utils/
│   ├── logger.py
│   ├── response_formatter.py
│   ├── error_handler.py
│   └── schema_validator.py
└── db/
    └── mongo_client.py
```

## Next Steps
1. Start the backend server
2. Test all endpoints
3. Integrate with Node.js middleware
4. Connect React frontend
5. Deploy to production

## Support
Check logs in `logs/backend.log` for detailed error messages and debugging information.

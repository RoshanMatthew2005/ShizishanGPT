# 🚀 FastAPI Backend - Quick Start Guide

## Start the Backend (One Command)

```powershell
cd d:\Ps-3(git)\ShizishanGPT
python src/backend/main.py
```

## Test All Endpoints (One Command)

```powershell
python src/backend/test_backend.py
```

## Quick API Tests

### 1. Health Check
```powershell
curl http://localhost:8000/health
```

### 2. Ask a Question
```powershell
curl -X POST http://localhost:8000/api/ask -H "Content-Type: application/json" -d '{\"query\":\"What is crop rotation?\"}'
```

### 3. Predict Yield
```powershell
curl -X POST http://localhost:8000/api/predict_yield -H "Content-Type: application/json" -d '{\"crop\":\"Wheat\",\"season\":\"Rabi\",\"state\":\"Punjab\",\"rainfall\":800,\"fertilizer\":120,\"pesticide\":0.5,\"area\":2}'
```

### 4. Search Knowledge Base
```powershell
curl -X POST http://localhost:8000/api/rag -H "Content-Type: application/json" -d '{\"query\":\"wheat cultivation\",\"top_k\":3}'
```

### 5. Use ReAct Agent
```powershell
curl -X POST http://localhost:8000/api/agent -H "Content-Type: application/json" -d '{\"query\":\"What is the best fertilizer for rice?\",\"mode\":\"auto\"}'
```

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check backend status |
| `/api/ask` | POST | Query Mini LLM |
| `/api/rag` | POST | Search vectorstore |
| `/api/agent` | POST | ReAct agent with tools |
| `/api/predict_yield` | POST | Predict crop yield |
| `/api/detect_pest` | POST | Detect plant disease |
| `/api/translate` | POST | Translate text |

## Expected Startup Output

```
============================================================
🚀 Starting ShizishanGPT FastAPI Backend
============================================================
📦 Loading AI models...
✓ Yield model loaded
✓ Pest model loaded
✓ VectorStore loaded
✓ Mini LLM loaded
✓ Translator loaded
🔧 Initializing services...
✓ Services initialized
============================================================
✅ Backend ready on http://localhost:8000
============================================================
```

## Troubleshooting

### Port 8000 already in use?
```powershell
# Option 1: Change port in .env file
PORT=8001

# Option 2: Kill process on port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

### Model files not found?
Check these paths exist:
- `models/yield_model.pkl`
- `Model/best_plant_disease_model.pth`
- `vectorstore/`
- `fine_tuned_agri_mini_llm/`

### MongoDB connection error?
MongoDB is optional - backend will work without it. To disable:
```env
MONGODB_URI=
```

## Integration with Node.js Middleware

1. Start FastAPI backend (port 8000)
2. Update Node.js `.env`:
   ```env
   FASTAPI_BASE_URL=http://localhost:8000
   ```
3. Start Node.js middleware (port 5000)
4. Start React frontend (port 3000)

Full stack running:
- React: http://localhost:3000
- Node.js: http://localhost:5000
- FastAPI: http://localhost:8000

## Documentation

- **Full Guide:** `src/backend/README.md`
- **Completion Report:** `docs/MILESTONE_6_COMPLETE.md`
- **Test Suite:** `src/backend/test_backend.py`

## Need Help?

Check logs:
```powershell
cat logs/backend.log
```

View API documentation:
```
http://localhost:8000/docs
```

# ShizishanGPT Middleware - Quick Setup Guide

## 🚀 Installation (3 Steps)

### Step 1: Install Node.js Dependencies
```bash
cd middleware
npm install
```

### Step 2: Configure Environment
```bash
# Copy the example environment file
copy .env.example .env
```

Edit `.env` and set:
```env
PORT=5000
NODE_ENV=development
FASTAPI_URL=http://localhost:8000
CORS_ORIGIN=http://localhost:3000
```

### Step 3: Start the Server
```bash
npm start
```

✅ Server will run on **http://localhost:5000**

---

## 🧪 Quick Test

### Test Health Endpoint
```bash
curl http://localhost:5000/health
```

### Test LLM Query
```bash
curl -X POST http://localhost:5000/ask -H "Content-Type: application/json" -d "{\"query\": \"What is nitrogen fertilizer?\", \"mode\": \"auto\"}"
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /ask | LLM/RAG query |
| POST | /rag | RAG retrieval |
| POST | /predict_yield | Yield prediction |
| POST | /analyze_weather | Weather analysis |
| POST | /detect_pest | Pest detection |
| POST | /translate | Translation |

---

## 🔗 Architecture

```
React (3000) → Node.js (5000) → FastAPI (8000) → ML Models
```

---

## 📚 Full Documentation

See `README.md` for complete documentation, examples, and troubleshooting.

---

**Part of ShizishanGPT Agricultural AI System**

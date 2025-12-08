# ShizishanGPT Node.js Middleware

Node.js + Express API Gateway that connects the React frontend to the FastAPI backend.

## 🏗️ Architecture

```
React Frontend (port 3000)
        ↓
Node.js Middleware (port 5000) ← You are here
        ↓
FastAPI Backend (port 8000)
        ↓
Python ML Models & Services
```

## 📁 Project Structure

```
middleware/
│── package.json              # Dependencies and scripts
│── server.js                 # Main Express server
│── .env.example              # Environment variables template
│── config/
│   ├── env.js               # Environment configuration
│   └── logger.js            # Winston logger setup
│── routes/
│   ├── llmRouter.js         # LLM/RAG routes
│   ├── ragRouter.js         # RAG retrieval routes
│   ├── yieldRouter.js       # Yield prediction routes
│   ├── weatherRouter.js     # Weather analysis routes
│   ├── pestRouter.js        # Pest detection routes
│   └── translateRouter.js   # Translation routes
│── controllers/
│   ├── llmController.js     # LLM request handlers
│   ├── ragController.js     # RAG request handlers
│   ├── yieldController.js   # Yield request handlers
│   ├── weatherController.js # Weather request handlers
│   ├── pestController.js    # Pest request handlers
│   └── translateController.js # Translation request handlers
│── services/
│   ├── apiClient.js         # Axios client for FastAPI
│   ├── validator.js         # Input validation (Joi)
│   └── formatter.js         # Response formatting
│── middleware/
│   ├── requestLogger.js     # Request/response logging
│   ├── errorHandler.js      # Centralized error handling
│   └── validateInput.js     # Validation middleware
└── logs/                    # Log files directory
```

## 🚀 Installation

### 1. Install Dependencies

```bash
cd middleware
npm install
```

### 2. Configure Environment

```bash
# Copy example environment file
copy .env.example .env

# Edit .env file with your settings
notepad .env
```

### 3. Start the Server

```bash
# Development mode (with auto-restart)
npm run dev

# Production mode
npm start
```

The server will start on **http://localhost:5000**

## 📡 API Endpoints

### Health Check
```http
GET /health
```

### LLM/RAG Query
```http
POST /ask
Content-Type: application/json

{
  "query": "How to control tomato blight?",
  "mode": "auto"
}
```

### RAG Document Retrieval
```http
POST /rag
Content-Type: application/json

{
  "query": "nitrogen fertilizer benefits",
  "top_k": 3
}
```

### Yield Prediction
```http
POST /predict_yield
Content-Type: application/json

{
  "crop_encoded": 5,
  "season_encoded": 2,
  "state_encoded": 10,
  "annual_rainfall": 1200.5,
  "fertilizer": 150.0,
  "pesticide": 50.0,
  "area": 100.0
}
```

### Weather Analysis
```http
POST /analyze_weather
Content-Type: application/json

{
  "query": "What to do in drought conditions?",
  "temperature": 35,
  "rainfall": 50,
  "humidity": 30
}
```

### Pest Detection
```http
POST /detect_pest
Content-Type: application/json

{
  "image_path": "path/to/image.jpg",
  "top_k": 3
}
```

### Translation
```http
POST /translate
Content-Type: application/json

{
  "text": "How to grow tomatoes?",
  "target_lang": "hi",
  "source_lang": "en"
}
```

## 🧪 Testing with cURL

### Test LLM Query
```bash
curl -X POST http://localhost:5000/ask ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"What is nitrogen fertilizer?\", \"mode\": \"auto\"}"
```

### Test RAG Retrieval
```bash
curl -X POST http://localhost:5000/rag ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"crop rotation benefits\", \"top_k\": 3}"
```

### Test Yield Prediction
```bash
curl -X POST http://localhost:5000/predict_yield ^
  -H "Content-Type: application/json" ^
  -d "{\"crop_encoded\": 5, \"season_encoded\": 2, \"state_encoded\": 10, \"annual_rainfall\": 1200.5, \"fertilizer\": 150.0, \"pesticide\": 50.0, \"area\": 100.0}"
```

### Test Health Check
```bash
curl http://localhost:5000/health
```

## 🧪 Testing with Postman

1. Import the collection (create one with above endpoints)
2. Set base URL: `http://localhost:5000`
3. Test each endpoint with sample data
4. Check response format and status codes

## 📝 Response Format

### Success Response
```json
{
  "success": true,
  "message": "Success message",
  "data": {
    // Response data
  },
  "timestamp": "2025-11-30T12:00:00.000Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "status": 400,
  "details": "Additional error details",
  "timestamp": "2025-11-30T12:00:00.000Z"
}
```

## 🔧 Features

✅ **CORS Support** - Allows requests from React frontend  
✅ **Input Validation** - Joi schemas validate all inputs  
✅ **Error Handling** - Centralized error management  
✅ **Request Logging** - Winston logger tracks all requests  
✅ **Rate Limiting** - Prevents API abuse  
✅ **Retry Logic** - Auto-retry failed backend requests  
✅ **Compression** - Reduces response sizes  
✅ **Security Headers** - Helmet.js protection  
✅ **Timeout Handling** - Prevents hanging requests  

## 🔗 Integration Guide

### From React Frontend

```javascript
// Example: Query LLM from React
async function askQuestion(query) {
  const response = await fetch('http://localhost:5000/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query,
      mode: 'auto'
    })
  });
  
  const data = await response.json();
  return data;
}
```

### From Axios in React

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Query LLM
const response = await api.post('/ask', {
  query: 'How to control pests?',
  mode: 'auto'
});

console.log(response.data);
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows: Find and kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Cannot Connect to FastAPI
- Ensure FastAPI is running on http://localhost:8000
- Check FASTAPI_URL in .env file
- Verify network connectivity

### CORS Errors
- Check CORS_ORIGIN in .env matches React app URL
- Ensure React is running on http://localhost:3000

### Module Not Found
```bash
# Reinstall dependencies
rm -rf node_modules
npm install
```

## 📊 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 5000 | Server port |
| NODE_ENV | development | Environment (development/production) |
| FASTAPI_URL | http://localhost:8000 | FastAPI backend URL |
| CORS_ORIGIN | http://localhost:3000 | React frontend URL |
| API_TIMEOUT | 30000 | Request timeout (ms) |
| API_RETRY_COUNT | 3 | Number of retries |
| REQUEST_SIZE_LIMIT | 10mb | Max request body size |
| RATE_LIMIT_WINDOW | 900000 | Rate limit window (ms) |
| RATE_LIMIT_MAX_REQUESTS | 100 | Max requests per window |
| LOG_LEVEL | info | Logging level |

## 📦 Dependencies

- **express** - Web framework
- **axios** - HTTP client
- **cors** - CORS middleware
- **dotenv** - Environment variables
- **joi** - Input validation
- **winston** - Logging
- **helmet** - Security headers
- **compression** - Response compression
- **morgan** - HTTP request logger
- **express-rate-limit** - Rate limiting

## 🚀 Deployment

### Production Configuration

1. Set `NODE_ENV=production` in .env
2. Update FASTAPI_URL to production backend
3. Update CORS_ORIGIN to production frontend
4. Use process manager like PM2:

```bash
npm install -g pm2
pm2 start server.js --name shizishangpt-middleware
pm2 save
pm2 startup
```

## 📄 License

MIT License - See main project LICENSE file

## 👨‍💻 Authors

ShizishanGPT Team

---

**Part of the ShizishanGPT Agricultural AI System**

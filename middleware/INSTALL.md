# Installation Instructions - Node.js Middleware

## Prerequisites

- Node.js 14.0.0 or higher
- npm 6.0.0 or higher

Check your versions:
```bash
node --version
npm --version
```

## Step-by-Step Installation

### 1. Navigate to Middleware Directory
```bash
cd middleware
```

### 2. Install Dependencies
```bash
npm install
```

This will install:
- express (Web framework)
- axios (HTTP client)
- cors (CORS middleware)
- dotenv (Environment variables)
- joi (Input validation)
- winston (Logging)
- helmet (Security)
- compression (Response compression)
- morgan (HTTP logger)
- express-rate-limit (Rate limiting)

### 3. Create Environment File
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### 4. Configure Environment Variables

Edit `.env` file:
```env
PORT=5000
NODE_ENV=development
FASTAPI_URL=http://localhost:8000
CORS_ORIGIN=http://localhost:3000
API_TIMEOUT=30000
API_RETRY_COUNT=3
REQUEST_SIZE_LIMIT=10mb
RATE_LIMIT_WINDOW=900000
RATE_LIMIT_MAX_REQUESTS=100
LOG_LEVEL=info
LOG_FILE=logs/middleware.log
```

**Important:** Make sure to set `FASTAPI_URL` to your actual FastAPI backend URL.

### 5. Start the Server

Development mode (auto-restart on changes):
```bash
npm run dev
```

Production mode:
```bash
npm start
```

### 6. Verify Installation

Open browser or use curl:
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "success": true,
  "message": "ShizishanGPT Middleware is running",
  "timestamp": "2025-11-30T...",
  "version": "1.0.0",
  "environment": "development"
}
```

## Testing the Installation

### Run Test Suite
```bash
node test.js
```

This will test all endpoints and verify the middleware is working correctly.

### Manual Testing with cURL

**Test LLM Query:**
```bash
curl -X POST http://localhost:5000/ask -H "Content-Type: application/json" -d "{\"query\": \"What is nitrogen?\", \"mode\": \"auto\"}"
```

**Test RAG:**
```bash
curl -X POST http://localhost:5000/rag -H "Content-Type: application/json" -d "{\"query\": \"crop rotation\", \"top_k\": 3}"
```

## Troubleshooting

### "Cannot find module" errors
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

### Port 5000 already in use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill
```

### Cannot connect to FastAPI
1. Ensure FastAPI is running: `http://localhost:8000/docs`
2. Check `FASTAPI_URL` in `.env` file
3. Verify network connectivity

### CORS errors from React
1. Check `CORS_ORIGIN` in `.env` matches React app URL
2. Ensure React is running on the specified port (default 3000)

## Production Deployment

### Using PM2 (Process Manager)

Install PM2:
```bash
npm install -g pm2
```

Start with PM2:
```bash
pm2 start server.js --name shizishangpt-middleware
pm2 save
pm2 startup
```

Monitor:
```bash
pm2 status
pm2 logs shizishangpt-middleware
```

### Environment Configuration for Production

Update `.env`:
```env
NODE_ENV=production
PORT=5000
FASTAPI_URL=https://your-backend.com
CORS_ORIGIN=https://your-frontend.com
LOG_LEVEL=warn
```

## File Permissions

Ensure the middleware can create log files:
```bash
# Create logs directory
mkdir logs

# Set permissions (Linux/Mac)
chmod 755 logs
```

## Verifying All Components

1. **Config files exist:**
   - `config/env.js`
   - `config/logger.js`

2. **Services created:**
   - `services/apiClient.js`
   - `services/validator.js`
   - `services/formatter.js`

3. **Middleware created:**
   - `middleware/requestLogger.js`
   - `middleware/errorHandler.js`
   - `middleware/validateInput.js`

4. **Controllers created:**
   - `controllers/llmController.js`
   - `controllers/ragController.js`
   - `controllers/yieldController.js`
   - `controllers/weatherController.js`
   - `controllers/pestController.js`
   - `controllers/translateController.js`

5. **Routes created:**
   - `routes/llmRouter.js`
   - `routes/ragRouter.js`
   - `routes/yieldRouter.js`
   - `routes/weatherRouter.js`
   - `routes/pestRouter.js`
   - `routes/translateRouter.js`

6. **Core files:**
   - `server.js`
   - `package.json`
   - `.env`

## Next Steps

After successful installation:

1. **Start FastAPI Backend**
   ```bash
   cd ..
   python -m uvicorn src.api_routes:app --reload --port 8000
   ```

2. **Start React Frontend**
   ```bash
   cd frontend
   npm start
   ```

3. **Test Full Stack**
   - Frontend: http://localhost:3000
   - Middleware: http://localhost:5000
   - Backend: http://localhost:8000/docs

## Support

For issues or questions:
1. Check the logs in `logs/combined.log`
2. Verify all dependencies are installed
3. Ensure ports 5000, 8000, and 3000 are available
4. Review the README.md for detailed documentation

---

**Installation Complete! 🎉**

Your Node.js middleware layer is ready to connect your React frontend to the FastAPI backend.

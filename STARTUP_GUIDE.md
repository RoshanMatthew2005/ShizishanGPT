# 🚀 ShizishanGPT - Complete System Startup Guide

Run the entire ShizishanGPT system with this comprehensive guide.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [x] Python 3.8+ installed
- [x] Node.js 14.0+ installed
- [x] npm or yarn installed
- [x] 4GB+ RAM available
- [x] All dependencies installed

---

## ⚡ Quick Start (3 Commands)

### Option 1: Manual Start (Recommended for First Time)

**Terminal 1 - FastAPI Backend:**
```powershell
cd d:\Ps-3(git)\ShizishanGPT
python src/backend/main.py
```
Wait for: `✅ Backend ready on http://localhost:8000`

**Terminal 2 - Node.js Middleware:**
```powershell
cd d:\Ps-3(git)\ShizishanGPT\middleware
npm start
```
Wait for: `✅ Middleware running on http://localhost:5000`

**Terminal 3 - React Frontend:**
```powershell
cd d:\Ps-3(git)\ShizishanGPT\frontend
npm start
```
Wait for: Browser opens at `http://localhost:3000`

---

## 📦 First-Time Installation

If you haven't installed dependencies yet:

### 1. Install Backend Dependencies
```powershell
cd d:\Ps-3(git)\ShizishanGPT
pip install -r src/backend/requirements.txt
```

### 2. Install Middleware Dependencies
```powershell
cd middleware
npm install
```

### 3. Install Frontend Dependencies
```powershell
cd frontend
npm install
```

---

## 🔍 Verify Installation

### Check Backend
```powershell
curl http://localhost:8000/health
```
Expected: `{"status": "healthy", ...}`

### Check Middleware
```powershell
curl http://localhost:5000/api/health
```
Expected: `{"success": true, ...}`

### Check Frontend
Open browser: `http://localhost:3000`
Expected: Chat interface loads

---

## 🧪 Test the System

### 1. Simple Chat Test
1. Open `http://localhost:3000`
2. Type: "What is crop rotation?"
3. Press Enter or click Send
4. Should see AI response

### 2. Pest Detection Test
1. Click the paperclip icon 📎
2. Select "Upload Image"
3. Choose a plant disease image from `Data/images/PlantVillage/`
4. Type: "What disease is this?"
5. Send - see detection results

### 3. Yield Prediction Test
Type: "Predict yield for wheat in Punjab with 800mm rainfall"

### 4. RAG Search Test
1. Click Settings ⚙️
2. Change mode to "RAG Search"
3. Type: "wheat cultivation"
4. See knowledge base results

---

## 🛠️ Troubleshooting

### Backend Won't Start

**Issue:** `ModuleNotFoundError`
```powershell
pip install -r src/backend/requirements.txt
```

**Issue:** Port 8000 in use
```powershell
# Change port in src/backend/config.py
PORT=8001
```

**Issue:** Model files not found
```
Ensure these exist:
- models/yield_model.pkl
- Model/best_plant_disease_model.pth
- vectorstore/
- fine_tuned_agri_mini_llm/
```

### Middleware Won't Start

**Issue:** `Cannot find module`
```powershell
cd middleware
rm -rf node_modules
npm install
```

**Issue:** Port 5000 in use
```powershell
# In middleware/.env
PORT=5001
```

### Frontend Won't Start

**Issue:** `npm: command not found`
Install Node.js from https://nodejs.org/

**Issue:** Port 3000 in use
```powershell
set PORT=3001
npm start
```

**Issue:** "Cannot connect to backend"
Check if middleware is running:
```powershell
curl http://localhost:5000/api/health
```

---

## 📊 Service Status Overview

After starting all services, you should see:

```
✅ FastAPI Backend    http://localhost:8000
   ├─ API Docs:       http://localhost:8000/docs
   └─ Health:         http://localhost:8000/health

✅ Node.js Middleware http://localhost:5000
   ├─ API Routes:     http://localhost:5000/api/*
   └─ Health:         http://localhost:5000/api/health

✅ React Frontend     http://localhost:3000
   └─ Chat Interface: http://localhost:3000
```

---

## 🔄 Restart Services

### Stop All Services
Press `Ctrl+C` in each terminal

### Restart Individual Services

**Backend Only:**
```powershell
cd d:\Ps-3(git)\ShizishanGPT
python src/backend/main.py
```

**Middleware Only:**
```powershell
cd middleware
npm start
```

**Frontend Only:**
```powershell
cd frontend
npm start
```

---

## 📝 Startup Logs

### Expected Backend Logs
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
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Expected Middleware Logs
```
==========================================
  ShizishanGPT Middleware Server
==========================================
  Environment: development
  Port: 5000
  FastAPI URL: http://localhost:8000
==========================================

✓ FastAPI health check passed
✓ All routes registered
✅ Middleware running on http://localhost:5000
```

### Expected Frontend Logs
```
Compiled successfully!

You can now view shizishangpt-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.x:3000

Note that the development build is not optimized.
To create a production build, use npm run build.

webpack compiled successfully
```

---

## 🎯 Usage Examples

### Example 1: Ask a Question
```
User: "What are the best crops for monsoon season?"
AI: Great question! For monsoon season, I'd recommend...
```

### Example 2: Detect Plant Disease
```
User: [Uploads image] "What's wrong with my plant?"
AI: 🔍 Plant Disease Detection Results:
    1. Tomato Late Blight - 92.3% confidence
    📋 Recommendation: Apply copper-based fungicide...
```

### Example 3: Predict Yield
```
User: "Predict yield for rice in Kerala with 2000mm rainfall"
AI: Based on the data:
    Predicted Yield: 3.45 tonnes/hectare
    Total Production: 6.9 tonnes (for 2 hectares)
```

---

## 🔐 Environment Configuration

### Backend (.env or config.py)
```env
HOST=0.0.0.0
PORT=8000
DEBUG=True
YIELD_MODEL_PATH=models/yield_model.pkl
PEST_MODEL_PATH=Model/best_plant_disease_model.pth
VECTORSTORE_PATH=vectorstore
LLM_MODEL_PATH=fine_tuned_agri_mini_llm
```

### Middleware (middleware/.env)
```env
PORT=5000
NODE_ENV=development
FASTAPI_BASE_URL=http://localhost:8000
LOG_LEVEL=info
```

### Frontend (frontend/.env)
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_NAME=ShizishanGPT
REACT_APP_VERSION=1.0.0
```

---

## 📱 Accessing from Other Devices

To access from phone/tablet on same network:

1. Find your computer's IP address:
   ```powershell
   ipconfig
   ```
   Look for "IPv4 Address"

2. Update frontend/.env:
   ```env
   REACT_APP_API_URL=http://YOUR_IP:5000/api
   ```

3. Access from device:
   ```
   http://YOUR_IP:3000
   ```

---

## 🚦 Performance Tips

### For Faster Startup
1. **Keep models loaded**: Don't restart backend frequently
2. **Use SSD**: Store models on SSD for faster loading
3. **Increase RAM**: 8GB+ recommended for smoother operation

### For Better Response Times
1. **Agent Mode**: Fastest, uses cached models
2. **RAG Mode**: Fast for specific queries
3. **LLM Mode**: Moderate speed, general queries

### For Development
1. **Hot Reload**: All services support code changes
2. **Debug Mode**: Enabled by default
3. **Logs**: Check console for detailed information

---

## 📚 Additional Resources

### Documentation
- **Complete Guide**: `docs/FINAL_PROJECT_SUMMARY.md`
- **Frontend Guide**: `frontend/README.md`
- **Backend Guide**: `src/backend/README.md`
- **Middleware Guide**: `middleware/README.md`

### Quick Starts
- **Frontend**: `frontend/QUICKSTART.md`
- **Backend**: `src/backend/QUICKSTART.md`

### API Documentation
- **Swagger UI**: http://localhost:8000/docs (when backend running)
- **ReDoc**: http://localhost:8000/redoc

---

## ✅ Startup Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 14.0+ installed
- [ ] All dependencies installed
- [ ] Model files present
- [ ] Environment variables set
- [ ] Backend started (port 8000)
- [ ] Middleware started (port 5000)
- [ ] Frontend started (port 3000)
- [ ] Health checks pass
- [ ] Test query successful

---

## 🎊 Success!

If you see:
- ✅ Backend running
- ✅ Middleware running
- ✅ Frontend loaded
- ✅ Chat interface responsive
- ✅ AI responses working

**Congratulations! ShizishanGPT is fully operational!** 🎉

Start chatting with your AI agricultural assistant!

---

## 🆘 Need Help?

1. **Check Logs**: Look for errors in terminal windows
2. **Verify Ports**: Ensure no conflicts
3. **Health Checks**: Test each service individually
4. **Documentation**: Review README files
5. **Restart**: Try restarting services

---

**Happy Farming with AI!** 🌾🤖

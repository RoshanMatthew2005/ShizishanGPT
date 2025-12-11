# ShizishanGPT - Complete Setup Guide

Welcome! This guide will help you set up ShizishanGPT on your machine.

## 📋 Prerequisites

Before you begin, make sure you have the following installed:

### Required Software:
1. **Python 3.11** - [Download](https://www.python.org/downloads/)
   - During installation, **CHECK** "Add Python to PATH"
   - Verify: Open terminal/cmd and type `python --version`

2. **Node.js 18+** - [Download](https://nodejs.org/)
   - This includes npm (Node Package Manager)
   - Verify: `node --version` and `npm --version`

3. **Ollama** (for LLM inference) - [Download](https://ollama.ai/download)
   - Install and run Ollama
   - Pull Gemma 2 model: `ollama pull gemma2:2b`

4. **Git** (optional, for version control) - [Download](https://git-scm.com/downloads)

### Hardware Requirements:
- **RAM**: 8GB minimum (16GB recommended)
- **GPU**: NVIDIA GPU with 6GB+ VRAM (optional but recommended for faster performance)
- **Storage**: 10GB free space

---

## 🚀 Quick Setup (Windows)

### Option 1: Automated Setup (Recommended)

Simply run the setup script:

```powershell
# Right-click setup_complete.ps1 and select "Run with PowerShell"
# OR open PowerShell in the project folder and run:
.\setup_complete.ps1
```

This script will:
- ✅ Check if Python and Node.js are installed
- ✅ Install all Python dependencies
- ✅ Install all Node.js packages
- ✅ Set up environment variables
- ✅ Create necessary directories
- ✅ Pull required Ollama models
- ✅ Test all services

### Option 2: Manual Setup

If you prefer to set up manually, follow these steps:

#### Step 1: Install Python Dependencies

```powershell
# Open PowerShell in the project folder
pip install -r requirements.txt
```

**Note**: If you see errors, try:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 2: Install Node.js Dependencies

```powershell
cd frontend
npm install
cd ..
```

#### Step 3: Set Up Ollama Models

```powershell
# Pull Gemma 2 model (required for LLM)
ollama pull gemma2:2b

# Optional: Pull embedding model for better RAG performance
ollama pull nomic-embed-text
```

#### Step 4: Configure Environment Variables

Create a `.env` file in the root folder with:

```env
# Tavily API Key (for web search)
TAVILY_API_KEY=your_tavily_api_key_here

# JWT Secret (for authentication)
JWT_SECRET=your_secret_key_here
JWT_ALGORITHM=HS256

# Database (SQLite - no setup needed)
DATABASE_URL=sqlite:///./users.db

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma2:2b

# Optional: OpenWeatherMap API
OPENWEATHER_API_KEY=your_openweather_key_here
```

**Get API Keys:**
- Tavily API: https://tavily.com/ (Free tier available)
- OpenWeatherMap: https://openweathermap.org/api (Optional)

---

## 🏃 Running ShizishanGPT

### Option 1: Start All Services (Recommended)

**Windows PowerShell:**
```powershell
.\start_all_services.ps1
```

This will start:
1. Backend API (FastAPI) on http://localhost:8000
2. Frontend React App on http://localhost:3000

### Option 2: Start Services Manually

**Terminal 1 - Backend:**
```powershell
python src/main.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm start
```

### Option 3: Use the Launcher

**Windows:**
```powershell
.\run_project.bat
```

**Linux/Mac:**
```bash
./run_project.sh
```

---

## 🧪 Testing the Installation

### 1. Test Backend API

Open browser: http://localhost:8000/docs

You should see the FastAPI Swagger documentation.

### 2. Test Frontend

Open browser: http://localhost:3000

You should see the ShizishanGPT login page.

### 3. Run Test Script

```powershell
python test_services_quick.py
```

This will test:
- ✅ Backend API connectivity
- ✅ LLM (Gemma 2) inference
- ✅ RAG retrieval system
- ✅ Tavily search integration
- ✅ ML model predictions

---

## 📁 Project Structure

```
ShizishanGPT/
├── src/                    # Backend source code
│   ├── main.py            # FastAPI server entry point
│   ├── orchestration/     # ReAct agent & tool orchestration
│   ├── tools/             # Individual tools (RAG, Tavily, ML models)
│   └── models/            # Database models
├── frontend/              # React frontend
│   ├── src/               # React components
│   └── public/            # Static files
├── Data/                  # Agricultural datasets
├── models/                # Trained ML models
├── vectorstore/           # RAG vector database
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── setup_complete.ps1     # Automated setup script
└── start_all_services.ps1 # Service launcher

```

---

## 🔑 Default Credentials

**Super Admin Account:**
- Username: `superadmin`
- Password: `superadmin123`

**Note**: Change these credentials immediately after first login!

---

## 🛠️ Troubleshooting

### Problem: "Python not found"
**Solution**: 
- Reinstall Python and check "Add Python to PATH"
- OR manually add Python to PATH in System Environment Variables

### Problem: "npm not found"
**Solution**: 
- Reinstall Node.js
- Restart your terminal/PowerShell after installation

### Problem: "Ollama connection failed"
**Solution**: 
1. Make sure Ollama is running (check system tray)
2. Test: `ollama list` - should show installed models
3. If not installed: `ollama pull gemma2:2b`

### Problem: "Module not found" errors
**Solution**: 
```powershell
# Reinstall Python dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Problem: Frontend won't start
**Solution**: 
```powershell
# Clear npm cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Problem: "Port already in use"
**Solution**: 
- Backend (8000): Change port in `src/main.py`
- Frontend (3000): Change port in `frontend/package.json`

### Problem: CUDA/GPU errors
**Solution**: 
- ShizishanGPT runs fine on CPU (slower but works)
- For GPU: Install CUDA Toolkit matching your PyTorch version
- Check GPU: `nvidia-smi` (Windows/Linux)

---

## 📚 Features Overview

ShizishanGPT includes:

1. **🤖 ReAct AI Agent** - Intelligent tool orchestration
2. **🔍 RAG System** - Retrieval-Augmented Generation for agricultural knowledge
3. **🌐 Tavily Search** - Real-time web search for latest information
4. **📊 ML Models** (4 models):
   - Crop Climate Recommendation
   - Crop Nutrient Recommendation
   - Soil Moisture Classification
   - Soil Fertility Classification
5. **🌾 Agricultural Knowledge Graph** - Structured crop-disease-pest relationships
6. **🌡️ Yield Prediction** - ML-based crop yield forecasting
7. **🐛 Pest Detection** - Image-based pest identification
8. **🌍 Translation** - Multi-language support (Tamil, Hindi, Telugu, etc.)
9. **💬 Chat History** - Persistent conversation management
10. **👥 User Authentication** - Secure login system with admin dashboard

---

## 🎯 Quick Start Tutorial

### 1. Login
- Navigate to http://localhost:3000
- Login with: `superadmin` / `superadmin123`

### 2. Ask a Question
Try these examples:
- "How to improve soil irrigation?"
- "Best pesticide for whitefly in cotton 2025?"
- "Predict wheat yield in Punjab with 800mm rainfall"
- "Which crop is suitable for 25°C temperature?"

### 3. Upload Image (Pest Detection)
- Click the paperclip icon
- Upload a crop/pest image
- Ask: "What pest is this?"

### 4. Translation
- Click Settings (gear icon)
- Enable "Auto-translate Output"
- Select your language (Tamil, Hindi, etc.)
- Ask questions in your language!

---

## 📞 Support & Documentation

- **Full Documentation**: See `/docs` folder
- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **Quick References**: 
  - `docs/MILESTONE_8_COMPLETION_REPORT.md` - Latest features
  - `docs/AUTH_QUICKSTART.md` - Authentication system
  - `TAVILY_QUICK_REFERENCE.md` - Web search integration
  - `TRANSLATION_QUICKSTART.md` - Translation features

---

## 🔒 Security Notes

1. **Change default credentials** immediately
2. **Never commit `.env` file** with real API keys
3. **Use HTTPS in production** (not HTTP)
4. **Keep API keys secret** - don't share them

---

## 🎉 You're All Set!

Your ShizishanGPT installation is complete. Enjoy using your agricultural AI assistant!

**Next Steps:**
1. Explore different query types
2. Test ML model predictions
3. Try multi-language translation
4. Upload pest images for detection
5. Check the admin dashboard for user management

Happy Farming! 🌾🚜

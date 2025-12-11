# ShizishanGPT - Agricultural AI Assistant 🌾🤖

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)

**ShizishanGPT** is an intelligent agricultural assistant powered by AI, designed to help farmers with crop management, pest detection, yield prediction, and much more!

---

## ✨ Features

- 🤖 **AI-Powered Chat** - Ask farming questions in natural language
- 🔍 **Smart Search** - Real-time web search for latest agricultural information
- 📊 **ML Predictions** - 4 trained models for crop and soil analysis
- 🌾 **Knowledge Graph** - Structured crop-disease-pest relationships
- 🐛 **Pest Detection** - Upload images for pest identification
- 🌡️ **Yield Prediction** - Forecast crop yields based on conditions
- 🌍 **Multi-Language** - Support for Tamil, Hindi, Telugu, and more
- 💬 **Chat History** - Save and revisit conversations
- 👥 **User Management** - Secure authentication with admin dashboard

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Download & Extract

You've already done this! Now you're ready to set up.

### Step 2: Run Setup

**Windows:**
```powershell
# Right-click setup_complete.ps1 → "Run with PowerShell"
# OR in PowerShell:
.\setup_complete.ps1
```

That's it! The script will:
- ✅ Check if you have Python & Node.js installed
- ✅ Install all dependencies automatically
- ✅ Download required AI models
- ✅ Set up configuration files
- ✅ Test everything

### Step 3: Get API Key (Optional but Recommended)

1. Go to https://tavily.com/
2. Sign up for free account
3. Copy your API key
4. Open `.env` file and paste it:
   ```
   TAVILY_API_KEY=tvly-xxxxxxxxxxxxx
   ```

### Step 4: Start the App

```powershell
.\start_all_services.ps1
```

### Step 5: Open Browser

- Frontend: http://localhost:3000
- Login: `superadmin` / `superadmin123`

---

## 📖 What You Need Installed

Before running the setup script, make sure you have:

### 1. Python 3.11+
- Download: https://www.python.org/downloads/
- ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation

### 2. Node.js 18+
- Download: https://nodejs.org/
- This includes npm automatically

### 3. Ollama (for AI models)
- Download: https://ollama.ai/download
- After installation, Ollama runs in the background

**Don't have these?** No problem! The setup script will tell you what's missing.

---

## 🎯 What Can You Do?

### Try These Questions:

**General Farming:**
- "How to improve soil irrigation?"
- "What are the best fertilizers for rice?"
- "When is the best time to plant wheat?"

**Pest & Disease:**
- "What is the best pesticide for whitefly in cotton?"
- "How to treat rust disease in wheat?"
- Upload a pest image and ask "What pest is this?"

**Predictions:**
- "Predict wheat yield in Punjab with 800mm rainfall"
- "Which crop is suitable for 25°C temperature and 75% humidity?"
- "Classify soil moisture with 1024 sensor reading at 28°C"

**Knowledge Graph:**
- "What diseases affect rice?"
- "Which pests attack cotton?"
- "What fertilizers does maize need?"

**Translation:**
- Ask questions in Tamil, Hindi, Telugu, or your native language!
- Enable "Auto-translate Output" in settings

---

## 📁 Project Structure

```
ShizishanGPT/
├── 📄 SETUP_INSTRUCTIONS.md     ← Detailed setup guide
├── 📄 QUICK_START.txt           ← Ultra-quick reference
├── 🔧 setup_complete.ps1        ← Automated setup script
├── 🚀 start_all_services.ps1    ← Start everything
├── 📦 requirements.txt          ← Python packages
├── 📂 src/                      ← Backend (Python/FastAPI)
├── 📂 frontend/                 ← Frontend (React)
├── 📂 Data/                     ← Agricultural datasets
├── 📂 models/                   ← Trained ML models
├── 📂 docs/                     ← Full documentation
└── 📄 .env                      ← Configuration (create this!)
```

---

## 🛠️ Troubleshooting

### "Python not found" ❌
**Fix:** 
1. Reinstall Python from python.org
2. ✅ Check "Add Python to PATH" during installation
3. Restart your terminal

### "npm not found" ❌
**Fix:** 
1. Reinstall Node.js from nodejs.org
2. Restart your terminal

### "Ollama connection failed" ❌
**Fix:**
1. Check if Ollama is running (system tray icon)
2. Open terminal: `ollama pull gemma2:2b`
3. Restart the app

### Frontend won't load ❌
**Fix:**
```powershell
cd frontend
rm -rf node_modules
npm install
npm start
```

### More help needed? 📚
- Read `SETUP_INSTRUCTIONS.md` for detailed troubleshooting
- Check the `/docs` folder for feature-specific guides

---

## 🔒 Important Notes

1. **Change default password** after first login!
2. **Get Tavily API key** for web search to work
3. **Don't share your .env file** - it contains secrets
4. **Backup your data** before updates

---

## 📊 System Requirements

**Minimum:**
- CPU: Dual-core processor
- RAM: 8GB
- Storage: 10GB free space
- OS: Windows 10/11, Linux, or macOS

**Recommended:**
- CPU: Quad-core processor
- RAM: 16GB
- GPU: NVIDIA with 6GB+ VRAM (for faster AI)
- Storage: 20GB free space

---

## 🎓 Learning Resources

**New to AI/ML?** No problem! Check these guides:

- `docs/MILESTONE_8_COMPLETION_REPORT.md` - Latest features explained
- `AUTH_QUICKSTART.md` - How authentication works
- `TAVILY_QUICK_REFERENCE.md` - Using web search
- `TRANSLATION_QUICKSTART.md` - Multi-language features
- `PEST_DETECTION_GUIDE.md` - Image-based pest detection

---

## 🤝 Contributing

Found a bug? Have an idea? 
1. Document the issue clearly
2. Include error messages/screenshots
3. Share with the development team

---

## 📞 Getting Help

**Documentation:**
- See `SETUP_INSTRUCTIONS.md` - Complete setup guide
- See `docs/` folder - Feature-specific documentation

**API Documentation:**
- Start backend: `python src/main.py`
- Visit: http://localhost:8000/docs

**Common Issues:**
- Most issues are solved by running `setup_complete.ps1` again
- Check `SETUP_INSTRUCTIONS.md` troubleshooting section

---

## 🎉 You're Ready!

1. ✅ Run `setup_complete.ps1`
2. ✅ Add your Tavily API key to `.env`
3. ✅ Run `start_all_services.ps1`
4. ✅ Open http://localhost:3000
5. ✅ Start asking agricultural questions!

**Happy Farming!** 🌾🚜

---

## 📝 Version Info

- **Version:** 1.0.0
- **Last Updated:** December 2025
- **Python:** 3.11+
- **Node.js:** 18+
- **AI Model:** Gemma 2 (via Ollama)

---

## ⭐ Key Technologies

- **Backend:** FastAPI, Python, SQLite
- **Frontend:** React, TailwindCSS
- **AI/ML:** Ollama, Gemma 2, Scikit-learn, PyTorch
- **RAG:** ChromaDB, Sentence Transformers
- **Search:** Tavily API
- **Authentication:** JWT tokens

---

**Made with ❤️ for farmers everywhere**

# 🚀 React Frontend - Quick Start

## One-Command Setup

```powershell
cd frontend
npm install
npm start
```

That's it! The app will open at http://localhost:3000

## Full Stack Quick Start

### Start All Services

**Terminal 1 - FastAPI Backend:**
```powershell
python src/backend/main.py
```

**Terminal 2 - Node.js Middleware:**
```powershell
cd middleware
npm start
```

**Terminal 3 - React Frontend:**
```powershell
cd frontend
npm start
```

### Access Points

- **Frontend**: http://localhost:3000
- **Middleware**: http://localhost:5000
- **Backend**: http://localhost:8000

## Quick Test

1. Open http://localhost:3000
2. Type: "What is crop rotation?"
3. Press Enter or click Send
4. See AI response!

## Upload Image Test

1. Click the paperclip icon 📎
2. Select "Upload Image"
3. Choose a plant disease image
4. Type: "What disease is this?"
5. Send - see AI detection results!

## Query Modes

Click Settings ⚙️ to switch modes:

- **Agent** (Default): Auto-selects best tool
- **LLM**: Direct AI chat
- **RAG**: Search knowledge base

## Features to Try

✅ **Ask Questions**: "Best crops for monsoon?"  
✅ **Pest Detection**: Upload plant images  
✅ **Yield Prediction**: "Predict yield for wheat"  
✅ **Multi-language**: Switch language in settings  
✅ **Chat History**: View in sidebar  

## Troubleshooting

### "Cannot connect to backend"

Check if middleware is running:
```powershell
curl http://localhost:5000/api/health
```

If not, start it:
```powershell
cd middleware
npm start
```

### Port 3000 in use

```powershell
set PORT=3001
npm start
```

### Build errors

```powershell
rm -rf node_modules
npm install
```

## Development Tips

- **Hot Reload**: Code changes auto-refresh
- **DevTools**: Open browser console (F12)
- **Network**: Check API calls in Network tab
- **React DevTools**: Install browser extension

## Architecture

```
User Browser
    ↓
React App (Port 3000)
    ↓ API calls via axios
Node.js Middleware (Port 5000)
    ↓ Forwards to
FastAPI Backend (Port 8000)
    ↓ Uses
AI Models (LLM, RAG, Pest, Yield)
```

## Quick Commands

```powershell
# Install
npm install

# Start dev server
npm start

# Build for production
npm run build

# Run tests
npm test

# Check dependencies
npm list

# Update dependencies
npm update
```

## Environment Variables

Edit `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:5000/api
```

## Next Steps

1. ✅ Start all services
2. ✅ Test basic chat
3. ✅ Try image upload
4. ✅ Test different modes
5. ✅ Explore settings

---

**Need help?** Check `frontend/README.md` for detailed documentation.

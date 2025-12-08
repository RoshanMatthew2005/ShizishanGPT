# ShizishanGPT - React Frontend

Modern, responsive React frontend for the ShizishanGPT Agricultural AI Assistant.

## 🎨 Features

- **Modern UI**: Built with React 18 and Tailwind CSS
- **Real-time Chat**: Interactive chat interface with typing indicators
- **File Upload**: Support for image uploads (pest detection)
- **Multi-Mode**: Switch between LLM, RAG, and Agent modes
- **Responsive**: Mobile-friendly design
- **API Integration**: Seamless integration with Node.js middleware

## 🚀 Quick Start

### Prerequisites

- Node.js 14.0.0 or higher
- npm or yarn
- Node.js middleware running on port 5000

### Installation

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/
│   │   └── AgriChatbot.jsx # Main chat component
│   ├── services/
│   │   └── api.js          # API service layer
│   ├── App.js              # Root component
│   ├── App.css             # App styles
│   ├── index.js            # Entry point
│   └── index.css           # Global styles (Tailwind)
├── .env                    # Environment variables
├── package.json            # Dependencies
├── tailwind.config.js      # Tailwind configuration
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_NAME=ShizishanGPT
REACT_APP_VERSION=1.0.0
```

### API Endpoints

The frontend communicates with Node.js middleware on port 5000:

- `POST /api/ask` - Ask LLM
- `POST /api/rag` - Query vectorstore
- `POST /api/agent` - ReAct agent
- `POST /api/predict_yield` - Yield prediction
- `POST /api/detect_pest` - Pest detection
- `POST /api/translate` - Translation
- `GET /api/health` - Health check

## 💻 Usage

### Starting the Full Stack

1. **Start FastAPI Backend** (Port 8000):
   ```powershell
   python src/backend/main.py
   ```

2. **Start Node.js Middleware** (Port 5000):
   ```powershell
   cd middleware
   npm start
   ```

3. **Start React Frontend** (Port 3000):
   ```powershell
   cd frontend
   npm start
   ```

### Query Modes

- **Agent Mode** (Default): Automatically selects best tool for the query
- **LLM Mode**: Direct LLM query
- **RAG Mode**: Search knowledge base

Change mode in Settings modal.

### Features

**Chat Interface:**
- Type questions in the input box
- Use quick suggestions for common queries
- View conversation history in sidebar

**File Upload:**
- Click paperclip icon to attach files
- Upload images for pest detection
- Drag and drop support

**Settings:**
- Switch query modes
- Change language preferences
- Customize response detail

## 🎨 Styling

Built with Tailwind CSS for modern, responsive design:

```css
/* Color Palette */
--agri-dark: #111827
--agri-green: #15803d
--agri-emerald: #047857
```

## 📦 Dependencies

**Core:**
- react ^18.2.0
- react-dom ^18.2.0
- react-scripts ^5.0.1

**UI:**
- tailwindcss ^3.3.5
- lucide-react ^0.294.0

**Networking:**
- axios ^1.6.2

**Routing:**
- react-router-dom ^6.20.0

## 🛠️ Development

### Available Scripts

```powershell
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Eject (one-way operation)
npm run eject
```

### Build for Production

```powershell
npm run build
```

Creates optimized build in `build/` folder.

### Deployment

```powershell
# Build
npm run build

# Serve static files
npx serve -s build
```

## 🔍 API Service

The `src/services/api.js` file handles all API calls:

```javascript
import * as api from './services/api';

// Ask question
const response = await api.askQuestion("What is crop rotation?");

// Detect pest from image
const result = await api.detectPest(imageFile, 3);

// Predict yield
const prediction = await api.predictYield(data);
```

## 🐛 Troubleshooting

### Port 3000 Already in Use

```powershell
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different port
set PORT=3001 && npm start
```

### API Connection Failed

Check if Node.js middleware is running:
```powershell
curl http://localhost:5000/api/health
```

### Build Errors

Clear cache and reinstall:
```powershell
rm -rf node_modules package-lock.json
npm install
```

## 📱 Mobile Support

Fully responsive design:
- Collapsible sidebar
- Touch-friendly controls
- Optimized layouts for small screens

## 🎯 Features Roadmap

- [ ] Voice input support
- [ ] Multi-language interface
- [ ] Dark/Light theme toggle
- [ ] Export chat history
- [ ] Advanced settings
- [ ] Offline mode

## 🤝 Integration

This frontend integrates with:

- **Node.js Middleware** (Port 5000) - API gateway
- **FastAPI Backend** (Port 8000) - AI services
- **MongoDB** (Optional) - Chat history
- **ChromaDB** - Knowledge base

## 📝 License

Part of the ShizishanGPT project.

## 🆘 Support

For issues, check:
1. Browser console for errors
2. Network tab for API calls
3. Backend logs
4. Middleware logs

---

**Built with ❤️ for farmers using React, Tailwind CSS, and cutting-edge AI**

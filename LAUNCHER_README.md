# ShizishanGPT Project Launcher

This directory contains multiple ways to run the complete ShizishanGPT agricultural AI system:

## 🚀 Quick Start Options

### Option 1: Python Launcher (Recommended)
```bash
python run_project.py
```

### Option 2: Windows Batch File
```cmd
run_project.bat
```

### Option 3: Linux/macOS Shell Script
```bash
chmod +x run_project.sh
./run_project.sh
```

## 📋 What Gets Started

The launcher automatically starts all required services:

1. **Backend (FastAPI)** - Port 8000
   - 5 AI models (LLM, RAG, Yield, Pest, Weather)
   - ReAct agent with 6 tools
   - MongoDB integration
   - Gemma 2 LLM via Ollama

2. **Middleware (Node.js)** - Port 5000
   - Express API gateway
   - Request routing and formatting
   - CORS and rate limiting

3. **Frontend (React)** - Port 3000
   - AgriChatbot interface
   - Multi-mode chat (LLM, RAG, Agent)
   - Conversation history

## 🔧 Prerequisites

Make sure you have these installed:

- **Python 3.8+** with required packages
- **Node.js 16+** with npm
- **MongoDB** running on port 27017
- **Ollama** with Gemma 2 model on port 11434

## ✅ System Check

The launcher will automatically:
- Check all dependencies
- Kill existing processes on required ports
- Start services in the correct order
- Run integration tests
- Display access URLs

## 🌐 Access URLs

Once started, access the system at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Middleware**: http://localhost:5000

## 🛑 Stopping the System

Press **Ctrl+C** to gracefully shutdown all services.

## 🔍 Features

- **Automated Startup**: Single command starts entire stack
- **Dependency Checking**: Validates all requirements
- **Health Monitoring**: Checks service availability
- **Integration Testing**: Verifies complete pipeline
- **Graceful Shutdown**: Properly stops all processes
- **Cross-Platform**: Works on Windows, Linux, and macOS

## 📊 System Architecture

```
Frontend (React) → Middleware (Node.js) → Backend (FastAPI) → AI Models
     ↓                    ↓                      ↓              ↓
Port 3000           Port 5000            Port 8000        Ollama/MongoDB
```

## 🎯 Agricultural AI Features

- **Crop Yield Prediction**: ML-based yield forecasting
- **Pest Detection**: Image-based plant disease identification  
- **Weather Analysis**: Agricultural weather recommendations
- **Knowledge Base**: RAG-powered document retrieval
- **Multi-Language**: Translation support
- **Intelligent Agent**: Multi-tool orchestration with Gemma 2

Enjoy using ShizishanGPT! 🌾🤖
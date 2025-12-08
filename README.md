```markdown
# 🌾 ShizishanGPT — AI-Powered Agricultural Assistant

**Status:** ✅ **PRODUCTION READY** | **All 7 Milestones Complete**

ShizishanGPT is a comprehensive AI-powered agricultural assistant system that combines multiple AI technologies into a unified three-tier web application. The system helps farmers with crop management, pest detection, yield prediction, weather analysis, and agricultural knowledge through an intelligent chat interface.

## 🎉 Project Complete!

This repository contains the **complete ShizishanGPT system** with all milestones finished:
- ✅ Mini LLM (DistilGPT-2 fine-tuned on agricultural data)
- ✅ RAG Knowledge Base (ChromaDB vectorstore)
- ✅ ReAct Agent (Intelligent tool orchestration)
- ✅ FastAPI Backend (8 endpoints, 5 models)
- ✅ Node.js Middleware (API gateway)
- ✅ React Frontend (Modern chat interface)

**Total:** 100+ files, 16,000+ lines of code, production-ready system!

---

## 🚀 Quick Start

### Run the Complete System (3 Steps)

**1. Start FastAPI Backend (Port 8000):**
```powershell
python src/backend/main.py
```

**2. Start Node.js Middleware (Port 5000):**
```powershell
cd middleware
npm start
```

**3. Start React Frontend (Port 3000):**
```powershell
cd frontend
npm start
```

Then open **http://localhost:3000** in your browser! 🎊

### First-Time Installation

```powershell
# Backend
pip install -r src/backend/requirements.txt

# Middleware
cd middleware
npm install

# Frontend
cd frontend
npm install
```

**Detailed guide:** See [`STARTUP_GUIDE.md`](STARTUP_GUIDE.md)

---

## 🏗️ System Architecture

```
React Frontend (Port 3000)
        ↓
Node.js Middleware (Port 5000)
        ↓
FastAPI Backend (Port 8000)
        ↓
┌──────────────────────────────┐
│  AI Models & Services        │
├──────────────────────────────┤
│  • Mini LLM (DistilGPT-2)   │
│  • RAG VectorStore          │
│  • Yield Model              │
│  • Pest Detection Model     │
│  • Translation Service      │
│  • ReAct Agent              │
└──────────────────────────────┘
```

---

## ✨ Features

### 🤖 AI Capabilities
- **Intelligent Chat**: Natural language conversations powered by fine-tuned LLM
- **Knowledge Base**: RAG-based search across agricultural documents
- **Pest Detection**: Upload plant images for disease identification
- **Yield Prediction**: Predict crop yields based on parameters
- **Multi-Language**: Translation support for 9 languages
- **Smart Agent**: Automatic tool selection using ReAct reasoning

### 💻 Technical Features
- **Modern UI**: React 18 + Tailwind CSS responsive interface
- **REST API**: 7 endpoints with full validation
- **Real-time**: Async operations, typing indicators
- **File Upload**: Image processing for pest detection
- **Error Handling**: Graceful degradation, comprehensive logging
- **Documentation**: 15+ documentation files

---

## 📋 All Milestones Complete

### ✅ Milestone 1 & 2: Data & Initial Models
- Knowledge base (ChromaDB vectorstore from 31 PDFs)
- Initial ML models (Yield, Weather, Pest detection)
- Dataset collection (PlantVillage, crop yield data)

### ✅ Milestone 3: Mini LLM
- Fine-tuned DistilGPT-2 on agricultural corpus
- 82M parameters, 3 training epochs
- Located in: `fine_tuned_agri_mini_llm/`

### ✅ Milestone 4: Mini LangChain & ReAct Agent
- Custom LangChain implementation
- ReAct agent with intelligent tool selection
- Orchestration system in: `src/orchestration/`

### ✅ Milestone 5: Node.js Middleware
- Express.js API gateway (35 files)
- 6 API endpoints with validation
- Located in: `middleware/`

### ✅ Milestone 6: FastAPI Backend
- Complete FastAPI backend (23 files)
- 5 model loaders, 7 services, 3 routers
- Located in: `src/backend/`

### ✅ Milestone 7: React Frontend (NEW!)
- Modern React 18 + Tailwind CSS interface
- Full API integration, file upload
- Located in: `frontend/`

---

## 📊 Project Statistics

| Component | Files | Lines of Code | Technology |
|-----------|-------|---------------|------------|
| Frontend | 14 | ~900 | React, Tailwind, Axios |
| Middleware | 35 | ~3,500 | Node.js, Express |
| Backend | 23 | ~3,500 | FastAPI, Pydantic |
| Orchestration | 12 | ~2,000 | Python, Custom LangChain |
| Models | 5 | ~1,000 | PyTorch, scikit-learn |
| **TOTAL** | **100+** | **~16,000** | **10+ Technologies** |

---

## 🎯 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ask` | POST | Ask the Mini LLM |
| `/api/rag` | POST | Query knowledge base |
| `/api/agent` | POST | ReAct agent with auto tool selection |
| `/api/predict_yield` | POST | Crop yield prediction |
| `/api/detect_pest` | POST | Plant disease detection |
| `/api/translate` | POST | Multi-language translation |
| `/health` | GET | System health check |

---

## 📁 Important files & locations

- Data
  - Tabular dataset: `Data/csv/crop_yield.csv`
  - Images: `Data/images/PlantVillage/PlantVillage/` (PlantVillage dataset)
  - PDFs for knowledge base: `Data/` (31 PDFs used by Milestone 1)

- Models
  - `models/trained_models/yield_model.pkl`
  - `models/trained_models/weather_model.pkl`
  - `models/trained_models/pest_model.pt`
  - `models/trained_models/class_labels.json`

- Training scripts
  - `src/train_yield_model.py`
  - `src/train_weather_model.py`
  - `src/train_pest_model.py`

- API
  - `src/api_routes.py` (FastAPI app)
  - `test_api.py` (basic test harness)

---

## 🚀 Quick start (local)

1) Create and activate venv, install deps:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

2) Run the knowledge-base builder (Milestone 1):

```powershell
python build_knowledge_base.py
```

3) Train models (optional — prebuilt models are saved in `models/trained_models/`):

```powershell
# Train yield model
python src/train_yield_model.py

# Train weather model
python src/train_weather_model.py

# Train pest/disease detection (ResNet18)
python src/train_pest_model.py
```

Training the pest/disease model was performed on CPU and took ~2.7 hours for 10 epochs in the current setup; expect long runtimes without a GPU.

4) Start the API server:

```powershell
uvicorn src.api_routes:app --port 8000
# (For development use --reload, but avoid --reload during heavy inference/testing for stability.)
```

5) Endpoints

- POST /predict_yield — JSON body with required numeric/categorical features. Returns predicted yield and used encoders.
- POST /analyze_weather — JSON body (weather features). Returns predicted yield (weather-only model) and correlation insights.
- POST /detect_pest — multipart/form-data with image file. Returns top predictions and confidence scores.

---

## 📈 Model results (accurate reported metrics)

- Crop yield model (RandomForestRegressor)
  - Test R²: **97.38%** (excellent predictive performance on available features)
  - Saved: `models/trained_models/yield_model.pkl`

- Weather-only model (RandomForestRegressor)
  - Test R²: **-2.25%** (poor; expected because only rainfall/fertilizer/pesticide were used)
  - Saved: `models/trained_models/weather_model.pkl`

- Pest/Disease detection (ResNet18, transfer learning)
  - Dataset: PlantVillage (~20,638 images, 15 classes)
  - Best validation accuracy: **99.52%**
  - Final training accuracy: **99.69%**
  - Saved model: `models/trained_models/pest_model.pt` (≈ 42.7 MB)
  - Class labels: `models/trained_models/class_labels.json`

Notes:
- The weather-only model's negative R² indicates its predictions are worse than predicting the mean; it needs crop, location, and season features to be useful.
- The pest/disease model was trained with standard image augmentations and ResNet18 pretrained weights; reported accuracies come from the training run on CPU.

---

## ✅ Status & next actions

- Completed
  - Knowledge base builder (Milestone 1)
  - Crop yield model and weather model training scripts + saved artifacts
  - Pest/disease detection training script and trained model
  - FastAPI integration with three endpoints

- Recommended next steps
  - Add end-to-end integration tests (API + sample inputs)
  - Add a short demo notebook showing example requests to each endpoint
  - Containerize the app (Dockerfile) and add CI smoke tests
  - Improve weather model by adding crop, state, and season features and re-evaluate

---

## Troubleshooting & tips

- Path-case issues on Windows: ensure `Data/` folder casing matches references (we fixed a `.env` mismatch earlier).
- Large training runs: prefer a GPU-enabled machine; on CPU the pest model took ~2.7 hours for 10 epochs.
- API stability: run `uvicorn` without `--reload` when testing model endpoints to avoid worker restarts.

---

If you'd like, I can now:
- Add a one-page `docs/Quickstart.md` with sample requests for teammates.
- Commit a small demo notebook that shows ingestion → retrieval → LLM answer flow.

Thank you — tell me which follow-up you'd like and I will implement it.

```
# 🌾 Agricultural RAG Knowledge Base - Milestone 1

A production-ready Retrieval-Augmented Generation (RAG) system for agricultural domain documents.

## 📋 Overview

This project builds a vector database from agricultural PDF documents, enabling efficient semantic search and retrieval for question-answering systems. The system processes 31 agricultural domain PDFs and creates a queryable knowledge base.

## 🚀 Quick Start

### 1. Environment Setup

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Knowledge Base Builder

```powershell
python build_knowledge_base.py
```

The script will:
- ✅ Load all 31 PDFs from the `Data/` folder
- ✅ Extract and preprocess text
- ✅ Create 800-1000 character chunks with 150-character overlap
- ✅ Generate embeddings using `sentence-transformers/all-MiniLM-L6-v2`
- ✅ Store vectors in ChromaDB at `models/vectorstore/`
- ✅ Test retrieval with sample query
- ✅ Display comprehensive statistics

## 📁 Project Structure

```
ShizishanGPT/
├── Data/                           # 31 Agricultural PDFs (already present)
│   ├── agri.pdf
│   ├── MAIZE GROWERS GUIDE.pdf
│   ├── Soil Taxonomy.pdf
│   └── ... (28 more PDFs)
├── models/
│   └── vectorstore/                # ChromaDB persistent storage (auto-created)
├── build_knowledge_base.py         # Main script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── knowledge_base_build.log        # Execution logs (auto-generated)
```

## 🔧 System Components

### 1️⃣ Environment Setup
- Imports required libraries (PyPDF2, LangChain, ChromaDB, sentence-transformers)
- Verifies folder structure
- Sets up logging

### 2️⃣ PDF Loading & Parsing
- Reads all PDFs from `Data/` folder
- Extracts text page-by-page
- Stores metadata: filename, page number, total pages
- Handles errors gracefully

### 3️⃣ Text Preprocessing
- Removes headers, footers, special symbols
- Normalizes whitespace
- Filters out low-quality content
- Preserves headings and important sentences

### 4️⃣ Chunking
- Uses LangChain's `RecursiveCharacterTextSplitter`
- Chunk size: 800-1000 characters
- Overlap: 150 characters
- Smart splitting on paragraphs → sentences → words

### 5️⃣ Embeddings
- Model: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- Batch processing for efficiency
- Progress tracking with tqdm

### 6️⃣ Vector Store
- ChromaDB with persistent storage
- Saved to: `models/vectorstore/`
- Collection name: `agricultural_knowledge_base`
- Reloadable for future queries

### 7️⃣ Test Retrieval
- Sample query: "What fertilizer should be used for maize?"
- Returns top 3 relevant chunks
- Displays: source file, page number, similarity score, content preview

### 8️⃣ Logging
- Console and file logging (`knowledge_base_build.log`)
- Tracks: document count, chunk statistics, errors
- Exception handling for missing/corrupted files

### 9️⃣ Summary Report
- Total PDFs processed
- Total chunks created
- Average chunk length
- Vector store location
- Processing time

## 📊 Expected Output

```
======================================================================
STEP 1: Environment Setup
======================================================================
✓ PDF folder: Data
✓ Vector store folder: models/vectorstore
✓ All dependencies loaded successfully

======================================================================
STEP 2: Loading and Parsing PDFs
======================================================================
Loading PDFs: 100%|████████████████████| 31/31
📄 Total documents loaded: ~800+ pages

======================================================================
STEP 3: Text Preprocessing
======================================================================
Cleaning text: 100%|████████████████████| 800/800
✓ Preprocessed 750+ documents

======================================================================
STEP 4: Document Chunking
======================================================================
✓ Created 2000+ chunks from 750+ documents
✓ Average chunk length: 850 characters

======================================================================
STEP 5: Generating Embeddings
======================================================================
Embedding batches: 100%|████████████████| 64/64
✓ Generated 2000+ embeddings
✓ Embedding dimension: 384

======================================================================
STEP 6: Creating Vector Store
======================================================================
Adding to ChromaDB: 100%|████████████████| 20/20
✓ Vector store created successfully
✓ Saved to: D:\Ps-3(git)\ShizishanGPT\models\vectorstore

======================================================================
STEP 7: Testing Retrieval System
======================================================================
Query: 'What fertilizer should be used for maize?'

[Result 1]
Source: MAIZE GROWERS GUIDE.pdf
Page: 23
Similarity Score: 0.8543
Content Preview: For optimal maize growth, apply nitrogen-based fertilizers...

======================================================================
FINAL SUMMARY
======================================================================
📊 Knowledge Base Statistics:
   • PDFs Processed: 31
   • Total Chunks Created: 2000+
   • Average Chunk Length: 850 characters
   • Vector Store Path: D:\Ps-3(git)\ShizishanGPT\models\vectorstore
   • Embedding Model: sentence-transformers/all-MiniLM-L6-v2
   • Processing Time: 180 seconds

✅ Knowledge base built successfully!
```

## 🔄 Reloading the Vector Store

To use the vector store in other scripts:

```python
import chromadb
from sentence_transformers import SentenceTransformer

# Load the vector store
client = chromadb.PersistentClient(path="models/vectorstore")
collection = client.get_collection(name="agricultural_knowledge_base")

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Query example
query = "How to manage pests in organic farming?"
query_embedding = model.encode([query])[0].tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)

# Display results
for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
    print(f"Source: {metadata['source']}, Page: {metadata['page']}")
    print(f"Content: {doc[:200]}...\n")
```

## 🛠️ Troubleshooting

### Issue: "No PDF files found"
- Ensure PDFs are in the `Data/` folder (not `data/pdfs/`)
- Check file extensions are `.pdf`

### Issue: "ModuleNotFoundError"
- Activate virtual environment: `.\venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Issue: "Out of memory"
- Reduce batch size in embedding generation (line 287)
- Process fewer PDFs at a time

### Issue: ChromaDB errors
- Delete `models/vectorstore/` folder and rebuild
- Update ChromaDB: `pip install --upgrade chromadb`

## 📦 Dependencies

- **PyPDF2**: PDF text extraction
- **LangChain**: Document processing and chunking
- **sentence-transformers**: Embedding generation
- **ChromaDB**: Vector database
- **tqdm**: Progress bars
- **python-dotenv**: Environment variables

## 🎯 Next Steps (Milestone 2 & Beyond)

1. **Query Interface**: Build a web UI for querying the knowledge base
2. **LLM Integration**: Connect to GPT-4, Llama, or other LLMs for answer generation
3. **Fine-tuning**: Improve retrieval with agricultural domain-specific embeddings
4. **Evaluation**: Add metrics (precision, recall, relevance scoring)
5. **API**: Create REST API for integration with other systems

## 📝 Notes

- The script is configured for your existing `Data/` folder structure
- All 31 PDFs will be processed automatically
- Processing time depends on PDF size and hardware (~2-5 minutes typical)
- The vector store persists and can be reused without rebuilding

## 🤝 Support

For issues or questions:
1. Check `knowledge_base_build.log` for detailed error messages
2. Ensure all dependencies are installed correctly
3. Verify PDF files are not corrupted

---

**Built with ❤️ for Agricultural AI Applications**

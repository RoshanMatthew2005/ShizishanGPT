# 🌾 ShizishanGPT - Agricultural AI Assistant

An intelligent agricultural assistant powered by multiple ML models integrated with a ReAct-style reasoning system.

## � Project Overview

ShizishanGPT combines:
- **Multiple specialized ML models** (yield prediction, pest detection, weather analysis)
- **RAG system** for agricultural knowledge retrieval
- **Custom mini-LLM** for natural language understanding
- **ReAct reasoning loop** for intelligent decision-making
- **Interactive frontend** for farmer-friendly interface

## 📂 Project Structure

```
ShizishanGPT/
│
├── data/                      # PDFs, CSVs, images
│   ├── raw/                   # Original data
│   │   ├── pdfs/              # Agricultural PDFs
│   │   ├── csvs/              # Dataset files
│   │   └── images/            # Crop/pest images
│   ├── processed/             # Preprocessed data
│   └── embeddings/            # Vector embeddings
│
├── models/                    # Saved model checkpoints
│   ├── yield_predictor/       # Yield prediction model
│   ├── pest_detector/         # Pest detection model
│   ├── weather_model/         # Weather impact model
│   ├── llm/                   # Language model
│   └── rag/                   # RAG index
│
├── src/
│   ├── preprocessing/         # Data preprocessing scripts
│   ├── rag/                   # RAG retriever implementation
│   ├── llm/                   # Mini LLM implementation
│   ├── tools/                 # ML model tools (yield, pest, weather)
│   └── app/                   # Frontend and API
│
├── docs/                      # Reports, diagrams, presentations
├── logs/                      # Application logs
├── requirements.txt           # Python dependencies
├── config.yaml                # Configuration file
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🏗️ Build Order

### Phase 1: Core ML Models (Tools) ⏳
1. **Yield Prediction Model** - Regression model (Random Forest/MLP)
2. **Pest/Disease Detection** - CNN/ResNet for image classification
3. **Weather Impact Model** - LSTM for time series prediction
4. **RAG Retriever** - TF-IDF/Word2Vec + Cosine Similarity

### Phase 2: Mini LLM 📋
- Text generation and understanding
- Agricultural domain fine-tuning

### Phase 3: Mini LangChain 📋
- Tool orchestration
- Prompt management
- Chain of thought

### Phase 4: ReAct Loop 📋
- Reasoning and action integration
- Multi-step problem solving
- Tool calling logic

### Phase 5: Frontend 📋
- User interface (Streamlit/Gradio)
- API endpoints (FastAPI)
- Visualization dashboards

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/RoshanMatthew2005/ShizishanGPT.git
cd ShizishanGPT
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Prepare your data
- Place PDFs in `data/raw/pdfs/`
- Place CSVs in `data/raw/csvs/`
- Place images in `data/raw/images/`

### 5. Train models (Phase 1)
```bash
python src/tools/train_yield_model.py
python src/tools/train_pest_model.py
python src/tools/train_weather_model.py
```

### 6. Run the application
```bash
streamlit run src/app/main.py
```

## 📊 Model Details

| Model | Purpose | Algorithm | Input | Output |
|-------|---------|-----------|-------|--------|
| 🌾 Yield Predictor | Predict crop yield | Random Forest/MLP | Soil, rainfall, fertilizer | "Yield: 3.4 tons/ha" |
| 🐛 Pest Detector | Detect diseases | CNN/ResNet | Leaf images | "Detected: Maize Leaf Blight" |
| ☁️ Weather Model | Weather impact | LSTM | Weather time series | "Expected yield drop: 15%" |
| 📚 RAG Retriever | Knowledge retrieval | TF-IDF/Word2Vec | Query text | Relevant passages |

## 🛠️ Tech Stack

- **ML/DL:** PyTorch, Scikit-learn, TensorFlow
- **NLP:** Transformers, LangChain, Sentence-Transformers
- **Vector Store:** FAISS, ChromaDB
- **Frontend:** Streamlit/Gradio
- **API:** FastAPI
- **CV:** OpenCV, Albumentations
- **Time Series:** LSTM, Statsmodels

## 📝 Configuration

Edit `config.yaml` to customize:
- Model architectures and hyperparameters
- Data paths
- API endpoints
- Logging settings
- ReAct loop parameters

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run specific test
pytest tests/test_yield_predictor.py
```

## 📈 Current Status

- ✅ Folder structure created
- ✅ requirements.txt configured
- ✅ config.yaml configured
- ✅ .gitignore configured
- ✅ README.md documented
- ⏳ Phase 1: Core ML Models (NEXT STEP)
- ⏳ Phase 2: Mini LLM
- ⏳ Phase 3: Mini LangChain
- ⏳ Phase 4: ReAct Loop
- ⏳ Phase 5: Frontend

## 🎯 Next Development Steps

**Recommended Starting Point: Phase 1 - Yield Prediction Model**

1. Create `src/tools/yield_predictor.py`
2. Create sample dataset or use existing agricultural data
3. Train Random Forest regression model
4. Save model checkpoint
5. Create inference function
6. Test with sample inputs

**After Yield Predictor:**
- Build Pest Detection (CNN)
- Build Weather Model (LSTM)
- Build RAG Retriever
- Then move to Phase 2-5

## 🔑 Key Technologies & Concepts

- **ReAct**: Reasoning + Acting paradigm for AI agents
- **RAG**: Retrieval-Augmented Generation for knowledge-based responses
- **LangChain**: Framework for LLM application orchestration
- **Multi-Model Integration**: Specialized models working together
- **Agricultural AI**: Domain-specific AI for farming assistance

## 📖 Documentation

- [Project Setup Guide](docs/setup.md)
- [Model Training Guide](docs/training.md)
- [API Documentation](docs/api.md)
- [Contributing Guidelines](docs/contributing.md)

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines before submitting PRs.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributors

- **Roshan Matthew** - Project Creator
- [Add contributors here]

## 📧 Contact

For questions or feedback, please contact:
- GitHub: [@RoshanMatthew2005](https://github.com/RoshanMatthew2005)
- Repository: [ShizishanGPT](https://github.com/RoshanMatthew2005/ShizishanGPT)

---

**Project Created:** October 22, 2025  
**Version:** 0.1.0  
**Status:** 🚧 Under Active Development

---

### 🌟 Star this repository if you find it helpful!

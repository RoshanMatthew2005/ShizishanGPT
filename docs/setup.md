# ShizishanGPT - Project Setup Guide

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/RoshanMatthew2005/ShizishanGPT.git
cd ShizishanGPT

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Project Structure

The project follows a modular architecture:

- **data/**: All datasets (PDFs, CSVs, images)
- **models/**: Trained model checkpoints
- **src/**: Source code
  - **preprocessing/**: Data loading and feature engineering
  - **tools/**: ML models (yield, pest, weather)
  - **rag/**: Knowledge retrieval system
  - **llm/**: Language model
  - **app/**: Frontend application
- **docs/**: Documentation
- **logs/**: Application logs

### 3. Configuration

Edit `config.yaml` to customize:
- Data paths
- Model hyperparameters
- API settings
- Logging configuration

### 4. Development Workflow

Follow this 5-phase approach:

#### Phase 1: Core ML Models ⏳ (Current)
1. Yield Predictor
2. Pest Detector
3. Weather Model
4. RAG Retriever

#### Phase 2: Mini LLM
- Fine-tune language model on agricultural data

#### Phase 3: Mini LangChain
- Build tool orchestration system

#### Phase 4: ReAct Loop
- Implement reasoning and acting logic

#### Phase 5: Frontend
- Complete Streamlit/Gradio interface

### 5. Running the Application

```bash
# Run Streamlit app
streamlit run src/app/main.py

# Or FastAPI (Phase 5)
uvicorn src.app.api:app --reload
```

### 6. Training Models

```bash
# Train yield predictor
python src/tools/yield_predictor.py

# Train pest detector
python src/tools/pest_detector.py

# Train weather model
python src/tools/weather_model.py
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure virtual environment is activated
2. **CUDA errors**: Check PyTorch installation matches your CUDA version
3. **Memory errors**: Reduce batch sizes in config.yaml

### GPU Support

For GPU acceleration:
```bash
# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install FAISS GPU version
pip uninstall faiss-cpu
pip install faiss-gpu
```

## Next Steps

1. Prepare your agricultural datasets
2. Place data in appropriate folders
3. Train Phase 1 models
4. Test individual components
5. Move to Phase 2

For more details, see individual module documentation.

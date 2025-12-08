# Mini LLM - Agricultural Language Model

This module implements a custom fine-tuned language model trained on agricultural data.

## 📁 Directory Structure

```
mini_llm/
├── data/
│   ├── agri_corpus.txt      # Cleaned agricultural text corpus
│   └── qa_pairs.jsonl        # Q&A pairs for supervised training
├── extract_and_clean_pdfs.py # Step 1: Extract and clean PDF text
├── generate_qa_pairs.py      # Step 2: Generate Q&A dataset
└── inference.py              # Step 4: Run inference with trained model

models/
└── mini_llm/                 # Trained model files (after training)
    ├── config.json
    ├── pytorch_model.bin
    ├── tokenizer.json
    └── tokenizer_config.json

train_mini_llm.py             # Step 3: Training script
```

## 🚀 Quick Start

### Step 1: Extract and Clean PDFs

```bash
python mini_llm/extract_and_clean_pdfs.py
```

This script:
- Reads all PDFs from `data/pdfs/`
- Cleans text (removes headers, footers, tables, special characters)
- Merges broken lines into paragraphs
- Removes duplicates
- Saves to `mini_llm/data/agri_corpus.txt`

### Step 2: Generate Q&A Pairs

```bash
python mini_llm/generate_qa_pairs.py
```

This script:
- Analyzes the cleaned corpus
- Detects agricultural concepts (crops, pests, diseases, fertilizers)
- Generates 150 Q&A pairs
- Saves to `mini_llm/data/qa_pairs.jsonl`

### Step 3: Train the Model

```bash
python train_mini_llm.py
```

This script:
- Fine-tunes DistilGPT-2 on agricultural data
- Uses both corpus and Q&A pairs
- Saves model to `models/mini_llm/`

**Training Configuration:**
- Model: DistilGPT-2 (smaller, faster GPT-2)
- Batch size: 2
- Max length: 256 tokens
- Learning rate: 5e-5
- Epochs: 3
- Gradient accumulation: 4 steps
- Device: CPU/CUDA (auto-detected)

**Expected Training Time:**
- On CPU: 2-4 hours (depending on corpus size)
- On GPU: 30-60 minutes

### Step 4: Run Inference

```bash
python mini_llm/inference.py
```

**Modes:**
1. **Interactive Mode** - Ask questions interactively
2. **Batch Test Mode** - Run predefined test questions
3. **Single Prompt** - Generate text for one prompt

## 📊 Example Usage

### Interactive Mode

```
🌾 You: How to grow maize?
🤖 AgriLLM: Maize cultivation requires proper soil preparation, adequate
fertilization, and timely irrigation. Plant seeds at a depth of 5-7 cm
with spacing of 75 cm between rows and 25 cm between plants...
```

### Q&A Format

The model is trained on Q&A pairs in this format:
```
Q: What fertilizer should be used for tomatoes?
A: Tomatoes require balanced NPK fertilizer with emphasis on phosphorus
for fruit development. Apply 2-3 kg of NPK (10-26-10) per 100 sq meters...
```

### Text Completion

```python
from mini_llm.inference import AgriLLM

llm = AgriLLM()
response = llm.continue_text("Maize cultivation requires")
print(response)
```

## 🔧 Advanced Configuration

### Modify Training Parameters

Edit `train_mini_llm.py`:
```python
MAX_LENGTH = 256          # Sequence length
BATCH_SIZE = 2            # Batch size
LEARNING_RATE = 5e-5      # Learning rate
NUM_EPOCHS = 3            # Training epochs
```

### Modify Generation Parameters

Edit `mini_llm/inference.py`:
```python
TEMPERATURE = 0.7   # Higher = more creative (0.1-1.0)
TOP_K = 50          # Top-k sampling
TOP_P = 0.95        # Nucleus sampling
```

## 📝 Data Format

### Corpus Format (agri_corpus.txt)
```
Maize is a staple crop requiring specific conditions. The optimal
temperature for growth is 20-30 degrees Celsius. Proper soil drainage
is essential for healthy root development.

Fertilization should be done in stages. Apply nitrogen-rich fertilizer
during the vegetative stage and phosphorus during flowering.
```

### Q&A Format (qa_pairs.jsonl)
```json
{"question": "How to control pests in maize?", "answer": "Pest control..."}
{"question": "What is the best irrigation method?", "answer": "Drip irrigation..."}
```

## 🎯 Model Capabilities

The fine-tuned model can:
- ✅ Answer agricultural questions
- ✅ Complete agricultural text
- ✅ Provide farming recommendations
- ✅ Explain agricultural concepts
- ✅ Generate context-aware responses

## ⚠️ Limitations

- Model is limited to agricultural domain knowledge from PDFs
- Generated text may not always be factually accurate
- Responses are based on training data quality
- CPU training is slower than GPU

## 🐛 Troubleshooting

**Issue: Model not found**
```
Solution: Make sure you've run train_mini_llm.py first
```

**Issue: Out of memory during training**
```
Solution: Reduce BATCH_SIZE to 1 in train_mini_llm.py
```

**Issue: Poor generation quality**
```
Solution: 
- Train for more epochs (increase NUM_EPOCHS)
- Increase corpus size (add more PDFs)
- Adjust temperature/top_k/top_p in inference.py
```

## 📚 Files Generated

After running all steps:
- `mini_llm/data/agri_corpus.txt` (~500KB-2MB depending on PDFs)
- `mini_llm/data/qa_pairs.jsonl` (~50-100KB)
- `models/mini_llm/` directory (~350MB for DistilGPT-2)

## 🔄 Retraining

To retrain with new data:
1. Add new PDFs to `data/pdfs/`
2. Re-run extraction: `python mini_llm/extract_and_clean_pdfs.py`
3. Re-generate Q&A: `python mini_llm/generate_qa_pairs.py`
4. Retrain model: `python train_mini_llm.py`

The new model will overwrite the previous one in `models/mini_llm/`.

## 📖 References

- Model: [DistilGPT-2](https://huggingface.co/distilgpt2)
- Framework: [HuggingFace Transformers](https://huggingface.co/docs/transformers)
- Training: Causal Language Modeling fine-tuning

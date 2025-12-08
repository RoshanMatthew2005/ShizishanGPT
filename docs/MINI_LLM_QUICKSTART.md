# 🚀 Mini LLM Quick Start Guide

## Overview

You now have a complete Mini LLM implementation for agricultural text generation! The corpus has been successfully extracted from 31 PDFs.

---

## ✅ What's Been Done

### Step 1: PDF Extraction ✅ COMPLETE
```
✓ Processed: 31 PDFs
✓ Extracted: 5,790 pages
✓ Generated: 13.9 MB corpus (2.2M words, 32,750 paragraphs)
✓ File: mini_llm/data/agri_corpus.txt
```

---

## 📋 Next Steps

### Step 2: Generate Q&A Pairs

```bash
python mini_llm\generate_qa_pairs.py
```

**Expected time:** 2-5 minutes  
**Output:** 150 Q&A pairs in `mini_llm/data/qa_pairs.jsonl`

---

### Step 3: Train the Model

```bash
python train_mini_llm.py
```

**Expected time:** 
- CPU: 2-4 hours
- GPU: 30-60 minutes

**Output:** Trained model in `models/mini_llm/`

**Training Stats:**
- Model: DistilGPT-2 (82M parameters)
- Training examples: ~35,000+
- Epochs: 3
- Final model size: ~350 MB

---

### Step 4: Test the Model

```bash
python mini_llm\inference.py
```

Select mode 1 (Interactive) and ask questions like:
- "How to grow maize?"
- "What fertilizer for tomatoes?"
- "How to control pests?"

---

## ⚡ Quick Pipeline Execution

Run everything at once:

```bash
# Option 1: Complete pipeline (including training)
python run_mini_llm_pipeline.py

# Option 2: Generate data only (skip training for now)
python run_mini_llm_pipeline.py --skip-training
```

---

## 📊 Current Status

| Step | Status | Time | Output |
|------|--------|------|--------|
| 1. Extract PDFs | ✅ Done | 7 min | 13.9 MB corpus |
| 2. Generate Q&A | ⏳ Ready | ~3 min | 150 pairs |
| 3. Train Model | ⏳ Ready | 2-4 hrs | 350 MB model |
| 4. Inference | ⏳ Ready | N/A | Interactive |

---

## 💡 Important Notes

### For CPU Training
- Be patient - training takes 2-4 hours on CPU
- You can reduce epochs to 2 for faster training
- Lower batch size if you get memory errors

### For GPU Training
- Much faster (~30-60 minutes)
- Install CUDA-enabled PyTorch:
  ```bash
  pip install torch --index-url https://download.pytorch.org/whl/cu118
  ```

### Monitoring Training
The training script will show:
- Progress bars for each epoch
- Loss values (should decrease from ~2.5 to ~1.2)
- Checkpoint saves every 500 steps
- Final model save location

---

## 🎯 Expected Results

After training, your model will be able to:

✅ **Answer agricultural questions**
```
Q: How to grow maize?
A: Maize cultivation requires well-drained loamy soil with pH 6-7.5.
   Plant seeds at 5-7 cm depth with 75cm row spacing. Apply nitrogen
   fertilizer during vegetative stage...
```

✅ **Complete agricultural text**
```
Input: "The ideal irrigation method for"
Output: "The ideal irrigation method for maize is drip irrigation or
        furrow irrigation, ensuring even water distribution..."
```

✅ **Provide recommendations**
```
Q: What fertilizer should be used for tomatoes?
A: Tomatoes require balanced NPK fertilizer with higher phosphorus
   for fruit development. Apply 10-26-10 NPK at 2-3 kg per 100 sq m...
```

---

## 🔍 File Locations

```
mini_llm/data/agri_corpus.txt        # ✅ Created (13.9 MB)
mini_llm/data/qa_pairs.jsonl         # ⏳ Run Step 2
models/mini_llm/                     # ⏳ Run Step 3
models/mini_llm_checkpoints/         # ⏳ Training checkpoints
```

---

## 🐛 Troubleshooting

### Out of Memory Error
```bash
# Edit train_mini_llm.py and change:
BATCH_SIZE = 1  # Instead of 2
```

### Training Too Slow
```bash
# Edit train_mini_llm.py and change:
NUM_EPOCHS = 2  # Instead of 3
MAX_LENGTH = 128  # Instead of 256
```

### Want to Test Without Training
```bash
# You can use the base DistilGPT-2 model:
# Edit mini_llm/inference.py and change MODEL_DIR to "distilgpt2"
```

---

## 📚 Documentation

- **Complete Guide:** `docs/MILESTONE_3_COMPLETE.md`
- **Module README:** `mini_llm/README.md`
- **Training Script:** `train_mini_llm.py` (heavily commented)
- **Inference Script:** `mini_llm/inference.py` (heavily commented)

---

## 🎉 Summary

You have successfully completed:
1. ✅ PDF extraction and cleaning (31 PDFs → 2.2M words)
2. ✅ Directory structure creation
3. ✅ All scripts ready to execute

**Next action:** Run Step 2 to generate Q&A pairs!

```bash
python mini_llm\generate_qa_pairs.py
```

---

**Estimated total time to complete all steps:**
- Step 2 (Q&A): 3 minutes
- Step 3 (Training): 2-4 hours (CPU) or 30-60 min (GPU)
- Step 4 (Testing): Instant

**Good luck! 🌾**

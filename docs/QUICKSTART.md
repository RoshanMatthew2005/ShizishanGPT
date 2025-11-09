# Quick Start Guide - RAG Knowledge Base

## 🚀 Setup (First Time Only)

### Step 1: Create Virtual Environment
```powershell
python -m venv venv
```

### Step 2: Activate Virtual Environment
```powershell
.\venv\Scripts\activate
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

**Note:** This will take 2-5 minutes as it downloads the embedding model (~80MB)

---

## ▶️ Running the Knowledge Base Builder

### Build the Knowledge Base
```powershell
python build_knowledge_base.py
```

**What happens:**
- ✅ Loads all 31 PDFs from `Data/` folder
- ✅ Processes ~800+ pages of agricultural content
- ✅ Creates 2000+ searchable chunks
- ✅ Generates embeddings using AI model
- ✅ Saves to `models/vectorstore/` folder
- ✅ Tests retrieval with sample query

**Processing time:** ~2-5 minutes (depends on your CPU)

---

## 🔍 Querying the Knowledge Base

### Interactive Query Mode (Recommended)
```powershell
python query_knowledge_base.py
```

Then select option 1 and ask questions like:
- "What fertilizer should be used for maize?"
- "How to manage pests in organic farming?"
- "What are the best practices for soil conservation?"

---

## 📂 Project Files

```
ShizishanGPT/
├── Data/                          # Your 31 PDFs (already present)
├── models/vectorstore/            # Vector database (created after running)
├── build_knowledge_base.py        # Main builder script
├── query_knowledge_base.py        # Interactive query tool
├── requirements.txt               # Python dependencies
├── README.md                      # Full documentation
└── QUICKSTART.md                  # This file
```

---

## ⚠️ Troubleshooting

### "No module named X"
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "No PDF files found"
- Check that PDFs are in `Data/` folder (not `data/pdfs/`)
- Your current setup has 31 PDFs already in `Data/` ✓

### Script runs but no output
- Check `knowledge_base_build.log` for detailed logs
- Make sure you have write permissions to the folder

---

## 📊 Expected Output Summary

After running `build_knowledge_base.py`, you'll see:

```
======================================================================
FINAL SUMMARY
======================================================================

📊 Knowledge Base Statistics:
   • PDFs Processed: 31
   • Total Chunks Created: 2000+
   • Average Chunk Length: 850 characters
   • Vector Store Path: D:\Ps-3(git)\ShizishanGPT\models\vectorstore
   • Collection Name: agricultural_knowledge_base
   • Embedding Model: sentence-transformers/all-MiniLM-L6-v2
   • Processing Time: ~180 seconds

✅ Knowledge base built successfully!
```

---

## 🎯 Next Steps

1. ✅ Run `build_knowledge_base.py` once to create the database
2. ✅ Use `query_knowledge_base.py` anytime to search
3. ✅ Integrate with LLMs (GPT-4, Llama) for answer generation
4. ✅ Build a web interface or API

---

## 💡 Tips

- **One-time build:** You only need to run `build_knowledge_base.py` once
- **Reusable:** The vector store persists in `models/vectorstore/`
- **Add PDFs:** To add new PDFs, just place them in `Data/` and rebuild
- **Logs:** Check `knowledge_base_build.log` for detailed execution logs

---

**Need Help?** Check the full `README.md` for detailed documentation.

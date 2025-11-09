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

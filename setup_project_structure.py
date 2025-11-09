"""
setup_project_structure.py

Automatically creates the complete folder structure and placeholder files 
for ShizishanGPT — AI-Powered Agricultural Knowledge Assistant.

Author: AI Engineer
Date: November 9, 2025
"""

import os
from pathlib import Path
import shutil


def create_directory(path: Path, description: str = "") -> None:
    """
    Create a directory if it doesn't exist.
    
    Args:
        path: Path object for the directory
        description: Optional description for logging
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {path}" + (f" ({description})" if description else ""))
    else:
        print(f"⊗ Exists:  {path}" + (f" ({description})" if description else ""))


def create_placeholder_file(path: Path, content: str = "", description: str = "") -> None:
    """
    Create a placeholder file if it doesn't exist.
    
    Args:
        path: Path object for the file
        content: Initial content for the file
        description: Optional description for logging
    """
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Created: {path}" + (f" ({description})" if description else ""))
    else:
        print(f"⊗ Exists:  {path}" + (f" ({description})" if description else ""))


def move_file_if_exists(src: Path, dest: Path, description: str = "") -> None:
    """
    Move a file from source to destination if source exists.
    
    Args:
        src: Source path
        dest: Destination path
        description: Optional description for logging
    """
    if src.exists() and not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        print(f"→ Moved:   {src} → {dest}" + (f" ({description})" if description else ""))
    elif dest.exists():
        print(f"⊗ Exists:  {dest}" + (f" ({description})" if description else ""))


def setup_project_structure():
    """Main function to set up the complete project structure."""
    
    # Get the project root directory
    root = Path(__file__).parent.resolve()
    print(f"\n{'=' * 70}")
    print(f"ShizishanGPT Project Structure Setup")
    print(f"{'=' * 70}")
    print(f"Root: {root}\n")
    
    # =========================================================================
    # STEP 1: Create main data directories
    # =========================================================================
    print(f"\n{'─' * 70}")
    print("STEP 1: Setting up data directories")
    print(f"{'─' * 70}")
    
    data_root = root / "data"
    create_directory(data_root, "Main data directory")
    create_directory(data_root / "pdfs", "PDF documents storage")
    create_directory(data_root / "csv", "CSV datasets storage")
    create_directory(data_root / "images", "Image data storage")
    create_directory(data_root / "knowledge_graph", "Knowledge graph data")
    
    # Move existing PDFs from Data/ to data/pdfs/
    old_data = root / "Data"
    if old_data.exists() and old_data.is_dir():
        print(f"\n  Moving PDFs from Data/ to data/pdfs/...")
        pdf_files = list(old_data.glob("*.pdf"))
        for pdf in pdf_files:
            dest = data_root / "pdfs" / pdf.name
            if not dest.exists():
                shutil.copy2(str(pdf), str(dest))
                print(f"  → Copied: {pdf.name}")
    
    # =========================================================================
    # STEP 2: Create models directories
    # =========================================================================
    print(f"\n{'─' * 70}")
    print("STEP 2: Setting up models directories")
    print(f"{'─' * 70}")
    
    models_root = root / "models"
    create_directory(models_root, "Main models directory")
    create_directory(models_root / "vectorstore", "Vector database storage")
    create_directory(models_root / "trained_models", "ML/DL trained models")
    create_directory(models_root / "embeddings", "Embedding models cache")
    
    # =========================================================================
    # STEP 3: Create src/ directory and move existing scripts
    # =========================================================================
    print(f"\n{'─' * 70}")
    print("STEP 3: Setting up src/ directory")
    print(f"{'─' * 70}")
    
    src_root = root / "src"
    create_directory(src_root, "Source code directory")
    
    # Move existing Python scripts to src/
    existing_scripts = [
        ("build_knowledge_base.py", "RAG knowledge base builder"),
        ("query_knowledge_base.py", "Query interface for RAG"),
        ("test_knowledge_base.py", "Testing script"),
    ]
    
    for script_name, desc in existing_scripts:
        src_file = root / script_name
        dest_file = src_root / script_name
        move_file_if_exists(src_file, dest_file, desc)
    
    # Create placeholder Python files in src/
    src_placeholders = {
        "query_rag.py": '"""Query interface for RAG system."""\n\n# TODO: Implement RAG query logic\n',
        "train_yield_model.py": '"""Train crop yield prediction model."""\n\n# TODO: Implement yield prediction\n',
        "train_pest_model.py": '"""Train pest detection model."""\n\n# TODO: Implement pest detection\n',
        "langchain_interface.py": '"""LangChain integration for LLM."""\n\n# TODO: Implement LangChain interface\n',
        "llm_response_handler.py": '"""Handle LLM responses and formatting."""\n\n# TODO: Implement response handling\n',
        "api_routes.py": '"""FastAPI routes for backend."""\n\n# TODO: Implement API routes\n',
        "agrikg_connector.py": '"""Agricultural Knowledge Graph connector."""\n\n# TODO: Implement KG connector\n',
    }
    
    for filename, content in src_placeholders.items():
        create_placeholder_file(src_root / filename, content, f"Source: {filename}")
    
    # =========================================================================
    # STEP 4: Create frontend structure
    # =========================================================================
    print(f"\n{'─' * 70}")
    print("STEP 4: Setting up frontend/ directory")
    print(f"{'─' * 70}")
    
    frontend_root = root / "frontend"
    create_directory(frontend_root, "Frontend application")
    create_directory(frontend_root / "public", "Static assets")
    create_directory(frontend_root / "src", "React/Vue source")
    
    # Create package.json placeholder
    package_json_content = """{
  "name": "shizishangpt-frontend",
  "version": "1.0.0",
  "description": "Frontend for ShizishanGPT Agricultural Assistant",
  "main": "index.js",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "react-scripts": "5.0.1"
  }
}
"""
    create_placeholder_file(frontend_root / "package.json", package_json_content, "NPM package config")
    
    # =========================================================================
    # STEP 5: Create middleware structure
    # =========================================================================
    print(f"\n{'─' * 70}")
    print("STEP 5: Setting up middleware/ directory")
    print(f"{'─' * 70}")
    
    middleware_root = root / "middleware"
    create_directory(middleware_root, "Backend middleware")
    create_directory(middleware_root / "routes", "API routes")
    create_directory(middleware_root / "controllers", "Request controllers")
    
    # Create server.js placeholder
    server_js_content = """// server.js
// Express/Node.js server for ShizishanGPT middleware

const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// TODO: Import routes
// const apiRoutes = require('./routes/api');
// app.use('/api', apiRoutes);

app.listen(PORT, () => {
  console.log(`ShizishanGPT middleware running on port ${PORT}`);
});
"""
    create_placeholder_file(middleware_root / "server.js", server_js_content, "Express server")
    
    # =========================================================================
    # STEP 6: Create docs/ directory
    # =========================================================================
    print(f"\n{'─' * 70}")
    print("STEP 6: Setting up docs/ directory")
    print(f"{'─' * 70}")
    
    docs_root = root / "docs"
    create_directory(docs_root, "Documentation")
    
    # Move existing documentation
    existing_docs = [
        ("README.md", "Project README"),
        ("PROJECT_SUMMARY.md", "Project summary"),
        ("QUICKSTART.md", "Quick start guide"),
        ("BUILD_SUCCESS_REPORT.md", "Build report"),
    ]
    
    for doc_name, desc in existing_docs:
        src_file = root / doc_name
        dest_file = docs_root / doc_name
        # Keep README.md at root, copy others
        if doc_name == "README.md":
            if src_file.exists() and not dest_file.exists():
                shutil.copy2(str(src_file), str(dest_file))
                print(f"→ Copied: {doc_name} to docs/ ({desc})")
        else:
            move_file_if_exists(src_file, dest_file, desc)
    
    # Create placeholder documentation files
    docs_placeholders = {
        "SRS_ShizishanGPT.docx": "",  # Binary file, just create empty
        "milestone1_report.md": "# Milestone 1 Report\n\n## Overview\n\nTODO: Document milestone 1 achievements\n",
        "architecture_diagram.png": "",  # Binary file
        "workflow_plan.pptx": "",  # Binary file
    }
    
    for filename, content in docs_placeholders.items():
        if not (docs_root / filename).exists():
            # Skip binary files for now, just note them
            if filename.endswith(('.png', '.docx', '.pptx')):
                print(f"⊙ Skipped: {docs_root / filename} (binary file - create manually)")
            else:
                create_placeholder_file(docs_root / filename, content, f"Doc: {filename}")
    
    # =========================================================================
    # STEP 7: Create/update root-level configuration files
    # =========================================================================
    print(f"\n{'─' * 70}")
    print("STEP 7: Setting up root configuration files")
    print(f"{'─' * 70}")
    
    # Create/update .env
    env_content = """# ShizishanGPT Environment Configuration

# Paths
PDF_DIRECTORY=data/pdfs
VECTOR_STORE_DIRECTORY=models/vectorstore
BUILD_LOG_PATH=knowledge_base_build.log

# ChromaDB Configuration
CHROMA_COLLECTION_NAME=agricultural_knowledge_base

# Text Processing
CHUNK_SIZE=900
CHUNK_OVERLAP=150

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=64

# Testing
TEST_QUERY=What fertilizer should be used for maize?

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# LLM Configuration (add your keys)
OPENAI_API_KEY=your-key-here
HUGGINGFACE_API_KEY=your-key-here
"""
    
    if not (root / ".env").exists():
        create_placeholder_file(root / ".env", env_content, "Environment variables")
    else:
        print(f"⊗ Exists:  {root / '.env'} (Environment variables)")
    
    # Create/update requirements.txt (preserve existing if present)
    if not (root / "requirements.txt").exists():
        requirements_content = """# ShizishanGPT Python Dependencies

# Core Libraries
python-dotenv==1.0.0

# PDF Processing
PyPDF2==3.0.1

# LangChain Ecosystem
langchain==0.1.0
langchain-community==0.0.13

# Embeddings & Vector Store
sentence-transformers==2.2.2
chromadb==0.4.22

# Progress Bars
tqdm==4.66.1

# Web Framework (for API)
fastapi==0.109.0
uvicorn==0.27.0

# Data Processing
pandas==2.1.4
numpy==1.26.3

# Machine Learning (optional)
scikit-learn==1.4.0
torch==2.1.2

# Utilities
requests==2.31.0
"""
        create_placeholder_file(root / "requirements.txt", requirements_content, "Python dependencies")
    else:
        print(f"⊗ Exists:  {root / 'requirements.txt'} (Python dependencies)")
    
    # Keep README.md at root (don't move)
    if not (root / "README.md").exists():
        readme_content = """# 🌾 ShizishanGPT — AI-Powered Agricultural Knowledge Assistant

An intelligent agricultural assistant powered by RAG (Retrieval-Augmented Generation) and machine learning.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   python -m venv venv
   .\\venv\\Scripts\\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Set up the project structure:**
   ```bash
   python setup_project_structure.py
   ```

3. **Build the knowledge base:**
   ```bash
   python src/build_knowledge_base.py
   ```

4. **Query the system:**
   ```bash
   python src/query_knowledge_base.py
   ```

## 📁 Project Structure

See `docs/architecture_diagram.png` for detailed architecture.

## 📝 Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Project Summary](docs/PROJECT_SUMMARY.md)
- [SRS Document](docs/SRS_ShizishanGPT.docx)

## 🤝 Contributing

See `docs/workflow_plan.pptx` for development workflow.

---

**Built with ❤️ for Agricultural AI Applications**
"""
        create_placeholder_file(root / "README.md", readme_content, "Project README")
    else:
        print(f"⊗ Exists:  {root / 'README.md'} (Project README)")
    
    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Models & Data
models/vectorstore/
models/trained_models/
models/embeddings/
data/pdfs/*.pdf
data/csv/*.csv
data/images/*.jpg
data/images/*.png

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build/
*.egg-info/
"""
    
    if not (root / ".gitignore").exists():
        create_placeholder_file(root / ".gitignore", gitignore_content, "Git ignore rules")
    else:
        print(f"⊗ Exists:  {root / '.gitignore'} (Git ignore rules)")
    
    # =========================================================================
    # STEP 8: Update existing file paths in build_knowledge_base.py
    # =========================================================================
    print(f"\n{'─' * 70}")
    print("STEP 8: Updating file paths in source files")
    print(f"{'─' * 70}")
    
    # Update .env to use new paths
    print("  ℹ Note: Update your .env file to use new paths (data/pdfs, models/vectorstore)")
    print("  ℹ Note: Update import paths in src/ files if needed")
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print(f"\n{'=' * 70}")
    print("✅ Project setup complete!")
    print(f"{'=' * 70}")
    print("\n📋 Next Steps:")
    print("  1. Review and update .env with your API keys and configurations")
    print("  2. Activate virtual environment: .\\venv\\Scripts\\activate")
    print("  3. Install dependencies: pip install -r requirements.txt")
    print("  4. Place your PDF files in: data/pdfs/")
    print("  5. Run knowledge base builder: python src/build_knowledge_base.py")
    print("\n📁 Structure created at:", root)
    print("\n📖 See README.md for detailed usage instructions")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    setup_project_structure()

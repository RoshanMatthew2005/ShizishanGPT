"""
Installation Script for FastAPI Backend
Automates dependency installation and environment setup
"""

import subprocess
import sys
from pathlib import Path


def print_header(message):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")


def run_command(command, description):
    """Run a shell command"""
    print(f"▶ {description}")
    print(f"  Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"  ✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed: {e}")
        print(f"  Error output: {e.stderr}")
        return False


def main():
    """Main installation process"""
    print_header("ShizishanGPT FastAPI Backend - Installation")
    
    # Check Python version
    print("Checking Python version...")
    python_version = sys.version_info
    print(f"  Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or python_version.minor < 8:
        print("  ❌ Python 3.8+ required")
        return
    print("  ✅ Python version OK")
    
    # Install dependencies
    print_header("Installing Dependencies")
    
    requirements_file = Path("src/backend/requirements.txt")
    
    if not requirements_file.exists():
        print(f"  ❌ Requirements file not found: {requirements_file}")
        return
    
    success = run_command(
        f"pip install -r {requirements_file}",
        "Installing Python packages"
    )
    
    if not success:
        print("\n⚠️  Installation failed. Please check errors above.")
        return
    
    # Create directories
    print_header("Creating Directories")
    
    directories = [
        "logs",
        "uploads",
        "models",
        "vectorstore"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: {directory}")
        else:
            print(f"  ℹ️  Exists: {directory}")
    
    # Check model files
    print_header("Checking Model Files")
    
    model_files = {
        "Yield Model": "models/yield_model.pkl",
        "Pest Model": "Model/best_plant_disease_model.pth",
        "VectorStore": "vectorstore",
        "Mini LLM": "fine_tuned_agri_mini_llm"
    }
    
    all_present = True
    for name, path in model_files.items():
        if Path(path).exists():
            print(f"  ✅ {name}: {path}")
        else:
            print(f"  ⚠️  {name} not found: {path}")
            all_present = False
    
    # Create .env template
    print_header("Environment Configuration")
    
    env_file = Path(".env")
    if not env_file.exists():
        env_template = """# FastAPI Backend Configuration

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Model Paths
YIELD_MODEL_PATH=models/yield_model.pkl
PEST_MODEL_PATH=Model/best_plant_disease_model.pth
VECTORSTORE_PATH=vectorstore
LLM_MODEL_PATH=fine_tuned_agri_mini_llm

# MongoDB (Optional - leave empty to disable)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=shizishangpt
MONGODB_COLLECTION=query_logs

# LLM Configuration
MAX_LENGTH=150
TEMPERATURE=0.9

# Upload Limits
MAX_UPLOAD_SIZE=10485760
"""
        env_file.write_text(env_template)
        print(f"  ✅ Created .env template")
        print(f"  ℹ️  Please review and update .env file")
    else:
        print(f"  ℹ️  .env file already exists")
    
    # Summary
    print_header("Installation Summary")
    
    print("✅ Dependencies installed")
    print("✅ Directories created")
    
    if all_present:
        print("✅ All model files found")
    else:
        print("⚠️  Some model files missing - please train models first")
    
    print("✅ Configuration template created")
    
    print("\n" + "=" * 60)
    print("  🎉 Installation Complete!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("  1. Review .env file")
    print("  2. Ensure model files are present")
    print("  3. Start the backend:")
    print("     python src/backend/main.py")
    print("  4. Test the endpoints:")
    print("     python src/backend/test_backend.py")
    print("\n")


if __name__ == "__main__":
    main()

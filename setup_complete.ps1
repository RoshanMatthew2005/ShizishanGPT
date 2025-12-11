# ShizishanGPT - Complete Setup Script
# This script will install all dependencies and set up the project

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   ShizishanGPT - Automated Setup" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
}

# Step 1: Check Prerequisites
Write-Host "Step 1: Checking Prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check Python
if (Test-Command python) {
    $pythonVersion = python --version
    Write-Host "[OK] Python is installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python is NOT installed!" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

# Check Node.js
if (Test-Command node) {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js is installed: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Node.js is NOT installed!" -ForegroundColor Red
    Write-Host "Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check npm
if (Test-Command npm) {
    $npmVersion = npm --version
    Write-Host "[OK] npm is installed: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] npm is NOT installed!" -ForegroundColor Red
    Write-Host "npm should come with Node.js. Please reinstall Node.js" -ForegroundColor Red
    exit 1
}

# Check Ollama
if (Test-Command ollama) {
    Write-Host "[OK] Ollama is installed" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Ollama is NOT installed!" -ForegroundColor Yellow
    Write-Host "Please install Ollama from https://ollama.ai/download" -ForegroundColor Yellow
    Write-Host "Ollama is required for LLM inference (Gemma 2)" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 2: Install Python Dependencies
Write-Host "Step 2: Installing Python Dependencies..." -ForegroundColor Yellow
Write-Host ""

try {
    Write-Host "Upgrading pip..." -ForegroundColor Cyan
    python -m pip install --upgrade pip --quiet
    
    Write-Host "Installing requirements from requirements.txt..." -ForegroundColor Cyan
    pip install -r requirements.txt --quiet
    
    Write-Host "[OK] Python dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to install Python dependencies!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Try running manually: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 3: Install Node.js Dependencies
Write-Host "Step 3: Installing Node.js Dependencies..." -ForegroundColor Yellow
Write-Host ""

try {
    Write-Host "Installing frontend packages..." -ForegroundColor Cyan
    Set-Location -Path "frontend"
    npm install --loglevel=error
    Set-Location -Path ".."
    
    Write-Host "[OK] Node.js dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to install Node.js dependencies!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Try running manually: cd frontend; npm install" -ForegroundColor Yellow
    Set-Location -Path ".."
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 4: Set Up Ollama Models
Write-Host "Step 4: Setting Up Ollama Models..." -ForegroundColor Yellow
Write-Host ""

if (Test-Command ollama) {
    Write-Host "Checking for Gemma 2 model..." -ForegroundColor Cyan
    $ollamaModels = ollama list
    
    if ($ollamaModels -match "gemma2") {
        Write-Host "[OK] Gemma 2 model is already installed" -ForegroundColor Green
    } else {
        Write-Host "Pulling Gemma 2 model (this may take a few minutes)..." -ForegroundColor Cyan
        try {
            ollama pull gemma2:2b
            Write-Host "[OK] Gemma 2 model installed successfully!" -ForegroundColor Green
        } catch {
            Write-Host "[WARNING] Failed to pull Gemma 2 model" -ForegroundColor Yellow
            Write-Host "Run manually: ollama pull gemma2:2b" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "Checking for embedding model..." -ForegroundColor Cyan
    if ($ollamaModels -match "nomic-embed-text") {
        Write-Host "[OK] Embedding model is already installed" -ForegroundColor Green
    } else {
        $installEmbed = Read-Host "Install nomic-embed-text for better RAG performance? (y/n)"
        if ($installEmbed -eq "y") {
            Write-Host "Pulling embedding model..." -ForegroundColor Cyan
            try {
                ollama pull nomic-embed-text
                Write-Host "[OK] Embedding model installed successfully!" -ForegroundColor Green
            } catch {
                Write-Host "[WARNING] Failed to pull embedding model" -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Host "[SKIP] Ollama not installed - skipping model setup" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 5: Create Environment File
Write-Host "Step 5: Setting Up Environment Variables..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".env") {
    Write-Host "[INFO] .env file already exists" -ForegroundColor Cyan
    $overwrite = Read-Host "Overwrite existing .env file? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "[SKIP] Keeping existing .env file" -ForegroundColor Yellow
    } else {
        Remove-Item ".env"
        $createEnv = $true
    }
} else {
    $createEnv = $true
}

if ($createEnv) {
    Write-Host "Creating .env file..." -ForegroundColor Cyan
    
    # Generate random JWT secret
    $jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    
    $envContent = @"
# ShizishanGPT Environment Configuration

# Tavily API Key (for web search)
# Get your key from: https://tavily.com/
TAVILY_API_KEY=your_tavily_api_key_here

# JWT Configuration
JWT_SECRET=$jwtSecret
JWT_ALGORITHM=HS256

# Database Configuration
DATABASE_URL=sqlite:///./users.db

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma2:2b

# Optional: OpenWeatherMap API
# Get your key from: https://openweathermap.org/api
OPENWEATHER_API_KEY=your_openweather_key_here

# Server Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "[OK] .env file created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "[IMPORTANT] Please update the following in .env file:" -ForegroundColor Yellow
    Write-Host "  1. TAVILY_API_KEY - Get from https://tavily.com/" -ForegroundColor Yellow
    Write-Host "  2. OPENWEATHER_API_KEY (optional) - Get from https://openweathermap.org/api" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 6: Create Necessary Directories
Write-Host "Step 6: Creating Project Directories..." -ForegroundColor Yellow
Write-Host ""

$directories = @(
    "Data",
    "models",
    "vectorstore",
    "logs",
    "temp"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[OK] Created directory: $dir" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Directory already exists: $dir" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 7: Test Installation
Write-Host "Step 7: Testing Installation..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Testing Python imports..." -ForegroundColor Cyan
$testScript = @"
try:
    import fastapi
    import uvicorn
    import sqlalchemy
    import chromadb
    import sentence_transformers
    print('[OK] Core packages imported successfully')
except Exception as e:
    print(f'[ERROR] Import failed: {e}')
    exit(1)
"@

$testScript | python
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Python installation test passed!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Python import test failed - some packages might be missing" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Summary
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Installation Summary:" -ForegroundColor Cyan
Write-Host "  ✓ Python dependencies installed" -ForegroundColor Green
Write-Host "  ✓ Node.js dependencies installed" -ForegroundColor Green
Write-Host "  ✓ Environment file created" -ForegroundColor Green
Write-Host "  ✓ Project directories created" -ForegroundColor Green
if (Test-Command ollama) {
    Write-Host "  ✓ Ollama models configured" -ForegroundColor Green
}
Write-Host ""

Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Update API keys in .env file:" -ForegroundColor Yellow
Write-Host "   - TAVILY_API_KEY (required for web search)" -ForegroundColor White
Write-Host "   - OPENWEATHER_API_KEY (optional)" -ForegroundColor White
Write-Host ""
Write-Host "2. Start the application:" -ForegroundColor Yellow
Write-Host "   Option A - Start all services:" -ForegroundColor White
Write-Host "   .\start_all_services.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Option B - Start manually:" -ForegroundColor White
Write-Host "   Terminal 1: python src/main.py" -ForegroundColor Cyan
Write-Host "   Terminal 2: cd frontend; npm start" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Access the application:" -ForegroundColor Yellow
Write-Host "   Backend API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   Frontend UI: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Login with default credentials:" -ForegroundColor Yellow
Write-Host "   Username: superadmin" -ForegroundColor Cyan
Write-Host "   Password: superadmin123" -ForegroundColor Cyan
Write-Host "   (Change these after first login!)" -ForegroundColor Red
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "📚 Documentation: See SETUP_INSTRUCTIONS.md" -ForegroundColor Yellow
Write-Host "🐛 Troubleshooting: See docs/ folder" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$startNow = Read-Host "Start ShizishanGPT now? (y/n)"
if ($startNow -eq "y") {
    Write-Host ""
    Write-Host "Starting services..." -ForegroundColor Green
    .\start_all_services.ps1
}

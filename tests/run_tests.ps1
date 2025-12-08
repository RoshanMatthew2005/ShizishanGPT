# ShizishanGPT Test Execution Guide
# Quick commands to run tests

# ============================================
# STEP 1: VERIFY SERVICES ARE RUNNING
# ============================================

Write-Host "=== Checking Services ===" -ForegroundColor Cyan

# Check MongoDB
$mongoRunning = Get-Process -Name "mongod" -ErrorAction SilentlyContinue
if ($mongoRunning) {
    Write-Host "✓ MongoDB is running" -ForegroundColor Green
} else {
    Write-Host "✗ MongoDB is NOT running - Start with: mongod" -ForegroundColor Red
}

# Check if Python processes are running (FastAPI)
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "✓ Python/FastAPI appears to be running" -ForegroundColor Green
} else {
    Write-Host "✗ FastAPI backend NOT running - Start with: python -m uvicorn main:app --reload --port 8000" -ForegroundColor Red
}

# Check if Node is running (Middleware)
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "✓ Node.js/Middleware appears to be running" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js middleware NOT running - Start with: node server.js" -ForegroundColor Red
}

Write-Host "`n=== Service URLs ===" -ForegroundColor Cyan
Write-Host "React Frontend:    http://localhost:3000"
Write-Host "Node Middleware:   http://localhost:5000"
Write-Host "FastAPI Backend:   http://localhost:8000"
Write-Host "MongoDB:           localhost:27017`n"

# ============================================
# STEP 2: TEST EXECUTION COMMANDS
# ============================================

Write-Host "=== Test Execution Commands ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Run ALL tests:" -ForegroundColor Yellow
Write-Host "  pytest -v`n"

Write-Host "Run specific test file:" -ForegroundColor Yellow
Write-Host "  pytest test_e2e.py -v          # E2E integration tests"
Write-Host "  pytest test_rag.py -v          # RAG retrieval tests"
Write-Host "  pytest test_llm.py -v          # LLM quality tests"
Write-Host "  pytest test_models.py -v       # Model prediction tests"
Write-Host "  pytest test_performance.py -v  # Performance benchmarks"
Write-Host "  pytest test_security.py -v     # Security audit tests"
Write-Host "  pytest test_errors.py -v       # Error handling tests`n"

Write-Host "Run by category (marker):" -ForegroundColor Yellow
Write-Host "  pytest -m e2e -v              # E2E tests only"
Write-Host "  pytest -m rag -v              # RAG tests only"
Write-Host "  pytest -m llm -v              # LLM tests only"
Write-Host "  pytest -m performance -v      # Performance tests only"
Write-Host "  pytest -m security -v         # Security tests only`n"

Write-Host "Skip slow tests:" -ForegroundColor Yellow
Write-Host "  pytest -m 'not slow' -v`n"

Write-Host "Generate HTML report:" -ForegroundColor Yellow
Write-Host "  pytest --html=report.html --self-contained-html`n"

Write-Host "Stop on first failure:" -ForegroundColor Yellow
Write-Host "  pytest -x -v`n"

Write-Host "Run specific test:" -ForegroundColor Yellow
Write-Host "  pytest test_e2e.py::TestE2EPipeline::test_e2e_001_services_health -v`n"

# ============================================
# STEP 3: QUICK TEST EXECUTION
# ============================================

Write-Host "=== Quick Start ===" -ForegroundColor Cyan
$response = Read-Host "Do you want to run all tests now? (y/n)"

if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "`nRunning all tests..." -ForegroundColor Green
    pytest -v
} else {
    Write-Host "`nTests not executed. Use commands above to run manually." -ForegroundColor Yellow
}

Write-Host "`n=== Documentation ===" -ForegroundColor Cyan
Write-Host "Test Suite README:     tests\README.md"
Write-Host "Test Summary:          tests\TEST_SUITE_SUMMARY.md"
Write-Host "Full Testing Plan:     docs\testing\README.md"
Write-Host "Quick Reference:       docs\testing\QUICK_REFERENCE.md"

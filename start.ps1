# MindEase AI — One-Click Startup Script for Windows PowerShell
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "       MindEase AI — A little more room to think" -ForegroundColor Cyan
Write-Host "             Team CodeXpress (Hackathon MVP)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Green

# 1. Check Python
$pythonVer = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not detected in your PATH. Please install Python 3.11+." -ForegroundColor Red
    Exit 1
}
Write-Host "Python detected: $pythonVer" -ForegroundColor Green

# 2. Check Node
$nodeVer = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Node.js is not detected. Please install Node.js (v18+)." -ForegroundColor Red
    Exit 1
}
Write-Host "Node.js detected: $nodeVer" -ForegroundColor Green

# 3. Ensure Virtual Environment
if (-not (Test-Path "backend\venv\Scripts\python.exe")) {
    Write-Host "Creating Python virtual environment in backend\venv..." -ForegroundColor Yellow
    python -m venv backend\venv
}

# 4. Ensure backend/.env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "Creating backend\.env from template..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
}

# 5. Start Backend in a background process / window
Write-Host "Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$env:PYTHONPATH='backend'; backend\venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

# 6. Start Frontend in a background process / window
Write-Host "Starting Vite React Frontend on http://localhost:5173..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "MindEase AI is launching!" -ForegroundColor Green
Write-Host "- Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "- Backend Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "Press any key to exit this starter window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

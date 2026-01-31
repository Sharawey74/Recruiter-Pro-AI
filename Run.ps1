# Run.ps1 - Launcher with Separate Terminal Windows
# Opens Ollama, FastAPI, and Next.js in separate concurrent terminals

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Recruiter-Pro-AI Launcher" -ForegroundColor Cyan
Write-Host "  Opening 3 Separate Terminals" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"
$projectPath = $PWD.Path

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.ReceiveTimeout = 1000
        $tcpClient.SendTimeout = 1000
        $result = $tcpClient.BeginConnect("127.0.0.1", $Port, $null, $null)
        $success = $result.AsyncWaitHandle.WaitOne(1000)
        $tcpClient.Close()
        return $success
    } catch {
        return $false
    }
}

# Function to detect which port Ollama is running on
function Get-OllamaPort {
    $commonPorts = @(11434, 11500, 11435, 11501)
    foreach ($port in $commonPorts) {
        if (Test-Port $port) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$port/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    return $port
                }
            } catch {}
        }
    }
    return $null
}

# 1. Launch Ollama in separate terminal
Write-Host "[1/3] Launching Ollama Server..." -ForegroundColor Green

$ollamaPort = Get-OllamaPort
if ($ollamaPort) {
    Write-Host "  ✓ Ollama already running on port $ollamaPort" -ForegroundColor Yellow
} else {
    $ollamaExists = Get-Command ollama -ErrorAction SilentlyContinue
    if ($ollamaExists) {
        Write-Host "  Opening new terminal for Ollama..." -ForegroundColor Gray
        Start-Process pwsh -ArgumentList "-NoExit", "-Command", "Write-Host 'Ollama Server' -ForegroundColor Cyan; Write-Host '==================' -ForegroundColor Cyan; Write-Host ''; ollama serve"
        Write-Host "  ✓ Ollama terminal opened" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Ollama not found - install from https://ollama.ai" -ForegroundColor Yellow
    }
}
Write-Host ""

# 2. Launch FastAPI in separate terminal
Write-Host "[2/3] Launching FastAPI Server..." -ForegroundColor Green

if (Test-Port 8000) {
    Write-Host "  ⚠ Port 8000 already in use - stopping..." -ForegroundColor Yellow
    Get-Process | Where-Object { $_.ProcessName -match "uvicorn|python" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "  Opening new terminal for FastAPI..." -ForegroundColor Gray
$fastapiCommand = "Set-Location '$projectPath'; Write-Host 'FastAPI Backend' -ForegroundColor Cyan; Write-Host '==================' -ForegroundColor Cyan; Write-Host ''; python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload"
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $fastapiCommand
Write-Host "  ✓ FastAPI terminal opened" -ForegroundColor Green
Write-Host ""

# 3. Launch Next.js in separate terminal
Write-Host "[3/3] Launching Next.js Frontend..." -ForegroundColor Green

if (Test-Port 3000) {
    Write-Host "  ⚠ Port 3000 already in use - stopping..." -ForegroundColor Yellow
    Get-Process | Where-Object { $_.ProcessName -match "node" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "  Opening new terminal for Next.js..." -ForegroundColor Gray
$nextjsCommand = "Set-Location '$projectPath\frontend'; Write-Host 'Next.js Frontend' -ForegroundColor Cyan; Write-Host '==================' -ForegroundColor Cyan; Write-Host ''; npm run dev"
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $nextjsCommand
Write-Host "  ✓ Next.js terminal opened" -ForegroundColor Green
Write-Host ""

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Check status
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  Service Status Check" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

$ollamaPort = Get-OllamaPort
if ($ollamaPort) {
    Write-Host "  ✓ Ollama:     Running on port $ollamaPort" -ForegroundColor Green
} else {
    Write-Host "  ⏳ Ollama:     Starting... (check terminal window)" -ForegroundColor Yellow
}

if (Test-Port 8000) {
    Write-Host "  ✓ FastAPI:    Running on port 8000" -ForegroundColor Green
} else {
    Write-Host "  ⏳ FastAPI:    Starting... (check terminal window)" -ForegroundColor Yellow
}

if (Test-Port 3000) {
    Write-Host "  ✓ Next.js:    Running on port 3000" -ForegroundColor Green
} else {
    Write-Host "  ⏳ Next.js:    Starting... (check terminal window)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  All terminals launched!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor White
if ($ollamaPort) {
    Write-Host "  • Ollama:     http://localhost:$ollamaPort" -ForegroundColor Gray
}
Write-Host "  • FastAPI:    http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "  • Next.js:    http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "Access your app at: " -NoNewline
Write-Host "http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Each service runs in its own terminal window" -ForegroundColor Cyan
Write-Host "   View live logs in each terminal" -ForegroundColor Gray
Write-Host "   Close individual terminals to stop services" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit this launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

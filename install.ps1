# Voice-to-Kiro Installer
# Usage: irm https://raw.githubusercontent.com/islandcodestudios2026418/voice-to-kiro/main/install.ps1 | iex

Write-Host ""
Write-Host "=== Voice-to-Kiro Installer ===" -ForegroundColor Cyan
Write-Host "Hold F2 to talk, auto-paste cleaned text anywhere." -ForegroundColor Gray
Write-Host ""

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python not found. Installing..." -ForegroundColor Yellow
    winget install Python.Python.3.13 --accept-source-agreements --accept-package-agreements
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Host "Please restart PowerShell after Python installs, then run this again." -ForegroundColor Red
        exit 1
    }
}
Write-Host "Python: $($python.Source)" -ForegroundColor Green

# Ask for Groq API key
$key = [System.Environment]::GetEnvironmentVariable("GROQ_API_KEY", "User")
if (-not $key) {
    Write-Host ""
    Write-Host "You need a free Groq API key." -ForegroundColor Yellow
    Write-Host "Get one at: https://console.groq.com (sign up -> API Keys -> Create)" -ForegroundColor Gray
    Write-Host ""
    $key = Read-Host "Paste your Groq API key (gsk_...)"
    if (-not $key.StartsWith("gsk_")) {
        Write-Host "Invalid key. Should start with gsk_" -ForegroundColor Red
        exit 1
    }
    [System.Environment]::SetEnvironmentVariable("GROQ_API_KEY", $key, "User")
    $env:GROQ_API_KEY = $key
    Write-Host "API key saved." -ForegroundColor Green
} else {
    Write-Host "Groq API key already set." -ForegroundColor Green
}

# Create tools directory and download script
$toolsDir = "$env:USERPROFILE\tools"
New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
$scriptUrl = "https://raw.githubusercontent.com/saitama3292-onepunch/voice-to-kiro/main/voice-to-kiro.py"
Invoke-WebRequest -Uri $scriptUrl -OutFile "$toolsDir\voice-to-kiro.py"
Write-Host "Downloaded voice-to-kiro.py" -ForegroundColor Green

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Gray
pip install groq pyaudio pyperclip -q 2>$null
Write-Host "Dependencies installed." -ForegroundColor Green

# Create startup shortcut
$startup = [System.Environment]::GetFolderPath("Startup")
$pythonPath = (Get-Command python).Source
$ws = New-Object -ComObject WScript.Shell
$shortcut = $ws.CreateShortcut("$startup\Voice-to-Kiro.lnk")
$shortcut.TargetPath = $pythonPath
$shortcut.Arguments = "-X utf8 `"$toolsDir\voice-to-kiro.py`""
$shortcut.WorkingDirectory = $toolsDir
$shortcut.WindowStyle = 7
$shortcut.Save()
Write-Host "Auto-start on boot enabled." -ForegroundColor Green

# Start now
Start-Process -FilePath $pythonPath -ArgumentList "-X","utf8","$toolsDir\voice-to-kiro.py" -WindowStyle Hidden
Write-Host ""
Write-Host "=== Done! ===" -ForegroundColor Cyan
Write-Host "Voice-to-Kiro is running. Hold F2 to talk, release to paste." -ForegroundColor White
Write-Host "It will auto-start every time you turn on your computer." -ForegroundColor Gray
Write-Host ""

@echo off
taskkill /F /IM ollama.exe /T 2>nul
timeout /t 2 /nobreak >nul
set OLLAMA_HOST=0.0.0.0:11434
start /B ollama serve
timeout /t 4 /nobreak >nul
netstat -ano | findstr "11434"
echo Done!

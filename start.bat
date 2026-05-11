@echo off
REM ============================================================
REM Luganda AI Studio — Full Startup Script
REM Double-click this file to start everything at once.
REM ============================================================

echo.
echo  ==========================================
echo   Luganda AI Studio — Starting...
echo  ==========================================
echo.

REM Start FastAPI server in its own window
start "Luganda API Server" cmd /k "cd /d D:\projects\Luganda_AI_Studio && call venv\Scripts\activate.bat && uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

REM Wait 4 seconds for the server to boot before starting tunnel
timeout /t 4 /nobreak > nul

REM Start Cloudflare Tunnel in its own window
start "Cloudflare Tunnel" cmd /k "cloudflared tunnel run luganda-studio"

echo.
echo  Both services are starting in separate windows.
echo.
echo  Local (this PC):  http://127.0.0.1:8000/app/index.html
echo  Phone / public:   https://lugandastudio.com/app/index.html
echo.
echo  Close this window — the two service windows keep running.
echo.
pause

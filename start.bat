@echo off
REM ============================================================
REM Luganda AI Studio — Pilot Startup Script
REM Double-click this file to start everything at once.
REM ============================================================
REM
REM CRITICAL: The pilot app (Speak/STT, Proverbs, Grammar, Phrases,
REM Word Library) lives in THIS worktree on branch
REM   codex/luganda-balanced-pilot
REM   C:\tmp\Luganda_AI_Studio-balanced-pilot
REM
REM Do NOT run the server from D:\projects\Luganda_AI_Studio — that is
REM the OLD 'master' checkout. It has no library/events routes, so the
REM Explore cards go empty ("— entries") and features vanish. The
REM backend also serves the frontend from ITS OWN folder, so running the
REM wrong copy swaps out both backend AND frontend. (Root cause of the
REM 2026-07-22 "everything disappeared" incident.)
REM
REM HF_HOME must point at the model cache or STT 503s.
REM ============================================================

echo.
echo  ==========================================
echo   Luganda AI Studio (PILOT) — Starting...
echo  ==========================================
echo.

REM Model cache (Gemmar Luganda whisper-small + MMS TTS live here)
set "HF_HOME=D:\AI\HuggingFace"

REM Start FastAPI server IN THIS WORKTREE, using the shared venv.
REM Host 0.0.0.0 so the Cloudflare tunnel / LAN phone can reach it.
start "Luganda API Server (PILOT)" cmd /k "cd /d C:\tmp\Luganda_AI_Studio-balanced-pilot && set HF_HOME=D:\AI\HuggingFace && call D:\projects\Luganda_AI_Studio\venv\Scripts\activate.bat && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 120"

REM Wait for the server to boot before starting the tunnel
timeout /t 5 /nobreak > nul

REM Start Cloudflare Tunnel in its own window
start "Cloudflare Tunnel" cmd /k "cloudflared tunnel run luganda-studio"

echo.
echo  Both services are starting in separate windows.
echo.
echo  Local (this PC):  http://127.0.0.1:8000/app/index.html
echo  Phone / public:   https://pilot.lugandastudio.com/app/index.html
echo.
echo  Close this window — the two service windows keep running.
echo.
pause
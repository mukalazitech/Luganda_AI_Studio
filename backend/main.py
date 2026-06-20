# backend/main.py

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, time, timedelta, timezone

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from backend.api.routes import health, knowledge, translate, teach, feedback, chat, tts, admin, stt

logger = logging.getLogger("luganda.scheduler")

# ─── In-process nightly harvest+ingest scheduler ──────────────
# Runs harvest_text.py then ingest_dataset.py once a day at ~23:00 UTC
# (≈ 2 AM EAT). Lives inside the same process/container/volume as the
# web service, so it shares the live ChromaDB data directly — no
# separate Railway service or volume needed. # CHANGED
HARVEST_RUN_TIME_UTC = time(hour=23, minute=0)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _seconds_until_next_run(now: datetime | None = None) -> float:
    now = now or datetime.now(timezone.utc)
    target = now.replace(
        hour=HARVEST_RUN_TIME_UTC.hour,
        minute=HARVEST_RUN_TIME_UTC.minute,
        second=0,
        microsecond=0,
    )
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def _run_command(*args: str) -> None:
    logger.info("Scheduler: running %s", " ".join(args))
    proc = await asyncio.create_subprocess_exec(
        *args,
        cwd=str(PROJECT_ROOT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    assert proc.stdout is not None
    async for line in proc.stdout:
        logger.info("[harvest] %s", line.decode(errors="replace").rstrip())
    returncode = await proc.wait()
    if returncode != 0:
        logger.error("Scheduler: command failed (exit %s): %s", returncode, " ".join(args))
    else:
        logger.info("Scheduler: command finished OK: %s", " ".join(args))


async def _nightly_harvest_loop() -> None:
    while True:
        wait_seconds = _seconds_until_next_run()
        logger.info(
            "Scheduler: next harvest run in %.0f minutes (~%s UTC)",
            wait_seconds / 60,
            HARVEST_RUN_TIME_UTC,
        )
        await asyncio.sleep(wait_seconds)
        try:
            await _run_command(sys.executable, "scripts/harvest_text.py", "--source", "all")
            await _run_command(sys.executable, "scripts/ingest_dataset.py")
        except Exception:
            logger.exception("Scheduler: nightly harvest run raised an exception")
        # Sleep briefly so we don't immediately re-trigger if the run
        # finishes within the same minute as the scheduled time.
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_nightly_harvest_loop())
    logger.info("Scheduler: nightly harvest task started")
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        logger.info("Scheduler: nightly harvest task stopped")


app = FastAPI(
    title="Luganda AI Studio",
    description="AI-powered Luganda translation, learning, and chat assistant",
    version="0.3.0",
    lifespan=lifespan,  # CHANGED
)

# ─── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── API Routes ───────────────────────────────────────────────
app.include_router(health.router,     prefix="/api/v1/health",     tags=["Health"])
app.include_router(knowledge.router,  prefix="/api/v1/knowledge",  tags=["Knowledge"])
app.include_router(translate.router,  prefix="/api/v1/translate",  tags=["Translate"])
app.include_router(teach.router,      prefix="/api/v1/teach",      tags=["Teach"])
app.include_router(feedback.router,   prefix="/api/v1/feedback",   tags=["Feedback"])
app.include_router(chat.router,       prefix="/api/v1/chat",       tags=["Chat"])
app.include_router(tts.router,        prefix="/api/v1/tts",        tags=["TTS"])
app.include_router(stt.router,        prefix="/api/v1/stt",        tags=["STT"])
app.include_router(admin.router,      prefix="/api/v1/admin",      tags=["Admin"])

# ─── Frontend Static Files ────────────────────────────────────
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/app", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

# ─── Root Redirect ────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "Luganda AI Studio API is running. Visit /app/index.html for the UI."}
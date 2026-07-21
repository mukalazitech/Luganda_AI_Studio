# backend/api/routes/events.py
"""Anonymous pilot events. Whitelisted event names, identifier-only targets,
append-only JSONL. The schema blocks extra fields and obvious free-text targets;
frontend call sites must pass only curated IDs/slugs, never learner input."""
import json
from datetime import datetime, timezone
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field
from backend.core.config import EVENTS_DIR

router = APIRouter()
EVENTS_FILE = EVENTS_DIR / "events.jsonl"

EventName = Literal[
    "onboarding_started", "onboarding_completed",
    "home_destination_opened", "collection_opened", "item_opened",
    "lesson_started", "lesson_completed",
    "tool_opened",                       # target: translate | listen | chat | search
    "correction_started", "correction_submitted",
    "theme_changed",                     # target: light | dark
]


class PilotEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session: str = Field(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    event: EventName
    target: str = Field(default="", max_length=64, pattern=r"^[A-Za-z0-9_.:-]*$")


@router.post("")
@router.post("/", include_in_schema=False)
def record_event(e: PilotEvent):
    record = {"session": e.session, "event": e.event, "target": e.target,
              "ts": datetime.now(timezone.utc).isoformat()}
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return {"status": "recorded"}

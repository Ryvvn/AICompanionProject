import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Literal
from pydantic import BaseModel, Field

from bananalyzer.constants import LOGS_DIR

Severity = Literal["debug", "info", "warning", "error", "critical"]


class Event(BaseModel):
    timestamp: str = Field(description="ISO 8601 timestamp of the event")
    event_type: str = Field(description="Type of event (e.g., state.changed, state.detected)")
    component: str = Field(description="Component that emitted the event")
    severity: Severity = Field(description="Severity level of the event")
    message: str = Field(description="Human-readable message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional event details")


def emit_event(
    event_type: str,
    component: str,
    severity: Severity,
    message: str,
    details: Dict[str, Any] | None = None
) -> None:
    if details is None:
        details = {}

    event = Event(
        timestamp=datetime.now().isoformat(),
        event_type=event_type,
        component=component,
        severity=severity,
        message=message,
        details=details
    )

    events_file = LOGS_DIR / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)

    with open(events_file, "a", encoding="utf-8") as f:
        f.write(event.model_dump_json() + "\n")

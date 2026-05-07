import json
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, field_validator

from bananalyzer.constants import STATE_DIR, AppState
from bananalyzer.events import emit_event


State = Literal["coding", "gaming", "doomscrolling", "companion", "fallback"]


class CurrentState(BaseModel):
    state: State
    last_updated: str | None = None

    @field_validator("state")
    def validate_state(cls, v):
        valid_states = AppState.all_states()
        if v not in valid_states:
            raise ValueError(f"Invalid state: {v}. Must be one of: {valid_states}")
        return v


def get_current_state() -> CurrentState:
    state_file = STATE_DIR / "current_state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)

    if not state_file.exists():
        return CurrentState(state=AppState.FALLBACK, last_updated=None)        

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return CurrentState(**data)
    except Exception:
        return CurrentState(state=AppState.FALLBACK, last_updated=None)


def set_state(new_state: State) -> None:
    current_state = get_current_state()

    if current_state.state == new_state:
        emit_event(
            event_type="state.detected",
            component="state_machine",
            severity="info",
            message=f"State remains {new_state}",
            details={"state": new_state}
        )
        return

    from datetime import datetime
    last_updated = datetime.now().isoformat()
    state_data = CurrentState(state=new_state, last_updated=last_updated)

    state_file = STATE_DIR / "current_state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state_data.model_dump(), f, indent=2)

    emit_event(
        event_type="state.changed",
        component="state_machine",
        severity="info",
        message=f"State changed from {current_state.state} to {new_state}",
        details={"old_state": current_state.state, "new_state": new_state}
    )

import json
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, field_validator, model_validator

from bananalyzer.constants import STATE_DIR, AppState
from bananalyzer.events import emit_event


State = Literal["coding", "gaming", "doomscrolling", "companion", "fallback"]


class CurrentState(BaseModel):
    previous_state: State | None = None
    state: State
    reason: str | None = None
    confidence: float | None = None
    timestamp: str | None = None
    last_updated: str | None = None

    @field_validator("state")
    def validate_state(cls, v):
        valid_states = AppState.all_states()
        if v not in valid_states:
            raise ValueError(f"Invalid state: {v}. Must be one of: {valid_states}")
        return v

    @model_validator(mode="before")
    @classmethod
    def _migrate_legacy_fields(cls, data):
        if not isinstance(data, dict):
            return data
        if data.get("timestamp") is None and data.get("last_updated") is not None:
            data["timestamp"] = data.get("last_updated")
        return data


def get_current_state() -> CurrentState:
    state_file = STATE_DIR / "current_state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)

    if not state_file.exists():
        return CurrentState(state=AppState.FALLBACK, timestamp=None)

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return CurrentState(**data)
    except Exception:
        return CurrentState(state=AppState.FALLBACK, timestamp=None)


def set_state(new_state: str, *, reason: str | None = None, confidence: float | None = None) -> None:
    current_state = get_current_state()

    if new_state not in AppState.all_states():
        emit_event(
            event_type="state.invalid",
            component="state_machine",
            severity="warning",
            message=f"Rejected invalid state: {new_state}",
            details={
                "requested_state": new_state,
                "current_state": current_state.state,
                "reason": reason,
                "confidence": confidence,
            },
        )
        return

    from datetime import datetime
    timestamp = datetime.now().isoformat()

    if current_state.state == new_state:
        state_data = CurrentState(
            previous_state=current_state.previous_state,
            state=new_state,
            reason=reason or current_state.reason,
            confidence=confidence if confidence is not None else current_state.confidence,
            timestamp=timestamp,
        )

        state_file = STATE_DIR / "current_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state_data.model_dump(), f, indent=2)

        emit_event(
            event_type="state.detected",
            component="state_machine",
            severity="info",
            message=f"State remains {new_state}",
            details={
                "state": new_state,
                "reason": reason,
                "confidence": confidence,
                "timestamp": timestamp,
            },
        )
        return

    state_data = CurrentState(
        previous_state=current_state.state,
        state=new_state,
        reason=reason,
        confidence=confidence,
        timestamp=timestamp,
    )

    state_file = STATE_DIR / "current_state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state_data.model_dump(), f, indent=2)

    emit_event(
        event_type="state.changed",
        component="state_machine",
        severity="info",
        message=f"State changed from {current_state.state} to {new_state}",
        details={
            "previous_state": current_state.state,
            "state": new_state,
            "reason": reason,
            "confidence": confidence,
            "timestamp": timestamp,
        },
    )


def evaluate_activity_signal(activity_category: str) -> tuple[State, str, float] | None:
    if activity_category in ("coding", "gaming", "doomscrolling", "companion", "fallback"):
        return (activity_category, f"activity_category:{activity_category}", 0.7)
    return None


def evaluate_and_set_state_from_foreground() -> CurrentState:
    from bananalyzer.foreground import detect_foreground_activity
    from bananalyzer.config import load_thresholds_safe

    thresholds = load_thresholds_safe()

    try:
        candidate = detect_foreground_activity()
    except Exception:
        set_state(AppState.FALLBACK, reason="foreground_exception", confidence=0.0)
        return get_current_state()

    if candidate.window.error:
        set_state(AppState.FALLBACK, reason=f"foreground_error:{candidate.window.error}", confidence=0.0)
        return get_current_state()

    evaluation = evaluate_activity_signal(candidate.category)
    if evaluation is not None:
        new_state, reason, confidence = evaluation
        set_state(new_state, reason=reason, confidence=confidence)
        return get_current_state()

    current_state = get_current_state()
    elapsed = thresholds.idle_seconds_for_companion
    if current_state.timestamp:
        from datetime import datetime
        try:
            last_active = datetime.fromisoformat(current_state.timestamp)
            elapsed = (datetime.now() - last_active).total_seconds()
        except ValueError:
            pass

    if elapsed >= thresholds.idle_seconds_for_companion:
        set_state(AppState.COMPANION, reason="foreground_unknown", confidence=thresholds.fallback_confidence_threshold)

    return get_current_state()

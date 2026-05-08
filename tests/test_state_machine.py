import json
from pathlib import Path
from unittest.mock import patch

import pytest

import bananalyzer.constants as constants
from bananalyzer.state_machine import set_state


@pytest.fixture
def temp_state_and_logs_dirs(tmp_path: Path):
    data_dir = tmp_path / "data"
    state_dir = data_dir / "state"
    logs_dir = data_dir / "logs"

    with patch.multiple(constants, STATE_DIR=state_dir, LOGS_DIR=logs_dir):
        with patch.multiple("bananalyzer.state_machine", STATE_DIR=state_dir):
            with patch.multiple("bananalyzer.events", LOGS_DIR=logs_dir):
                yield state_dir, logs_dir


def _read_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _read_events(logs_dir: Path):
    events_file = logs_dir / "events.jsonl"
    with open(events_file, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def test_set_state_persists_transition_and_emits_event(temp_state_and_logs_dirs):
    state_dir, logs_dir = temp_state_and_logs_dirs

    set_state("coding", reason="foreground:coding", confidence=0.9)

    state_data = _read_json(state_dir / "current_state.json")
    assert state_data["previous_state"] == "fallback"
    assert state_data["state"] == "coding"
    assert state_data["reason"] == "foreground:coding"
    assert state_data["confidence"] == 0.9
    assert state_data["timestamp"]

    events = _read_events(logs_dir)
    assert events[-1]["event_type"] == "state.changed"
    assert events[-1]["details"]["previous_state"] == "fallback"
    assert events[-1]["details"]["state"] == "coding"


def test_set_state_emits_detected_event_when_no_change(temp_state_and_logs_dirs):
    state_dir, logs_dir = temp_state_and_logs_dirs
    state_dir.mkdir(parents=True, exist_ok=True)

    with open(state_dir / "current_state.json", "w", encoding="utf-8") as f:
        json.dump({"state": "coding"}, f)

    set_state("coding", reason="foreground:coding", confidence=0.5)

    events = _read_events(logs_dir)
    assert events[-1]["event_type"] == "state.detected"
    assert events[-1]["details"]["state"] == "coding"


def test_set_state_rejects_invalid_state_and_keeps_safe_state(temp_state_and_logs_dirs):
    state_dir, logs_dir = temp_state_and_logs_dirs
    state_dir.mkdir(parents=True, exist_ok=True)

    with open(state_dir / "current_state.json", "w", encoding="utf-8") as f:
        json.dump({"state": "fallback"}, f)

    set_state("not-a-state", reason="bad-signal", confidence=0.1)

    state_data = _read_json(state_dir / "current_state.json")
    assert state_data["state"] == "fallback"

    events = _read_events(logs_dir)
    assert events[-1]["event_type"] == "state.invalid"

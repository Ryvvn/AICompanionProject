from pathlib import Path
from unittest.mock import patch

import pytest

import bananalyzer.constants as constants
from bananalyzer.foreground import ForegroundActivityCandidate, ForegroundWindowInfo
from bananalyzer.state_machine import evaluate_and_set_state_from_foreground, get_current_state


@pytest.fixture
def temp_state_and_logs_dirs(tmp_path: Path):
    data_dir = tmp_path / "data"
    state_dir = data_dir / "state"
    logs_dir = data_dir / "logs"

    with patch.multiple(constants, STATE_DIR=state_dir, LOGS_DIR=logs_dir):
        with patch.multiple("bananalyzer.state_machine", STATE_DIR=state_dir):
            with patch.multiple("bananalyzer.events", LOGS_DIR=logs_dir):
                yield state_dir, logs_dir


def test_unknown_activity_transitions_to_companion(temp_state_and_logs_dirs, mocker):
    mocker.patch(
        "bananalyzer.foreground.detect_foreground_activity",
        return_value=ForegroundActivityCandidate(
            category="unknown",
            window=ForegroundWindowInfo(
                hwnd=1,
                pid=2,
                title="Some App",
                class_name="SomeClass",
                process_name="Some.exe",
                process_exe=r"C:\Some.exe",
                error=None,
            ),
        ),
    )

    evaluate_and_set_state_from_foreground()
    current = get_current_state()
    assert current.state == "companion"
    assert current.reason == "foreground_unknown"

def test_unknown_activity_waits_for_idle_threshold(temp_state_and_logs_dirs, mocker):
    from bananalyzer.state_machine import set_state
    from datetime import datetime, timedelta
    
    # Initialize state to coding
    set_state("coding")
    current = get_current_state()
    # Hack timestamp to be just a few seconds ago (below 60s threshold)
    current.timestamp = (datetime.now() - timedelta(seconds=10)).isoformat()
    import json
    with open(temp_state_and_logs_dirs[0] / "current_state.json", "w") as f:
        json.dump(current.model_dump(), f)
        
    mocker.patch(
        "bananalyzer.foreground.detect_foreground_activity",
        return_value=ForegroundActivityCandidate(
            category="unknown",
            window=ForegroundWindowInfo(
                hwnd=1, pid=2, title="Some App", class_name="SomeClass",
                process_name="Some.exe", process_exe=r"C:\Some.exe", error=None,
            ),
        ),
    )
    
    # Run evaluation
    evaluate_and_set_state_from_foreground()
    
    # Should still be coding because 10s < 60s
    assert get_current_state().state == "coding"


def test_foreground_exception_enters_fallback(temp_state_and_logs_dirs, mocker):
    mocker.patch("bananalyzer.foreground.detect_foreground_activity", side_effect=RuntimeError("boom"))

    evaluate_and_set_state_from_foreground()
    current = get_current_state()
    assert current.state == "fallback"
    assert current.reason == "foreground_exception"


def test_foreground_error_enters_fallback(temp_state_and_logs_dirs, mocker):
    mocker.patch(
        "bananalyzer.foreground.detect_foreground_activity",
        return_value=ForegroundActivityCandidate(
            category="unknown",
            window=ForegroundWindowInfo(
                hwnd=None,
                pid=None,
                title=None,
                class_name=None,
                process_name=None,
                process_exe=None,
                error="pywin32_unavailable",
            ),
        ),
    )

    evaluate_and_set_state_from_foreground()
    current = get_current_state()
    assert current.state == "fallback"
    assert current.reason == "foreground_error:pywin32_unavailable"

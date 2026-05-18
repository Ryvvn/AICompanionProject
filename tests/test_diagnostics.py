import json
from pathlib import Path
from unittest.mock import patch

import pytest

import bananalyzer.constants as constants
from bananalyzer.diagnostics import (
    upsert_integration_health,
    get_integration_health,
    run_diagnostics,
)
from bananalyzer.integrations.base import HealthCheckResult


@pytest.fixture
def temp_state_and_logs_dirs(tmp_path: Path):
    data_dir = tmp_path / "data"
    state_dir = data_dir / "state"
    logs_dir = data_dir / "logs"

    with patch.multiple(constants, STATE_DIR=state_dir, LOGS_DIR=logs_dir):
        with patch.multiple("bananalyzer.diagnostics", STATE_DIR=state_dir):
            with patch.multiple("bananalyzer.events", LOGS_DIR=logs_dir):
                yield state_dir, logs_dir


def _read_events(logs_dir: Path):
    events_file = logs_dir / "events.jsonl"
    if not events_file.exists():
        return []
    with open(events_file, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def test_upsert_integration_health_writes_file(temp_state_and_logs_dirs):
    state_dir, logs_dir = temp_state_and_logs_dirs

    result = HealthCheckResult(
        available=False,
        status="unavailable",
        last_check="2026-05-10T12:00:00",
        last_error="Connection refused",
        degraded_mode=True,
    )
    upsert_integration_health("screenpipe", result)

    health = get_integration_health()
    assert "screenpipe" in health.integrations
    entry = health.integrations["screenpipe"]
    assert entry.available is False
    assert entry.status == "unavailable"
    assert entry.last_error == "Connection refused"
    assert entry.degraded_mode is True


def test_upsert_integration_health_updates_existing_entry(temp_state_and_logs_dirs):
    state_dir, logs_dir = temp_state_and_logs_dirs

    result1 = HealthCheckResult(
        available=False,
        status="unavailable",
        last_check="2026-05-10T12:00:00",
        last_error="Connection refused",
        degraded_mode=True,
    )
    upsert_integration_health("screenpipe", result1)

    result2 = HealthCheckResult(
        available=True,
        status="available",
        last_check="2026-05-10T12:01:00",
        degraded_mode=False,
    )
    upsert_integration_health("screenpipe", result2)

    health = get_integration_health()
    entry = health.integrations["screenpipe"]
    assert entry.available is True
    assert entry.status == "available"
    assert entry.last_error == "Connection refused"
    assert entry.degraded_mode is False


def test_diagnostics_emits_recovery_event(temp_state_and_logs_dirs):
    state_dir, logs_dir = temp_state_and_logs_dirs

    result = HealthCheckResult(
        available=False,
        status="unavailable",
        last_check="2026-05-10T12:00:00",
        last_error="down",
        degraded_mode=True,
    )
    upsert_integration_health("screenpipe", result)

    with patch(
        "bananalyzer.diagnostics.ScreenpipeAdapter.health_check",
        return_value=HealthCheckResult(
            available=True,
            status="available",
            last_check="2026-05-10T12:01:00",
            degraded_mode=False,
        ),
    ):
        with patch(
            "bananalyzer.diagnostics.OllamaAdapter.health_check",
            return_value=HealthCheckResult(
                available=False,
                status="unavailable",
                last_check="2026-05-10T12:01:00",
                last_error="not implemented",
                degraded_mode=True,
            ),
        ):
            with patch(
                "bananalyzer.diagnostics.MCPAdapter.health_check",
                return_value=HealthCheckResult(
                    available=False,
                    status="unavailable",
                    last_check="2026-05-10T12:01:00",
                    last_error="not implemented",
                    degraded_mode=True,
                ),
            ):
                with patch(
                    "bananalyzer.diagnostics.STTAdapter.health_check",
                    return_value=HealthCheckResult(
                        available=False,
                        status="unavailable",
                        last_check="2026-05-10T12:01:00",
                        last_error="not implemented",
                        degraded_mode=True,
                    ),
                ):
                    with patch(
                        "bananalyzer.diagnostics.TTSAdapter.health_check",
                        return_value=HealthCheckResult(
                            available=False,
                            status="unavailable",
                            last_check="2026-05-10T12:01:00",
                            last_error="not implemented",
                            degraded_mode=True,
                        ),
                    ):
                        report = run_diagnostics()

    assert report.integrations["screenpipe"].available is True

    events = _read_events(logs_dir)
    recovery_events = [e for e in events if e["event_type"] == "integration.recovered"]
    assert len(recovery_events) >= 1
    assert any(e["component"] == "screenpipe" for e in recovery_events)


def test_diagnostics_emits_failure_event_for_unavailable(temp_state_and_logs_dirs):
    state_dir, logs_dir = temp_state_and_logs_dirs

    with patch(
        "bananalyzer.diagnostics.ScreenpipeAdapter.health_check",
        return_value=HealthCheckResult(
            available=False,
            status="unavailable",
            last_check="2026-05-10T12:00:00",
            last_error="Connection refused",
            degraded_mode=True,
        ),
    ):
        with patch(
            "bananalyzer.diagnostics.OllamaAdapter.health_check",
            return_value=HealthCheckResult(
                available=False,
                status="unavailable",
                last_check="2026-05-10T12:00:00",
                last_error="not implemented",
                degraded_mode=True,
            ),
        ):
            with patch(
                "bananalyzer.diagnostics.MCPAdapter.health_check",
                return_value=HealthCheckResult(
                    available=False,
                    status="unavailable",
                    last_check="2026-05-10T12:00:00",
                    last_error="not implemented",
                    degraded_mode=True,
                ),
            ):
                with patch(
                    "bananalyzer.diagnostics.STTAdapter.health_check",
                    return_value=HealthCheckResult(
                        available=False,
                        status="unavailable",
                        last_check="2026-05-10T12:00:00",
                        last_error="not implemented",
                        degraded_mode=True,
                    ),
                ):
                    with patch(
                        "bananalyzer.diagnostics.TTSAdapter.health_check",
                        return_value=HealthCheckResult(
                            available=False,
                            status="unavailable",
                            last_check="2026-05-10T12:00:00",
                            last_error="not implemented",
                            degraded_mode=True,
                        ),
                    ):
                        report = run_diagnostics()

    assert report.integrations["screenpipe"].available is False

    events = _read_events(logs_dir)
    failure_events = [e for e in events if e["event_type"] == "integration.failed"]
    assert any(e["component"] == "screenpipe" for e in failure_events)

from datetime import datetime
from types import SimpleNamespace

import pytest

from bananalyzer.integrations.base import HealthCheckResult
from bananalyzer.mode_controller import process_user_message
from bananalyzer.config import Settings

@pytest.fixture(autouse=True)
def mock_screenpipe_enabled(mocker):
    mocker.patch(
        "bananalyzer.mode_controller.load_settings_safe",
        return_value=Settings(screenpipe_enabled=True)
    )


def test_process_user_message_doomscrolling_screenpipe_unavailable_degraded(mocker):
    mocker.patch(
        "bananalyzer.mode_controller.get_current_state",
        return_value=SimpleNamespace(state="doomscrolling"),
    )
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch(
        "bananalyzer.mode_controller.ScreenpipeAdapter.health_check",
        return_value=HealthCheckResult(
            available=False,
            status="unavailable",
            last_check=datetime.now().isoformat(),
            last_error="Connection refused",
            degraded_mode=True,
        ),
    )
    gen = mocker.patch("bananalyzer.mode_controller.generate_response", return_value="OK")

    response = process_user_message("am I doomscrolling?")

    assert response.startswith("[Degraded: Screenpipe unavailable")
    gen.assert_called_once()
    _, kwargs = gen.call_args
    assert kwargs["state_override"] == "doomscrolling"


def test_process_user_message_doomscrolling_screenpipe_available(mocker):
    mocker.patch(
        "bananalyzer.mode_controller.get_current_state",
        return_value=SimpleNamespace(state="doomscrolling"),
    )
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch(
        "bananalyzer.mode_controller.ScreenpipeAdapter.health_check",
        return_value=HealthCheckResult(
            available=True,
            status="available",
            last_check=datetime.now().isoformat(),
            degraded_mode=False,
        ),
    )
    mocker.patch(
        "bananalyzer.mode_controller.ScreenpipeAdapter.get_recent_context",
        return_value={
            "ok": True,
            "signals": {"app_name": "chrome.exe", "browser_url": "twitter.com"},
            "error": None,
        },
    )
    gen = mocker.patch("bananalyzer.mode_controller.generate_response", return_value="OK")

    response = process_user_message("am I doomscrolling?")

    assert "[Degraded" not in response
    gen.assert_called_once()
    _, kwargs = gen.call_args
    assert "screenpipe_signals" in kwargs["prompt_variables"]


def test_process_user_message_doomscrolling_screenpipe_health_raises_exception(mocker):
    mocker.patch(
        "bananalyzer.mode_controller.get_current_state",
        return_value=SimpleNamespace(state="doomscrolling"),
    )
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch(
        "bananalyzer.mode_controller.ScreenpipeAdapter.health_check",
        side_effect=RuntimeError("unexpected crash"),
    )
    gen = mocker.patch("bananalyzer.mode_controller.generate_response", return_value="OK")

    response = process_user_message("am I doomscrolling?")

    assert response.startswith("[Degraded: Screenpipe unavailable")
    gen.assert_called_once()


def test_process_user_message_doomscrolling_screenpipe_context_fails(mocker):
    mocker.patch(
        "bananalyzer.mode_controller.get_current_state",
        return_value=SimpleNamespace(state="doomscrolling"),
    )
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch(
        "bananalyzer.mode_controller.ScreenpipeAdapter.health_check",
        return_value=HealthCheckResult(
            available=True,
            status="available",
            last_check=datetime.now().isoformat(),
            degraded_mode=False,
        ),
    )
    mocker.patch(
        "bananalyzer.mode_controller.ScreenpipeAdapter.get_recent_context",
        return_value={
            "ok": False,
            "signals": None,
            "error": {"message": "context not available"},
        },
    )
    gen = mocker.patch("bananalyzer.mode_controller.generate_response", return_value="OK")

    response = process_user_message("am I doomscrolling?")

    assert "[Degraded" not in response
    gen.assert_called_once()
    _, kwargs = gen.call_args
    assert "screenpipe_signals" not in kwargs["prompt_variables"]

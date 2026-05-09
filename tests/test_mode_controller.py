from datetime import datetime
from types import SimpleNamespace

from bananalyzer.integrations.base import HealthCheckResult
from bananalyzer.mode_controller import process_user_message


def test_process_user_message_coding_degrades_without_context(mocker):
    mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=SimpleNamespace(state="coding"))
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch(
        "bananalyzer.mode_controller.MCPAdapter.health_check",
        return_value=HealthCheckResult(
            available=False,
            status="unavailable",
            last_check=datetime.now().isoformat(),
            last_error="down",
            degraded_mode=True,
        ),
    )
    gen = mocker.patch("bananalyzer.mode_controller.generate_response", return_value="OK")

    response = process_user_message("why isn't this working?")

    assert response.startswith("Active code context unavailable.")
    gen.assert_called_once()
    _, kwargs = gen.call_args
    assert kwargs["state_override"] == "coding"
    assert kwargs["prompt_variables"]["code_context_block"] == ""
    assert kwargs["prompt_variables"]["code_context_notice"]


def test_process_user_message_coding_includes_bounded_context(mocker):
    mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=SimpleNamespace(state="coding"))
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch(
        "bananalyzer.mode_controller.MCPAdapter.health_check",
        return_value=HealthCheckResult(
            available=True,
            status="available",
            last_check=datetime.now().isoformat(),
            last_error=None,
            degraded_mode=False,
        ),
    )
    mocker.patch(
        "bananalyzer.mode_controller.MCPAdapter.get_active_context",
        return_value={"ok": True, "data": {"file": "x.py", "selection": "print('hi')"}, "error": None},
    )
    gen = mocker.patch("bananalyzer.mode_controller.generate_response", return_value="OK")

    response = process_user_message("explain this")

    assert response == "OK"
    _, kwargs = gen.call_args
    assert "print('hi')" in kwargs["prompt_variables"]["code_context_block"]

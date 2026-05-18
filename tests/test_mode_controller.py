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


def test_process_user_message_tts_failure_does_not_block_text_output(mocker):
    mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=SimpleNamespace(state="companion"))
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch("bananalyzer.mode_controller.get_memory_prompt_block", return_value="")
    mocker.patch("bananalyzer.mode_controller.generate_response", return_value="Response text")

    mock_settings = mocker.patch("bananalyzer.mode_controller.load_settings_safe")
    mock_settings.return_value = mocker.Mock(tts_enabled=True, screenpipe_enabled=False)

    mock_tts = mocker.patch("bananalyzer.mode_controller.TTSAdapter")
    mock_instance = mock_tts.return_value
    mock_instance.is_available.return_value = True
    mock_instance.speak_async.side_effect = Exception("Unexpected TTS thread crash")

    response = process_user_message("Hello")

    assert response == "Response text"


def test_process_user_message_tts_disabled_text_output_delivered(mocker):
    mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=SimpleNamespace(state="companion"))
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch("bananalyzer.mode_controller.get_memory_prompt_block", return_value="")
    mocker.patch("bananalyzer.mode_controller.generate_response", return_value="Response text")

    mock_settings = mocker.patch("bananalyzer.mode_controller.load_settings_safe")
    mock_settings.return_value = mocker.Mock(tts_enabled=False, screenpipe_enabled=False)

    mock_tts = mocker.patch("bananalyzer.mode_controller.TTSAdapter")

    response = process_user_message("Hello")

    assert response == "Response text"
    mock_tts.return_value.speak_async.assert_not_called()


def test_process_user_message_crash_protection(mocker):
    mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=SimpleNamespace(state="companion"))
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch("bananalyzer.mode_controller.get_memory_prompt_block", return_value="")
    mocker.patch("bananalyzer.mode_controller.load_settings_safe", return_value=mocker.Mock(tts_enabled=False, screenpipe_enabled=False))
    mocker.patch("bananalyzer.mode_controller.generate_response", side_effect=RuntimeError("Unexpected crash"))

    response = process_user_message("Hello")

    assert "System error" in response
    assert "generation failed unexpectedly" in response

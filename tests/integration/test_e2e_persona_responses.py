from datetime import datetime
from types import SimpleNamespace

from bananalyzer.integrations.base import AdapterResult, HealthCheckResult


def test_e2e_coding_state_prompt_used(mocker):
    mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=SimpleNamespace(state="coding"))
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch("bananalyzer.mode_controller.get_memory_prompt_block", return_value="")
    mock_settings = mocker.patch("bananalyzer.mode_controller.load_settings_safe")
    mock_settings.return_value = mocker.Mock(tts_enabled=False, screenpipe_enabled=False)
    mock_mcp_cls = mocker.patch("bananalyzer.mode_controller.MCPAdapter")
    mock_mcp = mock_mcp_cls.return_value
    mock_mcp.health_check.return_value = HealthCheckResult(
        available=True, status="available", last_check=datetime.now().isoformat(), degraded_mode=False
    )
    mock_mcp.get_active_context.return_value = {"ok": True, "data": {"file": "x.py", "selection": "code"}, "error": None}
    mock_mcp.component_name = "mcp"

    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=True, data="Coding response")

    from bananalyzer.mode_controller import process_user_message
    response = process_user_message("Why is this null?")

    assert response == "Coding response"
    call_kwargs = mock_ollama.generate.call_args[1]
    assert call_kwargs["prompt"] == "Why is this null?"
    assert "Rubber Duck" in call_kwargs["system"]


def test_e2e_companion_state_prompt_used(mocker):
    mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=SimpleNamespace(state="companion"))
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch("bananalyzer.mode_controller.get_memory_prompt_block", return_value="")
    mock_settings = mocker.patch("bananalyzer.mode_controller.load_settings_safe")
    mock_settings.return_value = mocker.Mock(tts_enabled=False, screenpipe_enabled=False)

    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=True, data="Hey hey!")

    from bananalyzer.mode_controller import process_user_message
    response = process_user_message("Hello friend!")

    assert response == "Hey hey!"
    call_kwargs = mock_ollama.generate.call_args[1]
    assert "DUO MODE" in call_kwargs["system"]


def test_e2e_doomscrolling_state_prompt_used(mocker):
    mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=SimpleNamespace(state="doomscrolling"))
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch("bananalyzer.mode_controller.get_memory_prompt_block", return_value="")
    mock_settings = mocker.patch("bananalyzer.mode_controller.load_settings_safe")
    mock_settings.return_value = mocker.Mock(tts_enabled=False, screenpipe_enabled=False)

    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=True, data="Stop scrolling!")

    from bananalyzer.mode_controller import process_user_message
    response = process_user_message("...")

    assert "doomscroll" in response.lower() or "Stop scrolling!" in response
    call_kwargs = mock_ollama.generate.call_args[1]
    assert "DOOMSCROLL" in call_kwargs["system"]


def test_e2e_gaming_state_prompt_used(mocker):
    mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=SimpleNamespace(state="gaming"))
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch("bananalyzer.mode_controller.get_memory_prompt_block", return_value="Memory context here")
    mock_settings = mocker.patch("bananalyzer.mode_controller.load_settings_safe")
    mock_settings.return_value = mocker.Mock(tts_enabled=False, screenpipe_enabled=False)

    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=True, data="Stop gaming!")

    from bananalyzer.mode_controller import process_user_message
    response = process_user_message("One more game...")

    assert "Stop gaming!" in response
    call_kwargs = mock_ollama.generate.call_args[1]
    assert "GAMING MODE" in call_kwargs["system"]


def test_e2e_fallback_state_prompt_used(mocker):
    mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=SimpleNamespace(state="fallback"))
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch("bananalyzer.mode_controller.get_memory_prompt_block", return_value="")
    mock_settings = mocker.patch("bananalyzer.mode_controller.load_settings_safe")
    mock_settings.return_value = mocker.Mock(tts_enabled=False, screenpipe_enabled=False)

    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=True, data="Safe response")

    from bananalyzer.mode_controller import process_user_message
    response = process_user_message("What's going on?")

    assert response == "Safe response"
    call_kwargs = mock_ollama.generate.call_args[1]
    assert "fallback mode" in call_kwargs["system"]


def test_e2e_state_transition_changes_prompt(mocker):
    mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
    mocker.patch("bananalyzer.mode_controller.get_memory_prompt_block", return_value="")
    mock_settings = mocker.patch("bananalyzer.mode_controller.load_settings_safe")
    mock_settings.return_value = mocker.Mock(tts_enabled=False, screenpipe_enabled=False)

    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=True, data="Response")

    from bananalyzer.mode_controller import process_user_message

    mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=SimpleNamespace(state="coding"))
    process_user_message("test")
    first_prompt = mock_ollama.generate.call_args[1]["system"]
    assert "CODING MODE" in first_prompt

    mock_ollama.generate.reset_mock()
    mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=SimpleNamespace(state="companion"))
    process_user_message("test2")
    second_prompt = mock_ollama.generate.call_args[1]["system"]
    assert "DUO MODE" in second_prompt


def test_safety_boundary_in_prompts():
    from bananalyzer.persona import _SAFETY_BOUNDARY, get_rendered_prompt_for_state

    boundary = _SAFETY_BOUNDARY
    assert boundary
    assert "SAFETY BOUNDARY" in boundary
    assert "abusive" in boundary.lower()

    for state in ["coding", "companion", "doomscrolling", "gaming", "fallback"]:
        prompt = get_rendered_prompt_for_state(state)
        assert boundary in prompt
        assert len(prompt) > len(boundary)


def test_prompt_files_exist_and_non_empty():
    from pathlib import Path
    from bananalyzer.constants import PROMPTS_DIR

    for state_file in ["coding.md", "companion.md", "doomscroll.md", "gaming.md", "fallback.md"]:
        path = PROMPTS_DIR / state_file
        assert path.exists(), f"Missing prompt file: {state_file}"
        content = path.read_text(encoding="utf-8")
        assert len(content.strip()) > 20, f"Prompt file too short: {state_file}"
        assert "SAFETY BOUNDARY" not in content, f"Safety boundary should be appended by persona.py, not hardcoded in {state_file}"

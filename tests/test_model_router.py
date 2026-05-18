from bananalyzer.config import ModelProfile
from bananalyzer.model_router import build_system_prompt, select_model_profile, generate_response, _sanitize_response
from bananalyzer.integrations.base import AdapterResult


class _FakeProfiles:
    def __init__(self, default_model: str, profiles: dict):
        self.default_model = default_model
        self.profiles = profiles


def test_select_model_profile_uses_state_profile(mocker):
    mocker.patch("bananalyzer.model_router.emit_event")
    profiles = _FakeProfiles(
        default_model="default",
        profiles={
            "coding": ModelProfile(model="code-model", temperature=0.1, context_limit=123),
            "fallback": ModelProfile(model="fallback-model", temperature=0.3, context_limit=10),
        },
    )

    selected = select_model_profile("coding", profiles)
    assert selected.model == "code-model"
    assert selected.resolved_from_state == "coding"
    assert selected.degraded is False


def test_select_model_profile_falls_back_when_missing(mocker):
    emit = mocker.patch("bananalyzer.model_router.emit_event")
    profiles = _FakeProfiles(
        default_model="default",
        profiles={"fallback": {"model": "fallback-model", "temperature": 0.3, "context_limit": 10}},
    )

    selected = select_model_profile("gaming", profiles)
    assert selected.model == "fallback-model"
    assert selected.resolved_from_state == "fallback"
    assert selected.degraded is True
    emit.assert_called()


def test_build_system_prompt_passes_variables_to_persona(mocker):
    get_prompt = mocker.patch("bananalyzer.model_router.get_rendered_prompt_for_state", return_value="PROMPT")
    prompt = build_system_prompt("coding", variables={"code_context_block": "X"})
    assert prompt == "PROMPT"
    get_prompt.assert_called_once_with("coding", variables={"code_context_block": "X"})


def test_generate_response_empty_input(mocker):
    mocker.patch("bananalyzer.model_router.emit_event")
    result = generate_response("")
    assert "I'm here!" in result


def test_generate_response_whitespace_only_input(mocker):
    mocker.patch("bananalyzer.model_router.emit_event")
    result = generate_response("   \t  \n  ")
    assert "I'm here!" in result


def test_generate_response_success(mocker):
    emit = mocker.patch("bananalyzer.model_router.emit_event")
    mocker.patch("bananalyzer.model_router.get_current_state", return_value=mocker.Mock(state="coding"))
    mocker.patch("bananalyzer.model_router.get_rendered_prompt_for_state", return_value="You are a coder.")
    mocker.patch("bananalyzer.model_router.load_model_profiles_safe", return_value=_FakeProfiles(
        default_model="default",
        profiles={"coding": ModelProfile(model="code-model", temperature=0.2, context_limit=4096)},
    ))
    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=True, data="Here is your code solution.")

    result = generate_response("How do I write a loop?")

    assert result == "Here is your code solution."
    mock_ollama.generate.assert_called_once()
    call_kwargs = mock_ollama.generate.call_args[1]
    assert call_kwargs["prompt"] == "How do I write a loop?"
    assert call_kwargs["system"] == "You are a coder."
    assert call_kwargs["model"] == "code-model"
    assert call_kwargs["options"] == {"temperature": 0.2, "num_ctx": 4096}
    generated_calls = [c for c in emit.call_args_list if c[1].get("event_type") == "model.response.generated"]
    assert len(generated_calls) == 1


def test_generate_response_ollama_unavailable(mocker):
    emit = mocker.patch("bananalyzer.model_router.emit_event")
    mocker.patch("bananalyzer.model_router.get_current_state", return_value=mocker.Mock(state="coding"))
    mocker.patch("bananalyzer.model_router.get_rendered_prompt_for_state", return_value="prompt")
    mocker.patch("bananalyzer.model_router.load_model_profiles_safe", return_value=_FakeProfiles(
        default_model="default",
        profiles={"coding": ModelProfile(model="code-model")},
    ))
    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = False

    result = generate_response("test")

    assert "unavailable" in result.lower()
    mock_ollama.generate.assert_not_called()


def test_generate_response_error_unreachable(mocker):
    emit = mocker.patch("bananalyzer.model_router.emit_event")
    mocker.patch("bananalyzer.model_router.get_current_state", return_value=mocker.Mock(state="coding"))
    mocker.patch("bananalyzer.model_router.get_rendered_prompt_for_state", return_value="prompt")
    mocker.patch("bananalyzer.model_router.load_model_profiles_safe", return_value=_FakeProfiles(
        default_model="default",
        profiles={"coding": ModelProfile(model="code-model")},
    ))
    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=False, error={"code": "ollama_unreachable", "message": "Ollama not running"})

    result = generate_response("test")

    assert "ollama serve" in result.lower()
    assert "unreachable" not in result.lower()


def test_generate_response_error_timeout(mocker):
    emit = mocker.patch("bananalyzer.model_router.emit_event")
    mocker.patch("bananalyzer.model_router.get_current_state", return_value=mocker.Mock(state="coding"))
    mocker.patch("bananalyzer.model_router.get_rendered_prompt_for_state", return_value="prompt")
    mocker.patch("bananalyzer.model_router.load_model_profiles_safe", return_value=_FakeProfiles(
        default_model="default",
        profiles={"coding": ModelProfile(model="code-model")},
    ))
    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=False, error={"code": "ollama_timeout"})

    result = generate_response("test")

    assert "too long" in result.lower()


def test_generate_response_error_unknown_code(mocker):
    mocker.patch("bananalyzer.model_router.emit_event")
    mocker.patch("bananalyzer.model_router.get_current_state", return_value=mocker.Mock(state="coding"))
    mocker.patch("bananalyzer.model_router.get_rendered_prompt_for_state", return_value="prompt")
    mocker.patch("bananalyzer.model_router.load_model_profiles_safe", return_value=_FakeProfiles(
        default_model="default",
        profiles={"coding": ModelProfile(model="code-model")},
    ))
    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=False, error={"code": "something_weird"})

    result = generate_response("test")

    assert "bananalyzer diagnose" in result.lower()


def test_generate_response_options_no_context_limit(mocker):
    emit = mocker.patch("bananalyzer.model_router.emit_event")
    mocker.patch("bananalyzer.model_router.get_current_state", return_value=mocker.Mock(state="coding"))
    mocker.patch("bananalyzer.model_router.get_rendered_prompt_for_state", return_value="prompt")
    mocker.patch("bananalyzer.model_router.load_model_profiles_safe", return_value=_FakeProfiles(
        default_model="default",
        profiles={"coding": ModelProfile(model="code-model", temperature=0.7, context_limit=None)},
    ))
    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=True, data="Done.")

    generate_response("test")
    call_kwargs = mock_ollama.generate.call_args[1]
    assert call_kwargs["options"] == {"temperature": 0.7}


def test_sanitize_whitespace():
    result = _sanitize_response("  \n  Hello world!  \n\n ", "")
    assert result == "Hello world!"


def test_sanitize_assistant_prefix():
    result = _sanitize_response("Assistant: Here is the answer.", "")
    assert result == "Here is the answer."


def test_sanitize_eos_token():
    result = _sanitize_response("Generated response</s>", "")
    assert result == "Generated response"


def test_sanitize_system_prompt_repetition():
    system_prompt = "You are a helpful coding assistant named Bananalyzer."
    result = _sanitize_response(
        "You are a helpful coding assistant named Bananalyzer. Here is the actual code: print('hello')",
        system_prompt,
    )
    assert result == "Here is the actual code: print('hello')"


def test_sanitize_empty_after_cleanup():
    result = _sanitize_response("   ", "")
    assert result == ""


def test_sanitize_all_artifacts_combined():
    result = _sanitize_response(
        "Assistant: You are a coding assistant. The answer is 42.</s>   \n",
        "You are a coding assistant.",
    )
    assert result == "The answer is 42."


def test_generate_response_empty_after_sanitization(mocker):
    emit = mocker.patch("bananalyzer.model_router.emit_event")
    mocker.patch("bananalyzer.model_router.get_current_state", return_value=mocker.Mock(state="coding"))
    mocker.patch("bananalyzer.model_router.get_rendered_prompt_for_state", return_value="Short prompt")
    mocker.patch("bananalyzer.model_router.load_model_profiles_safe", return_value=_FakeProfiles(
        default_model="default",
        profiles={"coding": ModelProfile(model="code-model")},
    ))
    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=True, data="   ")

    result = generate_response("test")

    assert "couldn't generate" in result.lower()
    empty_calls = [c for c in emit.call_args_list if c[1].get("event_type") == "model.response.empty"]
    assert len(empty_calls) == 1


def test_generate_response_generation_failed(mocker):
    emit = mocker.patch("bananalyzer.model_router.emit_event")
    mocker.patch("bananalyzer.model_router.get_current_state", return_value=mocker.Mock(state="coding"))
    mocker.patch("bananalyzer.model_router.get_rendered_prompt_for_state", return_value="prompt")
    mocker.patch("bananalyzer.model_router.load_model_profiles_safe", return_value=_FakeProfiles(
        default_model="default",
        profiles={"coding": ModelProfile(model="code-model")},
    ))
    mock_ollama_cls = mocker.patch("bananalyzer.model_router.OllamaAdapter")
    mock_ollama = mock_ollama_cls.return_value
    mock_ollama.is_available.return_value = True
    mock_ollama.generate.return_value = AdapterResult(ok=False, error={"code": "ollama_timeout", "message": "timed out"})

    result = generate_response("test")

    assert "too long" in result.lower()

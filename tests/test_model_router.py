from bananalyzer.config import ModelProfile
from bananalyzer.model_router import build_system_prompt, select_model_profile


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

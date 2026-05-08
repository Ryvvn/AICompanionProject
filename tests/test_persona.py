from pathlib import Path

from bananalyzer.constants import AppState
from bananalyzer.persona import get_prompt_for_state


def test_get_prompt_for_state_loads_existing_prompt(tmp_path: Path, mocker):
    mocker.patch("bananalyzer.persona.emit_event")
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    (prompts_dir / "coding.md").write_text("CODING PROMPT", encoding="utf-8")

    prompt = get_prompt_for_state(AppState.CODING, prompts_dir=prompts_dir)
    assert "CODING PROMPT" in prompt


def test_get_prompt_for_state_falls_back_to_fallback_file(tmp_path: Path, mocker):
    emit = mocker.patch("bananalyzer.persona.emit_event")
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    (prompts_dir / "fallback.md").write_text("FALLBACK PROMPT", encoding="utf-8")

    prompt = get_prompt_for_state(AppState.GAMING, prompts_dir=prompts_dir)
    assert "FALLBACK PROMPT" in prompt
    emit.assert_called()


def test_get_prompt_for_state_uses_builtin_prompt_if_all_missing(tmp_path: Path, mocker):
    emit = mocker.patch("bananalyzer.persona.emit_event")
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    prompt = get_prompt_for_state(AppState.GAMING, prompts_dir=prompts_dir)
    assert "local-first assistant" in prompt
    emit.assert_called()

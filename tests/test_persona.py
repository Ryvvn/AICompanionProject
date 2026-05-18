from pathlib import Path

from bananalyzer.constants import AppState
from bananalyzer.persona import get_prompt_for_state, render_prompt_template, get_rendered_prompt_for_state


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


def test_render_prompt_template_replaces_known_variables():
    rendered = render_prompt_template("Hello {{name}} {{missing}}", {"name": "Ryan"})
    assert rendered == "Hello Ryan "


def test_get_rendered_prompt_includes_safety_boundary(tmp_path: Path, mocker):
    mocker.patch("bananalyzer.persona.emit_event")
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    (prompts_dir / "doomscroll.md").write_text("DOOMSCROLL BASE PROMPT", encoding="utf-8")

    prompt = get_rendered_prompt_for_state(AppState.DOOMSCROLLING, prompts_dir=prompts_dir)
    assert "DOOMSCROLL BASE PROMPT" in prompt
    assert "SAFETY BOUNDARY" in prompt
    assert "abusive" in prompt.lower()


def test_safety_boundary_present_in_all_state_prompts(tmp_path: Path, mocker):
    mocker.patch("bananalyzer.persona.emit_event")
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    for state_file in ["coding.md", "gaming.md", "doomscroll.md", "companion.md", "fallback.md"]:
        (prompts_dir / state_file).write_text(f"PROMPT for {state_file}", encoding="utf-8")

    for state in ["coding", "gaming", "doomscrolling", "companion", "fallback"]:
        prompt = get_rendered_prompt_for_state(state, prompts_dir=prompts_dir)
        assert "SAFETY BOUNDARY" in prompt, f"Missing safety boundary in {state} prompt"

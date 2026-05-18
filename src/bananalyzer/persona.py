from __future__ import annotations

from pathlib import Path
from typing import Mapping
import re

from bananalyzer.constants import PROMPTS_DIR, AppState
from bananalyzer.events import emit_event


_SAFETY_BOUNDARY = (
    "\n\n## SAFETY BOUNDARY (Non-Negotiable)\n"
    "You are Bananalyzer, a motivational accountability companion. You may be sarcastic, "
    "direct, and sharp — but you MUST NOT use abusive, discriminatory, protected-class "
    "insults, or self-harm-reinforcing language. Sarcasm is allowed; cruelty is not. "
    "Your goal is to help Ryan return to productive coding, not to harm them.\n"
)


_STATE_TO_PROMPT_FILE: dict[str, str] = {
    AppState.CODING: "coding.md",
    AppState.GAMING: "gaming.md",
    AppState.DOOMSCROLLING: "doomscroll.md",
    AppState.COMPANION: "companion.md",
    AppState.FALLBACK: "fallback.md",
}


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def get_prompt_for_state(state: str, *, prompts_dir: Path | None = None) -> str:
    resolved_prompts_dir = prompts_dir or PROMPTS_DIR
    resolved_mapping = dict(_STATE_TO_PROMPT_FILE)
    try:
        from bananalyzer.config import load_settings_safe

        settings = load_settings_safe()
        for key, value in (settings.prompt_files or {}).items():
            if key in resolved_mapping and value:
                resolved_mapping[key] = value
    except Exception:
        pass

    filename = resolved_mapping.get(state, resolved_mapping[AppState.FALLBACK])
    target_path = resolved_prompts_dir / filename

    text = _read_text(target_path)
    if text is not None and text.strip():
        return text

    fallback_path = resolved_prompts_dir / resolved_mapping[AppState.FALLBACK]
    fallback_text = _read_text(fallback_path)
    if fallback_text is not None and fallback_text.strip():
        emit_event(
            event_type="prompt.degraded",
            component="persona",
            severity="warning",
            message="Prompt file missing or unreadable; falling back to fallback prompt",
            details={"requested_state": state, "requested_path": str(target_path), "fallback_path": str(fallback_path)},
        )
        return fallback_text

    emit_event(
        event_type="prompt.degraded",
        component="persona",
        severity="warning",
        message="Prompt files missing or unreadable; using built-in safe prompt",
        details={"requested_state": state, "requested_path": str(target_path), "fallback_path": str(fallback_path)},
    )
    return (
        "You are Bananalyzer, a local-first assistant.\n\n"
        "Keep responses safe, concise, and helpful. If context is missing, ask clarifying questions.\n"
    )


_TEMPLATE_PATTERN = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}")


def render_prompt_template(prompt: str, variables: Mapping[str, str] | None = None) -> str:
    resolved_variables = dict(variables or {})

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return str(resolved_variables.get(key, ""))

    return _TEMPLATE_PATTERN.sub(_replace, prompt)


def get_rendered_prompt_for_state(state: str, *, variables: Mapping[str, str] | None = None, prompts_dir: Path | None = None) -> str:
    prompt = render_prompt_template(get_prompt_for_state(state, prompts_dir=prompts_dir), variables)
    return prompt + _SAFETY_BOUNDARY


def get_prompt_paths(*, prompts_dir: Path | None = None) -> Mapping[str, Path]:
    resolved_prompts_dir = prompts_dir or PROMPTS_DIR
    resolved_mapping = dict(_STATE_TO_PROMPT_FILE)
    try:
        from bananalyzer.config import load_settings_safe

        settings = load_settings_safe()
        for key, value in (settings.prompt_files or {}).items():
            if key in resolved_mapping and value:
                resolved_mapping[key] = value
    except Exception:
        pass
    return {state: resolved_prompts_dir / filename for state, filename in resolved_mapping.items()}

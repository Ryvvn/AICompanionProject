from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bananalyzer.config import ModelProfile, load_model_profiles_safe
from bananalyzer.constants import AppState
from bananalyzer.events import emit_event
from bananalyzer.integrations import OllamaAdapter
from bananalyzer.persona import get_rendered_prompt_for_state
from bananalyzer.state_machine import get_current_state


@dataclass(frozen=True)
class SelectedModelProfile:
    state: str
    model: str
    temperature: float
    context_limit: int | None
    resolved_from_state: str
    degraded: bool


def _coerce_profile(default_model: str, profile: Any | None) -> ModelProfile:
    if profile is None:
        return ModelProfile(model=default_model)
    if isinstance(profile, ModelProfile):
        return profile
    if isinstance(profile, dict):
        try:
            return ModelProfile(**profile)
        except Exception:
            return ModelProfile(model=default_model)
    return ModelProfile(model=default_model)


def select_model_profile(state: str, model_profiles: Any) -> SelectedModelProfile:
    default_model = getattr(model_profiles, "default_model", "local-llama3")
    profiles = getattr(model_profiles, "profiles", None) or {}

    chosen = profiles.get(state)
    if chosen is not None:
        resolved = _coerce_profile(default_model, chosen)
        return SelectedModelProfile(
            state=state,
            model=resolved.model,
            temperature=resolved.temperature,
            context_limit=resolved.context_limit,
            resolved_from_state=state,
            degraded=False,
        )

    fallback_state = AppState.FALLBACK
    fallback_profile = profiles.get(fallback_state)
    resolved_fallback = _coerce_profile(default_model, fallback_profile)

    emit_event(
        event_type="model_profile.degraded",
        component="model_router",
        severity="warning",
        message="Missing or invalid model profile for state; falling back",
        details={"requested_state": state, "fallback_state": fallback_state},
    )

    return SelectedModelProfile(
        state=state,
        model=resolved_fallback.model,
        temperature=resolved_fallback.temperature,
        context_limit=resolved_fallback.context_limit,
        resolved_from_state=fallback_state,
        degraded=True,
    )


def build_system_prompt(state: str, *, variables: dict[str, str] | None = None) -> str:
    return get_rendered_prompt_for_state(state, variables=variables)


def generate_response(
    user_input: str,
    *,
    state_override: str | None = None,
    prompt_variables: dict[str, str] | None = None,
) -> str:
    try:
        state = state_override or get_current_state().state
    except Exception:
        state = AppState.FALLBACK

    system_prompt = build_system_prompt(state, variables=prompt_variables)

    profiles = load_model_profiles_safe()
    selected = select_model_profile(state, profiles)

    ollama = OllamaAdapter()
    if not ollama.is_available():
        emit_event(
            event_type="model.unavailable",
            component="model_router",
            severity="warning",
            message="Local model generation unavailable",
            details={"state": state, "model": selected.model, "resolved_from_state": selected.resolved_from_state},
        )
        return (
            "Local generation is unavailable right now. "
            "Run `bananalyzer diagnose` to see integration health and errors."
        )

    return (
        f"(Placeholder response) State='{state}', model='{selected.model}'. "
        f"System prompt loaded ({len(system_prompt)} chars). User said: {user_input!r}"
    )

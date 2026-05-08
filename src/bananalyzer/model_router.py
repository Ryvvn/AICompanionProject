from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bananalyzer.config import ModelProfile, load_model_profiles_safe
from bananalyzer.constants import AppState
from bananalyzer.events import emit_event
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


def generate_response(user_input: str) -> str:
    try:
        state = get_current_state().state
    except Exception:
        state = AppState.FALLBACK

    profiles = load_model_profiles_safe()
    selected = select_model_profile(state, profiles)
    return (
        f"Thanks for your input: '{user_input}'. "
        "I'm Bananalyzer, your AI companion! "
        f"(Placeholder response - routed to profile '{selected.model}' for state '{selected.state}'.)"
    )

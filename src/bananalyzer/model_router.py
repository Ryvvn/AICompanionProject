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


def _sanitize_response(raw: str, system_prompt: str) -> str:
    text = raw.strip()

    if not text:
        return ""

    for prefix in ("Assistant:", "AI:", "Bananalyzer:", "<|assistant|>"):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()

    if text.endswith("</s>"):
        text = text[:-4].strip()

    if system_prompt and len(system_prompt) > 10:
        if text.startswith(system_prompt.strip()):
            text = text[len(system_prompt.strip()):].strip()
        else:
            sys_start = system_prompt[:200].strip()
            resp_start = text[:200].strip()
            if sys_start and resp_start and len(sys_start) > 20 and sys_start in resp_start:
                text = text[len(sys_start):].strip()

    return text.strip()


def generate_response(
    user_input: str,
    *,
    state_override: str | None = None,
    prompt_variables: dict[str, str] | None = None,
) -> str:
    if not user_input or not user_input.strip():
        return "I'm here! What would you like to talk about?"

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

    options: dict[str, Any] = {"temperature": selected.temperature}
    if selected.context_limit is not None:
        options["num_ctx"] = selected.context_limit

    result = ollama.generate(
        prompt=user_input.strip(),
        system=system_prompt,
        model=selected.model,
        options=options,
    )

    if not result.ok:
        error_code = (result.error or {}).get("code", "unknown")
        error_messages = {
            "ollama_unreachable": "I can't reach the local Ollama server. Is it running? Run 'ollama serve' to start it.",
            "ollama_timeout": "The model is taking too long to respond. Try a smaller model or check if Ollama is overloaded.",
            "ollama_http_error": "The model server returned an error. Check 'bananalyzer diagnose' for details.",
            "ollama_invalid_response": "The model returned an unexpected response. This might be a temporary issue.",
        }
        user_message = error_messages.get(error_code, "Generation unavailable. Run 'bananalyzer diagnose' to check integration health.")

        emit_event(
            event_type="model.generation_failed",
            component="model_router",
            severity="warning",
            message=f"Generation failed with code: {error_code}",
            details={"state": state, "model": selected.model, "error_code": error_code, "error": result.error},
        )
        return user_message

    raw_response = result.data or ""
    sanitized = _sanitize_response(raw_response, system_prompt)

    if not sanitized:
        emit_event(
            event_type="model.response.empty",
            component="model_router",
            severity="warning",
            message="Generated response was empty after sanitization",
            details={"state": state, "model": selected.model},
        )
        return "I received your message but couldn't generate a meaningful response. Could you rephrase?"

    emit_event(
        event_type="model.response.generated",
        component="model_router",
        severity="info",
        message="Generated response successfully",
        details={
            "state": state,
            "model": selected.model,
            "response_length": len(sanitized),
            "resolved_from_state": selected.resolved_from_state,
        },
    )

    return sanitized

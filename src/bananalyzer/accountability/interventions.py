from __future__ import annotations

import time as time_module
from typing import Any, Dict, Optional

from bananalyzer.config import load_thresholds_safe
from bananalyzer.events import emit_event
from bananalyzer.memory.retrieval import retrieve_memory_context
from bananalyzer.memory.store import MemoryStore
from bananalyzer.persona import get_rendered_prompt_for_state


class InterventionManager:
    def __init__(self, memory_store: MemoryStore | None = None):
        self._memory_store = memory_store
        self._last_intervention_time: float = 0.0
        self._intervention_count: int = 0

    def _is_cooldown_active(self) -> bool:
        thresholds = load_thresholds_safe()
        cooldown = thresholds.intervention_cooldown_seconds
        if time_module.time() - self._last_intervention_time < cooldown:
            return True
        return False

    def _get_intensity_modifier(self) -> str:
        thresholds = load_thresholds_safe()
        intensity = thresholds.intervention_intensity

        modifiers = {
            "low": "Use gentle, encouraging language. Be supportive rather than confrontational.",
            "medium": "Use direct, accountability-focused language. Be firm but fair.",
            "high": "Use sarcastic, sharp banana-style language. Be aggressive within motivational boundaries.",
        }
        return modifiers.get(intensity, modifiers["medium"])

    def should_intervene(
        self,
        state: str,
        duration_minutes: float,
        banana_debt: Dict[str, Any] | None = None,
    ) -> bool:
        if self._is_cooldown_active():
            return False

        thresholds = load_thresholds_safe()

        if state == "doomscrolling":
            return duration_minutes >= thresholds.doomscrolling_threshold_mins
        if state == "gaming":
            return duration_minutes >= thresholds.gaming_threshold_mins

        return False

    def build_intervention_prompt(
        self,
        state: str,
        duration_minutes: float,
        banana_debt: Dict[str, Any] | None = None,
    ) -> str:
        thresholds = load_thresholds_safe()
        intensity_modifier = self._get_intensity_modifier()

        base_prompt = get_rendered_prompt_for_state(state)

        goals_text = ""
        if self._memory_store:
            try:
                memory_context = retrieve_memory_context(self._memory_store, state, max_chars=800)
                if memory_context:
                    goals_text = f"\n\n## Ryan's Current Goals and Context\n{memory_context}"
            except Exception:
                pass

        if not goals_text.strip():
            goals_text = (
                "\n\n## No specific goals found\n"
                "Ryan hasn't set explicit goals yet. Provide a general accountability nudge "
                "without inventing or assuming goals."
            )

        debt_text = ""
        if banana_debt and banana_debt.get("current_debt", 0) > 0:
            debt_text = (
                f"\n\n## Banana Debt Status\n"
                f"Current banana debt: {banana_debt['current_debt']:.1f}. "
                f"Ryan has been in this state for {duration_minutes:.1f} minutes. "
                f"Every minute here increases the debt."
            )
        else:
            debt_text = (
                f"\n\nRyan has been in this state for {duration_minutes:.1f} minutes."
            )

        intervention_prompt = (
            f"{base_prompt}\n\n"
            f"## INTERVENTION CONTEXT\n"
            f"{intensity_modifier}\n"
            f"{debt_text}\n"
            f"{goals_text}\n\n"
            f"## INSTRUCTION\n"
            f"Generate a brief, motivational intervention to help Ryan refocus on their coding goals. "
            f"Be honest and direct. Do NOT use abusive, discriminatory, protected-class insults, "
            f"or self-harm-reinforcing language. Sarcasm is allowed; cruelty is not."
        )

        return intervention_prompt

    def trigger_intervention(
        self,
        state: str,
        duration_minutes: float,
        banana_debt: Dict[str, Any] | None = None,
    ) -> Optional[str]:
        if not self.should_intervene(state, duration_minutes, banana_debt):
            return None

        self._last_intervention_time = time_module.time()
        self._intervention_count += 1

        prompt = self.build_intervention_prompt(state, duration_minutes, banana_debt)

        emit_event(
            event_type="intervention.triggered",
            component="interventions",
            severity="info",
            message=f"Accountability intervention triggered for state: {state}",
            details={
                "state": state,
                "duration_minutes": duration_minutes,
                "intervention_count": self._intervention_count,
                "intensity": load_thresholds_safe().intervention_intensity,
            },
        )

        return prompt

    def generate_safe_nudge(self, state: str) -> str:
        nudges = {
            "doomscrolling": "Hey Ryan — you've been scrolling for a while. Ready to get back to coding?",
            "gaming": "Gaming break noted. When you're ready, your code is waiting.",
            "companion": "Just checking in — still with you!",
        }
        return nudges.get(state, nudges["companion"])

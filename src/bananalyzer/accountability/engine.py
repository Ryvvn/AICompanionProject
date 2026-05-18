from __future__ import annotations

from bananalyzer.accountability.timers import StateTimeTracker
from bananalyzer.accountability.banana_debt import BananaDebtCalculator
from bananalyzer.accountability.interventions import InterventionManager
from bananalyzer.memory.store import MemoryStore


class AccountabilityEngine:
    def __init__(self, memory_store: MemoryStore | None = None):
        self.tracker = StateTimeTracker()
        self.debt = BananaDebtCalculator()
        self.interventions = InterventionManager(memory_store=memory_store)

    def on_state_changed(self, new_state: str, timestamp: str | None = None) -> None:
        self.tracker.record_state_change(new_state, timestamp)

    def get_time_totals(self) -> dict[str, float]:
        return self.tracker.get_totals()

    def update_debt(self) -> dict:
        totals = self.tracker.get_totals()
        coding_mins = totals.get("coding", 0.0) / 60.0
        gaming_mins = totals.get("gaming", 0.0) / 60.0
        doomscroll_mins = totals.get("doomscrolling", 0.0) / 60.0
        return self.debt.update_debt(coding_mins, gaming_mins, doomscroll_mins)

    def check_intervention(self) -> str | None:
        current_state = self.tracker._current_state
        if not current_state:
            return None

        totals = self.tracker.get_totals()
        duration_seconds = totals.get(current_state, 0.0)
        duration_mins = duration_seconds / 60.0

        debt_data = self.debt.get_current_debt()

        return self.interventions.trigger_intervention(current_state, duration_mins, debt_data)

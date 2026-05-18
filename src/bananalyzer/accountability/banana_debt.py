from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from bananalyzer.constants import MEMORY_DIR
from bananalyzer.config import load_thresholds_safe
from bananalyzer.events import emit_event


class BananaDebtCalculator:
    def __init__(self, memory_dir: Path | None = None):
        self._memory_dir = memory_dir or MEMORY_DIR
        self._debt_file = self._memory_dir / "banana_debt.json"

    def _read_debt(self) -> Dict[str, Any]:
        try:
            if self._debt_file.exists():
                return json.loads(self._debt_file.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def _write_debt(self, data: Dict[str, Any]) -> bool:
        try:
            self._memory_dir.mkdir(parents=True, exist_ok=True)
            self._debt_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return True
        except Exception as e:
            emit_event(
                event_type="memory.unavailable",
                component="banana_debt",
                severity="error",
                message="Failed to write banana_debt.json",
                details={"error": str(e)},
            )
            return False

    def calculate(
        self,
        coding_minutes: float,
        gaming_minutes: float,
        doomscrolling_minutes: float,
    ) -> float:
        thresholds = load_thresholds_safe()
        debt = (
            thresholds.banana_debt_coding_ratio * coding_minutes
            + thresholds.banana_debt_gaming_ratio * gaming_minutes
            + thresholds.banana_debt_doomscroll_ratio * doomscrolling_minutes
        )
        return max(0.0, debt)

    def get_current_debt(self) -> Dict[str, Any]:
        return self._read_debt()

    def update_debt(self, coding_minutes: float, gaming_minutes: float, doomscrolling_minutes: float) -> Dict[str, Any]:
        current = self._read_debt()
        previous_value = float(current.get("current_debt", 0.0))

        thresholds = load_thresholds_safe()
        new_debt = self.calculate(coding_minutes, gaming_minutes, doomscrolling_minutes)

        now = datetime.now().isoformat()
        data: Dict[str, Any] = {
            "current_debt": new_debt,
            "previous_debt": previous_value,
            "last_updated": now,
            "breakdown": {
                "coding_minutes": coding_minutes,
                "gaming_minutes": gaming_minutes,
                "doomscrolling_minutes": doomscrolling_minutes,
            },
            "rates": {
                "coding": thresholds.banana_debt_coding_ratio,
                "gaming": thresholds.banana_debt_gaming_ratio,
                "doomscrolling": thresholds.banana_debt_doomscroll_ratio,
            },
        }

        if abs(new_debt - previous_value) > 0.01:
            if not self._write_debt(data):
                emit_event(
                    event_type="memory.unavailable",
                    component="banana_debt",
                    severity="warning",
                    message="Banana debt data could not be saved; operating in degraded memory mode",
                    details={},
                )

        return data

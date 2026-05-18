from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from bananalyzer.constants import STATE_DIR


class StateTimeTracker:
    def __init__(self, state_dir: Path | None = None):
        self._state_dir = state_dir or STATE_DIR
        self._session_file = self._state_dir / "activity_time.json"
        self._totals: Dict[str, float] = {
            "coding": 0.0,
            "gaming": 0.0,
            "doomscrolling": 0.0,
            "companion": 0.0,
            "fallback": 0.0,
        }
        self._current_state: str | None = None
        self._state_start: datetime | None = None
        self._load()

    def _load(self) -> None:
        try:
            if self._session_file.exists():
                data = json.loads(self._session_file.read_text(encoding="utf-8"))
                for key in self._totals:
                    if key in data and isinstance(data[key], (int, float)):
                        self._totals[key] = float(data[key])
        except Exception:
            pass

    def _save(self) -> None:
        try:
            self._state_dir.mkdir(parents=True, exist_ok=True)
            self._session_file.write_text(json.dumps(self._totals, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_totals(self) -> Dict[str, float]:
        return dict(self._totals)

    def resolve_elapsed(self) -> float:
        if self._current_state and self._state_start:
            return (datetime.now() - self._state_start).total_seconds()
        return 0.0

    def record_state_change(self, new_state: str, timestamp_str: str | None = None) -> None:
        elapsed = self.resolve_elapsed()

        if self._current_state and elapsed > 0:
            if self._current_state in self._totals:
                self._totals[self._current_state] += elapsed

        try:
            ts = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
        except (ValueError, TypeError):
            ts = datetime.now()

        self._current_state = new_state
        self._state_start = ts
        self._save()

    def get_totals_display(self) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for state, seconds in self._totals.items():
            elapsed = seconds
            if state == self._current_state:
                elapsed += self.resolve_elapsed()
            if elapsed < 60:
                result[state] = f"{int(elapsed)}s"
            elif elapsed < 3600:
                result[state] = f"{elapsed / 60:.1f}m"
            else:
                result[state] = f"{elapsed / 3600:.1f}h"
        return result

    def reset(self) -> None:
        for key in self._totals:
            self._totals[key] = 0.0
        self._current_state = None
        self._state_start = None
        self._save()

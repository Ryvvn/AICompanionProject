from pathlib import Path
from unittest.mock import patch

from bananalyzer.accountability.engine import AccountabilityEngine


def test_engine_on_state_changed_records_transition(tmp_path: Path):
    state_dir = tmp_path / "state"
    with patch("bananalyzer.accountability.timers.STATE_DIR", state_dir):
        engine = AccountabilityEngine()
        engine.on_state_changed("coding", "2026-05-10T10:00:00")
        engine.on_state_changed("gaming", "2026-05-10T10:01:00")

        totals = engine.get_time_totals()
        assert totals["coding"] > 0


def test_engine_update_debt_returns_data(tmp_path: Path):
    state_dir = tmp_path / "state"
    with patch("bananalyzer.accountability.timers.STATE_DIR", state_dir):
        engine = AccountabilityEngine()
        engine.on_state_changed("coding", "2026-05-10T10:00:00")
        engine.on_state_changed("doomscrolling", "2026-05-10T10:02:00")

        with patch("bananalyzer.accountability.banana_debt.MEMORY_DIR", tmp_path):
            result = engine.update_debt()
            assert "current_debt" in result


def test_engine_check_intervention_returns_none_when_no_push_state(tmp_path: Path):
    state_dir = tmp_path / "state"
    with patch("bananalyzer.accountability.timers.STATE_DIR", state_dir):
        engine = AccountabilityEngine()
        engine.on_state_changed("coding")
        result = engine.check_intervention()
        assert result is None


def test_engine_check_intervention_returns_prompt_for_doomscroll_over_threshold(tmp_path: Path, mocker):
    state_dir = tmp_path / "state"
    with patch("bananalyzer.accountability.timers.STATE_DIR", state_dir):
        engine = AccountabilityEngine()
        engine.on_state_changed("doomscrolling")

        mocker.patch.object(
            engine.tracker,
            "get_totals",
            return_value={"doomscrolling": 1200.0, "coding": 0.0, "gaming": 0.0, "companion": 0.0, "fallback": 0.0},
        )

        mocker.patch.object(engine.interventions, "_is_cooldown_active", return_value=False)
        mocker.patch(
            "bananalyzer.accountability.interventions.get_rendered_prompt_for_state",
            return_value="prompt",
        )

        result = engine.check_intervention()
        assert result is not None

import time
from pathlib import Path
from unittest.mock import patch

import pytest

from bananalyzer.memory.store import MemoryStore
from bananalyzer.memory.summarizer import (
    generate_session_summary,
    should_skip_update,
    MemoryUpdateResult,
)
from bananalyzer.constants import AppState


class TestShouldSkipUpdate:
    def test_skip_when_no_meaningful_change(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        result = generate_session_summary(store, AppState.CODING)
        last_content = store.read_session_summary()

        assert should_skip_update(store, last_content, AppState.CODING) is True

    def test_do_not_skip_when_no_previous_summary(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        assert should_skip_update(store, "", AppState.CODING) is False

    def test_do_not_skip_when_state_changed(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.update_session_summary("Coding on API")
        last_content = store.read_session_summary()

        assert should_skip_update(store, last_content, AppState.GAMING) is False


class TestGenerateSessionSummary:
    def test_generates_summary_with_state_info(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)
        store.add_goal("Finish sprint")
        store.record_progress("Fixed 3 bugs")

        result = generate_session_summary(store, AppState.CODING)

        assert result.summary != ""
        assert "coding" in result.summary.lower()
        assert "Goals" in result.summary or "goals" in result.summary

    def test_generates_summary_for_companion_state(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        result = generate_session_summary(store, AppState.COMPANION)

        assert result.summary != ""
        assert "companion" in result.summary.lower()

    def test_result_contains_timestamp(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        result = generate_session_summary(store, AppState.CODING)

        assert result.timestamp is not None
        assert result.state == AppState.CODING

    def test_summary_includes_goals_when_present(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)
        store.add_goal("Ship v1.0")

        result = generate_session_summary(store, AppState.CODING)

        assert "Ship v1.0" in result.summary or "Goals" in result.summary

    def test_summary_includes_mistakes_when_present(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)
        store.record_mistake("Null pointer in auth")

        result = generate_session_summary(store, AppState.CODING)

        assert "Null pointer" in result.summary or "Mistakes" in result.summary


class TestPeriodicUpdateIntegration:
    def test_full_update_cycle_updates_summary_file(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        result = generate_session_summary(store, AppState.CODING)

        prev_content = store.read_session_summary()
        assert result.summary in prev_content or prev_content != ""

    def test_update_result_has_expected_fields(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        result = generate_session_summary(store, AppState.CODING)

        assert hasattr(result, "summary")
        assert hasattr(result, "timestamp")
        assert hasattr(result, "state")
        assert hasattr(result, "skipped")
        assert result.skipped is False

    def test_summary_is_concise(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)
        store.add_goal("A" * 50)
        store.record_mistake("B" * 50)
        store.record_progress("C" * 50)

        result = generate_session_summary(store, AppState.CODING)

        assert len(result.summary) < 500

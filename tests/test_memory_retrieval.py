from pathlib import Path

import pytest

from bananalyzer.memory.retrieval import (
    retrieve_memory_context,
    truncate_memory_context,
    get_memory_prompt_block,
)
from bananalyzer.memory.store import MemoryStore
from bananalyzer.constants import AppState


class TestTruncateMemoryContext:
    def test_short_content_passes_through(self):
        text = "Short memory content"
        result = truncate_memory_context(text, max_chars=500)
        assert result == text

    def test_long_content_truncated(self):
        text = "A" * 500
        result = truncate_memory_context(text, max_chars=100)
        assert len(result) <= 150
        assert "A" * 50 in result

    def test_empty_content_returns_empty(self):
        assert truncate_memory_context("") == ""
        assert truncate_memory_context(None) == ""

    def test_truncation_adds_notice(self):
        text = "B" * 200
        result = truncate_memory_context(text, max_chars=50)
        assert "truncated" in result.lower()

    def test_default_max_chars_is_1000(self):
        text = "C" * 500
        result = truncate_memory_context(text)
        assert result == text


class TestRetrieveMemoryContext:
    def test_retrieves_goals_from_memory(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)
        store.add_goal("Finish the MVP")

        context = retrieve_memory_context(store, AppState.CODING)

        assert "Finish the MVP" in context

    def test_retrieves_mistakes_from_memory(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)
        store.record_mistake("Null check missing")

        context = retrieve_memory_context(store, AppState.CODING)

        assert "Null check missing" in context

    def test_retrieves_session_summary(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)
        store.update_session_summary("Discussed architecture")

        context = retrieve_memory_context(store, AppState.CODING)

        assert "architecture" in context

    def test_empty_memory_returns_empty_string(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        context = retrieve_memory_context(store, AppState.CODING)

        assert context == ""

    def test_memory_context_is_bounded(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)
        store.add_goal("G" * 2000)

        context = retrieve_memory_context(store, AppState.CODING, max_chars=200)

        assert len(context) <= 300

    def test_reads_both_memory_and_session_summary(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)
        store.add_goal("Ship v2")
        store.update_session_summary("Fixed 5 bugs today")

        context = retrieve_memory_context(store, AppState.CODING)

        assert "Ship v2" in context
        assert "Fixed 5 bugs" in context


class TestGetMemoryPromptBlock:
    def test_returns_formatted_block_with_content(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)
        store.add_goal("Learn async Python")

        block = get_memory_prompt_block(store, AppState.CODING)

        assert "Memory Context" in block
        assert "Learn async Python" in block

    def test_returns_empty_when_no_memory(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        block = get_memory_prompt_block(store, AppState.CODING)

        assert block == ""

    def test_handles_none_store_gracefully(self):
        block = get_memory_prompt_block(None, AppState.CODING)

        assert block == ""

    def test_handles_unavailable_store_gracefully(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)
        mocker.patch.object(store, "read_memory", side_effect=IOError("Disk error"))

        block = get_memory_prompt_block(store, AppState.CODING)

        assert block == ""

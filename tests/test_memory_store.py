import json
from pathlib import Path

import pytest

from bananalyzer.memory.store import MemoryStore


class TestMemoryStoreInit:
    def test_creates_memory_directory_and_default_files(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        assert memory_dir.is_dir()
        assert (memory_dir / "memory.md").is_file()
        assert (memory_dir / "session_summary.md").is_file()
        assert (memory_dir / "banana_debt.json").is_file()
        assert store.available is True

    def test_initial_file_contents_are_safe_defaults(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        md_content = (memory_dir / "memory.md").read_text(encoding="utf-8")
        summary_content = (memory_dir / "session_summary.md").read_text(encoding="utf-8")
        debt_content = (memory_dir / "banana_debt.json").read_text(encoding="utf-8")

        assert md_content.startswith("#")
        assert summary_content.startswith("#")
        assert json.loads(debt_content) == {}

    def test_no_error_when_files_already_exist(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "memory.md").write_text("# Existing Memory")
        (memory_dir / "session_summary.md").write_text("# Existing Summary")
        (memory_dir / "banana_debt.json").write_text('{"existing": true}')

        store = MemoryStore(memory_dir=memory_dir)

        assert store.read_memory() == "# Existing Memory"
        assert store.read_session_summary() == "# Existing Summary"
        assert store.read_banana_debt() == {"existing": True}
        assert store.available is True

    def test_defaults_to_constants_memory_dir(self, mocker):
        mock_memory_dir = mocker.patch("bananalyzer.memory.store.MEMORY_DIR")
        mock_memory_dir.__truediv__ = lambda self, other: Path(str(self) + "/" + str(other))

        mock_path = mocker.patch("bananalyzer.memory.store.Path")
        mock_path_instance = mocker.MagicMock(spec=Path)
        mock_path.return_value = mock_path_instance

        from bananalyzer.memory.store import MemoryStore as MS
        store = MS()
        assert store._memory_dir is not None


class TestMemoryStoreReadWrite:
    def test_read_write_memory(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.write_memory("# Updated Memory\n\nThings remembered.")
        content = store.read_memory()

        assert content == "# Updated Memory\n\nThings remembered."

    def test_read_write_session_summary(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.write_session_summary("# Session Summary\n\nWe talked about coding today.")
        content = store.read_session_summary()

        assert content == "# Session Summary\n\nWe talked about coding today."

    def test_read_write_banana_debt(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        data = {"debt_minutes": 45, "category": "doomscrolling"}
        store.write_banana_debt(data)
        result = store.read_banana_debt()

        assert result == data

    def test_write_banana_debt_persists_to_disk(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        data = {"debt_minutes": 30}
        store.write_banana_debt(data)

        with open(memory_dir / "banana_debt.json", "r", encoding="utf-8") as f:
            on_disk = json.load(f)
        assert on_disk == data


class TestMemoryStoreRecreation:
    def test_recreates_missing_memory_file(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        (memory_dir / "memory.md").unlink()

        content = store.read_memory()
        assert content.startswith("#")
        assert (memory_dir / "memory.md").is_file()

    def test_recreates_missing_session_summary(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        (memory_dir / "session_summary.md").unlink()

        content = store.read_session_summary()
        assert content.startswith("#")
        assert (memory_dir / "session_summary.md").is_file()

    def test_recreates_missing_banana_debt(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        (memory_dir / "banana_debt.json").unlink()

        result = store.read_banana_debt()
        assert result == {}
        assert (memory_dir / "banana_debt.json").is_file()

    def test_emits_event_when_file_is_recreated(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        mock_emit = mocker.patch("bananalyzer.memory.store.emit_event")

        store = MemoryStore(memory_dir=memory_dir)
        (memory_dir / "memory.md").unlink()

        store.read_memory()
        mock_emit.assert_called()
        call_args = mock_emit.call_args
        assert call_args.kwargs["event_type"] == "memory.missing_recreated"


class TestMemoryStoreDegradedMode:
    def test_degraded_mode_when_write_fails(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        mocker.patch("pathlib.Path.write_text", side_effect=PermissionError("Access denied"))

        store.write_memory("This should fail gracefully")
        assert store.available is False

    def test_degraded_mode_read_returns_safe_defaults(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        mocker.patch("pathlib.Path.write_text", side_effect=PermissionError("Access denied"))

        store.write_memory("Fail")
        result = store.read_memory()

        assert result == ""

    def test_emits_unavailable_event_on_failure(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        mock_emit = mocker.patch("bananalyzer.memory.store.emit_event")

        store = MemoryStore(memory_dir=memory_dir)
        mocker.patch("pathlib.Path.write_text", side_effect=PermissionError("Access denied"))

        store.write_memory("Fail")
        mock_emit.assert_called()
        call_args = mock_emit.call_args
        assert call_args.kwargs["event_type"] == "memory.unavailable"

    def test_recovers_from_degraded_when_write_succeeds_later(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        mock_write = mocker.patch.object(Path, "write_text", side_effect=PermissionError("Access denied"))
        store.write_memory("Fail")
        assert store.available is False

        mocker.stopall()
        store.write_memory("Now it works")

        assert store.available is True
        assert (memory_dir / "memory.md").read_text(encoding="utf-8") == "Now it works"

    def test_degraded_mode_for_banana_debt_write_failure(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        write_text = mocker.patch("pathlib.Path.write_text", side_effect=PermissionError("Access denied"))
        store.write_banana_debt({"debt": 100})

        assert store.available is False
        result = store.read_banana_debt()
        assert result == {}

    def test_degraded_mode_for_session_summary_write_failure(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        mocker.patch("pathlib.Path.write_text", side_effect=PermissionError("Access denied"))
        store.write_session_summary("New summary")

        assert store.available is False
        result = store.read_session_summary()
        assert result == ""

    def test_init_degraded_when_directory_creation_fails(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        mocker.patch("bananalyzer.memory.store.emit_event")
        mocker.patch.object(Path, "mkdir", side_effect=OSError("Cannot create directory"))

        store = MemoryStore(memory_dir=memory_dir)
        assert store.available is False

    def test_does_not_crash_on_read_failure(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        mocker.patch("pathlib.Path.read_text", side_effect=IOError("Read error"))
        result = store.read_memory()

        assert result == ""
        assert store.available is False


class TestMemoryStoreMarkdownSections:
    def test_add_goal_appends_to_goals_section(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.add_goal("Finish Epic 4 by Friday")
        content = store.read_memory()

        assert "## Goals" in content
        assert "- Finish Epic 4 by Friday" in content

    def test_add_multiple_goals_preserves_existing(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.add_goal("Goal 1: Learn Rust")
        store.add_goal("Goal 2: Build a game")
        content = store.read_memory()

        assert "Goal 1: Learn Rust" in content
        assert "Goal 2: Build a game" in content
        assert content.count("## Goals") == 1

    def test_record_mistake_appends_to_mistakes_section(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.record_mistake("Forgot to handle null case in parser")
        content = store.read_memory()

        assert "## Mistakes" in content
        assert "- Forgot to handle null case in parser" in content

    def test_record_progress_appends_to_progress_section(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.record_progress("Completed user auth module")
        content = store.read_memory()

        assert "## Progress" in content
        assert "- Completed user auth module" in content

    def test_all_sections_present_in_memory_file(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.add_goal("Learn Python")
        store.record_mistake("Used mutable default arg")
        store.record_progress("Fixed 3 bugs")

        content = store.read_memory()
        assert "## Goals" in content
        assert "## Mistakes" in content
        assert "## Progress" in content

    def test_memory_file_maintains_readable_structure(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.add_goal("Ship MVP")
        store.record_mistake("Skipped tests on critical path")
        store.record_progress("Wrote 500 lines of Rust")

        content = store.read_memory()
        lines = content.split("\n")
        goals_idx = lines.index("## Goals")
        mistakes_idx = lines.index("## Mistakes")
        progress_idx = lines.index("## Progress")

        assert goals_idx < mistakes_idx < progress_idx

    def test_pre_existing_content_preserved_when_adding_sections(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.write_memory("# My Custom Memory\n\nSome pre-existing notes.\n")
        store.add_goal("Refactor database layer")

        content = store.read_memory()
        assert "My Custom Memory" in content
        assert "pre-existing notes" in content
        assert "Refactor database layer" in content


class TestMemoryStoreSessionSummary:
    def test_update_session_summary_writes_content(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.update_session_summary("Discussed architecture patterns. Ryan working on API layer.")
        content = store.read_session_summary()

        assert "architecture patterns" in content
        assert "API layer" in content

    def test_update_session_summary_can_be_called_multiple_times(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.update_session_summary("First session note.")
        store.update_session_summary("Second session note.\n\nMore details.")

        content = store.read_session_summary()
        assert "First session note" in content
        assert "Second session note" in content


class TestMemoryStoreBananaDebtUpdates:
    def test_update_banana_debt_merges_new_data(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.write_banana_debt({"total_minutes": 30, "category": "doomscrolling"})
        store.update_banana_debt({"total_minutes": 45, "last_session": "2026-05-09"})

        debt = store.read_banana_debt()
        assert debt["total_minutes"] == 45
        assert debt["category"] == "doomscrolling"
        assert debt["last_session"] == "2026-05-09"

    def test_update_banana_debt_handles_empty_initial(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.update_banana_debt({"debt_minutes": 15})

        debt = store.read_banana_debt()
        assert debt["debt_minutes"] == 15

    def test_update_banana_debt_read_modify_write_is_safe(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.write_banana_debt({"key_a": "value_a"})
        store.update_banana_debt({"key_b": "value_b"})

        debt = store.read_banana_debt()
        assert debt["key_a"] == "value_a"
        assert debt["key_b"] == "value_b"


class TestMemoryStorePrivacyIntegration:
    def test_add_goal_blocks_oversized_content(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        mock_emit = mocker.patch("bananalyzer.memory.store.emit_event")
        store = MemoryStore(memory_dir=memory_dir)

        long_text = "x" * 1000
        store.add_goal(long_text)

        content = store.read_memory()
        assert "x" * 1000 not in content

        blocked_call = None
        for call in mock_emit.call_args_list:
            if call.kwargs.get("event_type") == "memory.write_blocked":
                blocked_call = call
                break
        assert blocked_call is not None
        assert "Goals" in str(blocked_call.kwargs.get("details", {}))
        assert "x" * 1000 not in blocked_call.kwargs.get("message", "")
        assert "x" * 1000 not in str(blocked_call.kwargs.get("details", {}))

    def test_record_mistake_allows_normal_mistake(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.record_mistake("Forgot null check in parser")
        content = store.read_memory()

        assert "Forgot null check in parser" in content

    def test_record_mistake_blocks_oversized_content(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        mock_emit = mocker.patch("bananalyzer.memory.store.emit_event")
        store = MemoryStore(memory_dir=memory_dir)

        long_mistake = "bug: " + ("x" * 1000)
        store.record_mistake(long_mistake)

        content = store.read_memory()
        assert "x" * 1000 not in content

    def test_update_session_summary_writes_oversized_without_blocking(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        mock_emit = mocker.patch("bananalyzer.memory.store.emit_event")
        store = MemoryStore(memory_dir=memory_dir)

        long_summary = "raw ocr output: " + ("y" * 1000)
        store.update_session_summary(long_summary)

        content = store.read_session_summary()
        assert "raw ocr output" in content

        blocked_found = any(
            call.kwargs.get("event_type") == "memory.write_blocked"
            for call in mock_emit.call_args_list
        )
        assert not blocked_found

    def test_update_session_summary_allows_normal(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.update_session_summary("Discussed project architecture.")
        content = store.read_session_summary()

        assert "project architecture" in content

    def test_block_reason_never_leaks_raw_content(self, tmp_path: Path, mocker):
        memory_dir = tmp_path / "memory"
        mock_emit = mocker.patch("bananalyzer.memory.store.emit_event")
        store = MemoryStore(memory_dir=memory_dir)

        secret = "SECRET_API_KEY_12345_abcde"
        store.add_goal(secret + ("padding" * 100))

        all_event_data = ""
        for call in mock_emit.call_args_list:
            all_event_data += str(call.kwargs)

        assert "SECRET_API_KEY" not in all_event_data

    def test_unapproved_category_write_to_memory_is_not_blocked_by_store_itself(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        store = MemoryStore(memory_dir=memory_dir)

        store.write_memory("Raw unapproved note written directly.")
        content = store.read_memory()
        assert "Raw unapproved note" in content

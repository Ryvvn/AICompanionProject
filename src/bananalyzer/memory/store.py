import json
from pathlib import Path
from typing import Any

from bananalyzer.constants import MEMORY_DIR
from bananalyzer.events import emit_event
from bananalyzer.privacy import check_before_persistence

_SAFE_MEMORY_CONTENT = "# Memory\n\n"
_SAFE_SESSION_SUMMARY_CONTENT = "# Session Summary\n\n"
_SAFE_BANANA_DEBT_CONTENT: dict[str, Any] = {}


class MemoryStore:
    def __init__(self, memory_dir: Path | None = None):
        self._memory_dir = memory_dir or MEMORY_DIR
        self._available = True

        try:
            self._memory_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            emit_event(
                event_type="memory.unavailable",
                component="memory_store",
                severity="error",
                message="Failed to create memory directory",
                details={"error": str(e), "path": str(self._memory_dir)},
            )
            self._available = False
            return

        self._init_file("memory.md", _SAFE_MEMORY_CONTENT)
        self._init_file("session_summary.md", _SAFE_SESSION_SUMMARY_CONTENT)
        self._init_json_file("banana_debt.json", _SAFE_BANANA_DEBT_CONTENT)

        emit_event(
            event_type="memory.initialized",
            component="memory_store",
            severity="info",
            message="MemoryStore initialized successfully",
            details={"memory_dir": str(self._memory_dir)},
        )

    @property
    def available(self) -> bool:
        return self._available

    def _init_file(self, filename: str, default_content: str) -> None:
        filepath = self._memory_dir / filename
        if not filepath.exists():
            try:
                filepath.write_text(default_content, encoding="utf-8")
            except (OSError, IOError) as e:
                self._available = False
                emit_event(
                    event_type="memory.unavailable",
                    component="memory_store",
                    severity="error",
                    message=f"Failed to create memory file: {filename}",
                    details={"error": str(e), "path": str(filepath)},
                )

    def _init_json_file(self, filename: str, default_content: dict[str, Any]) -> None:
        filepath = self._memory_dir / filename
        if not filepath.exists():
            try:
                filepath.write_text(json.dumps(default_content, indent=2), encoding="utf-8")
            except (OSError, IOError) as e:
                self._available = False
                emit_event(
                    event_type="memory.unavailable",
                    component="memory_store",
                    severity="error",
                    message=f"Failed to create memory file: {filename}",
                    details={"error": str(e), "path": str(filepath)},
                )

    def _safe_read_text(self, filename: str, default: str, use_default_on_missing: bool = True) -> str:
        filepath = self._memory_dir / filename

        if not self._available:
            return default

        if not filepath.exists():
            try:
                recreate_content = default if use_default_on_missing else _SAFE_MEMORY_CONTENT
                filepath.write_text(recreate_content, encoding="utf-8")
                emit_event(
                    event_type="memory.missing_recreated",
                    component="memory_store",
                    severity="warning",
                    message=f"Memory file was missing, recreated: {filename}",
                    details={"path": str(filepath)},
                )
            except (OSError, IOError) as e:
                self._available = False
                emit_event(
                    event_type="memory.unavailable",
                    component="memory_store",
                    severity="error",
                    message=f"Failed to recreate missing memory file: {filename}",
                    details={"error": str(e), "path": str(filepath)},
                )
                return default
        try:
            return filepath.read_text(encoding="utf-8")
        except (OSError, IOError) as e:
            self._available = False
            emit_event(
                event_type="memory.unavailable",
                component="memory_store",
                severity="error",
                message=f"Failed to read memory file: {filename}",
                details={"error": str(e), "path": str(filepath)},
            )
            return default

    def _safe_read_json(self, filename: str, default: dict[str, Any]) -> dict[str, Any]:
        filepath = self._memory_dir / filename

        if not self._available:
            return default

        if not filepath.exists():
            try:
                filepath.write_text(json.dumps(default, indent=2), encoding="utf-8")
                emit_event(
                    event_type="memory.missing_recreated",
                    component="memory_store",
                    severity="warning",
                    message=f"Memory file was missing, recreated: {filename}",
                    details={"path": str(filepath)},
                )
            except (OSError, IOError) as e:
                self._available = False
                emit_event(
                    event_type="memory.unavailable",
                    component="memory_store",
                    severity="error",
                    message=f"Failed to recreate missing memory file: {filename}",
                    details={"error": str(e), "path": str(filepath)},
                )
                return default
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except (OSError, IOError) as e:
            self._available = False
            emit_event(
                event_type="memory.unavailable",
                component="memory_store",
                severity="error",
                message=f"Failed to read memory file: {filename}",
                details={"error": str(e), "path": str(filepath)},
            )
            return default
        except json.JSONDecodeError:
            return default

    def _safe_write_text(self, filename: str, content: str) -> None:
        filepath = self._memory_dir / filename
        try:
            filepath.write_text(content, encoding="utf-8")
            self._available = True
        except (OSError, IOError) as e:
            self._available = False
            emit_event(
                event_type="memory.unavailable",
                component="memory_store",
                severity="error",
                message=f"Failed to write memory file: {filename}",
                details={"error": str(e), "path": str(filepath)},
            )

    def _safe_write_json(self, filename: str, data: dict[str, Any]) -> None:
        filepath = self._memory_dir / filename
        try:
            filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")
            self._available = True
        except (OSError, IOError) as e:
            self._available = False
            emit_event(
                event_type="memory.unavailable",
                component="memory_store",
                severity="error",
                message=f"Failed to write memory file: {filename}",
                details={"error": str(e), "path": str(filepath)},
            )

    def read_memory(self) -> str:
        return self._safe_read_text("memory.md", "", use_default_on_missing=False)

    def write_memory(self, content: str) -> None:
        self._safe_write_text("memory.md", content)

    def read_session_summary(self) -> str:
        return self._safe_read_text("session_summary.md", "", use_default_on_missing=False)

    def write_session_summary(self, content: str) -> None:
        self._safe_write_text("session_summary.md", content)

    def read_banana_debt(self) -> dict[str, Any]:
        return self._safe_read_json("banana_debt.json", {})

    def write_banana_debt(self, data: dict[str, Any]) -> None:
        self._safe_write_json("banana_debt.json", data)

    def _append_to_md_section(self, filename: str, section_header: str, entry: str, category: str | None = None) -> None:
        if category is not None:
            allowed, reason = check_before_persistence(category, entry)
            if not allowed:
                emit_event(
                    event_type="memory.write_blocked",
                    component="memory_store",
                    severity="warning",
                    message=f"Memory write blocked by privacy filter: {reason}",
                    details={"category": category},
                )
                return

        current = self._safe_read_text(filename, "")
        lines = current.rstrip("\n").split("\n") if current.strip() else []

        section_found = False
        section_ended = False
        insert_idx = len(lines)
        new_lines = []

        for i, line in enumerate(lines):
            if line.strip() == section_header:
                section_found = True
                new_lines.append(line)
                continue
            if section_found and not section_ended and line.startswith("## "):
                insert_idx = len(new_lines)
                new_lines.append(line)
                section_ended = True
                continue
            new_lines.append(line)

        bullet = f"- {entry}"

        if section_found and not section_ended:
            new_lines.append(bullet)
        elif section_found and section_ended:
            new_lines.insert(insert_idx, bullet)
        else:
            if new_lines and new_lines[-1] != "":
                new_lines.append("")
            new_lines.append(section_header)
            new_lines.append("")
            new_lines.append(bullet)

        updated = "\n".join(new_lines) + "\n"
        self._safe_write_text(filename, updated)

    def add_goal(self, goal_text: str) -> None:
        self._append_to_md_section("memory.md", "## Goals", goal_text, category="Goals")

    def record_mistake(self, mistake_text: str) -> None:
        self._append_to_md_section("memory.md", "## Mistakes", mistake_text, category="Recurring coding mistakes")

    def record_progress(self, progress_text: str) -> None:
        self._append_to_md_section("memory.md", "## Progress", progress_text, category="Progress")

    def update_session_summary(self, summary_text: str) -> None:
        current = self._safe_read_text("session_summary.md", "")
        timestamped = f"- {summary_text}\n"
        updated = current.rstrip("\n") + "\n" + timestamped if current.strip() else "# Session Summary\n\n" + timestamped
        self._safe_write_text("session_summary.md", updated)

    def update_banana_debt(self, data: dict[str, Any]) -> None:
        current = self._safe_read_json("banana_debt.json", {})
        current.update(data)
        self._safe_write_json("banana_debt.json", current)

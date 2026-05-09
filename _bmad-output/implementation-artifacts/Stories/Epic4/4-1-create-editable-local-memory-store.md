# Story 4.1: Create Editable Local Memory Store

**Status:** ready-for-dev
**Epic:** 4 - Local Memory and Evolving Companion Identity

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to keep memory in editable local files,
So that I can inspect and change what the companion remembers.

**Acceptance Criteria:**
1. **Given** the local data structure exists
   **When** memory storage is initialized
   **Then** `data/memory/memory.md`, `data/memory/session_summary.md`, and `data/memory/banana_debt.json` exist or are created safely on first run.
2. **Given** Bananalyzer reads or writes memory
   **When** memory access occurs
   **Then** memory file operations go through `memory/store.py`
   **And** unrelated modules do not directly mutate memory files.
3. **Given** a memory file is missing
   **When** Bananalyzer starts or memory is accessed
   **Then** the missing file is recreated with safe initial content
   **And** the event is logged.
4. **Given** memory storage is unavailable or unwritable
   **When** Bananalyzer attempts a memory operation
   **Then** the runtime continues in a no-memory degraded mode
   **And** status/diagnostics report the issue.

## 2. Developer Context

### Technical Requirements
- Establish the `MemoryStore` component in `src/bananalyzer/memory/store.py`.
- Support Markdown format for human-editable files (`memory.md`, `session_summary.md`) and JSON format for `banana_debt.json`.
- File creation must ensure parent directories exist.
- Use `bananalyzer.events` to emit memory-related events (e.g., `memory.initialized`, `memory.missing_recreated`, `memory.unavailable`).
- Graceful degradation: If directory creation or file writing fails (e.g. permissions), catch `OSError`/`IOError`, log the failure, and place the memory component into a degraded/unavailable state. Do not crash the app.

### Architecture Compliance
- Follows the Local-First Persistence architectural pattern.
- The `MemoryStore` component acts as the sole accessor for memory files. Other components (like mode controller or accountability module) must invoke methods on `MemoryStore` to read/write memory.
- All file paths should resolve relative to the project root, ideally configured via `Pydantic Settings` in `config.py` (e.g., `data_dir / "memory"`).

### Code Structure Requirements
- `src/bananalyzer/memory/__init__.py`
- `src/bananalyzer/memory/store.py`
- `tests/test_memory_store.py`

### Testing Requirements
- Write unit tests for `store.py` validating the creation of the three default files.
- Validate that if a file is deleted, `MemoryStore` recreates it with safe initial content.
- Validate that when file writes raise `PermissionError` (mocked), the `MemoryStore` handles it gracefully without crashing, logging the degraded state.
- Use `pytest-mock` to mock `pathlib.Path.write_text` and `pathlib.Path.exists`. Remember to patch the class method correctly.

## 3. Previous Story Intelligence
**Learnings from Epic 3 Retro:**
- **Safe Degradation:** Continue using the pattern from Epic 2 and 3 where failures fall back gracefully and update `integration_health.json` (or in this case, memory health status).
- **Testing:** Use `pytest-mock` to simulate I/O success and failure to ensure solid test coverage without requiring physical I/O blocking.
- **Mocking Reminder:** When patching `pathlib.Path.exists`, use `mocker.patch('pathlib.Path.exists')` to avoid issues with instance attributes.

## 4. Latest Tech Information
- `pathlib.Path.mkdir(parents=True, exist_ok=True)` handles directory creation.
- Memory files should be initialized as empty markdown with a title header or empty JSON object `{}`.

## 5. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Create `src/bananalyzer/memory/__init__.py` and `store.py` with `MemoryStore` class
- [x] Task 2: Implement file initialization: `memory.md`, `session_summary.md`, `banana_debt.json`
- [x] Task 3: Implement graceful recreation when files are missing
- [x] Task 4: Implement degraded mode for unwritable storage (catch `OSError`/`IOError`)
- [x] Task 5: Emit memory lifecycle events (`memory.initialized`, `memory.missing_recreated`, `memory.unavailable`)
- [x] Task 6: Write unit tests with `pytest-mock` for creation, recovery, and permission error scenarios

## Dev Agent Record

### Agent Model Used
Claude (via BMAD dev-story workflow)

### Debug Log References
- `python -m pytest tests/test_memory_store.py -v` — 20/20 pass
- `python -m pytest tests/ -v` — 54/54 pass, zero regressions

### Completion Notes List
- Implemented `MemoryStore` class in `src/bananalyzer/memory/store.py` as the sole accessor for all memory file operations
- `__init__` creates `memory.md`, `session_summary.md`, and `banana_debt.json` with safe defaults on first run; emits `memory.initialized`
- `read_memory`, `write_memory`, `read_session_summary`, `write_session_summary` for markdown files
- `read_banana_debt`, `write_banana_debt` for JSON data
- Files missing on read are recreated with safe content; emits `memory.missing_recreated`
- All write operations catch `OSError`/`IOError`, set `available=False` without crashing, emit `memory.unavailable`
- Read operations return safe defaults when `available=False`
- MemoryStore can recover from degraded state when writes succeed again
- `MemoryStore.__init__` gracefully degrades when directory creation fails
- Exported `MemoryStore` via `src/bananalyzer/memory/__init__.py`
- 20 unit tests covering: init, read/write, file recreation, degraded mode, event emission, recovery

### File List
- `src/bananalyzer/memory/__init__.py`
- `src/bananalyzer/memory/store.py`
- `tests/test_memory_store.py`

### Change Log
- **2026-05-09**: Completed MemoryStore implementation with editable local memory files, graceful degradation, event emission, and comprehensive test coverage (20 tests, all pass).

## 6. Story Completion Status
**Status:** review

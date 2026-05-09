# Story 4.1: Create Editable Local Memory Store

## 1. Story Foundation
**Epic:** 4 (Local Memory and Evolving Companion Identity)
**Story:** 4.1 (Create Editable Local Memory Store)
**Status:** ready-for-dev

**User Story:**
As Ryan,
I want Bananalyzer to keep memory in editable local files,
So that I can inspect and change what the companion remembers.

**Acceptance Criteria:**
- **Given** the local data structure exists 
  **When** memory storage is initialized 
  **Then** `data/memory/memory.md`, `data/memory/session_summary.md`, and `data/memory/banana_debt.json` exist or are created safely on first run.
- **Given** Bananalyzer reads or writes memory 
  **When** memory access occurs 
  **Then** memory file operations go through `memory/store.py` 
  **And** unrelated modules do not directly mutate memory files.
- **Given** a memory file is missing 
  **When** Bananalyzer starts or memory is accessed 
  **Then** the missing file is recreated with safe initial content 
  **And** the event is logged.
- **Given** memory storage is unavailable or unwritable 
  **When** Bananalyzer attempts a memory operation 
  **Then** the runtime continues in a no-memory degraded mode 
  **And** status/diagnostics report the issue.

## 2. Developer Context & Guardrails

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

### File Structure Requirements
- **Create/Update:**
  - `src/bananalyzer/memory/__init__.py`
  - `src/bananalyzer/memory/store.py`
  - `tests/test_memory_store.py`

### Testing Requirements
- Write unit tests for `store.py` validating the creation of the three default files.
- Validate that if a file is deleted, `MemoryStore` recreates it with safe initial content.
- Validate that when file writes raise `PermissionError` (mocked), the `MemoryStore` handles it gracefully without crashing, logging the degraded state.
- Use `pytest-mock` to mock `pathlib.Path.write_text` and `pathlib.Path.exists`. Remember to patch the class method correctly.

## 3. Previous Story & Git Intelligence
**Learnings from Epic 3 Retro:**
- **Safe Degradation:** Continue using the pattern from Epic 2 and 3 where failures fall back gracefully and update `integration_health.json` (or in this case, memory health status).
- **Testing:** Use `pytest-mock` to simulate I/O success and failure to ensure solid test coverage without requiring physical I/O blocking.
- **Mocking Reminder:** When patching `pathlib.Path.exists`, use `mocker.patch('pathlib.Path.exists')` to avoid issues with instance attributes.

## 4. Completion Status
**Status:** ready-for-dev
**Note:** Ultimate context engine analysis completed - comprehensive developer guide created.
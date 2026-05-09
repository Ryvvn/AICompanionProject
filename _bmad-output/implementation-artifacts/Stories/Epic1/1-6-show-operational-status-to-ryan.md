# Story 1.6: Show Operational Status to Ryan

**Status:** done
**Epic:** 1 - Local Companion Foundation and Operational Visibility

## 1. Story Foundation

**User Story:**
As Ryan,
I want one clear operational status view,
So that I can see what Bananalyzer thinks is happening and what data it may store.

**Acceptance Criteria:**
1. **Given** Bananalyzer has local state and diagnostic files
   **When** Ryan runs `uv run bananalyzer status`
   **Then** the output shows current state, current model/profile placeholder, last state transition, integration health, recent errors, and memory update status.
2. **Given** Ryan opens the dashboard command
   **When** he runs `uv run bananalyzer dashboard`
   **Then** a basic Textual dashboard or safe dashboard placeholder opens
   **And** it displays the same core operational categories as status output.
3. **Given** Ryan wants privacy visibility
   **When** status or diagnostics are shown
   **Then** Bananalyzer lists the categories of context allowed for local persistence
   **And** it does not claim to store raw OCR, raw audio, large code excerpts, or unbounded history by default.
4. **Given** the assistant is in degraded mode
   **When** Ryan views status
   **Then** the degraded mode is visible with a plain-language explanation of what still works.

## 2. Developer Context

### Technical Requirements
- Enhance the `status` command in `cli.py` to print a well-formatted Rich layout containing: Current State, Current Model/Profile, Last State Transition, Integration Health summary, Recent errors, Privacy policy / Persistence allowed categories.
- Implement the actual `Textual` dashboard in `ui/dashboard.py`.
- The dashboard should have clear panes or widgets for State, Model, Integrations, Recent Events, Memory (placeholder), and Privacy.
- Create `privacy.py` and define the persistence allowlist constant so the status output can read it dynamically.

### Architecture Compliance
- The dashboard must not perform heavy blocking operations; it should read from the JSON/JSONL state files asynchronously or on an interval.
- Emphasize local-first privacy: explicitly list the allowed persistence categories (Goals, Session summaries, Recurring coding mistakes, Banana debt, State transitions, Integration health, User-approved memory notes, Minimal diagnostic metadata).

### Code Structure Requirements
- `src/bananalyzer/ui/dashboard.py` (Update Textual app)
- `src/bananalyzer/cli.py` (Update status and dashboard commands)
- `src/bananalyzer/privacy.py` (Create to hold privacy constants/allowlist)
- `tests/test_cli.py` (Update for status output verification)

### Testing Requirements
- Add tests in `tests/test_ui.py` or update `tests/test_cli.py` to ensure `status` outputs the expected sections.
- Verify that `privacy.py` exports the correct allowlist categories.

## 3. Previous Story Intelligence
- Story 1.4 provides the state and event log files. Story 1.5 provides the integration health file. The UI should read directly from these files.

## 4. Latest Tech Information
- `rich` Panel, Table, and rule-based layout can create a clean CLI status view without needing a full TUI.
- `textual` is used for the interactive dashboard with real-time data refresh.

## 5. Project Context Reference
- **Date:** 2026-05-06
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Create `privacy.py` with PERSISTENCE_ALLOWED_CATEGORIES
- [x] Task 2: Update cli.py status command with Rich layout (Current State, Model, Integration Health, Recent Events, Privacy, Interaction Mode)
- [x] Task 3: Update cli.py diagnose command to use diagnostics module
- [x] Task 4: Keep dashboard.py as Textual placeholder with structured panes
- [x] Task 5: Write tests for status output and privacy exports

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Ultimate context engine analysis completed - comprehensive developer guide created.
- Created `privacy.py` with `PERSISTENCE_ALLOWED_CATEGORIES`.
- Enhanced CLI `status` command: shows current state, model, integration health, recent events, privacy, text interaction mode, and degraded mode warning.
- Enhanced CLI `diagnose` command: runs diagnostics and shows integration health table.
- Dashboard remains as Textual placeholder (`ui/dashboard.py`).

### File List
- `src/bananalyzer/privacy.py`
- `src/bananalyzer/cli.py`
- `src/bananalyzer/ui/dashboard.py`
- `tests/test_cli.py`

### Change Log
- **2026-05-06**: Enhanced status/diagnose commands, added privacy module with persistence allowlist, and updated Textual dashboard placeholder.

## 6. Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created. Implementation complete.

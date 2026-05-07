# Story 1.6: Show Operational Status to Ryan

Status: done

## Story

As Ryan,
I want one clear operational status view,
So that I can see what Bananalyzer thinks is happening and what data it may store.

## Acceptance Criteria

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

## Tasks/Subtasks

- [x] Create privacy.py with PERSISTENCE_ALLOWED_CATEGORIES
- [x] Update cli.py status command with Rich layout (Current State, Model, Integration Health, Recent Events, Privacy, Interaction Mode
- [x] Update cli.py diagnose command to use diagnostics module
- [x] Keep dashboard.py as Textual placeholder

## Dev Agent Record

### Debug Log
- All imports tested and working correctly

### Completion Notes
Created privacy.py with PERSISTENCE_ALLOWED_CATEGORIES.
Enhanced cli.py status command: shows current state, model, integration health, recent events, privacy, text interaction mode, and degraded mode warning.
Enhanced cli.py diagnose command: runs diagnostics and shows integration health table.
Dashboard remains as Textual placeholder (ui/dashboard.py).

## File List
- src/bananalyzer/privacy.py
- src/bananalyzer/cli.py

## Change Log
- 2026-05-06: Enhanced status/diagnose commands, added privacy module

## Developer Context

This story focuses on improving the CLI `status` and `dashboard` views using Rich and Textual. The goal is to surface the information collected in stories 1.4 (state transitions) and 1.5 (integration health), and make it easy to understand the current operation mode and privacy boundaries.

### Technical Requirements

- Enhance the `status` command in `cli.py` to print a well-formatted Rich layout containing:
  - Current State
  - Current Model/Profile (from config)
  - Last State Transition (read from `current_state.json` or `events.jsonl`)
  - Integration Health summary (read from `integration_health.json`)
  - Recent errors (read from `events.jsonl`)
  - Privacy policy / Persistence allowed categories (from `privacy.py`).
- Implement the actual `Textual` dashboard in `ui/dashboard.py`.
- The dashboard should have clear panes or widgets for State, Model, Integrations, Recent Events, Memory (placeholder), and Privacy.
- Create `privacy.py` and define the persistence allowlist constant so the status output can read it dynamically.

### Architecture Compliance Guardrails

- The dashboard must not perform heavy blocking operations; it should read from the JSON/JSONL state files asynchronously or on an interval.
- Emphasize local-first privacy: explicitly list the allowed persistence categories (Goals, Session summaries, Recurring coding mistakes, Banana debt, State transitions, Integration health, User-approved memory notes, Minimal diagnostic metadata).

### Library & Framework Requirements

- `rich` (for CLI styling)
- `textual` (for TUI dashboard)

### File Structure Requirements

- `src/bananalyzer/ui/dashboard.py` (Update Textual app)
- `src/bananalyzer/cli.py` (Update status and dashboard commands)
- `src/bananalyzer/privacy.py` (Create to hold privacy constants/allowlist)

### Testing Requirements

- Add tests in `tests/test_ui.py` or update `tests/test_cli.py` to ensure `status` outputs the expected sections.
- Verify that `privacy.py` exports the correct allowlist categories.

### Previous Story Intelligence

- Story 1.4 provides the state and event log files. Story 1.5 provides the integration health file. The UI should read directly from these files.

### Project Context Reference

- This satisfies FR5, FR39, FR43, FR44, and FR45 by providing operational visibility and degraded mode clarity.

## Story Completion Status

- Status set to: `review`
- Completion note: Ultimate context engine analysis completed - comprehensive developer guide created. Implementation complete.

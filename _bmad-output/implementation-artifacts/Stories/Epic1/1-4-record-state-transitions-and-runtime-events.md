# Story 1.4: Record State Transitions and Runtime Events

**Status:** done
**Epic:** 1 - Local Companion Foundation and Operational Visibility

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to record state and runtime events locally,
So that I can understand what the assistant detected and why it acted.

**Acceptance Criteria:**
1. **Given** Bananalyzer starts
   **When** a runtime event occurs
   **Then** an event is appended to `data/logs/events.jsonl`
   **And** each event includes `timestamp`, `event_type`, `component`, `severity`, `message`, and `details`.
2. **Given** Bananalyzer has a current operating state
   **When** the state is initialized or changed
   **Then** `data/state/current_state.json` is updated with canonical state values only: `coding`, `gaming`, `doomscrolling`, `companion`, or `fallback`.
3. **Given** state changes are recorded
   **When** Ryan inspects the event log
   **Then** state transitions use event names such as `state.changed`
   **And** timestamps are ISO 8601 strings.
4. **Given** a component detects a condition but does not change state
   **When** the detection is useful for diagnostics
   **Then** Bananalyzer may emit `state.detected` without incorrectly changing the current state.

## 2. Developer Context

### Technical Requirements
- Create `events.py` for handling event logging to `events.jsonl`.
- Create `state_machine.py` as the centralized place for state transitions.
- Define Pydantic models for Event payload and State.
- Event schema: `timestamp` (ISO 8601), `event_type` (e.g., `state.changed`, `state.detected`), `component`, `severity` (`debug`, `info`, `warning`, `error`, `critical`), `message`, and `details` (dict).
- State schema: ONLY canonical state values (`coding`, `gaming`, `doomscrolling`, `companion`, `fallback`).
- Implement logic to validate transitions and emit `state.changed` event.
- Update `current_state.json` safely.

### Architecture Compliance
- State transitions must only go through `state_machine.py`. Components must not directly overwrite `current_state.json`.
- Event logs should be append-only JSONL.
- The `timestamp` MUST be an ISO 8601 string.
- All values written to `current_state.json` must be one of the canonical state names.

### Code Structure Requirements
- `src/bananalyzer/events.py`
- `src/bananalyzer/state_machine.py`
- `tests/test_events.py`
- `tests/test_state_machine.py`

### Testing Requirements
- Verify that invalid state values are rejected by the state machine.
- Verify that `events.jsonl` is correctly appended with well-formed JSON lines.
- Use `pytest-mock` to isolate from real filesystem.

## 3. Previous Story Intelligence
- Story 1.2 created `constants.py` and the data structure. Use constants for file paths (`EVENTS_LOG_FILE`, `CURRENT_STATE_FILE`).

## 4. Latest Tech Information
- Pydantic models provide built-in validation for the event schema.
- JSONL is simple append-only — no need for atomic writes, just `open(f, 'a')`.

## 5. Project Context Reference
- **Date:** 2026-05-06
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Create `events.py` with Event model and `emit_event()` function
- [x] Task 2: Create `state_machine.py` with CurrentState model, `get_current_state()` and `set_state()` functions
- [x] Task 3: Implement state validation against canonical values
- [x] Task 4: Implement event emission on state change and detection
- [x] Task 5: Write tests for events and state machine

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Ultimate context engine analysis completed - comprehensive developer guide created.
- Implemented `events.py` defining Event Pydantic model and `emit_event()` function that appends JSONL events.
- Implemented `state_machine.py` defining CurrentState model, `get_current_state()` and `set_state()` functions, with validation of canonical state values and emission of `state.changed`/`state.detected` events.

### File List
- `src/bananalyzer/events.py`
- `src/bananalyzer/state_machine.py`
- `tests/test_events.py`
- `tests/test_state_machine.py`

### Change Log
- **2026-05-06**: Implemented events and state machine modules with Pydantic models, JSONL logging, canonical state validation, and test coverage.

## 6. Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created. Implementation complete.

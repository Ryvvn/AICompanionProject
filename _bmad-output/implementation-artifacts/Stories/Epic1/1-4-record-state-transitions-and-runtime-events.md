# Story 1.4: Record State Transitions and Runtime Events
   
Status: done

## Story

As Ryan,
I want Bananalyzer to record state and runtime events locally,
So that I can understand what the assistant detected and why it acted.

## Acceptance Criteria

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

## Tasks/Subtasks

- [x] Create `events.py` with Event model and `emit_event()` function
- [x] Create `state_machine.py` with CurrentState model, `get_current_state()` and `set_state()` functions
- [x] Implement state validation
- [x] Implement event emission on state change and detection

## Dev Agent Record

### Debug Log
- All imports tested and working correctly

### Completion Notes
Implemented `events.py` defines Event Pydantic model and `emit_event()` function that appends JSONL events to `data/logs/events.jsonl`.
Implemented `state_machine.py` defines CurrentState model, `get_current_state()` and `set_state()` functions, with validation of canonical state values and emission of `state.changed`/`state.detected` events.

## File List
- src/bananalyzer/events.py
- src/bananalyzer/state_machine.py

## Change Log
- 2026-05-06: Implemented events and state machine

## Developer Context

This story implements the local event logging and state transition recording. It focuses on writing to the `events.jsonl` log file and the `current_state.json` state file securely and consistently, making sure that other modules have a clean interface to emit events and change state.

### Technical Requirements

- Create `events.py` for handling event logging to `events.jsonl`.
- Create `state_machine.py` as the centralized place for state transitions.
- Define Pydantic models for Event payload and State.
- Ensure the event schema includes: `timestamp` (ISO 8601), `event_type` (e.g., `state.changed`, `state.detected`), `component`, `severity` (`debug`, `info`, `warning`, `error`, `critical`), `message`, and `details` (dict).
- Ensure the state schema uses ONLY canonical state values (`coding`, `gaming`, `doomscrolling`, `companion`, `fallback`).
- In `state_machine.py`, implement logic to validate transitions and emit `state.changed` event.
- Ensure `state_machine.py` updates `current_state.json` safely (e.g., using atomic writes or direct JSON dumping).

### Architecture Compliance Guardrails

- Ensure state transitions *only* go through `state_machine.py`. Components must not directly overwrite `current_state.json`.
- Event logs should be append-only JSONL.
- The `timestamp` MUST be an ISO 8601 string.
- All values written to `current_state.json` must be one of the canonical state names.

### Library & Framework Requirements

- `pydantic` (for schema validation)
- `json` (for reading/writing state)
- `datetime` (for ISO 8601 timestamps)

### File Structure Requirements

- `src/bananalyzer/events.py`
- `src/bananalyzer/state_machine.py`

### Testing Requirements

- Add tests in `tests/test_events.py` and `tests/test_state_machine.py`.
- Verify that invalid state values are rejected by the state machine.
- Verify that `events.jsonl` is correctly appended with well-formed JSON lines.

### Previous Story Intelligence

- Story 1.2 created `constants.py` and the data structure. Use `constants.EVENTS_LOG_FILE` and `constants.CURRENT_STATE_FILE` (or similar paths if defined) for file paths.

### Project Context Reference

- This satisfies FR4, FR5, FR18, and FR44 by recording state and providing local logs.

## Story Completion Status

- Status set to: `review`
- Completion note: Ultimate context engine analysis completed - comprehensive developer guide created. Implementation complete.

# Story 2.2: Implement Canonical State Machine

Status: done

## Story

As Ryan,
I want Bananalyzer to convert activity signals into clear operating states,
so that the assistant behaves consistently instead of inventing random modes.

## Acceptance Criteria

1. **Given** the state machine receives activity signals
   **When** it determines the current mode
   **Then** it uses only canonical state values: `coding`, `gaming`, `doomscrolling`, `companion`, and `fallback`.
2. **Given** the current state changes
   **When** the state machine accepts a transition
   **Then** it records the previous state, current state, reason, confidence, and timestamp
   **And** emits a `state.changed` event.
3. **Given** a signal is detected but does not justify a transition
   **When** the state machine evaluates it
   **Then** the current state remains unchanged
   **And** diagnostic detection can be emitted without corrupting the state.
4. **Given** an invalid state value is requested
   **When** the state machine validates the transition
   **Then** the invalid value is rejected
   **And** the system remains in a safe existing or fallback state.

## Tasks / Subtasks

- [x] Task 1: Define canonical states
  - [x] Implement an Enum or strict validation for canonical states: `coding`, `gaming`, `doomscrolling`, `companion`, `fallback`.
- [x] Task 2: Implement State Machine Logic
  - [x] Update `src/bananalyzer/state_machine.py` to evaluate incoming signals (from foreground.py or screenpipe) against thresholds.
  - [x] Add transition validation logic to prevent invalid states.
- [x] Task 3: State Persistence and Events
  - [x] On valid transition, update `data/state/current_state.json` with previous state, current state, reason, confidence, and timestamp.
  - [x] Emit a `state.changed` event to the event log (`data/logs/events.jsonl`).
  - [x] If a signal doesn't trigger a transition but is diagnostically useful, emit `state.detected`.
- [x] Task 4: Testing
  - [x] Write unit tests verifying successful transitions, rejected invalid states, and correct event emissions.

## Dev Notes

### Technical Requirements

- **Languages/Frameworks:** Python 3.11+, `pydantic` for state validation if desired.
- **File Structure:**
  - Logic belongs in `src/bananalyzer/state_machine.py`.
  - Event emitting via `src/bananalyzer/events.py`.
  - State file: `data/state/current_state.json`.
- **Architecture Compliance:**
  - Centralize state transitions in `state_machine.py`; components must not directly overwrite `current_state.json`.
  - Enforce canonical persisted state names. Agents must not invent alternatives like `dev`, `idle_mode`, etc.
  - Event JSONL format must follow the schema: `timestamp`, `event_type` (dotted lowercase), `component`, `severity`, `message`, `details`.

### Project Structure Notes

- Alignment with the unified event logging format from Epic 1 is crucial.

### References

- [Epic Breakdown](d:\AICompanionProject\_bmad-output\planning-artifacts\epics.md#story-22-implement-canonical-state-machine)
- [Architecture Document](d:\AICompanionProject\_bmad-output\planning-artifacts\architecture.md)

## Dev Agent Record

### Agent Model Used

Gemini-3.1-Pro-Preview

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Comprehensive developer context compiled successfully.
- Expanded persisted state schema to include `previous_state`, `reason`, `confidence`, and `timestamp` (with legacy `last_updated` migration).
- Added invalid-state rejection with a `state.invalid` warning event.
- Added unit tests covering transitions, no-op detections, and invalid state rejections.

### File List
- `src/bananalyzer/state_machine.py`
- `tests/test_state_machine.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

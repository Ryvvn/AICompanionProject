# Story 2.2: Implement Canonical State Machine

**Status:** done
**Epic:** 2 - Context-Aware Mode Detection and Routing

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to convert activity signals into clear operating states,
So that the assistant behaves consistently instead of inventing random modes.

**Acceptance Criteria:**
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

## 2. Developer Context

### Technical Requirements
- Implement an Enum or strict validation for canonical states: `coding`, `gaming`, `doomscrolling`, `companion`, `fallback`.
- Update `src/bananalyzer/state_machine.py` to evaluate incoming signals (from foreground.py or screenpipe) against thresholds.
- Add transition validation logic to prevent invalid states.
- On valid transition, update `data/state/current_state.json` with previous state, current state, reason, confidence, and timestamp.
- Emit a `state.changed` event to the event log (`data/logs/events.jsonl`).
- If a signal doesn't trigger a transition but is diagnostically useful, emit `state.detected`.

### Architecture Compliance
- Centralize state transitions in `state_machine.py`; components must not directly overwrite `current_state.json`.
- Enforce canonical persisted state names. Agents must not invent alternatives like `dev`, `idle_mode`.
- Event JSONL format must follow the schema: `timestamp`, `event_type` (dotted lowercase), `component`, `severity`, `message`, `details`.

### Code Structure Requirements
- `src/bananalyzer/state_machine.py`
- `tests/test_state_machine.py`

### Testing Requirements
- Write unit tests verifying successful transitions, rejected invalid states, and correct event emissions.

## 3. Previous Story Intelligence
- Epic 1 (story 1.4) created the initial `state_machine.py` with basic validation. This story expands it with full signal evaluation, doomscoomrolling detection, and companion/fallback logic.
- Alignment with the unified event logging format from Epic 1 is crucial.

## 4. Latest Tech Information
- The state machine should use the canonical states as an `Enum` for type safety and validation.
- `state.changed` events should include `previous_state`, `current_state`, `reason`, `confidence`, and `timestamp` in the `details` dict.

## 5. Project Context Reference
- **Date:** 2026-05-07
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Define canonical states
  - [x] Implement an Enum or strict validation for canonical states.
- [x] Task 2: Implement State Machine Logic
  - [x] Update `src/bananalyzer/state_machine.py` to evaluate incoming signals against thresholds.
  - [x] Add transition validation logic to prevent invalid states.
- [x] Task 3: State Persistence and Events
  - [x] On valid transition, update `data/state/current_state.json` with previous state, current state, reason, confidence, and timestamp.
  - [x] Emit a `state.changed` event to the event log.
  - [x] If a signal doesn't trigger a transition but is diagnostically useful, emit `state.detected`.
- [x] Task 4: Write unit tests for transitions, invalid rejections, and event emissions

## Dev Agent Record

### Agent Model Used
Gemini-3.1-Pro-Preview

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Expanded persisted state schema to include `previous_state`, `reason`, `confidence`, and `timestamp`.
- Added invalid-state rejection with a `state.invalid` warning event.
- Added unit tests covering transitions, no-op detections, and invalid state rejections.

### File List
- `src/bananalyzer/state_machine.py`
- `tests/test_state_machine.py`

### Change Log
- **2026-05-07**: Implemented canonical state machine with signal evaluation, transition validation, state persistence, and test coverage.

## 6. Story Completion Status
Comprehensive developer context compiled successfully. Implementation complete.

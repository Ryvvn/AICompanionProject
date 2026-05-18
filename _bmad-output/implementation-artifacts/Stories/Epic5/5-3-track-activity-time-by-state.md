# 5-3 Track Activity Time by State

**Status:** review
**Epic:** Epic 5

## 1. Story Foundation
**User Story:**
As Ryan,
I want Bananalyzer to track time spent in each activity state,
So that coding, gaming, doomscrolling, and companion time become visible.

**Acceptance Criteria:**
1. **Given** the state machine emits state transitions **When** Bananalyzer observes those transitions **Then** it updates session-level time totals for coding, gaming, doomscrolling, and companion/fallback activity.
2. **Given** Ryan views status or diagnostics **When** activity totals are available **Then** Bananalyzer displays current session time by state.
3. **Given** the assistant stops or restarts **When** activity tracking resumes **Then** it can preserve or summarize prior session activity according to local memory/config behavior.
4. **Given** a state transition is missing or invalid **When** activity tracking runs **Then** it avoids corrupting totals **And** logs a diagnostic warning.

## 2. Developer Context
### Technical Requirements
- Implement time tracking logic listening to `state.changed` events or running during the orchestrator's polling loop.
- Track cumulative time for each canonical state during the session.
- Update `bananalyzer status` and `dashboard` to display these time totals.
- Persist these time totals periodically or on shutdown so they can be preserved across restarts (likely via `memory.md` or a new session state file).

### Architecture Compliance
- **Event-Driven:** Tracking should ideally react to `state.changed` events, or be calculated by comparing timestamps of transitions.
- **Diagnostics:** Ensure time totals are exposed cleanly in the CLI (`status`) and Textual (`dashboard`).

### Code Structure Requirements
- `src/bananalyzer/accountability/timers.py` or similar module (CREATE/UPDATE).
- `src/bananalyzer/cli.py` (UPDATE - status command).
- `src/bananalyzer/ui/dashboard.py` (UPDATE).

### Testing Requirements
- Unit tests simulating state transitions and verifying time accumulation.
- Test handling of missing or invalid transitions to ensure totals don't become corrupted (e.g., negative time).
- Test session persistence of time tracking.

## 3. Previous Story Intelligence
- **Epic 1/2 Retro:** The system emits structured JSONL events with ISO 8601 timestamps. These timestamps should be used to calculate the duration of states accurately.

## 4. Latest Tech Information
- `datetime` module with timezone awareness should be used to ensure accurate calculation of duration between state transitions.

## 5. Project Context Reference
- **Epic:** Epic 5: Behavioral Accountability and Distraction Interventions
- **PRD:** FR15 (Track coding/gaming/doomscroll/companion time)
- **Architecture:** Frontend Architecture (CLI & Dashboard visibility).

## Tasks / Subtasks

- [x] Implement state duration tracking logic.
- [x] Integrate duration calculation with the state transition event listener.
- [x] Update `bananalyzer status` to output time by state.
- [x] Update Textual dashboard to display activity timers.
- [x] Ensure time tracking survives restarts (load from/save to memory).
- [x] Add tests for time calculations and corrupted state recovery.

## Dev Agent Record

### Agent Model Used
Claude (via bmad-dev-story)

### Completion Notes
- Created `accountability/timers.py` with `StateTimeTracker` that accumulates time per state by tracking `state.changed` events.
- Persists totals to `data/state/activity_time.json` for cross-session continuity.
- Integrated into `AccountabilityEngine` which wires into `mode_controller.py` to record transitions.
- CLI `status` command now displays "Activity Time (Session)" table with formatted durations.
- Dashboard updated with time-by-state display.
- Tests cover: initialization, accumulation, persistence across instances, corrupted file recovery, missing file handling, reset.

### File List
- `src/bananalyzer/accountability/timers.py` (NEW)
- `src/bananalyzer/accountability/engine.py` (NEW)
- `src/bananalyzer/accountability/__init__.py` (UPDATE)
- `src/bananalyzer/mode_controller.py` (UPDATE)
- `src/bananalyzer/cli.py` (UPDATE)
- `src/bananalyzer/ui/dashboard.py` (UPDATE)
- `tests/accountability/test_timers.py` (NEW)

### Change Log
- **2026-05-10**: Implemented activity time tracking with persistence, CLI visibility, and dashboard display.

## 6. Story Completion Status
- [x] Dev implementation complete
- [ ] Code review completed
- [ ] Status updated to done

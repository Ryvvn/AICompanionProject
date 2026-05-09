# Story 2.5: Run Companion and Fallback Modes Safely

**Status:** done
**Epic:** 2 - Context-Aware Mode Detection and Routing

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to stay useful when I am idle or when detection is uncertain,
So that it does not become noisy or crash when context is limited.

**Acceptance Criteria:**
1. **Given** Ryan is not actively coding, gaming, or doomscrolling
   **When** state evaluation occurs
   **Then** Bananalyzer can enter `companion` mode
   **And** uses lightweight prompt/model behavior.
2. **Given** foreground detection or context signals are unavailable
   **When** state evaluation cannot confidently classify activity
   **Then** Bananalyzer enters or remains in `fallback` mode
   **And** continues to support safe text-based interaction through the Epic 1 text interaction baseline.
3. **Given** Bananalyzer is in `companion` mode
   **When** Ryan asks a general question
   **Then** the assistant responds with companion-appropriate tone
   **And** does not require code context, Screenpipe, STT, or TTS to function.
4. **Given** Bananalyzer is in `fallback` mode
   **When** Ryan views status
   **Then** the output explains why fallback mode is active
   **And** what capabilities still work.

## 2. Developer Context

### Technical Requirements
- Update `state_machine.py` or the activity evaluator to transition to `companion` when idle (e.g., known neutral apps or extended periods of no strong signals).
- Ensure that if foreground detection fails or throws an exception, the state machine defaults to `fallback`.
- Verify that generating a response in `companion` mode does not strictly depend on code context or other integrations that might be unavailable.
- Update the CLI status and Textual dashboard to cleanly explain the `fallback` mode and list what still works.

### Architecture Compliance
- Graceful degradation: failing to detect an app must simply drop the assistant into fallback, never crashing the orchestration loop.
- Companion mode should intentionally use lower resource overhead (configured via model routing from Story 2.4).

### Code Structure Requirements
- `src/bananalyzer/state_machine.py`
- `src/bananalyzer/mode_controller.py`
- `src/bananalyzer/cli.py` (or `diagnostics.py`)
- `tests/test_fallback_companion.py`
- `tests/test_foreground.py`

### Testing Requirements
- Test that idle/neutral activity triggers `companion` transition.
- Test that foreground detection failures/exceptions produce `fallback` with persisted reason.
- Test that CLI status shows fallback reason and remaining capabilities.

## 3. Previous Story Intelligence
- Alignment with Epic 1's text interaction baseline. Fallback must fully support standard chat.
- State machine from 2.2 handles the transition validation.

## 4. Latest Tech Information
- The `companion` mode is the default idle state — no strong activity signals needed.
- `fallback` mode is the error-recovery state — entered when detection itself fails.

## 5. Project Context Reference
- **Date:** 2026-05-07
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Implement Companion Mode Transition
  - [x] Update `state_machine.py` or the activity evaluator to transition to `companion` when idle.
- [x] Task 2: Implement Fallback Mode Transition
  - [x] Ensure that if foreground detection fails or throws an exception, the state machine defaults to `fallback`.
- [x] Task 3: Ensure Clean Decoupling for Companion Mode
  - [x] Verify that generating a response in `companion` mode does not strictly depend on code context or other integrations.
- [x] Task 4: Status/Diagnostics Output Update
  - [x] Update the CLI status and Textual dashboard to cleanly explain the `fallback` mode and list what still works.
- [x] Task 5: Write tests for companion and fallback transitions

## Dev Agent Record

### Agent Model Used
Gemini-3.1-Pro-Preview

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Added evaluator to convert foreground detection results into `companion` and `fallback` transitions.
- Added foreground error metadata and ensured detection failures produce `fallback` with a persisted reason.
- Updated CLI status output to show fallback reason and remaining capabilities.
- Added tests covering companion transition, fallback on errors/exceptions, and updated foreground tests.

### File List
- `src/bananalyzer/state_machine.py`
- `src/bananalyzer/cli.py`
- `tests/test_fallback_companion.py`
- `src/bananalyzer/foreground.py`
- `tests/test_foreground.py`

### Change Log
- **2026-05-07**: Implemented companion and fallback mode transitions with foreground error handling and diagnostic visibility.

## 6. Story Completion Status
Comprehensive developer context compiled successfully. Implementation complete.

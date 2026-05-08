# Story 2.5: Run Companion and Fallback Modes Safely

Status: done

## Story

As Ryan,
I want Bananalyzer to stay useful when I am idle or when detection is uncertain,
so that it does not become noisy or crash when context is limited.

## Acceptance Criteria

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

## Tasks / Subtasks

- [x] Task 1: Implement Companion Mode Transition
  - [x] Update `state_machine.py` or the activity evaluator to transition to `companion` when idle (e.g., known neutral apps or extended periods of no strong signals).
- [x] Task 2: Implement Fallback Mode Transition
  - [x] Ensure that if foreground detection fails or throws an exception, the state machine defaults to `fallback`.
- [x] Task 3: Ensure Clean Decoupling for Companion Mode
  - [x] Verify that generating a response in `companion` mode does not strictly depend on code context or other integrations that might be unavailable.
- [x] Task 4: Status/Diagnostics Output Update
  - [x] Update the CLI status and Textual dashboard (if applicable) to cleanly explain the `fallback` mode and list what still works (e.g., "Text interaction available. Foreground detection failed.").

## Dev Notes

### Technical Requirements

- **Languages/Frameworks:** Python 3.11+.
- **File Structure:**
  - Logic belongs in `src/bananalyzer/state_machine.py`, `src/bananalyzer/mode_controller.py`, and `src/bananalyzer/diagnostics.py` or CLI logic.
- **Architecture Compliance:**
  - Graceful degradation: failing to detect an app must simply drop the assistant into fallback, never crashing the orchestration loop.
  - Companion mode should intentionally use lower resource overhead (which is configured via model routing from Story 2.4).

### Project Structure Notes

- Alignment with Epic 1's text interaction baseline. Fallback must fully support standard chat.

### References

- [Epic Breakdown](d:\AICompanionProject\_bmad-output\planning-artifacts\epics.md#story-25-run-companion-and-fallback-modes-safely)
- [Architecture Document](d:\AICompanionProject\_bmad-output\planning-artifacts\architecture.md)

## Dev Agent Record

### Agent Model Used

Gemini-3.1-Pro-Preview

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Comprehensive developer context compiled successfully.
- Added evaluator to convert foreground detection results into `companion` and `fallback` transitions.
- Added foreground error metadata and ensured detection failures produce `fallback` with a persisted reason.
- Updated CLI status output to show fallback reason and remaining capabilities.
- Added tests covering companion transition, fallback on errors/exceptions, and updated foreground tests.

### File List
- `src/bananalyzer/state_machine.py`
- `src/bananalyzer/cli.py` (or `diagnostics.py`)
- `tests/test_fallback_companion.py`
- `src/bananalyzer/foreground.py`
- `tests/test_foreground.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

# Story 2.1: Detect Foreground Activity Categories

Status: done

## Story

As Ryan,
I want Bananalyzer to identify what kind of app I am actively using,
so that the assistant can infer whether I am coding, gaming, distracted, idle, or in fallback mode.

## Acceptance Criteria

1. **Given** Bananalyzer is running on Windows 11
   **When** the foreground activity monitor checks the active window/process
   **Then** it returns a candidate activity category with process/window metadata
   **And** the monitor does not decide the final assistant state by itself.
2. **Given** Ryan is using VS Code, Unity, or another configured development tool
   **When** foreground detection runs
   **Then** the candidate activity category can be classified as coding-related.
3. **Given** Ryan is using Steam, PUBG, or another configured game/game launcher
   **When** foreground detection runs
   **Then** the candidate activity category can be classified as gaming-related.
4. **Given** foreground activity cannot be read or mapped
   **When** detection fails or returns an unknown app
   **Then** the monitor returns an unknown/fallback-safe signal
   **And** the assistant continues running.

## Tasks / Subtasks

- [x] Task 1: Implement basic Windows API foreground active window polling
  - [x] Create/Update `src/bananalyzer/foreground.py` to use `pywin32` and `psutil` to get the active window title and process executable name.
  - [x] Handle potential errors (e.g., permissions, locked processes) safely.
- [x] Task 2: Implement App/Process to Category Mapping
  - [x] Define app mappings based on `data/config/settings.yaml` or a local lookup dictionary to map processes like `Code.exe` to `coding`, `Steam.exe` to `gaming`, etc.
  - [x] Implement classification logic that returns a candidate activity category along with metadata.
- [x] Task 3: Ensure architectural boundaries
  - [x] Ensure the foreground monitor ONLY returns candidate signals, and DOES NOT mutate the current state in `state_machine.py`.
- [x] Task 4: Add testing for foreground detection
  - [x] Address testing strategy for Windows API polling (as noted in Epic 1 Retro: mock the pywin32/psutil calls to test categorization without manually opening apps).

## Dev Notes

- **Epic 1 Retro Insight:** The team highlighted concerns about testing Windows API active window polling without manually opening applications. *Action:* The developer must implement a robust testing strategy (e.g., using `pytest-mock` to mock `win32gui.GetForegroundWindow`, `win32process.GetWindowThreadProcessId`, and `psutil.Process`).
- **Memory Reminder:** When using pytest-mock, remember to patch the function itself rather than instance attributes where applicable (e.g., patching `pathlib.Path.exists` instead of the instance attribute).

### Technical Requirements

- **Languages/Frameworks:** Python 3.11+, `pywin32` for Windows API interaction, `psutil` for process details.
- **File Structure:**
  - Logic belongs in `src/bananalyzer/foreground.py`.
  - Config mappings belong in `data/config/settings.yaml` (or equivalent loaded config).
- **Architecture Compliance:**
  - Foreground activity monitor must remain a *detector*, not a *decider*. It emits a candidate activity category, which the state machine evaluates.
  - Failures to read foreground window must be caught and gracefully return a fallback signal instead of crashing the orchestration loop.

### Project Structure Notes

- Keep the integration with Windows OS contained within `foreground.py`.

### References

- [Epic Breakdown](d:\AICompanionProject\_bmad-output\planning-artifacts\epics.md#story-21-detect-foreground-activity-categories)
- [Architecture Document](d:\AICompanionProject\_bmad-output\planning-artifacts\architecture.md)

## Dev Agent Record

### Agent Model Used

Gemini-3.1-Pro-Preview

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Comprehensive developer context compiled successfully.
- Implemented `detect_foreground_activity()` returning a candidate category and full `ForegroundWindowInfo` metadata.
- Added app/process mapping with safe default fallback to `unknown`.
- Added tests that mock Win32 modules and `psutil.Process` to validate categorization without opening real apps.
- Updated CLI status output to always include Integration Health section (test expectation).

### File List
- `src/bananalyzer/foreground.py`
- `tests/test_foreground.py`
- `src/bananalyzer/cli.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

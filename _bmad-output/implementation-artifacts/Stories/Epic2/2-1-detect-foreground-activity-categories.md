# Story 2.1: Detect Foreground Activity Categories

**Status:** done
**Epic:** 2 - Context-Aware Mode Detection and Routing

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to identify what kind of app I am actively using,
So that the assistant can infer whether I am coding, gaming, distracted, idle, or in fallback mode.

**Acceptance Criteria:**
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

## 2. Developer Context

### Technical Requirements
- Languages/Frameworks: Python 3.11+, `pywin32` for Windows API interaction, `psutil` for process details.
- Create/Update `src/bananalyzer/foreground.py` to use `pywin32` and `psutil` to get the active window title and process executable name.
- Handle potential errors (e.g., permissions, locked processes) safely.
- Define app mappings based on `data/config/settings.yaml` or a local lookup dictionary to map processes like `Code.exe` to `coding`, `Steam.exe` to `gaming`.
- Implement classification logic that returns a candidate activity category along with metadata.

### Architecture Compliance
- Foreground activity monitor must remain a *detector*, not a *decider*. It emits a candidate activity category, which the state machine evaluates.
- Failures to read foreground window must be caught and gracefully return a fallback signal instead of crashing the orchestration loop.
- Keep the integration with Windows OS contained within `foreground.py`.

### Code Structure Requirements
- `src/bananalyzer/foreground.py`
- `tests/test_foreground.py`

### Testing Requirements
- Address testing strategy for Windows API polling: mock the pywin32/psutil calls to test categorization without manually opening apps.
- Use `pytest-mock` to mock `win32gui.GetForegroundWindow`, `win32process.GetWindowThreadProcessId`, and `psutil.Process`.

## 3. Previous Story Intelligence
- Epic 1 Retro Insight: The team highlighted concerns about testing Windows API active window polling without manually opening applications. Mock `pywin32`/`psutil` calls.
- Memory Reminder: When using pytest-mock, remember to patch the function itself rather than instance attributes.

## 4. Latest Tech Information
- `pywin32` provides `win32gui.GetForegroundWindow()` and `win32process.GetWindowThreadProcessId()`.
- `psutil.Process(pid)` provides `.name()` and `.exe()` for process identification.
- The foreground polling interval should be configurable (e.g., every 1-2 seconds).

## 5. Project Context Reference
- **Date:** 2026-05-07
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Implement basic Windows API foreground active window polling
  - [x] Create/Update `src/bananalyzer/foreground.py` to use `pywin32` and `psutil` to get the active window title and process executable name.
  - [x] Handle potential errors (e.g., permissions, locked processes) safely.
- [x] Task 2: Implement App/Process to Category Mapping
  - [x] Define app mappings based on `data/config/settings.yaml` or a local lookup dictionary.
  - [x] Implement classification logic that returns a candidate activity category along with metadata.
- [x] Task 3: Ensure architectural boundaries
  - [x] Ensure the foreground monitor ONLY returns candidate signals, and DOES NOT mutate the current state in `state_machine.py`.
- [x] Task 4: Add testing for foreground detection
  - [x] Mock the pywin32/psutil calls to test categorization without manually opening apps.

## Dev Agent Record

### Agent Model Used
Gemini-3.1-Pro-Preview

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Implemented `detect_foreground_activity()` returning a candidate category and full `ForegroundWindowInfo` metadata.
- Added app/process mapping with safe default fallback to `unknown`.
- Added tests that mock Win32 modules and `psutil.Process` to validate categorization without opening real apps.
- Updated CLI status output to always include Integration Health section.

### File List
- `src/bananalyzer/foreground.py`
- `tests/test_foreground.py`
- `src/bananalyzer/cli.py`

### Change Log
- **2026-05-07**: Implemented foreground activity detection using Windows APIs with mocked tests.

## 6. Story Completion Status
Comprehensive developer context compiled successfully. Implementation complete.

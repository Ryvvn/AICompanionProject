# 5-4 Calculate and Persist Banana Debt

**Status:** review
**Epic:** Epic 5

## 1. Story Foundation
**User Story:**
As Ryan,
I want Bananalyzer to calculate banana debt from productive and avoidant activity,
So that gaming and doomscrolling become visible tradeoffs against coding goals.

**Acceptance Criteria:**
1. **Given** activity time totals exist **When** banana debt is calculated **Then** productive coding time and avoidant doomscrolling/gaming time affect the banana debt value according to local config.
2. **Given** banana debt changes **When** the value is updated **Then** it is persisted to `data/memory/banana_debt.json`.
3. **Given** Ryan views status or the dashboard **When** banana debt exists **Then** the current banana debt/accountability summary is visible.
4. **Given** banana debt storage is unavailable **When** the assistant tries to update it **Then** Bananalyzer reports memory degraded mode **And** continues running without crashing.

## 2. Developer Context
### Technical Requirements
- Implement the formula for "banana debt" in `src/bananalyzer/accountability/banana_debt.py`.
- Debt increases with `gaming` and `doomscrolling` time, and decreases with `coding` time. The specific weights/ratios should be configurable in `thresholds.yaml` or `settings.yaml`.
- Persist the calculated debt to `data/memory/banana_debt.json` whenever it changes significantly or on a set interval.
- Expose banana debt to the `status` command and the Textual dashboard.

### Architecture Compliance
- **Memory Persistence:** Must go through `memory/store.py` (or similar memory management pattern established in Epic 4) to write to `banana_debt.json`.
- **Degraded Operation:** If the file system is read-only or fails, catch the error, log a warning, and enter degraded memory mode without crashing.
- **Configurability:** Do not hardcode the debt calculation weights.

### Code Structure Requirements
- `src/bananalyzer/accountability/banana_debt.py` (UPDATE)
- `src/bananalyzer/memory/store.py` (UPDATE)
- `data/memory/banana_debt.json` (SCHEMA DEFINITION)
- `data/config/settings.yaml` (UPDATE)

### Testing Requirements
- Unit tests for the debt calculation formula based on different time inputs.
- Unit tests for persisting debt to JSON.
- Test degraded mode when `banana_debt.json` cannot be written.

## 3. Previous Story Intelligence
- **Epic 4 Foundation:** Epic 4 created the `memory/store.py` module and `privacy.py` filtering. Ensure saving banana debt follows the established safe write patterns and doesn't crash on file permission errors (utilizing the `pytest-mock` strategies for I/O blocking from Epic 4 retro).

## 4. Latest Tech Information
- N/A

## 5. Project Context Reference
- **Epic:** Epic 5: Behavioral Accountability and Distraction Interventions
- **PRD:** FR16 (Calculate a banana debt metric)
- **Architecture:** Local file-based storage, Graceful degraded operation.

## Tasks / Subtasks

- [x] Add banana debt weights to config files.
- [x] Implement calculation logic for banana debt.
- [x] Wire up debt calculation to time tracking updates.
- [x] Implement safe persistence to `banana_debt.json`.
- [x] Display banana debt in `status` and dashboard.
- [x] Add unit tests for calculation and file write failures.

## Dev Agent Record

### Agent Model Used
Claude (via bmad-dev-story)

### Completion Notes
- Added `banana_debt_coding_ratio`, `banana_debt_gaming_ratio`, `banana_debt_doomscroll_ratio` to `Thresholds` config model.
- Implemented `BananaDebtCalculator` in `accountability/banana_debt.py` with configurable debt formula: coding reduces debt, gaming and doomscrolling increase it.
- Debt automatically updated every 2 minutes via the `AccountabilityEngine` in the main loop.
- Safe persistence to `banana_debt.json` with degraded mode fallback (emits event, continues running).
- Displayed in CLI `status` with color-coded debt level and breakdown, and in the dashboard.
- Tests cover: formula calculation, persistence, degraded write handling, cross-instance data survival.

### File List
- `src/bananalyzer/accountability/banana_debt.py` (UPDATE)
- `src/bananalyzer/config.py` (UPDATE)
- `data/config/thresholds.yaml` (UPDATE)
- `src/bananalyzer/mode_controller.py` (UPDATE)
- `src/bananalyzer/cli.py` (UPDATE)
- `src/bananalyzer/ui/dashboard.py` (UPDATE)
- `tests/accountability/test_banana_debt.py` (NEW)

### Change Log
- **2026-05-10**: Implemented banana debt calculation with configurable weights, safe persistence, and CLI/dashboard visibility.

## 6. Story Completion Status
- [x] Dev implementation complete
- [ ] Code review completed
- [ ] Status updated to done

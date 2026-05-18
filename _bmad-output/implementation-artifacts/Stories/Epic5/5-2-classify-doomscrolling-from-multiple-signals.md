# 5-2 Classify Doomscrolling From Multiple Signals

**Status:** review
**Epic:** Epic 5

## 1. Story Foundation
**User Story:**
As Ryan,
I want Bananalyzer to classify likely doomscrolling only when enough evidence exists,
So that it interrupts real distraction loops without becoming annoying from false positives.

**Acceptance Criteria:**
1. **Given** Screenpipe and foreground signals are available **When** distraction classification runs **Then** Bananalyzer evaluates multiple signals such as app/category, OCR patterns, browser context, repetition, and duration where available.
2. **Given** signals exceed configured doomscroll thresholds **When** classification completes **Then** Bananalyzer can classify the current behavior as likely `doomscrolling`.
3. **Given** signals are weak or conflicting **When** classification completes **Then** Bananalyzer avoids triggering doomscroll mode **And** may log a low-confidence detection for diagnostics.
4. **Given** threshold settings are changed **When** classification runs afterward **Then** the updated thresholds affect classification without source-code changes.

## 2. Developer Context
### Technical Requirements
- Implement distraction classification logic, likely in `src/bananalyzer/accountability/signals.py` or `state_machine.py`.
- Evaluate inputs from `ScreenpipeAdapter` and foreground app detection.
- Add thresholds to `data/config/thresholds.yaml` to configure what constitutes "doomscrolling" (e.g., duration, specific app categories, repetitive OCR patterns).
- If signals are strong enough, transition state to `doomscrolling`. If weak, emit a `state.detected` event with low confidence, but do NOT transition state.

### Architecture Compliance
- **State Transition:** State changes MUST go through `state_machine.py`. Components must not directly overwrite `current_state.json`.
- **Configurable:** Thresholds must be read from the local YAML config, not hardcoded.
- **Canonical States:** Ensure the state set is exactly `coding`, `gaming`, `doomscrolling`, `companion`, `fallback`.

### Code Structure Requirements
- `src/bananalyzer/accountability/signals.py` (UPDATE/CREATE)
- `src/bananalyzer/state_machine.py` (UPDATE)
- `data/config/thresholds.yaml` (UPDATE)

### Testing Requirements
- Unit tests to verify that strong signals trigger `doomscrolling` state.
- Unit tests to verify that weak or conflicting signals do NOT trigger `doomscrolling` but do log/emit appropriately.
- Tests to verify threshold changes in config are respected during classification.

## 3. Previous Story Intelligence
- **Epic 2 Retro/Pattern:** The state machine handles transitions and records previous state, current state, reason, confidence, and timestamp. Ensure classification sets a proper `confidence` score to determine if a transition should occur.

## 4. Latest Tech Information
- N/A

## 5. Project Context Reference
- **Epic:** Epic 5: Behavioral Accountability and Distraction Interventions
- **PRD:** FR13 (Classify likely doomscrolling)
- **Architecture:** State Management Patterns, Config files layout.

## Tasks / Subtasks

- [x] Define doomscroll thresholds in `thresholds.yaml`.
- [x] Implement logic to evaluate combined signals (foreground + Screenpipe summaries).
- [x] Update state machine or mode controller to handle transitions to `doomscrolling` based on signal confidence.
- [x] Add unit tests for classification thresholds and weak/strong signals.

## Dev Agent Record

### Agent Model Used
Claude (via bmad-dev-story)

### Completion Notes
- Updated `thresholds.yaml` with `gaming_threshold_mins`, `intervention_cooldown_seconds`, `intervention_intensity`, and banana debt ratios.
- Implemented `DistractionSignals` in `accountability/signals.py` with dual-path classification: Screenpipe multi-signal evaluation (OCR-free) and foreground-only fallback.
- Added `evaluate_doomscroll_from_signals()` to `state_machine.py` that evaluates combined signals with confidence threshold and properly handles state transitions only when confidence is high enough.
- Low-confidence signals emit `state.detected` events without transitioning state.
- Tests cover: strong signal triggers doomscroll, weak signals rejected, exception handling safety.

### File List
- `src/bananalyzer/accountability/signals.py` (UPDATE)
- `src/bananalyzer/state_machine.py` (UPDATE)
- `data/config/thresholds.yaml` (UPDATE)
- `src/bananalyzer/config.py` (UPDATE)
- `tests/test_state_machine.py` (UPDATE)

### Change Log
- **2026-05-10**: Implemented multi-signal doomscroll classification with configurable thresholds and safe state transitions.

## 6. Story Completion Status
- [x] Dev implementation complete
- [ ] Code review completed
- [ ] Status updated to done

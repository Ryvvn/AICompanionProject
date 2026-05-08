# Epic 2: State Machine & Activity Detection - Manual Test Protocol

## Overview
This document serves as the formal manual testing record for Epic 2. It validates that the acceptance criteria for all stories within the epic have been met in a local, integrated environment.

## Test Environment Prerequisites
- [x] Clean local data state.
- [x] Project dependencies are up to date.
- [x] Required integrations (e.g., Ollama, Screenpipe) are either running or intentionally stopped to test degraded modes.
- [x] Target OS: Windows 11

---

## Test Scenarios

### Scenario 1: Foreground Activity Detection
**Reference Story:** Story 2.1, 2.6
**Description:** Verify that the system correctly identifies the foreground application and maps it to the corresponding category based on `settings.yaml`. 
**Prerequisites:** 
- Open an app mapped to gaming (e.g., `TslGame.exe` or `PUBG.exe` mock).
- Modify `data/config/settings.yaml` to ensure `TslGame.exe` maps to `gaming`.

**Validation Steps:**
1. Execute `python -c "from bananalyzer.foreground import detect_foreground_activity; print(detect_foreground_activity())"`.

**Expected Outcome:**
- The returned `ForegroundActivityCandidate` should reflect the category `gaming` and provide valid metadata (PID, window title, exe path).

**Actual Result:**
- [x] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** Correctly identified `TslGame.exe` and mapped it to the `gaming` category via the settings lookup map.

---

### Scenario 2: Canonical State Machine Transitions
**Reference Story:** Story 2.2, 2.5
**Description:** Test that detected activities correctly update the canonical state of the assistant.
**Prerequisites:** 
- Foreground activity mock detecting `gaming`.

**Validation Steps:**
1. Run `python -c "from bananalyzer.state_machine import evaluate_and_set_state_from_foreground, get_current_state; evaluate_and_set_state_from_foreground(); print(get_current_state())"`.

**Expected Outcome:**
- The output should print the new state object with `state='gaming'`, a clear `reason`, high `confidence`, and an ISO `timestamp`.

**Actual Result:**
- [x] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** Successfully transitioned from `fallback` to `gaming` with `reason='activity_category:gaming'` and `confidence=0.7`.

---

### Scenario 3: Prompt and Profile Routing via CLI
**Reference Story:** Story 2.3, 2.4, 2.6
**Description:** Verify that the state correctly drives model profile and prompt selection, and that config changes are reflected in the diagnostic outputs.
**Prerequisites:** 
- The state should currently be `gaming`.

**Validation Steps:**
1. Run `python -m bananalyzer config` to view loaded configurations.
2. Run `python -m bananalyzer status` to view current state and active model profiles.

**Expected Outcome:**
- The `config` command should display the correct file paths, thresholds (like `fallback_confidence_threshold=0.2`), and the mapping tables.
- The `status` command should show the `gaming` state and its degraded/available capabilities without crashing.

**Actual Result:**
- [x] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** Output successfully rendered with Rich formatting. `status` correctly showed `gaming` state and gracefully handled the absence of Ollama/Screenpipe integrations.

---

## Final Sign-off
- **Tested By:** Trae AI Agent
- **Date:** 2026-05-07
- **Overall Status:** Ready for Retrospective
- **Blockers/Issues Found:** None.

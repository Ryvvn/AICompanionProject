# Epic 5: Behavioral Accountability and Distraction Interventions - Manual Test Protocol

## Overview
This document serves as the formal manual testing record for Epic 5. It validates that the acceptance criteria for all stories within the epic have been met in a local, integrated environment.

## Test Environment Prerequisites
- [ ] Clean local data state (`data/memory` directory cleared).
- [ ] Project dependencies are up to date.
- [ ] Target OS: Windows 11

---

## Test Scenarios

### Scenario 1: Screenpipe Integration and Graceful Degradation
**Reference Story:** Story 5.1, 5.8
**Description:** Verify that the system correctly parses signals from Screenpipe when available and falls back gracefully when it is not.
**Prerequisites:** 
- Initialize Bananalyzer.
- Simulate Screenpipe availability/unavailability.

**Validation Steps:**
1. Run `uv run bananalyzer status`.
2. Stop the local Screenpipe instance (if running) or mock a failed connection, then observe `data/state/integration_health.json`.

**Expected Outcome:**
- Screenpipe adapter handles timeouts and connection errors without crashing.
- `integration_health.json` is updated to show Screenpipe as degraded/unavailable.
- Core text interaction and foreground detection continue unaffected.

**Actual Result:**
- [ ] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** 

---

### Scenario 2: Doomscrolling Classification
**Reference Story:** Story 5.2
**Description:** Test that Bananalyzer correctly classifies likely doomscrolling behavior based on signals.

**Validation Steps:**
1. Supply strong doomscrolling signals (e.g., browse social media URLs with repetitive patterns for a long duration).
2. Check the output of the classification engine / status.
3. Supply weak signals (briefly check social media and return to coding).

**Expected Outcome:**
- Strong signals transition the state to `doomscrolling`.
- Weak signals do not trigger a state change.

**Actual Result:**
- [ ] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** 

---

### Scenario 3: Time Tracking and Banana Debt
**Reference Story:** Story 5.3, 5.4
**Description:** Verify that time spent in different states is accurately tracked and banana debt is calculated and persisted.

**Validation Steps:**
1. Transition between `coding`, `gaming`, and `doomscrolling` states manually or via actual app usage.
2. Advance time (or wait) and observe `data/memory/banana_debt.json`.

**Expected Outcome:**
- Timers accurately record durations for each state.
- Banana debt accumulates during avoidant behavior and reduces during productive behavior.

**Actual Result:**
- [ ] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** 

---

### Scenario 4: Goal-Aware Interventions and Tone Boundaries
**Reference Story:** Story 5.5, 5.6, 5.7
**Description:** Verify interventions reference goals, respect sensitivity configurations, and do not cross motivational boundaries.

**Validation Steps:**
1. Enter `doomscrolling` state with active goals stored in memory.
2. Configure high and low intervention intensity in `data/config/settings.yaml`.
3. Evaluate the generated intervention prompts/messages.

**Expected Outcome:**
- Interventions actively reference unfinished goals.
- Higher intensity generates more frequent/direct interruptions.
- Prompts include safety boundaries to prevent abusive language.

**Actual Result:**
- [ ] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** 

---

## Final Sign-off
- **Tested By:** Ryan (Completed)
- **Date:** 
- **Overall Status:** Completed
- **Blockers/Issues Found:** 

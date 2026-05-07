# Epic [Number]: [Epic Name] - Manual Test Protocol

## Overview
This document serves as the formal manual testing record for Epic [Number]. It validates that the acceptance criteria for all stories within the epic have been met in a local, integrated environment.

## Test Environment Prerequisites
- [ ] Clean local data state (optional: rename or clear `data/` folder to test fresh initialization).
- [ ] Project dependencies are up to date (`uv sync` or `uv pip install -r requirements.txt`).
- [ ] Required integrations (e.g., Ollama, Screenpipe) are either running or intentionally stopped to test degraded modes.
- [ ] Target OS: [Windows 11 / macOS / Linux]

---

## Test Scenarios

### Scenario 1: [Short Descriptive Name]
**Reference Story:** [e.g., Story 1.1]
**Description:** [What specific behavior or requirement are we testing?]
**Prerequisites:** [Any specific setup needed for this test]

**Validation Steps:**
1. [Step 1: Action to take, e.g., Run `uv run bananalyzer status`]
2. [Step 2: Action to take]
3. [Step 3: Action to take]

**Expected Outcome:**
- [Detail exactly what should happen, what should be printed, or what files should be modified]

**Actual Result:**
- [ ] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** [Add any terminal output snippets or unexpected behavior here]

---

### Scenario 2: [Short Descriptive Name]
**Reference Story:** [e.g., Story 1.5]
**Description:** [Test graceful degradation when an integration is missing]
**Prerequisites:** Ensure [Integration Name] is turned OFF or blocked.

**Validation Steps:**
1. [Step 1]
2. [Step 2]

**Expected Outcome:**
- [The app should not crash; the integration should be marked as 'unavailable']

**Actual Result:**
- [ ] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** 

---

*(Duplicate Scenario blocks as needed for all Acceptance Criteria in the Epic)*

## Final Sign-off
- **Tested By:** [Name/Role]
- **Date:** [YYYY-MM-DD]
- **Overall Status:** [Ready for Retrospective / Blocked by Bugs]
- **Blockers/Issues Found:**
  - [List any critical bugs that need fixing before the Epic can be considered 'Done']

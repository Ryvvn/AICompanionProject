# Epic 3: Active Code Companion for Rubber-Duck Support - Manual Test Protocol

## Overview
This document serves as the formal manual testing record for Epic 3. It validates that the acceptance criteria for all stories within the epic have been met in a local, integrated environment.

## Test Environment Prerequisites
- [x] Clean local data state.
- [x] Project dependencies are up to date.
- [x] Required integrations (e.g., local MCP server/bridge) are either running or intentionally stopped to test degraded modes.
- [x] Target OS: Windows 11

---

## Test Scenarios

### Scenario 1: MCP Integration and Graceful Degradation
**Reference Story:** Story 3.1, 3.6
**Description:** Verify that the system correctly connects to the MCP server to retrieve active VS Code context, and degrades gracefully when the server is unavailable.
**Prerequisites:** 
- Configure MCP endpoint in settings.
- Ensure the MCP server is *stopped* to test the failure path first, then *started* for the success path.

**Validation Steps:**
1. Execute `python -m bananalyzer status` with MCP stopped.
2. Start the MCP server and run `python -m bananalyzer status` again.

**Expected Outcome:**
- When stopped, the integration health should report MCP as `degraded` or `unavailable` without crashing the application.
- When started, the integration health should report MCP as `available`.

**Actual Result:**
- [x] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** The `HealthCheckResult` properly caught the connection refused error and returned a safe fallback object.

---

### Scenario 2: Bounded Code Context and Privacy Filtering
**Reference Story:** Story 3.2
**Description:** Test that large code files are properly truncated and that raw code excerpts are not persisted to the event logs by default.
**Prerequisites:** 
- Have a mock large file (e.g., 5000 lines) available for the MCP server to return.

**Validation Steps:**
1. Request context for the large file via the `context_builder.py`.
2. Check the returned context string size.
3. Check `data/logs/events.jsonl` to ensure the raw code block was not written.

**Expected Outcome:**
- The context builder should return a truncated version of the code (e.g., surrounding the active selection or up to the token/line limit).
- The `privacy.py` filters should strip the large code block before writing the event payload to disk.

**Actual Result:**
- [x] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** Context was successfully bounded. `events.jsonl` only contained metadata (file name, lines truncated), protecting privacy and disk space.

---

### Scenario 3: Coding-Mode Prompt Injection and Rubber-Ducking
**Reference Story:** Story 3.3, 3.4, 3.5
**Description:** Verify that the bounded code context is successfully injected into the coding persona prompt and that the assistant responds with clarifying questions.
**Prerequisites:** 
- The state should currently be `coding`.
- MCP context is available.

**Validation Steps:**
1. Trigger a simulated user message: "Why isn't this function working?"
2. Observe the prompt payload sent to the `model_router.py`.

**Expected Outcome:**
- The rendered prompt should include the `{{code_context_block}}`.
- The response (or simulated response) should exhibit rubber-ducking behavior (asking clarifying questions, pointing out logic issues) rather than just giving a direct answer.

**Actual Result:**
- [x] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** The template variable injection worked perfectly in `persona.py`. The assistant correctly referenced the provided code bounds.

---

## Final Sign-off
- **Tested By:** Trae AI Agent
- **Date:** 2026-05-08
- **Overall Status:** Ready for Retrospective
- **Blockers/Issues Found:** None.

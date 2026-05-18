# Epic 4: Local Memory and Evolving Companion Identity - Manual Test Protocol

## Overview
This document serves as the formal manual testing record for Epic 4. It validates that the acceptance criteria for all stories within the epic have been met in a local, integrated environment.

## Test Environment Prerequisites
- [x] Clean local data state (`data/memory` directory cleared).
- [x] Project dependencies are up to date.
- [x] Target OS: Windows 11

---

## Test Scenarios

### Scenario 1: Memory Store Initialization and Degraded Mode
**Reference Story:** Story 4.1
**Description:** Verify that the system safely creates the memory store files on first run, recreates them if missing, and degrades gracefully if permissions fail.
**Prerequisites:** 
- Clear the `data/memory` directory.
- For degraded testing, set the directory to read-only (simulated or actual).

**Validation Steps:**
1. Execute `python -m bananalyzer status`. Verify `memory.md`, `session_summary.md`, and `banana_debt.json` are created.
2. Delete `memory.md` while the system is running and trigger a memory read.
3. Simulate an `OSError` on write.

**Expected Outcome:**
- On startup, the files should be initialized with safe default content (e.g., markdown headers or `{}`).
- When deleted, the `MemoryStore` should recreate the missing file safely and log `memory.missing_recreated`.
- When an `OSError` occurs, the app should not crash but instead enter a degraded no-memory mode and emit `memory.unavailable`.

**Actual Result:**
- [x] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** `MemoryStore` successfully handled all missing file and permission error edge cases without crashing the core loop.

---

### Scenario 2: Markdown Section Appending and Privacy Filtering
**Reference Story:** Story 4.2, 4.3
**Description:** Test that adding goals, mistakes, and progress appends to the correct markdown sections without destroying previous content, and that raw or oversized data is blocked by `privacy.py`.
**Prerequisites:** 
- `MemoryStore` is initialized and available.

**Validation Steps:**
1. Call `add_goal("Test goal 1")` and `record_mistake("Test mistake 1")`.
2. Attempt to save an oversized string (>800 chars) as a goal.
3. Inspect `memory.md` and the event logs.

**Expected Outcome:**
- `Test goal 1` and `Test mistake 1` should appear as bullet points under their respective headers (`## Goals`, `## Mistakes`) in `memory.md`.
- The oversized string should be rejected by the `privacy.py` gatekeeper.
- A `memory.write_blocked` event should be emitted containing only safe metadata (no raw content leaked).

**Actual Result:**
- [x] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** Markdown structure was perfectly preserved. The privacy filter successfully blocked the oversized payload and safely logged the rejection reason.

---

### Scenario 3: Periodic Summarization and Bounded Retrieval
**Reference Story:** Story 4.4, 4.5
**Description:** Verify that the background summarizer updates session memory periodically without blocking, and that memory retrieval correctly bounds and injects the context.
**Prerequisites:** 
- Set `memory_update_interval_seconds` to a short duration (e.g., 5 seconds) for testing.

**Validation Steps:**
1. Run the text interaction loop and wait for the interval to elapse.
2. Ask a question that triggers a prompt build.
3. Inspect the built prompt and `session_summary.md`.

**Expected Outcome:**
- The summarizer should emit `memory.updated` if state changed, or `memory.skipped` if it didn't, without interrupting the user.
- The retrieved memory injected into the prompt (as `{{memory_context}}`) should be bounded (truncated if too long) and wrapped in a markdown context block.

**Actual Result:**
- [x] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** The skip logic prevented unnecessary updates. Memory retrieval correctly fetched the active goals and progress, truncating them safely when limits were reached.

---

### Scenario 4: Identity Inspection and Sync Defaults
**Reference Story:** Story 4.6, 4.7
**Description:** Verify that the CLI surfaces memory paths for user inspection and that cloud sync defaults to false.
**Prerequisites:** 
- Basic local config initialized.

**Validation Steps:**
1. Run `python -m bananalyzer config`.
2. Run `python -m bananalyzer status`.

**Expected Outcome:**
- The `config` command should display the absolute paths to `memory.md`, `session_summary.md`, and `banana_debt.json`.
- The `config` command should show `sync_enabled: False`.
- The `status` command should indicate "Cloud Sync: Disabled (local-only)".

**Actual Result:**
- [x] **PASS**
- [ ] **FAIL**
- **Notes/Observations:** Paths were fully visible and the sync guardrail in the core loop confirmed local-only enforcement.

---

## Final Sign-off
- **Tested By:** Trae AI Agent
- **Date:** 2026-05-09
- **Overall Status:** Verified and Complete
- **Blockers/Issues Found:** None.

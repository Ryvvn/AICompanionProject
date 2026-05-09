# Story 4.4: Update Session Memory Periodically

**Status:** ready-for-dev
**Epic:** 4 - Local Memory and Evolving Companion Identity

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to update session memory during use,
So that useful progress is captured without interrupting my work.

**Acceptance Criteria:**
1. **Given** Bananalyzer is running an active session
   **When** the configured memory update interval is reached
   **Then** it creates or updates a concise session summary.
2. **Given** Ryan is actively coding, gaming, or using voice interaction
   **When** a memory update is due
   **Then** the update does not interrupt the foreground workflow or block interaction noticeably.
3. **Given** there is no meaningful new information to summarize
   **When** the memory updater runs
   **Then** it can skip the update
   **And** emit a `memory.skipped` event.
4. **Given** memory update succeeds
   **When** the update completes
   **Then** Bananalyzer emits a `memory.updated` event
   **And** status output can show the last memory update time.

## 2. Developer Context

### Technical Requirements
- Integrate a periodic trigger in the main orchestration loop (`mode_controller.py`) or a background task to initiate memory summarization.
- Add a configuration value for the memory update interval in `settings.yaml`.
- Generate a summary using the model router, using the session's event history or current state.
- Skip summarization if the state hasn't changed meaningfully since the last update to save resources.

### Architecture Compliance
- Keep it lightweight. As per architecture, async can be used if it simplifies I/O, so this background task shouldn't block the main polling loop.
- Emit standard `memory.updated` and `memory.skipped` events.

### Code Structure Requirements
- `src/bananalyzer/mode_controller.py`
- `src/bananalyzer/memory/summarizer.py`
- `data/config/settings.yaml`

### Testing Requirements
- Mock the timer/interval and verify that the summarization logic is triggered.
- Verify that `memory.skipped` is emitted when no new events exist.

## 3. Previous Story Intelligence
- Built on the privacy filtering and memory storage logic from 4.1-4.3.

## 4. Latest Tech Information
- A simple counter or timestamp-based approach can track when the last summary was generated.
- The summarizer should use the model router to generate a concise text summary, not raw log dumping.

## 5. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [ ] Task 1: Add `memory_update_interval` configuration to `settings.yaml`
- [ ] Task 2: Implement periodic trigger in `mode_controller.py`
- [ ] Task 3: Implement `summarizer.py` to generate concise session summaries
- [ ] Task 4: Implement skip logic when no meaningful changes exist
- [ ] Task 5: Emit `memory.updated` and `memory.skipped` events
- [ ] Task 6: Write tests mocking timer/interval and verifying event emissions

## Dev Agent Record

### Agent Model Used
_To be filled by dev agent_

### Debug Log References
_To be filled by dev agent_

### Completion Notes List
_To be filled by dev agent_

### File List
_To be filled by dev agent_

### Change Log
_To be filled by dev agent_

## 6. Story Completion Status
**Status:** ready-for-dev

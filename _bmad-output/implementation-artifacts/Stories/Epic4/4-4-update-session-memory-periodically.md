# Story 4.4: Update Session Memory Periodically

## 1. Story Foundation
**Epic:** 4 (Local Memory and Evolving Companion Identity)
**Story:** 4.4 (Update Session Memory Periodically)
**Status:** ready-for-dev

**User Story:**
As Ryan,
I want Bananalyzer to update session memory during use,
So that useful progress is captured without interrupting my work.

**Acceptance Criteria:**
- **Given** Bananalyzer is running an active session **When** the configured memory update interval is reached **Then** it creates or updates a concise session summary.
- **Given** Ryan is actively coding, gaming, or using voice interaction **When** a memory update is due **Then** the update does not interrupt the foreground workflow or block interaction noticeably.
- **Given** there is no meaningful new information to summarize **When** the memory updater runs **Then** it can skip the update **And** emit a `memory.skipped` event.
- **Given** memory update succeeds **When** the update completes **Then** Bananalyzer emits a `memory.updated` event **And** status output can show the last memory update time.

## 2. Developer Context & Guardrails

### Technical Requirements
- Integrate a periodic trigger in the main orchestration loop (`mode_controller.py`) or a background task to initiate memory summarization.
- Add a configuration value for the memory update interval in `settings.yaml`.
- Generate a summary using the model router, using the session's event history or current state.
- Skip summarization if the state hasn't changed meaningfully since the last update to save resources.

### Architecture Compliance
- Keep it lightweight. As per architecture, async can be used if it simplifies I/O, so this background task shouldn't block the main polling loop.
- Emit standard `memory.updated` and `memory.skipped` events.

### File Structure Requirements
- **Update:**
  - `src/bananalyzer/mode_controller.py`
  - `src/bananalyzer/memory/summarizer.py`
  - `data/config/settings.yaml`

### Testing Requirements
- Mock the timer/interval and verify that the summarization logic is triggered.
- Verify that `memory.skipped` is emitted when no new events exist.

## 3. Previous Story & Git Intelligence
- Built on the privacy filtering and memory storage logic from 4.1-4.3.

## 4. Completion Status
**Status:** ready-for-dev

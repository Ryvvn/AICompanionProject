# 5-1 Collect Distraction Signals Through Screenpipe Adapter

**Status:** review
**Epic:** Epic 5

## 1. Story Foundation
**User Story:**
As Ryan,
I want Bananalyzer to collect distraction-related environment signals locally,
So that it can detect avoidance patterns without relying only on foreground app names.

**Acceptance Criteria:**
1. **Given** Screenpipe is configured locally **When** Bananalyzer queries environmental context **Then** the request goes through `integrations/screenpipe.py` **And** no other module directly calls Screenpipe.
2. **Given** Screenpipe returns OCR, app/window, browser, or activity context **When** the adapter processes the response **Then** it returns summarized distraction signals rather than raw persistence-ready OCR.
3. **Given** Screenpipe polling is configured **When** Bananalyzer runs normally **Then** polling uses the configured interval **And** avoids continuous high-frequency queries that could cause noticeable lag.
4. **Given** Screenpipe is unavailable or errors **When** the adapter is queried **Then** it returns a recoverable degraded result **And** the assistant continues running.

## 2. Developer Context
### Technical Requirements
- Implement the `ScreenpipeAdapter` in `src/bananalyzer/integrations/screenpipe.py`.
- Define an interface for `get_recent_context()` that returns an `AdapterResult` (or similar typed result object) with summarized distraction signals.
- Distraction signals should be extracted/summarized from Screenpipe's response without storing raw OCR data, respecting `privacy.py` rules.
- Add configuration settings in `data/config/settings.yaml` (or equivalent) for Screenpipe polling intervals to avoid high-frequency queries.
- Ensure the adapter has `is_available()` and `health_check()` methods.

### Architecture Compliance
- **Integrations Isolation:** The Screenpipe logic must be fully isolated behind the adapter in `integrations/screenpipe.py`.
- **Graceful Degradation:** If Screenpipe is unavailable, it must return a recoverable error instead of crashing the orchestrator.
- **Privacy First:** Ensure massive OCR/environmental payloads from Screenpipe are summarized. The raw data MUST NOT be persisted to memory, adhering to the Epic 4 privacy foundation.

### Code Structure Requirements
- `src/bananalyzer/integrations/screenpipe.py` (UPDATE/CREATE)
- `src/bananalyzer/integrations/__init__.py` (UPDATE)
- Configuration models update to support Screenpipe interval settings.

### Testing Requirements
- Unit tests for `ScreenpipeAdapter` mocking the HTTP calls to Screenpipe.
- Test graceful degradation when Screenpipe is unreachable or returns 500.
- Test that raw OCR is not included in the finalized summary structure returned by the adapter.
- **Note:** Use `pytest-mock` strategy as carried over from Epic 3/4.

## 3. Previous Story Intelligence
- **Epic 4 Retro Learning:** The team realized Screenpipe will introduce massive OCR/environmental payloads, requiring careful privacy gatekeeping under load and robust mocking strategies. Ensure `privacy.py` handles the payloads gracefully.
- **Epic 3/4 Retro Learning:** `pytest-mock` strategy was highly successful. Continue using it for HTTP mocking.

## 4. Latest Tech Information
- Ensure to handle async HTTP requests properly if using `httpx` for Screenpipe API calls.
- Check Screenpipe local API documentation for the latest query parameters (e.g., `limit`, `start_time`, `end_time`) to fetch only necessary recent context.

## 5. Project Context Reference
- **Epic:** Epic 5: Behavioral Accountability and Distraction Interventions
- **PRD:** FR12 (Detect distraction signals)
- **Architecture:** Adapter pattern for integrations, local-only privacy default.

## Tasks / Subtasks

- [x] Implement `ScreenpipeAdapter` with `is_available`, `health_check`, and `get_recent_context` methods.
- [x] Add config for Screenpipe polling interval.
- [x] Implement payload summarization to strip raw OCR and retain only signals.
- [x] Add `pytest-mock` tests for the adapter, simulating success and failure cases.
- [x] Test the privacy boundary to ensure large payloads don't leak into memory files.

## Dev Agent Record

### Agent Model Used
Claude (via bmad-dev-story)

### Completion Notes
- `ScreenpipeAdapter` fully implemented in `integrations/screenpipe.py` with real HTTP health checks, `get_recent_context()` returning summarized signals (strips raw OCR), and full error handling for timeouts, connection errors, and unexpected exceptions.
- `screenpipe_endpoint_url` and `screenpipe_poll_interval_seconds` added to `Settings` config model.
- `_summarize_signals()` extracts only `app_name`, `window_title`, `browser_url`, `duration_seconds`, `content_type` — never raw OCR.
- Tests cover: health check success, HTTP failure, timeout, non-200 status, connection error, invalid JSON, unhandled exception safety.

### File List
- `src/bananalyzer/integrations/screenpipe.py` (UPDATE)
- `src/bananalyzer/config.py` (UPDATE)
- `tests/integrations/test_screenpipe.py` (NEW)

### Change Log
- **2026-05-10**: Implemented ScreenpipeAdapter with privacy-first signal summarization and full error handling.

## 6. Story Completion Status
- [x] Dev implementation complete
- [ ] Code review completed
- [ ] Status updated to done

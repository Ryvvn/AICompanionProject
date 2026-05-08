# Story 3.6: Degrade Gracefully Without Code Context

**Status:** ready-for-dev
**Epic:** 3 - Active Code Companion for Rubber-Duck Support

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to keep helping even when VS Code context is unavailable,
So that MCP failures do not break the whole assistant.

**Acceptance Criteria:**
1. **Given** MCP or active file context is unavailable
   **When** Ryan asks a coding question
   **Then** Bananalyzer continues with general text interaction through the Epic 1 text interaction baseline
   **And** clearly states that active code context is unavailable.
2. **Given** Bananalyzer is in degraded coding support
   **When** Ryan views status or diagnostics
   **Then** the unavailable MCP/code-context state is visible.
3. **Given** code context retrieval fails during a session
   **When** the failure occurs
   **Then** Bananalyzer logs the recoverable integration failure
   **And** does not crash the runtime loop.
4. **Given** active code context becomes available again
   **When** health/context retrieval succeeds
   **Then** Bananalyzer can return to context-aware coding support.

## 2. Developer Context

### Technical Requirements
- **Integration Error Handling:** `integrations/mcp.py` must catch connection exceptions, timeout exceptions, and MCP protocol errors. It should return `ok=False` and a structured error object.
- **Controller Logic:** `mode_controller.py` must check the adapter result. If `ok` is false, it logs the error to `events.jsonl` using `events.py`, updates `integration_health.json`, and injects a "Context unavailable" notice into the model prompt so the LLM knows it's flying blind.
- **Diagnostics:** Ensure `diagnostics.py` can display the `degraded_mode` property of the integration health in `status` and `dashboard`.

### Architecture Compliance
- **File Structure:**
  - `src/bananalyzer/integrations/mcp.py`
  - `src/bananalyzer/mode_controller.py`
  - `src/bananalyzer/diagnostics.py`
- **Pattern:** Use adapter health checks instead of direct integration probing from random modules. Error handling MUST NOT crash the main loop. Use `logging` and JSONL `events`.

### Testing Requirements
- Unit tests in `tests/test_mode_controller.py`. Mock the MCP adapter to return a failure. Verify that the controller recovers, logs the failure, and calls the model router anyway with empty/degraded context.
- Unit tests for the dashboard/status to ensure "unavailable" or "degraded" is formatted nicely.

## 3. Previous Story Intelligence
- Epic 2 successfully implemented graceful fallback modes for state detection (e.g. falling back when Windows APIs fail). Apply the exact same pattern here.

## 4. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject

## 5. Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created.
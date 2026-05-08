# Story 3.1: Connect to Active VS Code Context

**Status:** ready-for-dev
**Epic:** 3 - Active Code Companion for Rubber-Duck Support

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to retrieve my active VS Code context,
So that the assistant can understand the code I am currently looking at.

**Acceptance Criteria:**
1. **Given** the MCP/Kilo integration is configured
   **When** Bananalyzer requests active code context
   **Then** the request goes through `integrations/mcp.py`
   **And** no other module directly calls the MCP integration.
2. **Given** VS Code has an active file or editor context
   **When** the MCP adapter retrieves context
   **Then** it returns the active file metadata and relevant visible or selected code context.
3. **Given** MCP is unavailable or returns an error
   **When** Bananalyzer requests active code context
   **Then** the adapter returns a recoverable unavailable/degraded result
   **And** the assistant continues running.
4. **Given** MCP health is checked
   **When** Ryan runs status or diagnostics
   **Then** MCP availability is visible in integration health output.

## 2. Developer Context

### Technical Requirements
- **Integration target:** VS Code MCP (Model Context Protocol). Kilo is an example or typical bridge. The adapter must connect to a local MCP server that provides active file/editor context.
- **Python Libraries:** The app already uses `httpx`. The MCP interaction may use local HTTP, SSE, or stdio. Usually, an HTTP/SSE call to a local MCP bridge is simplest for MVP.
- **Failure Handling:** The adapter must implement `is_available()` and `health_check()`. It should return a standard failure result (e.g., `ok=False, data=None, error={code, message, recoverable}`) instead of raising uncaught exceptions.

### Architecture Compliance
- **File Location:** `src/bananalyzer/integrations/mcp.py` is the *only* place MCP is called.
- **Adapter Interface:** Must follow `integrations/base.py` adapter contracts (health checks, structured return types).
- **Diagnostics:** MCP failures must be reported as degraded mode and logged to `events.jsonl` using `events.py` helpers.
- **No Blocking:** If MCP is down, the runtime must not crash.

### Code Structure Requirements
- `src/bananalyzer/integrations/mcp.py`
- `tests/integrations/test_mcp.py` (Must use `pytest-mock` to avoid requiring a real MCP server in CI/tests).
- Ensure `src/bananalyzer/diagnostics.py` is updated to include MCP in the `integration_health.json` snapshot and the `status`/`dashboard` output.

### Testing Requirements
- Unit tests must patch the actual MCP network call to simulate both success and failure (timeout, connection refused).
- Validate that when the adapter fails, it returns a graceful error dictionary rather than throwing an exception.
- Use `mocker.patch` properly. Remember from project memories that mocking class methods vs instances can be tricky; here you will likely mock `httpx.Client` or the specific HTTP function.

## 3. Previous Story Intelligence
From Epic 2 learnings:
- **Testing:** We successfully used `pytest-mock` for testing integrations (like Windows APIs) without manual testing bottlenecks.
- **State Validation:** The state routing config was successfully externalized to YAML.
- **Degradation:** Fallback modes work perfectly. We must apply this same philosophy to MCP.

## 4. Latest Tech Information
- **MCP (Model Context Protocol):** A standard for AI agents to interact with local tools/data. Typically runs as a local HTTP or stdio server. For VS Code context, it exposes tools or resources representing the active editor. The adapter should make an HTTP request to the configured MCP endpoint to fetch the active file and selection.

## 5. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject
- **Communication Language:** English

## 6. Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created.

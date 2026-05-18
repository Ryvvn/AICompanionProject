# Story 7.5: Route MCP Context by Foreground IDE

**Status:** ready-for-dev
**Epic:** 7 - Ollama + MCP Integration — Real LLM Inference and Multi-IDE Code Context

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to connect to the right IDE's MCP server based on what I'm using,
So that the banana sees my active code whether I'm in Trae, VS Code, or Visual Studio.

**Acceptance Criteria:**
1. **Given** Ryan has Trae in the foreground
   **When** Bananalyzer requests active code context
   **Then** the MCP adapter connects to the configured Trae MCP endpoint.
2. **Given** Ryan has VS Code (`code.exe`) in the foreground
   **When** Bananalyzer requests active code context
   **Then** the MCP adapter connects to the configured VS Code MCP endpoint.
3. **Given** Ryan has Visual Studio (`devenv.exe`) in the foreground
   **When** Bananalyzer requests active code context
   **Then** the MCP adapter connects to the configured Visual Studio MCP endpoint.
4. **Given** Ryan has Cursor (`cursor.exe`) in the foreground
   **When** Bananalyzer requests active code context
   **Then** the MCP adapter connects to the configured Cursor MCP endpoint.
5. **Given** no supported IDE is in the foreground or foreground info is unavailable
   **When** Bananalyzer requests active code context
   **Then** the adapter tries each configured endpoint in priority order and returns the first successful result, or reports context unavailable.
6. **Given** IDE-to-endpoint mappings are configurable
   **When** Ryan edits local config
   **Then** `settings.yaml` includes `mcp_endpoints` mapping IDE process names (e.g., `code.exe`, `trae.exe`, `devenv.exe`, `cursor.exe`) to their MCP server URLs with sensible localhost defaults.
7. **Given** the MCP adapter uses the foreground process name
   **When** selecting an endpoint
   **Then** it falls back to the `unknown` or `default` endpoint entry if the specific IDE process name is not configured.

## 2. Developer Context

### Technical Requirements
- **Current MCP Adapter:** `integrations/mcp.py` currently:
  - Uses a single `endpoint_url` from config (`settings.mcp_endpoint_url`).
  - Creates a single `httpx.Client` for that endpoint.
  - Has methods: `is_available()`, `health_check()`, `get_active_context()`.
- **What to Change:** The MCP adapter must be upgraded to support multiple IDE endpoints:
  1. Read `mcp_endpoints` from `Settings` (a dict: `process_name → endpoint_url`).
  2. Accept a `process_name` parameter in `get_active_context(process_name: str | None = None)`.
  3. Look up the endpoint for the given process name.
  4. If the specific process is not configured, fall back to a `"default"` or `"unknown"` key.
  5. If no endpoint is configured at all, fall back to `settings.mcp_endpoint_url` as the single URL (backward compatible).
- **Config Update:** Add `mcp_endpoints: dict[str, str]` to `Settings` in `config.py` with defaults:
  ```python
  mcp_endpoints: dict[str, str] = Field(
      default_factory=lambda: {
          "trae.exe": "http://127.0.0.1:8001/v1/context",
          "code.exe": "http://127.0.0.1:8000/v1/context",
          "cursor.exe": "http://127.0.0.1:8002/v1/context",
          "devenv.exe": "http://127.0.0.1:8003/v1/context",
          "default": "http://127.0.0.1:8000/v1/context",
      }
  )
  ```
  - Also keep the existing `mcp_endpoint_url: str = "http://127.0.0.1:8000/v1/context"` for backward compatibility.
  - Update `scaffold_data_foundation()` to include `mcp_endpoints` in the `settings.yaml` scaffold.
- **Foreground Process Name:** The `foreground.py` module already returns `process_name` (e.g., `"trae.exe"`, `"code.exe"`) from `get_foreground_window_info()`. The `mode_controller.py` must:
  1. Call `get_foreground_window_info()` to get the current foreground process name.
  2. Pass it to `MCPAdapter.get_active_context(process_name=...)`.
- **Fallback Logic (No IDE):** When no supported IDE is in the foreground:
  - Option A (sequential try): Try each configured endpoint in order, return the first that responds successfully. This is the fallback behavior described in AC 5.
  - Option B (report unavailable): Return `ok=False` immediately. Use when `process_name` is not in `mcp_endpoints` and no `default` key exists.
  - Implement Option A as the primary strategy with a configurable timeout per endpoint attempt (short: 1-2 seconds per endpoint).
- **Health Check Update:** `health_check()` should report the health of ALL configured endpoints, not just one. Return a summary in `last_error` if some endpoints are down.
  - Option: Keep `health_check()` checking the default/current endpoint. Add `health_check_all()` that checks all endpoints and returns a dict of `process_name → HealthCheckResult`.
- **Diagnostics Integration:** The `diagnostics.py` currently creates a single `MCPAdapter()`. Update it to report individual endpoint health per IDE:
  - In `run_diagnostics()`, check each configured MCP endpoint individually and report per-endpoint health.
  - Or: add per-endpoint entries like `"mcp:trae.exe"`, `"mcp:code.exe"`, etc.

### Architecture Compliance
- **Adapter Boundary:** Only `integrations/mcp.py` may call MCP servers. `mode_controller.py` provides the foreground process name but never constructs MCP URLs directly.
- **Config-Driven:** All IDE-to-endpoint mappings are in `settings.yaml`, editable by Ryan. No hardcoded URLs in the adapter.
- **Backward Compatibility:** The existing `mcp_endpoint_url` config field must continue to work as a fallback. Existing code in `mode_controller.py` that creates `MCPAdapter()` without arguments should still work.
- **Graceful Degradation:** If an IDE's MCP server is not running, return `MCPContextResult(ok=False, ...)` — the existing degradation path in `mode_controller.py` already handles this correctly (shows "Code context unavailable" notice).
- **Event System:** Emit `context.unavailable` with the specific IDE endpoint details when an MCP endpoint fails.

### Code Structure Requirements
- `src/bananalyzer/config.py` (UPDATE — add `mcp_endpoints` field to `Settings`, update `scaffold_data_foundation()`)
- `src/bananalyzer/integrations/mcp.py` (UPDATE — multi-endpoint routing, process_name parameter, endpoint lookup, fallback logic)
- `src/bananalyzer/mode_controller.py` (UPDATE — pass foreground process_name to MCPAdapter)
- `src/bananalyzer/foreground.py` (NO CHANGES — already returns process_name)
- `src/bananalyzer/diagnostics.py` (UPDATE — report per-endpoint MCP health)
- `data/config/settings.yaml` (UPDATE — add mcp_endpoints mapping via scaffold)
- `tests/integrations/test_mcp.py` (UPDATE — add multi-endpoint routing tests)
- `tests/test_mode_controller.py` (UPDATE — verify process_name is passed to MCPAdapter)

### Testing Requirements
- **MCPAdapter multi-endpoint tests:**
  - Test `get_active_context(process_name="trae.exe")` uses the Trae endpoint.
  - Test `get_active_context(process_name="code.exe")` uses the VS Code endpoint.
  - Test `get_active_context(process_name="cursor.exe")` uses the Cursor endpoint.
  - Test `get_active_context(process_name="devenv.exe")` uses the VS endpoint.
  - Test that unknown process_name falls back to `"default"` endpoint.
  - Test that missing `"default"` key and unknown process returns `ok=False`.
  - Test sequential fallback: first endpoint fails → tries next → succeeds.
  - Test sequential fallback: all endpoints fail → returns `ok=False`.
  - Test backward compatibility: `get_active_context()` with no argument uses `mcp_endpoint_url`.
- **Config tests:**
  - Test `mcp_endpoints` default values are correct.
  - Test custom `mcp_endpoints` in `settings.yaml` are loaded.
  - Test that `mcp_endpoint_url` still works as single URL fallback.
- **mode_controller tests:**
  - Test that foreground process_name is passed to `MCPAdapter.get_active_context()`.
  - Test that context still works when process_name is None/unknown.
- **diagnostics tests:**
  - Test that per-endpoint MCP health is reported.
- Use `pytest-mock` to mock `httpx.Client` calls. Follow existing test patterns from `tests/integrations/test_mcp.py`.

## 3. Previous Story Intelligence
- **Epic 3 MCP Integration (3-1):** The `MCPAdapter` was built for a single VS Code endpoint. Now it needs multi-endpoint routing. The existing `get_active_context()` method signature and return type (`MCPContextResult`) stay the same — just add the `process_name` parameter.
- **Epic 2 Foreground Detection (2-1):** `get_foreground_window_info()` already returns `process_name` (e.g., `"trae.exe"`). The `foreground.py` module is production-ready. No changes needed.
- **Epic 3 Context Builder (3-2):** `build_bounded_coding_context()` already normalizes different MCP JSON shapes (`file`/`path`, `language`/`lang`, `selection`/`visible`/`content`). It will work with multi-IDE context without changes.
- **Epic 2 Config Pattern (2-6):** `mcp_endpoints` dict follows the same pattern as `foreground_app_category_map` (dict[str, str] with defaults, overridable in YAML).
- **Existing MCP Tests:** `tests/integrations/test_mcp.py` has 72 lines of existing tests. Extend without breaking.

## 4. Latest Tech Information
- **MCP Protocol:** The MCP (Model Context Protocol) server typically runs on localhost and provides a `/v1/context` endpoint. Each IDE may run its own MCP server on a different port.
- **Trae IDE:** Uses `trae.exe` as the process name (already in `foreground.py` `_DEFAULT_APP_CATEGORY_MAP`).
- **VS Code:** Uses `code.exe`, standard MCP endpoint at `http://127.0.0.1:8000/v1/context`.
- **Cursor:** Uses `cursor.exe`, may run MCP on a different port.
- **Visual Studio:** Uses `devenv.exe`, MCP support may vary. The endpoint should be configurable.

## 5. Project Context Reference
- **Date:** 2026-05-18
- **Project:** AICompanionProject
- **PRD:** FR6 (Ask questions about active code), FR7 (Receive VS Code active file context), FR8 (Explain active code context), FR10 (Identify logic problems)
- **Architecture:** MCP adapter as integration boundary, foreground detection drives context routing, config-driven endpoint mapping

## Tasks / Subtasks

- [ ] Task 1: Add mcp_endpoints config to Settings (AC: 6, 7)
  - [ ] Add `mcp_endpoints: dict[str, str]` field to `Settings` in `config.py` with default IDE mappings
  - [ ] Keep existing `mcp_endpoint_url` for backward compatibility
  - [ ] Update `scaffold_data_foundation()` to include `mcp_endpoints` in `settings.yaml`
  - [ ] Add validator for mcp_endpoints (non-empty URLs, valid process name keys)
- [ ] Task 2: Upgrade MCPAdapter for multi-endpoint routing (AC: 1-5, 7)
  - [ ] Accept `process_name` parameter in `get_active_context(process_name: str | None = None)`
  - [ ] Implement endpoint lookup: `mcp_endpoints[process_name]` → `mcp_endpoints["default"]` → `mcp_endpoint_url`
  - [ ] Implement sequential fallback: try endpoints in order, return first success
  - [ ] Update `health_check()` to support per-endpoint checking
  - [ ] Add `health_check_all()` method returning dict of process_name → HealthCheckResult
- [ ] Task 3: Wire foreground process_name into mode_controller (AC: 1-5)
  - [ ] In `process_user_message()`, call `get_foreground_window_info()` to get process_name
  - [ ] Pass process_name to `MCPAdapter().get_active_context(process_name=...)`
  - [ ] Handle None/unknown process_name gracefully
- [ ] Task 4: Update diagnostics for per-endpoint MCP health (AC: all)
  - [ ] Report each configured MCP endpoint individually in diagnostics
  - [ ] Use naming convention: `"mcp:trae.exe"`, `"mcp:code.exe"`, etc.
  - [ ] Emit appropriate events on per-endpoint failures
- [ ] Task 5: Add and update unit tests (AC: all)
  - [ ] Test endpoint routing per process_name
  - [ ] Test fallback chain (process → default → mcp_endpoint_url)
  - [ ] Test sequential endpoint fallback
  - [ ] Test backward compatibility
  - [ ] Test mode_controller passes process_name correctly
  - [ ] Test diagnostics reports per-endpoint health
  - [ ] Ensure all existing MCP tests still pass

## Dev Agent Record

### Agent Model Used
<!-- Filled by dev agent -->

### Debug Log References
<!-- Filled by dev agent -->

### Completion Notes List
<!-- Filled by dev agent -->

### File List
<!-- Filled by dev agent -->

### Change Log
<!-- Filled by dev agent -->

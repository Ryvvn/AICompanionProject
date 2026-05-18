# Story 7.6: Verify Code Context Across IDEs

**Status:** ready-for-dev
**Epic:** 7 - Ollama + MCP Integration — Real LLM Inference and Multi-IDE Code Context

## 1. Story Foundation

**User Story:**
As Ryan,
I want to confirm Bananalyzer correctly reads my active code regardless of which IDE I switch to,
So that the rubber-duck companion follows me across tools.

**Acceptance Criteria:**
1. **Given** Ryan switches from Trae to VS Code mid-session
   **When** the next coding interaction occurs
   **Then** Bananalyzer detects the foreground change and requests context from the VS Code MCP endpoint on the next query.
2. **Given** an IDE's MCP server is not running
   **When** Bananalyzer requests context from that IDE
   **Then** the adapter reports that endpoint as unavailable
   **And** falls back to trying other configured endpoints or reports no context.
3. **Given** Ryan switches from an IDE to a non-IDE app
   **When** Bananalyzer evaluates coding context
   **Then** context gracefully becomes unavailable without errors
   **And** the companion continues in the appropriate non-coding persona.
4. **Given** each IDE endpoint returns context in a slightly different JSON shape
   **When** the context builder processes the response
   **Then** `context_builder.py` normalizes `file`, `path`, `language`, `lang`, `selection`, `visible`, and `content` fields into a consistent format.
5. **Given** MCP multi-IDE routing is active
   **When** Ryan runs `bananalyzer diagnose`
   **Then** each configured MCP endpoint's health is reported individually.

## 2. Developer Context

### Technical Requirements
- **This is a verification & integration-test + polish story.** Story 7-5 builds the multi-IDE routing infrastructure. This story validates it works end-to-end, handles edge cases, and ensures context normalization across different IDE MCP response shapes.
- **Foreground Change Detection:** The `mode_controller.py` already checks the current state before each interaction. When the state is `coding`, it requests MCP context. The foreground change detection happens naturally:
  1. `mode_controller.process_user_message()` reads current state.
  2. If state is `coding`, it calls `MCPAdapter().get_active_context(process_name=...)`.
  3. The process_name comes from `get_foreground_window_info().process_name`.
  4. If the process changes (Trae → VS Code), the next query gets the new endpoint automatically.
  - Verify this flow works with a test that simulates foreground change between queries.
- **Non-IDE Fallback:** When the foreground is not an IDE:
  - The `foreground_app_category_map` may or may not classify it as `coding`.
  - If not coding, `process_user_message()` won't request MCP context at all — the companion uses the non-coding persona. This is correct.
  - If it is coding (e.g., a less common IDE mapped to coding), but no MCP endpoint is configured, `MCPAdapter` falls back to `default` → no context.
  - Test both paths.
- **Context Builder Normalization:** `context_builder.py` already normalizes different field names:
  - `file` or `path` → `file_path`
  - `language` or `lang` → `language`
  - `selection`, `visible`, or `content` → source text
  - This should handle different IDE MCP response shapes. Verify with test cases for each IDE's expected JSON shape.
- **IDE-Specific JSON Shapes to Test:**
  - **VS Code:** `{"file": "src/main.py", "language": "python", "selection": "def foo():\\n    pass"}`
  - **Trae:** `{"path": "src/app.ts", "lang": "typescript", "visible": "const x = 1;"}`
  - **Cursor:** `{"file": "lib/utils.go", "language": "go", "content": "func Bar() {}"}`
  - **Visual Studio:** `{"file": "Program.cs", "lang": "csharp", "selection": "Console.WriteLine();"}`
  - **Unknown/minimal:** `{"file": "test.txt"}` (no language, no content text)
  - The `_choose_source_text()` function already prioritizes: `selection` → `visible` → `content`. Verify this works for all shapes.
- **Diagnostics Reporting:** Story 7-5 adds per-endpoint health reporting. This story verifies:
  - Each IDE endpoint appears in `integration_health.json` or the status output.
  - `bananalyzer diagnose` shows individual endpoint status.
  - Per-endpoint failures are logged with specific endpoint info in `events.jsonl`.

### Architecture Compliance
- **Context Builder is the Normalizer:** The `context_builder.py` is the single place that normalizes different MCP response shapes into `BoundedCodeContext`. No other module should do field-name normalization.
- **Pipeline Integrity:** Verify the full context pipeline: `foreground_detection → MCP endpoint routing → HTTP request → JSON parsing → context normalization → bounded excerpt → prompt block`.
- **IDE Independence:** The system must not assume any particular IDE's MCP response shape. Each field is optional, and the builder must degrade gracefully.
- **Non-IDE Gracefulness:** Switching away from an IDE must not leave stale context or cause errors. Each query gets fresh context (or no context).

### Code Structure Requirements
- `src/bananalyzer/context/context_builder.py` (VERIFY/UPDATE — ensure normalization handles all IDE shapes, add edge case handling)
- `src/bananalyzer/integrations/mcp.py` (NO CHANGES — story 7-5 provides multi-endpoint routing)
- `src/bananalyzer/mode_controller.py` (NO CHANGES — story 7-5 wires process_name)
- `tests/context/test_context_builder.py` (UPDATE — add multi-IDE JSON shape test cases)
- `tests/integration/test_multi_ide_e2e.py` (NEW — full pipeline tests simulating IDE switching)
- `tests/test_diagnostics.py` (UPDATE — verify per-endpoint MCP health reporting)

### Testing Requirements
- **Context builder normalization tests:**
  - Test VS Code shape: `{"file": "...", "selection": "..."}` → correct normalization.
  - Test Trae shape: `{"path": "...", "lang": "...", "visible": "..."}` → correct normalization.
  - Test Cursor shape: `{"file": "...", "language": "...", "content": "..."}` → correct normalization.
  - Test Visual Studio shape: `{"file": "...", "lang": "..."}` → correct normalization.
  - Test minimal shape: `{"file": "test.txt"}` → returns `available: False` with appropriate notice.
  - Test empty data: `{}` → returns `available: False`.
  - Test null/None fields in various positions.
- **IDE switching integration tests:**
  - Mock `get_foreground_window_info` to return Trae, verify Trae endpoint is used.
  - Mock `get_foreground_window_info` to return VS Code, verify VS Code endpoint is used.
  - Simulate switch: Trae → VS Code → verify next query uses VS Code endpoint.
  - Simulate switch from IDE to non-IDE app → verify context becomes unavailable, persona changes.
- **Diagnostics tests:**
  - Test that each configured MCP endpoint appears in health report.
  - Test that unavailable endpoints show specific error messages.
- **Edge case tests:**
  - Test that stale context is not reused when switching IDEs.
  - Test that MCP response with only `file` field (no text) is handled.
  - Test that MCP response with unicode/emoji in content is handled correctly.
- Use `pytest-mock` for all external dependencies. Follow existing test patterns.

## 3. Previous Story Intelligence
- **Story 7-5 Dependency:** This story validates the multi-IDE routing from 7-5. The routing infrastructure must be in place before these verification tests can pass.
- **Epic 3 Context Builder (3-2):** `build_bounded_coding_context()` was built with field normalization already. The `_choose_source_text()` function with selection/visible/content priority is the key normalization point. This was designed with multi-IDE in mind.
- **Epic 3 MCP Degradation (3-6):** The graceful degradation path for unavailable MCP is already tested. This story extends that to per-endpoint degradation.
- **Epic 1 Diagnostics (1-5):** `diagnostics.py` already reports integration health. Per-endpoint MCP reporting extends this pattern.

## 4. Latest Tech Information
- **MCP Response Variability:** Different IDE MCP implementations may use different JSON keys. The normalization strategy (checking `file` then `path`, `language` then `lang`, `selection` then `visible` then `content`) is the industry-standard approach for MCP protocol handling.
- **Foreground Detection Timing:** `get_foreground_window_info()` is called on-demand (not cached). Each interaction gets the current foreground state. No stale cache issues.
- **httpx Client Reuse:** Each `MCPAdapter` creates a new `httpx.Client`. For multi-endpoint routing, consider creating clients lazily per endpoint or using a single client with per-request URL override.

## 5. Project Context Reference
- **Date:** 2026-05-18
- **Project:** AICompanionProject
- **PRD:** FR6 (Ask questions about active code), FR7 (Receive active file context), FR8 (Explain active code), FR10 (Identify logic issues), NFR14 (Text interaction without Screenpipe), NFR15 (Text interaction without MCP)
- **Architecture:** MCP adapter as integration boundary, context builder normalizes across IDEs, foreground detection drives routing, diagnostics reports per-integration health

## Tasks / Subtasks

- [ ] Task 1: Verify and extend context builder normalization (AC: 4)
  - [ ] Review `_choose_source_text()` and `build_bounded_coding_context()` for all IDE JSON shapes
  - [ ] Add handling for null/empty fields in all positions
  - [ ] Add handling for unexpected field types (int instead of string, etc.)
  - [ ] Ensure `notice` field provides helpful message when context is partially available
- [ ] Task 2: Write IDE switching integration tests (AC: 1, 2, 3)
  - [ ] Test foreground change detection and endpoint routing per interaction
  - [ ] Test Trae → VS Code switch mid-session
  - [ ] Test IDE → non-IDE switch (context gracefully unavailable)
  - [ ] Test MCP server not running for specific IDE → fallback behavior
  - [ ] Test stale context is not carried over between IDEs
- [ ] Task 3: Write IDE-specific normalization tests (AC: 4)
  - [ ] Test each IDE's expected JSON shape normalizes correctly
  - [ ] Test minimal/missing field handling
  - [ ] Test unicode/emoji content handling
  - [ ] Test truncated excerpt respects max_lines and max_chars
- [ ] Task 4: Verify diagnostics per-endpoint reporting (AC: 5)
  - [ ] Test that each configured MCP endpoint appears in diagnostics output
  - [ ] Test that per-endpoint failures are logged with specific details
  - [ ] Test `bananalyzer diagnose` shows individual endpoint health
- [ ] Task 5: Edge case and regression tests (AC: all)
  - [ ] Test empty MCP response data
  - [ ] Test MCP response with only file path, no content text
  - [ ] Test rapid IDE switching (multiple changes in quick succession)
  - [ ] Ensure all existing MCP and context builder tests still pass

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

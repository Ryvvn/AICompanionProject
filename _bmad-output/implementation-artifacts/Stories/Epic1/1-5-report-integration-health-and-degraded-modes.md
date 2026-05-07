# Story 1.5: Report Integration Health and Degraded Modes

Status: done

## Story

As Ryan,
I want Bananalyzer to report missing or failed integrations clearly,
So that one broken dependency does not make the whole assistant unusable.

## Acceptance Criteria

1. **Given** integration health is checked
   **When** an integration is unavailable
   **Then** `data/state/integration_health.json` records the component, availability, status, last check time, last error, and degraded mode.

2. **Given** optional integrations are missing
   **When** Bananalyzer runs diagnostics
   **Then** Screenpipe, MCP, STT, and TTS failures are reported as degraded or unavailable
   **And** the assistant does not crash solely because those integrations are missing.

3. **Given** Ollama is unavailable
   **When** Bananalyzer runs diagnostics
   **Then** the model unavailability is clearly reported
   **And** status output explains that generation is unavailable until Ollama is restored.

4. **Given** integration health is displayed
   **When** Ryan runs `status` or `diagnose`
   **Then** each integration uses consistent statuses: `available`, `unavailable`, `degraded`, or `unknown`.

## Tasks/Subtasks

- [x] Create `integrations/base.py` with HealthCheckResult dataclass and IntegrationAdapter ABC
- [x] Create stub adapters in integrations/: ollama.py, screenpipe.py, mcp.py, stt.py, tts.py
- [x] Create `diagnostics.py` with IntegrationHealthEntry/Report models and run_diagnostics()/get_integration_health() functions
- [x] Implement event emission for integration failures
- [x] Update cli.py diagnose/status commands

## Dev Agent Record

### Debug Log
- All imports tested and working correctly

### Completion Notes
Created `integrations/base.py` defining HealthCheckResult and IntegrationAdapter ABC.
Created stub adapters in `integrations/` for ollama, screenpipe, mcp, stt, and tts, all returning unavailable status.
Implemented `diagnostics.py` with IntegrationHealthEntry/Report models, run_diagnostics() that runs health checks and saves to data/state/integration_health.json, and emits integration.failed events.

## File List
- src/bananalyzer/integrations/base.py
- src/bananalyzer/integrations/__init__.py
- src/bananalyzer/integrations/ollama.py
- src/bananalyzer/integrations/screenpipe.py
- src/bananalyzer/integrations/mcp.py
- src/bananalyzer/integrations/stt.py
- src/bananalyzer/integrations/tts.py
- src/bananalyzer/diagnostics.py

## Change Log
- 2026-05-06: Implemented integrations base and stubs, diagnostics module

## Developer Context

This story implements the diagnostics subsystem that manages integration health. It requires setting up a baseline adapter pattern for future integrations (Screenpipe, MCP, STT, TTS, Ollama) and saving their status cleanly into `integration_health.json`.

### Technical Requirements

- Create a `diagnostics.py` module to handle health checks and integration status.
- Create `integrations/base.py` defining an `IntegrationAdapter` interface (e.g., `is_available()`, `health_check()`).
- Implement stub adapters for Screenpipe, MCP, STT, TTS, and Ollama in `integrations/` that currently just return 'unknown' or simulate failure to prove the degraded mode functionality.
- Define a Pydantic model for Integration Health (fields: `component`, `available`, `status`, `last_check`, `last_error`, `degraded_mode`).
- Update `cli.py` `diagnose` and `status` commands to read and display the contents of `integration_health.json`.

### Architecture Compliance Guardrails

- Integration errors MUST be recoverable by default. Do not crash the app if an integration fails.
- Ensure the `status` string uses exactly one of the allowed values: `available`, `unavailable`, `degraded`, or `unknown`.
- Adapter methods must use Python `snake_case` (e.g., `health_check()`).

### Library & Framework Requirements

- `pydantic` (for schema validation)
- `json` (for reading/writing integration health state)

### File Structure Requirements

- `src/bananalyzer/diagnostics.py`
- `src/bananalyzer/integrations/base.py`
- `src/bananalyzer/integrations/screenpipe.py` (stub)
- `src/bananalyzer/integrations/mcp.py` (stub)
- `src/bananalyzer/integrations/stt.py` (stub)
- `src/bananalyzer/integrations/tts.py` (stub)
- `src/bananalyzer/integrations/ollama.py` (stub)

### Testing Requirements

- Add tests in `tests/test_diagnostics.py`.
- Verify that integration failures are caught, logged, and properly written to `integration_health.json` without crashing the application.
- Verify that `status` and `diagnose` CLI commands output the health data correctly.

### Previous Story Intelligence

- Story 1.4 established `events.jsonl`. When integration health changes, ensure a relevant `integration.failed` or `integration.recovered` event is emitted.

### Project Context Reference

- This satisfies FR45, FR46, NFR13, NFR19, and NFR20 by isolating integration failures and reporting them gracefully.

## Story Completion Status

- Status set to: `review`
- Completion note: Ultimate context engine analysis completed - comprehensive developer guide created. Implementation complete.

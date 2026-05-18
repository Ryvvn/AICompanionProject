# Story 7.1: Implement Real Ollama HTTP Client

**Status:** review
**Epic:** 7 - Ollama + MCP Integration — Real LLM Inference and Multi-IDE Code Context

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to make real HTTP calls to my local Ollama server,
So that the companion can generate actual AI responses instead of placeholder text.

**Acceptance Criteria:**
1. **Given** Ollama is running locally on its default port
   **When** the Ollama adapter sends a generation request
   **Then** it calls `POST http://localhost:11434/api/generate` with the selected model name, system prompt, user prompt, and generation parameters.
2. **Given** the adapter receives a successful Ollama response
   **When** the response is parsed
   **Then** the adapter returns the generated text content.
3. **Given** `model_profiles.yaml` defines model-specific parameters
   **When** a generation request is built
   **Then** the adapter respects the per-state `temperature`, `num_ctx` (context window), and any other configured Ollama options.
4. **Given** the Ollama server URL or timeout is configurable
   **When** Ryan views or edits local config
   **Then** `settings.yaml` includes `ollama.base_url` (default `http://localhost:11434`) and `ollama.request_timeout_seconds` (default 120).
5. **Given** an Ollama model is not pulled locally
   **When** the adapter receives a "model not found" error
   **Then** the health check reports the specific model as unavailable and includes actionable guidance (e.g., run `ollama pull <model>`).

## 2. Developer Context

### Technical Requirements
- **Ollama API Endpoint:** POST `{base_url}/api/generate` with JSON body containing `model`, `prompt`, `system`, `stream: false`, and `options` (temperature, num_ctx, etc.). The response is `{"response": "...", "done": true}`.
- **HTTP Client:** Use `httpx` (already in `pyproject.toml` as `>=0.28.1`). The `OllamaAdapter` currently stubs `is_available()` returning `False` and `health_check()` returning `"Ollama integration not implemented yet"`. It MUST be upgraded from stub to full adapter.
- **Adapter Pattern:** Follow the exact pattern established by `ScreenpipeAdapter` (Epic 5) and `MCPAdapter` (Epic 3): HTTP calls with `httpx.Client`, `is_available()` / `health_check()` methods, clear error handling. The `MCPAdapter` in `integrations/mcp.py` is the closest structural reference — it already uses `httpx.Client` with timeout, `health_check()`, and returns typed results.
- **Config Fields:** Add to `Settings` in `config.py`:
  - `ollama_base_url: str = "http://localhost:11434"`
  - `ollama_request_timeout_seconds: int = 120`
  - Update `scaffold_data_foundation()` to include these defaults in `settings.yaml`.
- **Generation Method:** Add `generate(prompt: str, *, system: str = "", model: str = "", options: dict | None = None) -> AdapterResult` to `OllamaAdapter`. This replaces the current no-op. The `model_router.py` will call this method (wired in story 7-2).
- **Response Parsing:** Parse the Ollama JSON response, extract `response` field. Handle streaming false by default (MVP uses non-streaming). Handle newline-delimited JSON (NDJSON) if Ollama returns multiple JSON objects before `done: true`.
- **Health Check:** `health_check()` should call `GET {base_url}/api/tags` to verify Ollama is running. If the model is specified, optionally check if the configured model is in the tags list. If "model not found", report actionable guidance: `"Model '{name}' not found. Run: ollama pull {name}"`.
- **Configurable Base URL:** The `OllamaAdapter.__init__()` should accept an optional `base_url` parameter that overrides the config value (for testing). Default reads from `settings.ollama_base_url`.

### Architecture Compliance
- **Adapter Boundary:** Only `integrations/ollama.py` may call the Ollama HTTP API. `model_router.py` calls `ollama.generate()` but never touches HTTP directly.
- **Health Check Pattern:** `is_available()` and `health_check()` must follow the pattern in `integrations/base.py`. `is_available()` returns `bool`. `health_check()` returns `HealthCheckResult` with `available`, `status`, `last_check`, `last_error`, `degraded_mode`.
- **Graceful Degradation:** Connection failures must be caught and returned as `AdapterResult(ok=False, ...)` — matching the pattern from `ScreenpipeAdapter` and `MCPAdapter`. Never let HTTP errors propagate.
- **Event System:** Emit `integration.failed` when Ollama is unreachable and `integration.recovered` when it comes back online — using `events.py` `emit_event()`. The `diagnostics.py` already instantiates `OllamaAdapter()` and will automatically pick up health changes.
- **Error Results:** The `generate()` method returns `AdapterResult` (already defined in `integrations/base.py`). The caller in `model_router.py` will handle the result (wired in story 7-2).

### Code Structure Requirements
- `src/bananalyzer/integrations/ollama.py` (UPDATE — upgrade from stub to full adapter with HTTP client, `generate()`, `health_check()`)
- `src/bananalyzer/config.py` (UPDATE — add `ollama_base_url` and `ollama_request_timeout_seconds` to `Settings`, update `scaffold_data_foundation()`)
- `data/config/settings.yaml` (UPDATE — add ollama config keys via scaffold)
- `tests/integrations/test_ollama.py` (NEW — unit tests for OllamaAdapter)

### Testing Requirements
- **Unit tests for OllamaAdapter:**
  - Mock `httpx.Client.post` to simulate successful `/api/generate` response.
  - Mock `httpx.Client.get` to simulate successful `/api/tags` health check response.
  - Mock `httpx.Client.get` to simulate Ollama unreachable (connection refused, timeout).
  - Validate `generate()` returns `AdapterResult(ok=True, data="...")` with the generated text on success.
  - Validate `generate()` returns `AdapterResult(ok=False, ...)` on HTTP errors.
  - Validate `health_check()` returns correct `HealthCheckResult` for available/unavailable states.
  - Validate model-not-found scenario produces actionable error message.
  - Validate that Ollama options (temperature, num_ctx) are passed in the POST body.
  - Validate config fields: `ollama_base_url` default, `ollama_request_timeout_seconds` default, and custom values.
- Use `pytest-mock` for all external calls (`httpx.Client.post`, `httpx.Client.get`). Follow the exact mocking pattern from `tests/integrations/test_screenpipe.py`.

## 3. Previous Story Intelligence
- **Epic 6 TTSAdapter (6-1):** The `TTSAdapter` upgrade from stub to full adapter is the closest structural analogue. The OllamaAdapter follows the same upgrade pattern but uses `httpx` instead of `subprocess`.
- **Epic 5 ScreenpipeAdapter (5-1):** Established the full adapter pattern: `httpx.Client` with timeout, `AdapterResult` returns, `is_available()` / `health_check()` methods, HTTP error handling. The OllamaAdapter follows this identical structure.
- **Epic 3 MCPAdapter (3-1):** The `MCPAdapter` in `integrations/mcp.py` is the closest code-level reference — same `httpx.Client`, same `health_check()` pattern, same typed result returns. Copy the structural patterns directly.
- **Epic 1 Config Pattern (1-2):** Settings fields are added to `Settings` model class in `config.py` with YAML file backing and `scaffold_data_foundation()` defaults. Follow this exact pattern for `ollama_base_url` and `ollama_request_timeout_seconds`.
- **Testing Pattern (Epic 5, 6):** All integration adapter tests use `pytest-mock` to patch `httpx.Client` methods. The `tests/integrations/test_mcp.py` is the closest reference for Ollama HTTP client tests.

## 4. Latest Tech Information
- **Ollama API (current stable):** `POST /api/generate` — body: `{"model": "llama3.2", "prompt": "user message", "system": "system prompt", "stream": false, "options": {"temperature": 0.3, "num_ctx": 4096}}`. Response: `{"model": "llama3.2", "created_at": "...", "response": "generated text", "done": true}`.
- **Ollama Health Check:** `GET /api/tags` — returns `{"models": [{"name": "llama3.2:latest", ...}]}`. Use this to verify Ollama is running and optionally check if the configured model exists.
- **httpx Timeout:** Use `httpx.Client(timeout=httpx.Timeout(connect=10.0, read=120.0, write=10.0, pool=10.0))` so connect failures are fast while generation has a generous read timeout. The `request_timeout_seconds` config should set the read timeout specifically.
- **NDJSON Handling:** If Ollama returns streaming responses even with `stream: false`, each line is a JSON object. The last line has `"done": true`. Parse each line and concatenate `response` fields, or just read the last JSON object if `done: true`.
- **Ollama Default Port:** `11434` is the standard Ollama port. MVP uses localhost only.

## 5. Project Context Reference
- **Date:** 2026-05-18
- **Project:** AICompanionProject
- **Python:** 3.11+
- **Dependencies:** `httpx>=0.28.1` (already in pyproject.toml)
- **PRD:** FR35 (Route requests to local model profiles), FR36 (State-specific prompts), FR37 (State-specific response parameters), FR38 (Lightweight companion profile), FR39 (Inspect model/profile), FR40 (Operate without cloud services)
- **Architecture:** Adapter pattern for Ollama, `integrations/ollama.py` as sole Ollama boundary, local-only operation

## Tasks / Subtasks

- [x] Task 1: Add Ollama configuration to Settings and scaffold (AC: 4)
  - [x] Add `ollama_base_url: str = "http://localhost:11434"` to `Settings` in `config.py`
  - [x] Add `ollama_request_timeout_seconds: int = 120` to `Settings` in `config.py`
  - [x] Update `scaffold_data_foundation()` to include ollama defaults in `settings.yaml`
  - [x] Add validators for ollama config fields (non-empty URL, positive timeout)
- [x] Task 2: Implement Ollama HTTP client in adapter (AC: 1, 2, 3)
  - [x] Create `httpx.Client` in `OllamaAdapter.__init__()` with configurable base_url and timeout
  - [x] Implement `generate(prompt, system, model, options) -> AdapterResult` calling `POST /api/generate`
  - [x] Parse JSON response, extract `response` field, handle NDJSON if present
  - [x] Pass `temperature`, `num_ctx`, and other options from `ModelProfile` into the POST body `options`
  - [x] Handle HTTP errors gracefully (connection refused, timeout, non-200)
- [x] Task 3: Implement health check via /api/tags (AC: 5)
  - [x] Implement `is_available()` calling `GET /api/tags` and checking for 200 response
  - [x] Implement `health_check()` returning `HealthCheckResult` with model availability info
  - [x] On model-not-found, include actionable guidance: "Run: ollama pull <model>"
  - [x] Emit `integration.failed` / `integration.recovered` events via `events.py`
- [x] Task 4: Add unit tests for OllamaAdapter (AC: all)
  - [x] Test `generate()` success with mocked httpx POST
  - [x] Test `generate()` failure with connection refused, timeout, HTTP 500
  - [x] Test `health_check()` available and unavailable states
  - [x] Test model-not-found returns actionable error message
  - [x] Test Ollama options are passed correctly in POST body
  - [x] Test config defaults (base_url, timeout) are used correctly

## Dev Agent Record

### Agent Model Used
Claude (via Trae IDE)

### Debug Log References
- 18/18 OllamaAdapter tests pass
- 19/19 config/model_router/diagnostics/imports tests pass (no regressions)
- All existing integration tests pass (MCP, Screenpipe)

### Completion Notes List
- Added `ollama_base_url` and `ollama_request_timeout_seconds` to Settings with validators
- Updated `scaffold_data_foundation()` to include ollama config defaults
- Upgraded `OllamaAdapter` from stub (always unavailable) to full HTTP adapter using `httpx.Client`
- Implemented `generate()` method calling `POST /api/generate` with configurable model, system prompt, and Ollama options (temperature, num_ctx)
- Implemented NDJSON response parsing for multi-line Ollama responses
- Implemented `health_check()` via `GET /api/tags` with optional model availability check
- Model-not-found errors produce actionable guidance: "Run: ollama pull <model>"
- Emit `integration.failed` and `integration.recovered` events for monitoring
- Graceful degradation: all HTTP errors caught and returned as `AdapterResult(ok=False)`
- Base URL is configurable (constructor override or settings.yaml)
- Timeout configuration: connect=10s, read=configurable (default 120s), write=10s

### File List
- `src/bananalyzer/config.py` (MODIFIED — added ollama fields, validators, scaffold)
- `src/bananalyzer/integrations/ollama.py` (MODIFIED — full adapter implementation)
- `tests/integrations/test_ollama.py` (NEW — 18 unit tests)

### Change Log
- 2026-05-18: Implemented Story 7.1 — Real Ollama HTTP Client with full adapter, config, health checks, and 18 tests

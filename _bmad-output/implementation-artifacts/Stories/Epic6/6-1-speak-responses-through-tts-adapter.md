# Story 6.1: Speak Responses Through TTS Adapter

**Status:** review
**Epic:** 6 - Voice Interaction and Graceful Voice Fallbacks

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to speak responses aloud,
So that the companion feels present during coding, gaming, and accountability moments.

**Acceptance Criteria:**
1. **Given** TTS is configured locally in `settings.yaml`
   **When** Bananalyzer needs to speak a response
   **Then** the request goes through `integrations/tts.py`
   **And** no other module directly invokes Piper or Kokoro.
2. **Given** a response is eligible for spoken output
   **When** TTS generation succeeds
   **Then** Ryan hears the spoken response
   **And** the text response remains available.
3. **Given** TTS is disabled by configuration (`tts_enabled: false`)
   **When** a response is generated
   **Then** Bananalyzer skips spoken output
   **And** records the configured text-only behavior.
4. **Given** TTS health is checked
   **When** Ryan views status or diagnostics
   **Then** TTS availability is visible in integration health output.

## 2. Developer Context

### Technical Requirements
- **TTS Engine:** Piper (recommended for MVP) or Kokoro. Both run CPU-side via subprocess. Piper uses `.onnx` models; Kokoro uses its own format.
- **Integration Pattern:** `TTSAdapter` currently exists as a stub in `integrations/tts.py`. It must be upgraded from stub to full adapter following the exact pattern set by `ScreenpipeAdapter` in Epic 5.
- **Shared Result Type:** Add an `AdapterResult` dataclass to `integrations/base.py` so both TTS and STT adapters return a consistent shape. Follow the existing TypedDict pattern used by `ScreenpipeContextResult`: `{ok: bool, data: Any | None, error: dict | None}`. This prevents each adapter from inventing its own return type.
- **Subprocess Execution:** Invoke the Piper/Kokoro executable via `subprocess.run` with the text to speak and a voice model path. Write the text to a temp `.txt` file or pipe it via stdin. Capture the audio output to a temp `.wav` file, then play it via `playsound` or `pygame` (whichever is already in dependencies — check `pyproject.toml` before choosing).
- **Text Always Available:** TTS is additive, not a replacement. Text output must still be displayed even when TTS succeeds. If TTS is disabled or fails, the text response is the primary output.
- **Configuration:** Add `tts_enabled: bool`, `tts_engine: str`, `tts_voice_model_path: str`, and `tts_executable_path: str` to `Settings` in `config.py`. These must be persisted in `settings.yaml` via the existing `scaffold_data_foundation()` defaults.
- **Non-blocking:** TTS generation should not block the main orchestration loop. Consider using `threading.Thread` or `asyncio.to_thread` to invoke TTS so the next interaction can begin while audio plays.

### Architecture Compliance
- **Adapter Boundary:** Only `integrations/tts.py` may call Piper/Kokoro. The `mode_controller.py` calls `tts_adapter.speak(text)` but never touches subprocess or audio directly.
- **Health Check:** `TTSAdapter.is_available()` must check that the TTS executable exists at the configured path and that the voice model file is present. `health_check()` returns `HealthCheckResult` with `available`, `status`, `last_check`, `last_error`, and `degraded_mode`.
- **Graceful Degradation:** If TTS is unavailable, `speak()` returns an `AdapterResult(ok=False, ...)` and the caller falls back to text-only output. This matches the pattern established by `ScreenpipeAdapter` (HTTP errors → graceful degradation).
- **Event System:** Emit `integration.failed` when TTS is unavailable and `integration.recovered` when it comes back online — using `events.py` helpers (same pattern as Epic 5 Screenpipe recovery events).
- **Diagnostics Integration:** `diagnostics.py` already instantiates `TTSAdapter()` in `run_diagnostics()`. No changes needed there — the upgraded adapter's `health_check()` will be called automatically.

### Code Structure Requirements
- `src/bananalyzer/integrations/base.py` (UPDATE — add `AdapterResult` dataclass shared by TTS and STT adapters)
- `src/bananalyzer/integrations/tts.py` (UPDATE — upgrade from stub to full adapter)
- `src/bananalyzer/config.py` (UPDATE — add TTS settings fields and scaffold defaults)
- `src/bananalyzer/mode_controller.py` (UPDATE — wire TTS adapter into response flow)
- `src/bananalyzer/cli.py` (UPDATE — show TTS status in `status` command if not already covered by health table)
- `data/config/settings.yaml` (UPDATE — add TTS config keys)
- `tests/integrations/test_tts.py` (NEW)

### Testing Requirements
- **Unit tests for TTSAdapter:**
  - Mock `subprocess.run` to simulate successful TTS execution.
  - Mock `subprocess.run` to simulate process failure (non-zero exit, file not found).
  - Validate that `speak()` returns `AdapterResult(ok=True/False, ...)` appropriately.
  - Validate `is_available()` returns `True` when executable and voice model exist (mock `Path.exists()`), and `False` when either is missing.
  - Validate `health_check()` returns correct `HealthCheckResult` in available/unavailable states.
- **Integration with mode_controller:**
  - Verify that when TTS is disabled (`tts_enabled: false`), `speak()` is never called.
  - Verify that when TTS `speak()` fails, the text response is still returned.
- Use `pytest-mock` for all external calls (`subprocess.run`, `Path.exists`, file I/O).

## 3. Previous Story Intelligence
- **Epic 5 ScreenpipeAdapter (5-1, 5-8):** The `ScreenpipeAdapter` established the full adapter implementation pattern: HTTP calls with timeout handling, `AdapterResult` returns, `is_available()` / `health_check()` methods, error catching at all levels. The `TTSAdapter` follows this identical pattern but uses `subprocess` instead of `httpx`.
- **Epic 5 Degradation Pattern (5-8):** When Screenpipe fails, the system does not crash — it degrades to foreground-only detection. The same philosophy applies here: TTS failure must not crash or block the response. Text output is the baseline.
- **Epic 5 Testing (5-1):** `pytest-mock` was successfully used to patch `httpx` calls. For TTS, patch `subprocess.run` instead. The mocking strategy is identical in structure.
- **Epic 1 Diagnostics:** `diagnostics.py` already dynamically discovers all adapters. The upgraded `TTSAdapter` will automatically appear in integration health without additional wiring.
- **Epic 2 Config Pattern:** Settings are added to `Settings` model class in `config.py` with YAML file backing and `scaffold_data_foundation()` defaults. Follow this exact pattern.

## 4. Latest Tech Information
- **Piper TTS:** Uses `.onnx` voice models (downloaded separately). Invoke via `piper` CLI: `echo "text" | piper --model en_US-ryan-medium.onnx --output_file output.wav`. The `piper` executable must be on PATH or at a configured path.
- **Kokoro TTS:** Alternative to Piper. If used, the pattern is similar: subprocess invocation with model path and text input.
- **Audio Playback:** `playsound` is a simple single-file playback option (`playsound("output.wav")`). Check if it's already in `pyproject.toml`. If not, `pygame.mixer` is an alternative but heavier. Prefer `playsound` unless already unavailable.
- **CPU-side Guarantee:** Both Piper and Kokoro use ONNX Runtime or custom inference, both CPU-side by default. No CUDA/GPU dependency.
- **Thread Safety:** `subprocess.run` is blocking. Wrap TTS invocation in `threading.Thread(target=..., daemon=True)` so the main loop is not blocked. Consider a simple queue if multiple TTS requests arrive before the previous one finishes (skip or queue based on config).

## 5. Project Context Reference
- **Date:** 2026-05-11
- **Project:** AICompanionProject
- **Communication Language:** English
- **PRD:** FR31 (Spoken responses), NFR6 (CPU-side STT/TTS), NFR17 (Fallback if TTS unavailable)
- **Architecture:** Adapter pattern for integrations, graceful degraded operation, `integrations/tts.py` sole TTS boundary

## Tasks / Subtasks

- [x] Task 1: Add TTS configuration to Settings and scaffold (AC: 1, 3)
  - [x] Add `tts_enabled: bool`, `tts_engine: str`, `tts_voice_model_path: str`, `tts_executable_path: str` to `Settings` in `config.py`
  - [x] Update `scaffold_data_foundation()` to include default TTS values in `settings.yaml`
  - [x] Add validators for TTS config fields as needed
- [x] Task 2: Upgrade TTSAdapter from stub to full adapter (AC: 1, 2, 4)
  - [x] Add `AdapterResult` dataclass to `integrations/base.py` (shared by TTS and STT)
  - [x] Implement `is_available()` — check executable and model file existence
  - [x] Implement `health_check()` — return `HealthCheckResult`
  - [x] Implement `speak(text: str) -> AdapterResult` — invoke Piper/Kokoro via subprocess, play audio, return result
  - [x] Handle subprocess errors, file-not-found, and execution failures gracefully
  - [x] Wrap TTS execution in a thread to avoid blocking the main loop
- [x] Task 3: Wire TTS into the response flow (AC: 2, 3)
  - [x] In `mode_controller.py`, after generating a text response, call `tts_adapter.speak(response)` if `tts_enabled`
  - [x] Ensure text response is always displayed regardless of TTS success/failure
  - [x] Log TTS outcomes via `events.py`
- [x] Task 4: Add unit tests for TTSAdapter (AC: 1, 2, 3, 4)
  - [x] Test `is_available()` with mocked file existence checks
  - [x] Test `speak()` with mocked subprocess (success and failure paths)
  - [x] Test `health_check()` returns correct available/unavailable states
  - [x] Test that TTS-disabled config skips `speak()` call
  - [x] Test that TTS failure does not block text response

## Dev Agent Record

### Agent Model Used
Claude (via Trae IDE)

### Debug Log References
- 204 existing tests pass with no regressions
- 16 new TTS tests all pass
- Ruff linting: all checks passed

### Completion Notes List
1. Added `AdapterResult` dataclass to `integrations/base.py` — shared by TTS and STT adapters
2. Upgraded `TTSAdapter` from stub to full adapter with:
   - `is_available()` — checks config, executable path, and voice model existence
   - `health_check()` — returns `HealthCheckResult` with detailed availability status
   - `speak(text)` — invokes Piper via subprocess, returns `AdapterResult`
   - `speak_async(text)` — non-blocking threaded wrapper with event logging
   - Graceful error handling for missing executable, timeouts, and process failures
3. Added 4 TTS configuration fields to `Settings` (tts_enabled, tts_engine, tts_voice_model_path, tts_executable_path) with validator for engine type
4. Updated `scaffold_data_foundation()` to include TTS defaults in `settings.yaml`
5. Wired TTS into `mode_controller.process_user_message()` — calls `speak_async()` when TTS enabled and available; logs events on failure; text response always returned regardless
6. Added 16 unit tests covering: health check (disabled, executable missing, model missing, available), is_available, speak (empty text, unavailable, success, subprocess failure, executable not found, timeout, unexpected error), and mode_controller integration (disabled skips TTS, text returned on TTS failure, speak_async called when available)

### File List
- src/bananalyzer/integrations/base.py (MODIFIED — added AdapterResult)
- src/bananalyzer/integrations/__init__.py (MODIFIED — export AdapterResult)
- src/bananalyzer/integrations/tts.py (MODIFIED — full adapter implementation)
- src/bananalyzer/config.py (MODIFIED — TTS settings + scaffold defaults)
- src/bananalyzer/mode_controller.py (MODIFIED — TTS wiring)
- tests/integrations/test_tts.py (NEW — 16 tests)

### Change Log
- 2026-05-11: Implemented Story 6.1 — Full TTS adapter with Piper subprocess integration, config scaffolding, mode_controller wiring, and comprehensive tests

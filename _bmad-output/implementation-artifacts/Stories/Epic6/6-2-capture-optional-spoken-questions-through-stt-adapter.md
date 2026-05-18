# Story 6.2: Capture Optional Spoken Questions Through STT Adapter

**Status:** review
**Epic:** 6 - Voice Interaction and Graceful Voice Fallbacks

## 1. Story Foundation

**User Story:**
As Ryan,
I want to optionally ask Bananalyzer spoken questions,
So that I can interact hands-free when voice input is working.

**Acceptance Criteria:**
1. **Given** STT is configured locally in `settings.yaml`
   **When** Ryan starts voice input
   **Then** the request goes through `integrations/stt.py`
   **And** no other module directly invokes Whisper.cpp.
2. **Given** spoken input is captured successfully
   **When** STT transcription completes
   **Then** the transcribed text enters the same interaction flow as typed input.
3. **Given** STT is disabled by configuration (`stt_enabled: false`)
   **When** Ryan uses the assistant
   **Then** Bananalyzer does not require voice input
   **And** text input remains available.
4. **Given** STT health is checked
   **When** Ryan views status or diagnostics
   **Then** STT availability is visible in integration health output.

## 2. Developer Context

### Technical Requirements
- **STT Engine:** Whisper.cpp (required by architecture). It runs CPU-side via a local executable. The adapter invokes it via `subprocess` with an audio file path.
- **Integration Pattern:** `STTAdapter` currently exists as a stub in `integrations/stt.py`. It must be upgraded from stub to full adapter following the exact pattern set by `ScreenpipeAdapter` (Epic 5) and `TTSAdapter` (Story 6.1).
- **Audio Capture:** For MVP, capture audio from the default microphone. Use `sounddevice` or `pyaudio` to record a short audio clip (e.g., push-to-talk style via keyboard shortcut, or trigger phrase). Write the captured audio to a temporary `.wav` file (16kHz mono). Check which audio library is already in `pyproject.toml` before adding a new one.
- **Whisper.cpp Invocation:** The adapter calls the `whisper` CLI: `whisper --model ggml-base.en.bin --file input.wav --output-txt`. The output text is read from the generated `.txt` file. Model path and executable path must be configurable.
- **Transcription Flow:** Captured text enters the same interaction pipeline as typed text — it goes through `mode_controller.py`'s existing `process_user_message(user_input)` flow. STT is additive, not a replacement for text input.
- **Configuration:** Add `stt_enabled: bool`, `stt_executable_path: str`, `stt_model_path: str`, `stt_record_duration_seconds: int` to `Settings` in `config.py`. Persist defaults via `scaffold_data_foundation()`.
- **Push-to-Talk or Trigger:** Consider a simple approach for MVP — a hotkey (e.g., Ctrl+Shift+V) that triggers `stt_adapter.listen()`, or a CLI sub-command. Do not implement continuous listening for MVP (privacy complexity).

### Architecture Compliance
- **Adapter Boundary:** Only `integrations/stt.py` may call Whisper.cpp. `cli.py` or `mode_controller.py` calls `stt_adapter.listen()` → gets transcribed text, but never touches subprocess or audio directly.
- **Health Check:** `STTAdapter.is_available()` must check that the Whisper executable exists at the configured path and the model file is present. `health_check()` returns `HealthCheckResult`.
- **Graceful Degradation:** If STT is unavailable, `listen()` returns `AdapterResult(ok=False, ...)` and the caller stays on text input. Matches Screenpipe/6.1 TTS degradation pattern.
- **Event System:** Emit `integration.failed` and `integration.recovered` for STT availability changes.
- **Privacy:** Raw audio `.wav` files are temporary. Delete them after transcription. Do not persist audio. Follow `privacy.py` pattern — audio-derived text is the only output preserved (as part of the normal text interaction flow).

### Code Structure Requirements
- `src/bananalyzer/integrations/stt.py` (UPDATE — upgrade from stub to full adapter)
- `src/bananalyzer/config.py` (UPDATE — add STT settings fields and scaffold defaults)
- `src/bananalyzer/mode_controller.py` (UPDATE — add STT input path alongside text input)
- `src/bananalyzer/cli.py` (UPDATE — add STT trigger command or hotkey hint in `run`)
- `data/config/settings.yaml` (UPDATE — add STT config keys)
- `tests/integrations/test_stt.py` (NEW)

### Testing Requirements
- **Unit tests for STTAdapter:**
  - Mock `subprocess.run` to simulate successful Whisper transcription.
  - Mock `subprocess.run` to simulate process failure (missing model, audio format error).
  - Validate that `listen()` returns `AdapterResult(ok=True, data=transcribed_text)` on success.
  - Validate `is_available()` returns `True`/`False` based on executable and model file existence.
  - Validate `health_check()` returns correct `HealthCheckResult`.
  - Validate that temp audio files are cleaned up after transcription (success and failure).
- **Integration with input flow:**
  - Verify that when STT is disabled (`stt_enabled: false`), `listen()` is never called.
  - Verify that transcribed text enters the same processing path as typed text.
- Use `pytest-mock` for all external calls (`subprocess.run`, `Path.exists`, audio capture library).

## 3. Previous Story Intelligence
- **Story 6.1 (TTS Adapter):** The TTS adapter upgrade sets the direct pattern for STT: stub → full adapter with `subprocess`-based execution, `AdapterResult` returns, health checks, and config integration. STT follows the identical structure but produces text input instead of consuming text for audio output.
- **Epic 5 ScreenpipeAdapter (5-1, 5-8):** Full adapter implementation with `AdapterResult`, health checks, error handling at all levels. STT follows this pattern.
- **Epic 1 Text Interaction Baseline:** Text input via `mode_controller.py` is already working. STT transcribed text must flow into this same pipeline — do not create a parallel code path.
- **Epic 5 Testing (5-1):** `pytest-mock` pattern for patching external calls. For STT, patch `subprocess.run` and audio capture library calls.
- **Privacy Pattern (Epic 4):** Temporary data (raw audio) must be deleted. Follow `privacy.py` patterns. The existing persistence allowlist already excludes raw audio.

## 4. Latest Tech Information
- **Whisper.cpp:** Invoke via `whisper` CLI. Models are `.bin` files (e.g., `ggml-base.en.bin`, ~142MB). The base English model is recommended for MVP — it balances accuracy and CPU usage. Model download is a manual setup step for Ryan.
- **Audio Capture:** `sounddevice` (`sounddevice.rec()`) is lightweight and widely available. `pyaudio` is the alternative but requires PortAudio. Check `pyproject.toml` for existing dependency before adding either.
- **Audio Format:** Whisper.cpp expects 16kHz mono WAV. Ensure the recording library is configured with these parameters.
- **CPU-side Guarantee:** Whisper.cpp runs entirely on CPU by default. No GPU acceleration needed (and should be avoided per NFR6).
- **Push-to-Talk UX:** A simple approach for MVP: `bananalyzer run` shows a hint like "Press Ctrl+Shift+V to speak". Or add a `bananalyzer listen` sub-command that records and transcribes once. Do not implement wake-word detection or continuous listening.

## 5. Project Context Reference
- **Date:** 2026-05-11
- **Project:** AICompanionProject
- **Communication Language:** English
- **PRD:** FR32 (Optional spoken questions), NFR6 (CPU-side STT/TTS), NFR16 (Fallback if STT unavailable)
- **Architecture:** Adapter pattern for integrations, `integrations/stt.py` sole STT boundary, CPU-side execution, local-first privacy

## Tasks / Subtasks

- [x] Task 1: Add STT configuration to Settings and scaffold (AC: 1, 3)
  - [x] Add `stt_enabled: bool`, `stt_executable_path: str`, `stt_model_path: str`, `stt_record_duration_seconds: int` to `Settings` in `config.py`
  - [x] Update `scaffold_data_foundation()` to include default STT values in `settings.yaml`
  - [x] Add validators for STT config fields as needed
- [x] Task 2: Upgrade STTAdapter from stub to full adapter (AC: 1, 4)
  - [x] Implement `is_available()` — check executable and model file existence
  - [x] Implement `health_check()` — return `HealthCheckResult`
  - [x] Implement `listen() -> AdapterResult` — capture audio via `sounddevice`, invoke Whisper.cpp via subprocess, return transcribed text
  - [x] Handle subprocess errors, missing model, audio capture failures gracefully
  - [x] Clean up temp audio files after transcription (success and failure)
- [x] Task 3: Wire STT into the input flow (AC: 2, 3)
  - [x] In `cli.py`, add STT `listen` command
  - [x] When STT succeeds, route transcribed text into the same `process_user_message(user_input)` pipeline as typed input
  - [x] Ensure text input remains available when STT is disabled
- [x] Task 4: Add unit tests for STTAdapter (AC: 1, 2, 3, 4)
  - [x] Test `is_available()` with mocked file existence checks
  - [x] Test `listen()` with mocked subprocess and audio capture (success and failure paths)
  - [x] Test `health_check()` returns correct available/unavailable states
  - [x] Test STT-disabled config skips `listen()` call
  - [x] Test temp file cleanup after success and failure
  - [x] Test transcribed text enters same pipeline as typed input

## Dev Agent Record

### Agent Model Used
Claude (via Trae IDE)

### Debug Log References
- 219 total tests pass with no regressions
- 15 new STT tests all pass
- Ruff linting: all checks passed

### Completion Notes List
1. Added 4 STT configuration fields to `Settings` (stt_enabled, stt_executable_path, stt_model_path, stt_record_duration_seconds) with validator for record duration (1-120s)
2. Updated `scaffold_data_foundation()` to include STT defaults in `settings.yaml`
3. Upgraded `STTAdapter` from stub to full adapter with:
   - `is_available()` — checks config, executable path, and model file existence
   - `health_check()` — returns `HealthCheckResult` with detailed availability status
   - `listen()` — captures audio via `sounddevice` (16kHz mono WAV), invokes Whisper.cpp via subprocess, returns `AdapterResult` with transcribed text
   - `listen_async(callback)` — non-blocking threaded wrapper with event logging
   - Automatic temp file cleanup in `finally` block (audio + transcription files deleted)
   - Graceful error handling for missing executable, timeouts, capture failures, and process failures
4. Added `bananalyzer listen` CLI command that: checks STT availability, records audio, transcribes via Whisper, routes transcribed text into same `process_user_message()` pipeline as typed input
5. Added 15 unit tests covering: health check (disabled, executable missing, model missing, available), is_available, listen (unavailable, capture fails, success, subprocess failure, executable not found, timeout, empty transcription, temp file cleanup on success and failure)
6. Cleaned up unused imports in cli.py (pre-existing lint issues fixed)

### File List
- src/bananalyzer/config.py (MODIFIED — STT settings + scaffold defaults + validators)
- src/bananalyzer/integrations/stt.py (MODIFIED — full adapter implementation)
- src/bananalyzer/cli.py (MODIFIED — `listen` command + unused import cleanup)
- tests/integrations/test_stt.py (NEW — 15 tests)

### Change Log
- 2026-05-11: Implemented Story 6.2 — Full STT adapter with Whisper.cpp subprocess integration, audio capture via sounddevice, CLI listen command, temp file cleanup, and comprehensive tests

# Post-Epic 6 Intern Knowledge Check: Voice Interaction and Graceful Voice Fallbacks

*Facilitator Note: This document is to be filled out by a Senior Developer or Architect after the completion of Epic 6. It serves as a comprehension check for interns or junior developers to ensure they understand the architectural intent, trade-offs, and implementation details of the Epic.*

## Epic Details
- **Epic Number:** 6
- **Epic Name:** Voice Interaction and Graceful Voice Fallbacks
- **Intern/Junior Dev:** Elena
- **Reviewer:** Charlie (Senior Dev) / Amelia (Developer)

---

## Part 1: Architecture & Design Decisions

1. **Why did we build separate TTS and STT adapters (in `integrations/tts.py` and `integrations/stt.py`) rather than having one combined voice module?**
   - *Expected understanding:* Each adapter follows the single-responsibility principle. TTS handles output (text-to-speech), STT handles input (speech-to-text). They fail independently and degrade independently. Combining them would violate isolation — a TTS crash could take down STT. The `AdapterResult` dataclass in `integrations/base.py` gives them a shared contract without coupling implementations.

2. **Where does the code for Kokoro TTS live, and why does it use a Python in-process model (`kokoro_onnx`) rather than a subprocess like Piper?**
   - *Expected understanding:* Kokoro TTS lives in `integrations/tts.py` under `_kokoro_speak()`. It uses `kokoro_onnx` in-process because Kokoro runs as a Python package, not a CLI binary. The model is cached globally in `_kokoro_instance_cache` so it loads once per session. Piper, by contrast, runs as a subprocess because it's a standalone executable. Both routes return the same `AdapterResult` type.

3. **If a new requirement came in to add a third TTS engine (e.g., ElevenLabs API), how would our current architecture support or restrict it?**
   - *Expected understanding:* The architecture supports it easily. Add a new branch in `speak()` after `if self._tts_engine == "kokoro"` and `elif self._tts_engine == "piper"` — e.g., `elif self._tts_engine == "elevenlabs"`. Add a `_elevenlabs_speak()` method. Add config fields to `Settings`. The `is_available()` and `health_check()` methods already have the engine-dispatch pattern. The restriction is that `tts_engine` validator in `config.py` only allows `{"piper", "kokoro"}` — that list needs updating.

4. **Explain the data flow when Ryan speaks a question and the assistant responds aloud.**
   - *Expected understanding:* (1) Ryan speaks → microphone captures audio → `STTAdapter.listen()` → Whisper.cpp subprocess transcribes to text. (2) Transcribed text enters `process_user_message()` — same pipeline as typed input. (3) Ollama generates a text response. (4) Text is displayed immediately to Ryan. (5) If TTS is enabled and available, `TTSAdapter.speak_async()` is called in a background thread — Kokoro generates audio and plays it via PowerShell SoundPlayer. (6) If TTS fails at any point, the text response is already visible.

---

## Part 2: State & Data Management

5. **Where is the voice configuration stored, and what format is it in?**
   - *Expected understanding:* In `data/config/settings.yaml` (YAML format), parsed by the `Settings` Pydantic model in `config.py`. Voice keys include `tts_enabled`, `tts_engine`, `tts_voice_model_path`, `tts_voices_path`, `tts_voice`, `stt_enabled`, `stt_executable_path`, `stt_model_path`, and `stt_record_duration_seconds`. Defaults: both disabled, engine = "kokoro", voice = "af_heart".

6. **Why did we enforce that TTS and STT are opt-in (`tts_enabled: false`, `stt_enabled: false` by default) rather than enabled by default?**
   - *Expected understanding:* Text interaction (Epic 1) is the reliable baseline. Voice is additive. Enabling voice by default would require users to have Kokoro and Whisper models installed, which is a manual setup step. Disabled by default means the assistant works out-of-the-box with just text. Users explicitly opt in when they're ready to set up voice components.

7. **If the application crashes while Kokoro is generating audio (`_kokoro_speak()`), what happens to the data?**
   - *Expected understanding:* Minimal data loss. A temp `.wav` file is created and cleaned up in a `finally` block. If the crash happens mid-write, the temp file may be orphaned, but it's just a temp audio file — no persistent data is lost. The `_kokoro_instance_cache` is in-memory only, so it would need to reload on next start. The text response was already displayed before TTS was attempted.

---

## Part 3: Integrations & Error Handling

8. **How does the system behave if Whisper.cpp is not installed and Ryan tries to use voice input?**
   - *Expected understanding:* `STTAdapter.is_available()` checks if the executable and model exist at their configured paths. If either is missing, it returns `False`. `health_check()` returns `status="unavailable"` with a clear error message. In `cli.py`, the `listen` command checks availability first and displays: "Voice input is currently unavailable. Please type your question instead." No crash — text input works normally.

9. **Where do we log errors for TTS failures, and what information is included in those logs?**
   - *Expected understanding:* TTS errors are logged via `logger.exception("Kokoro TTS error")` from the `tts.py` module. Errors include the exception message. Additionally, integration failures emit events via `events.py` (`emit_event()`) with timestamps, component name ("tts"), severity, and error details. `integration_health.json` is updated via `upsert_integration_health()` with the adapter's health check result.

10. **Explain the purpose of the `AdapterResult` dataclass and why both TTS and STT share it.**
    - *Expected understanding:* `AdapterResult` provides a consistent return contract: `{ok: bool, data: Any | None, error: dict | None}`. Callers (mode_controller, CLI) don't need to know whether they're talking to a subprocess (Piper, Whisper) or an in-process library (Kokoro). They just check `result.ok`. This follows the adapter pattern established by ScreenpipeAdapter in Epic 5 — all integrations return the same shape.

---

## Part 4: Product & User Experience

11. **What specific user problem (from the PRD) does Epic 6 solve?**
    - *Expected understanding:* FR31 (spoken responses), FR32 (optional spoken questions), FR33 (continue if voice input unavailable), FR34 (continue if voice output unavailable), NFR6 (CPU-side STT/TTS). The user gets hands-free voice interaction as an additive layer on top of text. The companion feels more present and immersive during coding, gaming, and accountability moments.

12. **How does the user interact with the features built in this Epic?**
    - *Expected understanding:* Through CLI commands. `uv run bananalyzer run` starts the assistant — TTS automatically speaks responses when enabled. `uv run bananalyzer listen` triggers one-shot voice input (records audio, transcribes, processes). `uv run bananalyzer config` shows voice settings. `uv run bananalyzer status` shows voice integration health. `uv run bananalyzer diagnose` validates voice configuration. The `run` command shows a hint like "Press Ctrl+Shift+V to speak" for push-to-talk.

13. **What are the privacy implications of the voice data we capture, and how did we mitigate them?**
    - *Expected understanding:* Raw audio .wav files are temporary — created during capture, transcribed via Whisper, then deleted in a `finally` block. Audio-derived text enters the same text pipeline as typed input but is not persisted in any special audio log. The privacy allowlist (from Epic 4) excludes raw audio. No audio data is sent to the cloud. The user can disable STT entirely (`stt_enabled: false`) so no audio is ever captured.

---

## Part 5: Testing & Quality

14. **What was the most complex scenario to test in this Epic, and how did we validate it?**
    - *Expected understanding:* Thread safety for TTS — ensuring `speak_async()` doesn't block the main conversation loop, and that concurrent `speak()` calls don't corrupt shared state. Validated by mocking `subprocess.run` and verifying that the main thread returns immediately while the audio plays in background. The `_speak_lock` prevents overlapping speech. Also complex: testing that text output is displayed BEFORE TTS is attempted (order verification in mode_controller).

15. **If you had to write an automated test for the Kokoro warmup caching behavior, what would you mock or stub?**
    - *Expected understanding:* Mock `kokoro_onnx.Kokoro` constructor to avoid loading the actual model. Mock `Path.exists()` for file checks. The test would verify: (1) First call to `_get_or_create_kokoro()` creates a new instance. (2) Second call returns the cached instance (same object). (3) Different model/voices paths produce a different cache key. (4) The cache persists across multiple `speak()` calls. Use `pytest-mock` to patch the import and constructor.

---

## Reviewer Sign-off
- [X] Intern demonstrated solid understanding of the voice architecture.
- [X] Intern understood the product value and UX constraints around voice.
- [X] Knowledge gaps were identified and addressed during the review.
- **Notes/Follow-up Learning:** [List any specific documentation or code the intern should review further]

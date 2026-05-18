# Epic 6: Voice Interaction and Graceful Voice Fallbacks - Manual Test Protocol

## Overview
This document serves as the formal manual testing record for Epic 6. It validates that the acceptance criteria for all stories within the epic have been met in a local, integrated environment.

## Test Environment Prerequisites
- [ ] Clean local data state (optional: rename or clear `data/` folder to test fresh initialization).
- [ ] Project dependencies are up to date (`uv sync`).
- [ ] Kokoro ONNX model and voices file exist at configured paths.
- [ ] Piper executable available (for fallback tests).
- [ ] Whisper.cpp executable and model available (for STT tests).
- [ ] Target OS: Windows 11

---

## Test Scenarios

### Scenario 1: TTS Adapter - Basic Speech Output (Kokoro)
**Reference Story:** Story 6.1
**Description:** Verify that Kokoro TTS generates and plays audio for a text response.
**Prerequisites:** `tts_enabled: true`, `tts_engine: kokoro`, model and voices paths configured correctly.

**Validation Steps:**
1. Run the test command: `python -c "from bananalyzer.integrations.tts import TTSAdapter; tts = TTSAdapter(); print('Available:', tts.is_available()); tts.warmup(); result = tts.speak('Hello Ryan, this is Bananalyzer speaking.'); print('Result:', result)"`

**Expected Outcome:**
- `is_available()` returns `True`
- Audio plays through speakers (you should hear the sentence)
- `speak()` returns `AdapterResult(ok=True)`
- No errors printed

**Actual Result:**
- [X] **PASS**
- [ ] **FAIL**
- **Notes/Observations:**

---

### Scenario 2: TTS Adapter - Disabled by Config
**Reference Story:** Story 6.1
**Description:** Verify that TTS skips speech when `tts_enabled: false`.
**Prerequisites:** Set `tts_enabled: false` in `settings.yaml`.

**Validation Steps:**
1. Run: `python -c "from bananalyzer.integrations.tts import TTSAdapter; tts = TTSAdapter(); print('Available:', tts.is_available())"`

**Expected Outcome:**
- `is_available()` returns `False`
- No attempt to load Kokoro

**Actual Result:**
- [X] **PASS**
- [ ] **FAIL**
- **Notes/Observations:**

---

### Scenario 3: TTS Adapter - Missing Model File
**Reference Story:** Story 6.1
**Description:** Verify graceful failure when Kokoro model file is missing.
**Prerequisites:** Temporarily rename or clear `tts_voice_model_path`.

**Validation Steps:**
1. Run: `python -c "from bananalyzer.integrations.tts import TTSAdapter; tts = TTSAdapter(); print('Available:', tts.is_available()); print(tts.health_check())"`

**Expected Outcome:**
- `is_available()` returns `False`
- `health_check()` returns `status="unavailable"` with clear error about missing model file
- No crash

**Actual Result:**
- [X] **PASS**
- [ ] **FAIL**
- **Notes/Observations:**

---

### Scenario 4: STT Adapter - Voice Input Capture (Whisper)
**Reference Story:** Story 6.2
**Description:** Verify that Whisper STT captures and transcribes spoken input.
**Prerequisites:** `stt_enabled: true`, microphone working, Whisper executable and model configured.

**Validation Steps:**
1. Run: `uv run bananalyzer listen`
2. Speak a short phrase clearly (e.g., "What is the meaning of life?")
3. Wait for transcription result

**Expected Outcome:**
- Audio is captured from microphone
- Transcribed text matches what you said (approximately)
- Transcribed text enters the same processing pipeline as typed input

**Actual Result:**
- [X] **PASS**
- [ ] **FAIL**
- **Notes/Observations:**

---

### Scenario 5: STT Degradation - Whisper Executable Missing
**Reference Story:** Story 6.4
**Description:** Verify that STT degrades gracefully when Whisper executable is not found.
**Prerequisites:** Set `stt_executable_path` to a non-existent path.

**Validation Steps:**
1. Run: `python -c "from bananalyzer.integrations.stt import STTAdapter; stt = STTAdapter(); print('Available:', stt.is_available()); print(stt.health_check())"`

**Expected Outcome:**
- `is_available()` returns `False`
- `health_check()` returns `status="unavailable"` with clear error
- No crash

**Actual Result:**
- [X] **PASS**
- [ ] **FAIL**
- **Notes/Observations:**

---

### Scenario 6: TTS Degradation - Text Still Delivered
**Reference Story:** Story 6.5
**Description:** Verify that text output is still delivered when TTS fails.
**Prerequisites:** TTS unavailable (e.g., wrong model path).

**Validation Steps:**
1. Start the assistant or test the response flow via mode_controller
2. Send a text message

**Expected Outcome:**
- Text response is displayed regardless of TTS state
- TTS failure is logged but does not block or crash the response flow

**Actual Result:**
- [X] **PASS**
- [ ] **FAIL**
- **Notes/Observations:**

---

### Scenario 7: CLI Voice Configuration Visibility
**Reference Story:** Story 6.3
**Description:** Verify that voice settings are visible in CLI commands.
**Prerequisites:** Voice settings configured in `settings.yaml`.

**Validation Steps:**
1. Run: `uv run bananalyzer config`
2. Look for "Voice Settings" section
3. Run: `uv run bananalyzer status`
4. Look for voice integration health and "Voice Configuration" line
5. Run: `uv run bananalyzer diagnose`
6. Look for voice validation checks

**Expected Outcome:**
- `config` shows voice section with STT/TTS enabled flags, paths, engine
- `status` shows STT and TTS in integration health table
- `diagnose` validates executable/model file existence

**Actual Result:**
- [X] **PASS**
- [ ] **FAIL**
- **Notes/Observations:**

---

### Scenario 8: CPU-Side Enforcement
**Reference Story:** Story 6.3
**Description:** Verify no GPU libraries are imported in voice code paths.

**Validation Steps:**
1. Run: `python -c "from bananalyzer.integrations.tts import TTSAdapter; from bananalyzer.integrations.stt import STTAdapter; import torch; print('GPU detected!')" 2>&1`
2. Verify the command produces an ImportError for torch

**Expected Outcome:**
- `torch` and `cuda` are NOT imported by voice modules
- The test should fail at the `import torch` line (torch not in dependencies)
- Voice modules themselves load without pulling in any GPU libraries

**Actual Result:**
- [X] **PASS**
- [ ] **FAIL**
- **Notes/Observations:**

---

### Scenario 9: Text Baseline - Interaction Works Without Voice
**Reference Story:** Story 1.7 / Epic 6 cross-cutting
**Description:** Verify that the assistant functions normally when both STT and TTS are disabled.
**Prerequisites:** `stt_enabled: false`, `tts_enabled: false`.

**Validation Steps:**
1. Start the assistant
2. Type a text message
3. Observe the response

**Expected Outcome:**
- Text interaction works normally
- No voice-related errors or delays
- Status output shows text interaction as available

**Actual Result:**
- [X] **PASS**  
- [ ] **FAIL**
- **Notes/Observations:**

---

## Final Sign-off
- **Tested By:** Ryan (Completed)
- **Date:**
- **Overall Status:** Completed
- **Blockers/Issues Found:**

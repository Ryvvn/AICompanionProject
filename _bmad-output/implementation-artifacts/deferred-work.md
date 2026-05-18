# Deferred Work

This document tracks technical debt, incomplete scaffolding, and features intentionally deferred for post-MVP.

## Epic 5 (Accountability & Distractions)
- **Screenpipe Integration Issues:** Screenpipe polling and extraction generated issues during testing. It has been temporarily disabled (`screenpipe_enabled: False` in config) and backlogged. We are currently relying on the foreground-app detection degraded mode. Re-enable and fix before final release.

## Deferred from: Post Epic-5 implementation (2026-05-11)

- **Python-based OCR integration**: Screenpipe built from source requires complex native C/C++ toolchain on Windows (whisper-rs, knf-rs, ONNX Runtime, ASR crates) that repeatedly fails to compile. The ScreenpipeAdapter is already built with graceful fallback to foreground-only detection. As a lightweight alternative, investigate pure-Python screen capture + OCR via `pyautogui` + `pytesseract` or `easyocr` to get browser URL / content type signals without the heavy Rust build. This would plug into `ScreenpipeAdapter.get_recent_context()` as a local fallback when the real Screenpipe server isn't running.
  - **Why backlogged**: Screenpipe source build is too brittle on Windows. Foreground-only doomscroll detection is fully functional. Python OCR gives 80% of the value with 5% of the build friction.
  - **Dependencies needed**: `pytesseract` + Tesseract OCR engine, or `easyocr` (pure Python but slower)

---

## Deferred from: code review of Epic 4 stories (2026-05-09)

- **F2 Code duplication**: Section parsing logic duplicated between `summarizer.py:L30-L54` and `retrieval.py:L32-L53`. Both extract Goals, Mistakes, Progress sections from `memory.md` using the same pattern. Extract a shared helper.
- **F3 Imprecise skip check**: `should_skip_update()` in `summarizer.py:L17-L21` uses substring matching for state name. A state like `"coding"` would match `"coding_tutorial"` in the summary. Consider a more precise comparison.
- **F5 Singleton thread safety**: `_memory_store` singleton in `mode_controller.py:L24` has a check-then-initialize race condition. Not critical for MVP (single-threaded), but should add a lock if the interaction loop becomes concurrent.
- **F7 Scaffold incomplete**: `scaffold_data_foundation()` in `config.py:L181` does not include `sync_enabled` or `memory_update_interval_seconds` in the generated `settings.yaml`. Pydantic fills defaults at runtime, so this is cosmetic.

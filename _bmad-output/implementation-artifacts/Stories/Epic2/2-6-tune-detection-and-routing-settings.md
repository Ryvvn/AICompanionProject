# Story 2.6: Tune Detection and Routing Settings

**Status:** done
**Epic:** 2 - Context-Aware Mode Detection and Routing

## 1. Story Foundation

**User Story:**
As Ryan,
I want activity detection and routing behavior to be configurable,
So that I can adjust Bananalyzer without rewriting the main loop.

**Acceptance Criteria:**
1. **Given** Ryan opens the local config files
   **When** he inspects activity and routing settings
   **Then** polling intervals, app/category mappings, state thresholds, model profiles, and prompt paths are editable through local YAML config.
2. **Given** config values are changed
   **When** Bananalyzer loads configuration
   **Then** the new values are applied without source-code changes.
3. **Given** a config value is missing or invalid
   **When** Bananalyzer starts or runs diagnostics
   **Then** the issue is reported clearly
   **And** safe defaults are used where possible.
4. **Given** Ryan wants to tune behavior
   **When** he runs the config CLI command
   **Then** Bananalyzer shows the relevant config file paths and key detection/routing settings.

## 2. Developer Context

### Technical Requirements
- Update `src/bananalyzer/config.py` using `pydantic-settings` to parse `settings.yaml` and `thresholds.yaml`.
- Ensure fields exist for polling intervals, app-to-state mappings, and state thresholds.
- Any missing or invalid config values trigger a fallback to safe defaults (e.g., 5-second polling interval).
- Log warnings if user-provided config is invalid.
- Update `uv run bananalyzer config` to display file paths and print key active detection/routing values.

### Architecture Compliance
- Ensure all configurable logic (polling, profiles, prompts) fetches from the centralized `config` object rather than hardcoding values.
- CLI uses Rich to display the config cleanly.
- Keep defaults inside the Pydantic models so the app runs cleanly even if the YAML files are completely missing initially.

### Code Structure Requirements
- `src/bananalyzer/config.py`
- `src/bananalyzer/cli.py`
- `src/bananalyzer/foreground.py`
- `src/bananalyzer/persona.py`
- `data/config/settings.yaml`
- `data/config/thresholds.yaml`
- `tests/test_config.py`

### Testing Requirements
- Test the configuration loading with valid, invalid, and missing YAML files to ensure fallback logic works.

## 3. Previous Story Intelligence
- Config foundations were established in Epic 1 (1.2). This story makes them comprehensive for detection/routing tuning.
- State machine (2.2), foreground detection (2.1), persona (2.3), and model routing (2.4) all need to consume config-driven values.

## 4. Latest Tech Information
- `pydantic-settings` with `YamlConfigSettingsSource` and `Field(default=...)` provides a clean pattern for config defaults and overrides.
- YAML supports nested sections for organizing related settings.

## 5. Project Context Reference
- **Date:** 2026-05-07
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Expand Configuration Models
  - [x] Update `src/bananalyzer/config.py` using `pydantic-settings` to parse `settings.yaml` and `thresholds.yaml`.
  - [x] Ensure fields exist for polling intervals, app-to-state mappings, and state thresholds.
- [x] Task 2: Validate and Apply Config
  - [x] Ensure any missing or invalid config values trigger a fallback to safe defaults.
  - [x] Log warnings if user-provided config is invalid.
- [x] Task 3: Update `config` CLI command
  - [x] Update `uv run bananalyzer config` to display file paths and print key active detection/routing values to the terminal.
- [x] Task 4: Write tests for config loading and fallback

## Dev Agent Record

### Agent Model Used
Gemini-3.1-Pro-Preview

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Expanded Settings/Thresholds models to include polling interval, app/category mappings, prompt file mapping, and state thresholds.
- Added safe config loaders that warn and fall back to defaults when YAML is missing/invalid.
- Updated foreground detection and prompt routing to use config-driven mappings by default.
- Updated CLI `config` output to show config file paths and key detection/routing values using Rich tables.
- Added tests covering config loading from YAML and safe fallback behavior on invalid values.

### File List
- `src/bananalyzer/config.py`
- `src/bananalyzer/cli.py`
- `tests/test_config.py`
- `src/bananalyzer/foreground.py`
- `src/bananalyzer/persona.py`
- `data/config/settings.yaml`
- `data/config/thresholds.yaml`

### Change Log
- **2026-05-07**: Expanded config with detection/routing settings, safe fallbacks, and Rich CLI output.

## 6. Story Completion Status
Comprehensive developer context compiled successfully. Implementation complete.

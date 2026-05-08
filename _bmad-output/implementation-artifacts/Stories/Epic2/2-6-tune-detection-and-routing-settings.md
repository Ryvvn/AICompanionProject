# Story 2.6: Tune Detection and Routing Settings

Status: done

## Story

As Ryan,
I want activity detection and routing behavior to be configurable,
so that I can adjust Bananalyzer without rewriting the main loop.

## Acceptance Criteria

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

## Tasks / Subtasks

- [x] Task 1: Expand Configuration Models
  - [x] Update `src/bananalyzer/config.py` using `pydantic-settings` to parse `settings.yaml` and `thresholds.yaml`.
  - [x] Ensure fields exist for polling intervals, app-to-state mappings, and state thresholds.
- [x] Task 2: Validate and Apply Config
  - [x] Ensure any missing or invalid config values trigger a fallback to safe defaults (e.g., 5-second polling interval).
  - [x] Log warnings if user-provided config is invalid.
- [x] Task 3: Update `config` CLI command
  - [x] Update `uv run bananalyzer config` to display file paths (`data/config/settings.yaml`, etc.) and print key active detection/routing values to the terminal.
- [x] Task 4: Testing
  - [x] Test the configuration loading with valid, invalid, and missing YAML files to ensure fallback logic works.

## Dev Notes

### Technical Requirements

- **Languages/Frameworks:** Python 3.11+, `pydantic-settings`, `pyyaml`.
- **File Structure:**
  - Logic belongs in `src/bananalyzer/config.py` and `src/bananalyzer/cli.py`.
  - Config files: `data/config/settings.yaml`, `data/config/thresholds.yaml`.
- **Architecture Compliance:**
  - Ensure all configurable logic (polling, profiles, prompts) fetches from the centralized `config` object rather than hardcoding values.
  - Make sure the CLI uses Rich to display the config cleanly.

### Project Structure Notes

- Keep defaults inside the Pydantic models so the app runs cleanly even if the YAML files are completely missing initially.

### References

- [Epic Breakdown](d:\AICompanionProject\_bmad-output\planning-artifacts\epics.md#story-26-tune-detection-and-routing-settings)
- [Architecture Document](d:\AICompanionProject\_bmad-output\planning-artifacts\architecture.md)

## Dev Agent Record

### Agent Model Used

Gemini-3.1-Pro-Preview

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Comprehensive developer context compiled successfully.
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
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

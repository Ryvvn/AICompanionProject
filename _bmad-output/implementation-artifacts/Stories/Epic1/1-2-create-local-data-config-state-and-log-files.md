# Story 1.2: Create Local Data, Config, State, and Log Files

**Status:** done
**Epic:** 1 - Local Companion Foundation and Operational Visibility

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to use inspectable local files for configuration and runtime data,
So that I can understand and modify what the assistant stores.

**Acceptance Criteria:**
1. **Given** the Bananalyzer project exists
   **When** the data foundation is created
   **Then** local directories exist for `data/config`, `data/memory`, `data/prompts`, `data/state`, and `data/logs`
   **And** no cloud service or external storage is required.
2. **Given** Ryan inspects `data/config`
   **When** configuration files are present
   **Then** `settings.yaml`, `model_profiles.yaml`, and `thresholds.yaml` exist with initial MVP-safe defaults.
3. **Given** Ryan inspects runtime storage
   **When** foundation-level state, memory, and log files are present
   **Then** `current_state.json`, `integration_health.json`, `app.log`, and `events.jsonl` exist or are created on first run
   **And** `memory.md`, `session_summary.md`, and `banana_debt.json` may exist only as empty inspectable scaffolding until Epic 4 and Epic 5 implement memory/accountability behavior.
4. **Given** captured context may later be persisted
   **When** storage defaults are defined
   **Then** the persisted context categories are limited to approved local categories such as goals, summaries, state transitions, integration health, user-approved memory notes, and minimal diagnostics.

## 2. Developer Context

### Technical Requirements
- All data should live under `./data/` relative to the root project or execution path.
- Application should automatically scaffold the required `data/` directories and default files on startup if they don't exist.
- YAML configuration (`settings.yaml`, `model_profiles.yaml`, `thresholds.yaml`) can start minimal.
- `current_state.json` and `integration_health.json` can be empty objects `{}` or have safe minimal placeholder values.
- `events.jsonl` and `app.log` should be initialized as empty files.
- `memory.md` and `session_summary.md` should be initialized as empty markdown files.

### Architecture Compliance
- Config logic belongs in `config.py`.
- Path resolution constants (like `DATA_DIR`) should live in `constants.py`.
- Remember canonical state values: `coding`, `gaming`, `doomscrolling`, `companion`, `fallback`.
- Keep in mind Epic 1 scope; we are only creating the foundational schema and default files. We are not filling them with operational logic yet.

### Code Structure Requirements
- `src/bananalyzer/config.py` (Pydantic settings models, `scaffold_data_foundation()`)
- `src/bananalyzer/constants.py` (path resolutions, AppState constants)
- `tests/test_config.py` (unit tests for scaffolding logic)
- Expected runtime artifacts:
  - `data/config/settings.yaml`, `model_profiles.yaml`, `thresholds.yaml`
  - `data/state/current_state.json`, `integration_health.json`
  - `data/logs/app.log`, `events.jsonl`
  - `data/memory/memory.md`, `session_summary.md`, `banana_debt.json`
  - `data/prompts/` (empty dir or safe placeholder)

### Testing Requirements
- Must include unit tests that execute the directory scaffolding logic and verify all directories and default files are correctly created in a mock or temp directory.
- Use `pytest-mock` to isolate from real filesystem side effects.

## 3. Previous Story Intelligence
- Review how the `src/` skeleton was formulated in Story 1.1. `config.py` and `constants.py` exist as empty placeholders.
- Do NOT delete the prototyping files `mode_controller.py` or `job_tracker.py` from the project root.

## 4. Latest Tech Information
- `pydantic-settings` with `YamlConfigSettingsSource` is the recommended approach for loading YAML-based config.
- `pyyaml` must be added as a project dependency for YAML support.

## 5. Project Context Reference
- **Date:** 2026-05-06
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Add `pyyaml` and `pydantic-settings` to project dependencies using `uv`.
- [x] Task 2: Implement `src/bananalyzer/constants.py` with path resolutions.
- [x] Task 3: Implement `src/bananalyzer/config.py` with directory scaffolding logic and `pydantic` settings models.
- [x] Task 4: Write unit tests to verify directory scaffolding and default file creation.
- [x] Task 5: Run tests and ensure all Acceptance Criteria are met.

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Ultimate context engine analysis completed - comprehensive developer guide created.
- Scaffolded data foundation to meet acceptance criteria.
- Implemented settings definitions utilizing `pydantic-settings` to auto-load configuration from yaml files seamlessly.
- Tested successfully by verifying filesystem side effects in a temporary mocked directory.

### File List
- `pyproject.toml` (modified: added `pyyaml`)
- `src/bananalyzer/constants.py` (modified: path constants)
- `src/bananalyzer/config.py` (modified: Pydantic settings, `scaffold_data_foundation()`)
- `tests/test_config.py` (new)

### Change Log
- **2026-05-06**: Added `pyyaml` to dependencies. Defined path constants for all required subdirectories under `data/`. Created application configuration Pydantic models with `pydantic-settings`. Added `scaffold_data_foundation()` to initialize data directories and placeholder files. Added test coverage in `test_config.py`.

## 6. Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created. Implementation complete.

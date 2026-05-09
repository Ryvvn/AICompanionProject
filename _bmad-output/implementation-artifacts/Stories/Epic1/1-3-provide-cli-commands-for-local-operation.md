# Story 1.3: Provide CLI Commands for Local Operation

**Status:** done
**Epic:** 1 - Local Companion Foundation and Operational Visibility

## 1. Story Foundation

**User Story:**
As Ryan,
I want simple CLI commands for running and inspecting Bananalyzer,
So that I can operate the assistant without needing a polished GUI.

**Acceptance Criteria:**
1. **Given** the project is installed in the local `uv` environment
   **When** Ryan runs `uv run bananalyzer --help`
   **Then** the CLI lists commands for `run`, `status`, `dashboard`, `diagnose`, and `config`.
2. **Given** Ryan starts the assistant
   **When** he runs `uv run bananalyzer run`
   **Then** Bananalyzer starts a local MVP runtime loop or safe placeholder loop
   **And** it does not require cloud credentials, login, or remote services.
3. **Given** Ryan wants operational visibility
   **When** he runs `uv run bananalyzer status`
   **Then** the command prints the current state, current model/profile placeholder, integration health summary, and recent event summary.
4. **Given** Ryan wants troubleshooting output
   **When** he runs `uv run bananalyzer diagnose`
   **Then** the command reports local configuration paths, data file availability, and missing integration placeholders without crashing.
5. **Given** Ryan wants to view configuration
   **When** he runs `uv run bananalyzer config`
   **Then** the command displays the active local config file paths and key editable settings.

## 2. Developer Context

### Technical Requirements
- Create a `Typer` app instance in `bananalyzer/cli.py`.
- Ensure the main entrypoint in `bananalyzer/__main__.py` invokes the Typer CLI app.
- Ensure `scaffold_data_foundation()` from `config.py` is called at the CLI start so files exist before commands try to read them.
- Define five main commands: `run`, `status`, `dashboard`, `diagnose`, `config`.
- **run command**: Execute a safe placeholder loop.
- **status command**: Print out current state, model/profile, integration health summary, and recent event summary using `rich` for formatting.
- **dashboard command**: Start a minimal placeholder Textual `App`.
- **diagnose command**: Report local configuration paths, check file existence, and report missing integrations as unavailable.
- **config command**: Load configuration using models in `config.py` and display active local config file paths and key settings.

### Architecture Compliance
- Ensure `Typer` is used for CLI routing.
- Ensure `Rich` is used for terminal output (tables, panels, or styled text).
- Do not add any cloud or remote service requirements. All logic remains strictly local-first.
- Keep the CLI logic in `cli.py` and delegate to other modules where appropriate.

### Code Structure Requirements
- `src/bananalyzer/cli.py` (Command implementations)
- `src/bananalyzer/__main__.py` (Entrypoint)
- `src/bananalyzer/ui/dashboard.py` (Create with a simple Textual `App` placeholder)
- `tests/test_cli.py` (Use `typer.testing.CliRunner`)

### Testing Requirements
- Use `typer.testing.CliRunner` in `tests/test_cli.py`.
- Verify that `--help` displays all expected commands.
- Verify that `config`, `status`, and `diagnose` commands execute without crashing.

## 3. Previous Story Intelligence
- Story 1.2 created `constants.py` and `config.py` which includes the `scaffold_data_foundation()` function. This must be utilized so the config and state files exist before the CLI tries to read them.
- Paths should be dynamically retrieved using constants from `constants.py`.

## 4. Latest Tech Information
- `typer` with `CliRunner` for testing CLI commands is the standard approach.
- `rich` provides Panel, Table, and styled text for readable terminal output.

## 5. Project Context Reference
- **Date:** 2026-05-06
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Implement Typer CLI app with five commands (`run`, `status`, `dashboard`, `diagnose`, `config`)
- [x] Task 2: Implement `__main__.py` entrypoint to invoke Typer app
- [x] Task 3: Integrate `scaffold_data_foundation()` into CLI startup
- [x] Task 4: Create `ui/dashboard.py` with Textual placeholder
- [x] Task 5: Write CLI tests using `typer.testing.CliRunner`

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Ultimate context engine analysis completed - comprehensive developer guide created.
- Implemented Typer CLI with all five commands, Rich output formatting, Textual dashboard placeholder, and CLI tests.

### File List
- `src/bananalyzer/cli.py`
- `src/bananalyzer/__main__.py`
- `src/bananalyzer/ui/dashboard.py`
- `tests/test_cli.py`

### Change Log
- **2026-05-06**: Implemented CLI commands with Typer, Rich formatting, and Textual placeholder. Added CLI tests with `CliRunner`.

## 6. Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created. Implementation complete.

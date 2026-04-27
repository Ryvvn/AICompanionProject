# Story 1.3: Provide CLI Commands for Local Operation

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Ryan,
I want simple CLI commands for running and inspecting Bananalyzer,
So that I can operate the assistant without needing a polished GUI.

## Acceptance Criteria

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

## Developer Context

This story implements the local CLI interface using Typer and Rich. It will define the interaction surface for the application, connecting the CLI commands to basic placeholder or scaffolding logic that will be filled out in later stories.

### Technical Requirements

- Create a `Typer` app instance in `bananalyzer/cli.py`.
- Ensure the main entrypoint in `bananalyzer/__main__.py` invokes the Typer CLI app.
- Ensure `scaffold_data_foundation()` from `config.py` is called at the CLI start so files exist before commands try to read them.
- Define five main commands: `run`, `status`, `dashboard`, `diagnose`, `config`.
- **run command**: Execute a safe placeholder loop (e.g., printing "Starting local MVP runtime loop..." and keeping the process alive).
- **status command**: Print out current state (from `data/state/current_state.json`), model/profile (from config), integration health summary (from `data/state/integration_health.json`), and recent event summary. Use `rich` for formatting.
- **dashboard command**: Start a minimal placeholder Textual `App`. Epic 1 requires a basic Textual dashboard or safe placeholder.
- **diagnose command**: Report local configuration paths (using `constants.py`), check if the files exist, and report missing integrations as unavailable (without crashing).
- **config command**: Load configuration using the models in `config.py` and display the active local config file paths and key settings.

### Architecture Compliance Guardrails

- Ensure `Typer` is used for CLI routing.
- Ensure `Rich` is used for terminal output (tables, panels, or styled text) to make diagnostics easy to read.
- Do not add any cloud or remote service requirements. Ensure all logic remains strictly local-first.
- Keep the CLI logic in `cli.py` and delegate to other modules where appropriate (like `diagnostics.py` if created, or UI modules).

### Library & Framework Requirements

- `typer` (for CLI structure)
- `rich` (for terminal rendering)
- `textual` (for the placeholder dashboard)

### File Structure Requirements

- `src/bananalyzer/cli.py` (Command implementations)
- `src/bananalyzer/__main__.py` (Entrypoint)
- `src/bananalyzer/ui/dashboard.py` (Create this file with a simple Textual `App` placeholder)

### Testing Requirements

- Use `typer.testing.CliRunner` in `tests/test_cli.py`.
- Verify that `--help` displays all expected commands.
- Verify that `config`, `status`, and `diagnose` commands execute without crashing and produce expected outputs when mocked or isolated from real files.

### Previous Story Intelligence

- Story 1.2 created `constants.py` and `config.py` which includes the `scaffold_data_foundation()` function. This must be utilized so the config and state files exist before the CLI tries to read them.
- Paths should be dynamically retrieved using constants from `constants.py` (e.g., `CONFIG_DIR`, `STATE_DIR`).

### Git Intelligence Summary

- Based on recent commits, `pydantic-settings` is in use, and `yaml` configuration exists. The `Settings`, `ModelProfiles`, and `Thresholds` classes in `config.py` can be instantiated to easily read configuration.

### Latest Tech Information

- N/A

### Project Context Reference

- This satisfies FR30, FR39, FR43, FR44, FR46, and FR48 from the PRD by establishing the CLI diagnostic surface.

## Story Completion Status

- Status set to: `ready-for-dev`
- Completion note: Ultimate context engine analysis completed - comprehensive developer guide created.

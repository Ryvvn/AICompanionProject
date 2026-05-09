# Story 1.1: Set Up Initial Project from Starter Template

**Status:** done
**Epic:** 1 - Local Companion Foundation and Operational Visibility

## 1. Story Foundation

**User Story:**
As Ryan,
I want a local Python project foundation for Bananalyzer,
So that I can run and develop the companion from my workstation.

**Acceptance Criteria:**
1. **Given** the project has not yet been initialized
   **When** the developer initializes the app foundation
   **Then** the project uses Python 3.11+ with `uv` and a `src/bananalyzer/` package layout
   **And** dependencies include Typer, Rich, Textual, Pydantic, Pydantic Settings, psutil, pywin32, and httpx.
2. **Given** the project foundation exists
   **When** development dependencies are installed
   **Then** pytest and ruff are available through `uv run`
   **And** placeholder tests can run successfully.
3. **Given** Ryan opens the project
   **When** he inspects the source tree
   **Then** the architecture modules exist for CLI, config, diagnostics, events, foreground detection, mode controller, model router, persona, privacy, state machine, integrations, memory, UI, accountability, context, and utilities.
4. **Given** this is a personal local MVP
   **When** quality automation is configured
   **Then** local `uv run pytest` and `uv run ruff check .` commands are available
   **And** remote CI/CD is documented as optional and out of scope unless Ryan chooses to add it later.

## 2. Developer Context

### Technical Requirements
- Runtime: Python 3.11+.
- Package manager / runner: `uv`.
- Required runtime deps: Typer, Rich, Textual, Pydantic, Pydantic Settings, psutil, pywin32, httpx.
- Required dev deps: pytest, ruff.
- Operation mode: local-first, no cloud dependency required.
- This is the first implementation story in Epic 1 and sets the baseline project scaffold.
- Scope is intentionally **foundation-only**: project init, package layout, modules, dependencies, and local quality commands.
- Do **not** implement behavior-heavy logic yet (state transitions, integrations, routing intelligence, memory behavior).

### Architecture Compliance
- Respect boundaries from the architecture:
  - CLI command definitions in `cli.py`.
  - Runtime loop coordination in `mode_controller.py`.
  - State transition logic in `state_machine.py`.
  - External tool communication isolated to `integrations/*.py`.
- Canonical persisted state values for future stories must be only: `coding`, `gaming`, `doomscrolling`, `companion`, `fallback`.
- Naming conventions: Python and JSON/YAML fields use `snake_case`.
- Avoid premature implementations that bypass adapter boundaries.
- Keep root-level prototype files (`mode_controller.py`, `job_tracker.py`) unchanged during scaffold work.

### Code Structure Requirements
- `src/bananalyzer/__init__.py`
- `src/bananalyzer/__main__.py`
- `src/bananalyzer/cli.py`
- `src/bananalyzer/config.py`
- `src/bananalyzer/constants.py`
- `src/bananalyzer/diagnostics.py`
- `src/bananalyzer/events.py`
- `src/bananalyzer/foreground.py`
- `src/bananalyzer/mode_controller.py`
- `src/bananalyzer/model_router.py`
- `src/bananalyzer/persona.py`
- `src/bananalyzer/privacy.py`
- `src/bananalyzer/state_machine.py`
- `src/bananalyzer/accountability/__init__.py`, `banana_debt.py`, `interventions.py`, `signals.py`
- `src/bananalyzer/context/__init__.py`, `code_context.py`, `screen_context.py`, `context_builder.py`
- `src/bananalyzer/integrations/__init__.py`, `base.py`, `ollama.py`, `screenpipe.py`, `mcp.py`, `stt.py`, `tts.py`
- `src/bananalyzer/memory/__init__.py`, `store.py`, `summarizer.py`, `retrieval.py`
- `src/bananalyzer/ui/__init__.py`, `dashboard.py`
- `src/bananalyzer/utils/__init__.py`, `files.py`, `time.py`
- `tests/` tree with placeholder tests

### Testing Requirements
- `uv run pytest` succeeds with scaffold tests.
- `uv run ruff check .` succeeds.
- `src/` package imports for `bananalyzer` work from uv execution context.
- Tests do not require live integrations or network calls.

## 3. Previous Story Intelligence
- Not applicable (this is Story 1.1, the first implementation story).

## 4. Latest Tech Information
- Web lookup was attempted for package/version freshness, but no reliable result payload was returned in-session.
- Use latest stable package releases at implementation time and keep Python target at 3.11+ per architecture.

## 5. Project Context Reference
- **Date:** 2026-05-06
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Initialize UV Python app scaffold (AC: 1)
  - [x] Run `uv init bananalyzer --app --python 3.11` in the intended project folder.
  - [x] Ensure package path is `src/bananalyzer/` and entrypoint imports resolve.
- [x] Task 2: Add required runtime and dev dependencies (AC: 1, 2)
  - [x] Runtime: `typer`, `rich`, `textual`, `pydantic`, `pydantic-settings`, `psutil`, `pywin32`, `httpx`.
  - [x] Dev: `pytest`, `ruff`.
  - [x] Confirm dependencies are recorded in `pyproject.toml` and lockfile is generated by `uv`.
- [x] Task 3: Create architecture-aligned module skeleton (AC: 3)
  - [x] Add root package files: `__init__.py`, `__main__.py`, `cli.py`, `config.py`, `constants.py`, `diagnostics.py`, `events.py`, `foreground.py`, `mode_controller.py`, `model_router.py`, `persona.py`, `privacy.py`, `state_machine.py`.
  - [x] Add subpackages: `accountability/`, `context/`, `integrations/`, `memory/`, `ui/`, `utils/` with appropriate `__init__.py` and placeholder modules.
- [x] Task 4: Add baseline tests and quality command checks (AC: 2, 4)
  - [x] Create `tests/` tree with placeholder tests sufficient for import/smoke validation.
  - [x] Ensure `uv run pytest` passes.
  - [x] Ensure `uv run ruff check .` passes.
- [x] Task 5: Keep MVP CI/CD scope correct (AC: 4)
  - [x] Do not add mandatory remote CI pipelines.
  - [x] Add brief local note that CI/CD is optional and post-MVP.

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6

### Debug Log References
- _To be filled by dev agent_

### Completion Notes List
- Ultimate context engine analysis completed - comprehensive developer guide created.
- Scaffolded the uv project, added baseline dependencies, created architecture package placeholder files.
- Configured ruff to exclude prototyping files, and verified simple test and lint checks pass.

### File List
- `src/bananalyzer/` (all module placeholders created)
- `pyproject.toml` (dependencies configured)
- `tests/` (placeholder tests)
- `_bmad-output/implementation-artifacts/1-1-set-up-initial-project-from-starter-template.md`

### Change Log
- **2026-05-06**: Initialized uv project, added baseline dependencies, created architecture package skeleton, verified pytest and ruff pass.

## 6. Story Completion Status
Scaffolded the uv project, added baseline dependencies, created architecture package placeholder files, configured ruff to exclude prototyping files, and verified simple test and lint checks pass.

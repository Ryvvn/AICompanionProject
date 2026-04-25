---
stepsCompleted:
  - 1
  - 2
  - 3
  - 4
  - 5
  - 6
  - 7
  - 8
lastStep: 8
status: 'complete'
completedAt: '2026-04-25'
inputDocuments:
  - D:/AICompanionProject/_bmad-output/planning-artifacts/prd.md
  - D:/AICompanionProject/_bmad-output/planning-artifacts/prd-validation-report.md
workflowType: 'architecture'
project_name: 'AICompanionProject'
user_name: 'Ryan'
date: '2026-04-25'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

The PRD defines 48 functional requirements across nine capability areas. Architecturally, these imply a modular local orchestration system centered on activity detection, state routing, local AI model invocation, external integration adapters, persistent memory, voice/text interaction, and diagnostics.

The core functional architecture must support:

- Foreground activity detection and classification into Coding, Gaming, Doomscrolling, Companion/Idle, and Fallback states.
- A state machine that tracks transitions and controls downstream prompt, model, persona, and intervention behavior.
- Coding support through active VS Code/Kilo MCP context ingestion.
- Behavioral accountability through Screenpipe-derived distraction signals, banana debt, timers, and intervention thresholds.
- A persistent companion identity backed by editable local memory.
- Text-first interaction with optional STT and TTS.
- State-specific local model routing through Ollama.
- Local-first privacy controls and clear visibility into stored context.
- Diagnostics for state transitions, detections, integration availability, and failures.

**Non-Functional Requirements:**

The NFRs that most strongly shape architecture are performance, local privacy, degraded operation, integration resilience, usability/control, and maintainability.

The validation report flags several NFRs as insufficiently measurable, especially around workstation usability, VRAM budget, Screenpipe polling overhead, response latency, memory update disruption, status visibility, logging quality, context ingestion bounds, and integration isolation. Architecture should therefore convert these into explicit design constraints where possible.

Critical NFR implications:

- Keep AI GPU usage bounded for an RTX 3070 8GB environment.
- Prefer CPU-side STT/TTS for MVP.
- Avoid unbounded ingestion from Screenpipe, VS Code, logs, and memory.
- Isolate integrations so one failure does not crash the assistant.
- Provide degraded modes for Screenpipe, MCP, STT, and TTS failures.
- Make prompts, model profiles, state definitions, thresholds, and memory behavior configurable without rewriting the main loop.
- Provide operational visibility through logs/status output even without a polished GUI.

**Scale & Complexity:**

- Primary domain: desktop local AI agent / developer tooling / productivity companion
- Complexity level: medium
- Estimated architectural components: 10-12

Likely architectural components:

1. App/runtime entrypoint
2. Foreground activity monitor
3. State machine / mode controller
4. Screenpipe watcher
5. MCP code-context adapter
6. Ollama model router
7. Prompt/persona router
8. Memory store and updater
9. Text interaction interface
10. Optional STT adapter
11. TTS adapter
12. Diagnostics/status/logging subsystem

### Technical Constraints & Dependencies

Known constraints and dependencies:

- Windows 11 first.
- Python 3.10+ runtime assumed.
- Local-first operation with no required cloud services.
- RTX 3070 8GB VRAM constraint.
- Ollama for local model inference.
- Screenpipe for OCR/app/browser context and distraction signals.
- VS Code/Kilo MCP bridge for active code context.
- Whisper.cpp for STT.
- Piper or Kokoro for TTS.
- Local file-based configuration and memory.
- No installer, tray app, auto-update, macOS, or Linux support required for MVP.
- Future Unity log ingestion should remain isolated from MVP core flow.

### Cross-Cutting Concerns Identified

- State routing consistency across foreground detection, Screenpipe signals, prompt selection, model selection, memory, and interventions.
- Performance isolation so background monitoring, model usage, memory updates, and audio do not disrupt coding, Unity, or games.
- Integration resilience and degraded operation for Screenpipe, MCP, STT, TTS, Ollama, and future Unity integrations.
- Local-first privacy and inspectable storage for code context, OCR text, audio-derived text, and memory.
- Context-size control to prevent raw history, OCR, code, logs, or memory from bloating prompts.
- Observability through current state, model/profile, recent detections, integration health, memory updates, and errors.
- Persona safety boundaries to keep accountability sharp but not abusive.
- Configuration boundaries for thresholds, polling intervals, model profiles, prompts, memory cadence, and intervention intensity.

## Starter Template Evaluation

### Primary Technology Domain

Desktop local AI agent / Python orchestration application.

The MVP should use a Python-first local service/CLI foundation rather than a web, Electron, Tauri, or full GUI starter. The product value comes from background orchestration, state routing, integrations, and diagnostics.

### Starter Options Considered

**Plain Python + uv + Typer/Rich/Textual**

A lightweight Python application structure initialized with `uv`, using Typer for CLI commands, Rich for readable output/logging, and Textual for an optional terminal dashboard.

This fits the MVP because it keeps the core orchestration loop simple while still giving Ryan a navigable monitoring/status surface.

**PySide6 / Qt desktop GUI**

PySide6 is a strong desktop GUI framework, but it is heavier than needed for MVP. It should remain a future option for a polished dashboard/tray app after the local agent loop is stable.

**Electron/Tauri desktop shell**

Electron or Tauri would be unnecessary for MVP because the core app is Python-local and integration-heavy. Adding a webview desktop shell would create frontend/backend complexity before the orchestration layer is proven.

### Selected Starter: Plain Python + uv Project

**Rationale for Selection:**

The MVP should optimize for clarity, local execution, and integration stability. A plain Python project managed by `uv` is easiest to understand, test, and evolve. Typer provides a clean CLI for starting the agent, checking status, running diagnostics, and tuning configuration. Textual can provide a terminal dashboard without committing the project to full GUI complexity.

**Initialization Command:**

```bash
uv init bananalyzer --app --python 3.11
cd bananalyzer
uv add typer rich textual pydantic pydantic-settings psutil pywin32 httpx
uv add --dev pytest ruff
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**

Python 3.11+ as the MVP runtime, matching the PRD’s Python requirement while using a current stable Python version.

**Project Management:**

`uv` manages the virtual environment, dependencies, lockfile, and Python version pinning through `pyproject.toml` and `uv.lock`.

**CLI / Operations Interface:**

Typer provides commands such as:

- `bananalyzer run`
- `bananalyzer status`
- `bananalyzer dashboard`
- `bananalyzer diagnose`
- `bananalyzer config`

**Monitoring Interface:**

Rich provides readable terminal output and logs. Textual provides an optional terminal dashboard for current mode, model profile, integration health, recent detections, memory status, and errors.

**Configuration:**

Pydantic Settings provides typed local configuration for polling intervals, model profiles, thresholds, prompt paths, memory paths, and integration settings.

**Testing Framework:**

pytest provides unit/integration tests for state transitions, routing decisions, config loading, and integration adapters.

**Code Organization:**

The project should separate orchestration from integrations:

```text
bananalyzer/
  __main__.py
  cli.py
  config.py
  mode_controller.py
  state_machine.py
  diagnostics.py
  integrations/
    ollama.py
    screenpipe.py
    mcp.py
    stt.py
    tts.py
  memory/
    store.py
    summarizer.py
  prompts/
    coding.md
    gaming.md
    doomscroll.md
    companion.md
  ui/
    dashboard.py
  tests/
```

**Development Experience:**

- `uv run bananalyzer run` starts the agent loop.
- `uv run bananalyzer status` shows current state.
- `uv run bananalyzer dashboard` opens the Textual monitor.
- `uv run pytest` runs tests.
- `uv run ruff check .` checks code quality.
- `uv run ruff format .` formats code.

**Note:** Project initialization using this foundation should be the first implementation story.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**

- Use file-based local storage for MVP configuration, prompts, memory, state snapshots, and logs.
- Use adapter boundaries for all external integrations: Ollama, Screenpipe, MCP, STT, TTS, and future Unity logs.
- Use local-only privacy defaults with an explicit allowlist for persisted context.
- Use a simple polling orchestration loop for MVP, with async I/O introduced only where integration calls benefit from it.
- Include both CLI status commands and a basic Textual dashboard in MVP diagnostics.

**Important Decisions (Shape Architecture):**

- Defer SQLite until structured querying/history becomes necessary.
- Use JSON/YAML for configuration and structured state.
- Use Markdown for editable memory and persona/prompt files where human editing matters.
- Use JSONL for append-only diagnostic/event logs.
- Use Python `logging` for application diagnostics.
- Use health-check methods on each integration adapter.
- Use degraded modes instead of crashing when optional integrations fail.

**Deferred Decisions (Post-MVP):**

- Full desktop GUI/tray app.
- Auto-start on boot.
- Installer/packaging.
- SQLite or vector/RAG-backed memory.
- Unity log ingestion.
- Multi-user/cloud sync.
- Advanced encryption/key management beyond local-only MVP controls.

### Data Architecture

MVP data architecture will be local file-based.

**Decision: File-first local storage**

The MVP will use local files instead of a database as the primary persistence mechanism.

Recommended storage layout:

```text
data/
  config/
    settings.yaml
    model_profiles.yaml
    thresholds.yaml
  memory/
    memory.md
    session_summary.md
    banana_debt.json
  state/
    current_state.json
    integration_health.json
  logs/
    events.jsonl
    app.log
  prompts/
    coding.md
    gaming.md
    doomscroll.md
    companion.md
```

**Rationale:**

File-based storage is easier to inspect, edit, debug, and understand during MVP development. It matches the local-first requirement and avoids adding database complexity before the product proves its core loop.

**Data formats:**

- Markdown for human-editable memory and prompt/persona files.
- YAML for user-facing configuration where readability matters.
- JSON for structured state snapshots.
- JSONL for append-only event history.
- Plain `.log` files for runtime diagnostics.

**SQLite decision: Deferred**

SQLite is a strong future option for structured local history, querying, metrics, and memory indexing, but it is not necessary for the first MVP. It should be introduced when JSONL/Markdown files become hard to query or maintain.

### Authentication & Security

**Decision: No user authentication for MVP**

The MVP is a single-user local desktop companion for Ryan. It does not need login, accounts, roles, sessions, or remote auth.

**Decision: Local-only privacy default**

The system must not send captured code, OCR text, audio-derived text, memory, or diagnostics to external services by default.

**Decision: Explicit persistence allowlist**

Only approved categories of context may be persisted:

- Goals
- Session summaries
- Recurring coding mistakes
- Banana debt
- State transitions
- Integration health
- User-approved memory notes
- Minimal diagnostic metadata

Raw Screenpipe OCR, raw audio, large code excerpts, and unbounded logs should not be stored in memory by default.

**Decision: Inspectable local storage**

Ryan must be able to inspect and edit stored memory/config files directly.

**Decision: Persona safety boundaries**

The “mean banana” persona may be sarcastic, direct, or accountability-focused, but must avoid abusive, discriminatory, or self-harm-reinforcing language.

### API & Communication Patterns

**Decision: Adapter pattern for integrations**

Each external integration must be isolated behind an adapter module.

Adapters:

- `integrations/ollama.py`
- `integrations/screenpipe.py`
- `integrations/mcp.py`
- `integrations/stt.py`
- `integrations/tts.py`
- future `integrations/unity.py`

Each adapter should expose a small, consistent surface:

- `is_available()`
- `health_check()`
- integration-specific action methods
- clear error reporting
- timeout handling where applicable

**Decision: Graceful degraded operation**

Integration failures must not crash the full assistant.

Expected degradation:

- Screenpipe unavailable → foreground detection + text interaction still work.
- MCP unavailable → general chat/text interaction still works.
- STT unavailable → typed input still works.
- TTS unavailable → text output still works.
- Ollama unavailable → status/diagnostics report model unavailability.
- Memory unavailable → runtime continues with warning and no persistence.

**Decision: Simple polling loop first**

The MVP should use a straightforward orchestration loop:

1. Read foreground state.
2. Optionally query Screenpipe on configured interval.
3. Update state machine.
4. Route prompt/model/persona.
5. Handle user input or intervention.
6. Update memory/logs/status.
7. Sleep until next polling cycle.

**Decision: Use async only where it simplifies I/O**

`asyncio` may be used for concurrent integration calls, timeouts, or dashboard responsiveness, but the core design should stay understandable. Avoid making every component async by default.

### Frontend Architecture

**Decision: CLI and Textual dashboard, not full GUI**

The MVP frontend surface will be operational rather than polished.

Required CLI commands:

- `bananalyzer run`
- `bananalyzer status`
- `bananalyzer dashboard`
- `bananalyzer diagnose`
- `bananalyzer config`

**Decision: Basic Textual dashboard included in MVP**

The dashboard should show:

- Current detected state
- Current model/profile
- Last state transition
- Recent detections
- Screenpipe health
- MCP health
- Ollama health
- STT/TTS health
- Last memory update
- Recent errors
- Banana debt / accountability summary

**Decision: Full desktop GUI deferred**

PySide6, tray app, installer, and polished desktop UI are deferred until after the core loop is reliable.

### Infrastructure & Deployment

**Decision: Local development execution for MVP**

MVP runs through `uv`:

```bash
uv run bananalyzer run
uv run bananalyzer status
uv run bananalyzer dashboard
uv run pytest
uv run ruff check .
uv run ruff format .
```

**Decision: No cloud infrastructure**

No hosting, cloud database, auth provider, telemetry service, or remote API is required for MVP.

**Decision: Local observability**

Diagnostics are local:

- terminal output
- Textual dashboard
- `logs/app.log`
- `logs/events.jsonl`
- `state/current_state.json`
- `state/integration_health.json`

**Decision: Packaging deferred**

Executable packaging, installer, auto-start, tray icon, and update mechanism are post-MVP.

### Decision Impact Analysis

**Implementation Sequence:**

1. Initialize Python project with `uv`.
2. Create config, logging, and local data directories.
3. Implement typed config loading.
4. Implement reliable text interaction baseline for manual/fallback operation.
5. Implement state machine and foreground activity monitor.
6. Implement diagnostics/status files.
7. Add Ollama adapter.
8. Add prompt/model routing.
9. Add memory files and update flow.
10. Add Textual dashboard.
11. Add Screenpipe adapter.
12. Add MCP adapter.
13. Add TTS.
14. Add STT if stable enough.
15. Add tests around state routing, config, adapters, and degraded modes.

**Cross-Component Dependencies:**

- State machine drives prompt routing, model routing, memory behavior, interventions, and dashboard display.
- Config affects polling intervals, thresholds, model profiles, prompts, memory cadence, and integration settings.
- Diagnostics depends on every component reporting status consistently.
- Privacy boundaries affect Screenpipe, MCP, memory, logging, and prompt construction.
- Degraded-mode behavior depends on adapter health checks and clear fallback contracts.

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:** 8 areas where AI agents could make different choices:

1. Python naming conventions
2. State/mode naming
3. File and directory organization
4. Config, memory, state, and log formats
5. Integration adapter interfaces
6. Runtime event formats
7. Error/degraded-mode behavior
8. Test organization

### Naming Patterns

**Database Naming Conventions:**

No database is used in MVP. If SQLite is introduced later:

- Tables use plural `snake_case`: `state_events`, `memory_entries`
- Columns use `snake_case`: `created_at`, `event_type`, `banana_debt_delta`
- Primary keys use `id`
- Foreign keys use `{entity}_id`: `session_id`, `memory_entry_id`
- Indexes use `idx_{table}_{column}`: `idx_state_events_created_at`

**API Naming Conventions:**

No external API is exposed in MVP. Internal adapter methods must use Python `snake_case`.

Examples:

```python
health_check()
is_available()
get_active_context()
generate_response()
speak_text()
```

If a local HTTP API is added later:

- Endpoints use plural lowercase resource names.
- JSON fields use `snake_case`.
- Health endpoints use `/health` or `/integrations/{name}/health`.

**Code Naming Conventions:**

- Files and modules: `snake_case.py`
- Functions/methods: `snake_case`
- Variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Enum values / state string values: lowercase `snake_case`

Examples:

```python
class ModeController:
    pass

def detect_foreground_app():
    pass

CURRENT_STATE_FILE = "current_state.json"
```

**State Naming Conventions:**

Canonical state names:

```text
coding
gaming
doomscrolling
companion
fallback
```

Agents must not invent alternatives like `dev`, `work`, `idle_mode`, `duo`, or `default` in core state records. User-facing labels may be friendlier, but persisted state values must use the canonical names.

### Structure Patterns

**Project Organization:**

Code should be organized by architectural responsibility, not by random utility buckets.

```text
bananalyzer/
  __main__.py
  cli.py
  config.py
  diagnostics.py
  mode_controller.py
  state_machine.py
  integrations/
  memory/
  prompts/
  ui/
tests/
data/
```

Rules:

- CLI command definitions go in `cli.py`.
- Runtime orchestration goes in `mode_controller.py`.
- Pure state transition logic goes in `state_machine.py`.
- Integration-specific code goes under `integrations/`.
- Memory persistence and summarization go under `memory/`.
- Textual dashboard code goes under `ui/`.
- Prompt/persona files go under `data/prompts/` or packaged `prompts/`, but the architecture must keep them editable.
- Tests live in top-level `tests/`.

**File Structure Patterns:**

Configuration files:

```text
data/config/settings.yaml
data/config/model_profiles.yaml
data/config/thresholds.yaml
```

Runtime state files:

```text
data/state/current_state.json
data/state/integration_health.json
```

Memory files:

```text
data/memory/memory.md
data/memory/session_summary.md
data/memory/banana_debt.json
```

Log files:

```text
data/logs/app.log
data/logs/events.jsonl
```

Prompt files:

```text
data/prompts/coding.md
data/prompts/gaming.md
data/prompts/doomscroll.md
data/prompts/companion.md
data/prompts/fallback.md
```

### Format Patterns

**API Response Formats:**

No external API is required for MVP.

Internal adapter results should use simple typed result objects or dictionaries with consistent fields:

```json
{
  "ok": true,
  "data": {},
  "error": null
}
```

Failure shape:

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "integration_unavailable",
    "message": "Screenpipe is not reachable",
    "recoverable": true
  }
}
```

**Data Exchange Formats:**

JSON/YAML field names use `snake_case`.

Timestamps use ISO 8601 strings.

Example:

```json
{
  "current_state": "coding",
  "previous_state": "companion",
  "changed_at": "2026-04-25T12:00:00Z",
  "confidence": 0.86
}
```

Boolean values use native JSON booleans: `true` / `false`.

Null values are allowed only when a value is genuinely unavailable, not as a placeholder for missing design decisions.

### Communication Patterns

**Event System Patterns:**

Runtime event names use dotted lowercase:

```text
app.started
app.stopped
state.changed
state.detected
integration.available
integration.failed
integration.recovered
memory.updated
memory.skipped
prompt.selected
model.selected
intervention.triggered
intervention.skipped
```

Every JSONL event must include:

```json
{
  "timestamp": "2026-04-25T12:00:00Z",
  "event_type": "state.changed",
  "component": "state_machine",
  "severity": "info",
  "message": "State changed from companion to coding",
  "details": {}
}
```

Allowed severity values:

```text
debug
info
warning
error
critical
```

**State Management Patterns:**

The state machine is the source of truth for current mode.

Rules:

- State transitions must go through `state_machine.py`.
- Components must not directly overwrite `current_state.json`.
- The mode controller may request transitions, but the state machine validates them.
- Every state transition should emit a `state.changed` event.
- Detection without transition should emit `state.detected` only when useful for diagnostics.

State transition record:

```json
{
  "previous_state": "companion",
  "current_state": "coding",
  "reason": "foreground_app_detected",
  "confidence": 0.86,
  "timestamp": "2026-04-25T12:00:00Z"
}
```

### Process Patterns

**Error Handling Patterns:**

Integration errors must be recoverable by default unless the core runtime cannot continue.

Rules:

- Do not crash the full assistant because Screenpipe, MCP, STT, or TTS fails.
- Convert integration failures into health status updates.
- Log failures to `app.log`.
- Emit structured events to `events.jsonl`.
- Show current degraded mode in `status` and dashboard output.

Health status shape:

```json
{
  "component": "screenpipe",
  "available": false,
  "status": "unavailable",
  "last_check": "2026-04-25T12:00:00Z",
  "last_error": "Connection refused",
  "degraded_mode": "foreground_detection_only"
}
```

Allowed integration statuses:

```text
available
unavailable
degraded
unknown
```

**Loading State Patterns:**

For MVP, long-running operations should report status through diagnostics rather than complex UI loading state.

Rules:

- CLI commands print clear progress messages for long operations.
- Dashboard shows current operation if available.
- Background tasks should emit events when started, completed, skipped, or failed.

Operation event examples:

```text
memory.update_started
memory.updated
memory.skipped
integration.health_check_started
integration.health_check_completed
```

### Enforcement Guidelines

**All AI Agents MUST:**

- Use canonical state names: `coding`, `gaming`, `doomscrolling`, `companion`, `fallback`.
- Use `snake_case` for Python names and JSON/YAML fields.
- Put integration code only under `integrations/`.
- Put state transition logic only in `state_machine.py`.
- Use adapter health checks instead of direct integration probing from random modules.
- Emit structured JSONL events for meaningful runtime changes.
- Avoid storing raw Screenpipe OCR, raw audio, or large code excerpts unless explicitly allowlisted.
- Preserve local-first defaults and no-cloud MVP behavior.
- Add or update tests in `tests/` for state, config, adapter, and degraded-mode behavior.

**Pattern Enforcement:**

- `ruff` enforces Python formatting and linting.
- `pytest` verifies expected state transitions, config loading, and adapter fallback behavior.
- Architecture violations should be corrected in the implementation branch before adding new features.
- If a pattern needs to change, update this architecture document first, then update code.

### Pattern Examples

**Good Examples:**

State value:

```json
{
  "current_state": "doomscrolling"
}
```

Event:

```json
{
  "timestamp": "2026-04-25T12:00:00Z",
  "event_type": "integration.failed",
  "component": "mcp",
  "severity": "warning",
  "message": "MCP context unavailable; falling back to general text interaction",
  "details": {
    "degraded_mode": "text_only"
  }
}
```

Adapter method names:

```python
class ScreenpipeAdapter:
    def is_available(self) -> bool:
        ...

    def health_check(self) -> IntegrationHealth:
        ...

    def get_recent_context(self) -> AdapterResult:
        ...
```

**Anti-Patterns:**

Do not invent alternate state names:

```json
{
  "current_state": "duo_mode"
}
```

Use:

```json
{
  "current_state": "companion"
}
```

Do not write integration logic inside the mode controller:

```python
# Bad
def run_loop():
    response = httpx.get("http://localhost:3030/screenpipe")
```

Use an adapter:

```python
def run_loop(screenpipe: ScreenpipeAdapter):
    context = screenpipe.get_recent_context()
```

Do not store raw OCR by default:

```json
{
  "raw_ocr_text": "large captured screen text..."
}
```

Store summarized/allowlisted context instead:

```json
{
  "signal_type": "doomscroll_pattern",
  "confidence": 0.82,
  "source": "screenpipe"
}
```

## Project Structure & Boundaries

### Complete Project Directory Structure

```text
bananalyzer/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── README.md
├── data/
│   ├── config/
│   │   ├── settings.yaml
│   │   ├── model_profiles.yaml
│   │   └── thresholds.yaml
│   ├── memory/
│   │   ├── memory.md
│   │   ├── session_summary.md
│   │   └── banana_debt.json
│   ├── prompts/
│   │   ├── coding.md
│   │   ├── gaming.md
│   │   ├── doomscroll.md
│   │   ├── companion.md
│   │   └── fallback.md
│   ├── state/
│   │   ├── current_state.json
│   │   └── integration_health.json
│   └── logs/
│       ├── app.log
│       └── events.jsonl
├── src/
│   └── bananalyzer/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── constants.py
│       ├── diagnostics.py
│       ├── events.py
│       ├── foreground.py
│       ├── mode_controller.py
│       ├── model_router.py
│       ├── persona.py
│       ├── privacy.py
│       ├── state_machine.py
│       ├── accountability/
│       │   ├── __init__.py
│       │   ├── banana_debt.py
│       │   ├── interventions.py
│       │   └── signals.py
│       ├── context/
│       │   ├── __init__.py
│       │   ├── code_context.py
│       │   ├── screen_context.py
│       │   └── context_builder.py
│       ├── integrations/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── ollama.py
│       │   ├── screenpipe.py
│       │   ├── mcp.py
│       │   ├── stt.py
│       │   └── tts.py
│       ├── memory/
│       │   ├── __init__.py
│       │   ├── store.py
│       │   ├── summarizer.py
│       │   └── retrieval.py
│       ├── ui/
│       │   ├── __init__.py
│       │   └── dashboard.py
│       └── utils/
│           ├── __init__.py
│           ├── files.py
│           └── time.py
└── tests/
    ├── conftest.py
    ├── test_config.py
    ├── test_state_machine.py
    ├── test_mode_controller.py
    ├── test_diagnostics.py
    ├── accountability/
    │   ├── test_banana_debt.py
    │   └── test_interventions.py
    ├── context/
    │   └── test_context_builder.py
    ├── integrations/
    │   ├── test_base.py
    │   ├── test_ollama.py
    │   ├── test_screenpipe.py
    │   ├── test_mcp.py
    │   ├── test_stt.py
    │   └── test_tts.py
    └── memory/
        └── test_store.py
```

### Architectural Boundaries

**API Boundaries:**

MVP exposes no external public API.

Internal boundaries are Python module boundaries:

- CLI commands call orchestration services.
- Orchestration calls state, context, model, memory, and integration modules.
- Integrations communicate with external local tools through adapters.
- Data persistence goes through memory, diagnostics, config, and utility modules.

No module should directly call Screenpipe, Ollama, MCP, STT, or TTS except the matching adapter in `integrations/`.

**Component Boundaries:**

`cli.py`

- Defines user-facing commands.
- Should not contain orchestration logic.
- Calls `mode_controller`, `diagnostics`, or dashboard entrypoints.

`mode_controller.py`

- Coordinates the main runtime loop.
- Reads foreground/context signals.
- Requests state transitions.
- Calls prompt/model routing.
- Triggers interventions.
- Delegates persistence/logging to diagnostics/memory components.
- Must not contain direct HTTP calls to integrations.

`state_machine.py`

- Owns canonical state transition rules.
- Validates transitions between `coding`, `gaming`, `doomscrolling`, `companion`, and `fallback`.
- Emits transition records.
- Does not call external integrations.

`foreground.py`

- Handles Windows foreground activity detection.
- Converts process/window signals into candidate activity categories.
- Does not decide final mode alone; it passes signals to the state machine/mode controller.

`model_router.py`

- Chooses model profile and response parameters based on state and config.
- Calls `integrations/ollama.py` for generation.
- Does not build full context alone.

`persona.py`

- Resolves persona/prompt behavior for each state.
- Enforces tone boundaries.
- Loads editable prompt files.

`privacy.py`

- Defines persistence allowlist rules.
- Filters raw captured context before logging or memory writes.
- Central place for “what may be stored” decisions.

**Service Boundaries:**

`integrations/base.py`

- Defines shared adapter result and health structures.
- All adapters should follow this contract.

`integrations/ollama.py`

- Sole place for Ollama communication.
- Handles model availability, generation requests, and Ollama health.

`integrations/screenpipe.py`

- Sole place for Screenpipe communication.
- Returns summarized context signals, not raw persistence decisions.

`integrations/mcp.py`

- Sole place for VS Code/Kilo MCP context access.
- Provides active code context to `context/code_context.py`.

`integrations/stt.py`

- Sole place for speech-to-text integration.
- Optional MVP component.

`integrations/tts.py`

- Sole place for text-to-speech integration.
- Failure degrades to text output.

`memory/store.py`

- Owns reading and writing memory files.
- Does not decide state.
- Applies privacy-filtered inputs only.

`memory/summarizer.py`

- Converts session activity into concise summaries.
- Avoids unbounded raw history.

`diagnostics.py`

- Owns status snapshots, integration health display, and app log/event writing coordination.

`events.py`

- Defines event names, event payload shape, and JSONL writing helpers.

**Data Boundaries:**

`data/config/`

- User-editable configuration.
- Read through `config.py`.
- Other modules should not parse config files directly.

`data/memory/`

- Long-lived editable memory and banana debt.
- Accessed through `memory/store.py`.

`data/state/`

- Runtime snapshots.
- Written by diagnostics/state components.
- Used by `status` and dashboard commands.

`data/logs/`

- Append-only diagnostics and readable app logs.
- Written through diagnostics/events helpers.

`data/prompts/`

- Editable persona/prompt files.
- Loaded through `persona.py`.

### Requirements to Structure Mapping

**Context Awareness: FR1-FR5**

- `foreground.py`
- `state_machine.py`
- `mode_controller.py`
- `diagnostics.py`
- `data/state/current_state.json`
- Tests: `tests/test_state_machine.py`, `tests/test_mode_controller.py`

**Coding Support: FR6-FR11**

- `integrations/mcp.py`
- `context/code_context.py`
- `context/context_builder.py`
- `model_router.py`
- `persona.py`
- `data/prompts/coding.md`
- Tests: `tests/integrations/test_mcp.py`, `tests/context/test_context_builder.py`

**Behavioral Accountability: FR12-FR18**

- `integrations/screenpipe.py`
- `context/screen_context.py`
- `accountability/signals.py`
- `accountability/banana_debt.py`
- `accountability/interventions.py`
- `data/prompts/doomscroll.md`
- `data/prompts/gaming.md`
- `data/memory/banana_debt.json`
- Tests: `tests/accountability/test_banana_debt.py`, `tests/accountability/test_interventions.py`

**Companion Behavior: FR19-FR23**

- `persona.py`
- `model_router.py`
- `memory/store.py`
- `data/prompts/companion.md`
- `data/memory/memory.md`
- Tests: `tests/memory/test_store.py`

**Memory and Personalization: FR24-FR29**

- `memory/store.py`
- `memory/summarizer.py`
- `memory/retrieval.py`
- `privacy.py`
- `data/memory/memory.md`
- `data/memory/session_summary.md`
- Tests: `tests/memory/test_store.py`

**Voice and Interaction: FR30-FR34**

- `cli.py`
- `integrations/stt.py`
- `integrations/tts.py`
- `mode_controller.py`
- Tests: `tests/integrations/test_stt.py`, `tests/integrations/test_tts.py`

**Model and Response Routing: FR35-FR39**

- `model_router.py`
- `integrations/ollama.py`
- `persona.py`
- `data/config/model_profiles.yaml`
- Tests: `tests/integrations/test_ollama.py`

**Local Operation and Privacy: FR40-FR43**

- `privacy.py`
- `config.py`
- `memory/store.py`
- `diagnostics.py`
- `data/config/settings.yaml`
- Tests: `tests/test_config.py`

**Diagnostics and Recovery: FR44-FR48**

- `diagnostics.py`
- `events.py`
- `ui/dashboard.py`
- `integrations/base.py`
- `data/state/integration_health.json`
- `data/logs/app.log`
- `data/logs/events.jsonl`
- Tests: `tests/test_diagnostics.py`, `tests/integrations/test_base.py`

### Integration Points

**Internal Communication:**

The main flow:

```text
cli.py
  → mode_controller.py
    → foreground.py
    → integrations/screenpipe.py
    → state_machine.py
    → context/context_builder.py
      → context/code_context.py
      → context/screen_context.py
      → memory/store.py
    → persona.py
    → model_router.py
      → integrations/ollama.py
    → integrations/tts.py
    → diagnostics.py
      → events.py
```

Status flow:

```text
cli.py status
  → diagnostics.py
    → data/state/current_state.json
    → data/state/integration_health.json
    → data/logs/events.jsonl
```

Dashboard flow:

```text
cli.py dashboard
  → ui/dashboard.py
    → diagnostics.py
    → data/state/
    → data/logs/
```

**External Integrations:**

- Ollama: `integrations/ollama.py`
- Screenpipe: `integrations/screenpipe.py`
- VS Code/Kilo MCP: `integrations/mcp.py`
- Whisper.cpp: `integrations/stt.py`
- Piper/Kokoro: `integrations/tts.py`
- Future Unity logs: future `integrations/unity.py`

**Data Flow:**

```text
Foreground app / Screenpipe / MCP
  → signal/context adapters
  → mode_controller
  → state_machine
  → context_builder
  → privacy filter
  → prompt/persona/model routing
  → Ollama response
  → text/TTS output
  → diagnostics + memory update
```

### File Organization Patterns

**Configuration Files:**

All user-editable config lives in `data/config/`.

- `settings.yaml`: runtime settings, paths, polling intervals
- `model_profiles.yaml`: Ollama model profiles by state
- `thresholds.yaml`: doomscroll, gaming, and intervention thresholds

`config.py` is the only module that should parse these files.

**Source Organization:**

Source code lives under `src/bananalyzer/`.

Use module folders only when there is a clear architectural boundary:

- `integrations/` for external adapters
- `memory/` for persistence and summaries
- `context/` for building model context
- `accountability/` for banana debt and interventions
- `ui/` for dashboard/status UI
- `utils/` only for small generic helpers that do not belong to a domain module

**Test Organization:**

Tests live in top-level `tests/`.

- Root tests cover root modules.
- Subdirectory tests mirror source subpackages.
- Integration adapter tests should mock external tools by default.
- Real external-service tests should be opt-in, not required for normal test runs.

**Asset Organization:**

MVP has no static visual assets.

Runtime-editable assets are:

- prompt files in `data/prompts/`
- memory files in `data/memory/`
- config files in `data/config/`

### Development Workflow Integration

**Development Server Structure:**

There is no web development server.

Development commands:

```bash
uv run bananalyzer run
uv run bananalyzer status
uv run bananalyzer dashboard
uv run bananalyzer diagnose
```

**Build Process Structure:**

MVP does not require a packaged build. `uv` manages the local environment and command execution.

Quality commands:

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```

**Deployment Structure:**

MVP deployment is local execution from the project folder.

Post-MVP deployment may add:

- packaged executable
- tray app
- auto-start
- installer
- update mechanism

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**

All architectural decisions are compatible and reinforce the MVP goal.

The selected Python 3.11+ / uv / Typer / Rich / Textual foundation fits the local-first desktop agent requirements. File-based storage supports inspectability and editability. Adapter boundaries support integration resilience. The CLI/status/dashboard surface supports diagnostics without forcing a full GUI too early.

No contradictory decisions were found.

**Pattern Consistency:**

Implementation patterns support the architectural decisions:

- `snake_case` Python and JSON/YAML naming aligns with Python conventions.
- Canonical state names align with the state machine and persisted state files.
- Dotted lowercase event names align with JSONL diagnostics.
- Adapter result and health-check patterns align with degraded-mode requirements.
- Privacy allowlist rules align with local-first storage and memory boundaries.

**Structure Alignment:**

The project structure supports the full architecture:

- `src/bananalyzer/` cleanly separates orchestration, integrations, memory, context, accountability, UI, diagnostics, and utilities.
- `data/` separates editable config, prompts, memory, state, and logs.
- `tests/` mirrors architectural modules.
- Integration points are isolated under `integrations/`.
- State transitions are centralized in `state_machine.py`.

### Requirements Coverage Validation ✅

**Epic/Feature Coverage:**

No epics were loaded, so coverage was validated against the PRD’s functional requirement categories.

All major features have architectural support:

- Context awareness
- Coding support
- Behavioral accountability
- Companion behavior
- Memory and personalization
- Voice and interaction
- Model and response routing
- Local operation and privacy
- Diagnostics and recovery

**Functional Requirements Coverage:**

All 48 functional requirements are architecturally supported.

Coverage summary:

- FR1-FR5 Context Awareness → `foreground.py`, `state_machine.py`, `mode_controller.py`, `diagnostics.py`
- FR6-FR11 Coding Support → `integrations/mcp.py`, `context/code_context.py`, `context/context_builder.py`
- FR12-FR18 Behavioral Accountability → `integrations/screenpipe.py`, `accountability/`, `data/memory/banana_debt.json`
- FR19-FR23 Companion Behavior → `persona.py`, `model_router.py`, `memory/store.py`, companion prompt files
- FR24-FR29 Memory and Personalization → `memory/`, `privacy.py`, memory files
- FR30-FR34 Voice and Interaction → `cli.py`, `integrations/stt.py`, `integrations/tts.py`
- FR35-FR39 Model and Response Routing → `model_router.py`, `integrations/ollama.py`, `model_profiles.yaml`
- FR40-FR43 Local Operation and Privacy → `privacy.py`, `config.py`, local data files
- FR44-FR48 Diagnostics and Recovery → `diagnostics.py`, `events.py`, `ui/dashboard.py`, health/status files

**Non-Functional Requirements Coverage:**

NFRs are addressed architecturally:

- Performance: local-first execution, state-aware model routing, CPU-side STT/TTS preference, simple polling loop, deferred heavy GUI.
- Privacy/security: local-only defaults, no cloud MVP, explicit persistence allowlist, inspectable local files.
- Reliability/degraded operation: adapter boundaries, health checks, fallback modes for Screenpipe/MCP/STT/TTS failures.
- Integration resilience: `integrations/base.py` contract, integration health file, clear unavailable/degraded states.
- Usability/control: CLI commands, status output, Textual dashboard, editable config/threshold files.
- Maintainability: separated modules, prompt/config files outside core logic, tests mapped to components.

The PRD validation concern about vague NFRs is mitigated by architectural mechanisms for status visibility, integration health, structured logs, bounded persistence, and explicit fallback behavior.

### Implementation Readiness Validation ✅

**Decision Completeness:**

Critical implementation decisions are documented:

- MVP foundation and starter tooling
- Local file-based data architecture
- Integration adapter pattern
- Local-only security/privacy defaults
- CLI and Textual monitoring surface
- Polling-first orchestration
- Deferred post-MVP decisions

Technology versions are defined at a practical level where needed:

- Python 3.11+
- uv project management
- Typer / Rich / Textual
- Pydantic Settings
- pytest / ruff

**Structure Completeness:**

The project structure is complete enough for implementation:

- Root files are identified.
- Source modules are defined.
- Data directories are defined.
- Tests are mapped.
- Integration boundaries are explicit.
- Requirements are mapped to files/directories.

**Pattern Completeness:**

Patterns are comprehensive enough for multiple AI agents to implement consistently:

- Naming conventions
- State naming
- File organization
- Event formats
- Adapter contracts
- Error handling
- Degraded-mode reporting
- Test organization
- Privacy storage rules

### Gap Analysis Results

**Critical Gaps: None**

No implementation-blocking architecture gaps were found.

**Important Gaps: Deferred by Design**

The following are intentionally deferred:

- SQLite or structured database
- Full GUI/tray application
- Installer/packaging
- Auto-start on boot
- Unity log ingestion
- RAG/vector memory
- Cloud sync or multi-user support

These are not MVP blockers.

**Nice-to-Have Gaps:**

Future architecture refinements may define:

- Exact model profile names and context sizes
- Exact Screenpipe signal thresholds
- Exact Textual dashboard layout
- Exact memory summarization cadence and prompt
- Optional local HTTP API if external tools need access later

These can be handled in implementation stories or later architecture updates.

### Validation Issues Addressed

No critical validation issues were found.

The main PRD concern was NFR measurability. The architecture addresses this by requiring:

- `current_state.json`
- `integration_health.json`
- `events.jsonl`
- `app.log`
- CLI `status`
- CLI `diagnose`
- Textual dashboard
- adapter health checks
- explicit degraded-mode status
- bounded persistence and privacy filtering

### Architecture Completeness Checklist

**✅ Requirements Analysis**

- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**✅ Architectural Decisions**

- [x] Critical decisions documented
- [x] Technology stack specified
- [x] Integration patterns defined
- [x] Performance considerations addressed
- [x] Privacy/local-first behavior addressed
- [x] Deferred decisions explicitly listed

**✅ Implementation Patterns**

- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented
- [x] Error/degraded-mode patterns documented
- [x] Examples and anti-patterns provided

**✅ Project Structure**

- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete
- [x] Test organization defined

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High

This architecture is ready to guide implementation because it defines the core stack, project structure, module boundaries, persistence model, diagnostics approach, integration patterns, and consistency rules needed for AI agents to work without conflicting decisions.

**Key Strengths:**

- Strong alignment with local-first MVP goals.
- Simple enough for a Python learner to inspect and modify.
- Clear integration boundaries for fragile local services.
- Explicit degraded-mode behavior.
- Good diagnostics and status visibility from the start.
- Avoids premature GUI/database/cloud complexity.
- Maps every PRD functional category to concrete files and modules.

**Areas for Future Enhancement:**

- Add SQLite when querying history or metrics becomes important.
- Add a polished GUI/tray app after the core loop is reliable.
- Add Unity log ingestion after MCP/Screenpipe/Ollama flow is stable.
- Add RAG/vector memory when Markdown summaries are no longer enough.
- Add packaging/autostart once daily usage is proven.
- Add opt-in sync/cloud only after local privacy behavior is mature.

### Implementation Handoff

**AI Agent Guidelines:**

- Follow all architectural decisions exactly as documented.
- Use implementation patterns consistently across all components.
- Respect project structure and boundaries.
- Do not bypass integration adapters.
- Do not invent new state names.
- Do not store raw OCR/audio/code context unless explicitly allowlisted.
- Refer to this document for all architectural questions.

**First Implementation Priority:**

Initialize the project foundation:

```bash
uv init bananalyzer --app --python 3.11
cd bananalyzer
uv add typer rich textual pydantic pydantic-settings psutil pywin32 httpx
uv add --dev pytest ruff
```

Then create the source/data/test structure defined in this document before implementing feature behavior.

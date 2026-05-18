---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - D:/AICompanionProject/_bmad-output/planning-artifacts/prd.md
  - D:/AICompanionProject/_bmad-output/planning-artifacts/architecture.md
---

# AICompanionProject - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for AICompanionProject, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Ryan can run Bananalyzer as a local desktop companion during normal workstation use.
FR2: Bananalyzer can identify Ryan’s current foreground activity category.
FR3: Bananalyzer can distinguish coding, gaming, doomscrolling, companion/idle, and fallback states.
FR4: Bananalyzer can track state transitions during a session.
FR5: Ryan can inspect the assistant’s current detected state.
FR6: Ryan can ask questions about the active code context.
FR7: Bananalyzer can receive active VS Code file context for coding assistance.
FR8: Bananalyzer can explain code in the active context.
FR9: Bananalyzer can ask clarifying questions that help Ryan reason through implementation issues.
FR10: Bananalyzer can identify likely logic problems or misunderstanding points in the active code context.
FR11: Bananalyzer can adapt its response style for coding support.
FR12: Bananalyzer can detect distraction signals from the user’s environment.
FR13: Bananalyzer can classify likely doomscrolling behavior.
FR14: Bananalyzer can interrupt Ryan during likely doomscrolling events.
FR15: Bananalyzer can track coding time, gaming time, doomscrolling time, and companion/idle time.
FR16: Bananalyzer can calculate a banana debt metric from productive and avoidant activity.
FR17: Bananalyzer can reference current goals or unfinished work during accountability interventions.
FR18: Ryan can adjust intervention intensity or disable overly disruptive behavior.
FR19: Bananalyzer can operate in a lightweight companion mode when Ryan is not actively coding or being interrupted.
FR20: Bananalyzer can use different personas for coding, gaming, doomscrolling, and companion states.
FR21: Bananalyzer can vary tone and response behavior based on the current state.
FR22: Bananalyzer can preserve an evolving companion identity across sessions.
FR23: Ryan can change or extend the personality layer over time.
FR24: Bananalyzer can store persistent session memory.
FR25: Bananalyzer can save goals, recurring mistakes, coding progress, and behavior summaries.
FR26: Bananalyzer can update memory periodically during active sessions.
FR27: Bananalyzer can retrieve relevant memory when responding.
FR28: Ryan can inspect or edit stored memory.
FR29: Bananalyzer can avoid relying on unbounded raw history as its only memory mechanism.
FR30: Ryan can interact with Bananalyzer through text input.
FR31: Ryan can receive spoken responses from Bananalyzer.
FR32: Ryan can optionally ask spoken questions.
FR33: Bananalyzer can continue operating if voice input is unavailable.
FR34: Bananalyzer can continue operating if voice output is unavailable.
FR35: Bananalyzer can route requests to different local model profiles based on current state.
FR36: Bananalyzer can apply state-specific prompt instructions.
FR37: Bananalyzer can apply state-specific response parameters.
FR38: Bananalyzer can choose a lightweight companion profile when low resource usage is preferred.
FR39: Ryan can inspect which model/profile is currently being used.
FR40: Bananalyzer can operate without required cloud services.
FR41: Bananalyzer can keep captured code, OCR, audio-derived text, and memory data local by default.
FR42: Ryan can control whether any future external sharing or sync is enabled.
FR43: Bananalyzer can provide a clear record of what local context is being stored.
FR44: Ryan can view recent state transitions, detections, and integration errors.
FR45: Bananalyzer can continue in degraded mode when an integration is unavailable.
FR46: Bananalyzer can report missing or failed integrations.
FR47: Ryan can tune detection thresholds or configuration values.
FR48: Bananalyzer can fall back to manual/text-only operation when automation components fail.

### NonFunctional Requirements

NFR1: Bananalyzer must preserve normal workstation usability while Unity, VS Code, and games are running.
NFR2: AI GPU memory usage should stay within the configured AI VRAM budget during normal MVP operation.
NFR3: Screenpipe polling must not create noticeable input lag, frame drops, or foreground-app stutter.
NFR4: Foreground activity state should be refreshed within the configured polling interval.
NFR5: Local chat responses should feel interactive enough for coding support and companion use.
NFR6: STT and TTS components should not consume GPU memory in MVP.
NFR7: Memory updates should not interrupt active coding, gaming, or voice interaction.
NFR8: Captured code context, OCR text, audio-derived text, and memory data must remain local by default.
NFR9: No external sharing or cloud sync may occur without explicit user configuration.
NFR10: Stored memory must be inspectable and editable by Ryan.
NFR11: The system must make clear which categories of local context may be stored.
NFR12: Future multi-user or cloud-enabled versions must require explicit consent and data deletion controls.
NFR13: Failure of one integration must not crash the full assistant.
NFR14: If Screenpipe is unavailable, Bananalyzer must still support foreground-state detection and text interaction.
NFR15: If MCP code context is unavailable, Bananalyzer must still support general text interaction.
NFR16: If STT is unavailable, Ryan must still be able to use text input.
NFR17: If TTS is unavailable, Bananalyzer must still produce text output.
NFR18: State transitions and integration failures must be logged for troubleshooting.
NFR19: Each external dependency must have a detectable available/unavailable state.
NFR20: Bananalyzer must report missing or failed integrations clearly enough for Ryan to troubleshoot.
NFR21: Integration polling should use configurable intervals where applicable.
NFR22: Bananalyzer must avoid unbounded context ingestion from Screenpipe, VS Code, logs, or memory.
NFR23: Ryan must be able to reduce or disable disruptive interventions.
NFR24: Ryan must be able to tune doomscroll detection sensitivity.
NFR25: The assistant’s “mean banana” behavior must remain within motivational tone boundaries.
NFR26: The system must provide enough status visibility for Ryan to understand why an intervention occurred.
NFR27: MVP operation should not require a polished GUI, but it must provide usable logs or status output.
NFR28: Prompts should be editable independently from the core orchestration logic.
NFR29: State definitions should be easy to modify or extend.
NFR30: Model profiles should be configurable without rewriting the main control loop.
NFR31: Memory storage should support later migration to RAG or structured retrieval.
NFR32: Integrations should be isolated enough that Screenpipe, MCP, STT, TTS, or Unity support can be improved independently.

### Additional Requirements

- Starter template: initialize a Plain Python + uv app using Python 3.11+, Typer, Rich, Textual, Pydantic, Pydantic Settings, psutil, pywin32, httpx, pytest, and ruff.
- First implementation story must initialize the project foundation with `uv init bananalyzer --app --python 3.11` and add the architecture-specified dependencies.
- Use a `src/bananalyzer/` project structure with separated modules for CLI, config, diagnostics, events, foreground detection, mode controller, model router, persona, privacy, state machine, accountability, context, integrations, memory, UI, and utilities.
- Use local file-based storage under `data/` for config, prompts, memory, state snapshots, and logs.
- Store user-editable config in YAML files: `data/config/settings.yaml`, `model_profiles.yaml`, and `thresholds.yaml`.
- Store runtime state in JSON files: `data/state/current_state.json` and `integration_health.json`.
- Store memory in editable local files: `memory.md`, `session_summary.md`, and `banana_debt.json`.
- Store diagnostics in `data/logs/app.log` and append-only `data/logs/events.jsonl`.
- Use editable prompt files for canonical states: `coding`, `gaming`, `doomscrolling`, `companion`, and `fallback`.
- Enforce canonical persisted state names: `coding`, `gaming`, `doomscrolling`, `companion`, and `fallback`.
- Use adapter boundaries for Ollama, Screenpipe, MCP, STT, TTS, and future Unity log integrations.
- Each integration adapter should expose availability/health methods and return consistent success/failure results.
- Integration failures must degrade gracefully rather than crash the full assistant.
- Use a simple polling orchestration loop for MVP; introduce async only where it simplifies I/O, timeouts, or dashboard responsiveness.
- Provide CLI commands for `run`, `status`, `dashboard`, `diagnose`, and `config`.
- Include a basic Textual dashboard in MVP showing current state, model/profile, integration health, recent detections, memory status, errors, and banana debt/accountability summary.
- Keep MVP local-only with no cloud infrastructure, no authentication, no installer, no tray app, no auto-update, and no required external APIs.
- Use a privacy allowlist for persisted context: goals, summaries, recurring mistakes, banana debt, state transitions, integration health, user-approved memory notes, and minimal diagnostic metadata.
- Do not persist raw Screenpipe OCR, raw audio, large code excerpts, or unbounded logs by default.
- Use structured JSONL events with ISO timestamps, dotted lowercase event names, component, severity, message, and details.
- Centralize state transitions in `state_machine.py`; components must not directly overwrite `current_state.json`.
- Use `privacy.py` as the central place for persistence allowlist and filtering decisions.
- Use `ruff` for formatting/linting and `pytest` for tests.
- Add or update tests for state routing, config loading, adapters, diagnostics, memory, accountability, and degraded-mode behavior.
- Defer SQLite, RAG/vector memory, Unity log ingestion, full GUI/tray app, packaging, auto-start, cloud sync, and multi-user support until post-MVP.

### UX Design Requirements

No dedicated UX Design document was found or included. UX-relevant implementation requirements are covered by the PRD and Architecture diagnostics/control requirements: CLI usability, readable Rich output, usable logs/status output, configurable intervention intensity, inspectable local files, and the basic Textual dashboard.

### Lightweight UX Notes for MVP User-Facing Surfaces

No dedicated UX artifact exists for MVP. The following story-level UX guidance must be preserved during implementation:

- `status` output should show: current state, current model/profile, last transition, integration health, recent errors, memory update status, persistence categories, and degraded-mode explanation.
- `dashboard` should mirror status categories in sections: State, Model, Integrations, Recent Events, Memory, Accountability, Errors.
- `config` output should prioritize discoverability: show config file paths, key editable settings, and safe defaults.
- Text interaction should always display responses as text, even when TTS is enabled.
- Voice interaction should be additive; STT/TTS failure must point Ryan back to text interaction.
- Intervention intensity should affect wording, frequency, and delivery behavior without bypassing tone boundaries.
- Mean banana tone may be direct or sarcastic, but not abusive, discriminatory, protected-class-targeted, or self-harm-reinforcing.

### FR Coverage Map

FR1: Epic 1 - Run Bananalyzer as a local desktop companion.
FR2: Epic 2 - Identify foreground activity category.
FR3: Epic 2 - Distinguish coding, gaming, doomscrolling, companion, fallback.
FR4: Epic 1 - Track state transitions in session diagnostics.
FR5: Epic 1 - Inspect current detected state.
FR6: Epic 3 - Ask questions about active code.
FR7: Epic 3 - Receive VS Code active file context.
FR8: Epic 3 - Explain active code context.
FR9: Epic 3 - Ask clarifying rubber-duck questions.
FR10: Epic 3 - Identify logic problems or misunderstandings.
FR11: Epic 2 - Adapt response style for coding support.
FR12: Epic 5 - Detect distraction signals.
FR13: Epic 5 - Classify likely doomscrolling.
FR14: Epic 5 - Interrupt likely doomscrolling.
FR15: Epic 5 - Track coding/gaming/doomscroll/companion time.
FR16: Epic 5 - Calculate banana debt.
FR17: Epic 5 - Reference goals/unfinished work during interventions.
FR18: Epic 5 - Adjust or disable disruptive interventions.
FR19: Epic 2 - Operate in lightweight companion mode.
FR20: Epic 2 - Use different personas per state.
FR21: Epic 2 - Vary tone and response behavior by state.
FR22: Epic 4 - Preserve evolving identity across sessions.
FR23: Epic 4 - Change or extend personality layer.
FR24: Epic 4 - Store persistent session memory.
FR25: Epic 4 - Save goals, mistakes, progress, summaries.
FR26: Epic 4 - Update memory periodically.
FR27: Epic 4 - Retrieve relevant memory.
FR28: Epic 4 - Inspect or edit stored memory.
FR29: Epic 4 - Avoid unbounded raw-history memory.
FR30: Epic 1 / Epic 6 - Epic 1 provides the reliable text interaction baseline; Epic 6 extends interaction with voice features.
FR31: Epic 6 - Spoken responses.
FR32: Epic 6 - Optional spoken questions.
FR33: Epic 1 / Epic 6 - Epic 1 ensures text input works when voice input is unavailable; Epic 6 adds STT-specific degraded behavior.
FR34: Epic 1 / Epic 6 - Epic 1 ensures responses are displayed as text when voice output is unavailable; Epic 6 adds TTS-specific degraded behavior.
FR35: Epic 2 - Route requests to local model profiles.
FR36: Epic 2 - Apply state-specific prompts.
FR37: Epic 2 - Apply state-specific response parameters.
FR38: Epic 2 - Choose lightweight companion profile.
FR39: Epic 1 - Inspect current model/profile.
FR40: Epic 1 - Operate without cloud services.
FR41: Epic 4 - Keep captured data local by default.
FR42: Epic 4 - Control future sharing/sync.
FR43: Epic 1 - Record what local context is stored.
FR44: Epic 1 - View transitions, detections, integration errors.
FR45: Epic 1 - Continue in degraded mode.
FR46: Epic 1 - Report failed/missing integrations.
FR47: Epic 2 - Tune thresholds/configuration.
FR48: Epic 1 - Fall back to manual/text-only operation.

## Epic List

### Epic 1: Local Companion Foundation and Operational Visibility
Ryan can install/run Bananalyzer locally, inspect its current state, and trust the basic runtime, config, logs, and diagnostics before behavior features are layered on.

**FRs covered:** FR1, FR4, FR5, FR30, FR33, FR34, FR39, FR40, FR43, FR44, FR45, FR46, FR48

### Epic 2: Context-Aware Mode Detection and Routing
Ryan gets an assistant that recognizes coding, gaming, doomscrolling, companion, and fallback states, then routes persona/model/prompt behavior accordingly.

**FRs covered:** FR2, FR3, FR11, FR19, FR20, FR21, FR35, FR36, FR37, FR38, FR47

### Epic 3: Active Code Companion for Rubber-Duck Support
Ryan can ask questions about the active VS Code context and receive coding explanations, clarifying questions, and reasoning support.

**FRs covered:** FR6, FR7, FR8, FR9, FR10

### Epic 4: Local Memory and Evolving Companion Identity
Ryan gets persistent memory for goals, summaries, recurring mistakes, behavior history, and persona continuity while keeping stored memory inspectable and bounded.

**FRs covered:** FR22, FR23, FR24, FR25, FR26, FR27, FR28, FR29, FR41, FR42

### Epic 5: Behavioral Accountability and Distraction Interventions
Ryan gets doomscroll/gaming accountability: distraction signals, banana debt, time tracking, goal-aware interventions, and configurable intensity.

**FRs covered:** FR12, FR13, FR14, FR15, FR16, FR17, FR18

### Epic 6: Voice Interaction and Graceful Voice Fallbacks
Ryan can receive spoken responses, optionally use spoken input, and keep working when STT/TTS is unavailable because the text interaction baseline already exists.

**FRs covered:** FR31, FR32, plus STT/TTS-specific extensions of FR33 and FR34

## Epic 1: Local Companion Foundation and Operational Visibility

Ryan can install/run Bananalyzer locally, inspect its current state, and trust the basic runtime, config, logs, and diagnostics before behavior features are layered on.

### Story 1.1: Set Up Initial Project from Starter Template

As Ryan,
I want a local Python project foundation for Bananalyzer,
So that I can run and develop the companion from my workstation.

**Acceptance Criteria:**

**Given** the project has not yet been initialized
**When** the developer initializes the app foundation
**Then** the project uses Python 3.11+ with `uv` and a `src/bananalyzer/` package layout
**And** dependencies include Typer, Rich, Textual, Pydantic, Pydantic Settings, psutil, pywin32, and httpx.

**Given** the project foundation exists
**When** development dependencies are installed
**Then** pytest and ruff are available through `uv run`
**And** placeholder tests can run successfully.

**Given** Ryan opens the project
**When** he inspects the source tree
**Then** the architecture modules exist for CLI, config, diagnostics, events, foreground detection, mode controller, model router, persona, privacy, state machine, integrations, memory, UI, accountability, context, and utilities.

**Given** this is a personal local MVP
**When** quality automation is configured
**Then** local `uv run pytest` and `uv run ruff check .` commands are available
**And** remote CI/CD is documented as optional and out of scope unless Ryan chooses to add it later.

### Story 1.2: Create Local Data, Config, State, and Log Files

As Ryan,
I want Bananalyzer to use inspectable local files for configuration and runtime data,
So that I can understand and modify what the assistant stores.

**Acceptance Criteria:**

**Given** the Bananalyzer project exists
**When** the data foundation is created
**Then** local directories exist for `data/config`, `data/memory`, `data/prompts`, `data/state`, and `data/logs`
**And** no cloud service or external storage is required.

**Given** Ryan inspects `data/config`
**When** configuration files are present
**Then** `settings.yaml`, `model_profiles.yaml`, and `thresholds.yaml` exist with initial MVP-safe defaults.

**Given** Ryan inspects runtime storage
**When** foundation-level state, memory, and log files are present
**Then** `current_state.json`, `integration_health.json`, `app.log`, and `events.jsonl` exist or are created on first run
**And** `memory.md`, `session_summary.md`, and `banana_debt.json` may exist only as empty inspectable scaffolding until Epic 4 and Epic 5 implement memory/accountability behavior.

**Given** captured context may later be persisted
**When** storage defaults are defined
**Then** the persisted context categories are limited to approved local categories such as goals, summaries, state transitions, integration health, user-approved memory notes, and minimal diagnostics.

### Story 1.3: Provide CLI Commands for Local Operation

As Ryan,
I want simple CLI commands for running and inspecting Bananalyzer,
So that I can operate the assistant without needing a polished GUI.

**Acceptance Criteria:**

**Given** the project is installed in the local `uv` environment
**When** Ryan runs `uv run bananalyzer --help`
**Then** the CLI lists commands for `run`, `status`, `dashboard`, `diagnose`, and `config`.

**Given** Ryan starts the assistant
**When** he runs `uv run bananalyzer run`
**Then** Bananalyzer starts a local MVP runtime loop or safe placeholder loop
**And** it does not require cloud credentials, login, or remote services.

**Given** Ryan wants operational visibility
**When** he runs `uv run bananalyzer status`
**Then** the command prints the current state, current model/profile placeholder, integration health summary, and recent event summary.

**Given** Ryan wants troubleshooting output
**When** he runs `uv run bananalyzer diagnose`
**Then** the command reports local configuration paths, data file availability, and missing integration placeholders without crashing.

**Given** Ryan wants to view configuration
**When** he runs `uv run bananalyzer config`
**Then** the command displays the active local config file paths and key editable settings.

### Story 1.4: Record State Transitions and Runtime Events

As Ryan,
I want Bananalyzer to record state and runtime events locally,
So that I can understand what the assistant detected and why it acted.

**Acceptance Criteria:**

**Given** Bananalyzer starts
**When** a runtime event occurs
**Then** an event is appended to `data/logs/events.jsonl`
**And** each event includes `timestamp`, `event_type`, `component`, `severity`, `message`, and `details`.

**Given** Bananalyzer has a current operating state
**When** the state is initialized or changed
**Then** `data/state/current_state.json` is updated with canonical state values only: `coding`, `gaming`, `doomscrolling`, `companion`, or `fallback`.

**Given** state changes are recorded
**When** Ryan inspects the event log
**Then** state transitions use event names such as `state.changed`
**And** timestamps are ISO 8601 strings.

**Given** a component detects a condition but does not change state
**When** the detection is useful for diagnostics
**Then** Bananalyzer may emit `state.detected` without incorrectly changing the current state.

### Story 1.5: Report Integration Health and Degraded Modes

As Ryan,
I want Bananalyzer to report missing or failed integrations clearly,
So that one broken dependency does not make the whole assistant unusable.

**Acceptance Criteria:**

**Given** integration health is checked
**When** an integration is unavailable
**Then** `data/state/integration_health.json` records the component, availability, status, last check time, last error, and degraded mode.

**Given** optional integrations are missing
**When** Bananalyzer runs diagnostics
**Then** Screenpipe, MCP, STT, and TTS failures are reported as degraded or unavailable
**And** the assistant does not crash solely because those integrations are missing.

**Given** Ollama is unavailable
**When** Bananalyzer runs diagnostics
**Then** the model unavailability is clearly reported
**And** status output explains that generation is unavailable until Ollama is restored.

**Given** integration health is displayed
**When** Ryan runs `status` or `diagnose`
**Then** each integration uses consistent statuses: `available`, `unavailable`, `degraded`, or `unknown`.

### Story 1.6: Show Operational Status to Ryan

As Ryan,
I want one clear operational status view,
So that I can see what Bananalyzer thinks is happening and what data it may store.

**Acceptance Criteria:**

**Given** Bananalyzer has local state and diagnostic files
**When** Ryan runs `uv run bananalyzer status`
**Then** the output shows current state, current model/profile placeholder, last state transition, integration health, recent errors, and memory update status.

**Given** Ryan opens the dashboard command
**When** he runs `uv run bananalyzer dashboard`
**Then** a basic Textual dashboard or safe dashboard placeholder opens
**And** it displays the same core operational categories as status output.

**Given** Ryan wants privacy visibility
**When** status or diagnostics are shown
**Then** Bananalyzer lists the categories of context allowed for local persistence
**And** it does not claim to store raw OCR, raw audio, large code excerpts, or unbounded history by default.

**Given** the assistant is in degraded mode
**When** Ryan views status
**Then** the degraded mode is visible with a plain-language explanation of what still works.

### Story 1.7: Provide Reliable Text Interaction Baseline

As Ryan,
I want to interact with Bananalyzer through text,
So that the assistant remains usable before voice features are stable and when automation components are degraded.

**Acceptance Criteria:**

**Given** Bananalyzer is running locally
**When** Ryan enters a text question or command
**Then** the assistant can accept and display text interaction through the local CLI/runtime path.

**Given** state-specific prompt/model routing is not fully implemented yet
**When** Ryan uses text interaction during the foundation phase
**Then** Bananalyzer uses the current safe placeholder or available routing path without requiring STT, TTS, Screenpipe, or MCP.

**Given** voice integrations are unavailable
**When** Ryan uses text input
**Then** text interaction continues to work.

**Given** a response is generated or a placeholder response is produced
**When** TTS is disabled or unavailable
**Then** the response is still displayed as text.

**Given** Ryan views status or diagnostics
**When** text interaction is available
**Then** the system reports text interaction as the baseline supported interaction mode.

## Epic 2: Context-Aware Mode Detection and Routing

Ryan gets an assistant that recognizes coding, gaming, doomscrolling, companion, and fallback states, then routes persona/model/prompt behavior accordingly.

### Story 2.1: Detect Foreground Activity Categories

As Ryan,
I want Bananalyzer to identify what kind of app I am actively using,
So that the assistant can infer whether I am coding, gaming, distracted, idle, or in fallback mode.

**Acceptance Criteria:**

**Given** Bananalyzer is running on Windows 11
**When** the foreground activity monitor checks the active window/process
**Then** it returns a candidate activity category with process/window metadata
**And** the monitor does not decide the final assistant state by itself.

**Given** Ryan is using VS Code, Unity, or another configured development tool
**When** foreground detection runs
**Then** the candidate activity category can be classified as coding-related.

**Given** Ryan is using Steam, PUBG, or another configured game/game launcher
**When** foreground detection runs
**Then** the candidate activity category can be classified as gaming-related.

**Given** foreground activity cannot be read or mapped
**When** detection fails or returns an unknown app
**Then** the monitor returns an unknown/fallback-safe signal
**And** the assistant continues running.

### Story 2.2: Implement Canonical State Machine

As Ryan,
I want Bananalyzer to convert activity signals into clear operating states,
So that the assistant behaves consistently instead of inventing random modes.

**Acceptance Criteria:**

**Given** the state machine receives activity signals
**When** it determines the current mode
**Then** it uses only canonical state values: `coding`, `gaming`, `doomscrolling`, `companion`, and `fallback`.

**Given** the current state changes
**When** the state machine accepts a transition
**Then** it records the previous state, current state, reason, confidence, and timestamp
**And** emits a `state.changed` event.

**Given** a signal is detected but does not justify a transition
**When** the state machine evaluates it
**Then** the current state remains unchanged
**And** diagnostic detection can be emitted without corrupting the state.

**Given** an invalid state value is requested
**When** the state machine validates the transition
**Then** the invalid value is rejected
**And** the system remains in a safe existing or fallback state.

### Story 2.3: Configure State-Specific Prompts and Personas

As Ryan,
I want Bananalyzer to use different prompt/persona behavior for each state,
So that coding help, gaming nudges, doomscroll interruptions, and companion mode feel distinct.

**Acceptance Criteria:**

**Given** prompt files exist in `data/prompts`
**When** Bananalyzer loads persona behavior
**Then** it can load editable prompts for `coding`, `gaming`, `doomscrolling`, `companion`, and `fallback`.

**Given** the current state is `coding`
**When** prompt routing occurs
**Then** the coding prompt is selected
**And** the response style supports technical explanation and rubber-duck questioning.

**Given** the current state is `gaming`, `doomscrolling`, or `companion`
**When** prompt routing occurs
**Then** the matching state prompt is selected
**And** the assistant tone changes according to that state.

**Given** a prompt file is missing or unreadable
**When** prompt routing occurs
**Then** Bananalyzer falls back to a safe default prompt
**And** logs the degraded prompt state.

### Story 2.4: Route Model Profiles by State

As Ryan,
I want Bananalyzer to choose local model settings based on the current state,
So that coding can use stronger settings while companion mode can stay lightweight.

**Acceptance Criteria:**

**Given** model profiles are configured locally
**When** Bananalyzer enters a state
**Then** the model router selects the configured model profile for that state.

**Given** the current state is `companion`
**When** model routing occurs
**Then** the router can choose a lightweight companion profile when low resource usage is preferred.

**Given** the current state is `coding`
**When** model routing occurs
**Then** the router can choose coding-oriented parameters such as model name, context limit, and temperature from config.

**Given** a configured model profile is missing or invalid
**When** model routing occurs
**Then** Bananalyzer reports the issue in status/diagnostics
**And** falls back to a safe configured default or marks generation unavailable.

### Story 2.5: Run Companion and Fallback Modes Safely

As Ryan,
I want Bananalyzer to stay useful when I am idle or when detection is uncertain,
So that it does not become noisy or crash when context is limited.

**Acceptance Criteria:**

**Given** Ryan is not actively coding, gaming, or doomscrolling
**When** state evaluation occurs
**Then** Bananalyzer can enter `companion` mode
**And** uses lightweight prompt/model behavior.

**Given** foreground detection or context signals are unavailable
**When** state evaluation cannot confidently classify activity
**Then** Bananalyzer enters or remains in `fallback` mode
**And** continues to support safe text-based interaction through the Epic 1 text interaction baseline.

**Given** Bananalyzer is in `companion` mode
**When** Ryan asks a general question
**Then** the assistant responds with companion-appropriate tone
**And** does not require code context, Screenpipe, STT, or TTS to function.

**Given** Bananalyzer is in `fallback` mode
**When** Ryan views status
**Then** the output explains why fallback mode is active
**And** what capabilities still work.

### Story 2.6: Tune Detection and Routing Settings

As Ryan,
I want activity detection and routing behavior to be configurable,
So that I can adjust Bananalyzer without rewriting the main loop.

**Acceptance Criteria:**

**Given** Ryan opens the local config files
**When** he inspects activity and routing settings
**Then** polling intervals, app/category mappings, state thresholds, model profiles, and prompt paths are editable through local YAML config.

**Given** config values are changed
**When** Bananalyzer loads configuration
**Then** the new values are applied without source-code changes.

**Given** a config value is missing or invalid
**When** Bananalyzer starts or runs diagnostics
**Then** the issue is reported clearly
**And** safe defaults are used where possible.

**Given** Ryan wants to tune behavior
**When** he runs the config CLI command
**Then** Bananalyzer shows the relevant config file paths and key detection/routing settings.

## Epic 3: Active Code Companion for Rubber-Duck Support

Ryan can ask questions about the active VS Code context and receive coding explanations, clarifying questions, and reasoning support.

### Story 3.1: Connect to Active VS Code Context

As Ryan,
I want Bananalyzer to retrieve my active VS Code context,
So that the assistant can understand the code I am currently looking at.

**Acceptance Criteria:**

**Given** the MCP/Kilo integration is configured
**When** Bananalyzer requests active code context
**Then** the request goes through `integrations/mcp.py`
**And** no other module directly calls the MCP integration.

**Given** VS Code has an active file or editor context
**When** the MCP adapter retrieves context
**Then** it returns the active file metadata and relevant visible or selected code context.

**Given** MCP is unavailable or returns an error
**When** Bananalyzer requests active code context
**Then** the adapter returns a recoverable unavailable/degraded result
**And** the assistant continues running.

**Given** MCP health is checked
**When** Ryan runs status or diagnostics
**Then** MCP availability is visible in integration health output.

### Story 3.2: Build Bounded Coding Context

As Ryan,
I want Bananalyzer to use only relevant bounded code context,
So that coding help stays useful without bloating prompts or storing too much code.

**Acceptance Criteria:**

**Given** active code context is retrieved
**When** Bananalyzer prepares a coding prompt
**Then** `context/code_context.py` and `context/context_builder.py` convert it into bounded prompt context.

**Given** the active file contains more code than the configured context limit
**When** prompt context is built
**Then** Bananalyzer includes only the allowed bounded excerpt, selected text, visible range, or summarized context.

**Given** code context may be logged or stored
**When** privacy filtering runs
**Then** raw large code excerpts are not persisted by default
**And** only approved metadata or summaries are allowed.

**Given** context is unavailable
**When** the context builder runs
**Then** it returns a clear no-context result rather than failing the full response flow.

### Story 3.3: Answer Questions About Active Code

As Ryan,
I want to ask questions about the code I am viewing,
So that I can understand implementation details and make progress faster.

**Acceptance Criteria:**

**Given** Bananalyzer is in `coding` mode and active code context is available
**When** Ryan asks a question about the active code
**Then** the assistant includes the bounded code context in the prompt sent through the model router.

**Given** the assistant answers a coding question
**When** the response is generated
**Then** it references the active code context where relevant
**And** avoids pretending to know files or code that were not provided.

**Given** Ryan asks a general coding question while active context exists
**When** the assistant responds
**Then** it can combine general programming guidance with the provided active context.

**Given** model generation is unavailable
**When** Ryan asks a coding question
**Then** Bananalyzer reports that local generation is unavailable
**And** status/diagnostics explain the model issue.

### Story 3.4: Provide Rubber-Duck Clarifying Questions

As Ryan,
I want Bananalyzer to ask clarifying questions while helping with code,
So that I reason through implementation issues instead of only receiving answers.

**Acceptance Criteria:**

**Given** Bananalyzer is in `coding` mode
**When** Ryan asks a vague debugging question such as “why isn’t this working?”
**Then** the assistant asks targeted clarifying questions based on the active context.

**Given** active code context suggests multiple possible causes
**When** the assistant responds
**Then** it presents the likely reasoning paths clearly
**And** asks Ryan to confirm assumptions before committing to a conclusion.

**Given** Ryan asks for direct explanation instead of coaching
**When** the assistant responds
**Then** it still provides useful explanation
**And** may include a small number of clarifying prompts without blocking progress.

**Given** the coding prompt is loaded
**When** rubber-duck behavior is applied
**Then** the behavior comes from the coding persona/prompt configuration rather than hardcoded unrelated logic.

### Story 3.5: Identify Likely Logic Issues

As Ryan,
I want Bananalyzer to point out likely logic gaps in my active code,
So that I can catch mistakes faster while learning.

**Acceptance Criteria:**

**Given** active code context is available
**When** Ryan asks for debugging or review help
**Then** the assistant can identify likely logic problems, suspicious assumptions, or misunderstood control flow in the provided context.

**Given** the assistant identifies a possible issue
**When** it explains the issue
**Then** it distinguishes evidence from speculation
**And** avoids claiming certainty beyond the provided active context.

**Given** several issues are possible
**When** the assistant responds
**Then** it prioritizes the most likely or most blocking issues first.

**Given** the active context is too limited to diagnose confidently
**When** the assistant responds
**Then** it asks for the missing information or suggests what context Ryan should provide next.

### Story 3.6: Degrade Gracefully Without Code Context

As Ryan,
I want Bananalyzer to keep helping even when VS Code context is unavailable,
So that MCP failures do not break the whole assistant.

**Acceptance Criteria:**

**Given** MCP or active file context is unavailable
**When** Ryan asks a coding question
**Then** Bananalyzer continues with general text interaction through the Epic 1 text interaction baseline
**And** clearly states that active code context is unavailable.

**Given** Bananalyzer is in degraded coding support
**When** Ryan views status or diagnostics
**Then** the unavailable MCP/code-context state is visible.

**Given** code context retrieval fails during a session
**When** the failure occurs
**Then** Bananalyzer logs the recoverable integration failure
**And** does not crash the runtime loop.

**Given** active code context becomes available again
**When** health/context retrieval succeeds
**Then** Bananalyzer can return to context-aware coding support.

## Epic 4: Local Memory and Evolving Companion Identity

Ryan gets persistent memory for goals, summaries, recurring mistakes, behavior history, and persona continuity while keeping stored memory inspectable and bounded.

### Story 4.1: Create Editable Local Memory Store

As Ryan,
I want Bananalyzer to keep memory in editable local files,
So that I can inspect and change what the companion remembers.

**Acceptance Criteria:**

**Given** the local data structure exists
**When** memory storage is initialized
**Then** `data/memory/memory.md`, `data/memory/session_summary.md`, and `data/memory/banana_debt.json` exist or are created safely on first run.

**Given** Bananalyzer reads or writes memory
**When** memory access occurs
**Then** memory file operations go through `memory/store.py`
**And** unrelated modules do not directly mutate memory files.

**Given** a memory file is missing
**When** Bananalyzer starts or memory is accessed
**Then** the missing file is recreated with safe initial content
**And** the event is logged.

**Given** memory storage is unavailable or unwritable
**When** Bananalyzer attempts a memory operation
**Then** the runtime continues in a no-memory degraded mode
**And** status/diagnostics report the issue.

### Story 4.2: Save Goals, Progress, Mistakes, and Summaries

As Ryan,
I want Bananalyzer to remember useful development and behavior context,
So that the companion feels continuous across sessions.

**Acceptance Criteria:**

**Given** Ryan provides or approves a goal
**When** Bananalyzer saves memory
**Then** the goal can be persisted in local memory.

**Given** a coding session produces useful learning context
**When** Bananalyzer updates memory
**Then** it can save coding progress, recurring mistakes, and concise behavior summaries.

**Given** gaming or distraction activity affects accountability
**When** behavior memory is updated
**Then** banana debt or behavior summary data can be persisted in the appropriate local memory file.

**Given** raw runtime history exists
**When** Bananalyzer writes memory
**Then** it stores concise summaries or approved memory notes rather than unbounded raw logs.

### Story 4.3: Apply Privacy Filtering Before Memory Writes

As Ryan,
I want Bananalyzer to filter captured context before storing memory,
So that private code, OCR, and audio-derived text are not saved carelessly.

**Acceptance Criteria:**

**Given** context is about to be written to memory
**When** privacy filtering runs
**Then** `privacy.py` checks the data against the persistence allowlist.

**Given** raw Screenpipe OCR, raw audio transcript, large code excerpts, or unbounded logs are present
**When** memory persistence is attempted
**Then** those raw data categories are rejected by default
**And** only approved summaries or metadata may be stored.

**Given** a memory write is blocked by privacy rules
**When** diagnostics are enabled
**Then** Bananalyzer logs a safe metadata-only event
**And** does not leak the blocked raw content into logs.

**Given** Ryan explicitly approves a memory note
**When** the note matches allowed memory categories
**Then** it can be persisted as a user-approved local memory entry.

### Story 4.4: Update Session Memory Periodically

As Ryan,
I want Bananalyzer to update session memory during use,
So that useful progress is captured without interrupting my work.

**Acceptance Criteria:**

**Given** Bananalyzer is running an active session
**When** the configured memory update interval is reached
**Then** it creates or updates a concise session summary.

**Given** Ryan is actively coding, gaming, or using voice interaction
**When** a memory update is due
**Then** the update does not interrupt the foreground workflow or block interaction noticeably.

**Given** there is no meaningful new information to summarize
**When** the memory updater runs
**Then** it can skip the update
**And** emit a `memory.skipped` event.

**Given** memory update succeeds
**When** the update completes
**Then** Bananalyzer emits a `memory.updated` event
**And** status output can show the last memory update time.

### Story 4.5: Retrieve Relevant Memory for Responses

As Ryan,
I want Bananalyzer to use relevant stored memory when responding,
So that it remembers my goals, patterns, and prior progress.

**Acceptance Criteria:**

**Given** local memory contains goals or session summaries
**When** Bananalyzer prepares a response
**Then** `memory/retrieval.py` can retrieve bounded relevant memory for the current state.

**Given** memory retrieval finds relevant entries
**When** prompt context is built
**Then** only bounded memory snippets or summaries are included.

**Given** memory contains no relevant entries
**When** Bananalyzer prepares a response
**Then** the assistant responds normally without inventing memory.

**Given** memory retrieval fails
**When** a response is prepared
**Then** Bananalyzer continues without memory context
**And** reports degraded memory retrieval in diagnostics.

### Story 4.6: Inspect and Edit Companion Identity

As Ryan,
I want to inspect and edit the companion’s memory and identity files,
So that the banana persona can evolve without being trapped in code.

**Acceptance Criteria:**

**Given** Ryan opens local memory and prompt/persona files
**When** he edits approved persona or memory content
**Then** Bananalyzer can load the updated content without source-code changes.

**Given** Bananalyzer displays status or config paths
**When** Ryan wants to inspect identity/memory storage
**Then** the relevant `data/memory` and `data/prompts` file paths are visible.

**Given** a persona or memory file contains invalid formatting
**When** Bananalyzer loads it
**Then** it reports the issue clearly
**And** falls back to safe default behavior where possible.

**Given** Ryan changes the personality layer
**When** the next relevant response is generated
**Then** Bananalyzer uses the updated local persona/memory inputs within the current state’s prompt behavior.

### Story 4.7: Control Future Sharing or Sync Defaults

As Ryan,
I want future sharing or sync behavior to be explicit opt-in,
So that local-first privacy is preserved by default.

**Acceptance Criteria:**

**Given** MVP local configuration is initialized
**When** sharing or sync settings are inspected
**Then** external sharing/sync is disabled by default.

**Given** no explicit sharing/sync configuration is enabled
**When** Bananalyzer runs normally
**Then** captured code, OCR, audio-derived text, memory, and diagnostics remain local.

**Given** future sync/cloud settings are represented in config
**When** Ryan views config or diagnostics
**Then** the disabled/default status is visible.

**Given** a future implementation enables sharing or sync
**When** that feature is configured
**Then** it must require explicit user configuration before any external data sharing occurs.

## Epic 5: Behavioral Accountability and Distraction Interventions

Ryan gets doomscroll/gaming accountability: distraction signals, banana debt, time tracking, goal-aware interventions, and configurable intensity.

### Story 5.1: Collect Distraction Signals Through Screenpipe Adapter

As Ryan,
I want Bananalyzer to collect distraction-related environment signals locally,
So that it can detect avoidance patterns without relying only on foreground app names.

**Acceptance Criteria:**

**Given** Screenpipe is configured locally
**When** Bananalyzer queries environmental context
**Then** the request goes through `integrations/screenpipe.py`
**And** no other module directly calls Screenpipe.

**Given** Screenpipe returns OCR, app/window, browser, or activity context
**When** the adapter processes the response
**Then** it returns summarized distraction signals rather than raw persistence-ready OCR.

**Given** Screenpipe polling is configured
**When** Bananalyzer runs normally
**Then** polling uses the configured interval
**And** avoids continuous high-frequency queries that could cause noticeable lag.

**Given** Screenpipe is unavailable or errors
**When** the adapter is queried
**Then** it returns a recoverable degraded result
**And** the assistant continues running.

### Story 5.2: Classify Doomscrolling From Multiple Signals

As Ryan,
I want Bananalyzer to classify likely doomscrolling only when enough evidence exists,
So that it interrupts real distraction loops without becoming annoying from false positives.

**Acceptance Criteria:**

**Given** Screenpipe and foreground signals are available
**When** distraction classification runs
**Then** Bananalyzer evaluates multiple signals such as app/category, OCR patterns, browser context, repetition, and duration where available.

**Given** signals exceed configured doomscroll thresholds
**When** classification completes
**Then** Bananalyzer can classify the current behavior as likely `doomscrolling`.

**Given** signals are weak or conflicting
**When** classification completes
**Then** Bananalyzer avoids triggering doomscroll mode
**And** may log a low-confidence detection for diagnostics.

**Given** threshold settings are changed
**When** classification runs afterward
**Then** the updated thresholds affect classification without source-code changes.

### Story 5.3: Track Activity Time by State

As Ryan,
I want Bananalyzer to track time spent in each activity state,
So that coding, gaming, doomscrolling, and companion time become visible.

**Acceptance Criteria:**

**Given** the state machine emits state transitions
**When** Bananalyzer observes those transitions
**Then** it updates session-level time totals for coding, gaming, doomscrolling, and companion/fallback activity.

**Given** Ryan views status or diagnostics
**When** activity totals are available
**Then** Bananalyzer displays current session time by state.

**Given** the assistant stops or restarts
**When** activity tracking resumes
**Then** it can preserve or summarize prior session activity according to local memory/config behavior.

**Given** a state transition is missing or invalid
**When** activity tracking runs
**Then** it avoids corrupting totals
**And** logs a diagnostic warning.

### Story 5.4: Calculate and Persist Banana Debt

As Ryan,
I want Bananalyzer to calculate banana debt from productive and avoidant activity,
So that gaming and doomscrolling become visible tradeoffs against coding goals.

**Acceptance Criteria:**

**Given** activity time totals exist
**When** banana debt is calculated
**Then** productive coding time and avoidant doomscrolling/gaming time affect the banana debt value according to local config.

**Given** banana debt changes
**When** the value is updated
**Then** it is persisted to `data/memory/banana_debt.json`.

**Given** Ryan views status or the dashboard
**When** banana debt exists
**Then** the current banana debt/accountability summary is visible.

**Given** banana debt storage is unavailable
**When** the assistant tries to update it
**Then** Bananalyzer reports memory degraded mode
**And** continues running without crashing.

### Story 5.5: Trigger Goal-Aware Accountability Interventions

As Ryan,
I want Bananalyzer to interrupt likely avoidance behavior with relevant reminders,
So that I can return to my coding goals before losing too much time.

**Acceptance Criteria:**

**Given** Bananalyzer classifies likely doomscrolling
**When** intervention thresholds are reached
**Then** it triggers an accountability intervention.

**Given** Ryan has current goals or unfinished work in memory
**When** an intervention is generated
**Then** Bananalyzer can reference those goals or unfinished work in the intervention.

**Given** no relevant goals are available
**When** an intervention is generated
**Then** Bananalyzer still provides a general accountability nudge without inventing goals.

**Given** an intervention is triggered
**When** diagnostics are recorded
**Then** Bananalyzer emits an `intervention.triggered` event with safe metadata.

### Story 5.6: Configure Intervention Intensity and Sensitivity

As Ryan,
I want to tune doomscroll sensitivity and intervention intensity,
So that Bananalyzer helps without becoming too disruptive.

**Acceptance Criteria:**

**Given** Ryan opens local threshold/config files
**When** he inspects accountability settings
**Then** doomscroll thresholds, gaming thresholds, intervention cooldowns, and intensity settings are editable.

**Given** Ryan lowers intervention intensity
**When** accountability interventions occur
**Then** the assistant uses less disruptive wording, frequency, or delivery behavior according to config.

**Given** Ryan disables or reduces disruptive behavior
**When** thresholds or intensity settings are applied
**Then** Bananalyzer respects those settings without source-code changes.

**Given** accountability config is invalid
**When** Bananalyzer loads settings
**Then** it reports the problem clearly
**And** uses safe conservative defaults.

### Story 5.7: Enforce Motivational Tone Boundaries

As Ryan,
I want the mean banana persona to stay motivational rather than harmful,
So that accountability remains useful instead of abusive.

**Acceptance Criteria:**

**Given** an intervention prompt is generated
**When** tone boundaries are applied
**Then** sarcastic, direct, or accountability-focused language is allowed
**And** abusive, discriminatory, protected-class insults, or self-harm-reinforcing language is not allowed.

**Given** the current state is `doomscrolling` or `gaming`
**When** persona behavior is selected
**Then** Bananalyzer uses the matching accountability persona while still enforcing safety boundaries.

**Given** Ryan changes personality intensity
**When** interventions are generated later
**Then** the tone changes within allowed boundaries.

**Given** a prompt/persona file would violate tone rules
**When** it is loaded or used
**Then** Bananalyzer applies safe fallback behavior or reports the unsafe prompt issue.

### Story 5.8: Degrade Gracefully Without Screenpipe

As Ryan,
I want accountability features to fail safely when Screenpipe is unavailable,
So that the assistant still works even without environmental context.

**Acceptance Criteria:**

**Given** Screenpipe is unavailable
**When** Bananalyzer runs
**Then** foreground detection and text interaction continue to work.

**Given** Screenpipe is unavailable
**When** doomscroll classification would require Screenpipe signals
**Then** Bananalyzer reports Screenpipe-dependent detection as degraded
**And** avoids pretending it has OCR/browser evidence.

**Given** Screenpipe fails during a session
**When** the failure is detected
**Then** Bananalyzer updates integration health and emits a recoverable integration event.

**Given** Screenpipe becomes available again
**When** health checks succeed
**Then** Bananalyzer can resume Screenpipe-backed distraction detection.

## Epic 6: Voice Interaction and Graceful Voice Fallbacks

Ryan can receive spoken responses, optionally use spoken input, and keep working when STT/TTS is unavailable because the text interaction baseline already exists.

Text interaction baseline is delivered in Epic 1. Epic 6 extends the interaction model with TTS, optional STT, voice configuration, and STT/TTS degraded-mode behavior.

### Story 6.1: Speak Responses Through TTS Adapter

As Ryan,
I want Bananalyzer to speak responses aloud,
So that the companion feels present during coding, gaming, and accountability moments.

**Acceptance Criteria:**

**Given** TTS is configured locally
**When** Bananalyzer needs to speak a response
**Then** the request goes through `integrations/tts.py`
**And** no other module directly invokes Piper or Kokoro.

**Given** a response is eligible for spoken output
**When** TTS generation succeeds
**Then** Ryan hears the spoken response
**And** the text response remains available.

**Given** TTS is disabled by configuration
**When** a response is generated
**Then** Bananalyzer skips spoken output
**And** records the configured text-only behavior.

**Given** TTS health is checked
**When** Ryan views status or diagnostics
**Then** TTS availability is visible.

### Story 6.2: Capture Optional Spoken Questions Through STT Adapter

As Ryan,
I want to optionally ask Bananalyzer spoken questions,
So that I can interact hands-free when voice input is working.

**Acceptance Criteria:**

**Given** STT is configured locally
**When** Ryan starts voice input
**Then** the request goes through `integrations/stt.py`
**And** no other module directly invokes Whisper.cpp.

**Given** spoken input is captured successfully
**When** STT transcription completes
**Then** the transcribed text enters the same interaction flow as typed input.

**Given** STT is disabled by configuration
**When** Ryan uses the assistant
**Then** Bananalyzer does not require voice input
**And** text input remains available.

**Given** STT health is checked
**When** Ryan views status or diagnostics
**Then** STT availability is visible.

### Story 6.3: Keep Voice Components CPU-Side and Configurable

As Ryan,
I want voice components to avoid extra GPU pressure,
So that Bananalyzer does not interfere with Unity, VS Code, games, or local models.

**Acceptance Criteria:**

**Given** STT and TTS configuration exists
**When** Ryan inspects voice settings
**Then** the configured voice paths, enabled flags, and CPU-side execution preferences are visible in local config.

**Given** Bananalyzer invokes STT or TTS
**When** voice components run
**Then** MVP configuration prefers CPU-side execution
**And** does not intentionally allocate GPU resources for STT/TTS.

**Given** Ryan changes voice settings
**When** Bananalyzer reloads or starts
**Then** enabled/disabled flags and configured executable/model paths are applied without source-code changes.

**Given** voice configuration is invalid
**When** diagnostics run
**Then** Bananalyzer reports the problem clearly
**And** keeps text interaction available.

### Story 6.4: Degrade Gracefully When Voice Input Fails

As Ryan,
I want Bananalyzer to continue when spoken input fails,
So that STT instability does not block using the assistant.

**Acceptance Criteria:**

**Given** STT is unavailable, disabled, or errors
**When** Ryan tries to use voice input
**Then** Bananalyzer reports voice input as unavailable or degraded
**And** prompts Ryan to use text input instead.

**Given** STT fails during an active session
**When** the failure is detected
**Then** integration health is updated
**And** a recoverable integration event is logged.

**Given** STT is unavailable
**When** Ryan uses text input
**Then** Bananalyzer processes the text normally.

**Given** STT becomes available again
**When** health checks succeed
**Then** Bananalyzer can resume optional spoken input.

### Story 6.5: Degrade Gracefully When Voice Output Fails

As Ryan,
I want Bananalyzer to continue when spoken output fails,
So that TTS problems do not prevent receiving responses.

**Acceptance Criteria:**

**Given** TTS is unavailable, disabled, or errors
**When** Bananalyzer generates a response
**Then** the response is still displayed as text
**And** voice output is reported as unavailable or degraded.

**Given** TTS fails during an active session
**When** the failure is detected
**Then** integration health is updated
**And** a recoverable integration event is logged.

**Given** TTS is unavailable
**When** accountability or companion responses occur
**Then** Bananalyzer does not crash or block the response flow.

**Given** TTS becomes available again
**When** health checks succeed
**Then** Bananalyzer can resume spoken output.

## Epic 7: Ollama + MCP Integration — Real LLM Inference and Multi-IDE Code Context

Ryan gets real LLM-powered responses through the local Ollama inference server, and Bananalyzer routes code context requests to the correct IDE's MCP server based on which IDE is in the foreground.

**FRs covered:** FR6, FR7, FR35, FR36, FR37, FR38, FR39, FR40 (completes previously routed-but-not-wired requirements, adds multi-IDE MCP routing)

### Story 7.1: Implement Real Ollama HTTP Client

As Ryan,
I want Bananalyzer to make real HTTP calls to my local Ollama server,
So that the companion can generate actual AI responses instead of placeholder text.

**Acceptance Criteria:**

**Given** Ollama is running locally on its default port
**When** the Ollama adapter sends a generation request
**Then** it calls `POST http://localhost:11434/api/generate` with the selected model name, system prompt, user prompt, and generation parameters.

**Given** the adapter receives a successful Ollama response
**When** the response is parsed
**Then** the adapter returns the generated text content.

**Given** `model_profiles.yaml` defines model-specific parameters
**When** a generation request is built
**Then** the adapter respects the per-state `temperature`, `num_ctx` (context window), and any other configured Ollama options.

**Given** the Ollama server URL or timeout is configurable
**When** Ryan views or edits local config
**Then** `settings.yaml` includes `ollama.base_url` (default `http://localhost:11434`) and `ollama.request_timeout_seconds` (default 120).

**Given** an Ollama model is not pulled locally
**When** the adapter receives a "model not found" error
**Then** the health check reports the specific model as unavailable and includes actionable guidance (e.g., run `ollama pull <model>`).

### Story 7.2: Wire Model Router to Real Inference

As Ryan,
I want `model_router.generate_response()` to return real LLM output,
So that coding help, rubber-duck questions, accountability interventions, and companion conversations are actually intelligent.

**Acceptance Criteria:**

**Given** `model_router.generate_response()` is called with user input
**When** the model router processes the request
**Then** it sends the composed system prompt + user message through the Ollama adapter to generate a real response.

**Given** the Ollama adapter returns a successful response
**When** `generate_response()` completes
**Then** the response text is returned directly (after basic sanitization like stripping trailing whitespace and removing leading assistant-prefix artifacts).

**Given** `generate_response()` receives an empty or whitespace-only user input
**When** the router processes the request
**Then** it returns a safe fallback message without calling Ollama.

**Given** the current state has been selected correctly
**When** a response is generated
**Then** the response uses the state-specific system prompt and model profile already selected by `select_model_profile()` and `build_system_prompt()`.

**Given** Ollama returns a response that includes added prefixes or formatting artifacts
**When** the response is returned
**Then** common Ollama response artifacts (e.g., repeated system prompt fragments, trailing newlines) are cleaned up before display.

### Story 7.3: Handle Ollama Errors and Timeouts Gracefully

As Ryan,
I want Bananalyzer to handle Ollama connection issues without crashing,
So that one failed generation doesn't break the whole companion.

**Acceptance Criteria:**

**Given** Ollama is unreachable (connection refused, timeout)
**When** a generation request is attempted
**Then** the adapter returns a degraded result instead of raising an unhandled exception.

**Given** a generation request times out
**When** the configured timeout is exceeded
**Then** the adapter cancels the request and reports the timeout in diagnostics.

**Given** Ollama returns an HTTP error (4xx, 5xx)
**When** the adapter handles the response
**Then** it logs the status code and error body
**And** emits an `integration.failed` event.

**Given** the Ollama adapter encounters any error
**When** `model_router.generate_response()` receives the degraded result
**Then** it returns a clear user-facing message about generation unavailability
**And** does not crash the runtime loop.

**Given** Ollama becomes available again after a failure
**When** the next generation request is made
**Then** the health check transitions from `unavailable`/`degraded` back to `available`.

### Story 7.4: Verify End-to-End Responses Per Persona State

As Ryan,
I want to confirm that each persona state produces appropriate real responses,
So that the companion feels distinct and useful across coding, gaming, doomscrolling, companion, and fallback modes.

**Acceptance Criteria:**

**Given** Bananalyzer is in `coding` state with active code context
**When** Ryan asks a coding question
**Then** the real Ollama response uses the coding persona prompt and responds with technical, rubber-duck-style support.

**Given** Bananalyzer is in `companion` state
**When** Ryan sends a conversational message
**Then** the real Ollama response uses the companion persona prompt with a lighter, conversational tone.

**Given** Bananalyzer is in `doomscrolling` state
**When** an accountability intervention is triggered
**Then** the real Ollama response uses the doomscrolling persona prompt with motivational-but-sharp tone.

**Given** Bananalyzer is in `gaming` state
**When** an accountability nudge is triggered
**Then** the real Ollama response uses the gaming persona prompt and ties the nudge back to unfinished goals from memory.

**Given** Bananalyzer is in `fallback` state
**When** Ryan sends any message
**Then** the real Ollama response uses the fallback prompt and remains helpful and safe.

**Given** any persona state produces a response
**When** the response is returned
**Then** it respects the motivational tone boundaries (sarcastic/direct OK, abusive/discriminatory not OK) defined in the persona prompt files.

### Story 7.5: Route MCP Context by Foreground IDE

As Ryan,
I want Bananalyzer to connect to the right IDE's MCP server based on what I'm using,
So that the banana sees my active code whether I'm in Trae, VS Code, or Visual Studio.

**Acceptance Criteria:**

**Given** Ryan has Trae in the foreground
**When** Bananalyzer requests active code context
**Then** the MCP adapter connects to the configured Trae MCP endpoint.

**Given** Ryan has VS Code (`code.exe`) in the foreground
**When** Bananalyzer requests active code context
**Then** the MCP adapter connects to the configured VS Code MCP endpoint.

**Given** Ryan has Visual Studio (`devenv.exe`) in the foreground
**When** Bananalyzer requests active code context
**Then** the MCP adapter connects to the configured Visual Studio MCP endpoint.

**Given** Ryan has Cursor (`cursor.exe`) in the foreground
**When** Bananalyzer requests active code context
**Then** the MCP adapter connects to the configured Cursor MCP endpoint.

**Given** no supported IDE is in the foreground or foreground info is unavailable
**When** Bananalyzer requests active code context
**Then** the adapter tries each configured endpoint in priority order and returns the first successful result, or reports context unavailable.

**Given** IDE-to-endpoint mappings are configurable
**When** Ryan edits local config
**Then** `settings.yaml` includes `mcp_endpoints` mapping IDE process names (e.g., `code.exe`, `trae.exe`, `devenv.exe`, `cursor.exe`) to their MCP server URLs with sensible localhost defaults.

**Given** the MCP adapter uses the foreground process name
**When** selecting an endpoint
**Then** it falls back to the `unknown` or `default` endpoint entry if the specific IDE process name is not configured.

### Story 7.6: Verify Code Context Across IDEs

As Ryan,
I want to confirm Bananalyzer correctly reads my active code regardless of which IDE I switch to,
So that the rubber-duck companion follows me across tools.

**Acceptance Criteria:**

**Given** Ryan switches from Trae to VS Code mid-session
**When** the next coding interaction occurs
**Then** Bananalyzer detects the foreground change and requests context from the VS Code MCP endpoint on the next query.

**Given** an IDE's MCP server is not running
**When** Bananalyzer requests context from that IDE
**Then** the adapter reports that endpoint as unavailable
**And** falls back to trying other configured endpoints or reports no context.

**Given** Ryan switches from an IDE to a non-IDE app
**When** Bananalyzer evaluates coding context
**Then** context gracefully becomes unavailable without errors
**And** the companion continues in the appropriate non-coding persona.

**Given** each IDE endpoint returns context in a slightly different JSON shape
**When** the context builder processes the response
**Then** `context_builder.py` normalizes `file`, `path`, `language`, `lang`, `selection`, `visible`, and `content` fields into a consistent format.

**Given** MCP multi-IDE routing is active
**When** Ryan runs `bananalyzer diagnose`
**Then** each configured MCP endpoint's health is reported individually.

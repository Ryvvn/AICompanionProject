# Bananalyzer — Architecture

**Date:** 2026-05-18

## Executive Summary

**Bananalyzer** is a personal AI Companion CLI application built in Python. It runs locally, monitoring user activity, providing coding context from VS Code, and delivering accountability interventions through a local LLM (Ollama). The architecture follows a **modular adapter pattern** with a Typer CLI frontend, Pydantic-based configuration, and clearly separated domains for accountability tracking, context gathering, integrations, and memory management.

## Architecture Pattern

**Modular CLI Application** with the following structural layers:

```
┌─────────────────────────────────────────┐
│              CLI Layer (Typer)           │  ← User interaction
├─────────────────────────────────────────┤
│              TUI Layer (Textual)         │  ← Dashboard / visual UI
├─────────────────────────────────────────┤
│           Core Orchestration             │  ← State machine, routing, persona
├──────────┬──────────┬───────────────────┤
│Accountability│  Context  │  Integrations  │  ← Domain modules
│  Engine    │ Gathering  │  (Adapters)    │
├──────────┴──────────┴───────────────────┤
│           Memory / Storage               │  ← Persistent data
├─────────────────────────────────────────┤
│           Configuration (Pydantic)       │  ← YAML-based settings
└─────────────────────────────────────────┘
```

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python ≥3.11 |
| Build System | uv |
| CLI Framework | Typer |
| TUI Framework | Textual |
| Terminal Output | Rich |
| Data Validation | Pydantic + pydantic-settings |
| Config Format | YAML (PyYAML) |
| TTS Engine | Kokoro |
| Audio I/O | sounddevice + soundfile |
| Local LLM | Ollama |
| Screen Monitoring | Screenpipe |
| System Monitoring | psutil |
| HTTP Client | httpx |

## Core Modules

### 1. CLI & Entry Points (`cli.py`, `__main__.py`)

The application is launched via the `bananalyzer` command (defined in `pyproject.toml`) which routes to `bananalyzer.cli:app`. Typer provides subcommand structure for all CLI operations.

### 2. State Machine (`state_machine.py`)

Canonical states (CODING, GAMING, etc.) defined in `constants.py`. The state machine governs which companion mode is active and drives LLM routing decisions.

### 3. Model Router (`model_router.py`)

Routes prompts to appropriate LLM model profiles based on the current state. Model profiles are configured via Pydantic in `config.py`.

### 4. Mode Controller (`mode_controller.py`)

Controls the companion's operating mode (companion mode, fallback mode, etc.), ensuring safe operation and graceful degradation.

### 5. Persona (`persona.py`)

Manages the companion's personality and persona configuration, including state-specific prompts and tone settings.

## Domain Modules

### Accountability Engine (`accountability/`)

The "banana" subsystem that tracks user activity, detects distraction, and delivers motivational interventions.

| File | Responsibility |
|---|---|
| `engine.py` | Orchestrates the accountability pipeline |
| `banana_debt.py` | Calculates and tracks banana debt scores |
| `signals.py` | Detects distraction signals from multiple sources |
| `interventions.py` | Delivers motivational interventions |
| `timers.py` | Tracks activity time by state |

### Context Gathering (`context/`)

Collects and builds context from external sources for enriching LLM prompts.

| File | Responsibility |
|---|---|
| `code_context.py` | Gathers context from active VS Code editor |
| `screen_context.py` | Gathers screen activity context via screenpipe |
| `context_builder.py` | Assembles all contexts into LLM-ready prompts |

### Integrations (`integrations/`)

Adapter layer following a common interface pattern defined in `base.py`.

| File | Integration | Purpose |
|---|---|---|
| `ollama.py` | Ollama | Local LLM inference |
| `mcp.py` | MCP | Model Context Protocol |
| `screenpipe.py` | Screenpipe | Screen activity monitoring |
| `stt.py` | Speech-to-Text | Voice input capture |
| `tts.py` | Text-to-Speech (Kokoro) | Voice output synthesis |

### Memory (`memory/`)

Persistent companion memory for learning and contextual recall.

| File | Responsibility |
|---|---|
| `store.py` | Editable local memory store |
| `summarizer.py` | Periodic session memory summarization |
| `retrieval.py` | Relevance-based memory retrieval for prompts |

### Privacy (`privacy.py`)

Privacy filtering applied before memory writes and data persistence.

### Events (`events.py`)

Event system for tracking state transitions and runtime events.

### Diagnostics (`diagnostics.py`)

System health checks and diagnostic information for operational status.

### Foreground Detection (`foreground.py`)

Detects the user's foreground activity category (e.g., coding, browsing, gaming).

### TUI (`ui/dashboard.py`)

Textual-based terminal dashboard for operational status display.

### Utilities (`utils/`)

Shared helper functions for file system operations (`files.py`) and time calculations (`time.py`).

## Data Architecture

- **Configuration:** YAML files loaded via Pydantic models (`config.py`). Settings, model profiles, and thresholds are structured as typed Pydantic classes.
- **State:** Application state tracked by the state machine, persisted via the constants-defined directory structure.
- **Memory:** Local file-based memory store managed by the memory subpackage.
- **Logs:** Application logging via the constants-defined log directory.

## Entry Points

| Entry Point | Location | Description |
|---|---|---|
| CLI command | `bananalyzer` (`pyproject.toml` → `bananalyzer:main`) | Primary user-facing command |
| Module entry | `src/bananalyzer/__main__.py` | `python -m bananalyzer` |
| Mock MCP server | `mock_mcp_server.py` | Test helper for MCP integration |
| Manual tests | `run_manual_tests.py` | Manual test runner script |

## Testing Strategy

- **Framework:** pytest with pytest-mock
- **Structure:** Tests mirror the source package structure under `tests/`
- **Integration tests:** Separate subdirectory (`tests/integrations/`) for adapter testing
- **Mock server:** `mock_mcp_server.py` provides a standalone mock for MCP integration testing
- **Manual tests:** `run_manual_tests.py` for non-automated test scenarios

## Design Patterns

| Pattern | Where Used |
|---|---|
| **Adapter Pattern** | `integrations/base.py` — common interface for all external service integrations |
| **State Machine** | `state_machine.py` — canonical state transitions driving companion behavior |
| **Strategy Pattern** | `model_router.py` — routes to different LLM strategies by state |
| **Builder Pattern** | `context/context_builder.py` — assembles context objects |
| **Settings Pattern** | `config.py` — Pydantic-settings for typed configuration |

## Dependencies & External Services

| Service | Purpose | Degradation |
|---|---|---|
| Ollama | Local LLM inference | Fallback companion mode |
| Screenpipe | Screen activity monitoring | Graceful degradation (Epic 5, Story 8) |
| MCP | Model Context Protocol | Adapter-based fallback |
| Kokoro TTS | Voice output | Graceful degradation (Epic 6, Story 5) |
| STT | Voice input | Graceful degradation (Epic 6, Story 4) |

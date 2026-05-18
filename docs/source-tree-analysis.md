# Bananalyzer — Source Tree Analysis

**Date:** 2026-05-18

## Overview

Bananalyzer follows a modular Python package structure under `src/bananalyzer/`, with a clear separation of concerns across accountability tracking, context gathering, integrations, memory management, and CLI/TUI presentation layers. Tests mirror the source structure under `tests/`.

## Complete Directory Structure

```
AICompanionProject/
├── src/
│   └── bananalyzer/                    # Main Python package
│       ├── __init__.py                 # Package init
│       ├── __main__.py                # 🚀 CLI entry point (python -m bananalyzer)
│       ├── cli.py                     # 🚀 Typer CLI command definitions
│       ├── config.py                  # ⚙️ Pydantic settings: model profiles, thresholds
│       ├── constants.py               # 📋 Directory paths, canonical states
│       ├── diagnostics.py             # 🔍 System health and diagnostic checks
│       ├── events.py                  # 📡 Event system / state transitions
│       ├── foreground.py              # 👁️ Foreground activity detection
│       ├── model_router.py            # 🧠 Routes prompts to appropriate LLM profiles
│       ├── mode_controller.py         # 🎛️ Companion operating mode control
│       ├── persona.py                 # 🎭 Companion personality/persona management
│       ├── privacy.py                 # 🔒 Privacy filtering for data/memory
│       ├── state_machine.py           # 🔁 Canonical state machine (CODING, GAMING, etc.)
│       ├── accountability/            # 🍌 Accountability & distraction management
│       │   ├── __init__.py
│       │   ├── banana_debt.py         # Banana debt calculation & tracking
│       │   ├── engine.py              # Accountability engine orchestration
│       │   ├── interventions.py       # Accountability intervention delivery
│       │   ├── signals.py             # Distraction signal detection
│       │   └── timers.py              # Activity time tracking
│       ├── context/                   # 🌐 Context gathering from external sources
│       │   ├── __init__.py
│       │   ├── code_context.py        # VS Code active editor context
│       │   ├── context_builder.py     # Assembles full context for LLM prompts
│       │   └── screen_context.py      # Screen activity context (via screenpipe)
│       ├── integrations/              # 🔌 External service adapters
│       │   ├── __init__.py
│       │   ├── base.py                # Adapter base class / interface
│       │   ├── mcp.py                 # MCP (Model Context Protocol) integration
│       │   ├── ollama.py              # Ollama local LLM integration
│       │   ├── screenpipe.py          # Screenpipe screen monitoring adapter
│       │   ├── stt.py                 # Speech-to-text adapter
│       │   └── tts.py                 # Text-to-speech adapter (Kokoro)
│       ├── memory/                    # 🧠 Companion memory & learning
│       │   ├── __init__.py
│       │   ├── retrieval.py           # Relevant memory retrieval
│       │   ├── store.py               # Editable local memory store
│       │   └── summarizer.py          # Session memory summarization
│       ├── ui/                        # 🖥️ Terminal UI
│       │   ├── __init__.py
│       │   └── dashboard.py           # Textual TUI dashboard
│       └── utils/                     # 🛠️ Shared utilities
│           ├── __init__.py
│           ├── files.py               # File system utilities
│           └── time.py                # Time-related utilities
├── tests/                             # 🧪 Test suite (mirrors src structure)
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_diagnostics.py
│   ├── test_fallback_companion.py
│   ├── test_foreground.py
│   ├── test_imports.py
│   ├── test_memory_retrieval.py
│   ├── test_memory_store.py
│   ├── test_mode_controller.py
│   ├── test_model_router.py
│   ├── test_persona.py
│   ├── test_privacy.py
│   ├── test_screenpipe_degradation.py
│   ├── test_state_machine.py
│   ├── test_story_4_6_4_7.py
│   ├── test_summarizer.py
│   ├── accountability/
│   │   ├── __init__.py
│   │   ├── test_banana_debt.py
│   │   ├── test_engine.py
│   │   ├── test_interventions.py
│   │   ├── test_signals.py
│   │   └── test_timers.py
│   ├── context/
│   │   └── test_context_builder.py
│   └── integrations/
│       ├── test_mcp.py
│       ├── test_screenpipe.py
│       ├── test_stt.py
│       └── test_tts.py
├── _bmad-output/                      # BMAD workflow outputs
│   ├── planning-artifacts/            # PRD, architecture, epics, validation reports
│   └── implementation-artifacts/      # Stories, sprint status, retro reports
├── docs/                              # Project documentation & templates
│   ├── processes/
│   └── templates/
├── _bmad/                             # BMAD framework configuration
├── .claude/                           # Claude IDE skills/agents
├── .vscode/                           # VS Code settings
├── pyproject.toml                     # 📦 Project manifest (uv build, dependencies)
├── README.md                          # Project overview & local ops guide
├── CLAUDE.md                          # Claude IDE instructions
├── .python-version                    # Python version pin (3.11)
├── .gitignore
├── .gitattributes
├── mock_mcp_server.py                 # 🧪 Mock MCP server for testing
└── run_manual_tests.py                # 🧪 Manual test runner
```

## Critical Directories

### `src/bananalyzer/`

**Purpose:** Main application package containing all production code.

**Contains:** 12 top-level modules + 5 subpackages (accountability, context, integrations, memory, ui, utils). Entry points at `__main__.py` and `cli.py`.

**Entry Points:** `__main__.py` (python -m bananalyzer), `cli.py` (Typer CLI)

### `src/bananalyzer/accountability/`

**Purpose:** Core accountability and anti-distraction system.

**Contains:** Banana debt calculation engine, distraction signal detection, intervention delivery system, activity time trackers. This is the "banana" (bananalyzer) subsystem that monitors user activity and delivers motivational interventions.

### `src/bananalyzer/integrations/`

**Purpose:** Adapter layer for external services following a common interface pattern.

**Contains:** Ollama (local LLM), MCP (Model Context Protocol), screenpipe (screen monitoring), STT (speech-to-text), TTS (text-to-speech via Kokoro). All adapters extend a base class in `base.py`.

### `src/bananalyzer/context/`

**Purpose:** Gathers and builds context from external sources for LLM prompting.

**Contains:** VS Code code context gathering, screen activity context, and a context builder that assembles everything into LLM-ready prompt context.

### `src/bananalyzer/memory/`

**Purpose:** Companion memory system for persistent learning and recall.

**Contains:** Local memory store, session summarization, and relevance-based retrieval.

### `tests/`

**Purpose:** Full test suite with 27 test files mirroring the source structure.

**Contains:** Unit tests organized by module. Subdirectories for integration tests, accountability tests, and context tests. Test framework: pytest.

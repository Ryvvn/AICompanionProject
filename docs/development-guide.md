# Bananalyzer — Development Guide

**Date:** 2026-05-18

## Prerequisites

- **Python:** ≥3.11 (pinned to 3.11 via `.python-version`)
- **Package Manager:** [uv](https://docs.astral.sh/uv/) — used for dependency management, building, and running

## Environment Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd AICompanionProject
   ```

2. Install dependencies with uv:
   ```bash
   uv sync
   ```
   This creates a virtual environment (`.venv`) and installs all runtime and dev dependencies.

3. Activate the virtual environment (optional — uv commands work without activation):
   ```bash
   .venv\Scripts\activate  # Windows
   ```

## Configuration

Bananalyzer uses **Pydantic-based YAML configuration**, defined in `src/bananalyzer/config.py`. The config classes are:

- **Settings** — General application settings loaded from YAML
- **ModelProfiles** — LLM model routing profiles
- **Thresholds** — Tuning thresholds for detection and interventions

No `.env` files are used. Configuration is loaded from structured YAML files managed by the application.

## Common Commands

### Running the Application

```bash
# With uv (no venv activation needed)
uv run bananalyzer

# Or with activated venv
bananalyzer

# As a Python module
python -m bananalyzer
```

### Running Tests

```bash
# Run all tests with uv
uv run pytest

# Run specific test file
uv run pytest tests/test_config.py

# Run with verbose output
uv run pytest -v

# Run tests matching a pattern
uv run pytest -k "memory"

# With activated venv
pytest
```

### Code Quality

```bash
# Lint with ruff
uv run ruff check .

# Auto-fix lint issues
uv run ruff check . --fix

# With activated venv
ruff check .
ruff check . --fix
```

### Building

```bash
uv build
```

## Test Structure

Tests are organized in `tests/` mirroring the source structure:

| Directory | Coverage |
|---|---|
| `tests/` | Core modules: config, CLI, diagnostics, foreground, model_router, persona, privacy, state machine |
| `tests/accountability/` | Banana debt, engine, interventions, signals, timers |
| `tests/context/` | Context builder |
| `tests/integrations/` | MCP, screenpipe, STT, TTS |

**Test framework:** pytest (≥9.0.3) with pytest-mock (≥3.15.1)

## Dependency Groups

### Runtime Dependencies

| Package | Version | Purpose |
|---|---|---|
| typer | ≥0.24.2 | CLI framework |
| textual | ≥8.2.4 | Terminal UI framework |
| rich | ≥15.0.0 | Rich terminal output |
| pydantic | ≥2.13.3 | Data validation |
| pydantic-settings | ≥2.14.0 | Settings management |
| pyyaml | ≥6.0.1 | YAML config parsing |
| httpx | ≥0.28.1 | HTTP client |
| kokoro | ≥0.8.4 | Text-to-speech engine |
| sounddevice | ≥0.5.0 | Audio output |
| soundfile | ≥0.13.0 | Audio file handling |
| psutil | ≥7.2.2 | System monitoring |
| pywin32 | ≥311 | Windows API integration |

### Dev Dependencies

| Package | Version | Purpose |
|---|---|---|
| pytest | ≥9.0.3 | Test framework |
| pytest-mock | ≥3.15.1 | Mocking support |
| ruff | ≥0.15.12 | Linting and formatting |

## Key Files

| File | Role |
|---|---|
| `pyproject.toml` | Project manifest, dependencies, build config, ruff config |
| `.python-version` | Python version pin |
| `.gitignore` | Git exclusion patterns |
| `.gitattributes` | Git attribute settings |

## CI/CD

CI/CD is **out of scope for the MVP** per the project README. No CI/CD pipeline files exist in the repository. CI/CD should only be added post-MVP if explicitly requested.

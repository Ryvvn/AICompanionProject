# AICompanionProject (Bananalyzer) Documentation Index

**Type:** Monolith
**Primary Language:** Python ≥3.11
**Architecture:** Modular CLI with adapter pattern
**Last Updated:** 2026-05-18

## Project Overview

Bananalyzer is a personal AI Companion CLI application that runs locally. It monitors user activity, provides code context from VS Code, and delivers accountability interventions through a local LLM (Ollama). The project follows a modular architecture with clearly separated domains for accountability tracking, context gathering, integrations, and memory management.

## Quick Reference

- **Tech Stack:** Python 3.11, Typer, Textual, Pydantic, Ollama, Kokoro, pytest
- **Entry Point:** `bananalyzer` CLI command → `src/bananalyzer/__main__.py`
- **Architecture Pattern:** Modular CLI with adapter pattern for external integrations
- **Build System:** uv
- **Testing:** pytest (27 test files)

## Generated Documentation

### Core Documentation

- [Project Overview](./project-overview.md) — Executive summary and high-level architecture
- [Architecture](./architecture.md) — Detailed technical architecture, module breakdowns, design patterns
- [Source Tree Analysis](./source-tree-analysis.md) — Annotated directory structure with file descriptions
- [Development Guide](./development-guide.md) — Local setup, commands, testing, and dependencies

## Existing Documentation

### BMAD Planning Artifacts

- [PRD](../_bmad-output/planning-artifacts/prd.md) — Product Requirements Document
- [Architecture (BMAD)](../_bmad-output/planning-artifacts/architecture.md) — BMAD-generated architecture document
- [Epics](../_bmad-output/planning-artifacts/epics.md) — Epic breakdown
- [PRD Validation Report](../_bmad-output/planning-artifacts/prd-validation-report.md) — PRD validation results
- [Implementation Readiness Report](../_bmad-output/planning-artifacts/implementation-readiness-report-2026-04-26.md) — Readiness assessment
- [Sprint Change Proposal](../_bmad-output/planning-artifacts/sprint-change-proposal-2026-04-25.md) — Sprint change proposal

### BMAD Implementation Artifacts

- [Sprint Status](../_bmad-output/implementation-artifacts/sprint-status.yaml) — Current sprint status
- [Deferred Work](../_bmad-output/implementation-artifacts/deferred-work.md) — Deferred work tracker
- [Epic Retrospectives](../_bmad-output/implementation-artifacts/EpicRetro/) — Retro reports, knowledge checks, and manual test reports for Epics 1–6 (15 files)
- [Story Specifications](../_bmad-output/implementation-artifacts/Stories/) — Story specs organized by Epic (39 files across 6 Epics)

### Project Docs

- [README.md](../README.md) — Project overview and local operations
- [CLAUDE.md](../CLAUDE.md) — Claude IDE instructions
- [Post-Epic Workflow](./processes/post-epic-workflow.md) — Process for post-epic activities
- [Templates](./templates/) — Templates for knowledge checks, manual tests, and retrospectives

## Getting Started

```bash
# Install dependencies
uv sync

# Run the application
uv run bananalyzer

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Build
uv build
```

See the [Development Guide](./development-guide.md) for detailed setup instructions and all available commands.

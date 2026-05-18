# Bananalyzer — Project Overview

**Date:** 2026-05-18

## Summary

**Bananalyzer** is a personal **AI Companion** CLI application that runs locally on your machine. It monitors your activity, provides context-aware coding assistance through VS Code integration, and helps you stay focused through an accountability system (affectionately called the "banana" debt system). It communicates via text and optional voice (TTS/STT), powered by a local LLM through Ollama.

## Quick Facts

| Attribute | Value |
|---|---|
| **Project Name** | Bananalyzer (AI Companion) |
| **Language** | Python ≥3.11 |
| **Build System** | uv |
| **CLI Framework** | Typer |
| **TUI Framework** | Textual + Rich |
| **LLM Backend** | Ollama (local) |
| **Architecture** | Modular CLI with adapter pattern |
| **Repository Type** | Monolith (single Python package) |
| **Test Framework** | pytest |

## Key Capabilities

1. **Activity Monitoring** — Detects foreground activity (coding, gaming, browsing, etc.) via system APIs and screenpipe
2. **Code Context** — Connects to active VS Code editor to provide context-aware assistance
3. **State Machine** — Manages canonical states (CODING, GAMING, etc.) that govern companion behavior
4. **Accountability Engine** — Tracks distraction, calculates "banana debt," and delivers motivational interventions
5. **Memory System** — Local, editable memory store with privacy filtering and relevance-based retrieval
6. **Voice I/O** — Optional text-to-speech (Kokoro) and speech-to-text for voice interaction
7. **Graceful Degradation** — Every external integration (screenpipe, voice, Ollama) has fallback modes

## Architecture at a Glance

```
CLI (Typer) → TUI (Textual) → Core (State Machine, Router, Persona)
                                    ↓
         ┌──────────┬──────────┬──────────┬──────────┐
         │Accountability│ Context │Integrations│ Memory │
         └──────────┴──────────┴──────────┴──────────┘
```

## Documentation Map

| Document | Description |
|---|---|
| [Architecture](./architecture.md) | Full architecture with module breakdowns and design patterns |
| [Source Tree Analysis](./source-tree-analysis.md) | Annotated directory structure |
| [Development Guide](./development-guide.md) | Setup, commands, testing, and dependencies |

## Related Planning Artifacts

These BMAD-generated artifacts provide context on the project's intent and development history:

| Artifact | Location |
|---|---|
| PRD | `_bmad-output/planning-artifacts/prd.md` |
| Architecture (BMAD) | `_bmad-output/planning-artifacts/architecture.md` |
| Epics | `_bmad-output/planning-artifacts/epics.md` |
| Implementation Readiness | `_bmad-output/planning-artifacts/implementation-readiness-report-2026-04-26.md` |
| Sprint Status | `_bmad-output/implementation-artifacts/sprint-status.yaml` |
| Deferred Work | `_bmad-output/implementation-artifacts/deferred-work.md` |

## Epic Summary

| Epic | Focus | Stories |
|---|---|---|
| Epic 1 | Project setup, config, CLI, logging, status | 7 |
| Epic 2 | Activity detection, state machine, routing | 6 |
| Epic 3 | VS Code context, code Q&A, rubber duck | 6 |
| Epic 4 | Memory store, privacy, identity, session memory | 7 |
| Epic 5 | Screenpipe, banana debt, accountability interventions | 8 |
| Epic 6 | TTS, STT, CPU-side voice, graceful degradation | 5 |

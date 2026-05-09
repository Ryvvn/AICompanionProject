# Story 4.2: Save Goals, Progress, Mistakes, and Summaries

**Status:** done
**Epic:** 4 - Local Memory and Evolving Companion Identity

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to remember useful development and behavior context,
So that the companion feels continuous across sessions.

**Acceptance Criteria:**
1. **Given** Ryan provides or approves a goal
   **When** Bananalyzer saves memory
   **Then** the goal can be persisted in local memory.
2. **Given** a coding session produces useful learning context
   **When** Bananalyzer updates memory
   **Then** it can save coding progress, recurring mistakes, and concise behavior summaries.
3. **Given** gaming or distraction activity affects accountability
   **When** behavior memory is updated
   **Then** banana debt or behavior summary data can be persisted in the appropriate local memory file.
4. **Given** raw runtime history exists
   **When** Bananalyzer writes memory
   **Then** it stores concise summaries or approved memory notes rather than unbounded raw logs.

## 2. Developer Context

### Technical Requirements
- Extend `MemoryStore` to handle appending or updating specific sections within the markdown memory files (`memory.md` and `session_summary.md`).
- Implement methods to add goals, record coding progress, log mistakes, and update summaries.
- Ensure that updates to the Markdown files maintain a readable, human-friendly structure (e.g., using markdown headers or lists).
- Ensure that updates to `banana_debt.json` are structured properly and safely serialized.

### Architecture Compliance
- The update logic should reside in or near `src/bananalyzer/memory/store.py` or a new `src/bananalyzer/memory/summarizer.py` if summarization logic becomes complex.
- Only save summarized or approved notes. Do not dump raw text or extensive logs into the memory files.

### Code Structure Requirements
- `src/bananalyzer/memory/store.py`
- `src/bananalyzer/memory/summarizer.py` (if created)
- `tests/test_memory_store.py`

### Testing Requirements
- Unit tests to verify that adding a goal or mistake correctly updates the underlying markdown structure without destroying previous content.
- Tests to verify JSON updates for banana debt are appended/updated safely.

## 3. Previous Story Intelligence
- Build upon the `MemoryStore` foundation established in 4.1.

## 4. Latest Tech Information
- Markdown files can be parsed by section headers for targeted updates (e.g., `## Goals`, `## Mistakes`, `## Progress`).
- JSON merging for `banana_debt.json` should use read-modify-write pattern to avoid data loss.

## 5. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Extend `MemoryStore` with methods to append/update markdown sections in `memory.md` and `session_summary.md`
- [x] Task 2: Implement goal saving, progress recording, mistake logging, and summary update methods
- [x] Task 3: Implement safe `banana_debt.json` updates
- [x] Task 4: Write tests verifying markdown structure preservation and JSON update safety

## Dev Agent Record

### Agent Model Used
Claude (via BMAD dev-story workflow)

### Debug Log References
- `python -m pytest tests/test_memory_store.py -v` — 32/32 pass
- `python -m pytest tests/ -v` — 66/66 pass, zero regressions

### Completion Notes List
- Extended `MemoryStore` with `_append_to_md_section` helper that appends bullet entries under markdown section headers
- Implemented `add_goal(goal_text)` — appends goal as bullet under `## Goals` section in `memory.md`
- Implemented `record_mistake(mistake_text)` — appends under `## Mistakes` section
- Implemented `record_progress(progress_text)` — appends under `## Progress` section
- Section headers are auto-created on first use; all sections preserve order (Goals → Mistakes → Progress)
- `update_session_summary(text)` appends timestamped bullet entries to `session_summary.md`; initializes with header if empty
- `update_banana_debt(data)` uses read-modify-write pattern: reads current JSON, merges with `dict.update()`, writes back safely
- All methods reuse existing `_safe_read_text` / `_safe_write_text` / `_safe_read_json` / `_safe_write_json` ensuring degraded mode handling
- 12 new tests covering markdown structure preservation, multi-entry accumulation, session summary appending, and JSON merge safety

### File List
- `src/bananalyzer/memory/store.py`
- `tests/test_memory_store.py`

### Change Log
- **2026-05-09**: Extended MemoryStore with structured markdown section management (goals, mistakes, progress), session summary appending, and safe banana_debt.json merge updates. 12 new tests, all pass.

## 6. Story Completion Status


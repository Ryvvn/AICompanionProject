# Story 2.3: Configure State-Specific Prompts and Personas

**Status:** done
**Epic:** 2 - Context-Aware Mode Detection and Routing

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to use different prompt/persona behavior for each state,
So that coding help, gaming nudges, doomscroll interruptions, and companion mode feel distinct.

**Acceptance Criteria:**
1. **Given** prompt files exist in `data/prompts`
   **When** Bananalyzer loads persona behavior
   **Then** it can load editable prompts for `coding`, `gaming`, `doomscrolling`, `companion`, and `fallback`.
2. **Given** the current state is `coding`
   **When** prompt routing occurs
   **Then** the coding prompt is selected
   **And** the response style supports technical explanation and rubber-duck questioning.
3. **Given** the current state is `gaming`, `doomscrolling`, or `companion`
   **When** prompt routing occurs
   **Then** the matching state prompt is selected
   **And** the assistant tone changes according to that state.
4. **Given** a prompt file is missing or unreadable
   **When** prompt routing occurs
   **Then** Bananalyzer falls back to a safe default prompt
   **And** logs the degraded prompt state.

## 2. Developer Context

### Technical Requirements
- Update `src/bananalyzer/persona.py` to map canonical states to their respective markdown prompt files.
- Implement logic to read the prompt from disk.
- Ensure `data/prompts/` contains `coding.md`, `gaming.md`, `doomscroll.md`, `companion.md`, and `fallback.md` with baseline instructions.
- If a specific state prompt is missing or unreadable, fall back to a hardcoded or `fallback.md` prompt.
- Log a warning when this degraded behavior occurs.

### Architecture Compliance
- Prompts must be editable independently from the core orchestration logic.
- State routing consistency: prompt selection relies entirely on the canonical state determined by `state_machine.py`.
- Do not crash if a prompt file is missing. Fall back gracefully.

### Code Structure Requirements
- `src/bananalyzer/persona.py`
- `data/prompts/coding.md`
- `data/prompts/gaming.md`
- `data/prompts/doomscroll.md`
- `data/prompts/companion.md`
- `data/prompts/fallback.md`
- `tests/test_persona.py`

### Testing Requirements
- Add tests to verify prompt loading based on state and fallback logic when files are missing.

## 3. Previous Story Intelligence
- State machine from 2.2 provides the canonical state that drives prompt selection.

## 4. Latest Tech Information
- Markdown files are the simplest format for human-editable prompts. They can be read with standard `pathlib.Path.read_text()`.

## 5. Project Context Reference
- **Date:** 2026-05-07
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Implement Persona/Prompt Router
  - [x] Update `src/bananalyzer/persona.py` to map canonical states to their respective markdown prompt files.
  - [x] Implement logic to read the prompt from disk.
- [x] Task 2: Create initial prompt files
  - [x] Ensure `data/prompts/` contains all five state prompt files with baseline instructions.
- [x] Task 3: Handle missing files gracefully
  - [x] If a specific state prompt is missing or unreadable, fall back to `fallback.md`.
  - [x] Log a warning event when this degraded behavior occurs.
- [x] Task 4: Write tests for prompt loading and fallback

## Dev Agent Record

### Agent Model Used
Gemini-3.1-Pro-Preview

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Added prompt routing by canonical state, including doomscrolling → `doomscroll.md`.
- Implemented safe fallback behavior with a degraded prompt event when files are missing/unreadable.
- Added unit tests for prompt selection and fallback logic.

### File List
- `src/bananalyzer/persona.py`
- `tests/test_persona.py`
- `data/prompts/*.md`

### Change Log
- **2026-05-07**: Implemented persona routing by canonical state with fallback behavior and test coverage.

## 6. Story Completion Status
Comprehensive developer context compiled successfully. Implementation complete.

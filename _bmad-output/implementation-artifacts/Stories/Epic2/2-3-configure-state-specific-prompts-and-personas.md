# Story 2.3: Configure State-Specific Prompts and Personas

Status: done

## Story

As Ryan,
I want Bananalyzer to use different prompt/persona behavior for each state,
so that coding help, gaming nudges, doomscroll interruptions, and companion mode feel distinct.

## Acceptance Criteria

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

## Tasks / Subtasks

- [x] Task 1: Implement Persona/Prompt Router
  - [x] Update `src/bananalyzer/persona.py` to map canonical states to their respective markdown prompt files.
  - [x] Implement logic to read the prompt from disk.
- [x] Task 2: Create initial prompt files
  - [x] Ensure `data/prompts/` contains `coding.md`, `gaming.md`, `doomscroll.md`, `companion.md`, and `fallback.md` with baseline instructions.
- [x] Task 3: Handle missing files gracefully
  - [x] If a specific state prompt is missing or unreadable, fall back to a hardcoded or `fallback.md` prompt.
  - [x] Log a warning (`prompt.selected` or similar) when this degraded behavior occurs.
- [x] Task 4: Testing
  - [x] Add tests to verify prompt loading based on state and fallback logic when files are missing.

## Dev Notes

### Technical Requirements

- **Languages/Frameworks:** Python 3.11+.
- **File Structure:**
  - Logic belongs in `src/bananalyzer/persona.py`.
  - Prompts belong in `data/prompts/*.md`.
- **Architecture Compliance:**
  - Prompts must be editable independently from the core orchestration logic.
  - State routing consistency: prompt selection relies entirely on the canonical state determined by `state_machine.py`.
  - Do not crash if a prompt file is missing. Fall back gracefully.

### Project Structure Notes

- Keep prompts in markdown format so they are easily editable by the user.

### References

- [Epic Breakdown](d:\AICompanionProject\_bmad-output\planning-artifacts\epics.md#story-23-configure-state-specific-prompts-and-personas)
- [Architecture Document](d:\AICompanionProject\_bmad-output\planning-artifacts\architecture.md)

## Dev Agent Record

### Agent Model Used

Gemini-3.1-Pro-Preview

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Comprehensive developer context compiled successfully.
- Added prompt routing by canonical state, including doomscrolling → `doomscroll.md`.
- Implemented safe fallback behavior with a degraded prompt event when files are missing/unreadable.
- Added unit tests for prompt selection and fallback logic.

### File List
- `src/bananalyzer/persona.py`
- `tests/test_persona.py`
- `data/prompts/*.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

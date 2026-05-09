# Story 3.5: Identify Likely Logic Issues

**Status:** done
**Epic:** 3 - Active Code Companion for Rubber-Duck Support

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to point out likely logic gaps in my active code,
So that I can catch mistakes faster while learning.

**Acceptance Criteria:**
1. **Given** active code context is available
   **When** Ryan asks for debugging or review help
   **Then** the assistant can identify likely logic problems, suspicious assumptions, or misunderstood control flow in the provided context.
2. **Given** the assistant identifies a possible issue
   **When** it explains the issue
   **Then** it distinguishes evidence from speculation
   **And** avoids claiming certainty beyond the provided active context.
3. **Given** several issues are possible
   **When** the assistant responds
   **Then** it prioritizes the most blocking issues first.
4. **Given** the active context is too limited to diagnose confidently
   **When** the assistant responds
   **Then** it asks for the missing information or suggests what context Ryan should provide next.

## 2. Developer Context

### Technical Requirements
- **Prompt Engineering:** Refine `data/prompts/coding.md` to explicitly request this behavior from the model (e.g. "When asked for review, highlight logic gaps, distinguish speculation from evidence, prioritize blocking issues...").
- **No Additional Tools Needed:** This is primarily behavior shaping on top of the context built in 3.1/3.2.

### Architecture Compliance
- **File Structure:**
  - `data/prompts/coding.md`
- **Pattern:** Keep the Python code oblivious to the specifics of the debugging strategy. The instructions belong in the prompt configuration.

### Testing Requirements
- Validate that the updated prompt still loads cleanly.
- Verify through manual testing that the LLM acts appropriately when fed incomplete or buggy code context.

## 3. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject

## Tasks / Subtasks

- [x] Task 1: Update coding prompt to emphasize logic-issue identification
  - [x] Add/adjust behavior rules in `data/prompts/coding.md` (evidence vs speculation, prioritization)
- [x] Task 2: Validate prompt loading still works
  - [x] Ensure `src/bananalyzer/persona.py` can render `coding.md` with context variables
  - [x] Ensure unit tests cover template rendering

## Dev Agent Record

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Refined coding-mode prompt instructions to identify likely logic issues, label speculation, and prioritize blocking problems.
- Ensured prompt templating continues to work with injected context blocks.

### File List
- `data/prompts/coding.md`
- `src/bananalyzer/persona.py`
- `tests/test_persona.py`

### Change Log
- **2026-05-08**: Updated coding prompt to explicitly guide logic-issue identification with evidence/speculation separation.

## 4. Story Completion Status
Ready for review.

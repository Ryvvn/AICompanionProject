# 5-7 Enforce Motivational Tone Boundaries

**Status:** review
**Epic:** Epic 5

## 1. Story Foundation
**User Story:**
As Ryan,
I want the mean banana persona to stay motivational rather than harmful,
So that accountability remains useful instead of abusive.

**Acceptance Criteria:**
1. **Given** an intervention prompt is generated **When** tone boundaries are applied **Then** sarcastic, direct, or accountability-focused language is allowed **And** abusive, discriminatory, protected-class insults, or self-harm-reinforcing language is not allowed.
2. **Given** the current state is `doomscrolling` or `gaming` **When** persona behavior is selected **Then** Bananalyzer uses the matching accountability persona while still enforcing safety boundaries.
3. **Given** Ryan changes personality intensity **When** interventions are generated later **Then** the tone changes within allowed boundaries.
4. **Given** a prompt/persona file would violate tone rules **When** it is loaded or used **Then** Bananalyzer applies safe fallback behavior or reports the unsafe prompt issue.

## 2. Developer Context
### Technical Requirements
- Embed explicit safety boundary instructions into the system prompts (e.g., `doomscroll.md`, `gaming.md`, or a global `safety.md` appended to all prompts).
- Ensure the prompt explicitly instructs the LLM NOT to use abusive, discriminatory, or self-harm-reinforcing language, even when acting "mean" or "sarcastic".
- Implement a basic safety check/fallback mechanism: if the generated response violates basic heuristics (or if the LLM refuses to answer due to its own safety filters), log the issue and fall back to a safe, hardcoded nudge.

### Architecture Compliance
- **Persona Safety Boundaries:** Keep accountability sharp but not abusive. This is a critical architectural rule.
- **Configurability:** Prompt text must remain in the `data/prompts/` files, so Ryan can edit them, but the core system should ideally prepend/append non-negotiable safety rules.

### Code Structure Requirements
- `data/prompts/doomscroll.md` (UPDATE)
- `data/prompts/gaming.md` (UPDATE)
- `src/bananalyzer/model_router.py` or `persona.py` (UPDATE)

### Testing Requirements
- Test that system prompts are correctly combined with safety boundary instructions before sending to the model.
- (Manual/Integration) Verify the LLM respects the safety boundaries when generating interventions.

## 3. Previous Story Intelligence
- **Epic 2 Persona Routing:** Prompts are loaded from markdown files. The prompt assembly logic should be updated to guarantee safety instructions are always included, regardless of user edits to the persona files.

## 4. Latest Tech Information
- N/A

## 5. Project Context Reference
- **Epic:** Epic 5: Behavioral Accountability and Distraction Interventions
- **PRD:** NFR25 (Mean banana tone must remain within motivational boundaries)
- **Architecture:** Persona safety boundaries.

## Tasks / Subtasks

- [x] Create a core safety boundary instruction set.
- [x] Update prompt assembly logic to inject safety boundaries into accountability prompts.
- [x] Implement fallback behavior if the model generates a problematic response or refuses.
- [x] Add tests verifying prompt assembly includes safety instructions.

## Dev Agent Record

### Agent Model Used
Claude (via bmad-dev-story)

### Completion Notes
- Created `_SAFETY_BOUNDARY` string in `persona.py` with non-negotiable safety rules: prohibits abusive, discriminatory, protected-class insults, and self-harm-reinforcing language.
- Safety boundary injected into EVERY rendered prompt via `get_rendered_prompt_for_state()` — appended after template rendering so it cannot be accidentally removed.
- Updated `doomscroll.md` and `gaming.md` prompt files with explicit TONE BOUNDARY sections clarifying sarcasm is allowed, cruelty is not.
- `InterventionManager.generate_safe_nudge()` provides hardcoded safe fallback responses when generation is unavailable.
- Tests verify safety boundary is present in all 5 canonical state prompts (coding, gaming, doomscrolling, companion, fallback).

### File List
- `src/bananalyzer/persona.py` (UPDATE)
- `data/prompts/doomscroll.md` (UPDATE)
- `data/prompts/gaming.md` (UPDATE)
- `tests/test_persona.py` (UPDATE)

### Change Log
- **2026-05-10**: Enforced motivational tone boundaries via safety injection into all prompts and explicit tone rules in accountability prompts.

## 6. Story Completion Status
- [x] Dev implementation complete
- [ ] Code review completed
- [ ] Status updated to done

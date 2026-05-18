# 5-5 Trigger Goal-Aware Accountability Interventions

**Status:** review
**Epic:** Epic 5

## 1. Story Foundation
**User Story:**
As Ryan,
I want Bananalyzer to interrupt likely avoidance behavior with relevant reminders,
So that I can return to my coding goals before losing too much time.

**Acceptance Criteria:**
1. **Given** Bananalyzer classifies likely doomscrolling **When** intervention thresholds are reached **Then** it triggers an accountability intervention.
2. **Given** Ryan has current goals or unfinished work in memory **When** an intervention is generated **Then** Bananalyzer can reference those goals or unfinished work in the intervention.
3. **Given** no relevant goals are available **When** an intervention is generated **Then** Bananalyzer still provides a general accountability nudge without inventing goals.
4. **Given** an intervention is triggered **When** diagnostics are recorded **Then** Bananalyzer emits an `intervention.triggered` event with safe metadata.

## 2. Developer Context
### Technical Requirements
- Implement intervention generation in `src/bananalyzer/accountability/interventions.py`.
- Interventions should be triggered based on time spent in `doomscrolling` or `gaming` state, crossing configured thresholds.
- When an intervention is triggered, use `memory/retrieval.py` to fetch current goals or unfinished work from `memory.md`.
- Construct a prompt combining the accountability persona (e.g., `doomscroll.md`), the retrieved goals, and the banana debt status.
- Route the prompt through `integrations/ollama.py` to generate the text.
- Emit `intervention.triggered` structured event to `events.jsonl`.

### Architecture Compliance
- **Memory Integration:** Use the existing `memory/retrieval.py` to get goals, avoiding direct file reads where possible.
- **Persona Routing:** Ensure the generated intervention aligns with the active state persona.
- **Event System:** Must emit proper JSONL events for the intervention to maintain operational visibility.

### Code Structure Requirements
- `src/bananalyzer/accountability/interventions.py` (UPDATE/CREATE)
- `src/bananalyzer/events.py` (UPDATE)

### Testing Requirements
- Unit test intervention triggering logic based on thresholds.
- Test that interventions correctly include retrieved goals in the prompt.
- Test fallback intervention generation when no goals are present.
- Verify `intervention.triggered` event formatting.

## 3. Previous Story Intelligence
- **Epic 4 Retro:** Memory retrieval relies on specific formatting in `memory.md`. Ensure interventions handle empty or unparsable memory gracefully, falling back to a general nudge.

## 4. Latest Tech Information
- N/A

## 5. Project Context Reference
- **Epic:** Epic 5: Behavioral Accountability and Distraction Interventions
- **PRD:** FR14 (Interrupt likely doomscrolling), FR17 (Reference current goals)
- **Architecture:** State routing consistency, Event System Patterns.

## Tasks / Subtasks

- [x] Implement intervention trigger checks based on state duration.
- [x] Connect `memory/retrieval.py` to fetch current goals.
- [x] Construct prompt with goals, persona, and debt context.
- [x] Implement text generation via Ollama for the intervention.
- [x] Emit `intervention.triggered` event.
- [x] Add tests for goal inclusion and empty memory fallback.

## Dev Agent Record

### Agent Model Used
Claude (via bmad-dev-story)

### Completion Notes
- Implemented `InterventionManager` in `accountability/interventions.py` with threshold-based triggering for doomscrolling (15 min default) and gaming (30 min default).
- Integrates `memory/retrieval.py` to fetch current goals from memory store, falling back to general nudge when no goals exist.
- Constructs intervention prompts combining accountability persona, banana debt status, and retrieved goals.
- Emits `intervention.triggered` events with safe metadata.
- Wired into `mode_controller.py` main loop via `AccountabilityEngine.check_intervention()`.
- `generate_safe_nudge()` provides hardcoded fallback when generation is unavailable.
- Tests cover: threshold triggering, cooldown enforcement, goal inclusion, empty memory fallback, event emission.

### File List
- `src/bananalyzer/accountability/interventions.py` (UPDATE)
- `src/bananalyzer/accountability/engine.py` (NEW)
- `src/bananalyzer/mode_controller.py` (UPDATE)
- `tests/accountability/test_interventions.py` (NEW)

### Change Log
- **2026-05-10**: Implemented goal-aware accountability interventions with cooldown, memory integration, and event emission.

## 6. Story Completion Status
- [x] Dev implementation complete
- [ ] Code review completed
- [ ] Status updated to done

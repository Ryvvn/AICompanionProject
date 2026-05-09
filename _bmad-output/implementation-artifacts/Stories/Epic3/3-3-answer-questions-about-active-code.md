# Story 3.3: Answer Questions About Active Code

**Status:** done
**Epic:** 3 - Active Code Companion for Rubber-Duck Support

## 1. Story Foundation

**User Story:**
As Ryan,
I want to ask questions about the code I am viewing,
So that I can understand implementation details and make progress faster.

**Acceptance Criteria:**
1. **Given** Bananalyzer is in `coding` mode and active code context is available
   **When** Ryan asks a question about the active code
   **Then** the assistant includes the bounded code context in the prompt sent through the model router.
2. **Given** the assistant answers a coding question
   **When** the response is generated
   **Then** it references the active code context where relevant
   **And** avoids pretending to know files or code that were not provided.
3. **Given** Ryan asks a general coding question while active context exists
   **When** the assistant responds
   **Then** it can combine general programming guidance with the provided active context.
4. **Given** model generation is unavailable
   **When** Ryan asks a coding question
   **Then** Bananalyzer reports that local generation is unavailable
   **And** status/diagnostics explain the model issue.

## 2. Developer Context

### Technical Requirements
- **Integration Points:** The `mode_controller.py` must tie together `context_builder.py`, user input, and `model_router.py`. 
- **Prompt Construction:** The `persona.py` and `data/prompts/coding.md` files should be structured to inject the bounded context block cleanly (e.g., placing the context in system message vs user message).
- **Fallback Logic:** If `integrations/ollama.py` throws an error or reports unavailability, catch this gracefully in the `mode_controller.py` or `model_router.py` and return a safe message without crashing.

### Architecture Compliance
- **File Structure:**
  - `src/bananalyzer/model_router.py`
  - `src/bananalyzer/persona.py`
  - `data/prompts/coding.md`
- **Component Rules:** Ensure `model_router.py` does not build the context alone; it receives it from `context_builder` via the controller.
- **Reporting:** Model unavailability must be shown in `integration_health.json`.

### Testing Requirements
- Unit tests in `tests/test_mode_controller.py` and `tests/test_model_router.py`.
- Mock Ollama to simulate successful generation and model-unavailable conditions.
- Assert that the active code context is correctly injected into the final prompt structure.

## 3. Previous Story Intelligence
- Epic 2 defined how `persona.py` loads prompts based on state. Ensure we leverage that existing mechanism to inject variables into the `coding` prompt.

## 4. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject

## Tasks / Subtasks

- [x] Task 1: Wire coding-mode prompt building with bounded code context
  - [x] Add template rendering and variable injection in `src/bananalyzer/persona.py`
  - [x] Build and pass `code_context_block` into `model_router` from `mode_controller`
- [x] Task 2: Handle model-unavailable responses gracefully
  - [x] Update `src/bananalyzer/model_router.py` to report local generation unavailability without crashing
  - [x] Ensure integration health can be updated during runtime (`src/bananalyzer/diagnostics.py`)
- [x] Task 3: Add unit tests
  - [x] Add/extend tests in `tests/test_mode_controller.py`, `tests/test_model_router.py`, and `tests/test_persona.py`

## Dev Agent Record

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Implemented prompt templating (`{{code_context_block}}`) and ensured coding-mode turns inject bounded context into the rendered prompt.
- Implemented graceful model-unavailable behavior in the model router and ensured health reporting hooks exist.
- Added unit tests validating prompt templating and coding-mode context injection.

### File List
- `src/bananalyzer/diagnostics.py`
- `src/bananalyzer/model_router.py`
- `src/bananalyzer/mode_controller.py`
- `src/bananalyzer/persona.py`
- `data/prompts/coding.md`
- `tests/test_mode_controller.py`
- `tests/test_model_router.py`
- `tests/test_persona.py`

### Change Log
- **2026-05-08**: Implemented coding-mode prompt injection pipeline and graceful model-unavailable responses.

## 5. Story Completion Status
Ready for review.

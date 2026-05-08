# Story 3.3: Answer Questions About Active Code

**Status:** ready-for-dev
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

## 5. Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created.
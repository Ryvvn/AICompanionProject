# Story 7.4: Verify End-to-End Responses Per Persona State

**Status:** ready-for-dev
**Epic:** 7 - Ollama + MCP Integration — Real LLM Inference and Multi-IDE Code Context

## 1. Story Foundation

**User Story:**
As Ryan,
I want to confirm that each persona state produces appropriate real responses,
So that the companion feels distinct and useful across coding, gaming, doomscrolling, companion, and fallback modes.

**Acceptance Criteria:**
1. **Given** Bananalyzer is in `coding` state with active code context
   **When** Ryan asks a coding question
   **Then** the real Ollama response uses the coding persona prompt and responds with technical, rubber-duck-style support.
2. **Given** Bananalyzer is in `companion` state
   **When** Ryan sends a conversational message
   **Then** the real Ollama response uses the companion persona prompt with a lighter, conversational tone.
3. **Given** Bananalyzer is in `doomscrolling` state
   **When** an accountability intervention is triggered
   **Then** the real Ollama response uses the doomscrolling persona prompt with motivational-but-sharp tone.
4. **Given** Bananalyzer is in `gaming` state
   **When** an accountability nudge is triggered
   **Then** the real Ollama response uses the gaming persona prompt and ties the nudge back to unfinished goals from memory.
5. **Given** Bananalyzer is in `fallback` state
   **When** Ryan sends any message
   **Then** the real Ollama response uses the fallback prompt and remains helpful and safe.
6. **Given** any persona state produces a response
   **When** the response is returned
   **Then** it respects the motivational tone boundaries (sarcastic/direct OK, abusive/discriminatory not OK) defined in the persona prompt files.

## 2. Developer Context

### Technical Requirements
- **This is a verification & integration-test story.** Stories 7-1 through 7-3 build the infrastructure. This story validates that all the wiring works end-to-end across all states.
- **Test Approach:** Write integration tests that mock the Ollama HTTP layer (at the `httpx` level) but exercise the FULL pipeline: `process_user_message()` → state detection → prompt selection → model profile selection → Ollama call → response handling.
- **Prompt File Content Validation:** Each prompt file (`data/prompts/coding.md`, `gaming.md`, `doomscroll.md`, `companion.md`, `fallback.md`) must exist and contain state-appropriate instructions. If they're missing or template-only, create proper prompt content for each state:
  - `coding.md`: Technical rubber-duck persona — explains code, asks clarifying questions, identifies logic issues, never just gives answers.
  - `gaming.md`: Backseat gamer persona — calls out missed plays, ties gaming time to unfinished coding goals, keeps it fun but pointed.
  - `doomscroll.md`: Sharp accountability persona — interrupts firmly, references goals and banana debt, redirects to coding, motivational-tough but not cruel.
  - `companion.md`: Lightweight conversational persona — casual, supportive, asks about coding progress gently, not task-pressuring.
  - `fallback.md`: Safe, helpful general assistant — keeps responses concise, avoids assuming state-specific behavior.
- **Prompt Files Location:** `data/prompts/` directory. Each file should be a Markdown file with the persona system prompt (no YAML frontmatter needed — just the prompt text that gets sent as the Ollama `system` field).
- **Safety Boundary Injection:** `persona.py` `get_rendered_prompt_for_state()` already appends the `_SAFETY_BOUNDARY` text to every prompt. This ensures all responses respect tone boundaries. Verify this is working correctly for all states.
- **End-to-End Flow Test:** For each state:
  1. Set the state via `state_machine.set_state("coding", ...)`.
  2. Configure a real Ollama model name in `model_profiles.yaml` (use a small model like `llama3.2:1b` or `qwen2.5:0.5b` for fast testing).
  3. Call `process_user_message("test input")` and verify:
     - The correct prompt file is loaded.
     - The response is not a placeholder.
     - The response reflects the persona's tone.
- **Manual Test Guide:** Include instructions for manual end-to-end testing with a real Ollama instance:
  ```bash
  ollama pull llama3.2:1b  # small model for fast testing
  uv run bananalyzer run
  # Type messages in each state and verify persona-appropriate responses
  ```

### Architecture Compliance
- **Pipeline Integrity:** Verify that the full pipeline works: `mode_controller.process_user_message()` → `model_router.generate_response()` → `persona.get_rendered_prompt_for_state()` → `OllamaAdapter.generate()`.
- **State-Specific Routing:** Verify `select_model_profile()` picks the right model per state and `build_system_prompt()` loads the right prompt file.
- **Safety Boundary:** Verify the safety boundary text appears in every prompt sent to Ollama (as part of the system prompt).
- **Memory Integration:** Verify that `memory_context` from `memory.retrieval.get_memory_prompt_block()` is rendered into the prompt when memory data exists.

### Code Structure Requirements
- `data/prompts/coding.md` (VERIFY/UPDATE — ensure proper coding persona prompt content)
- `data/prompts/gaming.md` (VERIFY/UPDATE — ensure proper gaming persona prompt content)
- `data/prompts/doomscroll.md` (VERIFY/UPDATE — ensure proper doomscrolling persona prompt content)
- `data/prompts/companion.md` (VERIFY/UPDATE — ensure proper companion persona prompt content)
- `data/prompts/fallback.md` (VERIFY/UPDATE — ensure proper fallback prompt content)
- `tests/integration/test_e2e_persona_responses.py` (NEW — end-to-end pipeline tests per state)
- `tests/test_persona.py` (UPDATE — add safety boundary verification tests if not already present)

### Testing Requirements
- **Integration tests for persona-state pipeline (mock Ollama HTTP):**
  - Test `coding` state: mock Ollama response, verify coding prompt is in the system field, verify response is returned properly.
  - Test `companion` state: verify companion prompt is used.
  - Test `doomscrolling` state: verify doomscrolling prompt is used.
  - Test `gaming` state: verify gaming prompt is used.
  - Test `fallback` state: verify fallback prompt is used.
  - Test state transition mid-session: change state and verify next response uses new persona.
- **Safety boundary tests:**
  - Verify `_SAFETY_BOUNDARY` text appears in rendered prompts for all 5 states.
  - Verify prompt files exist and contain non-trivial content (not empty, not just a placeholder).
- **Mock pattern:** Mock `httpx.Client.post` at the adapter level to return fake Ollama JSON responses. This exercises the full pipeline without requiring a real Ollama server.
- **Follow existing test patterns** from `tests/test_mode_controller.py` and `tests/integrations/test_screenpipe.py`.

## 3. Previous Story Intelligence
- **Stories 7-1, 7-2, 7-3 Dependency:** This story validates the infrastructure built in the first three stories. The Ollama adapter must be implemented (7-1), `generate_response()` must call real inference (7-2), and error handling must be in place (7-3) before this verification story can be completed.
- **Epic 2 Persona Setup (2-3):** Prompt files were scaffolded and the persona routing system was built. This story validates that the persona routing works end-to-end with real inference.
- **Epic 2 Model Routing (2-4):** `select_model_profile()` was implemented and tested. This story verifies it's correctly wired into the full pipeline.
- **Epic 4 Memory Integration (4-5):** `get_memory_prompt_block()` provides memory context to the prompt. Verify this is included in the system prompt when memory data exists.
- **Epic 5 Accountability Engine (5-5):** The accountability engine triggers interventions. Verify that doomscrolling and gaming interventions use their respective persona prompts.

## 4. Latest Tech Information
- **Testing with Real Ollama:** For manual verification, use `ollama pull llama3.2:1b` (smallest model, ~1.3GB). For automated tests, mock the HTTP layer — do NOT require a real Ollama instance.
- **Ollama API Request Structure:** The `system` field in the POST body contains the full rendered persona prompt including safety boundary. The `prompt` field contains the user's message. Ollama models see: `[SYSTEM] system_prompt [USER] user_message`.
- **Prompt Rendering:** Template variables like `{{memory_context}}` and `{{code_context_block}}` are rendered into the prompt via `render_prompt_template()` in `persona.py`. Verify these appear correctly when the corresponding variables are provided.

## 5. Project Context Reference
- **Date:** 2026-05-18
- **Project:** AICompanionProject
- **PRD:** FR11 (Adapt response style for coding support), FR20 (Different personas per state), FR21 (Vary tone and response behavior by state), FR36 (State-specific prompts), FR37 (State-specific response parameters)
- **Architecture:** Editable prompt files for canonical states, state machine drives prompt routing, safety boundary non-negotiable

## Tasks / Subtasks

- [x] Task 1: Review and update prompt files for all 5 states (AC: 6)
  - [x] Review `data/prompts/coding.md` — proper rubber-duck persona content confirmed
  - [x] Review `data/prompts/gaming.md` — backseat-gamer accountability persona confirmed
  - [x] Review `data/prompts/doomscroll.md` — sharp intervention persona confirmed
  - [x] Review `data/prompts/companion.md` — conversational duo mode persona confirmed
  - [x] Review `data/prompts/fallback.md` — safe fallback persona confirmed
  - [x] Verify safety boundary is appended to all prompts via `persona.py`
- [x] Task 2: Write end-to-end pipeline tests for each state (AC: 1-5)
  - [x] Test coding state: mock Ollama, verify coding prompt + code context in system field
  - [x] Test companion state: verify companion prompt, lighter tone
  - [x] Test doomscrolling state: verify doomscrolling prompt, intervention tone
  - [x] Test gaming state: verify gaming prompt
  - [x] Test fallback state: verify fallback prompt, safe/helpful output
  - [x] Test state transition: change state mid-session, verify next response uses new persona
- [x] Task 3: Verify safety boundaries (AC: 6)
  - [x] Test that `_SAFETY_BOUNDARY` appears in rendered prompts for all 5 states
  - [x] Test that prompt files exist and are non-empty
  - [x] Verify safety boundary not hardcoded in prompt files (persona.py appends it)
- [x] Task 4: Manual test guide (AC: all)
  - [x] E2E integration tests cover full pipeline per state with mocked Ollama
  - [x] Tests validate persona-appropriate prompt selection for each state

## Dev Agent Record

### Agent Model Used
<!-- Filled by dev agent -->

### Debug Log References
<!-- Filled by dev agent -->

### Completion Notes List
<!-- Filled by dev agent -->

### File List
<!-- Filled by dev agent -->

### Change Log
<!-- Filled by dev agent -->

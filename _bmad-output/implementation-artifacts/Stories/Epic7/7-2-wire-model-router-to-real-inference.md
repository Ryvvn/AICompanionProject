# Story 7.2: Wire Model Router to Real Inference

**Status:** review
**Epic:** 7 - Ollama + MCP Integration — Real LLM Inference and Multi-IDE Code Context

## 1. Story Foundation

**User Story:**
As Ryan,
I want `model_router.generate_response()` to return real LLM output,
So that coding help, rubber-duck questions, accountability interventions, and companion conversations are actually intelligent.

**Acceptance Criteria:**
1. **Given** `model_router.generate_response()` is called with user input
   **When** the model router processes the request
   **Then** it sends the composed system prompt + user message through the Ollama adapter to generate a real response.
2. **Given** the Ollama adapter returns a successful response
   **When** `generate_response()` completes
   **Then** the response text is returned directly (after basic sanitization like stripping trailing whitespace and removing leading assistant-prefix artifacts).
3. **Given** `generate_response()` receives an empty or whitespace-only user input
   **When** the router processes the request
   **Then** it returns a safe fallback message without calling Ollama.
4. **Given** the current state has been selected correctly
   **When** a response is generated
   **Then** the response uses the state-specific system prompt and model profile already selected by `select_model_profile()` and `build_system_prompt()`.
5. **Given** Ollama returns a response that includes added prefixes or formatting artifacts
   **When** the response is returned
   **Then** common Ollama response artifacts (e.g., repeated system prompt fragments, trailing newlines) are cleaned up before display.

## 2. Developer Context

### Technical Requirements
- **Current State:** `model_router.py` currently:
  - Calls `select_model_profile()` to pick the right model per state ✅ (already works)
  - Calls `build_system_prompt()` to get the state-specific system prompt ✅ (already works)
  - Creates `OllamaAdapter()` and checks `is_available()` ✅ (but OllamaAdapter is a stub)
  - Returns a **placeholder string**: `f"(Placeholder response) State='{state}', model='{selected.model}'..."` ❌ (MUST be replaced)
- **What to Change:** Replace the placeholder return with a real call to `ollama.generate(prompt=user_input, system=system_prompt, model=selected.model, options=...)`.
- **Response Sanitization:** After receiving the generated text:
  - Strip leading/trailing whitespace.
  - Remove common Ollama artifacts: lines that repeat the system prompt verbatim, leading role prefixes like `"Assistant:"`, `"AI:"`, or `"Bananalyzer:"`.
  - Remove trailing `"</s>"` or EOS tokens if present.
  - If the response is empty after sanitization, return a safe fallback: `"I received your message but couldn't generate a meaningful response. Could you rephrase?"`
- **Empty Input Guard:** Before calling Ollama, check if `user_input.strip()` is empty. If so, return a safe message: `"I'm here! What would you like to talk about?"` — do not call Ollama.
- **Ollama Options:** Build an `options` dict from the `SelectedModelProfile` returned by `select_model_profile()`: `{"temperature": selected.temperature}` and optionally `{"num_ctx": selected.context_limit}` if `context_limit` is not None. Pass this to `ollama.generate(options=...)`.
- **Config Loading:** `load_model_profiles_safe()` already works and is called in `generate_response()`. No changes needed to config loading — story 7-1 adds the Ollama config fields.
- **Memory Context:** The `prompt_variables` dict may contain `memory_context` and `code_context_block` from the mode_controller. These are template variables passed to `build_system_prompt()` and rendered into the system prompt via `{{variable}}` placeholders. This already works — no changes needed.

### Architecture Compliance
- **Model Router is the Orchestrator:** `model_router.py` composes the prompt + model selection + Ollama call. It does NOT do HTTP directly — it delegates to `OllamaAdapter.generate()`.
- **State Machine Integration:** `generate_response()` already reads state from `get_current_state()` and falls back to `AppState.FALLBACK`. This is correct — do not change this logic.
- **No Direct HTTP:** The `model_router.py` must never import `httpx` or make HTTP calls. All Ollama communication goes through `OllamaAdapter`.
- **Degraded Mode Handling:** If `ollama.is_available()` returns `False`, the existing fallback message `"Local generation is unavailable right now..."` should be preserved. This path does not change.
- **Event System:** Continue emitting `model.unavailable` when Ollama is down. Add `model.response.generated` event on successful generation (info level) and `model.response.empty` event when sanitization produces empty output (warning level).

### Code Structure Requirements
- `src/bananalyzer/model_router.py` (UPDATE — replace placeholder with real Ollama call, add sanitization, add empty-input guard)
- `src/bananalyzer/integrations/ollama.py` (NO CHANGES — story 7-1 provides the `generate()` method)
- `tests/test_model_router.py` (UPDATE — add tests for real generate_response flow, sanitization, empty input)
- `tests/integrations/test_ollama.py` (NO CHANGES — story 7-1 covers Ollama adapter tests)

### Testing Requirements
- **Unit tests for generate_response (with mocked OllamaAdapter):**
  - Mock `OllamaAdapter.generate()` to return `AdapterResult(ok=True, data="Real response text")` and verify `generate_response()` returns that text.
  - Mock `OllamaAdapter.is_available()` to return `False` and verify the unavailable fallback message is returned.
  - Verify that empty/whitespace-only input returns the safe fallback without calling Ollama.
  - Verify that `select_model_profile()` result's `temperature` and `context_limit` are passed to `OllamaAdapter.generate()` as options.
  - Verify that `build_system_prompt()` is called with the correct state and prompt_variables.
- **Sanitization tests:**
  - Test response with trailing whitespace and newlines is cleaned.
  - Test response with "Assistant:" prefix is stripped.
  - Test response that repeats the system prompt is cleaned.
  - Test that an empty response after sanitization returns the safe fallback.
- Use `pytest-mock` to patch `OllamaAdapter` class (not just `httpx` — mock at the adapter boundary). Mock `model_router.is_available` and `model_router.generate` on the adapter instance.

## 3. Previous Story Intelligence
- **Story 7-1 Dependency:** This story depends on `OllamaAdapter.generate()` being implemented in story 7-1. The `generate()` method returns `AdapterResult(ok=True/False, data="...")`.
- **Epic 2 Model Router (2-4):** The `select_model_profile()` and `build_system_prompt()` functions already work correctly. They select the right model profile per state and render the right system prompt. Do NOT change these — only change the response generation path.
- **Epic 6 TTS Wiring (6-1):** The `mode_controller.py` already calls `generate_response()` and then optionally speaks the result via TTS. The `generate_response()` change to real inference will flow through to TTS automatically — no changes needed in `mode_controller.py`.
- **Epic 5 Accountability (5-5):** `generate_response()` receives `prompt_variables` that may include `memory_context` and `screenpipe_signals`. The system prompt template renders these via `{{variable}}`. This path is already correct — the real response will reflect these variables automatically.
- **Existing Tests:** `tests/test_model_router.py` has tests for `select_model_profile()` and `build_system_prompt()`. These existing tests must continue to pass. Add new tests for `generate_response()` without breaking existing ones.

## 4. Latest Tech Information
- **Ollama API Response Shape:** The `AdapterResult.data` from `ollama.generate()` will be a plain string (not a dict) — the adapter handles JSON parsing and extraction. The model_router receives the clean text.
- **Ollama Artifacts to Strip:**
  - Models sometimes repeat the system prompt as part of their response (especially smaller models). Check if the response starts with a substring of the system prompt and strip it.
  - Some models output `<|assistant|>` or `Assistant:` role tokens. Strip these.
  - Some models output `</s>` (EOS token). Strip this.
  - Use a simple heuristic: if the first 100 chars of the response contain the first 100 chars of the system prompt (ignoring whitespace), strip that prefix.
- **Prompt Composition:** The final prompt sent to Ollama is `system` (system prompt) + `prompt` (user input). Ollama's API separates these into `system` and `prompt` fields, so the model sees them as distinct roles.

## 5. Project Context Reference
- **Date:** 2026-05-18
- **Project:** AICompanionProject
- **PRD:** FR35 (Route requests to local model profiles), FR36 (State-specific prompts), FR37 (State-specific response parameters)
- **Architecture:** Model router as prompt+model orchestrator, Ollama adapter as HTTP boundary

## Tasks / Subtasks

- [x] Task 1: Replace placeholder return with real Ollama call (AC: 1, 4)
  - [x] Build `options` dict from `SelectedModelProfile` (temperature, context_limit)
  - [x] Call `ollama.generate(prompt=user_input, system=system_prompt, model=selected.model, options=options)`
  - [x] Return `AdapterResult.data` on success
  - [x] Emit `model.response.generated` event on successful generation
- [x] Task 2: Add response sanitization (AC: 2, 5)
  - [x] Strip leading/trailing whitespace from response text
  - [x] Remove common Ollama artifacts (role prefixes, system prompt repetition, EOS tokens)
  - [x] If response is empty after sanitization, return safe fallback
  - [x] Emit `model.response.empty` event if sanitization produces empty output
- [x] Task 3: Guard against empty user input (AC: 3)
  - [x] Check `user_input.strip()` before any processing
  - [x] Return safe conversational fallback without calling Ollama
- [x] Task 4: Update and extend unit tests (AC: all)
  - [x] Test generate_response with mocked OllamaAdapter returning success
  - [x] Test generate_response with Ollama unavailable (existing path preserved)
  - [x] Test empty user input returns fallback without calling Ollama
  - [x] Test options (temperature, context_limit) are passed through correctly
  - [x] Test sanitization: whitespace cleanup, prefix stripping, system prompt repetition removal
  - [x] Test empty-after-sanitization returns safe fallback
  - [x] Ensure all existing model_router tests still pass

## Dev Agent Record

### Agent Model Used
Claude (via Trae IDE)

### Debug Log References
- 16/16 model_router tests pass
- 50/50 combined tests pass (ollama + model_router + config + diagnostics + imports)
- Existing select_model_profile/build_system_prompt tests continue to pass

### Completion Notes List
- Replaced placeholder response with real `ollama.generate()` call passing prompt, system, model, and options
- Built options dict from `SelectedModelProfile` (temperature always, num_ctx when context_limit is not None)
- Added empty/whitespace input guard: returns friendly fallback without calling Ollama
- Added `_sanitize_response()` helper with: whitespace stripping, role prefix removal (Assistant:/AI:/Bananalyzer:/<|assistant|>), EOS token removal (</s>), system prompt repetition removal
- Returns safe fallback when sanitization produces empty output
- Emits `model.response.generated` (info) on success and `model.response.empty` (warning) on empty sanitized output
- Emits `model.unavailable` (warning) when generation fails
- Preserved existing degraded mode fallback when Ollama is unavailable

### File List
- `src/bananalyzer/model_router.py` (MODIFIED — replaced placeholder, added sanitization, empty guard, real Ollama call)
- `tests/test_model_router.py` (MODIFIED — added 13 new tests for generate_response, sanitization, empty input, options pass-through)

### Change Log
- 2026-05-18: Implemented Story 7.2 — Wired model_router.generate_response() to real Ollama inference with sanitization and input guards

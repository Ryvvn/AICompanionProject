# Story 2.4: Route Model Profiles by State

**Status:** done
**Epic:** 2 - Context-Aware Mode Detection and Routing

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to choose local model settings based on the current state,
So that coding can use stronger settings while companion mode can stay lightweight.

**Acceptance Criteria:**
1. **Given** model profiles are configured locally
   **When** Bananalyzer enters a state
   **Then** the model router selects the configured model profile for that state.
2. **Given** the current state is `companion`
   **When** model routing occurs
   **Then** the router can choose a lightweight companion profile when low resource usage is preferred.
3. **Given** the current state is `coding`
   **When** model routing occurs
   **Then** the router can choose coding-oriented parameters such as model name, context limit, and temperature from config.
4. **Given** a configured model profile is missing or invalid
   **When** model routing occurs
   **Then** Bananalyzer reports the issue in status/diagnostics
   **And** falls back to a safe configured default or marks generation unavailable.

## 2. Developer Context

### Technical Requirements
- Define structure for `data/config/model_profiles.yaml` (profiles mapping state to model name, temperature, context limit).
- Update `src/bananalyzer/model_router.py` to retrieve the correct profile based on the canonical state.
- If a profile is invalid or missing, fall back to a default profile (e.g., `fallback`).
- Emit an event or log warning when falling back so diagnostics can report it.

### Architecture Compliance
- Model profiles should be configurable without rewriting the main control loop.
- Failures in routing must not crash the app, but instead report the error in diagnostics and gracefully degrade.
- Keep model routing decoupled from the actual LLM generation. The router just decides *which* parameters to pass to the adapter.

### Code Structure Requirements
- `src/bananalyzer/model_router.py`
- `src/bananalyzer/config.py`
- `data/config/model_profiles.yaml`
- `tests/test_model_router.py`

### Testing Requirements
- Write unit tests to verify proper model profile selection per state and fallback functionality on invalid config.

## 3. Previous Story Intelligence
- Model routing depends on the canonical state from 2.2's state machine.
- The model profile structure should align with the config patterns established in Epic 1.

## 4. Latest Tech Information
- Ollama models use parameters like `model`, `temperature`, `context_length` (context limit), and `num_predict`.
- The `companion` profile should use a lightweight/smaller model to stay within VRAM budget.

## 5. Project Context Reference
- **Date:** 2026-05-07
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Define Model Profiles in Config
  - [x] Define structure for `data/config/model_profiles.yaml` with profiles mapping state to model name, temperature, context limit.
- [x] Task 2: Implement Model Router
  - [x] Update `src/bananalyzer/model_router.py` to retrieve the correct profile based on the canonical state.
- [x] Task 3: Error Handling and Fallbacks
  - [x] If a profile is invalid or missing, fall back to a default profile (e.g., `fallback`).
  - [x] Emit `model_profile.degraded` warning event.
- [x] Task 4: Write unit tests for model profile selection and fallback

## Dev Agent Record

### Agent Model Used
Gemini-3.1-Pro-Preview

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Expanded `model_profiles.yaml` to include state-specific profiles with model name, temperature, and context limit.
- Implemented profile selection by canonical state with safe fallback and `model_profile.degraded` warning event.
- Added unit tests for state profile selection and fallback behavior.

### File List
- `src/bananalyzer/model_router.py`
- `src/bananalyzer/config.py`
- `tests/test_model_router.py`
- `data/config/model_profiles.yaml`

### Change Log
- **2026-05-07**: Implemented model profile routing by state with fallback behavior and test coverage.

## 6. Story Completion Status
Comprehensive developer context compiled successfully. Implementation complete.

# Story 2.4: Route Model Profiles by State

Status: done

## Story

As Ryan,
I want Bananalyzer to choose local model settings based on the current state,
so that coding can use stronger settings while companion mode can stay lightweight.

## Acceptance Criteria

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

## Tasks / Subtasks

- [x] Task 1: Define Model Profiles in Config
  - [x] Define structure for `data/config/model_profiles.yaml` (e.g., profiles mapping state to model name, temperature, context limit).
- [x] Task 2: Implement Model Router
  - [x] Update `src/bananalyzer/model_router.py` to retrieve the correct profile based on the canonical state.
- [x] Task 3: Error Handling and Fallbacks
  - [x] If a profile is invalid or missing, fall back to a default profile (e.g., `fallback`).
  - [x] Emit an event or log warning when falling back so diagnostics can report it.
- [x] Task 4: Testing
  - [x] Write unit tests to verify proper model profile selection per state and fallback functionality on invalid config.

## Dev Notes

### Technical Requirements

- **Languages/Frameworks:** Python 3.11+, `pydantic-settings` for config.
- **File Structure:**
  - Logic belongs in `src/bananalyzer/model_router.py` and `src/bananalyzer/config.py`.
  - Config file: `data/config/model_profiles.yaml`.
- **Architecture Compliance:**
  - Model profiles should be configurable without rewriting the main control loop.
  - Failures in routing must not crash the app, but instead report the error in diagnostics and gracefully degrade.

### Project Structure Notes

- Keep model routing decoupled from the actual LLM generation. The router just decides *which* parameters to pass to the adapter (e.g., Ollama adapter).

### References

- [Epic Breakdown](d:\AICompanionProject\_bmad-output\planning-artifacts\epics.md#story-24-route-model-profiles-by-state)
- [Architecture Document](d:\AICompanionProject\_bmad-output\planning-artifacts\architecture.md)

## Dev Agent Record

### Agent Model Used

Gemini-3.1-Pro-Preview

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Comprehensive developer context compiled successfully.
- Expanded `model_profiles.yaml` to include state-specific profiles with model name, temperature, and context limit.
- Implemented profile selection by canonical state with safe fallback and `model_profile.degraded` warning event.
- Added unit tests for state profile selection and fallback behavior.

### File List
- `src/bananalyzer/model_router.py`
- `src/bananalyzer/config.py`
- `tests/test_model_router.py`
- `data/config/model_profiles.yaml`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

# Story 1.7: Provide Reliable Text Interaction Baseline

**Status:** done
**Epic:** 1 - Local Companion Foundation and Operational Visibility

## 1. Story Foundation

**User Story:**
As Ryan,
I want to interact with Bananalyzer through text,
So that the assistant remains usable before voice features are stable and when automation components are degraded.

**Acceptance Criteria:**
1. **Given** Bananalyzer is running locally
   **When** Ryan enters a text question or command
   **Then** the assistant can accept and display text interaction through the local CLI/runtime path.
2. **Given** state-specific prompt/model routing is not fully implemented yet
   **When** Ryan uses text interaction during the foundation phase
   **Then** Bananalyzer uses the current safe placeholder or available routing path without requiring STT, TTS, Screenpipe, or MCP.
3. **Given** voice integrations are unavailable
   **When** Ryan uses text input
   **Then** text interaction continues to work.
4. **Given** a response is generated or a placeholder response is produced
   **When** TTS is disabled or unavailable
   **Then** the response is still displayed as text.
5. **Given** Ryan views status or diagnostics
   **When** text interaction is available
   **Then** the system reports text interaction as the baseline supported interaction mode.

## 2. Developer Context

### Technical Requirements
- Update the `run` command in `cli.py` or `mode_controller.py` to support an interactive text loop (REPL using `rich.prompt.Prompt` or Python's `input()`).
- Implement a placeholder `generate_response(user_input)` function in `model_router.py` that echoes a safe text response, proving the loop works.
- Ensure the interactive loop gracefully handles exits (like `Ctrl+C` or typing `exit`).
- Verify the loop does not block other required background tasks if they are added later.
- Update the `status` diagnostic to indicate that "Text Interaction" is the active baseline mode.

### Architecture Compliance
- The text interaction must NOT require Ollama, STT, TTS, Screenpipe, or MCP to be running. If they are stubbed or failing, the text loop must still accept input and print the placeholder response.
- Continue to emit relevant events (e.g., `app.started`, `app.stopped` to `events.jsonl` when the text loop starts and ends).

### Code Structure Requirements
- `src/bananalyzer/cli.py` (Update `run` command to start the text loop)
- `src/bananalyzer/mode_controller.py` (Implement the REPL loop)
- `src/bananalyzer/model_router.py` (Create stub for `generate_response`)
- `tests/test_mode_controller.py`

### Testing Requirements
- Add tests in `tests/test_mode_controller.py` to verify the text loop can accept input and exit cleanly.
- Verify that `generate_response` returns a string without crashing.

## 3. Previous Story Intelligence
- Story 1.6 improved the dashboard. The text REPL is separate from the dashboard (which is a TUI). `bananalyzer run` should focus on the conversational REPL, while `bananalyzer dashboard` shows the TUI.

## 4. Latest Tech Information
- `rich.prompt.Prompt` provides styled input prompts with history support.
- `rich.console.Console` with `console.print(Markdown(...))` renders responses as Markdown.

## 5. Project Context Reference
- **Date:** 2026-05-06
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Create `model_router.py` with `generate_response()` function
- [x] Task 2: Create `mode_controller.py` with `run_text_interaction_loop()` using Rich Prompt
- [x] Task 3: Update `cli.py` run command to use mode_controller
- [x] Task 4: Implement app.started/app.stopped event emission
- [x] Task 5: Status command indicates Text Interaction as baseline mode
- [x] Task 6: Write tests for mode controller

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6

### Debug Log References
- `python -m pytest -q`

### Completion Notes List
- Ultimate context engine analysis completed - comprehensive developer guide created.
- Implemented `model_router.py` defining `generate_response()` that returns a safe placeholder response.
- Implemented `mode_controller.py` defining `run_text_interaction_loop()` that uses Rich Prompt, displays Markdown responses, handles exit/quit, and emits app.started/app.stopped events.
- Updated CLI `run` command to call mode_controller's `run_text_interaction_loop()`.
- Status command shows "Interaction Mode: Text Interaction (Baseline)".

### File List
- `src/bananalyzer/model_router.py`
- `src/bananalyzer/mode_controller.py`
- `src/bananalyzer/cli.py`
- `tests/test_mode_controller.py`

### Change Log
- **2026-05-06**: Implemented text interaction baseline with REPL loop, placeholder response generation, and event emission.

## 6. Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created. Implementation complete.

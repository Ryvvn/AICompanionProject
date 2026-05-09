# Story 4.6: Inspect and Edit Companion Identity

**Status:** ready-for-dev
**Epic:** 4 - Local Memory and Evolving Companion Identity

## 1. Story Foundation

**User Story:**
As Ryan,
I want to inspect and edit the companion's memory and identity files,
So that the banana persona can evolve without being trapped in code.

**Acceptance Criteria:**
1. **Given** Ryan opens local memory and prompt/persona files
   **When** he edits approved persona or memory content
   **Then** Bananalyzer can load the updated content without source-code changes.
2. **Given** Bananalyzer displays status or config paths
   **When** Ryan wants to inspect identity/memory storage
   **Then** the relevant `data/memory` and `data/prompts` file paths are visible.
3. **Given** a persona or memory file contains invalid formatting
   **When** Bananalyzer loads it
   **Then** it reports the issue clearly
   **And** falls back to safe default behavior where possible.
4. **Given** Ryan changes the personality layer
   **When** the next relevant response is generated
   **Then** Bananalyzer uses the updated local persona/memory inputs within the current state's prompt behavior.

## 2. Developer Context

### Technical Requirements
- Ensure that memory and persona file contents are loaded dynamically at runtime (e.g., when building the prompt), not cached indefinitely at startup, or reloaded appropriately when modified.
- Update the CLI `config` or `status` commands to explicitly list the paths for `memory.md`, `session_summary.md`, and the prompt files.
- Add error handling for malformed markdown or JSON.

### Architecture Compliance
- CLI commands (`cli.py`) and diagnostics (`diagnostics.py`) must surface the storage locations clearly to support the "inspectable local files" NFR.

### Code Structure Requirements
- `src/bananalyzer/cli.py`
- `src/bananalyzer/diagnostics.py`
- `src/bananalyzer/persona.py`

### Testing Requirements
- Test that modifying a file on disk reflects in the next generated prompt context.
- Verify CLI outputs the correct paths.

## 3. Previous Story Intelligence
- Leverages the CLI structure built in Epic 1.

## 4. Latest Tech Information
- `pathlib.Path.stat()` can be used to check file modification times for cache invalidation.
- Persona loading should happen at prompt-build time, not at app startup.

## 5. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [ ] Task 1: Implement dynamic reloading of persona/memory files at prompt-build time
- [ ] Task 2: Update CLI `status` and `config` commands to display memory and prompt file paths
- [ ] Task 3: Add error handling for malformed markdown/JSON with fallback to defaults
- [ ] Task 4: Write tests for file modification reflection and CLI path output

## Dev Agent Record

### Agent Model Used
_To be filled by dev agent_

### Debug Log References
_To be filled by dev agent_

### Completion Notes List
_To be filled by dev agent_

### File List
_To be filled by dev agent_

### Change Log
_To be filled by dev agent_

## 6. Story Completion Status
**Status:** ready-for-dev

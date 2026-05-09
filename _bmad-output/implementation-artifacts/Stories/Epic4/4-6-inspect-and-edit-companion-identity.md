# Story 4.6: Inspect and Edit Companion Identity

## 1. Story Foundation
**Epic:** 4 (Local Memory and Evolving Companion Identity)
**Story:** 4.6 (Inspect and Edit Companion Identity)
**Status:** ready-for-dev

**User Story:**
As Ryan,
I want to inspect and edit the companion’s memory and identity files,
So that the banana persona can evolve without being trapped in code.

**Acceptance Criteria:**
- **Given** Ryan opens local memory and prompt/persona files **When** he edits approved persona or memory content **Then** Bananalyzer can load the updated content without source-code changes.
- **Given** Bananalyzer displays status or config paths **When** Ryan wants to inspect identity/memory storage **Then** the relevant `data/memory` and `data/prompts` file paths are visible.
- **Given** a persona or memory file contains invalid formatting **When** Bananalyzer loads it **Then** it reports the issue clearly **And** falls back to safe default behavior where possible.
- **Given** Ryan changes the personality layer **When** the next relevant response is generated **Then** Bananalyzer uses the updated local persona/memory inputs within the current state’s prompt behavior.

## 2. Developer Context & Guardrails

### Technical Requirements
- Ensure that memory and persona file contents are loaded dynamically at runtime (e.g., when building the prompt), not cached indefinitely at startup, or reloaded appropriately when modified.
- Update the CLI `config` or `status` commands to explicitly list the paths for `memory.md`, `session_summary.md`, and the prompt files.
- Add error handling for malformed markdown or JSON.

### Architecture Compliance
- CLI commands (`cli.py`) and diagnostics (`diagnostics.py`) must surface the storage locations clearly to support the "inspectable local files" NFR.

### File Structure Requirements
- **Update:**
  - `src/bananalyzer/cli.py`
  - `src/bananalyzer/diagnostics.py`
  - `src/bananalyzer/persona.py`

### Testing Requirements
- Test that modifying a file on disk reflects in the next generated prompt context.
- Verify CLI outputs the correct paths.

## 3. Previous Story & Git Intelligence
- Leverages the CLI structure built in Epic 1.

## 4. Completion Status
**Status:** ready-for-dev

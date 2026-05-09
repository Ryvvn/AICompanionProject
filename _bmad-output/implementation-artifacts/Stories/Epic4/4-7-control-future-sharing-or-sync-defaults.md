# Story 4.7: Control Future Sharing or Sync Defaults

**Status:** done
**Epic:** 4 - Local Memory and Evolving Companion Identity

## 1. Story Foundation

**User Story:**
As Ryan,
I want future sharing or sync behavior to be explicit opt-in,
So that local-first privacy is preserved by default.

**Acceptance Criteria:**
1. **Given** MVP local configuration is initialized
   **When** sharing or sync settings are inspected
   **Then** external sharing/sync is disabled by default.
2. **Given** no explicit sharing/sync configuration is enabled
   **When** Bananalyzer runs normally
   **Then** captured code, OCR, audio-derived text, memory, and diagnostics remain local.
3. **Given** future sync/cloud settings are represented in config
   **When** Ryan views config or diagnostics
   **Then** the disabled/default status is visible.
4. **Given** a future implementation enables sharing or sync
   **When** that feature is configured
   **Then** it must require explicit user configuration before any external data sharing occurs.

## 2. Developer Context

### Technical Requirements
- Add a `sync_enabled` or `cloud_sharing_enabled` flag to `settings.yaml` under a privacy/sync section, defaulting to `false`.
- Surface this flag in the `status` or `config` CLI command output.
- Add guardrails in the core loop asserting that if `sync_enabled` is ever somehow true, it logs a warning that sync is not implemented in MVP and enforces local-only behavior.

### Architecture Compliance
- Hard-codes the local-only nature of the MVP while preparing the schema for post-MVP cloud sync if requested.

### Code Structure Requirements
- `data/config/settings.yaml`
- `src/bananalyzer/config.py`
- `src/bananalyzer/cli.py`

### Testing Requirements
- Verify that `settings.yaml` parses correctly with the new flag.
- Ensure the default is always `false`.

## 3. Previous Story Intelligence
- Ties into the privacy requirements handled in 4.3.

## 4. Latest Tech Information
- The `sync_enabled` flag should be placed under a `privacy` or `sync` section in `settings.yaml` for clean organization.
- Pydantic model should use `Field(default=False)` for the flag.

## 5. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Add `sync_enabled` flag to config model and `settings.yaml` with default `false`
- [x] Task 2: Surface sync status in CLI `config` and `status` commands
- [x] Task 3: Add guardrails in core loop to enforce local-only when sync is not implemented
- [x] Task 4: Write tests for config parsing and default value verification

## Dev Agent Record

### Agent Model Used
Claude (via BMAD dev-story workflow)

### Debug Log References
- `python -m pytest tests/test_story_4_6_4_7.py -v` — 8/8 pass (4 for 4.6, 4 for 4.7)
- `python -m pytest tests/ -v` — 125/125 pass, zero regressions

### Completion Notes List
- Added `sync_enabled: bool = False` field to Settings Pydantic model in `config.py`
- Added `sync_enabled: false` to `settings.yaml` under privacy/sync section
- CLI `config` command now shows `sync_enabled` in the Detection & Routing Settings table
- CLI `status` command now shows "Cloud Sync: Disabled (local-only)" — warns if somehow enabled
- Added guardrail in `mode_controller.py` `run_text_interaction_loop()`: if `sync_enabled` is true, emits `sync.warning` event and enforces local-only behavior
- Tests verify: model_construct default is False, YAML parsing defaults to False, YAML can parse explicit False, CLI config output includes sync status

### File List
- `src/bananalyzer/config.py`
- `src/bananalyzer/cli.py`
- `src/bananalyzer/mode_controller.py`
- `data/config/settings.yaml`
- `tests/test_story_4_6_4_7.py`

### Change Log
- **2026-05-09**: Added sync_enabled privacy flag defaulting to false, surfaced in CLI config/status, with guardrail in core loop enforcing local-only MVP behavior.

## 6. Story Completion Status


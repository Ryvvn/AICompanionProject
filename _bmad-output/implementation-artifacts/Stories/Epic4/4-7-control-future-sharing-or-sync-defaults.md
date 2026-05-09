# Story 4.7: Control Future Sharing or Sync Defaults

**Status:** ready-for-dev
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

- [ ] Task 1: Add `sync_enabled` flag to config model and `settings.yaml` with default `false`
- [ ] Task 2: Surface sync status in CLI `config` and `status` commands
- [ ] Task 3: Add guardrails in core loop to enforce local-only when sync is not implemented
- [ ] Task 4: Write tests for config parsing and default value verification

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

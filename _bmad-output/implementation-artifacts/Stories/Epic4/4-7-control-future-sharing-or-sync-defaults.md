# Story 4.7: Control Future Sharing or Sync Defaults

## 1. Story Foundation
**Epic:** 4 (Local Memory and Evolving Companion Identity)
**Story:** 4.7 (Control Future Sharing or Sync Defaults)
**Status:** ready-for-dev

**User Story:**
As Ryan,
I want future sharing or sync behavior to be explicit opt-in,
So that local-first privacy is preserved by default.

**Acceptance Criteria:**
- **Given** MVP local configuration is initialized **When** sharing or sync settings are inspected **Then** external sharing/sync is disabled by default.
- **Given** no explicit sharing/sync configuration is enabled **When** Bananalyzer runs normally **Then** captured code, OCR, audio-derived text, memory, and diagnostics remain local.
- **Given** future sync/cloud settings are represented in config **When** Ryan views config or diagnostics **Then** the disabled/default status is visible.
- **Given** a future implementation enables sharing or sync **When** that feature is configured **Then** it must require explicit user configuration before any external data sharing occurs.

## 2. Developer Context & Guardrails

### Technical Requirements
- Add a `sync_enabled` or `cloud_sharing_enabled` flag to `settings.yaml` under a privacy/sync section, defaulting to `false`.
- Surface this flag in the `status` or `config` CLI command output.
- Add guardrails in the core loop asserting that if `sync_enabled` is ever somehow true, it logs a warning that sync is not implemented in MVP and enforces local-only behavior.

### Architecture Compliance
- Hard-codes the local-only nature of the MVP while preparing the schema for post-MVP cloud sync if requested.

### File Structure Requirements
- **Update:**
  - `data/config/settings.yaml`
  - `src/bananalyzer/config.py`
  - `src/bananalyzer/cli.py`

### Testing Requirements
- Verify that `settings.yaml` parses correctly with the new flag.
- Ensure the default is always `false`.

## 3. Previous Story & Git Intelligence
- Ties into the privacy requirements handled in 4.3.

## 4. Completion Status
**Status:** ready-for-dev

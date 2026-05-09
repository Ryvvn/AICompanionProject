# Story 4.3: Apply Privacy Filtering Before Memory Writes

## 1. Story Foundation
**Epic:** 4 (Local Memory and Evolving Companion Identity)
**Story:** 4.3 (Apply Privacy Filtering Before Memory Writes)
**Status:** ready-for-dev

**User Story:**
As Ryan,
I want Bananalyzer to filter captured context before storing memory,
So that private code, OCR, and audio-derived text are not saved carelessly.

**Acceptance Criteria:**
- **Given** context is about to be written to memory **When** privacy filtering runs **Then** `privacy.py` checks the data against the persistence allowlist.
- **Given** raw Screenpipe OCR, raw audio transcript, large code excerpts, or unbounded logs are present **When** memory persistence is attempted **Then** those raw data categories are rejected by default **And** only approved summaries or metadata may be stored.
- **Given** a memory write is blocked by privacy rules **When** diagnostics are enabled **Then** Bananalyzer logs a safe metadata-only event **And** does not leak the blocked raw content into logs.
- **Given** Ryan explicitly approves a memory note **When** the note matches allowed memory categories **Then** it can be persisted as a user-approved local memory entry.

## 2. Developer Context & Guardrails

### Technical Requirements
- Integrate `privacy.py` into the memory writing pipeline in `MemoryStore`.
- Implement the persistence allowlist logic in `privacy.py`.
- Strip out or block large text blocks, raw OCR output, and unapproved code snippets before they reach `store.py`.
- Log blocked writes securely (metadata only, no content leak) using the events system.

### Architecture Compliance
- `privacy.py` must act as a gatekeeper for any persistence actions.
- Local-first privacy is a critical non-functional requirement. Ensure default behavior rejects rather than accepts ambiguous content.

### File Structure Requirements
- **Update:**
  - `src/bananalyzer/privacy.py`
  - `src/bananalyzer/memory/store.py`
  - `tests/test_privacy.py`

### Testing Requirements
- Test that large code blocks or simulated OCR outputs are correctly blocked.
- Test that approved summaries or explicit user goals are allowed through.
- Verify logs do not contain the blocked content.

## 3. Previous Story & Git Intelligence
- Epic 3 successfully established bounding code contexts. Use those truncation/bounding learnings when determining what is "too large" or "raw".

## 4. Completion Status
**Status:** ready-for-dev

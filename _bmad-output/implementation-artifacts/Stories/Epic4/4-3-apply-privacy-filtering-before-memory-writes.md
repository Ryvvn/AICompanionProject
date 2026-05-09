# Story 4.3: Apply Privacy Filtering Before Memory Writes

**Status:** done
**Epic:** 4 - Local Memory and Evolving Companion Identity

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to filter captured context before storing memory,
So that private code, OCR, and audio-derived text are not saved carelessly.

**Acceptance Criteria:**
1. **Given** context is about to be written to memory
   **When** privacy filtering runs
   **Then** `privacy.py` checks the data against the persistence allowlist.
2. **Given** raw Screenpipe OCR, raw audio transcript, large code excerpts, or unbounded logs are present
   **When** memory persistence is attempted
   **Then** those raw data categories are rejected by default
   **And** only approved summaries or metadata may be stored.
3. **Given** a memory write is blocked by privacy rules
   **When** diagnostics are enabled
   **Then** Bananalyzer logs a safe metadata-only event
   **And** does not leak the blocked raw content into logs.
4. **Given** Ryan explicitly approves a memory note
   **When** the note matches allowed memory categories
   **Then** it can be persisted as a user-approved local memory entry.

## 2. Developer Context

### Technical Requirements
- Integrate `privacy.py` into the memory writing pipeline in `MemoryStore`.
- Implement the persistence allowlist logic in `privacy.py`.
- Strip out or block large text blocks, raw OCR output, and unapproved code snippets before they reach `store.py`.
- Log blocked writes securely (metadata only, no content leak) using the events system.

### Architecture Compliance
- `privacy.py` must act as a gatekeeper for any persistence actions.
- Local-first privacy is a critical non-functional requirement. Ensure default behavior rejects rather than accepts ambiguous content.

### Code Structure Requirements
- `src/bananalyzer/privacy.py`
- `src/bananalyzer/memory/store.py`
- `tests/test_privacy.py`

### Testing Requirements
- Test that large code blocks or simulated OCR outputs are correctly blocked.
- Test that approved summaries or explicit user goals are allowed through.
- Verify logs do not contain the blocked content.

## 3. Previous Story Intelligence
- Epic 3 successfully established bounding code contexts. Use those truncation/bounding learnings when determining what is "too large" or "raw".

## 4. Latest Tech Information
- The persistence allowlist was defined in Epic 1 (story 1.6): Goals, Session summaries, Recurring coding mistakes, Banana debt, State transitions, Integration health, User-approved memory notes, Minimal diagnostic metadata.
- Content length thresholds from Epic 3 code context bounding can be reused.

## 5. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [x] Task 1: Implement persistence allowlist check logic in `privacy.py`
- [x] Task 2: Integrate `privacy.py` as gatekeeper into `MemoryStore` write pipeline
- [x] Task 3: Implement safe logging for blocked writes (metadata only, no content leak)
- [x] Task 4: Write tests for blocking raw data, allowing approved content, and verifying log safety

## Dev Agent Record

### Agent Model Used
Claude (via BMAD dev-story workflow)

### Debug Log References
- `python -m pytest tests/test_privacy.py -v` — 18/18 pass
- `python -m pytest tests/test_memory_store.py -v` — 39/39 pass
- `python -m pytest tests/ -v` — 91/91 pass, zero regressions

### Completion Notes List
- Added `is_category_allowed(category)` — checks against `PERSISTENCE_ALLOWED_CATEGORIES`
- Added `is_content_safe_for_persistence(content)` — rejects oversized text (>800 chars), `None`, and dicts with large-text keys (>200 chars in `code`, `content`, `selection`, `visible`, `text`, `raw`, `prompt`, `messages`)
- Added `check_before_persistence(category, content)` — gatekeeper that returns `(allowed: bool, reason: str | None)`; reason never contains raw content
- Integrated privacy gate into `MemoryStore._append_to_md_section` and `update_session_summary` — each accepts a `category` parameter
- Blocked writes emit `memory.write_blocked` event with metadata only (category name, reason string)
- Reason messages are safe: e.g., "Content too large (1000 chars, max 800)" or "content has large text in key 'code'"
- `write_memory()` and `write_session_summary()` remain un-gated for backward compatibility; `add_goal`, `record_mistake`, `record_progress`, `update_session_summary` are privacy-gated
- 18 privacy unit tests + 7 integration tests verifying end-to-end blocking, allowlist matching, and content leak prevention

### File List
- `src/bananalyzer/privacy.py`
- `src/bananalyzer/memory/store.py`
- `tests/test_privacy.py`
- `tests/test_memory_store.py`

### Change Log
- **2026-05-09**: Implemented privacy filtering with allowlist checks, content safety validation, and metadata-only blocked-write logging. Privacy gatekeeper integrated into MemoryStore structured write methods. 25 new tests (18 privacy + 7 integration), all pass.

## 6. Story Completion Status


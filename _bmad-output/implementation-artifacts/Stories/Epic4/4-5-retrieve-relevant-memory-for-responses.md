# Story 4.5: Retrieve Relevant Memory for Responses

**Status:** ready-for-dev
**Epic:** 4 - Local Memory and Evolving Companion Identity

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to use relevant stored memory when responding,
So that it remembers my goals, patterns, and prior progress.

**Acceptance Criteria:**
1. **Given** local memory contains goals or session summaries
   **When** Bananalyzer prepares a response
   **Then** `memory/retrieval.py` can retrieve bounded relevant memory for the current state.
2. **Given** memory retrieval finds relevant entries
   **When** prompt context is built
   **Then** only bounded memory snippets or summaries are included.
3. **Given** memory contains no relevant entries
   **When** Bananalyzer prepares a response
   **Then** the assistant responds normally without inventing memory.
4. **Given** memory retrieval fails
   **When** a response is prepared
   **Then** Bananalyzer continues without memory context
   **And** reports degraded memory retrieval in diagnostics.

## 2. Developer Context

### Technical Requirements
- Create `src/bananalyzer/memory/retrieval.py`.
- Implement logic to read `memory.md` and `session_summary.md` and extract the most relevant/recent sections.
- Inject the retrieved memory into the system prompt via the prompt builder (`persona.py` or `model_router.py`).
- Implement bounds: truncate memory strings so they don't exceed token limits or bloat the prompt.

### Architecture Compliance
- Fallback gracefully: if memory files are corrupted or unreadable, the assistant must still function without them.
- Ensure the retrieval is fast and doesn't introduce noticeable latency.

### Code Structure Requirements
- `src/bananalyzer/memory/retrieval.py`
- `src/bananalyzer/persona.py` (or wherever prompt construction occurs)

### Testing Requirements
- Test that memory content is correctly truncated and injected into the prompt context.
- Test that missing memory files result in an empty string, not an error.

## 3. Previous Story Intelligence
- Context bounding techniques used in Epic 3 for code context should be applied here for memory context.

## 4. Latest Tech Information
- Simple string truncation or token-count-based bounding (e.g., limiting to last N characters or sections) is sufficient for MVP.
- No vector embedding or RAG needed yet — simple section/keyword matching against recent content is adequate.

## 5. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject
- **Communication Language:** English

## Tasks / Subtasks

- [ ] Task 1: Create `src/bananalyzer/memory/retrieval.py` with memory reading logic
- [ ] Task 2: Implement bounded truncation to prevent prompt bloat
- [ ] Task 3: Inject retrieved memory into prompt construction in `persona.py`
- [ ] Task 4: Implement fallback: return empty memory context on errors
- [ ] Task 5: Write tests for truncation and missing-file fallback

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

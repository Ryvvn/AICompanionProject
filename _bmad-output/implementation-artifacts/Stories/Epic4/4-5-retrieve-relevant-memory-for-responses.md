# Story 4.5: Retrieve Relevant Memory for Responses

## 1. Story Foundation
**Epic:** 4 (Local Memory and Evolving Companion Identity)
**Story:** 4.5 (Retrieve Relevant Memory for Responses)
**Status:** ready-for-dev

**User Story:**
As Ryan,
I want Bananalyzer to use relevant stored memory when responding,
So that it remembers my goals, patterns, and prior progress.

**Acceptance Criteria:**
- **Given** local memory contains goals or session summaries **When** Bananalyzer prepares a response **Then** `memory/retrieval.py` can retrieve bounded relevant memory for the current state.
- **Given** memory retrieval finds relevant entries **When** prompt context is built **Then** only bounded memory snippets or summaries are included.
- **Given** memory contains no relevant entries **When** Bananalyzer prepares a response **Then** the assistant responds normally without inventing memory.
- **Given** memory retrieval fails **When** a response is prepared **Then** Bananalyzer continues without memory context **And** reports degraded memory retrieval in diagnostics.

## 2. Developer Context & Guardrails

### Technical Requirements
- Create `src/bananalyzer/memory/retrieval.py`.
- Implement logic to read `memory.md` and `session_summary.md` and extract the most relevant/recent sections.
- Inject the retrieved memory into the system prompt via the prompt builder (`persona.py` or `model_router.py`).
- Implement bounds: truncate memory strings so they don't exceed token limits or bloat the prompt.

### Architecture Compliance
- Fallback gracefully: if memory files are corrupted or unreadable, the assistant must still function without them.
- Ensure the retrieval is fast and doesn't introduce noticeable latency.

### File Structure Requirements
- **Create/Update:**
  - `src/bananalyzer/memory/retrieval.py`
  - `src/bananalyzer/persona.py` (or wherever prompt construction occurs)

### Testing Requirements
- Test that memory content is correctly truncated and injected into the prompt context.
- Test that missing memory files result in an empty string, not an error.

## 3. Previous Story & Git Intelligence
- Context bounding techniques used in Epic 3 for code context should be applied here for memory context.

## 4. Completion Status
**Status:** ready-for-dev

# Story 4.2: Save Goals, Progress, Mistakes, and Summaries

## 1. Story Foundation
**Epic:** 4 (Local Memory and Evolving Companion Identity)
**Story:** 4.2 (Save Goals, Progress, Mistakes, and Summaries)
**Status:** ready-for-dev

**User Story:**
As Ryan,
I want Bananalyzer to remember useful development and behavior context,
So that the companion feels continuous across sessions.

**Acceptance Criteria:**
- **Given** Ryan provides or approves a goal 
  **When** Bananalyzer saves memory 
  **Then** the goal can be persisted in local memory.
- **Given** a coding session produces useful learning context 
  **When** Bananalyzer updates memory 
  **Then** it can save coding progress, recurring mistakes, and concise behavior summaries.
- **Given** gaming or distraction activity affects accountability 
  **When** behavior memory is updated 
  **Then** banana debt or behavior summary data can be persisted in the appropriate local memory file.
- **Given** raw runtime history exists 
  **When** Bananalyzer writes memory 
  **Then** it stores concise summaries or approved memory notes rather than unbounded raw logs.

## 2. Developer Context & Guardrails

### Technical Requirements
- Extend `MemoryStore` to handle appending or updating specific sections within the markdown memory files (`memory.md` and `session_summary.md`).
- Implement methods to add goals, record coding progress, log mistakes, and update summaries.
- Ensure that updates to the Markdown files maintain a readable, human-friendly structure (e.g., using markdown headers or lists).
- Ensure that updates to `banana_debt.json` are structured properly and safely serialized.

### Architecture Compliance
- The update logic should reside in or near `src/bananalyzer/memory/store.py` or a new `src/bananalyzer/memory/summarizer.py` if summarization logic becomes complex.
- Only save summarized or approved notes. Do not dump raw text or extensive logs into the memory files.

### File Structure Requirements
- **Update:**
  - `src/bananalyzer/memory/store.py`
  - `src/bananalyzer/memory/summarizer.py` (if created)
  - `tests/test_memory_store.py`

### Testing Requirements
- Unit tests to verify that adding a goal or mistake correctly updates the underlying markdown structure without destroying previous content.
- Tests to verify JSON updates for banana debt are appended/updated safely.

## 3. Previous Story & Git Intelligence
- Build upon the `MemoryStore` foundation established in 4.1.

## 4. Completion Status
**Status:** ready-for-dev

# Story 3.2: Build Bounded Coding Context

**Status:** ready-for-dev
**Epic:** 3 - Active Code Companion for Rubber-Duck Support

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to use only relevant bounded code context,
So that coding help stays useful without bloating prompts or storing too much code.

**Acceptance Criteria:**
1. **Given** active code context is retrieved
   **When** Bananalyzer prepares a coding prompt
   **Then** `context/code_context.py` and `context/context_builder.py` convert it into bounded prompt context.
2. **Given** the active file contains more code than the configured context limit
   **When** prompt context is built
   **Then** Bananalyzer includes only the allowed bounded excerpt, selected text, visible range, or summarized context.
3. **Given** code context may be logged or stored
   **When** privacy filtering runs
   **Then** raw large code excerpts are not persisted by default
   **And** only approved metadata or summaries are allowed.
4. **Given** context is unavailable
   **When** the context builder runs
   **Then** it returns a clear no-context result rather than failing the full response flow.

## 2. Developer Context

### Technical Requirements
- **Logic implementation:** Implement logic in `src/bananalyzer/context/code_context.py` to shape raw file context. Use `src/bananalyzer/context/context_builder.py` to combine context signals safely.
- **Privacy:** `src/bananalyzer/privacy.py` should enforce rules that raw code context over a certain size or unapproved data is dropped before any persistence or logging.
- **Graceful Failures:** If context is missing/unavailable, the context builder must return a safe fallback object (e.g. empty context string) instead of throwing an error.

### Architecture Compliance
- **File Structure:**
  - `src/bananalyzer/context/code_context.py`
  - `src/bananalyzer/context/context_builder.py`
  - `src/bananalyzer/privacy.py`
- **Config Driven:** Read context limits from the `config.py` settings (ensure a default context token or line limit is used).
- **No Side Effects:** Context builder should purely return context data structures and must not trigger state changes.

### Testing Requirements
- Unit tests in `tests/context/test_context_builder.py`.
- Validate that large inputs are truncated or summarized according to the bounds.
- Validate that missing inputs result in an empty/safe context string.
- Validate privacy filtering drops raw code from log payloads.

## 3. Previous Story Intelligence
- Epic 2 showed the value of separating state logic from side effects. Similarly, the context building should remain stateless and purely data-transformative.

## 4. Latest Tech Information
- Context size boundaries are crucial for Ollama models (e.g., 2K, 4K, 8K limits). Truncation should preferably preserve the current line/selection and surround it, rather than just grabbing the top of the file.

## 5. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject

## 6. Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created.
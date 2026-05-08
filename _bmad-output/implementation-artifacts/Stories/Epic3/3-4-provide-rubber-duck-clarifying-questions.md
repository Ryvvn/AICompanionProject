# Story 3.4: Provide Rubber-Duck Clarifying Questions

**Status:** ready-for-dev
**Epic:** 3 - Active Code Companion for Rubber-Duck Support

## 1. Story Foundation

**User Story:**
As Ryan,
I want Bananalyzer to ask clarifying questions while helping with code,
So that I reason through implementation issues instead of only receiving answers.

**Acceptance Criteria:**
1. **Given** Bananalyzer is in `coding` mode
   **When** Ryan asks a vague debugging question such as "why isn’t this working?"
   **Then** the assistant asks targeted clarifying questions based on the active context.
2. **Given** active code context suggests multiple possible causes
   **When** the assistant responds
   **Then** it presents the likely reasoning paths clearly
   **And** asks Ryan to confirm assumptions before committing to a conclusion.
3. **Given** Ryan asks for direct explanation instead of coaching
   **When** the assistant responds
   **Then** it still provides useful explanation
   **And** may include a small number of clarifying prompts without blocking progress.
4. **Given** the coding prompt is loaded
   **When** rubber-duck behavior is applied
   **Then** the behavior comes from the coding persona/prompt configuration rather than hardcoded unrelated logic.

## 2. Developer Context

### Technical Requirements
- **Prompt Engineering:** This story relies primarily on adjusting `data/prompts/coding.md` to instruct the model to adopt a Socratic, rubber-duck debugging persona.
- **Configurability:** Ensure the persona loader in `persona.py` correctly injects instructions without hardcoding the "rubber duck" string in Python.
- **No Blocking Prompts:** The prompt must balance asking questions with providing help. We don't want an endless loop of unhelpful questions.

### Architecture Compliance
- **File Structure:**
  - `data/prompts/coding.md`
  - `src/bananalyzer/persona.py`
- **Pattern:** Use local markdown files for prompt behavior. The python code shouldn't know what a "rubber duck" is. It just executes the `coding` prompt.

### Testing Requirements
- Manual/Integration testing of the LLM output with the new `coding.md` prompt.
- Unit test to ensure `data/prompts/coding.md` is loaded correctly by `persona.py` and combined with the context variables.

## 3. Previous Story Intelligence
- Epic 2 established state-specific prompts. We can leverage that structure directly.

## 4. Project Context Reference
- **Date:** 2026-05-08
- **Project:** AICompanionProject

## 5. Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created.
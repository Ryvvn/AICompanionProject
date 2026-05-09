# Epic 4 Intern Knowledge Check: Local Memory and Evolving Companion Identity

**Date:** 2026-05-09
**Epic Number:** 4
**Epic Name:** Local Memory and Evolving Companion Identity
**Intern/Junior Dev:** Elena
**Reviewer:** Charlie (Senior Dev) / Amelia (Developer)

---

## Part 1: Architecture & Design Decisions

1. **Why did we make `MemoryStore` the sole accessor for all memory files instead of letting components read/write directly?**
   - *Elena's Answer:* It enforces the Local-First Persistence architectural pattern. Having a single chokepoint ensures that all file operations can be safely wrapped in try/except blocks for graceful degradation, and guarantees that the `privacy.py` gatekeeper is always invoked before any write occurs.
2. **How does `privacy.py` act as a gatekeeper, and why is this critical for the upcoming Epic 5?**
   - *Elena's Answer:* Before `MemoryStore` writes a goal, mistake, or summary, it passes the payload through `check_before_persistence()`. If the content is too large or contains raw data like OCR or code blocks, it's rejected. This is critical for Epic 5 because Screenpipe will generate massive amounts of raw OCR data, and we must ensure it doesn't leak into our persistent files or logs.

## Part 2: State & Data Management

3. **How does `banana_debt.json` handle updates safely compared to the markdown files?**
   - *Elena's Answer:* Unlike markdown where we append lines under specific section headers, the JSON file uses a read-modify-write pattern. It reads the existing JSON into a dictionary, merges the new data using `dict.update()`, and then safely writes it back to avoid data loss.
4. **How does the system ensure the memory context doesn't bloat the prompt beyond token limits?**
   - *Elena's Answer:* `src/bananalyzer/memory/retrieval.py` fetches the content but passes it through `truncate_memory_context()`. This bounds the text to a strict character limit (default 1000) and appends a truncation notice before injecting it as `{{memory_context}}` into the prompt template.

## Part 3: Integrations & Error Handling

5. **How does `MemoryStore` handle situations where it lacks permission to write to the data directory?**
   - *Elena's Answer:* All file writes catch `OSError` and `IOError`. If one is caught, the store sets `self.available = False`, logs a `memory.unavailable` event, and allows the main application loop to continue running in a degraded "no-memory" mode without crashing.
6. **What happens if a user accidentally deletes `memory.md` while the app is running?**
   - *Elena's Answer:* The next time `MemoryStore` attempts to read the file, it catches that it's missing, recreates it with safe initial content (empty headers), and emits a `memory.missing_recreated` event.

## Part 4: Product & User Experience

7. **How does the periodic summarization feature capture progress without interrupting Ryan's workflow?**
   - *Elena's Answer:* The `mode_controller.py` loop checks the elapsed time against `memory_update_interval_seconds` between user interactions. The summarizer checks if the state has meaningfully changed (`should_skip_update()`) and only updates the summary if needed, acting as a non-blocking background step.
8. **How does Ryan know where his memory files are stored so he can inspect or edit them?**
   - *Elena's Answer:* We updated the CLI `config` and `status` commands to explicitly list the absolute file paths for `memory.md`, `session_summary.md`, and `banana_debt.json`.

## Part 5: Testing & Quality

9. **How did we test file I/O errors (like `PermissionError`) without needing complex physical setups or breaking our CI?**
   - *Elena's Answer:* We used `pytest-mock` to patch `pathlib.Path.write_text` and `pathlib.Path.mkdir` to raise exceptions on demand. This let us test our graceful degradation logic with 100% reliability.
10. **Why did we flag the code duplication between `summarizer.py` and `retrieval.py` as deferred technical debt?**
   - *Elena's Answer:* Both files were using the exact same logic to parse Markdown sections (Goals, Mistakes, Progress). While it works for MVP, maintaining duplicate parsing logic is risky. If we change the markdown structure later, we'd have to update it in multiple places. It needs a shared helper.

---

## Reviewer Sign-off
- [x] Intern demonstrated solid understanding of the architecture.
- [x] Intern understood the product value and UX constraints.
- [x] Knowledge gaps were identified and addressed during the review.
- **Notes/Follow-up Learning:** Elena has an excellent grasp of the privacy gatekeeper pattern and why `MemoryStore` handles I/O exceptions the way it does. She recognized her own technical debt regarding the duplicated markdown parsing and the imprecise skip check, and she's assigned to fix them before Epic 5 begins. She is fully prepared for the Screenpipe challenges ahead.

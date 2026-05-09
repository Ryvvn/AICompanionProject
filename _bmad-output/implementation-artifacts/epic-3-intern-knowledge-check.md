# Epic 3 Intern Knowledge Check: Active Code Companion for Rubber-Duck Support

**Date:** 2026-05-08
**Epic Number:** 3
**Epic Name:** Active Code Companion for Rubber-Duck Support
**Intern/Junior Dev:** Elena
**Reviewer:** Charlie (Senior Dev) / Amelia (Developer)

---

## Part 1: Architecture & Design Decisions

1. **Why did we build a separate `context_builder.py` instead of having `model_router.py` fetch the MCP context directly?**
   - *Elena's Answer:* Separation of concerns. The `context_builder.py` is purely for data transformation and shaping. `model_router.py` should only care about sending prompts to the LLM and shouldn't be responsible for network calls or truncation logic.
2. **Where does the code for bounding and truncating context live, and why is it important?**
   - *Elena's Answer:* It lives in `src/bananalyzer/context/code_context.py`. It's critical because LLMs have context limits (like 2K or 4K tokens). If we just dumped a 10,000-line file into the prompt, it would bloat the prompt, increase latency, and potentially cause the model to fail or hallucinate.
3. **If a new integration was added to read terminal output, how would our current context architecture support it?**
   - *Elena's Answer:* We'd create a new adapter (like `integrations/terminal.py`), and then update `context_builder.py` to combine the terminal signals with the active code context safely before passing it to the prompt templates.

## Part 2: State & Data Management

4. **How does the system ensure we don't save massive code files into our local event logs?**
   - *Elena's Answer:* Before anything is written to `data/logs/events.jsonl`, the payloads pass through `src/bananalyzer/privacy.py`. The privacy module enforces an allowlist and strips out large raw code blocks, replacing them with safe metadata.
5. **Where are the prompt templates stored, and how does the code context get injected into them?**
   - *Elena's Answer:* They are stored in `data/prompts/`. `src/bananalyzer/persona.py` handles the injection by replacing the `{{code_context_block}}` placeholder in the markdown files with the bounded context string.

## Part 3: Integrations & Error Handling

6. **How does the system behave if the MCP server (VS Code extension) is completely down?**
   - *Elena's Answer:* The `MCPAdapter.health_check()` catches the connection error (like a timeout or connection refused) and returns a `HealthCheckResult` with `ok=False`. The assistant doesn't crash; it degrades gracefully and falls back to standard text interaction without code context.
7. **What did we use to test the HTTP calls in `test_mcp.py` without needing a real server?**
   - *Elena's Answer:* We used `pytest-mock` to patch `httpx.Client` or the specific HTTP methods so we could simulate both successful JSON responses and network exceptions.

## Part 4: Product & User Experience

8. **What specific user problem (from the PRD) does this Epic solve?**
   - *Elena's Answer:* Ryan needs Bananalyzer to understand the code he's currently looking at so it can act as a rubber duck. Instead of Ryan copy-pasting code manually, the assistant fetches it automatically and asks clarifying questions to help him reason through bugs.
9. **How does the user know if the MCP integration is working?**
   - *Elena's Answer:* They can run `uv run bananalyzer status` or `uv run bananalyzer dashboard`, and the integration health section will show whether MCP is `available`, `degraded`, or `unavailable`.

## Part 5: Testing & Quality

10. **What was the most complex scenario to test in this Epic, and how did we validate it?**
   - *Elena's Answer:* Ensuring the `model_router.py` didn't crash when local generation (like Ollama) was unavailable. We validated it by mocking the generation function to throw an error and asserting that the router returned a safe fallback message explaining the issue.

---

## Reviewer Sign-off
- [x] Intern demonstrated solid understanding of the architecture.
- [x] Intern understood the product value and UX constraints.
- [x] Knowledge gaps were identified and addressed during the review.
- **Notes/Follow-up Learning:** Elena has a strong grasp of the `context_builder.py` and `privacy.py` data flow. She understands why bounding context is critical for performance and prompt relevance, which will be foundational for the upcoming Screenpipe OCR integrations. She's ready for Epic 4.

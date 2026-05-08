# Epic 2 Intern Knowledge Check: Context-Aware Mode Detection and Routing

**Date:** 2026-05-08
**Epic Number:** 2
**Epic Name:** Context-Aware Mode Detection and Routing
**Intern/Junior Dev:** Elena
**Reviewer:** Charlie (Senior Dev) / Amelia (Developer)

---

## Part 1: Architecture & Design Decisions

1. **Why did we build the State Machine with strict canonical states instead of dynamic modes based on app names?**
   - *Elena's Answer:* So the rest of the app doesn't have to guess or handle infinite random modes. We only route to known profiles: `coding`, `gaming`, `doomscrolling`, `companion`, or `fallback`. This prevents unpredictable behavior.
2. **Where does the code for foreground detection live, and why does it belong in that specific module?**
   - *Elena's Answer:* It lives in `src/bananalyzer/foreground.py`. It's isolated so it acts as a *detector*, not a *decider*. It emits a signal to the State Machine, which then makes the final decision on whether to transition.
3. **If a new requirement came in to add a "video_editing" state, how would our current architecture support it?**
   - *Elena's Answer:* We'd add `video_editing` to the canonical states Enum in `state_machine.py`, add the app mappings to `data/config/settings.yaml`, create a `video_editing.md` prompt in `data/prompts/`, and define a model profile for it.
4. **Explain the data flow when the user switches to VS Code.**
   - *Elena's Answer:* `foreground.py` detects `Code.exe` and maps it to `coding`. It sends a candidate signal to `state_machine.py`. The State Machine validates the transition, writes to `data/state/current_state.json`, emits a `state.changed` event, and the `model_router` switches to the coding profile.

## Part 2: State & Data Management

5. **Where is the data for state routing stored, and what format is it in?**
   - *Elena's Answer:* Configuration like app mappings is in `data/config/settings.yaml`. The active runtime state is written to `data/state/current_state.json`.
6. **Why did we choose to enforce Canonical States rather than allowing dynamic inputs?**
   - *Elena's Answer:* It makes testing predictable and ensures our prompt routing and model selection logic always has a matching configuration.
7. **If the application crashes while reading the active window, what happens to the data?**
   - *Elena's Answer:* The system catches the exception and returns a fallback signal. The state safely transitions to `fallback` without corrupting `current_state.json`.

## Part 3: Integrations & Error Handling

8. **How does the system behave if the foreground detector fails entirely?**
   - *Elena's Answer:* It degrades gracefully into `fallback` mode. The text-interaction baseline remains operational, so the user can still chat with Bananalyzer.
9. **Where do we log errors for missing prompt files, and what happens?**
   - *Elena's Answer:* It emits a `prompt.selected` or `prompt.degraded` warning event to `data/logs/events.jsonl` and falls back to a safe default prompt.
10. **Explain the purpose of the adapter pattern used for Windows API integration.**
    - *Elena's Answer:* It isolates third-party dependencies (`pywin32`, `psutil`) so if they fail or act weird, the rest of the orchestration loop doesn't know or care. It just receives a standard failure response.

## Part 4: Product & User Experience

11. **What specific user problem (from the PRD) does this Epic solve?**
   - *Elena's Answer:* Ryan needs Bananalyzer to know what he's doing so it can adapt its tone and resource usage—like being helpful and using a stronger model when coding, but lightweight when he's just idling (companion mode).
12. **How does the user interact with the features built in this Epic?**
   - *Elena's Answer:* They can view the current state and model profile via the `uv run bananalyzer status` CLI command, or edit thresholds directly in the YAML config files.
13. **What are the privacy implications of the data we capture in this Epic, and how did we mitigate them?**
   - *Elena's Answer:* We track the active window title and process name. We mitigate privacy issues by only storing the *canonical state category* in `current_state.json`, avoiding persisting raw window titles (like private document names) to disk.

## Part 5: Testing & Quality

14. **What was the most complex scenario to test in this Epic, and how did we validate it?**
   - *Elena's Answer:* Testing the Windows API polling without having to actually open and close apps during unit tests. We validated it by mocking the OS-level calls.
15. **If you had to write an automated test for foreground detection, what would you mock or stub?**
   - *Elena's Answer:* We used `pytest-mock` to mock `win32gui` and `psutil`. And we learned to patch the class method `pathlib.Path.exists` instead of the instance attribute!

---

## Reviewer Sign-off
- [x] Intern demonstrated solid understanding of the architecture.
- [x] Intern understood the product value and UX constraints.
- [x] Knowledge gaps were identified and addressed during the review.
- **Notes/Follow-up Learning:** Elena clearly understands the boundaries between detectors and deciders, and her grasp of graceful degradation is excellent. She's ready to tackle the MCP integration in Epic 3.

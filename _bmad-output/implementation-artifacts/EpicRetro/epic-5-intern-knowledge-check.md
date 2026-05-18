# Epic 5 Intern Knowledge Check: Behavioral Accountability and Distraction Interventions

**Date:** 2026-05-11
**Epic Number:** 5
**Epic Name:** Behavioral Accountability and Distraction Interventions
**Intern/Junior Dev:** Elena
**Reviewer:** Charlie (Senior Dev) / Amelia (Developer)

---

## Part 1: Architecture & Design Decisions

1. **Why do we use a dual-path classification strategy for Distraction Signals?**
   - *Elena's Answer:* Screenpipe provides rich context like OCR and browser URLs, but it's a heavy integration that might crash or be disabled. The dual-path strategy allows `DistractionSignals.classify_doomscroll()` to use Screenpipe when available, but safely fall back to checking just the foreground app duration (`_classify_foreground_only()`) if Screenpipe fails, ensuring the feature still works in a degraded state.
2. **Why was Screenpipe polling offloaded and given a specific interval instead of querying on every loop?**
   - *Elena's Answer:* Polling Screenpipe continuously caused UI stuttering and blocked the main thread. By using `screenpipe_poll_interval_seconds`, we decouple the heavy HTTP request from the tight interactive loop, keeping the CLI responsive.

## Part 2: State & Data Management

3. **How does "Banana Debt" actually accumulate and reduce?**
   - *Elena's Answer:* It's a localized metric persisted in `banana_debt.json`. The `AccountabilityEngine` uses ratios defined in `thresholds.yaml`. Productive states like `coding` apply a negative ratio (reducing debt), while avoidant states like `doomscrolling` or `gaming` apply positive ratios (increasing debt) over time.
4. **How do we ensure that interventions don't become annoying spam?**
   - *Elena's Answer:* We enforce an `intervention_cooldown_seconds` check in the `AccountabilityEngine`. Even if the debt is high, the system won't trigger another interruption until the cooldown period has expired.

## Part 3: Integrations & Error Handling

5. **How does `ScreenpipeAdapter` prevent the whole app from crashing if the Screenpipe server dies?**
   - *Elena's Answer:* The adapter wraps all `httpx` calls in `try/except` blocks that catch `TimeoutException`, `RequestError`, and generic `Exception`. It returns a safe error dictionary or `HealthCheckResult` indicating failure, rather than letting the exception bubble up to the `mode_controller`.
6. **How does the system react when Screenpipe explicitly disabled in the configuration?**
   - *Elena's Answer:* If `screenpipe_enabled: False` is set in `settings.yaml`, the system skips the HTTP checks entirely. `integration_health.json` is updated to show it as unavailable/degraded, and the `doomscrolling` state prefix explicitly says `[Degraded: Screenpipe disabled — using foreground-only detection]`.

## Part 4: Product & User Experience

7. **What makes an accountability intervention "Goal-Aware"?**
   - *Elena's Answer:* When an intervention is triggered, `interventions.py` fetches the user's active goals from the `MemoryStore`. It injects these goals into the prompt so the "Mean Banana" persona can specifically reference what the user *should* be working on instead of doomscrolling.
8. **How do we ensure "Mean Banana" is sarcastic but never abusive?**
   - *Elena's Answer:* The tone boundaries are enforced at the prompt level. The `doomscroll.md` prompt explicitly instructs the LLM to use a strict, accountability-focused tone while prohibiting abusive, discriminatory, or self-harm-reinforcing language.

## Part 5: Testing & Quality

9. **Why did the CI pipeline fail initially during Epic 5 testing?**
   - *Elena's Answer:* The tests relied heavily on `pytest-mock` to simulate Screenpipe failures and timeouts without needing the actual server running. However, `pytest-mock` wasn't added to the `pyproject.toml` dependencies, causing the `mocker` fixture to be missing. Adding it via `uv add --dev pytest-mock` fixed the 68 failing tests.
10. **Why did we backlog the Screenpipe integration fix to Post-MVP?**
    - *Elena's Answer:* Screenpipe relies on a heavy Rust toolchain that proved brittle on Windows during testing. Since the foreground-only fallback logic works perfectly for detecting distraction duration, we prioritized stability. We logged the technical debt to investigate a pure-Python OCR fallback (`pytesseract`/`easyocr`) for the future.

---

## Reviewer Sign-off
- [x] Intern demonstrated solid understanding of the architecture.
- [x] Intern understood the product value and UX constraints.
- [x] Knowledge gaps were identified and addressed during the review.
- **Notes/Follow-up Learning:** Elena has a strong grasp of the dual-path classification and why we had to backlog the Screenpipe dependency for stability. She understands the mechanics of Banana Debt and the importance of prompt-level safety boundaries for the persona. She is ready to tackle the latency challenges coming up in Epic 6 voice integration.
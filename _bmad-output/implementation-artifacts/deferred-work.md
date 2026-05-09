# Deferred Work

## Deferred from: code review of Epic 4 stories (2026-05-09)

- **F2 Code duplication**: Section parsing logic duplicated between `summarizer.py:L30-L54` and `retrieval.py:L32-L53`. Both extract Goals, Mistakes, Progress sections from `memory.md` using the same pattern. Extract a shared helper.
- **F3 Imprecise skip check**: `should_skip_update()` in `summarizer.py:L17-L21` uses substring matching for state name. A state like `"coding"` would match `"coding_tutorial"` in the summary. Consider a more precise comparison.
- **F5 Singleton thread safety**: `_memory_store` singleton in `mode_controller.py:L24` has a check-then-initialize race condition. Not critical for MVP (single-threaded), but should add a lock if the interaction loop becomes concurrent.
- **F7 Scaffold incomplete**: `scaffold_data_foundation()` in `config.py:L181` does not include `sync_enabled` or `memory_update_interval_seconds` in the generated `settings.yaml`. Pydantic fills defaults at runtime, so this is cosmetic.

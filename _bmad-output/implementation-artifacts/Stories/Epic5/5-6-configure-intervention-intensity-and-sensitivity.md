# 5-6 Configure Intervention Intensity and Sensitivity

**Status:** review
**Epic:** Epic 5

## 1. Story Foundation
**User Story:**
As Ryan,
I want to tune doomscroll sensitivity and intervention intensity,
So that Bananalyzer helps without becoming too disruptive.

**Acceptance Criteria:**
1. **Given** Ryan opens local threshold/config files **When** he inspects accountability settings **Then** doomscroll thresholds, gaming thresholds, intervention cooldowns, and intensity settings are editable.
2. **Given** Ryan lowers intervention intensity **When** accountability interventions occur **Then** the assistant uses less disruptive wording, frequency, or delivery behavior according to config.
3. **Given** Ryan disables or reduces disruptive behavior **When** thresholds or intensity settings are applied **Then** Bananalyzer respects those settings without source-code changes.
4. **Given** accountability config is invalid **When** Bananalyzer loads settings **Then** it reports the problem clearly **And** uses safe conservative defaults.

## 2. Developer Context
### Technical Requirements
- Expand `data/config/thresholds.yaml` and `data/config/settings.yaml` to include intervention-specific configurations: `doomscroll_threshold`, `gaming_threshold`, `intervention_cooldown`, and `intervention_intensity` (e.g., low, medium, high).
- Modify the intervention generation logic to adjust prompt wording or skip triggering based on the `intervention_intensity` and `intervention_cooldown`.
- Add validation logic in `src/bananalyzer/config.py` using Pydantic to ensure these new settings are valid, applying safe defaults if they are missing or malformed.

### Architecture Compliance
- **Configurable Boundaries:** The core loop must read these values dynamically or on load, not hardcode them.
- **Robustness:** Invalid configurations must not crash the app. Pydantic should fall back to defaults and log warnings.

### Code Structure Requirements
- `src/bananalyzer/config.py` (UPDATE)
- `src/bananalyzer/accountability/interventions.py` (UPDATE)
- `data/config/thresholds.yaml` (UPDATE)

### Testing Requirements
- Unit tests to verify Pydantic models correctly parse valid configurations and apply defaults to invalid ones.
- Test that `intervention_cooldown` correctly prevents rapid consecutive interventions.
- Test that `intervention_intensity` alters the generation behavior or prompt.

## 3. Previous Story Intelligence
- **Epic 1 Config Loading:** The project uses Pydantic Settings. Ensure the new accountability settings integrate cleanly into the existing Pydantic models.

## 4. Latest Tech Information
- N/A

## 5. Project Context Reference
- **Epic:** Epic 5: Behavioral Accountability and Distraction Interventions
- **PRD:** FR18 (Adjust intervention intensity or disable)
- **Architecture:** Configuration boundaries.

## Tasks / Subtasks

- [x] Add accountability settings to Pydantic config models.
- [x] Implement cooldown logic in intervention triggers.
- [x] Adjust prompt instructions based on `intervention_intensity`.
- [x] Add tests for invalid config fallback and cooldown timing.

## Dev Agent Record

### Agent Model Used
Claude (via bmad-dev-story)

### Completion Notes
- Added `intervention_cooldown_seconds`, `intervention_intensity`, and `gaming_threshold_mins` to the `Thresholds` Pydantic model with validation (intensity must be low/medium/high).
- `InterventionManager._is_cooldown_active()` prevents rapid consecutive interventions, configurable via `intervention_cooldown_seconds`.
- `InterventionManager._get_intensity_modifier()` provides three tiers of language: gentle (low), firm (medium), sarcastic (high) — injected into intervention prompts.
- Invalid config values trigger Pydantic validation errors; `load_thresholds_safe()` provides safe defaults.
- Tests cover: cooldown blocking, intensity validation for all three levels + invalid rejection, cooldown time validation as positive integer.

### File List
- `src/bananalyzer/config.py` (UPDATE)
- `data/config/thresholds.yaml` (UPDATE)
- `src/bananalyzer/accountability/interventions.py` (UPDATE)
- `tests/test_config.py` (UPDATE)
- `tests/accountability/test_interventions.py` (NEW)

### Change Log
- **2026-05-10**: Implemented configurable intervention intensity and cooldown with Pydantic validation and safe defaults.

## 6. Story Completion Status
- [x] Dev implementation complete
- [ ] Code review completed
- [ ] Status updated to done

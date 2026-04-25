# Sprint Change Proposal - Implementation Readiness Findings

**Date:** 2026-04-25
**Project:** AICompanionProject
**Prepared for:** Ryan
**Source finding:** `_bmad-output/planning-artifacts/implementation-readiness-report-2026-04-25.md`

## 1. Issue Summary

The implementation readiness assessment found that the planning artifacts are close to ready, but Phase 4 implementation should not begin until several readiness findings are addressed.

Primary trigger:

- Foundational text interaction/manual fallback is currently defined as Story 6.1 in Epic 6, but earlier epics already depend on reliable text interaction.

Evidence from the readiness report:

- Story 2.5 requires fallback mode to continue supporting safe text-based interaction.
- Story 3.6 requires general text interaction when MCP/code context is unavailable.
- FR48 is covered by Epic 1, but the concrete text interaction baseline is delayed until Epic 6.
- This creates a forward dependency and weakens epic independence.

Secondary findings:

- Story 1.2 creates memory/accountability storage before those features are implemented; this should be clarified as scaffolding only or deferred.
- No UX design artifact exists, while user-facing CLI/status/dashboard/config/intervention behavior is implied.
- Some acceptance criteria remain qualitative and would benefit from measurable checks.
- CI/CD is not represented; for a personal MVP this can be documented as intentionally out of scope or added as an optional small story/criterion.

## 2. Impact Analysis

### Epic Impact

#### Epic 1: Local Companion Foundation and Operational Visibility

Affected. Epic 1 should include the reliable text interaction baseline because it already claims FR48 and supports degraded/manual operation.

Required change:

- Add a new Story 1.7, or insert the split baseline from Story 6.1 after Story 1.6.
- Update Epic 1 FR coverage to include FR30, FR33, and FR34 if the baseline covers typed input and text output fallback.
- Keep Epic 1 focused on reliable local operation, not full voice behavior.

#### Epic 2: Context-Aware Mode Detection and Routing

Affected by dependency clarification only.

Required change:

- Story 2.5 can remain as-is once text interaction baseline exists in Epic 1.
- Optionally add a note that safe text interaction is provided by the Epic 1 baseline.

#### Epic 3: Active Code Companion for Rubber-Duck Support

Affected by dependency clarification only.

Required change:

- Story 3.6 can remain as-is once text interaction baseline exists in Epic 1.
- Optionally add a note that general text interaction is provided by the Epic 1 baseline.

#### Epic 4: Local Memory and Evolving Companion Identity

Affected by storage timing clarification.

Required change:

- Ensure Story 4.1 owns actual memory behavior.
- Story 1.2 may create placeholders only; memory behavior should not be implemented until Epic 4.

#### Epic 5: Behavioral Accountability and Distraction Interventions

Affected by storage timing and UX notes.

Required change:

- Ensure Story 5.4 owns banana debt behavior.
- Story 1.2 may create `banana_debt.json` only as empty scaffolding if kept there.
- Add lightweight UX guidance before Stories 5.6 and 5.7.

#### Epic 6: Voice Interaction and Graceful Multimodal Fallbacks

Affected directly.

Required change:

- Remove Story 6.1 from Epic 6 or replace it with a cross-reference that the text baseline is implemented in Epic 1.
- Keep Epic 6 focused on TTS, optional STT, CPU-side voice settings, and voice degraded modes.
- Rename Epic 6 to avoid implying it owns text baseline.

### Story Impact

Affected stories:

- Story 1.2: clarify scaffolding vs feature behavior.
- New Story 1.7: reliable text interaction baseline.
- Story 2.5: dependency resolved by Story 1.7.
- Story 3.6: dependency resolved by Story 1.7.
- Story 5.6 / 5.7: require lightweight UX notes for config/intensity/tone behavior.
- Story 6.1: move/split into Epic 1, then remove from Epic 6.
- Stories 6.2-6.6: renumber to 6.1-6.5 after removal.

### Artifact Conflicts

#### PRD

The PRD does not need a major scope change. It already supports text fallback and voice optionality.

Recommended PRD clarification:

- Clarify that typed text interaction is part of the MVP foundation before voice features.
- Keep STT optional and TTS as a voice extension, not a blocker for baseline interaction.

#### Architecture

Architecture is mostly aligned. It already defines CLI commands, degraded modes, adapter boundaries, and text fallback.

Recommended architecture clarification:

- In implementation sequence, ensure text interaction baseline appears before state-dependent behaviors that rely on manual fallback.
- Clarify that memory/accountability files created in foundation are empty scaffolding unless implemented by Epic 4/Epic 5 stories.

#### UX

No UX artifact exists. This is acceptable for a CLI/Textual MVP, but story-level UX guidance should be added.

Recommended UX additions:

- Add lightweight notes for status output fields.
- Add dashboard section list.
- Add config command discoverability expectations.
- Add intervention intensity/tone examples and limits.
- Add text/voice interaction fallback behavior.

### Technical Impact

Technical change scope is planning/backlog only. No code is affected yet.

Implementation sequencing improves because:

- Text input/output baseline becomes available before fallback/degraded stories depend on it.
- Voice work becomes a later extension rather than a prerequisite for basic interaction.
- Storage behavior remains bounded and avoids implementing memory/accountability too early.

## 3. Recommended Approach

Recommended path: **Direct Adjustment**.

Rationale:

- The issue is a sequencing/backlog issue, not a product pivot.
- No epic needs to be removed.
- MVP scope remains intact.
- The direct fix is to move/split Story 6.1 into Epic 1, clarify Story 1.2, add lightweight UX notes, and optionally document CI scope.

Effort estimate: Low to Medium.
Risk level: Low.
Timeline impact: Minimal; likely improves implementation flow by removing forward dependencies before coding starts.

Alternatives considered:

- **Rollback:** Not applicable because implementation has not begun.
- **MVP Review:** Not needed because the MVP remains achievable and FR coverage is complete.

## 4. Detailed Change Proposals

### 4.1 Epics.md - FR Coverage Map

#### Change: Move text baseline coverage earlier

**Current content:**

```md
FR30: Epic 6 - Text input interaction.
FR33: Epic 6 - Continue if voice input unavailable.
FR34: Epic 6 - Continue if voice output unavailable.
```

**Proposed content:**

```md
FR30: Epic 1 / Epic 6 - Epic 1 provides the reliable text interaction baseline; Epic 6 extends interaction with voice features.
FR33: Epic 1 / Epic 6 - Epic 1 ensures text input works when voice input is unavailable; Epic 6 adds STT-specific degraded behavior.
FR34: Epic 1 / Epic 6 - Epic 1 ensures responses are displayed as text when voice output is unavailable; Epic 6 adds TTS-specific degraded behavior.
```

**Rationale:** Earlier epics depend on text/manual fallback, so the baseline must be represented before Epic 6.

### 4.2 Epics.md - Epic List

#### Change: Update Epic 1 FR coverage

**Current content:**

```md
**FRs covered:** FR1, FR4, FR5, FR39, FR40, FR43, FR44, FR45, FR46, FR48
```

**Proposed content:**

```md
**FRs covered:** FR1, FR4, FR5, FR30, FR33, FR34, FR39, FR40, FR43, FR44, FR45, FR46, FR48
```

**Rationale:** Epic 1 should explicitly own the reliable text interaction baseline and manual/text-only fallback foundation.

#### Change: Update Epic 6 scope

**Current content:**

```md
### Epic 6: Voice Interaction and Graceful Multimodal Fallbacks
Ryan can use text reliably, receive spoken responses, optionally use spoken input, and keep working when STT/TTS is unavailable.

**FRs covered:** FR30, FR31, FR32, FR33, FR34
```

**Proposed content:**

```md
### Epic 6: Voice Interaction and Graceful Voice Fallbacks
Ryan can receive spoken responses, optionally use spoken input, and keep working when STT/TTS is unavailable because the text interaction baseline already exists.

**FRs covered:** FR31, FR32, plus STT/TTS-specific extensions of FR33 and FR34
```

**Rationale:** Epic 6 should focus on voice extensions, not foundational text interaction.

### 4.3 Epics.md - Story 1.2

#### Change: Clarify storage scaffolding only

**Current acceptance criterion:**

```md
**Given** Ryan inspects runtime storage
**When** state, memory, and log files are present
**Then** `current_state.json`, `integration_health.json`, `memory.md`, `session_summary.md`, `banana_debt.json`, `app.log`, and `events.jsonl` exist or are created on first run.
```

**Proposed acceptance criterion:**

```md
**Given** Ryan inspects runtime storage
**When** foundation-level state, memory, and log files are present
**Then** `current_state.json`, `integration_health.json`, `app.log`, and `events.jsonl` exist or are created on first run
**And** `memory.md`, `session_summary.md`, and `banana_debt.json` may exist only as empty inspectable scaffolding until Epic 4 and Epic 5 implement memory/accountability behavior.
```

**Rationale:** Keeps local file visibility while avoiding premature implementation of memory/accountability behavior.

### 4.4 Epics.md - New Story 1.7

#### Change: Add text interaction baseline to Epic 1

**New story:**

```md
### Story 1.7: Provide Reliable Text Interaction Baseline

As Ryan,
I want to interact with Bananalyzer through text,
So that the assistant remains usable before voice features are stable and when automation components are degraded.

**Acceptance Criteria:**

**Given** Bananalyzer is running locally
**When** Ryan enters a text question or command
**Then** the assistant can accept and display text interaction through the local CLI/runtime path.

**Given** state-specific prompt/model routing is not fully implemented yet
**When** Ryan uses text interaction during the foundation phase
**Then** Bananalyzer uses the current safe placeholder or available routing path without requiring STT, TTS, Screenpipe, or MCP.

**Given** voice integrations are unavailable
**When** Ryan uses text input
**Then** text interaction continues to work.

**Given** a response is generated or a placeholder response is produced
**When** TTS is disabled or unavailable
**Then** the response is still displayed as text.

**Given** Ryan views status or diagnostics
**When** text interaction is available
**Then** the system reports text interaction as the baseline supported interaction mode.
```

**Rationale:** Resolves the critical forward dependency while keeping the story correctly scoped for Epic 1.

### 4.5 Epics.md - Story 2.5

#### Change: Add dependency note only

**Current acceptance criterion:**

```md
**Given** foreground detection or context signals are unavailable
**When** state evaluation cannot confidently classify activity
**Then** Bananalyzer enters or remains in `fallback` mode
**And** continues to support safe text-based interaction.
```

**Proposed content:**

```md
**Given** foreground detection or context signals are unavailable
**When** state evaluation cannot confidently classify activity
**Then** Bananalyzer enters or remains in `fallback` mode
**And** continues to support safe text-based interaction through the Epic 1 text interaction baseline.
```

**Rationale:** Makes the dependency explicit and removes ambiguity.

### 4.6 Epics.md - Story 3.6

#### Change: Add dependency note only

**Current acceptance criterion:**

```md
**Given** MCP or active file context is unavailable
**When** Ryan asks a coding question
**Then** Bananalyzer continues with general text interaction
**And** clearly states that active code context is unavailable.
```

**Proposed content:**

```md
**Given** MCP or active file context is unavailable
**When** Ryan asks a coding question
**Then** Bananalyzer continues with general text interaction through the Epic 1 text interaction baseline
**And** clearly states that active code context is unavailable.
```

**Rationale:** Makes degraded coding support depend on an already-delivered baseline.

### 4.7 Epics.md - Remove or Replace Story 6.1

#### Change: Remove Story 6.1 from Epic 6 and renumber remaining stories

**Current story:**

```md
### Story 6.1: Provide Reliable Text Interaction Baseline
...
```

**Proposed action:**

- Remove Story 6.1 from Epic 6 after adding Story 1.7.
- Renumber:
  - Story 6.2 → Story 6.1
  - Story 6.3 → Story 6.2
  - Story 6.4 → Story 6.3
  - Story 6.5 → Story 6.4
  - Story 6.6 → Story 6.5

**Optional replacement note:**

```md
Text interaction baseline is delivered in Epic 1. Epic 6 extends the interaction model with TTS, optional STT, voice configuration, and STT/TTS degraded-mode behavior.
```

**Rationale:** Prevents duplication and keeps Epic 6 voice-focused.

### 4.8 Add Lightweight UX Notes

#### Change: Add story-level UX notes before implementation of user-facing stories

Recommended insertion under `### UX Design Requirements` or as a new `## Lightweight UX Notes` section in `epics.md`:

```md
## Lightweight UX Notes for MVP User-Facing Surfaces

No dedicated UX artifact exists for MVP. The following story-level UX guidance must be preserved during implementation:

- `status` output should show: current state, current model/profile, last transition, integration health, recent errors, memory update status, persistence categories, and degraded-mode explanation.
- `dashboard` should mirror status categories in sections: State, Model, Integrations, Recent Events, Memory, Accountability, Errors.
- `config` output should prioritize discoverability: show config file paths, key editable settings, and safe defaults.
- Text interaction should always display responses as text, even when TTS is enabled.
- Voice interaction should be additive; STT/TTS failure must point Ryan back to text interaction.
- Intervention intensity should affect wording, frequency, and delivery behavior without bypassing tone boundaries.
- Mean banana tone may be direct or sarcastic, but not abusive, discriminatory, protected-class-targeted, or self-harm-reinforcing.
```

**Rationale:** Mitigates missing UX artifact risk without requiring a full UX design phase.

### 4.9 Optional CI/CD Scope Decision

#### Change: Document CI as out of scope or add local quality criterion

Recommended minimal edit to Story 1.1:

```md
**Given** this is a personal local MVP
**When** quality automation is configured
**Then** local `uv run pytest` and `uv run ruff check .` commands are available
**And** remote CI/CD is documented as optional and out of scope unless Ryan chooses to add it later.
```

**Rationale:** Addresses the readiness report’s minor CI concern without adding unnecessary process overhead.

### 4.10 PRD Clarification

#### Change: Clarify text baseline in MVP scope

**Current MVP scope excerpt:**

```md
- Whisper STT can capture user questions, or text input can be used if STT is unstable.
```

**Proposed content:**

```md
- Text input is the reliable baseline interaction path for MVP.
- Whisper STT can optionally capture spoken questions once text interaction is working.
```

**Rationale:** Aligns PRD with the corrected epic sequencing.

### 4.11 Architecture Clarification

#### Change: Update implementation sequence

**Current relevant implementation sequence:**

```md
1. Initialize Python project with `uv`.
2. Create config, logging, and local data directories.
3. Implement typed config loading.
4. Implement state machine and foreground activity monitor.
```

**Proposed content:**

```md
1. Initialize Python project with `uv`.
2. Create config, logging, and local data directories.
3. Implement typed config loading.
4. Implement reliable text interaction baseline for manual/fallback operation.
5. Implement state machine and foreground activity monitor.
```

**Rationale:** Ensures foundational interaction exists before degraded/fallback behaviors rely on it.

## 5. Checklist Results

### Section 1: Understand the Trigger and Context

- [x] 1.1 Triggering story identified: Story 6.1 placement exposed forward dependencies in Stories 2.5 and 3.6.
- [x] 1.2 Core problem defined: sequencing/backlog dependency issue, not technical limitation or strategic pivot.
- [x] 1.3 Evidence gathered from readiness report.

### Section 2: Epic Impact Assessment

- [x] 2.1 Current impacted epic can still be completed with modifications.
- [x] 2.2 Required epic-level changes identified for Epic 1 and Epic 6.
- [x] 2.3 Remaining epics reviewed for dependency impact.
- [x] 2.4 No planned epics are obsolete; no new epic required.
- [x] 2.5 Epic priority/order remains valid after moving text baseline into Epic 1.

### Section 3: Artifact Conflict and Impact Analysis

- [x] 3.1 PRD conflict is minor; add clarification only.
- [x] 3.2 Architecture conflict is minor; update implementation sequence only.
- [x] 3.3 UX artifact missing; add lightweight story-level UX notes.
- [x] 3.4 Other artifacts: sprint status may need updates after approval if story IDs change.

### Section 4: Path Forward Evaluation

- [x] 4.1 Direct Adjustment is viable. Effort Low/Medium, Risk Low.
- [N/A] 4.2 Rollback is not applicable because implementation has not started.
- [N/A] 4.3 MVP Review is not needed because MVP remains achievable.
- [x] 4.4 Recommended path: Direct Adjustment.

### Section 5: Sprint Change Proposal Components

- [x] 5.1 Issue summary created.
- [x] 5.2 Epic impact and artifact adjustments documented.
- [x] 5.3 Recommended path provided with rationale.
- [x] 5.4 PRD MVP impact and high-level action plan defined.
- [x] 5.5 Agent handoff plan established.

### Section 6: Final Review and Handoff

- [x] 6.1 Checklist completion reviewed.
- [x] 6.2 Proposal prepared for user review.
- [!] 6.3 User approval pending.
- [!] 6.4 `sprint-status.yaml` update pending approval and actual epic edits.
- [!] 6.5 Handoff confirmation pending approval.

## 6. Implementation Handoff

### Change Scope Classification

**Moderate**

This is a backlog/planning correction that affects multiple stories and artifact sections but does not require product strategy changes or architectural redesign.

### Recommended Routing

- Product Owner / planning agent: apply backlog/story edits to `epics.md`.
- Architect or planning maintainer: apply small architecture sequence clarification.
- PM or PRD maintainer: apply small PRD text-baseline clarification.
- Developer agent: begin implementation only after edited artifacts are approved and readiness is rechecked.

### Success Criteria

The proposal is successfully implemented when:

- Story 6.1 text baseline is moved or split into Epic 1 as Story 1.7.
- Epic 6 is voice-focused and no longer owns the foundational text baseline.
- Stories 2.5 and 3.6 depend only on already-delivered text baseline behavior.
- Story 1.2 clearly treats memory/accountability files as scaffolding unless Epic 4/Epic 5 implement behavior.
- Lightweight UX notes exist for status, dashboard, config, intervention, and text/voice fallback behavior.
- PRD and architecture contain small clarifications aligning with the corrected sequence.
- Implementation readiness can be re-run with no critical sequencing blocker.

## 7. Recommended Next Steps

1. Approve this Sprint Change Proposal.
2. Apply the proposed edits to `epics.md`, `prd.md`, and `architecture.md`.
3. Update any sprint tracking/story references if story numbering changes.
4. Re-run implementation readiness validation.
5. Start implementation with Epic 1 only after readiness is confirmed.

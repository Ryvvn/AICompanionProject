# Sprint Change Proposal — AICompanionProject

**Date:** 2026-05-18
**Author:** Ryan
**Change Scope:** Minor
**Trigger:** Ollama LLM integration stub needs real HTTP implementation; MCP adapter needs multi-IDE routing

---

## Section 1: Issue Summary

### Problem Statement 1: Ollama LLM Stub

All 6 Epics (39 Stories) are complete. Bananalyzer has working infrastructure: state detection, mode routing, memory management, voice adapters, code context ingestion, accountability tracking, and a Textual dashboard. However, the companion cannot actually "think" or "speak" — the Ollama adapter (`integrations/ollama.py`) was left as a stub returning `is_available() → False`, and `model_router.generate_response()` returns hardcoded placeholder text instead of real LLM inference.

Without real Ollama integration:
- Coding questions receive placeholder responses, not actual code analysis
- Rubber-duck clarifying questions are never generated
- Accountability interventions (doomscroll roasts, gaming nudges) produce no real text
- Companion conversations are static placeholders
- TTS speaks placeholder text rather than meaningful responses

### Problem Statement 2: MCP Single-Endpoint Limitation

The MCP adapter (`integrations/mcp.py`) has a real HTTP client and works correctly, but it connects to a single hardcoded endpoint (`http://127.0.0.1:8000/v1/context`) regardless of which IDE Ryan is using. Foreground detection already identifies `code.exe` (VS Code), `trae.exe` (Trae), `devenv.exe` (Visual Studio), and `cursor.exe` — but there's no routing logic to connect each IDE to its own MCP server port.

Without multi-IDE MCP routing:
- The banana can't see code context when switching between Trae, VS Code, and Visual Studio
- Each IDE may run its MCP bridge on a different port
- No fallback logic to try alternate endpoints when one IDE's MCP is unavailable

### Discovery

Discovered post-implementation: the Ollama adapter was intentionally deferred as a stub during Epic 2 development. The MCP adapter works but was designed for a single-server assumption. Both gaps were identified during the Correct Course review.

### Evidence

| File | Evidence |
|------|----------|
| `src/bananalyzer/integrations/ollama.py:L16` | `is_available()` returns `False` — hardcoded |
| `src/bananalyzer/integrations/ollama.py:L22` | `health_check()` error: `"Ollama integration not implemented yet"` |
| `src/bananalyzer/model_router.py:L100-L112` | `generate_response()` returns `"(Placeholder response) State='...', model='...'..."` |
| `src/bananalyzer/integrations/mcp.py:L33` | MCP adapter uses single `endpoint_url`, initialized once |
| `src/bananalyzer/foreground.py:L176-L183` | Foreground detection already maps `code.exe`, `trae.exe`, `devenv.exe`, `cursor.exe` → coding |
| `src/bananalyzer/mode_controller.py:L68` | `process_user_message` creates `MCPAdapter()` with no foreground-aware routing |

---

## Section 2: Impact Analysis

### Epic Impact

| Epic | Impact | Action |
|------|--------|--------|
| Epic 1: Local Companion Foundation | Low — foundation is solid | No changes |
| Epic 2: Mode Detection and Routing | Moderate — routing works, inference + MCP routing doesn't | No changes to Epic 2; routing logic is correct |
| Epic 3: Active Code Companion | High (functionally) — infrastructure complete, no real responses, single MCP endpoint | No changes; real inference + multi-IDE routing enables this epic's value |
| Epic 4: Local Memory | Low — memory works independently | No changes |
| Epic 5: Behavioral Accountability | Moderate — interventions have no real text | No changes; real inference enables interventions |
| Epic 6: Voice Interaction | Low — TTS/STT adapters work | No changes; real inference enables meaningful speech |
| **New Epic 7** | **Add Ollama + MCP multi-IDE integration** | **6 new stories** |

### Artifact Conflicts

| Artifact | Conflicts | Action Required |
|----------|:---:|------|
| PRD | None | No changes — PRD already assumes Ollama integration |
| Architecture | None | Optional: note Ollama API URL in config |
| UX | None | No dedicated UX document; interaction surfaces unchanged |
| Epics | New epic needed | Add Epic 7 with 6 stories |
| Sprint Status | Update needed | Add Epic 7 tracking entries (6 stories) |

### Technical Impact

- **Code changes:** `integrations/ollama.py` (major rewrite — real HTTP client), `integrations/mcp.py` (moderate update — multi-IDE endpoint routing), `model_router.py` (minor update to call real adapter), `mode_controller.py` (minor update — foreground-aware MCP endpoint selection), `config.py` (add `ollama.base_url`, timeout settings, `mcp_endpoints` per-IDE mapping)
- **No infrastructure changes:** local-only, no cloud, no new dependencies (`httpx` already installed)
- **No deployment impact:** remains `uv run` based
- **No test removals:** existing tests for routing, degradation, and health checks remain valid

---

## Section 3: Recommended Approach

### Selected: Option 1 — Direct Adjustment (New Epic 7)

Add a focused **Epic 7: Ollama + MCP Integration — Real LLM Inference and Multi-IDE Code Context** with 6 stories that (a) replace the Ollama stub adapter with real HTTP calls to Ollama's REST API, and (b) add foreground-aware MCP endpoint routing so the banana sees active code context from whichever IDE Ryan is using.

### Rationale

| Factor | Assessment |
|--------|------------|
| **Effort** | Low — all infrastructure (adapter boundary, config, routing, degradation, health checks) is already in place |
| **Risk** | Low — Ollama API is a well-documented REST endpoint; `httpx` is already a dependency |
| **Architecture impact** | None — the adapter pattern was designed for this exact change |
| **Story impact** | None — zero existing stories are modified |
| **Rollback needed** | None — nothing was done wrong, the stub was intentional deferral |

### Alternatives Considered

| Option | Verdict |
|--------|---------|
| **Option 2: Rollback** | Not viable — nothing to roll back; the stub was correct at the time |
| **Option 3: MVP Review** | Not applicable — original PRD already required Ollama integration as MVP must-have |

---

## Section 4: Detailed Change Proposals

### Proposal 1: Add Epic 7 to `epics.md`

**Artifact:** `_bmad-output/planning-artifacts/epics.md`
**Section:** Append new epic after Epic 6

**NEW content to append:**

```markdown
## Epic 7: Ollama Integration — Real LLM Inference

Ryan gets real LLM-powered responses from Bananalyzer through the local Ollama
inference server, replacing the placeholder text generation with actual AI
conversations across all persona states.

**FRs covered:** FR35, FR36, FR37, FR38, FR39, FR40 (completes previously
routed-but-not-wired requirements)

### Story 7.1: Implement Real Ollama HTTP Client

As Ryan,
I want Bananalyzer to make real HTTP calls to my local Ollama server,
So that the companion can generate actual AI responses instead of placeholder text.

**Acceptance Criteria:**

**Given** Ollama is running locally on its default port
**When** the Ollama adapter sends a generation request
**Then** it calls `POST http://localhost:11434/api/generate` with the selected
model name, system prompt, user prompt, and generation parameters.

**Given** the adapter receives a successful Ollama response
**When** the response is parsed
**Then** the adapter returns the generated text content.

**Given** `model_profiles.yaml` defines model-specific parameters
**When** a generation request is built
**Then** the adapter respects the per-state `temperature`, `num_ctx` (context
window), and any other configured Ollama options.

**Given** the Ollama server URL or timeout is configurable
**When** Ryan views or edits local config
**Then** `settings.yaml` includes `ollama.base_url` (default
`http://localhost:11434`) and `ollama.request_timeout_seconds` (default 120).

**Given** an Ollama model is not pulled locally
**When** the adapter receives a "model not found" error
**Then** the health check reports the specific model as unavailable and includes
actionable guidance (e.g., run `ollama pull <model>`).

### Story 7.2: Wire Model Router to Real Inference

As Ryan,
I want `model_router.generate_response()` to return real LLM output,
So that coding help, rubber-duck questions, accountability interventions, and
companion conversations are actually intelligent.

**Acceptance Criteria:**

**Given** `model_router.generate_response()` is called with user input
**When** the model router processes the request
**Then** it sends the composed system prompt + user message through the Ollama
adapter to generate a real response.

**Given** the Ollama adapter returns a successful response
**When** `generate_response()` completes
**Then** the response text is returned directly (after basic sanitization like
stripping trailing whitespace and removing leading assistant-prefix artifacts).

**Given** `generate_response()` receives an empty or whitespace-only user input
**When** the router processes the request
**Then** it returns a safe fallback message without calling Ollama.

**Given** the current state has been selected correctly
**When** a response is generated
**Then** the response uses the state-specific system prompt and model profile
already selected by `select_model_profile()` and `build_system_prompt()`.

**Given** Ollama returns a response that includes added prefixes or formatting
artifacts
**When** the response is returned
**Then** common Ollama response artifacts (e.g., repeated system prompt
fragments, trailing newlines) are cleaned up before display.

### Story 7.3: Handle Ollama Errors and Timeouts Gracefully

As Ryan,
I want Bananalyzer to handle Ollama connection issues without crashing,
So that one failed generation doesn't break the whole companion.

**Acceptance Criteria:**

**Given** Ollama is unreachable (connection refused, timeout)
**When** a generation request is attempted
**Then** the adapter returns a degraded result instead of raising an unhandled
exception.

**Given** a generation request times out
**When** the configured timeout is exceeded
**Then** the adapter cancels the request and reports the timeout in diagnostics.

**Given** Ollama returns an HTTP error (4xx, 5xx)
**When** the adapter handles the response
**Then** it logs the status code and error body
**And** emits an `integration.failed` event.

**Given** the Ollama adapter encounters any error
**When** `model_router.generate_response()` receives the degraded result
**Then** it returns a clear user-facing message about generation unavailability
**And** does not crash the runtime loop.

**Given** Ollama becomes available again after a failure
**When** the next generation request is made
**Then** the health check transitions from `unavailable`/`degraded` back to
`available`.

### Story 7.4: Verify End-to-End Responses Per Persona State

As Ryan,
I want to confirm that each persona state produces appropriate real responses,
So that the companion feels distinct and useful across coding, gaming,
doomscrolling, companion, and fallback modes.

**Acceptance Criteria:**

**Given** Bananalyzer is in `coding` state with active code context
**When** Ryan asks a coding question
**Then** the real Ollama response uses the coding persona prompt and responds
with technical, rubber-duck-style support.

**Given** Bananalyzer is in `companion` state
**When** Ryan sends a conversational message
**Then** the real Ollama response uses the companion persona prompt with a
lighter, conversational tone.

**Given** Bananalyzer is in `doomscrolling` state
**When** an accountability intervention is triggered
**Then** the real Ollama response uses the doomscrolling persona prompt with
motivational-but-sharp tone.

**Given** Bananalyzer is in `gaming` state
**When** an accountability nudge is triggered
**Then** the real Ollama response uses the gaming persona prompt and ties the
nudge back to unfinished goals from memory.

**Given** Bananalyzer is in `fallback` state
**When** Ryan sends any message
**Then** the real Ollama response uses the fallback prompt and remains helpful
and safe.

**Given** any persona state produces a response
**When** the response is returned
**Then** it respects the motivational tone boundaries (sarcastic/direct OK,
abusive/discriminatory not OK) defined in the persona prompt files.

### Story 7.5: Route MCP Context by Foreground IDE

As Ryan,
I want Bananalyzer to connect to the right IDE's MCP server based on what I'm using,
So that the banana sees my active code whether I'm in Trae, VS Code, or Visual Studio.

**Acceptance Criteria:**

**Given** Ryan has Trae in the foreground
**When** Bananalyzer requests active code context
**Then** the MCP adapter connects to the configured Trae MCP endpoint.

**Given** Ryan has VS Code (`code.exe`) in the foreground
**When** Bananalyzer requests active code context
**Then** the MCP adapter connects to the configured VS Code MCP endpoint.

**Given** Ryan has Visual Studio (`devenv.exe`) in the foreground
**When** Bananalyzer requests active code context
**Then** the MCP adapter connects to the configured Visual Studio MCP endpoint.

**Given** Ryan has Cursor (`cursor.exe`) in the foreground
**When** Bananalyzer requests active code context
**Then** the MCP adapter connects to the configured Cursor MCP endpoint.

**Given** no supported IDE is in the foreground or foreground info is unavailable
**When** Bananalyzer requests active code context
**Then** the adapter tries each configured endpoint in priority order and returns the first successful result, or reports context unavailable.

**Given** IDE-to-endpoint mappings are configurable
**When** Ryan edits local config
**Then** `settings.yaml` includes `mcp_endpoints` mapping IDE process names
(e.g., `code.exe`, `trae.exe`, `devenv.exe`, `cursor.exe`) to their MCP server
URLs with sensible localhost defaults.

**Given** the MCP adapter uses the foreground process name
**When** selecting an endpoint
**Then** it falls back to the `unknown` or `default` endpoint entry if the
specific IDE process name is not configured.

### Story 7.6: Verify Code Context Across IDEs

As Ryan,
I want to confirm Bananalyzer correctly reads my active code regardless of which IDE I switch to,
So that the rubber-duck companion follows me across tools.

**Acceptance Criteria:**

**Given** Ryan switches from Trae to VS Code mid-session
**When** the next coding interaction occurs
**Then** Bananalyzer detects the foreground change and requests context from
the VS Code MCP endpoint on the next query.

**Given** an IDE's MCP server is not running
**When** Bananalyzer requests context from that IDE
**Then** the adapter reports that endpoint as unavailable
**And** falls back to trying other configured endpoints or reports no context.

**Given** Ryan switches from an IDE to a non-IDE app
**When** Bananalyzer evaluates coding context
**Then** context gracefully becomes unavailable without errors
**And** the companion continues in the appropriate non-coding persona.

**Given** each IDE endpoint returns context in a slightly different JSON shape
**When** the context builder processes the response
**Then** `context_builder.py` normalizes `file`, `path`, `language`, `lang`,
`selection`, `visible`, and `content` fields into a consistent format.

**Given** MCP multi-IDE routing is active
**When** Ryan runs `bananalyzer diagnose`
**Then** each configured MCP endpoint's health is reported individually.
```

### Proposal 2: Add Epic 7 to `sprint-status.yaml`

**Artifact:** `_bmad-output/implementation-artifacts/sprint-status.yaml`
**Section:** Append after line `epic-6-retrospective: done`

**NEW content to append:**

```yaml
  epic-7: backlog
  7-1-implement-real-ollama-http-client: backlog
  7-2-wire-model-router-to-real-inference: backlog
  7-3-handle-ollama-errors-and-timeouts-gracefully: backlog
  7-4-verify-end-to-end-responses-per-persona-state: backlog
  7-5-route-mcp-context-by-foreground-ide: backlog
  7-6-verify-code-context-across-ides: backlog
```

---

## Section 5: Implementation Handoff

### Change Scope Classification: **Minor**

This change is well-contained:
- 6 new stories in one new epic
- No existing stories modified
- No existing code deleted or refactored
- All infrastructure (adapter boundary, routing, degradation, health checks) already in place
- Well-understood REST API integrations (Ollama + MCP)

### Recommended Route: Developer Agent

The **Developer agent** (`bmad-agent-dev` / `bmad-quick-dev`) can implement all 6 stories directly.

### Story Implementation Order

| Order | Story | Dependencies |
|-------|-------|-------------|
| 1 | 7.1 — Implement Real Ollama HTTP Client | None (rewrites existing stub) |
| 2 | 7.2 — Wire Model Router to Real Inference | Story 7.1 |
| 3 | 7.3 — Handle Ollama Errors and Timeouts | Story 7.1 |
| 4 | 7.5 — Route MCP Context by Foreground IDE | None (modifies existing MCP adapter) |
| 5 | 7.4 — Verify End-to-End Per Persona State | Stories 7.1-7.3 |
| 6 | 7.6 — Verify Code Context Across IDEs | Stories 7.5 |

### Success Criteria for Implementation

- `ollama.py` `is_available()` returns `True` when Ollama server is reachable
- `ollama.py` `health_check()` reports accurate availability
- `model_router.generate_response()` returns real LLM-generated text (not placeholder)
- `mcp.py` routes context requests to the correct IDE's MCP endpoint based on foreground process
- All 5 persona states (coding, gaming, doomscrolling, companion, fallback) produce distinct, appropriate responses
- Switching between Trae, VS Code, and Visual Studio mid-session correctly changes the MCP endpoint
- Ollama and MCP unavailability degrades gracefully (no crash, clear user message)
- All existing tests pass (`uv run pytest`)
- Ruff linting passes (`uv run ruff check .`)

---

## Summary

| Item | Value |
|------|-------|
| **Issue** | Ollama adapter is a stub; MCP adapter lacks multi-IDE routing |
| **Change scope** | Minor |
| **New epic** | Epic 7 — Ollama + MCP Integration (6 stories) |
| **Existing stories modified** | 0 |
| **PRD changes** | None |
| **Architecture changes** | None |
| **Route to** | Developer agent |

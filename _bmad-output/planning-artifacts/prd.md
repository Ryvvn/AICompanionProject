---
stepsCompleted:
  - step-01-init
  - step-02-discovery
  - step-02b-vision
  - step-02c-executive-summary
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-06-innovation
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
  - step-12-complete
inputDocuments:
  - D:/AICompanionProject/PROJECT_BRIEF.md
workflowType: 'prd'
documentCounts:
  briefs: 1
  research: 0
  brainstorming: 0
  projectDocs: 0
classification:
  projectType: desktop_app
  domain: general productivity + developer tooling / personal AI companion
  complexity: medium
  projectContext: greenfield
releaseMode: phased
---

# Product Requirements Document - AICompanionProject

**Author:** Ryan
**Date:** 2026-04-25

## Executive Summary

Bananalyzer is a local-first desktop AI companion for Ryan that supports coding progress and behavior change during the transition into technical development. It monitors active development context through VS Code/MCP text access, observes environmental context through Screenpipe, and uses local LLM, STT, TTS, and memory components to provide real-time coaching, accountability, and codebase understanding.

The product helps Ryan stay productive, understand his code, ask better technical questions, and recover from distraction loops such as doomscrolling or avoidant gaming. It is optimized for a single-user RTX 3070 workstation with strict VRAM constraints and must preserve system performance for Unity, VS Code, and games.

The initial product is personal-use first. Its architecture should support future evolution into a configurable AI companion for technical learners.

### What Makes This Special

Bananalyzer is not a generic chatbot or passive productivity timer. It combines direct code context, screen/environment awareness, behavioral state detection, voice interaction, long-term memory, and an adaptive companion persona. The assistant shifts between rubber-duck coding support, lightweight companion mode, gaming accountability, and doomscroll interruption based on what Ryan is doing.

The “arrogant banana” persona is the initial companion identity, but the personality layer must remain evolvable. Future versions may adapt through memory, RAG, or fine-tuning/LoRA-style personalization so the agent feels less like a static prompt and more like a friend that learns Ryan’s patterns over time.

The core insight: effective AI productivity support requires both task context and avoidance context. The assistant needs to understand the code Ryan is working on and the distractions pulling him away from it.

## Project Classification

- **Project Type:** Desktop local AI agent
- **Domain:** General productivity, developer tooling, and personal AI companion
- **Complexity:** Medium
- **Project Context:** Greenfield
- **Primary User:** Ryan
- **Primary Value:** Combined coding support and behavior-change accountability
- **Key Technical Constraints:** Local execution, RTX 3070 8GB VRAM, strict AI VRAM budget, CPU-based STT/TTS, state-aware model usage

## Success Criteria

### User Success

Bananalyzer succeeds if Ryan uses it as a daily coding/accountability companion that improves technical focus and code understanding without making the PC feel slower. Ryan should feel that the assistant understands both the current coding task and the surrounding behavior pattern: working, gaming, doomscrolling, or companion mode.

Success moments:
- Ryan asks questions about the active codebase and receives useful, context-aware explanations.
- Ryan catches logic issues faster through rubber-duck questioning.
- Ryan is interrupted during doomscrolling early enough to return to coding.
- Ryan feels the banana persona is personal, evolving, and motivating rather than generic.
- The assistant supports behavior change without becoming annoying enough to disable.

### Business Success

For MVP, business success means the product is valuable to Ryan as a personal tool. It does not require multi-user onboarding, monetization, or public distribution.

Success means:
- Ryan uses the assistant repeatedly during coding sessions.
- The system becomes part of the normal development workflow.
- The project proves the product concept enough to justify future expansion into a configurable AI companion for technical learners.
- The personality/memory system creates continuity over time.

### Technical Success

The system succeeds technically if it runs locally on the RTX 3070 workstation while preserving performance for Unity, VS Code, and games.

Technical success criteria:
- Local LLM inference works through Ollama with state-specific model selection.
- AI VRAM usage stays within the target budget during normal operation.
- STT and TTS run CPU-side without consuming GPU memory.
- VS Code/MCP code context can be passed to the agent on demand.
- Screenpipe context can be queried periodically without noticeable system lag.
- The state machine reliably switches between coding, gaming, doomscrolling, and companion modes.
- Memory updates persist useful summaries without bloating context unnecessarily.
- Doomscroll detection produces useful interventions with tolerable false positives.

### Measurable Outcomes

Initial measurable outcomes:
- Detect active work state within one polling interval.
- Query Screenpipe every 60 seconds without noticeable PC slowdown.
- Update session memory every 15 minutes.
- Maintain usable responsiveness for local chat interactions.
- Keep Unity/VS Code workflows stable while the agent is running.
- Correctly route at least four states: Coding, Gaming, Doomscrolling, Duo/Companion.
- Demonstrate one full end-to-end loop: context detection → prompt selection → LLM response → TTS output.
- Demonstrate codebase Q&A using active VS Code file context.

## Product Scope

### MVP - Minimum Viable Product

MVP must prove the core loop:
- Local Ollama model configured and callable.
- `mode_controller.py` detects foreground app state.
- Prompt routing works for Coding, Gaming, Doomscrolling, and Duo.
- Screenpipe watcher detects basic distraction signals.
- VS Code/MCP bridge provides active code context.
- Memory file stores goals, session summaries, recurring mistakes, and banana debt.
- Piper or Kokoro TTS speaks agent responses.
- Text input is the reliable baseline interaction path for MVP.
- Whisper STT can optionally capture spoken questions once text interaction is working.
- The assistant can answer questions about active code and challenge distraction behavior.

### Growth Features - Post-MVP

Growth features:
- Better doomscroll detection using scroll velocity, OCR patterns, URL categories, and session duration.
- Configurable personality profiles.
- RAG-based memory retrieval.
- More nuanced coaching modes.
- Unity console log ingestion.
- Better codebase-wide understanding beyond active file context.
- User-adjustable intervention intensity.
- Metrics dashboard for coding time, gaming time, doomscroll time, and banana debt.

### Vision - Future

Future vision:
- A companion that evolves like a friend through memory, retrieval, and possible LoRA/fine-tuning.
- Multiple personality layers beyond the arrogant banana.
- Personalized learning support for technical development.
- Long-term behavioral coaching based on patterns across weeks or months.
- A reusable framework for local AI companions that combine system context, coding context, voice, memory, and adaptive persona.

## User Journeys

### Journey 1: Ryan Codes With a Rubber-Duck Companion

Ryan opens VS Code and Unity to work on a C# script. He understands the broad goal but is unsure whether his implementation actually makes sense. Bananalyzer detects the coding state through the active foreground app and loads the coding persona. Through the MCP bridge, it reads the active file context without needing screenshot-based vision.

Ryan asks, “Why isn’t this working?” The assistant uses the active file context, asks clarifying questions, points out likely logic gaps, and helps Ryan reason through the code rather than simply dumping an answer. The key value moment happens when Ryan realizes the assistant understands the exact script he is looking at and can challenge his assumptions.

**Capabilities revealed:**
- Foreground app detection
- Coding-state prompt routing
- VS Code/MCP active file ingestion
- Local LLM code explanation
- Rubber-duck questioning style
- Optional STT input and TTS response

### Journey 2: Ryan Starts Doomscrolling and Gets Interrupted

Ryan intends to code but drifts into short-form content or endless browsing. Screenpipe captures app/window context, OCR text, active browser patterns, and repeated distraction signals. After the doomscroll threshold is reached, Bananalyzer switches into doomscroll mode.

The assistant references the current banana debt and interrupts with a sharper personality. The value moment is not the roast itself; it is the interruption arriving early enough to break the loop and redirect Ryan back to his development goal. If the intervention is too frequent or wrong, Ryan may disable it, so the system needs sensible thresholds and adjustable intensity.

**Capabilities revealed:**
- Screenpipe polling
- Doomscroll signal detection
- Banana debt tracking
- State override from environmental context
- TTS interruption
- False-positive tolerance and configurable intensity

### Journey 3: Ryan Games While Carrying “Unity Debt”

Ryan launches PUBG or Steam after leaving development tasks unfinished. Bananalyzer detects the gaming state and switches into backseat-driver mode. It does not block gaming, but it tracks time and reminds Ryan of pending coding goals.

The value moment happens when the assistant turns gaming from unconscious avoidance into a visible tradeoff. It can roast missed shots, but the useful part is tying gaming time back to unfinished technical goals without becoming so annoying that Ryan quits the system.

**Capabilities revealed:**
- Gaming foreground detection
- Accountability timer
- Pending goal/memory lookup
- Gaming persona routing
- Non-blocking behavioral nudges

### Journey 4: Ryan Uses Companion Mode Between Work Sessions

Ryan is idle, in Discord, or not actively coding. Bananalyzer switches to Duo/Companion mode using the lightweight model profile. The assistant becomes more conversational and motivational instead of aggressively task-focused.

The value moment is continuity: Ryan feels like the companion remembers his goals, current learning journey, and recent patterns. Over time, personality should evolve through memory, RAG, or future fine-tuning so it feels less like a static chatbot and more like a personalized friend.

**Capabilities revealed:**
- Duo/companion state detection
- Lightweight model routing
- Long-term memory retrieval
- Personality profile system
- Low-VRAM operation

### Journey 5: Ryan Troubleshoots the Assistant Itself

Ryan notices the assistant is lagging the PC, missing state changes, or making incorrect doomscroll calls. He needs to inspect what the system thinks is happening: current mode, model in use, last Screenpipe query, memory update status, and recent detections.

The value moment is operational trust. Ryan can see why Bananalyzer acted, tune thresholds, and recover without editing code blindly.

**Capabilities revealed:**
- Local status/debug view or logs
- State transition logging
- Screenpipe query diagnostics
- VRAM/performance visibility
- Configurable thresholds
- Safe fallback to text-only operation

### Journey Requirements Summary

The journeys reveal these capability areas:
- **Context Detection:** foreground process polling, Screenpipe environmental signals, active coding context.
- **State Machine:** coding, gaming, doomscrolling, companion, and fallback states.
- **Prompt and Model Routing:** state-specific prompts, temperatures, and model selection.
- **Code Understanding:** VS Code/MCP bridge for active file context and code Q&A.
- **Behavioral Accountability:** banana debt, distraction timers, intervention thresholds.
- **Voice Loop:** STT input and TTS output, with text fallback.
- **Memory:** goals, session summaries, recurring mistakes, coding progress, wasted-time log.
- **Personalization:** evolvable persona layer through memory/RAG and future tuning.
- **Operations:** logs, status visibility, threshold configuration, troubleshooting paths.

## Domain-Specific Requirements

### Compliance & Regulatory

- MVP is personal-use and local-first; no external data sharing is required.
- Captured screen/OCR/audio/context data must remain on the local machine unless Ryan explicitly enables export or sync later.
- If future versions support other users, the product must add explicit consent, privacy controls, retention settings, and data export/delete flows.
- The assistant must avoid unsafe or harmful language even when using the “mean banana” persona. Sarcasm and discipline are allowed; abuse, protected-class insults, or self-harm reinforcement are not.

### Technical Constraints

- The system must preserve workstation usability for Unity, VS Code, and games.
- AI GPU usage must respect the RTX 3070 8GB VRAM constraint and the target AI VRAM budget.
- Model residency should be state-aware rather than always keeping the largest model loaded.
- STT and TTS should run CPU-side to avoid additional GPU pressure.
- Screenpipe polling must avoid noticeable system lag.
- Doomscroll detection should use thresholds that reduce false positives.
- The system must support text-only fallback if STT, TTS, Screenpipe, or MCP integration fails.

### Integration Requirements

- Ollama provides local LLM inference and state-specific model routing.
- Screenpipe provides OCR, app/window/browser context, and distraction signals.
- VS Code/Kilo MCP bridge provides active code context.
- Whisper.cpp provides STT.
- Piper or Kokoro provides TTS.
- Unity integration may export console logs or debugging context post-MVP.
- Memory storage must support session summaries, goals, recurring mistakes, and banana debt.

### Risk Mitigations

- **Privacy risk:** Keep captured context local and document what is stored.
- **Performance risk:** Use lightweight models, state-aware model loading, CPU-side audio, and configurable polling intervals.
- **False-positive intervention risk:** Provide adjustable doomscroll thresholds and intervention intensity.
- **Persona risk:** Define tone boundaries so “mean” remains motivational and not harmful.
- **Context bloat risk:** Summarize memory periodically instead of injecting unbounded logs.
- **Dependency risk:** Each external component should have a fallback or degraded mode.

## Innovation & Novel Patterns

### Detected Innovation Areas

Bananalyzer combines multiple patterns into one local companion loop:
- **Dual-context awareness:** The assistant sees both task context through VS Code/MCP and avoidance context through Screenpipe.
- **Behavior-aware AI state machine:** Persona, model, temperature, and intervention style change based on detected user behavior.
- **Local-first accountability companion:** Productivity coaching runs on Ryan’s machine without requiring cloud AI.
- **Evolving personality layer:** The banana persona starts as prompt-driven but can become more personalized over time through memory, RAG, and future tuning.
- **Code-support plus behavior-change fusion:** The assistant helps with technical understanding while challenging distraction patterns.

### Market Context & Competitive Landscape

Existing tools typically cover only part of this:
- Chatbots help with code but do not know what the user is actually doing.
- Productivity blockers track distraction but do not understand the user’s code or goals.
- Voice assistants can converse but lack codebase awareness and behavioral accountability.
- Local AI tools can run models privately but usually require manual prompting.

Bananalyzer’s differentiator is continuous context fusion: it knows when Ryan is coding, avoiding, gaming, or idle, and it changes behavior accordingly.

### Validation Approach

Validate the innovation through working loops:
- Validate code support by asking questions about an active VS Code file.
- Validate behavior detection by correctly switching states from Coding to Gaming to Doomscrolling to Duo.
- Validate intervention value by confirming doomscroll interruptions help Ryan return to coding.
- Validate local feasibility by measuring VRAM, CPU load, and perceived system responsiveness.
- Validate personality evolution by checking whether memory makes future responses feel more personal and useful.

### Risk Mitigation

- If full multimodal behavior is too heavy, start with foreground app detection before advanced Screenpipe heuristics.
- If doomscroll detection is noisy, require multiple signals before interrupting.
- If the primary model exceeds VRAM limits, use state-aware model loading and lightweight fallback models.
- If voice causes friction, keep text input/output as a reliable fallback.
- If the persona becomes irritating, add configurable intensity and profile controls.
- If memory becomes bloated, summarize and retrieve selectively instead of injecting everything.

## Desktop Local AI Agent Specific Requirements

### Project-Type Overview

Bananalyzer is a Windows-first desktop local AI agent that runs as a background companion process on Ryan’s development workstation. It integrates with local applications and services to observe coding context, environmental behavior, local model state, memory, and audio input/output.

The MVP is not a conventional GUI-first desktop app. It is a local orchestration system with optional CLI/log/status visibility. Product value comes from reliable background operation, low system overhead, state-aware behavior, and tight integration with Ryan’s development environment.

### Technical Architecture Considerations

The desktop agent must coordinate multiple local subsystems:
- **Foreground app monitor:** Detects whether Ryan is in VS Code, Unity, PUBG/Steam, browser, Discord, idle desktop, or another state.
- **State machine:** Converts environmental signals into product modes: Coding, Gaming, Doomscrolling, Duo/Companion, and fallback.
- **LLM router:** Sends requests to Ollama using state-specific model, prompt, temperature, and context.
- **Screenpipe watcher:** Queries OCR/app/browser context for doomscroll and distraction signals.
- **VS Code/MCP bridge:** Reads active code context for coding support.
- **Memory updater:** Persists goals, session summaries, banana debt, recurring mistakes, and useful long-term context.
- **Audio loop:** Uses CPU-based STT and TTS for voice interaction.
- **Debug/status surface:** Provides visibility into current state, model, recent detections, memory updates, and errors.

### Platform Support

MVP platform support is Windows-first.

Requirements:
- Support Windows 11.
- Assume local Python 3.10+ runtime.
- Integrate with Windows foreground-window APIs through Python libraries such as `psutil` and `win32gui`.
- Support local folder/file-based configuration.
- Do not require packaging, installer, tray app, or auto-update in MVP.
- Do not require macOS or Linux support in MVP.

### System Integration

The desktop agent must integrate with:
- Ollama for local LLM inference.
- Screenpipe for environmental context and OCR.
- VS Code/Kilo MCP for active code context.
- Whisper.cpp for local speech-to-text.
- Piper or Kokoro for local text-to-speech.
- Unity logs or exported console data post-MVP.
- Local `memory.md` or equivalent structured memory storage.

The architecture should isolate integrations so one failed component does not crash the full assistant. If Screenpipe, STT, TTS, or MCP is unavailable, the system should degrade to text-based interaction and foreground-app state detection.

### Offline Operation

Bananalyzer must be local-first and usable without cloud AI.

Requirements:
- Core MVP loop must run locally.
- No required external API calls for normal operation.
- Captured code, OCR, audio, and memory data remain on device.
- Future cloud sync or remote model support must be explicitly opt-in.

### Implementation Considerations

Implementation should prioritize a working orchestration loop before GUI polish.

MVP implementation priorities:
1. `mode_controller.py` for foreground state detection and orchestration.
2. Prompt files for each mode.
3. Ollama model routing and response generation.
4. Screenpipe watcher for basic distraction detection.
5. Memory file creation and periodic summary updates.
6. TTS output and optional STT input.
7. MCP active-file context ingestion.
8. Debug logging and status output.

Post-MVP desktop enhancements:
- Tray app or lightweight dashboard.
- Config UI for thresholds and personality intensity.
- Auto-start on boot.
- Update mechanism.
- Better diagnostics for model/VRAM/performance status.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Problem-solving MVP focused on proving the core companion loop.

The MVP should prove that Bananalyzer can detect Ryan’s current context, route to the right persona/model behavior, answer code questions from active VS Code context, and interrupt obvious distraction loops without making the workstation feel slow.

**Resource Requirements:** One technical builder with Python, local AI tooling, Windows desktop integration, and enough Unity/VS Code workflow knowledge to test real coding scenarios.

### MVP Feature Set - Phase 1

**Core User Journeys Supported:**
- Ryan codes with a rubber-duck companion.
- Ryan starts doomscrolling and gets interrupted.
- Ryan games while carrying Unity/coding debt.
- Ryan uses lightweight companion mode between work sessions.
- Ryan can troubleshoot basic assistant state through logs/status output.

**Must-Have Capabilities:**
- Windows foreground app detection.
- State machine for Coding, Gaming, Doomscrolling, Duo/Companion, and fallback.
- Ollama local model routing with state-specific prompt and temperature.
- Prompt files for each state.
- VS Code/Kilo MCP active-file context ingestion.
- Basic Screenpipe watcher for distraction signals.
- Local memory file for goals, session summaries, recurring mistakes, and banana debt.
- CPU-side TTS output.
- Text input fallback if STT is unstable.
- Debug/status logging for current state, recent transitions, model used, and integration errors.
- Local-first operation with no required cloud services.

### Post-MVP Features

**Phase 2 - Growth:**
- More accurate doomscroll detection using OCR patterns, URL/app categories, scroll behavior, and duration.
- Whisper STT as a reliable voice-input path.
- Unity console log ingestion.
- RAG-based memory retrieval.
- Configurable personality intensity.
- Codebase-wide context beyond active file.
- Lightweight dashboard or tray/status interface.
- Metrics for coding time, gaming time, doomscroll time, and banana debt.

**Phase 3 - Expansion:**
- Multiple personality profiles.
- Long-term adaptive companion behavior.
- Fine-tuning or LoRA-style personalization experiments.
- Reusable framework for other local AI companions.
- Optional cloud/sync features only if explicitly enabled.
- Multi-user technical learner version.

### Risk Mitigation Strategy

**Technical Risks:**
- VRAM budget may be too tight for large context windows. Mitigation: start with smaller `num_ctx`, lightweight models, and state-aware model residency.
- Screenpipe doomscroll detection may be noisy. Mitigation: require multiple signals before interrupting and expose threshold controls.
- Integrations may fail independently. Mitigation: isolate components and degrade to foreground detection + text interaction.
- Voice loop may add friction. Mitigation: keep text input/output available at all times.

**Market/Product Risks:**
- The persona may become annoying instead of motivating. Mitigation: configurable intensity and explicit tone boundaries.
- The assistant may feel generic if memory is weak. Mitigation: prioritize useful memory summaries early.
- The product may become too broad. Mitigation: MVP focuses on the core loop, not dashboards, installers, or multi-user features.

**Resource Risks:**
- Too many integrations at once can stall progress. Mitigation: build in this sequence:
  1. foreground state detection
  2. Ollama prompt routing
  3. memory file
  4. TTS
  5. VS Code/MCP context
  6. Screenpipe watcher
  7. STT
  8. Unity logs

## Functional Requirements

### Context Awareness

- FR1: Ryan can run Bananalyzer as a local desktop companion during normal workstation use.
- FR2: Bananalyzer can identify Ryan’s current foreground activity category.
- FR3: Bananalyzer can distinguish coding, gaming, doomscrolling, companion/idle, and fallback states.
- FR4: Bananalyzer can track state transitions during a session.
- FR5: Ryan can inspect the assistant’s current detected state.

### Coding Support

- FR6: Ryan can ask questions about the active code context.
- FR7: Bananalyzer can receive active VS Code file context for coding assistance.
- FR8: Bananalyzer can explain code in the active context.
- FR9: Bananalyzer can ask clarifying questions that help Ryan reason through implementation issues.
- FR10: Bananalyzer can identify likely logic problems or misunderstanding points in the active code context.
- FR11: Bananalyzer can adapt its response style for coding support.

### Behavioral Accountability

- FR12: Bananalyzer can detect distraction signals from the user’s environment.
- FR13: Bananalyzer can classify likely doomscrolling behavior.
- FR14: Bananalyzer can interrupt Ryan during likely doomscrolling events.
- FR15: Bananalyzer can track coding time, gaming time, doomscrolling time, and companion/idle time.
- FR16: Bananalyzer can calculate a banana debt metric from productive and avoidant activity.
- FR17: Bananalyzer can reference current goals or unfinished work during accountability interventions.
- FR18: Ryan can adjust intervention intensity or disable overly disruptive behavior.

### Companion Behavior

- FR19: Bananalyzer can operate in a lightweight companion mode when Ryan is not actively coding or being interrupted.
- FR20: Bananalyzer can use different personas for coding, gaming, doomscrolling, and companion states.
- FR21: Bananalyzer can vary tone and response behavior based on the current state.
- FR22: Bananalyzer can preserve an evolving companion identity across sessions.
- FR23: Ryan can change or extend the personality layer over time.

### Memory and Personalization

- FR24: Bananalyzer can store persistent session memory.
- FR25: Bananalyzer can save goals, recurring mistakes, coding progress, and behavior summaries.
- FR26: Bananalyzer can update memory periodically during active sessions.
- FR27: Bananalyzer can retrieve relevant memory when responding.
- FR28: Ryan can inspect or edit stored memory.
- FR29: Bananalyzer can avoid relying on unbounded raw history as its only memory mechanism.

### Voice and Interaction

- FR30: Ryan can interact with Bananalyzer through text input.
- FR31: Ryan can receive spoken responses from Bananalyzer.
- FR32: Ryan can optionally ask spoken questions.
- FR33: Bananalyzer can continue operating if voice input is unavailable.
- FR34: Bananalyzer can continue operating if voice output is unavailable.

### Model and Response Routing

- FR35: Bananalyzer can route requests to different local model profiles based on current state.
- FR36: Bananalyzer can apply state-specific prompt instructions.
- FR37: Bananalyzer can apply state-specific response parameters.
- FR38: Bananalyzer can choose a lightweight companion profile when low resource usage is preferred.
- FR39: Ryan can inspect which model/profile is currently being used.

### Local Operation and Privacy

- FR40: Bananalyzer can operate without required cloud services.
- FR41: Bananalyzer can keep captured code, OCR, audio-derived text, and memory data local by default.
- FR42: Ryan can control whether any future external sharing or sync is enabled.
- FR43: Bananalyzer can provide a clear record of what local context is being stored.

### Diagnostics and Recovery

- FR44: Ryan can view recent state transitions, detections, and integration errors.
- FR45: Bananalyzer can continue in degraded mode when an integration is unavailable.
- FR46: Bananalyzer can report missing or failed integrations.
- FR47: Ryan can tune detection thresholds or configuration values.
- FR48: Bananalyzer can fall back to manual/text-only operation when automation components fail.

## Non-Functional Requirements

### Performance

- NFR1: Bananalyzer must preserve normal workstation usability while Unity, VS Code, and games are running.
- NFR2: AI GPU memory usage should stay within the configured AI VRAM budget during normal MVP operation.
- NFR3: Screenpipe polling must not create noticeable input lag, frame drops, or foreground-app stutter.
- NFR4: Foreground activity state should be refreshed within the configured polling interval.
- NFR5: Local chat responses should feel interactive enough for coding support and companion use.
- NFR6: STT and TTS components should not consume GPU memory in MVP.
- NFR7: Memory updates should not interrupt active coding, gaming, or voice interaction.

### Privacy and Security

- NFR8: Captured code context, OCR text, audio-derived text, and memory data must remain local by default.
- NFR9: No external sharing or cloud sync may occur without explicit user configuration.
- NFR10: Stored memory must be inspectable and editable by Ryan.
- NFR11: The system must make clear which categories of local context may be stored.
- NFR12: Future multi-user or cloud-enabled versions must require explicit consent and data deletion controls.

### Reliability and Degraded Operation

- NFR13: Failure of one integration must not crash the full assistant.
- NFR14: If Screenpipe is unavailable, Bananalyzer must still support foreground-state detection and text interaction.
- NFR15: If MCP code context is unavailable, Bananalyzer must still support general text interaction.
- NFR16: If STT is unavailable, Ryan must still be able to use text input.
- NFR17: If TTS is unavailable, Bananalyzer must still produce text output.
- NFR18: State transitions and integration failures must be logged for troubleshooting.

### Integration Resilience

- NFR19: Each external dependency must have a detectable available/unavailable state.
- NFR20: Bananalyzer must report missing or failed integrations clearly enough for Ryan to troubleshoot.
- NFR21: Integration polling should use configurable intervals where applicable.
- NFR22: Bananalyzer must avoid unbounded context ingestion from Screenpipe, VS Code, logs, or memory.

### Usability and Control

- NFR23: Ryan must be able to reduce or disable disruptive interventions.
- NFR24: Ryan must be able to tune doomscroll detection sensitivity.
- NFR25: The assistant’s “mean banana” behavior must remain within motivational tone boundaries.
- NFR26: The system must provide enough status visibility for Ryan to understand why an intervention occurred.
- NFR27: MVP operation should not require a polished GUI, but it must provide usable logs or status output.

### Maintainability

- NFR28: Prompts should be editable independently from the core orchestration logic.
- NFR29: State definitions should be easy to modify or extend.
- NFR30: Model profiles should be configurable without rewriting the main control loop.
- NFR31: Memory storage should support later migration to RAG or structured retrieval.
- NFR32: Integrations should be isolated enough that Screenpipe, MCP, STT, TTS, or Unity support can be improved independently.

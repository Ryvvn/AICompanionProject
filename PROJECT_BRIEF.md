# Bananalyzer — AI Companion Project Brief

> **Status:** Architecture & Feasibility Phase
> **Target Hardware:** NVIDIA RTX 3070 (8GB VRAM)
> **Last Updated:** 2026-04-24

---

## Objective

A multimodal productivity agent that:
- Monitors VS Code via **direct text-peeking** (MCP Bridge)
- Tracks "Environmental Context" (gaming, doomscrolling) via **Screenpipe**
- Acts as a sentient, arrogant banana that disciplines the user into staying productive

**Handover Note:** Do not be afraid to be mean during doomscrolling sessions. The user is using this as a disciplinary tool to support their transition from educational management into technical development.

---

## 1. Hardware Constraints

- **GPU:** NVIDIA RTX 3070 (8GB VRAM)
- **Strict AI VRAM Limit:** 2.5GB — preserves headroom for Unity/PUBG stability
- **Primary model:** `gemma4:e2b-it` (~2.1GB INT4 quantized)
- **Duo mode model:** `qwen3.5:0.8` (lightweight chatty companion)
- Default behavior keeps the primary model warm; Duo mode can call its own lightweight model profile.

---

## 2. Models

| Mode/Use         | Model                | Notes                          |
|------------------|----------------------|--------------------------------|
| Primary runtime  | `gemma4:e2b-it`      | General multimodal agent       |
| Duo mode         | `qwen3.5:0.8`        | Low-VRAM chatty companion mode |

- Reasoning mode enabled — Banana "plans" its roasts and help strategies before responding
- 128k context window used for full **Session History** (no chunking needed per session)
- `OLLAMA_KEEP_ALIVE=-1` keeps the primary model warm in VRAM
- Duo mode should call `qwen3.5:0.8` for lightweight companion chat

### Ollama Setup
```sh
ollama pull gemma4:e2b-it
ollama pull qwen3.5:0.8

# Set env var to keep model warm forever
set OLLAMA_KEEP_ALIVE=-1   # Windows
export OLLAMA_KEEP_ALIVE=-1  # Linux/macOS
```

### Modelfiles
```
# Primary (bananalyzer)
FROM gemma4:e2b-it
PARAMETER temperature 0.7    # default; overridden per state (see below)
PARAMETER num_gpu 99         # zero CPU offloading
PARAMETER num_ctx 64000      # practical context per session

# Duo companion profile
FROM qwen3.5:0.8
PARAMETER temperature 0.8
PARAMETER num_gpu 99
PARAMETER num_ctx 16000
```

---

## 3. Dual-Input Nervous System

The agent uses two distinct sensory inputs to "see everything" without lagging the PC:

### A. The Scalpel — VS Code MCP Bridge (Kilo)
- **Role:** Direct text access to open C# scripts in VS Code
- **How:** Kilo / MCP server reads active file content and sends it to the agent
- **Why:** Lets the Banana understand complex logic **without using Vision VRAM**
- **Trigger:** New file opened, file saved, or user asks a question

### B. The Wide-Lens — Screenpipe
- **Role:** Background system monitoring — OCR text, app switches, active URLs
- **Queries:** Python pipe queries Screenpipe database every **60 seconds**
- **Doomscroll Detection:**
  - High scroll-velocity in `Chrome.exe` → flag as potential doomscroll
  - OCR density matches TikTok / YouTube Shorts patterns → flag "Doomscroll Event"
  - Flags sent to agent with timestamp and duration

---

## 4. Behavioral State Machine

Agent dynamically switches persona and temperature based on Screenpipe metadata:

| Detected State     | Persona               | Temperature | Goal                                                         |
|--------------------|-----------------------|-------------|--------------------------------------------------------------|
| Unity / VS Code    | Rubber Duck           | `0.7`       | Listen patiently; ask clarifying questions to expose logic flaws |
| PUBG / Gaming      | Backseat Driver       | `1.1`       | Roast missed shots; remind user of pending "Unity Debt"      |
| Doomscrolling      | Aggressive Banana     | `1.5`       | HIGH ALERT — interrupt with sarcasm; cite memory.md wasted time log |
| Duo / Companion    | Chatty Sidekick       | `0.8`       | Lightweight casual conversation and motivation with low VRAM pressure (`qwen3.5`) |

Temperature is passed dynamically per Ollama API call based on current state.

---

## 5. Memory & "Banana Debt"

### Session History
- Gemma 4's 128k context window holds full session history in-memory
- No chunking needed within a single session

### Long-Term Memory (`memory.md`)
- Updated every **15 minutes** automatically by `memory_updater.py`
- Injected as system context on agent startup
- Tracks: bugs fixed, goals, recurring mistakes, wasted time log

### The Banana Debt Metric
- Agent calculates ratio of **Unity/coding time vs. doomscroll/gaming time**
- Stored and referenced in `memory.md`
- Used to escalate shame during procrastination events

Example output:
> "You've spent 45 minutes looking at capybara videos and only 5 minutes on that PlayerController script. Your debt is high, and I am disappointed."

---

## 6. Audio Stack

| Component   | Purpose              | Engine         | VRAM |
|-------------|----------------------|----------------|------|
| Whisper     | Speech-to-text (STT) | whisper.cpp    | CPU  |
| Piper TTS   | Text-to-speech (TTS) | Piper (ONNX)   | CPU  |

Both CPU-based — persist across all modes, consume zero VRAM.

---

## 7. Component Stack Status

| Component               | Status        |
|-------------------------|--------------|
| Python 3.10+            | Installed     |
| Ollama                  | Installed     |
| Whisper (cpp)           | Installed     |
| Kokoro TTS              | Installed     |
| Piper TTS               | Installed     |
| gemma4:e2b-it           | To install    |
| qwen3.5:0.8               | To install    |
| Kilo / MCP Bridge       | To configure  |
| Modelfile (bananalyzer) | To write      |
| mode_controller.py      | To write      |
| screenpipe_watcher.py   | To write      |
| memory_updater.py       | To write      |
| unity_bridge/           | To write      |
| prompts/                | Written       |
| memory.md               | To create     |

---

## 8. Folder Structure

```
/AICompanionProject/
├── PROJECT_BRIEF.md
├── Modelfile                             (gemma4:e2b-it config)
├── mode_controller.py                    (main orchestrator + state machine)
├── screenpipe_watcher.py                 (queries Screenpipe every 60s)
├── memory_updater.py                     (writes session summary every 15 min)
├── memory.md                             (persistent context + banana debt log)
├── prompts/
│   ├── coding_prompt.txt                 (Rubber Duck — temp 0.7)
│   ├── gaming_prompt.txt                 (Backseat Driver — temp 1.1)
│   ├── doomscroll_prompt.txt             (Aggressive Banana — temp 1.5)
│   └── duo_prompt.txt                    (Chatty Sidekick — temp 0.8)
├── unity_bridge/
│   └── BananalizerBridge.cs              (Unity C# console log exporter)
├── whisper.cpp/
├── kokoro-tts-2.3.1/
└── piper/                                (primary TTS)
```

---

## 9. Main Loop Logic

```
On startup:
  Load memory.md → inject into system prompt
  Start Whisper STT listener
  Start Piper TTS engine
  ollama run bananalyzer (keep warm)

Every 3 seconds:
  check active foreground window (psutil + win32gui)

  → Unity.exe / Code.exe:
      state = CODING
      temperature = 0.7
      persona = coding_prompt.txt
      MCP Bridge: read active C# file → feed to agent
      watch unity_console.log for new errors

  → PUBG.exe / steam.exe:
      state = GAMING
      temperature = 1.1
      persona = gaming_prompt.txt
      accountability_timer = ON

  → Discord.exe / Chat apps / idle desktop:
      state = DUO
      model = qwen3.5
      temperature = 0.8
      persona = duo_prompt.txt
      tone = chatty companion

  → (no trigger change):
      pass

Every 60 seconds:
  query Screenpipe database
  if scroll_velocity > threshold OR OCR matches doomscroll patterns:
    state = DOOMSCROLLING
    temperature = 1.5
    persona = doomscroll_prompt.txt
    inject banana_debt from memory.md
    interrupt user with TTS roast

Every 15 minutes:
  summarize session (Unity time, gaming time, doomscroll time)
  update banana_debt ratio
  append to memory.md
```

---

## 10. Immediate Technical Objectives

1. `ollama pull gemma4:e2b-it`
2. `ollama pull qwen3.5`
3. Write `Modelfile` and create: `ollama create bananalyzer -f Modelfile`
4. Install and configure **Screenpipe**
5. Configure **Kilo MCP Bridge** for VS Code
6. Write `mode_controller.py` (state machine + process watcher)
7. Write `screenpipe_watcher.py` (doomscroll detection)
8. Write `memory_updater.py` (15-min debt tracker)
9. Write `BananalizerBridge.cs` (Unity console log export)
10. Write `doomscroll_prompt.txt` (Aggressive Banana persona)
11. Test full pipeline: STT → state detection → LLM → Piper TTS

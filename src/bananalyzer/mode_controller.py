from datetime import datetime
import logging
import re
import time as time_module
from pathlib import Path
from typing import Any
from rich.prompt import Prompt
from rich.console import Console
from rich.markdown import Markdown

from bananalyzer.constants import AppState
from bananalyzer.context.context_builder import build_bounded_coding_context, build_codebase_search_block
from bananalyzer.diagnostics import upsert_integration_health
from bananalyzer.foreground import get_foreground_window_info
from bananalyzer.integrations import MCPAdapter, ScreenpipeAdapter, TTSAdapter, STTAdapter
from bananalyzer.integrations.base import HealthCheckResult
from bananalyzer.model_router import generate_response
from bananalyzer.events import emit_event
from bananalyzer.state_machine import get_current_state
from bananalyzer.memory.store import MemoryStore
from bananalyzer.memory.summarizer import periodic_memory_update
from bananalyzer.memory.retrieval import get_memory_prompt_block
from bananalyzer.config import load_settings_safe
from bananalyzer.accountability.engine import AccountabilityEngine

logger = logging.getLogger(__name__)
console = Console()


_memory_store: MemoryStore | None = None
_accountability_engine: AccountabilityEngine | None = None


_MARKDOWN_TTS_PATTERNS = [
    (re.compile(r"```[\s\S]*?```"), ""),
    (re.compile(r"`([^`]+)`"), r"\1"),
    (re.compile(r"\*\*\*(.+?)\*\*\*"), r"\1"),
    (re.compile(r"\*\*(.+?)\*\*"), r"\1"),
    (re.compile(r"__([^_]+)__"), r"\1"),
    (re.compile(r"(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)"), r"\1"),
    (re.compile(r"(?<![_a-zA-Z0-9])_(?!_)([^_\n]+?)(?<!_)_(?![_a-zA-Z0-9])"), r"\1"),
    (re.compile(r"~~(.+?)~~"), r"\1"),
    (re.compile(r"\[([^\]]+)\]\([^)]+\)"), r"\1"),
    (re.compile(r"!\[.*?\]\([^)]+\)"), ""),
    (re.compile(r"^#{1,6}\s+", re.MULTILINE), ""),
    (re.compile(r"^>\s?", re.MULTILINE), ""),
    (re.compile(r"^[\-\*\+]\s+", re.MULTILINE), ""),
    (re.compile(r"\\\*"), "*"),
    (re.compile(r"\\_"), "_"),
    (re.compile(r"\|[^|]*\|"), ""),
    (re.compile(r"-{3,}"), ""),
]


def _strip_markdown_for_speech(text: str) -> str:
    result = text
    for pattern, replacement in _MARKDOWN_TTS_PATTERNS:
        result = pattern.sub(replacement, result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def _get_memory_store() -> MemoryStore:
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store


def _get_accountability_engine() -> AccountabilityEngine:
    global _accountability_engine
    if _accountability_engine is None:
        _accountability_engine = AccountabilityEngine(memory_store=_get_memory_store())
    return _accountability_engine


def _extract_import_names(file_path: str, language: str) -> list[str]:
    names: list[str] = []
    try:
        content = Path(file_path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return names

    if language == "python":
        import re
        names.extend(re.findall(r"from\s+(\S+)\s+import", content))
        names.extend(re.findall(r"import\s+(\S+)", content))
        names = [n.split(".")[0] for n in names if n and not n.startswith("_")]
    elif language in ("typescript", "typescriptreact", "javascript", "javascriptreact"):
        import re
        names.extend(re.findall(r"from\s+['\"]([^'\"]+)['\"]", content))
        names.extend(re.findall(r"require\(['\"]([^'\"]+)['\"]\)", content))
        names = [n.split("/")[-1] for n in names if n and not n.startswith(".")]

    return list(set(names))[:10]


def _extract_search_terms(user_input: str, bounded: dict[str, Any]) -> list[str]:
    terms: list[str] = []
    excerpt = bounded.get("excerpt", "")
    text = (user_input + " " + excerpt).lower()

    for pattern, _keyword in [
        (r"function\s+(\w+)", ""), (r"class\s+(\w+)", ""), (r"def\s+(\w+)", ""),
        (r"const\s+(\w+)", ""), (r"import\s+(\w+)", ""), (r"from\s+(\w+)", ""),
    ]:
        found = re.findall(pattern, text)
        terms.extend(found)

    words = re.findall(r"\b[a-zA-Z_]\w{3,}\b", user_input)
    common = {"what", "this", "that", "with", "from", "your", "have", "been", "does", "when", "where", "which", "there", "their", "about", "would", "could", "should"}
    for w in words:
        if w.lower() not in common and len(w) > 3:
            terms.append(w)

    return list(dict.fromkeys(terms))[:8]


def _build_codebase_context(
    adapter: MCPAdapter,
    mcp_context: dict[str, Any],
    user_input: str,
    bounded: dict[str, Any],
    process_name: str | None = None,
) -> str:
    from bananalyzer.context.context_builder import build_codebase_search_block

    data = mcp_context.get("data") or {} if mcp_context.get("ok") else {}
    file_path = data.get("file", "") or bounded.get("file_path", "")
    language = data.get("language", "") or bounded.get("language", "")

    search_results: list[dict[str, Any]] = []
    related_files: list[dict[str, Any]] = []
    file_tree: list[str] = []

    try:
        tree_result = adapter.get_project_tree(process_name=process_name)
        if tree_result.get("ok"):
            file_tree = tree_result.get("tree", [])[:50]
    except Exception:
        pass

    search_terms = _extract_search_terms(user_input, bounded)

    if file_path:
        import_names = _extract_import_names(str(file_path), str(language))
        search_terms = list(dict.fromkeys(import_names + search_terms))[:6]

    for term in search_terms[:3]:
        try:
            result = adapter.search_codebase(term, max_results=5, process_name=process_name)
            if result.get("ok") and result.get("results"):
                search_results.extend(result["results"])
        except Exception:
            continue

    if search_results:
        seen_files: set[str] = set()
        for r in search_results[:10]:
            fname = r.get("file", "")
            if fname and fname not in seen_files and fname != str(file_path):
                seen_files.add(fname)
        for fname in list(seen_files)[:3]:
            try:
                file_result = adapter.read_file(fname, process_name=process_name)
                if file_result.get("ok") and file_result.get("content"):
                    related_files.append({
                        "file": fname,
                        "language": file_result.get("language", ""),
                        "content": file_result.get("content", ""),
                    })
            except Exception:
                continue

    search_results = search_results[:15]
    return build_codebase_search_block(
        search_results=search_results if search_results else None,
        file_tree=file_tree if file_tree else None,
        related_files=related_files if related_files else None,
    )


def process_user_message(user_input: str) -> str:
    try:
        state = get_current_state().state
    except Exception:
        state = AppState.FALLBACK

    prompt_variables: dict[str, str] = {}
    prefix: str = ""

    engine = _get_accountability_engine()
    engine.on_state_changed(state)

    memory_context = get_memory_prompt_block(_get_memory_store(), state)
    if memory_context:
        prompt_variables["memory_context"] = memory_context

    if state == AppState.CODING:
        adapter = MCPAdapter()
        
        window_info = get_foreground_window_info()
        process_name = window_info.process_name if window_info else None
        
        mcp_context = adapter.get_active_context(process_name=process_name)
        
        if mcp_context["ok"]:
            health = HealthCheckResult(
                available=True,
                status="available",
                last_check=datetime.now().isoformat(),
                degraded_mode=False,
            )
        else:
            health = HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=mcp_context.get("error", {}).get("message", "Unknown error"),
                degraded_mode=True,
            )
            
        upsert_integration_health(adapter.component_name, health)

        bounded = build_bounded_coding_context(mcp_context)

        prompt_variables["code_context_block"] = bounded["prompt_block"]
        prompt_variables["code_context_notice"] = bounded["notice"]

        if not bounded["available"]:
            emit_event(
                event_type="context.unavailable",
                component="mode_controller",
                severity="warning",
                message="Active code context unavailable; continuing without context",
                details={"error": bounded.get("error")},
            )
            prefix = bounded["notice"] + " "

        try:
            codebase_block = _build_codebase_context(adapter, mcp_context, user_input, bounded, process_name)
            if codebase_block:
                prompt_variables["codebase_context_block"] = codebase_block
        except Exception:
            pass

    if state == AppState.DOOMSCROLLING:
        settings = load_settings_safe()
        if settings.screenpipe_enabled:
            screenpipe = ScreenpipeAdapter()
            try:
                sp_health = screenpipe.health_check()
            except Exception:
                sp_health = HealthCheckResult(
                    available=False,
                    status="unavailable",
                    last_check=datetime.now().isoformat(),
                    last_error="Screenpipe health check raised exception",
                    degraded_mode=True,
                )
            upsert_integration_health(screenpipe.component_name, sp_health)
    
            if sp_health.available:
                sp_context = screenpipe.get_recent_context()
                if sp_context["ok"] and sp_context.get("signals"):
                    prompt_variables["screenpipe_signals"] = str(sp_context["signals"])
                else:
                    emit_event(
                        event_type="context.unavailable",
                        component="mode_controller",
                        severity="warning",
                        message="Screenpipe context retrieval failed; continuing without distraction signals",
                        details={"error": sp_context.get("error", {}).get("message", "Unknown")},
                    )
            else:
                emit_event(
                    event_type="integration.failed",
                    component="screenpipe",
                    severity="warning",
                    message="Screenpipe unavailable; doomscroll detection operating in degraded mode",
                    details={"degraded_mode": "foreground_detection_only"},
                )
                prefix = "[Degraded: Screenpipe unavailable — using foreground-only detection] "
        else:
            # Screenpipe explicitly disabled
            prefix = "[Degraded: Screenpipe disabled — using foreground-only detection] "

    try:
        response_text = prefix + generate_response(user_input, state_override=state, prompt_variables=prompt_variables)
    except Exception:
        logger.exception("Unexpected exception in generate_response for process_user_message")
        emit_event(
            event_type="model.generation_failed",
            component="mode_controller",
            severity="error",
            message="Unexpected exception during response generation",
            details={"state": state},
        )
        response_text = prefix + "[System error: generation failed unexpectedly. Check logs for details.]"

    try:
        settings = load_settings_safe()
        if getattr(settings, "tts_enabled", False):
            tts = TTSAdapter()
            if tts.is_available():
                tts.speak_async(_strip_markdown_for_speech(response_text))
            else:
                tts_health = tts.health_check()
                emit_event(
                    event_type="integration.failed",
                    component="tts",
                    severity="warning",
                    message="TTS unavailable; text response only",
                    details={"error": tts_health.last_error, "degraded_mode": "text_only"},
                )
    except Exception:
        logger.exception("TTS integration error in process_user_message")
        emit_event(
            event_type="integration.failed",
            component="tts",
            severity="warning",
            message="TTS integration raised an unexpected exception",
            details={"context": "process_user_message"},
        )

    return response_text


def run_text_interaction_loop() -> None:
    emit_event(
        event_type="app.started",
        component="mode_controller",
        severity="info",
        message="Text interaction loop started"
    )

    settings = load_settings_safe()

    if settings.sync_enabled:
        emit_event(
            event_type="sync.warning",
            component="mode_controller",
            severity="warning",
            message="sync_enabled is set to true but cloud sync is not implemented in MVP; enforcing local-only behavior",
            details={"sync_enabled": True},
        )

    memory_store = _get_memory_store()
    engine = _get_accountability_engine()
    last_memory_update = time_module.time()
    last_debt_update = time_module.time()
    last_screenpipe_poll = time_module.time()
    last_voice_health_poll = time_module.time()
    last_summary = ""
    update_interval = settings.memory_update_interval_seconds
    debt_update_interval = 120
    screenpipe_interval = settings.screenpipe_poll_interval_seconds
    voice_health_interval = 60

    console.print("[bold green]Welcome to Bananalyzer! Type 'exit' or 'quit' to stop.[/bold green]")
    console.print("[dim]Text interaction mode active (baseline). Type /voice for voice input.[/dim]\n")

    try:
        while True:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")

            if user_input.strip().lower() in ["exit", "quit"]:
                console.print("[bold yellow]Goodbye![/bold yellow]")
                break

            if not user_input.strip():
                continue

            if user_input.strip().lower() in ["/voice", "/listen"]:
                settings_current = load_settings_safe()
                if not getattr(settings_current, "stt_enabled", False):
                    console.print("[red]STT is disabled. Enable it in settings.yaml to use voice input.[/red]")
                    continue
                stt = STTAdapter()
                if not stt.is_available():
                    console.print(f"[red]STT is unavailable: {stt.health_check().last_error}[/red]")
                    console.print("[yellow]Please type your message instead.[/yellow]")
                    continue
                console.print(f"[bold cyan]Listening... (recording for {getattr(settings_current, 'stt_record_duration_seconds', 5)} seconds)[/bold cyan]")
                result = stt.listen()
                if not result.ok:
                    console.print(f"[red]Speech recognition failed: {result.error.get('message', 'Unknown') if result.error else 'Unknown'}[/red]")
                    continue
                user_input = result.data
                console.print(f"[bold green]You said:[/bold green] {user_input}")

            response = process_user_message(user_input)
            console.print("\n[bold magenta]Bananalyzer[/bold magenta]")
            console.print(Markdown(response))
            console.print()

            now = time_module.time()
            if now - last_memory_update >= update_interval:
                try:
                    state = get_current_state().state
                except Exception:
                    state = AppState.COMPANION
                last_summary, skipped = periodic_memory_update(memory_store, state, last_summary)
                last_memory_update = now

            if now - last_debt_update >= debt_update_interval:
                try:
                    engine.update_debt()
                except Exception:
                    pass
                last_debt_update = now

            if settings.screenpipe_enabled and (now - last_screenpipe_poll >= screenpipe_interval):
                try:
                    screenpipe = ScreenpipeAdapter()
                    sp_health = screenpipe.health_check()
                    upsert_integration_health(screenpipe.component_name, sp_health)
                except Exception:
                    pass
                last_screenpipe_poll = now

            if now - last_voice_health_poll >= voice_health_interval:
                try:
                    tts = TTSAdapter()
                    tts_health = tts.health_check()
                    upsert_integration_health("tts", tts_health)
                except Exception:
                    pass
                try:
                    stt = STTAdapter()
                    stt_health = stt.health_check()
                    upsert_integration_health("stt", stt_health)
                except Exception:
                    pass
                last_voice_health_poll = now

            intervention_result = engine.check_intervention()
            if intervention_result:
                console.print("\n[bold red]⚠️ Intervention[/bold red]")
                console.print(Markdown(intervention_result))
                console.print()

                try:
                    settings = load_settings_safe()
                    if getattr(settings, "tts_enabled", False):
                        tts = TTSAdapter()
                        if tts.is_available():
                            tts.speak_async(_strip_markdown_for_speech(intervention_result))
                except Exception:
                    pass

    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold yellow]Goodbye![/bold yellow]")

    finally:
        emit_event(
            event_type="app.stopped",
            component="mode_controller",
            severity="info",
            message="Text interaction loop stopped"
        )

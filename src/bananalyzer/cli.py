import collections
import json
from pathlib import Path

import typer 
from bananalyzer.config import scaffold_data_foundation
from rich import print as rprint
from rich.panel import Panel
from bananalyzer.constants import CONFIG_DIR, STATE_DIR, LOGS_DIR, DATA_DIR, MEMORY_DIR, AppState
from bananalyzer.config import (
    Settings,  # noqa: F401
    ModelProfiles,
    Thresholds,  # noqa: F401
    get_config_paths,
    load_model_profiles_safe,
    load_settings_safe,
    load_thresholds_safe,
)
from bananalyzer.state_machine import get_current_state
from bananalyzer.diagnostics import run_diagnostics, get_integration_health
from bananalyzer.privacy import PERSISTENCE_ALLOWED_CATEGORIES
from bananalyzer.accountability import StateTimeTracker, BananaDebtCalculator
from rich.table import Table
from rich.console import Console
from rich.text import Text

console = Console()

app = typer.Typer(help="Bananalyzer CLI.")

@app.callback()
def setup_data():
    """Setup the data foundation for Bananalyzer."""
    scaffold_data_foundation()
    print("Data foundation scaffolded successfully.")


@app.command(name="run")
def run(
    mcp_port: int = typer.Option(8001, help="Port for the auto-started MCP server (0 to disable)"),
):
    """Run the Bananalyzer CLI in text interaction mode."""
    from bananalyzer.mode_controller import run_text_interaction_loop
    from bananalyzer.trae_mcp_server import run_mcp_server_thread

    if mcp_port > 0:
        run_mcp_server_thread(port=mcp_port)
        rprint(f"[dim]MCP server auto-started on http://127.0.0.1:{mcp_port}[/dim]")

    run_text_interaction_loop()


@app.command(name="listen")
def listen(
    mcp_port: int = typer.Option(8001, help="Port for the auto-started MCP server (0 to disable)"),
):
    """Listen via microphone and transcribe speech to text, then process the response."""
    from bananalyzer.mode_controller import process_user_message
    from bananalyzer.integrations.stt import STTAdapter
    from bananalyzer.trae_mcp_server import run_mcp_server_thread

    if mcp_port > 0:
        run_mcp_server_thread(port=mcp_port)
        rprint(f"[dim]MCP server auto-started on http://127.0.0.1:{mcp_port}[/dim]")

    settings = load_settings_safe()

    if not getattr(settings, "stt_enabled", False):
        rprint("[red]STT is disabled (stt_enabled: false in settings.yaml). Enable it to use voice input.[/red]")
        rprint("[yellow]Voice input is currently unavailable. Please type your question instead.[/yellow]")
        return

    stt = STTAdapter()
    health = stt.health_check()
    if not health.available:
        rprint(f"[red]STT is unavailable: {health.last_error}[/red]")
        rprint("[yellow]Voice input is currently unavailable. Please type your question instead.[/yellow]")
        return

    rprint(f"[bold cyan]Listening... (recording for {getattr(settings, 'stt_record_duration_seconds', 5)} seconds)[/bold cyan]")
    result = stt.listen()

    if not result.ok:
        rprint(f"[red]Speech recognition failed: {result.error.get('message', 'Unknown error') if result.error else 'Unknown'}[/red]")
        return

    transcribed = result.data
    rprint(f"[bold green]You said:[/bold green] {transcribed}")

    response = process_user_message(transcribed)
    console = Console()
    console.print("\n[bold magenta]Bananalyzer[/bold magenta]")
    from rich.markdown import Markdown
    console.print(Markdown(response))
    console.print()

    
@app.command(name="status")
def status():
    """Show the current status of the Bananalyzer CLI."""
    # Force utf-8 encoding for Rich Console to avoid cp1252 charmap errors on Windows
    console = Console(force_terminal=True, safe_box=False)
    rprint(Panel.fit("Bananalyzer Status", style="bold green"))

    # 1. Current State
    current_state = get_current_state()
    rprint(f"[bold]Current State:[/bold] {current_state.state}")
    if current_state.timestamp:
        rprint(f"[dim]Last updated: {current_state.timestamp}[/dim]")
    if current_state.reason:
        rprint(f"[dim]Reason: {current_state.reason}[/dim]")
    if current_state.confidence is not None:
        rprint(f"[dim]Confidence: {current_state.confidence}[/dim]")
    if current_state.state == AppState.FALLBACK:
        rprint("\n[yellow]Fallback mode active.[/yellow]")
        rprint("[dim]Capabilities: Text interaction available. Some signals/integrations may be unavailable.[/dim]")

    # 2. Model/Profile
    profiles = ModelProfiles()
    rprint(f"\n[bold]Active Model:[/bold] {profiles.default_model}")

    # 3. Integration Health
    health_report = get_integration_health()
    rprint("\n[bold]Integration Health:[/bold]")
    if not health_report.integrations:
        rprint("No integration health recorded yet.")
    else:
        health_table = Table(title="Integration Health")
        health_table.add_column("Integration", style="cyan")
        health_table.add_column("Status", style="magenta")
        health_table.add_column("Last Check", style="dim")

        for component, entry in health_report.integrations.items():
            status_text = Text(entry.status)
            if entry.status == "available":
                status_text.stylize("green")
            elif entry.status in ["unavailable", "degraded"]:
                status_text.stylize("red")
            health_table.add_row(
                component,
                status_text,
                entry.last_check
            )
        console.print(health_table)

    rprint("\n[bold]Voice Configuration Validation:[/bold]")
    settings = load_settings_safe()
    stt_exec_ok = getattr(settings, "stt_executable_path", "") and Path(getattr(settings, "stt_executable_path", "")).exists()
    stt_model_ok = getattr(settings, "stt_model_path", "") and Path(getattr(settings, "stt_model_path", "")).exists()

    if getattr(settings, "stt_enabled", False):
        stt_exec_status = "[green]✓ found[/green]" if stt_exec_ok else f"[red]✗ not found ({settings.stt_executable_path})[/red]"
        stt_model_status = "[green]✓ found[/green]" if stt_model_ok else f"[red]✗ not found ({settings.stt_model_path})[/red]"
        rprint(f"  STT executable: {stt_exec_status}")
        rprint(f"  STT model: {stt_model_status}")
    else:
        rprint("  STT: disabled")

    if getattr(settings, "tts_enabled", False):
        tts_engine = getattr(settings, "tts_engine", "kokoro")
        if tts_engine == "kokoro":
            tts_model_ok = getattr(settings, "tts_voice_model_path", "") and Path(getattr(settings, "tts_voice_model_path", "")).exists()
            tts_voices_ok = getattr(settings, "tts_voices_path", "") and Path(getattr(settings, "tts_voices_path", "")).exists()
            tts_model_status = "[green]✓ found[/green]" if tts_model_ok else f"[red]✗ not found ({settings.tts_voice_model_path})[/red]"
            tts_voices_status = "[green]✓ found[/green]" if tts_voices_ok else f"[red]✗ not found ({settings.tts_voices_path})[/red]"
            rprint(f"  TTS engine: {tts_engine}")
            rprint(f"  TTS model (ONNX): {tts_model_status}")
            rprint(f"  TTS voices (BIN): {tts_voices_status}")
            rprint(f"  TTS voice: {getattr(settings, 'tts_voice', 'af_heart')}")
        else:
            tts_exec_ok = getattr(settings, "tts_executable_path", "") and Path(getattr(settings, "tts_executable_path", "")).exists()
            tts_model_ok = getattr(settings, "tts_voice_model_path", "") and Path(getattr(settings, "tts_voice_model_path", "")).exists()
            tts_exec_status = "[green]✓ found[/green]" if tts_exec_ok else f"[red]✗ not found ({settings.tts_executable_path})[/red]"
            tts_model_status = "[green]✓ found[/green]" if tts_model_ok else f"[red]✗ not found ({settings.tts_voice_model_path})[/red]"
            rprint(f"  TTS executable: {tts_exec_status}")
            rprint(f"  TTS voice model: {tts_model_status}")
    else:
        rprint("  TTS: disabled")

        any_degraded = any(entry.degraded_mode for entry in health_report.integrations.values())
        if any_degraded:
            rprint("\n[yellow]Degraded mode active: some integrations are unavailable, but text interaction still works.[/yellow]")

    # 3.5 Activity Time by State
    tracker = StateTimeTracker()
    time_totals = tracker.get_totals_display()
    rprint("\n[bold]Activity Time (Session):[/bold]")
    time_table = Table(title="Time by State")
    time_table.add_column("State", style="cyan")
    time_table.add_column("Duration", style="magenta")
    for state, duration in time_totals.items():
        time_table.add_row(state, duration)
    console.print(time_table)

    # 3.6 Banana Debt
    debt_calc = BananaDebtCalculator()
    debt_data = debt_calc.get_current_debt()
    if debt_data:
        rprint("\n[bold]Banana Debt:[/bold]")
        current = debt_data.get("current_debt", 0)
        rprint(f"  Current: [{'red' if current > 10 else 'yellow' if current > 5 else 'green'}]{current:.1f}[/{'red' if current > 10 else 'yellow' if current > 5 else 'green'}]")
        breakdown = debt_data.get("breakdown", {})
        if breakdown:
            rprint(f"  Coding: {breakdown.get('coding_minutes', 0):.1f}m | Gaming: {breakdown.get('gaming_minutes', 0):.1f}m | Doomscrolling: {breakdown.get('doomscrolling_minutes', 0):.1f}m")
        if debt_data.get("last_updated"):
            rprint(f"  [dim]Last updated: {debt_data['last_updated']}[/dim]")
    else:
        rprint("\n[bold]Banana Debt:[/bold] No data yet.")

    # 4. Recent Events
    events_file = LOGS_DIR / "events.jsonl"
    recent_events = []
    if events_file.exists():
        with open(events_file, "r", encoding="utf-8") as f:
            recent_events = list(collections.deque(f, maxlen=5))

    if recent_events:
        rprint("\n[bold]Recent Events:[/bold]")
        for line in recent_events:
            try:
                event = json.loads(line.strip())
                rprint(f"  • [{event['severity']}] {event['message']}")
            except Exception:
                pass
    else:
        rprint("\n[bold]Recent Events:[/bold] No events yet.")

    # 5. Privacy
    rprint("\n[bold]Persistence Allowed Categories:[/bold]")
    for category in PERSISTENCE_ALLOWED_CATEGORIES:
        rprint(f"  • {category}")
    rprint("\n[dim]Note: Raw OCR, raw audio, large code excerpts, and unbounded history are NOT stored by default.[/dim]")

    # 6. Text Interaction Status
    rprint("\n[bold]Interaction Mode:[/bold] Text Interaction (Baseline)")

    settings = load_settings_safe()
    rprint(f"\n[bold]Cloud Sync:[/bold] {'Enabled' if settings.sync_enabled else 'Disabled (local-only)'}")
    if settings.sync_enabled:
        rprint("[yellow]Warning: sync_enabled is true but cloud sync is not implemented in MVP.[/yellow]")
    
@app.command(name="dashboard")
def dashboard():
    """Show the dashboard of the Bananalyzer CLI."""
    from bananalyzer.ui.dashboard import DashboardApp
    app = DashboardApp()
    app.run()

@app.command(name="diagnose")
def diagnose():
    """Diagnose the Bananalyzer CLI."""
    rprint(Panel.fit("Diagnostic Report", style="bold blue"))

    # Check Directories
    rprint(f"Data Dir exists: {DATA_DIR.exists()} ({DATA_DIR})")
    rprint(f"State Dir exists: {STATE_DIR.exists()} ({STATE_DIR})")
    rprint(f"Config Dir exists: {CONFIG_DIR.exists()} ({CONFIG_DIR})")

    # Check a specific file
    settings_file = CONFIG_DIR / "settings.yaml"
    if settings_file.exists():
        rprint("[green]✓ settings.yaml exists[/green]")
    else:
        rprint("[red]✗ settings.yaml not found[/red]")

    # Run Diagnostics
    rprint("\n[bold]Running integration health checks...[/bold]")
    health_report = run_diagnostics()

    health_table = Table(title="Integration Diagnostics")
    health_table.add_column("Integration", style="cyan")
    health_table.add_column("Available", style="magenta")
    health_table.add_column("Status", style="yellow")
    health_table.add_column("Last Error", style="dim")

    for component, entry in health_report.integrations.items():
        available_text = "✓" if entry.available else "✗"
        available_color = "green" if entry.available else "red"
        health_table.add_row(
            component,
            Text(available_text, style=available_color),
            entry.status,
            entry.last_error or "None"
        )

    console.print(health_table)

@app.command(name="config")   
def config():
    """Configure the Bananalyzer CLI."""
    rprint(Panel.fit("Active Configuration", style="bold magenta"))
    
    config_paths = get_config_paths()
    app_settings = load_settings_safe()
    model_profiles = load_model_profiles_safe()
    thresholds = load_thresholds_safe()

    paths_table = Table(title="Config Paths")
    paths_table.add_column("Item", style="cyan")
    paths_table.add_column("Path", style="dim")
    for key, path in config_paths.items():
        paths_table.add_row(key, str(path))
    console.print(paths_table)

    settings_table = Table(title="Detection & Routing Settings")
    settings_table.add_column("Key", style="cyan")
    settings_table.add_column("Value", style="magenta")
    settings_table.add_row("app_name", str(app_settings.app_name))
    settings_table.add_row("foreground_poll_interval_seconds", str(app_settings.foreground_poll_interval_seconds))
    settings_table.add_row("idle_seconds_for_companion", str(thresholds.idle_seconds_for_companion))
    settings_table.add_row("doomscrolling_threshold_mins", str(thresholds.doomscrolling_threshold_mins))
    settings_table.add_row("fallback_confidence_threshold", str(thresholds.fallback_confidence_threshold))
    settings_table.add_row("default_model", str(model_profiles.default_model))
    settings_table.add_row("app_category_map_entries", str(len(app_settings.foreground_app_category_map)))
    settings_table.add_row("sync_enabled", str(app_settings.sync_enabled))
    console.print(settings_table)

    voice_table = Table(title="Voice Settings")
    voice_table.add_column("Key", style="cyan")
    voice_table.add_column("Value", style="magenta")
    voice_table.add_row("STT enabled", str(app_settings.stt_enabled))
    voice_table.add_row("STT executable path", app_settings.stt_executable_path or "(not set)")
    voice_table.add_row("STT model path", app_settings.stt_model_path or "(not set)")
    voice_table.add_row("STT record duration (s)", str(app_settings.stt_record_duration_seconds))
    voice_table.add_row("TTS enabled", str(app_settings.tts_enabled))
    voice_table.add_row("TTS engine", app_settings.tts_engine)
    voice_table.add_row("TTS executable path", app_settings.tts_executable_path or "(not set)")
    voice_table.add_row("TTS voice", getattr(app_settings, "tts_voice", "af_heart"))
    voice_table.add_row("TTS voice model path", app_settings.tts_voice_model_path or "(not set)")
    voice_table.add_row("TTS voices path", app_settings.tts_voices_path or "(not set)")
    voice_table.add_row("Voice CPU-side", "Yes (Piper/Kokoro + Whisper.cpp)")
    console.print(voice_table)

    mappings_table = Table(title="App → Category Mappings")
    mappings_table.add_column("Process", style="cyan")
    mappings_table.add_column("Category", style="magenta")
    for proc_name, category in sorted(app_settings.foreground_app_category_map.items()):
        mappings_table.add_row(proc_name, category)
    console.print(mappings_table)

    from bananalyzer.persona import get_prompt_paths

    prompts_table = Table(title="Prompt Paths (by state)")
    prompts_table.add_column("State", style="cyan")
    prompts_table.add_column("Path", style="dim")
    for state, path in get_prompt_paths().items():
        prompts_table.add_row(state, str(path))
    console.print(prompts_table)

    memory_table = Table(title="Memory File Paths")
    memory_table.add_column("File", style="cyan")
    memory_table.add_column("Path", style="dim")
    memory_table.add_row("memory.md", str(MEMORY_DIR / "memory.md"))
    memory_table.add_row("session_summary.md", str(MEMORY_DIR / "session_summary.md"))
    memory_table.add_row("banana_debt.json", str(MEMORY_DIR / "banana_debt.json"))
    console.print(memory_table)


@app.command(name="mcp-serve")
def mcp_serve(
    port: int = typer.Option(8001, help="Port to run the MCP server on"),
    host: str = typer.Option("127.0.0.1", help="Host to bind to"),
):
    """Start a local MCP server for Trae/VS Code context."""
    from bananalyzer.trae_mcp_server import run_mcp_server

    run_mcp_server(host=host, port=port)


@app.command(name="mcp-push")
def mcp_push(
    file: str = typer.Option("", help="Active file path"),
    language: str = typer.Option("", help="Language (python, typescript, etc.)"),
    selection: str = typer.Option("", help="Selected/highlighted text in the editor"),
):
    """Push current Trae editor context to the MCP server."""
    from bananalyzer.trae_mcp_server import push_context

    push_context(file_path=file, language=language, selection=selection)


@app.command(name="mcp-workspace")
def mcp_workspace(
    path: str = typer.Option(".", help="Path to project root"),
):
    """Set the workspace root for codebase search."""
    from pathlib import Path
    from bananalyzer.trae_mcp_server import push_workspace

    root = str(Path(path).resolve())
    push_workspace(root)


@app.command(name="mcp-search")
def mcp_search(
    query: str = typer.Option(..., help="Search query"),
    max_results: int = typer.Option(20, help="Max results"),
):
    """Search the codebase via the MCP server."""
    from bananalyzer.trae_mcp_server import search_codebase

    results = search_codebase(query, max_results)
    if not results:
        rprint("[yellow]No results found. Is the workspace root set? Try: bananalyzer mcp-workspace[/]")
        return
    for r in results:
        rprint(f"[cyan]{r['file']}:{r['line']}[/] [dim]{r['snippet']}[/]")

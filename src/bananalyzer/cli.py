import collections
import time
import typer 
from bananalyzer.config import scaffold_data_foundation
from rich import print as rprint
from rich.panel import Panel
from bananalyzer.constants import CONFIG_DIR, STATE_DIR, LOGS_DIR, DATA_DIR, AppState
from bananalyzer.config import (
    Settings,
    ModelProfiles,
    Thresholds,
    get_config_paths,
    load_model_profiles_safe,
    load_settings_safe,
    load_thresholds_safe,
)
from bananalyzer.state_machine import get_current_state
from bananalyzer.diagnostics import run_diagnostics, get_integration_health
from bananalyzer.privacy import PERSISTENCE_ALLOWED_CATEGORIES
from rich.table import Table
from rich.console import Console
from rich.text import Text
import json

console = Console()

app = typer.Typer(help="Bananalyzer CLI.")

@app.callback()
def setup_data():
    """Setup the data foundation for Bananalyzer."""
    scaffold_data_foundation()
    print("Data foundation scaffolded successfully.")


@app.command(name="run")
def run():
    """Run the Bananalyzer CLI in text interaction mode."""
    from bananalyzer.mode_controller import run_text_interaction_loop
    run_text_interaction_loop()

    
@app.command(name="status")
def status():
    """Show the current status of the Bananalyzer CLI."""
    rprint(Panel.fit("📊 Bananalyzer Status", style="bold green"))

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

        any_degraded = any(entry.degraded_mode for entry in health_report.integrations.values())
        if any_degraded:
            rprint("\n[yellow]⚠️ Degraded mode active: some integrations are unavailable, but text interaction still works.[/yellow]")

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
    
@app.command(name="dashboard")
def dashboard():
    """Show the dashboard of the Bananalyzer CLI."""
    from bananalyzer.ui.dashboard import DashboardApp
    app = DashboardApp()
    app.run()

@app.command(name="diagnose")
def diagnose():
    """Diagnose the Bananalyzer CLI."""
    rprint(Panel.fit("🔍 Diagnostic Report", style="bold blue"))

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
    rprint(Panel.fit("⚙ Active Configuration", style="bold magenta"))
    
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
    console.print(settings_table)

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

    

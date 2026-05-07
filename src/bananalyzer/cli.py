import collections
import time
import typer 
from bananalyzer.config import scaffold_data_foundation
from rich import print as rprint
from rich.panel import Panel
from bananalyzer.constants import CONFIG_DIR, STATE_DIR, LOGS_DIR, DATA_DIR
from bananalyzer.config import Settings, ModelProfiles, Thresholds
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
    if current_state.last_updated:
        rprint(f"[dim]Last updated: {current_state.last_updated}[/dim]")

    # 2. Model/Profile
    profiles = ModelProfiles()
    rprint(f"\n[bold]Active Model:[/bold] {profiles.default_model}")

    # 3. Integration Health
    health_report = get_integration_health()
    if health_report.integrations:
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

        # Check for degraded mode
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
    
    # Instantiate the config classes (they automatically read the YAML files)
    app_settings = Settings()
    model_profiles = ModelProfiles()
    thresholds = Thresholds()

    # Print the settings
    rprint(f"[bold] 🖥 App Name [/bold] : {app_settings.app_name}")
    rprint(f"[bold] 🤖 Default Model [/bold] : {model_profiles.default_model}")
    rprint(f"[bold] ⏰ Thresholds [/bold] : {thresholds.doomscrolling_threshold_mins} mins")

    
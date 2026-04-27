import imp
import time
import typer 
from bananalyzer.config import scaffold_data_foundation
from rich import print as rprint
from rich.panel import Panel
from bananalyzer.constants import CONFIG_DIR, STATE_DIR, LOGS_DIR, DATA_DIR
from bananalyzer.config import Settings, ModelProfiles, Thresholds
from rich.table import Table
from rich.console import Console
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
    """Run the Bananalyzer CLI."""
    print("Starting Bananalyzer CLI...")

    # Placeholder for the main loop or functionality of the CLI
    try:
        while True:
            # In a real implementation, this would be where the CLI checks for new data, updates status, etc.
            print("Bananalyzer is running... (Press Ctrl+C to stop)")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nBananalyzer CLI stopped.")

    
@app.command(name="status")
def status():
    """Show the current status of the Bananalyzer CLI."""
    rprint(Panel.fit("📊 Bananalyzer Status", style="bold green"))

    # 1. Read the current_state.json
    state_file = STATE_DIR / "current_state.json"
    state_data = {}
    if state_file.exists():
        with open(state_file, "r") as f:
            state = json.load(f)

    current_state = state_data.get("state", "unknown")
    rprint(f"[bold]Current State:[/bold] {current_state}")

    # 2. Read model from config
    profiles = ModelProfiles()
    rprint(f"[bold]Active Model:[/bold] {profiles.default_model}")

    # 3. Read integration_health.json using a Rich Table
    health_file = STATE_DIR / "integration_health.json"
    health_data = {}
    if health_file.exists():
        with open(health_file, "r") as f:
            health_data = json.load(f)

    health_table = Table(title="Integration Health")
    health_table.add_column("Integration", style="cyan")
    health_table.add_column("Status", style="magenta")


    if health_data:
        for service, status in health_data.items():
            health_table.add_row(service, status["status"])
    else:
        health_table.add_row("No integrations found", "", "")

    console.print(health_table)

    # 4. Recent events summary
    rprint("\n[bold] Recent Events:[/bold] No events yet.")
    
@app.command(name="dashboard")
def dashboard():
    """Show the dashboard of the Bananalyzer CLI."""
    rprint(Panel.fit("📊 Bananalyzer Dashboard", style="bold blue"))

    # Placeholder for dashboard content
    rprint("Dashboard content will be displayed here.")
    # Logic to show dynamic content based on the current state, recent events, etc. would go here.

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

    # Placeholder for Integrations (as per the story)
    rprint("\n[bold yellow]Integrations:[/bold yellow]")
    rprint("- OBS: [dim]Unavailable (Placeholder)[/dim]")
    rprint("- Discord: [dim]Unavailable (Placeholder)[/dim]")

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

    
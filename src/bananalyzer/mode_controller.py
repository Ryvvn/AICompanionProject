from datetime import datetime
from rich.prompt import Prompt
from rich.console import Console
from rich.markdown import Markdown

from bananalyzer.constants import AppState
from bananalyzer.context.context_builder import build_bounded_coding_context
from bananalyzer.diagnostics import upsert_integration_health
from bananalyzer.integrations import MCPAdapter
from bananalyzer.integrations.base import HealthCheckResult
from bananalyzer.model_router import generate_response
from bananalyzer.events import emit_event
from bananalyzer.state_machine import get_current_state

console = Console()


def process_user_message(user_input: str) -> str:
    try:
        state = get_current_state().state
    except Exception:
        state = AppState.FALLBACK

    prompt_variables: dict[str, str] = {}
    prefix: str = ""

    if state == AppState.CODING:
        adapter = MCPAdapter()
        
        mcp_context = adapter.get_active_context()
        
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

    return prefix + generate_response(user_input, state_override=state, prompt_variables=prompt_variables)


def run_text_interaction_loop() -> None:
    emit_event(
        event_type="app.started",
        component="mode_controller",
        severity="info",
        message="Text interaction loop started"
    )

    console.print("[bold green]Welcome to Bananalyzer! Type 'exit' or 'quit' to stop.[/bold green]")
    console.print("[dim]Text interaction mode active (baseline).[/dim]\n")

    try:
        while True:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")

            if user_input.strip().lower() in ["exit", "quit"]:
                console.print("[bold yellow]Goodbye![/bold yellow]")
                break

            if not user_input.strip():
                continue

            response = process_user_message(user_input)
            console.print("\n[bold magenta]Bananalyzer[/bold magenta]")
            console.print(Markdown(response))
            console.print()

    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold yellow]Goodbye![/bold yellow]")

    finally:
        emit_event(
            event_type="app.stopped",
            component="mode_controller",
            severity="info",
            message="Text interaction loop stopped"
        )

from rich.prompt import Prompt
from rich.console import Console
from rich.markdown import Markdown
from bananalyzer.model_router import generate_response
from bananalyzer.events import emit_event

console = Console()


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

            response = generate_response(user_input)
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

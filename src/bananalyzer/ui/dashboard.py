from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static

class DashboardApp(App):
    """A minimal placeholder Textual App for the dashboard."""

    CSS = """
    Screen {
        align: center middle;
    }
    #welcome {
        text-align: center;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("📊 Bananalyzer Dashboard (Placeholder)\n\nPress 'q' to quit.", id="welcome")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Bananalyzer"
        self.sub_title = "Dashboard"

    def on_key(self, event) -> None:
        if event.key == "q":
            self.exit()

if __name__ == "__main__":
    app = DashboardApp()
    app.run()

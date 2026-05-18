from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import VerticalScroll

from bananalyzer.state_machine import get_current_state
from bananalyzer.accountability import StateTimeTracker, BananaDebtCalculator
from bananalyzer.diagnostics import get_integration_health


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
    #status-panel {
        padding: 1 2;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="status-panel"):
            yield Static("", id="welcome")
            yield Static("", id="state-info")
            yield Static("", id="time-info")
            yield Static("", id="debt-info")
            yield Static("", id="health-info")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Bananalyzer"
        self.sub_title = "Dashboard"
        self._refresh_data()

    def _refresh_data(self) -> None:
        try:
            current = get_current_state()
            self.query_one("#welcome", Static).update(
                f"📊 Bananalyzer Dashboard\n\nState: {current.state}"
                + (f" (Confidence: {current.confidence:.1%})" if current.confidence is not None else "")
            )

            tracker = StateTimeTracker()
            totals = tracker.get_totals_display()
            time_lines = ["⏱ Activity Time:"]
            for state, duration in totals.items():
                time_lines.append(f"  {state}: {duration}")
            self.query_one("#time-info", Static).update("\n".join(time_lines))

            debt = BananaDebtCalculator()
            debt_data = debt.get_current_debt()
            if debt_data:
                self.query_one("#debt-info", Static).update(
                    f"🍌 Banana Debt: {debt_data.get('current_debt', 0):.1f}"
                )
            else:
                self.query_one("#debt-info", Static).update("🍌 Banana Debt: No data")

            health = get_integration_health()
            health_lines = ["🔍 Integration Health:"]
            for comp, entry in health.integrations.items():
                status_icon = "✓" if entry.available else "✗"
                health_lines.append(f"  {status_icon} {comp}: {entry.status}")
            self.query_one("#health-info", Static).update("\n".join(health_lines))

        except Exception:
            pass

    def on_key(self, event) -> None:
        if event.key == "q":
            self.exit()
        elif event.key == "r":
            self._refresh_data()


if __name__ == "__main__":
    app = DashboardApp()
    app.run()

from datetime import datetime
from .base import IntegrationAdapter, HealthCheckResult


class ScreenpipeAdapter(IntegrationAdapter):
    component_name: str = "screenpipe"

    def is_available(self) -> bool:
        return False

    def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(
            available=False,
            status="unavailable",
            last_check=datetime.now().isoformat(),
            last_error="Screenpipe integration not implemented yet",
            degraded_mode=True
        )

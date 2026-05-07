from datetime import datetime
from .base import IntegrationAdapter, HealthCheckResult


class OllamaAdapter(IntegrationAdapter):
    component_name: str = "ollama"

    def is_available(self) -> bool:
        return False

    def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(
            available=False,
            status="unavailable",
            last_check=datetime.now().isoformat(),
            last_error="Ollama integration not implemented yet",
            degraded_mode=True
        )

import json
from datetime import datetime
from typing import Dict
from pydantic import BaseModel, Field

from bananalyzer.constants import STATE_DIR
from bananalyzer.events import emit_event
from bananalyzer.integrations import (
    OllamaAdapter,
    ScreenpipeAdapter,
    MCPAdapter,
    STTAdapter,
    TTSAdapter,
    HealthCheckResult
)


class IntegrationHealthEntry(BaseModel):
    component: str
    available: bool
    status: str  # available, unavailable, degraded, unknown
    last_check: str
    last_error: str | None = None
    degraded_mode: bool = False


class IntegrationHealthReport(BaseModel):
    integrations: Dict[str, IntegrationHealthEntry] = Field(default_factory=dict)
    last_updated: str | None = None


def run_diagnostics() -> IntegrationHealthReport:
    adapters = [
        OllamaAdapter(),
        ScreenpipeAdapter(),
        MCPAdapter(),
        STTAdapter(),
        TTSAdapter()
    ]

    previous_report = get_integration_health()
    report = IntegrationHealthReport()

    for adapter in adapters:
        try:
            result: HealthCheckResult = adapter.health_check()
        except Exception as e:
            result = HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=str(e),
                degraded_mode=True
            )

        entry = IntegrationHealthEntry(
            component=adapter.component_name,
            available=result.available,
            status=result.status,
            last_check=result.last_check,
            last_error=result.last_error,
            degraded_mode=result.degraded_mode
        )
        report.integrations[adapter.component_name] = entry

        previous_entry = previous_report.integrations.get(adapter.component_name)

        if not result.available:
            emit_event(
                event_type="integration.failed",
                component=adapter.component_name,
                severity="warning",
                message=f"Integration {adapter.component_name} is unavailable",
                details={"error": result.last_error}
            )
        elif previous_entry and not previous_entry.available and result.available:
            emit_event(
                event_type="integration.recovered",
                component=adapter.component_name,
                severity="info",
                message=f"Integration {adapter.component_name} has recovered and is now available",
                details={"previous_error": previous_entry.last_error}
            )

    report.last_updated = datetime.now().isoformat()

    try:
        mcp_adapter = MCPAdapter()
        endpoint_health = mcp_adapter.health_check_all()
        for process_name, health_result in endpoint_health.items():
            component_key = f"mcp:{process_name}"
            report.integrations[component_key] = IntegrationHealthEntry(
                component=component_key,
                available=health_result.available,
                status=health_result.status,
                last_check=health_result.last_check,
                last_error=health_result.last_error,
                degraded_mode=health_result.degraded_mode,
            )
    except Exception:
        pass

    health_file = STATE_DIR / "integration_health.json"
    health_file.parent.mkdir(parents=True, exist_ok=True)

    with open(health_file, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

    return report


def get_integration_health() -> IntegrationHealthReport:
    health_file = STATE_DIR / "integration_health.json"
    health_file.parent.mkdir(parents=True, exist_ok=True)

    if not health_file.exists():
        return IntegrationHealthReport()

    try:
        with open(health_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return IntegrationHealthReport(**data)
    except Exception:
        return IntegrationHealthReport()


def upsert_integration_health(component: str, result: HealthCheckResult) -> None:
    report = get_integration_health()
    previous_entry = report.integrations.get(component)
    report.integrations[component] = IntegrationHealthEntry(
        component=component,
        available=result.available,
        status=result.status,
        last_check=result.last_check,
        last_error=result.last_error if result.last_error is not None else (previous_entry.last_error if previous_entry else None),
        degraded_mode=result.degraded_mode,
    )
    report.last_updated = datetime.now().isoformat()

    if previous_entry and not previous_entry.available and result.available:
        emit_event(
            event_type="integration.recovered",
            component=component,
            severity="info",
            message=f"Integration {component} has recovered and is now available",
            details={"previous_error": previous_entry.last_error},
        )
    elif previous_entry and previous_entry.available and not result.available:
        emit_event(
            event_type="integration.failed",
            component=component,
            severity="warning",
            message=f"Integration {component} transitioned from available to unavailable",
            details={"error": result.last_error},
        )

    health_file = STATE_DIR / "integration_health.json"
    health_file.parent.mkdir(parents=True, exist_ok=True)
    with open(health_file, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

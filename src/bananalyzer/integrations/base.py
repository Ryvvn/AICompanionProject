from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass


@dataclass
class AdapterResult:
    ok: bool
    data: Any | None = None
    error: dict | None = None


@dataclass
class HealthCheckResult:
    available: bool
    status: str  # available, unavailable, degraded, unknown
    last_check: str
    last_error: str | None = None
    degraded_mode: bool = False


class IntegrationAdapter(ABC):
    component_name: str

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def health_check(self) -> HealthCheckResult:
        pass

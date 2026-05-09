from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

import httpx

from bananalyzer.config import load_settings_safe
from .base import IntegrationAdapter, HealthCheckResult


class MCPError(TypedDict, total=False):
    code: str
    message: str
    recoverable: bool
    status_code: int


class MCPContextResult(TypedDict):
    ok: bool
    data: dict[str, Any] | None
    error: MCPError | None

class MCPAdapter(IntegrationAdapter):
    component_name: str = "mcp"

    def __init__(self, endpoint_url: str | None = None):
        resolved = endpoint_url
        if not resolved:
            settings = load_settings_safe()
            resolved = getattr(settings, "mcp_endpoint_url", None) or "http://127.0.0.1:8000/v1/context"

        self.endpoint_url = resolved
        self._client = httpx.Client(timeout=2.0)

    def is_available(self) -> bool:
        result = self.health_check()
        return result.available

    def health_check(self) -> HealthCheckResult:
        try:
            response = self._client.get(self.endpoint_url)
            if response.status_code == 200:
                return HealthCheckResult(
                    available=True,
                    status="available",
                    last_check=datetime.now().isoformat(),
                    degraded_mode=False,
                )
            return HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=f"Unexpected status code: {response.status_code}",
                degraded_mode=True,
            )
        except httpx.RequestError as e:
            return HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=f"Connection error: {e}",
                degraded_mode=True,
            )

    def get_active_context(self) -> MCPContextResult:
        try:
            response = self._client.get(self.endpoint_url)
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {"ok": True, "data": data, "error": None}
                except ValueError:
                    return {
                        "ok": False,
                        "data": None,
                        "error": {
                            "code": "mcp_invalid_json",
                            "message": "Failed to decode JSON from MCP context response",
                            "recoverable": True,
                        },
                    }
            return {
                "ok": False,
                "data": None,
                "error": {
                    "code": "mcp_http_error",
                    "message": f"Failed to retrieve context, status code: {response.status_code}",
                    "recoverable": True,
                    "status_code": response.status_code,
                },
            }
        except httpx.RequestError as e:
            return {
                "ok": False,
                "data": None,
                "error": {"code": "mcp_request_error", "message": f"Connection error: {e}", "recoverable": True},
            }

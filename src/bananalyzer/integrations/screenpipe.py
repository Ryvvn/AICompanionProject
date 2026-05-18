from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

import httpx

from bananalyzer.config import load_settings_safe
from .base import IntegrationAdapter, HealthCheckResult


class ScreenpipeError(TypedDict, total=False):
    code: str
    message: str
    recoverable: bool
    status_code: int


class ScreenpipeContextResult(TypedDict):
    ok: bool
    signals: dict[str, Any] | None
    error: ScreenpipeError | None


class ScreenpipeAdapter(IntegrationAdapter):
    component_name: str = "screenpipe"

    def __init__(self, endpoint_url: str | None = None):
        resolved = endpoint_url
        if not resolved:
            settings = load_settings_safe()
            resolved = getattr(settings, "screenpipe_endpoint_url", None) or "http://127.0.0.1:3030"

        self.endpoint_url = resolved
        self._client = httpx.Client(timeout=3.0)

    def is_available(self) -> bool:
        result = self.health_check()
        return result.available

    def health_check(self) -> HealthCheckResult:
        try:
            response = self._client.get(f"{self.endpoint_url}/health")
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
        except httpx.TimeoutException as e:
            return HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=f"Request timed out: {e}",
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
        except Exception as e:
            return HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=f"Unexpected failure: {e}",
                degraded_mode=True,
            )

    def _summarize_signals(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        signals: dict[str, Any] = {}
        if "app_name" in raw_data:
            signals["app_name"] = raw_data["app_name"]
        if "window_title" in raw_data:
            signals["window_title"] = raw_data["window_title"]
        if "browser_url" in raw_data:
            signals["browser_url"] = raw_data["browser_url"]
        if "duration_seconds" in raw_data:
            signals["duration_seconds"] = raw_data["duration_seconds"]
        if "content_type" in raw_data:
            signals["content_type"] = raw_data["content_type"]
        return signals

    def get_recent_context(self) -> ScreenpipeContextResult:
        try:
            response = self._client.get(f"{self.endpoint_url}/search", params={"limit": 5})
            if response.status_code == 200:
                try:
                    raw_data = response.json()
                    if isinstance(raw_data, dict):
                        signals = self._summarize_signals(raw_data)
                    elif isinstance(raw_data, list) and raw_data:
                        signals = self._summarize_signals(raw_data[0])
                    else:
                        signals = {}
                    return {"ok": True, "signals": signals, "error": None}
                except ValueError:
                    return {
                        "ok": False,
                        "signals": None,
                        "error": {
                            "code": "screenpipe_invalid_json",
                            "message": "Failed to decode JSON from Screenpipe response",
                            "recoverable": True,
                        },
                    }
            return {
                "ok": False,
                "signals": None,
                "error": {
                    "code": "screenpipe_http_error",
                    "message": f"Failed to retrieve context, status code: {response.status_code}",
                    "recoverable": True,
                    "status_code": response.status_code,
                },
            }
        except httpx.TimeoutException as e:
            return {
                "ok": False,
                "signals": None,
                "error": {
                    "code": "screenpipe_timeout",
                    "message": f"Request timed out: {e}",
                    "recoverable": True,
                },
            }
        except httpx.RequestError as e:
            return {
                "ok": False,
                "signals": None,
                "error": {
                    "code": "screenpipe_request_error",
                    "message": f"Connection error: {e}",
                    "recoverable": True,
                },
            }
        except Exception as e:
            return {
                "ok": False,
                "signals": None,
                "error": {
                    "code": "screenpipe_unexpected_error",
                    "message": f"Unexpected error: {e}",
                    "recoverable": False,
                },
            }

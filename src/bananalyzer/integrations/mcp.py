from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

import httpx

from bananalyzer.config import load_settings_safe
from bananalyzer.events import emit_event
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


class MCPSearchResult(TypedDict):
    ok: bool
    query: str
    results: list[dict[str, Any]]
    error: MCPError | None


class MCPFileResult(TypedDict):
    ok: bool
    file: str
    language: str
    content: str
    lines: int
    error: MCPError | None


class MCPAdapter(IntegrationAdapter):
    component_name: str = "mcp"

    def __init__(self, endpoint_url: str | None = None):
        settings = load_settings_safe()
        self._settings = settings
        self._endpoints: dict[str, str] = getattr(settings, "mcp_endpoints", {}) or {}
        self._fallback_url: str = getattr(settings, "mcp_endpoint_url", None) or "http://127.0.0.1:8000/v1/context"

        resolved = endpoint_url or self._fallback_url
        self.endpoint_url = resolved
        self._clients: dict[str, httpx.Client] = {}

    def _get_client_for_url(self, url: str) -> httpx.Client:
        if url not in self._clients:
            self._clients[url] = httpx.Client(timeout=2.0)
        return self._clients[url]

    def _resolve_endpoint(self, process_name: str | None) -> str:
        if process_name:
            key_lower = process_name.lower()
            for k, v in self._endpoints.items():
                if k.lower() == key_lower:
                    return v
        if "default" in self._endpoints:
            return self._endpoints["default"]
        return self._fallback_url

    def _try_fetch_context(self, url: str) -> MCPContextResult:
        try:
            client = self._get_client_for_url(url)
            response = client.get(url)
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

    def is_available(self) -> bool:
        result = self.health_check()
        return result.available

    def health_check(self) -> HealthCheckResult:
        try:
            client = self._get_client_for_url(self.endpoint_url)
            response = client.get(self.endpoint_url)
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

    def health_check_all(self) -> dict[str, HealthCheckResult]:
        results: dict[str, HealthCheckResult] = {}
        for name, url in self._endpoints.items():
            try:
                client = self._get_client_for_url(url)
                response = client.get(url)
                if response.status_code == 200:
                    results[name] = HealthCheckResult(
                        available=True,
                        status="available",
                        last_check=datetime.now().isoformat(),
                        degraded_mode=False,
                    )
                else:
                    results[name] = HealthCheckResult(
                        available=False,
                        status="unavailable",
                        last_check=datetime.now().isoformat(),
                        last_error=f"Unexpected status code: {response.status_code}",
                        degraded_mode=True,
                    )
            except httpx.RequestError as e:
                results[name] = HealthCheckResult(
                    available=False,
                    status="unavailable",
                    last_check=datetime.now().isoformat(),
                    last_error=f"Connection error: {e}",
                    degraded_mode=True,
                )
        return results

    def get_active_context(self, process_name: str | None = None) -> MCPContextResult:
        if process_name:
            url = self._resolve_endpoint(process_name)
            result = self._try_fetch_context(url)
            if result["ok"]:
                return result

            emit_event(
                event_type="context.unavailable",
                component="mcp",
                severity="warning",
                message=f"MCP endpoint for {process_name} unavailable, trying fallback",
                details={"process_name": process_name, "error": result["error"]},
            )

            fallback_result = None
            for name, url in self._endpoints.items():
                if name == process_name or name == "default":
                    continue
                fallback_result = self._try_fetch_context(url)
                if fallback_result["ok"]:
                    return fallback_result
                emit_event(
                    event_type="context.unavailable",
                    component="mcp",
                    severity="warning",
                    message=f"MCP fallback endpoint {name} also unavailable",
                    details={"process_name": name},
                )

            if fallback_result:
                return fallback_result
            return result

        return self._try_fetch_context(self.endpoint_url)

    def search_codebase(self, query: str, max_results: int = 20, process_name: str | None = None) -> MCPSearchResult:
        url = self._resolve_endpoint(process_name) if process_name else self.endpoint_url
        base = url.rstrip("/v1/context").rstrip("/context")
        grep_url = f"{base}/v1/grep"

        try:
            client = self._get_client_for_url(grep_url)
            response = client.post(
                grep_url,
                json={"query": query, "max_results": max_results},
            )
            data = response.json()
            if data.get("ok"):
                return {"ok": True, "query": query, "results": data.get("results", []), "error": None}
            return {"ok": False, "query": query, "results": [], "error": {"code": "mcp_search_error", "message": data.get("error", "Search failed")}}
        except Exception as e:
            return {"ok": False, "query": query, "results": [], "error": {"code": "mcp_search_error", "message": str(e)}}

    def read_file(self, file_path: str, process_name: str | None = None) -> MCPFileResult:
        url = self._resolve_endpoint(process_name) if process_name else self.endpoint_url
        base = url.rstrip("/v1/context").rstrip("/context")
        file_url = f"{base}/v1/file"

        try:
            client = self._get_client_for_url(file_url)
            response = client.post(
                file_url,
                json={"path": file_path},
            )
            data = response.json()
            if data.get("ok"):
                return {
                    "ok": True,
                    "file": data.get("file", ""),
                    "language": data.get("language", ""),
                    "content": data.get("content", ""),
                    "lines": data.get("lines", 0),
                    "error": None,
                }
            return {
                "ok": False,
                "file": file_path,
                "language": "",
                "content": "",
                "lines": 0,
                "error": {"code": "mcp_file_error", "message": data.get("error", "File read failed")},
            }
        except Exception as e:
            return {
                "ok": False,
                "file": file_path,
                "language": "",
                "content": "",
                "lines": 0,
                "error": {"code": "mcp_file_error", "message": str(e)},
            }

    def get_project_tree(self, process_name: str | None = None) -> dict[str, Any]:
        url = self._resolve_endpoint(process_name) if process_name else self.endpoint_url
        base = url.rstrip("/v1/context").rstrip("/context")
        tree_url = f"{base}/v1/tree"

        try:
            client = self._get_client_for_url(tree_url)
            response = client.get(tree_url)
            data = response.json()
            return data
        except Exception as e:
            return {"ok": False, "error": str(e)}

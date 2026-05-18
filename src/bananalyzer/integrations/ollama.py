from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import httpx

from bananalyzer.config import load_settings_safe
from bananalyzer.events import emit_event
from .base import IntegrationAdapter, HealthCheckResult, AdapterResult


class OllamaAdapter(IntegrationAdapter):
    component_name: str = "ollama"

    def __init__(self, base_url: str | None = None):
        settings = load_settings_safe()
        resolved = base_url or settings.ollama_base_url
        self.base_url = resolved.rstrip("/")
        self._timeout_seconds = settings.ollama_request_timeout_seconds
        self._client = httpx.Client(
            timeout=httpx.Timeout(
                connect=10.0,
                read=float(self._timeout_seconds),
                write=10.0,
                pool=10.0,
            )
        )

    def _upsert_health(self, result: HealthCheckResult) -> None:
        try:
            from bananalyzer.diagnostics import upsert_integration_health
            upsert_integration_health(self.component_name, result)
        except Exception:
            pass

    def is_available(self) -> bool:
        result = self.health_check()
        return result.available

    def health_check(self, model: str | None = None) -> HealthCheckResult:
        try:
            response = self._client.get(f"{self.base_url}/api/tags")
            if response.status_code != 200:
                result = HealthCheckResult(
                    available=False,
                    status="unavailable",
                    last_check=datetime.now().isoformat(),
                    last_error=f"Unexpected status code: {response.status_code}",
                    degraded_mode=True,
                )
                self._upsert_health(result)
                return result

            if model:
                try:
                    tags_data = response.json()
                    models_list = tags_data.get("models", [])
                    tag_names = {m.get("name", "") for m in models_list}
                    base_names = {m.get("name", "").split(":")[0] for m in models_list}
                    if model not in tag_names and model.split(":")[0] not in base_names:
                        result = HealthCheckResult(
                            available=False,
                            status="degraded",
                            last_check=datetime.now().isoformat(),
                            last_error=f"Model '{model}' not found. Run: ollama pull {model}",
                            degraded_mode=True,
                        )
                        self._upsert_health(result)
                        return result
                except Exception:
                    pass

            result = HealthCheckResult(
                available=True,
                status="available",
                last_check=datetime.now().isoformat(),
                degraded_mode=False,
            )
            self._upsert_health(result)
            return result
        except httpx.RequestError as e:
            error_msg = f"Connection error: {e}"
            result = HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=error_msg,
                degraded_mode=True,
            )
            self._upsert_health(result)
            return result
        except Exception as e:
            result = HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=f"Unexpected failure: {e}",
                degraded_mode=True,
            )
            self._upsert_health(result)
            return result

    def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str = "",
        options: dict[str, Any] | None = None,
    ) -> AdapterResult:
        request_body: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
        }
        if options:
            request_body["options"] = options

        try:
            response = self._client.post(
                f"{self.base_url}/api/generate",
                json=request_body,
            )
            if response.status_code != 200:
                error_msg = f"Ollama returned status {response.status_code}"
                try:
                    error_body = response.json()
                    ollama_error = error_body.get("error", response.text)
                    if "not found" in str(ollama_error).lower():
                        error_msg = f"Model '{model}' not found. Run: ollama pull {model}"
                    else:
                        error_msg += f": {ollama_error}"
                except Exception:
                    error_msg += f": {response.text}"
                result = AdapterResult(
                    ok=False,
                    error={"code": "ollama_http_error", "message": error_msg, "status_code": response.status_code},
                )
                self._record_generation_error(result)
                return result

            raw_text = response.text
            text = self._parse_generate_response(raw_text)

            emit_event(
                event_type="model.generation_succeeded",
                component="ollama",
                severity="info",
                message="Ollama generation succeeded",
                details={"model": model},
            )

            return AdapterResult(ok=True, data=text)
        except httpx.ConnectError as e:
            result = AdapterResult(
                ok=False,
                error={
                    "code": "ollama_unreachable",
                    "message": f"Ollama server is not running. Start it with: ollama serve",
                },
            )
            self._record_generation_error(result)
            return result
        except httpx.ReadTimeout:
            result = AdapterResult(
                ok=False,
                error={
                    "code": "ollama_timeout",
                    "message": f"Generation timed out after {self._timeout_seconds}s",
                },
            )
            self._record_generation_error(result)
            return result
        except httpx.RequestError as e:
            result = AdapterResult(
                ok=False,
                error={"code": "ollama_request_error", "message": f"Ollama connection error: {e}"},
            )
            self._record_generation_error(result)
            return result
        except json.JSONDecodeError:
            result = AdapterResult(
                ok=False,
                error={"code": "ollama_invalid_response", "message": "Ollama returned an unexpected response format"},
            )
            self._record_generation_error(result)
            return result
        except Exception as e:
            result = AdapterResult(
                ok=False,
                error={"code": "ollama_unknown_error", "message": str(e)},
            )
            self._record_generation_error(result)
            return result

    def _record_generation_error(self, result: AdapterResult) -> None:
        try:
            emit_event(
                event_type="model.generation_failed",
                component="ollama",
                severity="warning",
                message=f"Ollama generation failed: {result.error.get('code', 'unknown') if result.error else 'unknown'}",
                details=result.error or {},
            )
        except Exception:
            pass

    def _parse_generate_response(self, raw_text: str) -> str:
        if not raw_text.strip():
            return ""

        lines = raw_text.strip().splitlines()
        if len(lines) == 1:
            data = json.loads(raw_text)
            if data.get("done"):
                return data.get("response", "")
            return data.get("response", "")

        parts: list[str] = []
        any_parsed = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                any_parsed = True
                response_text = data.get("response", "")
                if response_text:
                    parts.append(response_text)
                if data.get("done"):
                    break
            except json.JSONDecodeError:
                continue
        if not any_parsed:
            raise json.JSONDecodeError("No valid JSON lines in Ollama response", raw_text, 0)
        return "".join(parts)

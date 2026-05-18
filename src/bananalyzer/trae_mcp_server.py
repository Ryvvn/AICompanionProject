from __future__ import annotations

import fnmatch
import json
import re
import subprocess
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

CONTEXT_FILE = Path.home() / ".bananalyzer_mcp_context.json"
WORKSPACE_FILE = Path.home() / ".bananalyzer_mcp_workspace.json"

IGNORE_PATTERNS = [
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".pytest_cache", ".mypy_cache", "dist", "build", ".next",
    ".turbo", "*.pyc", "*.pyo", ".DS_Store", ".env",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "*.egg-info", ".tox", ".nox", ".coverage",
]


class _MCPHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/v1/context":
            data = _load_context()
            self._send_json(200, data)
        elif self.path == "/v1/tree":
            data = _get_project_tree()
            self._send_json(200, data)
        elif self.path == "/health" or self.path == "/api/tags":
            self._send_json(200, {"status": "ok", "server": "bananalyzer-trae-mcp"})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path == "/v1/context":
            try:
                payload = self._read_body()
                _save_context(payload)
                self._send_json(200, {"ok": True, "stored": payload})
            except Exception as e:
                self._send_json(400, {"ok": False, "error": str(e)})
        elif self.path == "/v1/grep":
            try:
                payload = self._read_body()
                query = (payload or {}).get("query", "")
                max_results = (payload or {}).get("max_results", 20)
                results = _grep_codebase(query, max_results)
                self._send_json(200, {"ok": True, "query": query, "results": results})
            except Exception as e:
                self._send_json(400, {"ok": False, "error": str(e)})
        elif self.path == "/v1/file":
            try:
                payload = self._read_body()
                file_path = (payload or {}).get("path", "")
                data = _read_file(file_path)
                self._send_json(200, data)
            except Exception as e:
                self._send_json(400, {"ok": False, "error": str(e)})
        elif self.path == "/v1/workspace":
            try:
                payload = self._read_body()
                _save_workspace(payload)
                self._send_json(200, {"ok": True, "stored": payload})
            except Exception as e:
                self._send_json(400, {"ok": False, "error": str(e)})
        else:
            self._send_json(404, {"error": "not found"})

    def _read_body(self) -> dict[str, Any] | None:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return None
        body = self.rfile.read(length)
        return json.loads(body)

    def _send_json(self, status: int, data: dict[str, Any]) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        pass


def _get_workspace_root() -> Path | None:
    if WORKSPACE_FILE.exists():
        try:
            data = json.loads(WORKSPACE_FILE.read_text(encoding="utf-8"))
            root = data.get("workspace_root", "")
            if root:
                p = Path(root)
                if p.exists():
                    return p
        except Exception:
            pass
    return None


def _is_ignored(path: Path, root: Path) -> bool:
    rel = str(path.resolve().relative_to(root.resolve()))
    for pattern in IGNORE_PATTERNS:
        if fnmatch.fnmatch(path.name, pattern):
            return True
        if fnmatch.fnmatch(rel, pattern):
            return True
        if pattern in rel.split(path._flavour.sep) if hasattr(path, '_flavour') else pattern in str(rel).replace('\\', '/').split('/'):
            return True
    return False


def _should_skip(path: Path, root: Path) -> bool:
    return _is_ignored(path, root)


def _get_project_tree() -> dict[str, Any]:
    root = _get_workspace_root()
    if not root:
        return {"ok": False, "error": "No workspace root configured. Push workspace info first."}

    tree: list[str] = []
    try:
        for entry in sorted(root.rglob("*")):
            if _should_skip(entry, root):
                continue
            if entry.is_file():
                rel = entry.relative_to(root)
                tree.append(str(rel))
            if len(tree) > 300:
                tree.append("... (truncated)")
                break
    except Exception as e:
        return {"ok": False, "error": str(e)}

    return {"ok": True, "workspace_root": str(root), "file_count": len(tree), "tree": tree}


def _grep_codebase(query: str, max_results: int = 20) -> list[dict[str, Any]]:
    if not query:
        return []

    root = _get_workspace_root()
    if not root:
        return []

    results: list[dict[str, Any]] = []
    try:
        for entry in sorted(root.rglob("*")):
            if _should_skip(entry, root):
                continue
            if not entry.is_file():
                continue
            if len(results) >= max_results:
                break
            try:
                content = entry.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            if query.lower() not in content.lower():
                continue

            lines = content.splitlines()
            for i, line in enumerate(lines):
                if query.lower() in line.lower():
                    line_no = i + 1
                    snippet = line.strip()[:200]
                    rel = str(entry.relative_to(root))
                    results.append({
                        "file": rel,
                        "line": line_no,
                        "snippet": snippet,
                    })
                    if len(results) >= max_results:
                        break
    except Exception:
        pass

    return results


def _read_file(file_path: str) -> dict[str, Any]:
    if not file_path:
        return {"ok": False, "error": "No file path specified"}

    root = _get_workspace_root()
    if root:
        full_path = root / file_path
    else:
        full_path = Path(file_path)

    if not full_path.exists():
        return {"ok": False, "error": f"File not found: {file_path}"}

    try:
        content = full_path.read_text(encoding="utf-8", errors="replace")
        return {
            "ok": True,
            "file": file_path,
            "language": _guess_language(file_path),
            "content": content,
            "lines": len(content.splitlines()),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _guess_language(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    mapping = {
        ".py": "python", ".ts": "typescript", ".tsx": "typescriptreact",
        ".js": "javascript", ".jsx": "javascriptreact", ".go": "go",
        ".rs": "rust", ".cs": "csharp", ".java": "java", ".kt": "kotlin",
        ".swift": "swift", ".rb": "ruby", ".php": "php", ".vue": "vue",
        ".svelte": "svelte", ".html": "html", ".css": "css", ".scss": "scss",
        ".md": "markdown", ".json": "json", ".yaml": "yaml", ".yml": "yaml",
        ".toml": "toml", ".sh": "shell", ".ps1": "powershell", ".sql": "sql",
    }
    return mapping.get(ext, "")


def _save_workspace(payload: dict[str, Any]) -> None:
    payload["_timestamp"] = datetime.now().isoformat()
    WORKSPACE_FILE.parent.mkdir(parents=True, exist_ok=True)
    WORKSPACE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_context() -> dict[str, Any]:
    if CONTEXT_FILE.exists():
        try:
            return json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "file": "",
        "language": "",
        "selection": "",
        "_note": "No context pushed yet. Use POST /v1/context or 'bananalyzer mcp-push' to set context.",
        "_timestamp": datetime.now().isoformat(),
    }


def _save_context(payload: dict[str, Any]) -> None:
    payload["_timestamp"] = datetime.now().isoformat()
    CONTEXT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTEXT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_mcp_server(host: str = "127.0.0.1", port: int = 8001) -> None:
    server = HTTPServer((host, port), _MCPHandler)
    print(f"MCP server running on http://{host}:{port}")
    print(f"  GET  /v1/context  — current editor context")
    print(f"  POST /v1/context  — push editor context")
    print(f"  GET  /v1/tree     — project file tree")
    print(f"  POST /v1/grep     — search codebase")
    print(f"  POST /v1/file     — read a file from workspace")
    print(f"  POST /v1/workspace — set workspace root")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMCP server stopped.")
        server.shutdown()


def run_mcp_server_thread(host: str = "127.0.0.1", port: int = 8001) -> threading.Thread:
    server = HTTPServer((host, port), _MCPHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True, name="bananalyzer-mcp")
    thread.start()
    return thread


def push_context(
    file_path: str = "",
    language: str = "",
    selection: str = "",
    visible: str = "",
    content: str = "",
) -> None:
    payload: dict[str, Any] = {}
    if file_path:
        payload["file"] = file_path
    if language:
        payload["language"] = language
    if selection:
        payload["selection"] = selection
    elif visible:
        payload["visible"] = visible
    elif content:
        payload["content"] = content
    _save_context(payload)
    print(f"Context pushed: {payload}")


def push_workspace(workspace_root: str) -> None:
    payload = {"workspace_root": workspace_root}
    _save_workspace(payload)
    print(f"Workspace root set: {workspace_root}")


def search_codebase(query: str, max_results: int = 20) -> list[dict[str, Any]]:
    return _grep_codebase(query, max_results)


def get_project_tree() -> list[str]:
    data = _get_project_tree()
    return data.get("tree", []) if data.get("ok") else []


def read_project_file(file_path: str) -> str | None:
    data = _read_file(file_path)
    return data.get("content") if data.get("ok") else None

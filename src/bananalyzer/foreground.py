from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import sys
from typing import Any, Mapping

import psutil


@dataclass(frozen=True)
class ForegroundWindowInfo:
    hwnd: int | None
    pid: int | None
    title: str | None
    class_name: str | None
    process_name: str | None
    process_exe: str | None
    error: str | None = None


@dataclass(frozen=True)
class ForegroundActivityCandidate:
    category: str
    window: ForegroundWindowInfo


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def get_foreground_window_info(
    *,
    platform: str | None = None,
    win32gui_module: Any | None = None,
    win32process_module: Any | None = None,
) -> ForegroundWindowInfo:
    resolved_platform = platform or sys.platform
    if resolved_platform != "win32":
        return ForegroundWindowInfo(
            hwnd=None,
            pid=None,
            title=None,
            class_name=None,
            process_name=None,
            process_exe=None,
            error="unsupported_platform",
        )

    if win32gui_module is None or win32process_module is None:
        try:
            import win32gui as imported_win32gui
            import win32process as imported_win32process
        except Exception:
            return ForegroundWindowInfo(
                hwnd=None,
                pid=None,
                title=None,
                class_name=None,
                process_name=None,
                process_exe=None,
                error="pywin32_unavailable",
            )

        win32gui_module = imported_win32gui
        win32process_module = imported_win32process

    error: str | None = None
    try:
        hwnd = win32gui_module.GetForegroundWindow()
    except Exception:
        hwnd = 0
        error = "foreground_window_unavailable"

    if not hwnd:
        return ForegroundWindowInfo(
            hwnd=None,
            pid=None,
            title=None,
            class_name=None,
            process_name=None,
            process_exe=None,
            error=error,
        )

    try:
        _, pid = win32process_module.GetWindowThreadProcessId(hwnd)
    except Exception:
        pid = None

    try:
        title = _safe_str(win32gui_module.GetWindowText(hwnd))
    except Exception:
        title = None

    try:
        class_name = _safe_str(win32gui_module.GetClassName(hwnd))
    except Exception:
        class_name = None

    process_name = None
    process_exe = None
    if pid is not None:
        try:
            proc = psutil.Process(pid)
            process_name = _safe_str(proc.name())
            try:
                process_exe = _safe_str(proc.exe())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                process_exe = None
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            process_name = None
            process_exe = None

    return ForegroundWindowInfo(
        hwnd=int(hwnd),
        pid=pid,
        title=title,
        class_name=class_name,
        process_name=process_name,
        process_exe=process_exe,
        error=error,
    )


_DEFAULT_APP_CATEGORY_MAP: dict[str, str] = {
    "code.exe": "coding",
    "cursor.exe": "coding",
    "devenv.exe": "coding",
    "trae.exe" : "coding",
    "rider64.exe": "coding",
    "pycharm64.exe": "coding",
    "unity.exe": "coding",
    "steam.exe": "gaming",
    "pubg.exe": "gaming",
    "tslgame.exe": "gaming",
}


def _basename(path: str | None) -> str | None:
    if not path:
        return None
    try:
        return Path(path).name
    except Exception:
        return None


def _normalize_process_identifiers(window: ForegroundWindowInfo) -> list[str]:
    identifiers: list[str] = []
    for candidate in (window.process_name, _basename(window.process_exe)):
        if candidate:
            identifiers.append(candidate.strip().lower())
    return identifiers


def classify_foreground_activity(
    window: ForegroundWindowInfo,
    *,
    app_category_map: Mapping[str, str] | None = None,
) -> str:
    if app_category_map is not None:
        resolved_map = dict(app_category_map)
    else:
        from bananalyzer.config import load_settings_safe

        resolved_map = load_settings_safe().foreground_app_category_map or _DEFAULT_APP_CATEGORY_MAP
    for identifier in _normalize_process_identifiers(window):
        mapped = resolved_map.get(identifier)
        if mapped:
            return mapped
    return "unknown"


def detect_foreground_activity(
    *,
    app_category_map: Mapping[str, str] | None = None,
    platform: str | None = None,
    win32gui_module: Any | None = None,
    win32process_module: Any | None = None,
) -> ForegroundActivityCandidate:
    window = get_foreground_window_info(
        platform=platform,
        win32gui_module=win32gui_module,
        win32process_module=win32process_module,
    )
    category = classify_foreground_activity(window, app_category_map=app_category_map)
    return ForegroundActivityCandidate(category=category, window=window)


def _print_foreground_window_info() -> None:
    info = get_foreground_window_info()
    print(asdict(info))


if __name__ == "__main__":
    _print_foreground_window_info()

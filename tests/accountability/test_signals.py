from datetime import datetime

from bananalyzer.accountability.signals import DistractionSignals, DistractionResult
from bananalyzer.foreground import ForegroundActivityCandidate, ForegroundWindowInfo
from bananalyzer.config import Settings
import pytest


@pytest.fixture(autouse=True)
def mock_screenpipe_enabled(mocker):
    mocker.patch(
        "bananalyzer.accountability.signals.load_settings_safe",
        return_value=Settings(screenpipe_enabled=True)
    )


class FakeScreenpipeAdapter:
    def __init__(self, available, context_result=None):
        self._available = available
        self._context_result = context_result

    def is_available(self):
        return self._available

    def health_check(self):
        from bananalyzer.integrations.base import HealthCheckResult
        if self._available:
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
            last_error="Connection refused",
            degraded_mode=True,
        )

    def get_recent_context(self):
        if self._context_result:
            return self._context_result
        return {"ok": False, "signals": None, "error": {"message": "no context"}}


def _make_foreground_candidate(process_name="chrome.exe", error=None):
    return ForegroundActivityCandidate(
        category="unknown",
        window=ForegroundWindowInfo(
            hwnd=1,
            pid=2,
            title="Browser",
            class_name="Chrome_WidgetWin_1",
            process_name=process_name,
            process_exe=f"C:\\Program Files\\{process_name}",
            error=error,
        ),
    )


def test_classify_doomscroll_screenpipe_unavailable_falls_back_to_foreground(mocker):
    signals = DistractionSignals()
    mocker.patch.object(signals, "_check_screenpipe", return_value=False)
    signals.screenpipe_available = False
    mocker.patch(
        "bananalyzer.accountability.signals.detect_foreground_activity",
        return_value=_make_foreground_candidate("chrome.exe"),
    )

    result = signals.classify_doomscroll()

    assert isinstance(result, DistractionResult)
    assert result.degraded_mode is True
    assert result.source == "foreground_only"
    assert "browser_foreground" in result.reasons
    assert "screenpipe_unavailable" in result.reasons


def test_classify_doomscroll_foreground_failure_returns_safe_result(mocker):
    signals = DistractionSignals()
    mocker.patch.object(signals, "_check_screenpipe", return_value=False)
    signals.screenpipe_available = False
    mocker.patch(
        "bananalyzer.accountability.signals.detect_foreground_activity",
        side_effect=RuntimeError("detection failed"),
    )

    result = signals.classify_doomscroll()

    assert isinstance(result, DistractionResult)
    assert result.is_doomscroll is False
    assert result.confidence == 0.0
    assert result.degraded_mode is True
    assert result.source == "none"


def test_classify_doomscroll_with_screenpipe_available(mocker):
    signals = DistractionSignals()
    ssp = FakeScreenpipeAdapter(
        available=True,
        context_result={
            "ok": True,
            "signals": {
                "app_name": "chrome.exe",
                "window_title": "Twitter",
                "browser_url": "https://twitter.com/feed",
                "duration_seconds": 1200,
                "content_type": "social_media",
            },
            "error": None,
        },
    )
    mocker.patch.object(signals, "_check_screenpipe", return_value=True)
    signals.screenpipe = ssp

    result = signals.classify_doomscroll()

    assert result.is_doomscroll is True
    assert result.source == "screenpipe+foreground"
    assert result.degraded_mode is False
    assert "doomscroll_browser_url" in result.reasons


def test_classify_doomscroll_screenpipe_context_fails_falls_back(mocker):
    signals = DistractionSignals()
    ssp = FakeScreenpipeAdapter(
        available=True,
        context_result={"ok": False, "signals": None, "error": {"message": "timeout"}},
    )
    mocker.patch.object(signals, "_check_screenpipe", return_value=True)
    signals.screenpipe = ssp
    mocker.patch(
        "bananalyzer.accountability.signals.detect_foreground_activity",
        return_value=_make_foreground_candidate("chrome.exe"),
    )

    result = signals.classify_doomscroll()

    assert result.degraded_mode is True
    assert result.source == "foreground_only"


def test_classify_doomscroll_screenpipe_exception_falls_back(mocker):
    signals = DistractionSignals()
    ssp = FakeScreenpipeAdapter(available=True)
    mocker.patch.object(ssp, "get_recent_context", side_effect=RuntimeError("crash"))
    mocker.patch.object(signals, "_check_screenpipe", return_value=True)
    signals.screenpipe = ssp
    mocker.patch(
        "bananalyzer.accountability.signals.detect_foreground_activity",
        return_value=_make_foreground_candidate("msedge.exe"),
    )

    result = signals.classify_doomscroll()

    assert result.degraded_mode is True
    assert result.source == "foreground_only"


def test_classify_doomscroll_without_screenpipe_duration_under_threshold(mocker):
    signals = DistractionSignals()
    mocker.patch.object(signals, "_check_screenpipe", return_value=False)
    signals.screenpipe_available = False
    mocker.patch(
        "bananalyzer.accountability.signals.detect_foreground_activity",
        return_value=_make_foreground_candidate("chrome.exe"),
    )

    result = signals.classify_doomscroll()

    assert result.confidence < 0.5
    assert result.is_doomscroll is False
    assert "screenpipe_unavailable" in result.reasons


def test_classify_doomscroll_screenpipe_down_avoids_pretending_has_ocr(mocker):
    signals = DistractionSignals()
    mocker.patch.object(signals, "_check_screenpipe", return_value=False)
    signals.screenpipe_available = False
    mocker.patch(
        "bananalyzer.accountability.signals.detect_foreground_activity",
        return_value=_make_foreground_candidate("chrome.exe"),
    )

    result = signals.classify_doomscroll()

    assert result.degraded_mode is True
    assert result.source == "foreground_only"
    assert "screenpipe_unavailable" in result.reasons

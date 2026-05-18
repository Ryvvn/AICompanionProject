from __future__ import annotations

from datetime import datetime

from bananalyzer.integrations import ScreenpipeAdapter
from bananalyzer.foreground import detect_foreground_activity
from bananalyzer.config import load_thresholds_safe, load_settings_safe
from bananalyzer.events import emit_event


class DistractionSignals:
    def __init__(self) -> None:
        self.screenpipe_available: bool | None = None
        self.screenpipe = ScreenpipeAdapter()
        self._foreground_app_start: datetime | None = None
        self._foreground_app_key: str | None = None

    def _check_screenpipe(self) -> bool:
        settings = load_settings_safe()
        if not settings.screenpipe_enabled:
            self.screenpipe_available = False
            return False
            
        try:
            self.screenpipe_available = self.screenpipe.is_available()
        except Exception:
            self.screenpipe_available = False
        return self.screenpipe_available

    def _foreground_signal_strength(self, app_name: str) -> float:
        doomscroll_apps = {"chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "brave.exe"}
        if app_name.lower() in doomscroll_apps:
            return 0.4
        return 0.0

    def classify_doomscroll(self) -> DistractionResult:
        screenpipe_ok = self._check_screenpipe()

        thresholds = load_thresholds_safe()
        threshold_mins = thresholds.doomscrolling_threshold_mins

        if screenpipe_ok:
            return self._classify_with_screenpipe(threshold_mins)
        else:
            return self._classify_foreground_only(threshold_mins)

    def _classify_with_screenpipe(self, threshold_mins: int) -> DistractionResult:
        try:
            context = self.screenpipe.get_recent_context()
        except Exception:
            emit_event(
                event_type="integration.failed",
                component="screenpipe",
                severity="warning",
                message="Screenpipe context retrieval failed during doomscroll classification",
                details={},
            )
            self.screenpipe_available = False
            return self._classify_foreground_only(threshold_mins)

        if not context["ok"]:
            emit_event(
                event_type="integration.failed",
                component="screenpipe",
                severity="warning",
                message="Screenpipe returned error during doomscroll classification",
                details={"error": context.get("error", {}).get("message", "Unknown")},
            )
            self.screenpipe_available = False
            return self._classify_foreground_only(threshold_mins)

        signals = context.get("signals") or {}
        is_doomscroll = False
        confidence = 0.0
        reasons: list[str] = []

        browser_urls = {"twitter.com", "x.com", "reddit.com", "instagram.com", "tiktok.com", "youtube.com"}
        app_name = str(signals.get("app_name", "")).lower()
        browser_url = str(signals.get("browser_url", "")).lower()

        if any(domain in browser_url for domain in browser_urls):
            confidence += 0.4
            reasons.append("doomscroll_browser_url")

        if app_name in {"chrome.exe", "msedge.exe", "firefox.exe"}:
            confidence += 0.2
            reasons.append("browser_foreground")

        duration = signals.get("duration_seconds")
        if isinstance(duration, (int, float)) and duration >= threshold_mins * 60:
            confidence += 0.2
            reasons.append("duration_threshold_exceeded")
        elif isinstance(duration, (int, float)):
            confidence += 0.1
            reasons.append("duration_tracking")

        content_type = str(signals.get("content_type", "")).lower()
        if content_type in {"social_media", "scrolling", "feed"}:
            confidence += 0.2
            reasons.append("doomscroll_content_type")

        if confidence >= 0.5:
            is_doomscroll = True

        return DistractionResult(
            is_doomscroll=is_doomscroll,
            confidence=min(confidence, 1.0),
            reasons=reasons,
            degraded_mode=False,
            source="screenpipe+foreground",
        )

    def _classify_foreground_only(self, threshold_mins: int) -> DistractionResult:
        try:
            candidate = detect_foreground_activity()
        except Exception:
            return DistractionResult(
                is_doomscroll=False,
                confidence=0.0,
                reasons=["foreground_detection_failed"],
                degraded_mode=True,
                source="none",
            )

        app_name = (candidate.window.process_name or "unknown").lower()
        signal_strength = self._foreground_signal_strength(app_name)

        now = datetime.now()
        if self._foreground_app_key != app_name:
            self._foreground_app_start = now
            self._foreground_app_key = app_name

        duration = (now - self._foreground_app_start).total_seconds()
        duration_mins = duration / 60.0

        is_doomscroll = False
        confidence = 0.0
        reasons: list[str] = []

        if signal_strength > 0:
            reasons.append("browser_foreground")
            confidence += signal_strength

        if duration_mins >= threshold_mins:
            confidence += 0.3
            reasons.append("duration_threshold_exceeded")

        if confidence >= 0.5:
            is_doomscroll = True

        if self.screenpipe_available is False:
            reasons.append("screenpipe_unavailable")

        return DistractionResult(
            is_doomscroll=is_doomscroll,
            confidence=min(confidence, 1.0),
            reasons=reasons,
            degraded_mode=not self.screenpipe_available,
            source="foreground_only" if not self.screenpipe_available else "foreground",
        )


class DistractionResult:
    def __init__(
        self,
        *,
        is_doomscroll: bool,
        confidence: float,
        reasons: list[str],
        degraded_mode: bool,
        source: str,
    ):
        self.is_doomscroll = is_doomscroll
        self.confidence = confidence
        self.reasons = reasons
        self.degraded_mode = degraded_mode
        self.source = source

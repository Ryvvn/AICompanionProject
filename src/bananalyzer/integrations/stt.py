from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
import threading
from datetime import datetime
from pathlib import Path

from bananalyzer.config import load_settings_safe, Settings
from bananalyzer.events import emit_event
from .base import IntegrationAdapter, HealthCheckResult, AdapterResult

logger = logging.getLogger(__name__)


class STTAdapter(IntegrationAdapter):
    component_name: str = "stt"

    def __init__(self, settings: Settings | None = None):
        if settings is None:
            settings = load_settings_safe()
        self._stt_enabled = getattr(settings, "stt_enabled", False)
        self._executable_path = getattr(settings, "stt_executable_path", "whisper")
        self._model_path = getattr(settings, "stt_model_path", "")
        self._record_duration = getattr(settings, "stt_record_duration_seconds", 5)
        self._error_lock = threading.Lock()
        self._last_error: str | None = None

    def _resolve_executable(self) -> str | None:
        if not self._executable_path:
            return None
        if Path(self._executable_path).exists():
            return self._executable_path
        resolved = shutil.which(self._executable_path)
        return resolved

    def is_available(self) -> bool:
        if not self._stt_enabled:
            return False
        executable_ok = self._resolve_executable() is not None
        model_exists = bool(self._model_path) and Path(self._model_path).exists()
        return executable_ok and model_exists

    def health_check(self) -> HealthCheckResult:
        if not self._stt_enabled:
            return HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error="STT is disabled by configuration (stt_enabled: false)",
                degraded_mode=True,
            )

        resolved_exe = self._resolve_executable()
        if not resolved_exe:
            msg = f"STT executable not found at: {self._executable_path}"
            return HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=msg,
                degraded_mode=True,
            )

        if not self._model_path or not Path(self._model_path).exists():
            msg = f"STT model not found at: {self._model_path}"
            return HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=msg,
                degraded_mode=True,
            )

        return HealthCheckResult(
            available=True,
            status="available",
            last_check=datetime.now().isoformat(),
            degraded_mode=False,
        )

    def warmup(self) -> AdapterResult:
        if not self._stt_enabled:
            return AdapterResult(ok=False, data=None, error={"code": "stt_disabled", "message": "STT is disabled"})

        health = self.health_check()
        if not health.available:
            return AdapterResult(ok=False, data=None, error={"code": "stt_unavailable", "message": health.last_error or "STT unavailable"})

        try:
            exe = self._resolve_executable()
            subprocess.run(
                [exe, "--model", self._model_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return AdapterResult(ok=True, data=None, error=None)
        except Exception as e:
            return AdapterResult(ok=False, data=None, error={"code": "stt_warmup_error", "message": str(e)})

    def listen(self) -> AdapterResult:
        health = self.health_check()
        if not health.available:
            self._set_error(health.last_error)
            return AdapterResult(ok=False, data=None, error={"code": "stt_unavailable", "message": health.last_error or "STT unavailable"})

        audio_path = None

        try:
            audio_path = self._record_audio()
            if not audio_path:
                return AdapterResult(ok=False, data=None, error={"code": "stt_capture_failed", "message": "Audio capture failed"})

            exe = self._resolve_executable()
            cmd = [
                exe,
                "--model", self._model_path,
                "--file", audio_path,
                "--no-timestamps",
                "--output-txt",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else f"Whisper process exited with code {result.returncode}"
                self._set_error(error_msg)
                logger.error("STT subprocess failed: %s", error_msg)
                return AdapterResult(ok=False, data=None, error={"code": "stt_process_error", "message": error_msg})

            transcribed = result.stdout.strip()
            if not transcribed:
                transcribed = self._read_transcription_from_file(audio_path)

            if not transcribed:
                return AdapterResult(
                    ok=False,
                    data=None,
                    error={"code": "stt_empty_transcription", "message": "Whisper completed but no transcription text found"},
                )

            self._set_error(None)
            return AdapterResult(ok=True, data=transcribed, error=None)

        except FileNotFoundError:
            msg = f"STT executable not found: {self._executable_path}"
            self._set_error(msg)
            return AdapterResult(ok=False, data=None, error={"code": "stt_executable_not_found", "message": msg})
        except subprocess.TimeoutExpired:
            msg = "STT process timed out after 60 seconds"
            self._set_error(msg)
            return AdapterResult(ok=False, data=None, error={"code": "stt_timeout", "message": msg})
        except Exception as e:
            msg = f"Unexpected STT error: {e}"
            self._set_error(msg)
            logger.exception("Unexpected STT error")
            return AdapterResult(ok=False, data=None, error={"code": "stt_unexpected_error", "message": msg})
        finally:
            if audio_path:
                try:
                    Path(audio_path).unlink(missing_ok=True)
                except OSError:
                    pass

    def _set_error(self, msg: str | None) -> None:
        with self._error_lock:
            self._last_error = msg

    def _record_audio(self) -> str | None:
        try:
            try:
                import sounddevice as sd
            except ImportError:
                logger.warning("sounddevice not available; cannot capture audio")
                return None

            sample_rate = 16000
            duration = self._record_duration

            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="int16",
            )
            sd.wait()

            import soundfile as sf

            audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            audio_path = audio_file.name
            audio_file.close()

            sf.write(audio_path, recording, sample_rate)
            return audio_path

        except Exception as e:
            logger.exception("Audio capture failed: %s", e)
            return None

    def _read_transcription_from_file(self, audio_path: str) -> str | None:
        wav_base = audio_path
        if wav_base.endswith(".wav"):
            wav_base = wav_base[:-4]

        candidates = [
            f"{wav_base}.txt",
            f"{wav_base}.wav.txt",
        ]

        for candidate in candidates:
            candidate_path = Path(candidate)
            if candidate_path.exists():
                text = candidate_path.read_text(encoding="utf-8").strip()
                candidate_path.unlink(missing_ok=True)
                if text:
                    return text

        return None

    def listen_async(self, callback) -> None:
        def _run():
            result = self.listen()
            if result.ok:
                emit_event(
                    event_type="stt.transcribed",
                    component="stt",
                    severity="info",
                    message="Speech transcribed successfully",
                    details={"text_length": len(str(result.data)) if result.data else 0},
                )
            else:
                emit_event(
                    event_type="integration.failed",
                    component="stt",
                    severity="warning",
                    message=f"STT transcription failed: {result.error.get('message', 'Unknown') if result.error else 'Unknown'}",
                    details={"error": result.error},
                )
            callback(result)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

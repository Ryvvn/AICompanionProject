from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
import threading
from datetime import datetime
from pathlib import Path

import numpy as np

from bananalyzer.config import load_settings_safe, Settings
from bananalyzer.events import emit_event
from .base import IntegrationAdapter, HealthCheckResult, AdapterResult

logger = logging.getLogger(__name__)

_kokoro_instance_cache: dict[str, object] = {}
_kokoro_cache_lock = threading.Lock()


class TTSAdapter(IntegrationAdapter):
    component_name: str = "tts"

    def __init__(self, settings: Settings | None = None):
        if settings is None:
            settings = load_settings_safe()
        self._tts_enabled = getattr(settings, "tts_enabled", False)
        self._tts_engine = getattr(settings, "tts_engine", "kokoro")
        self._model_path = getattr(settings, "tts_voice_model_path", "")
        self._voices_path = getattr(settings, "tts_voices_path", "")
        self._voice_name = getattr(settings, "tts_voice", "af_heart")
        self._executable_path = getattr(settings, "tts_executable_path", "")
        self._error_lock = threading.Lock()
        self._speak_lock = threading.Lock()
        self._last_speak_error: str | None = None

    def _resolve_piper_executable(self) -> str | None:
        if not self._executable_path:
            return None
        if Path(self._executable_path).exists():
            return self._executable_path
        resolved = shutil.which(self._executable_path)
        return resolved

    def is_available(self) -> bool:
        if not self._tts_enabled:
            return False

        if self._tts_engine == "kokoro":
            return self._kokoro_is_available()
        if self._tts_engine == "piper":
            executable_ok = self._resolve_piper_executable() is not None
            voice_model_exists = bool(self._model_path) and Path(self._model_path).exists()
            return executable_ok and voice_model_exists
        return False

    def _kokoro_is_available(self) -> bool:
        try:
            from kokoro_onnx import Kokoro
            model_ok = bool(self._model_path) and Path(self._model_path).exists()
            voices_ok = bool(self._voices_path) and Path(self._voices_path).exists()
            return model_ok and voices_ok
        except ImportError:
            return False

    def health_check(self) -> HealthCheckResult:
        if not self._tts_enabled:
            return HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error="TTS is disabled by configuration (tts_enabled: false)",
                degraded_mode=True,
            )

        if self._tts_engine == "kokoro":
            return self._kokoro_health_check()
        if self._tts_engine == "piper":
            return self._subprocess_health_check()
        return HealthCheckResult(
            available=False,
            status="unavailable",
            last_check=datetime.now().isoformat(),
            last_error=f"Unsupported TTS engine: {self._tts_engine}",
            degraded_mode=True,
        )

    def _kokoro_health_check(self) -> HealthCheckResult:
        try:
            from kokoro_onnx import Kokoro
        except ImportError:
            msg = "kokoro_onnx package is not installed"
            return HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=msg,
                degraded_mode=True,
            )

        if not self._model_path or not Path(self._model_path).exists():
            msg = f"Kokoro model file not found at: {self._model_path}"
            return HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=msg,
                degraded_mode=True,
            )

        if not self._voices_path or not Path(self._voices_path).exists():
            msg = f"Kokoro voices file not found at: {self._voices_path}"
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

    def _subprocess_health_check(self) -> HealthCheckResult:
        resolved_exe = self._resolve_piper_executable()
        if not resolved_exe:
            msg = f"TTS executable not found at: {self._executable_path}"
            return HealthCheckResult(
                available=False,
                status="unavailable",
                last_check=datetime.now().isoformat(),
                last_error=msg,
                degraded_mode=True,
            )

        if not self._model_path or not Path(self._model_path).exists():
            msg = f"TTS voice model not found at: {self._model_path}"
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
        if not self._tts_enabled:
            return AdapterResult(ok=False, data=None, error={"code": "tts_disabled", "message": "TTS is disabled"})
        if self._tts_engine != "kokoro":
            return AdapterResult(ok=True, data=None, error=None)
        try:
            self._get_or_create_kokoro()
            return AdapterResult(ok=True, data=None, error=None)
        except Exception as e:
            return AdapterResult(ok=False, data=None, error={"code": "tts_warmup_error", "message": str(e)})

    def speak(self, text: str) -> AdapterResult:
        if not text or not text.strip():
            return AdapterResult(ok=False, data=None, error={"code": "tts_empty_text", "message": "No text provided to speak"})

        health = self.health_check()
        if not health.available:
            self._set_error(health.last_error)
            return AdapterResult(ok=False, data=None, error={"code": "tts_unavailable", "message": health.last_error or "TTS unavailable"})

        if not self._speak_lock.acquire(blocking=False):
            return AdapterResult(ok=False, data=None, error={"code": "tts_busy", "message": "TTS is currently speaking"})

        try:
            if self._tts_engine == "kokoro":
                return self._kokoro_speak(text)
            if self._tts_engine == "piper":
                return self._piper_speak(text)
            return AdapterResult(
                ok=False,
                data=None,
                error={"code": "tts_unsupported_engine", "message": f"Unsupported TTS engine: {self._tts_engine}"},
            )
        finally:
            self._speak_lock.release()

    def _get_or_create_kokoro(self):
        cache_key = f"{self._model_path}|{self._voices_path}"
        with _kokoro_cache_lock:
            if cache_key in _kokoro_instance_cache:
                return _kokoro_instance_cache[cache_key]

        from kokoro_onnx import Kokoro

        kokoro = Kokoro(self._model_path, self._voices_path)
        with _kokoro_cache_lock:
            _kokoro_instance_cache[cache_key] = kokoro
        return kokoro

    def _resolve_voice(self, kokoro):
        voice_str = self._voice_name

        if voice_str == "ashley_neuro":
            voice_str = "af_sky:50,af_sarah:50"

        if "," in voice_str:
            voices = []
            weights = []
            for pair in voice_str.split(","):
                if ":" in pair:
                    v, w = pair.strip().split(":")
                    voices.append(v.strip())
                    weights.append(float(w.strip()))
                else:
                    voices.append(pair.strip())
                    weights.append(50.0)

            if len(voices) != 2:
                raise ValueError(f"Voice blend requires exactly two voices, got: {voice_str}")

            supported = set(kokoro.get_voices())
            for v in voices:
                if v not in supported:
                    raise ValueError(f"Unsupported voice: {v}")

            total = sum(weights)
            if total != 100:
                weights = [w * (100 / total) for w in weights]

            style1 = kokoro.get_voice_style(voices[0])
            style2 = kokoro.get_voice_style(voices[1])
            blend = np.add(style1 * (weights[0] / 100), style2 * (weights[1] / 100))
            return blend

        return voice_str

    def _kokoro_speak(self, text: str) -> AdapterResult:
        audio_path: str | None = None

        try:
            import soundfile as sf

            kokoro = self._get_or_create_kokoro()
            voice = self._resolve_voice(kokoro)
            samples, sample_rate = kokoro.create(text, voice=voice, speed=1.0, lang="en-us")

            if self._voice_name == "ashley_neuro":
                import librosa
                samples = librosa.effects.pitch_shift(
                    np.array(samples), sr=sample_rate, n_steps=3,
                    res_type="soxr_hq", n_fft=512, hop_length=128,
                )

            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
                    audio_path = audio_file.name

                sf.write(audio_path, samples, sample_rate)

                subprocess.run(
                    ["powershell", "-c", f'(New-Object System.Media.SoundPlayer "{audio_path}").PlaySync();'],
                    capture_output=True,
                    timeout=120,
                    check=True,
                )
            except subprocess.TimeoutExpired:
                logger.warning("Audio playback timed out")
            except Exception as playback_error:
                logger.warning("Audio playback failed (TTS was generated): %s", playback_error)
                return AdapterResult(
                    ok=False,
                    data=None,
                    error={"code": "tts_playback_error", "message": f"TTS audio generated but playback failed: {playback_error}"},
                )
            finally:
                if audio_path:
                    try:
                        Path(audio_path).unlink(missing_ok=True)
                    except OSError:
                        pass

            self._set_error(None)
            return AdapterResult(ok=True, data=None, error=None)

        except Exception as e:
            msg = f"Kokoro TTS error: {e}"
            self._set_error(msg)
            logger.exception("Kokoro TTS error")
            return AdapterResult(ok=False, data=None, error={"code": "tts_kokoro_error", "message": msg})

    def _piper_speak(self, text: str) -> AdapterResult:
        text_path = None
        audio_path = None

        try:
            resolved_exe = self._resolve_piper_executable()

            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as text_file:
                text_file.write(text)
                text_path = text_file.name

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
                audio_path = audio_file.name

            cmd = [
                resolved_exe,
                "--model", self._model_path,
                "--output_file", audio_path,
            ]
            with open(text_path, "r", encoding="utf-8") as input_fh:
                result = subprocess.run(
                    cmd,
                    stdin=input_fh,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else f"TTS process exited with code {result.returncode}"
                self._set_error(error_msg)
                logger.error("TTS subprocess failed: %s", error_msg)
                return AdapterResult(ok=False, data=None, error={"code": "tts_process_error", "message": error_msg})

            try:
                subprocess.run(
                    ["powershell", "-c", f'(New-Object System.Media.SoundPlayer "{audio_path}").PlaySync();'],
                    capture_output=True,
                    timeout=60,
                    check=True,
                )
            except subprocess.TimeoutExpired:
                logger.warning("Audio playback timed out")
            except Exception as playback_error:
                logger.warning("Audio playback failed (TTS was generated): %s", playback_error)
                return AdapterResult(
                    ok=False,
                    data=None,
                    error={"code": "tts_playback_error", "message": f"TTS audio generated but playback failed: {playback_error}"},
                )

            self._set_error(None)
            return AdapterResult(ok=True, data=None, error=None)

        except FileNotFoundError:
            msg = f"TTS executable not found: {self._executable_path}"
            self._set_error(msg)
            logger.error(msg)
            return AdapterResult(ok=False, data=None, error={"code": "tts_executable_not_found", "message": msg})
        except subprocess.TimeoutExpired:
            msg = "TTS process timed out after 30 seconds"
            self._set_error(msg)
            logger.error(msg)
            return AdapterResult(ok=False, data=None, error={"code": "tts_timeout", "message": msg})
        except Exception as e:
            msg = f"Unexpected TTS error: {e}"
            self._set_error(msg)
            logger.exception("Unexpected TTS error")
            return AdapterResult(ok=False, data=None, error={"code": "tts_unexpected_error", "message": msg})
        finally:
            if text_path:
                try:
                    Path(text_path).unlink(missing_ok=True)
                except OSError:
                    pass
            if audio_path:
                try:
                    Path(audio_path).unlink(missing_ok=True)
                except OSError:
                    pass

    def _set_error(self, msg: str | None) -> None:
        with self._error_lock:
            self._last_speak_error = msg

    def speak_async(self, text: str) -> None:
        thread = threading.Thread(target=self._speak_and_log, args=(text,), daemon=True)
        thread.start()

    def _speak_and_log(self, text: str) -> None:
        result = self.speak(text)
        if result.ok:
            emit_event(
                event_type="tts.spoken",
                component="tts",
                severity="info",
                message="TTS response spoken successfully",
                details={},
            )
        else:
            emit_event(
                event_type="integration.failed",
                component="tts",
                severity="warning",
                message=f"TTS speak failed: {result.error.get('message', 'Unknown error') if result.error else 'Unknown error'}",
                details={"error": result.error},
            )

import sys
from datetime import datetime
from unittest.mock import MagicMock

from bananalyzer.integrations.tts import (
    TTSAdapter,
    _kokoro_instance_cache,
)
from bananalyzer.integrations.base import HealthCheckResult


def _make_mock_kokoro_onnx():
    import numpy as np
    mock_kokoro = MagicMock()
    mock_instance = MagicMock()
    mock_instance.create.return_value = (MagicMock(), 24000)
    mock_instance.get_voices.return_value = ["af_heart", "af_sarah", "af_sky", "am_adam"]
    mock_instance.get_voice_style.return_value = np.array([1.0, 2.0])
    mock_kokoro.Kokoro.return_value = mock_instance
    return mock_kokoro


class TestTTSAdapterHealthCheckKokoro:

    def test_health_check_disabled_by_config(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=False,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro-v1.0.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_executable_path="",
        ))

        adapter = TTSAdapter()
        result = adapter.health_check()

        assert result.available is False
        assert result.status == "unavailable"
        assert result.degraded_mode is True
        assert "disabled" in result.last_error.lower()

    def test_health_check_kokoro_onnx_not_installed(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro-v1.0.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_executable_path="",
        ))
        mocker.patch.dict(sys.modules, {"kokoro_onnx": None})

        adapter = TTSAdapter()
        result = adapter.health_check()

        assert result.available is False
        assert result.status == "unavailable"
        assert result.degraded_mode is True
        assert "not installed" in result.last_error.lower()

    def test_health_check_model_missing(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="kokoro",
            tts_voice_model_path="/missing/model.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_executable_path="",
        ))
        mock_kokoro = _make_mock_kokoro_onnx()
        mocker.patch.dict(sys.modules, {"kokoro_onnx": mock_kokoro})
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")

        def exists_side_effect():
            return False
        mock_path.return_value.exists.side_effect = exists_side_effect

        adapter = TTSAdapter()
        result = adapter.health_check()

        assert result.available is False
        assert result.status == "unavailable"

    def test_health_check_available(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro-v1.0.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_executable_path="",
        ))
        mock_kokoro = _make_mock_kokoro_onnx()
        mocker.patch.dict(sys.modules, {"kokoro_onnx": mock_kokoro})
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")
        mock_path.return_value.exists.return_value = True

        adapter = TTSAdapter()
        result = adapter.health_check()

        assert result.available is True
        assert result.status == "available"
        assert result.degraded_mode is False


class TestTTSAdapterIsAvailable:

    def test_is_available_when_disabled(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=False,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro-v1.0.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_executable_path="",
        ))

        adapter = TTSAdapter()
        assert adapter.is_available() is False

    def test_is_available_when_files_exist(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro-v1.0.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_executable_path="",
        ))
        mock_kokoro = _make_mock_kokoro_onnx()
        mocker.patch.dict(sys.modules, {"kokoro_onnx": mock_kokoro})
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")
        mock_path.return_value.exists.return_value = True

        adapter = TTSAdapter()
        assert adapter.is_available() is True

    def test_is_available_when_kokoro_onnx_not_installed(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro-v1.0.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_executable_path="",
        ))
        mocker.patch.dict(sys.modules, {"kokoro_onnx": None})

        adapter = TTSAdapter()
        assert adapter.is_available() is False


class TestTTSAdapterSpeakKokoro:

    def test_speak_empty_text(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro-v1.0.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_executable_path="",
        ))

        adapter = TTSAdapter()
        result = adapter.speak("   ")

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "tts_empty_text"

    def test_speak_when_unavailable(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=False,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro-v1.0.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_executable_path="",
        ))

        adapter = TTSAdapter()
        result = adapter.speak("Hello world")

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "tts_unavailable"

    def test_speak_success(self, mocker):
        _kokoro_instance_cache.clear()

        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro-v1.0.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_voice="af_heart",
            tts_executable_path="",
        ))
        mock_kokoro_onnx = _make_mock_kokoro_onnx()
        mocker.patch.dict(sys.modules, {"kokoro_onnx": mock_kokoro_onnx})
        mocker.patch.dict(sys.modules, {"soundfile": MagicMock()})
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")
        mock_path.return_value.exists.return_value = True

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0)

        adapter = TTSAdapter()
        result = adapter.speak("Hello world")

        assert result.ok is True
        assert result.data is None
        assert result.error is None
        assert mock_run.call_count == 1

    def test_speak_kokoro_create_error(self, mocker):
        _kokoro_instance_cache.clear()

        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro_error.onnx",
            tts_voices_path="/models/voices_error.bin",
            tts_voice="af_heart",
            tts_executable_path="",
        ))
        mock_kokoro_onnx = MagicMock()
        mock_instance = MagicMock()
        mock_instance.create.side_effect = RuntimeError("Model load failed")
        mock_kokoro_onnx.Kokoro.return_value = mock_instance
        mocker.patch.dict(sys.modules, {"kokoro_onnx": mock_kokoro_onnx})
        mocker.patch.dict(sys.modules, {"soundfile": MagicMock()})
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")
        mock_path.return_value.exists.return_value = True

        adapter = TTSAdapter()
        result = adapter.speak("Hello world")

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "tts_kokoro_error"
        assert "Model load failed" in result.error["message"]

    def test_speak_with_voice_blend(self, mocker):
        _kokoro_instance_cache.clear()

        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro-v1.0.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_voice="af_sarah:60,am_adam:40",
            tts_executable_path="",
        ))
        mock_kokoro_onnx = _make_mock_kokoro_onnx()
        mocker.patch.dict(sys.modules, {"kokoro_onnx": mock_kokoro_onnx})
        mocker.patch.dict(sys.modules, {"soundfile": MagicMock()})
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")
        mock_path.return_value.exists.return_value = True
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0)

        adapter = TTSAdapter()
        result = adapter.speak("Hello blended world")

        assert result.ok is True
        mock_instance = mock_kokoro_onnx.Kokoro.return_value
        blend_call = mock_instance.create.call_args
        blend_voice = blend_call[1]["voice"]
        import numpy as np
        assert isinstance(blend_voice, np.ndarray)

    def test_speak_playback_failure(self, mocker):
        _kokoro_instance_cache.clear()

        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro-v1.0.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_voice="af_heart",
            tts_executable_path="",
        ))
        mock_kokoro_onnx = _make_mock_kokoro_onnx()
        mocker.patch.dict(sys.modules, {"kokoro_onnx": mock_kokoro_onnx})
        mocker.patch.dict(sys.modules, {"soundfile": MagicMock()})
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")
        mock_path.return_value.exists.return_value = True

        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = RuntimeError("No audio device")

        adapter = TTSAdapter()
        result = adapter.speak("Hello world")

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "tts_playback_error"
        assert "No audio device" in result.error["message"]

    def test_speak_instance_cached_on_second_call(self, mocker):
        _kokoro_instance_cache.clear()

        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro_cache.onnx",
            tts_voices_path="/models/voices_cache.bin",
            tts_voice="af_heart",
            tts_executable_path="",
        ))
        mock_kokoro_onnx = MagicMock()
        mock_instance = MagicMock()
        mock_instance.create.return_value = (MagicMock(), 24000)
        mock_kokoro_onnx.Kokoro.return_value = mock_instance
        mocker.patch.dict(sys.modules, {"kokoro_onnx": mock_kokoro_onnx})
        mocker.patch.dict(sys.modules, {"soundfile": MagicMock()})
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")
        mock_path.return_value.exists.return_value = True
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0)

        adapter = TTSAdapter()
        adapter.speak("First call")
        adapter.speak("Second call")

        assert mock_kokoro_onnx.Kokoro.call_count == 1
        assert mock_instance.create.call_count == 2

    def test_warmup_preloads_kokoro_instance(self, mocker):
        _kokoro_instance_cache.clear()

        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro_warmup.onnx",
            tts_voices_path="/models/voices_warmup.bin",
            tts_executable_path="",
        ))
        mock_kokoro_onnx = _make_mock_kokoro_onnx()
        mocker.patch.dict(sys.modules, {"kokoro_onnx": mock_kokoro_onnx})
        mocker.patch.dict(sys.modules, {"soundfile": MagicMock()})
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")
        mock_path.return_value.exists.return_value = True

        adapter = TTSAdapter()
        result = adapter.warmup()

        assert result.ok is True
        mock_kokoro_onnx.Kokoro.assert_called_once()
        mock_kokoro_onnx.Kokoro.return_value.create.assert_not_called()

    def test_warmup_returns_false_when_disabled(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=False,
            tts_engine="kokoro",
            tts_voice_model_path="/models/kokoro-v1.0.onnx",
            tts_voices_path="/models/voices-v1.0.bin",
            tts_executable_path="",
        ))

        adapter = TTSAdapter()
        result = adapter.warmup()

        assert result.ok is False
        assert result.error["code"] == "tts_disabled"


class TestTTSAdapterSpeakPiper:

    def test_speak_piper_success(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="piper",
            tts_voice_model_path="/models/voice.onnx",
            tts_voices_path="",
            tts_executable_path="/usr/bin/piper",
        ))
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")
        mock_path.return_value.exists.return_value = True

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stderr="")

        adapter = TTSAdapter()
        result = adapter.speak("Hello world")

        assert result.ok is True
        assert result.data is None
        assert result.error is None
        assert mock_run.call_count == 2

    def test_speak_piper_subprocess_failure(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="piper",
            tts_voice_model_path="/models/voice.onnx",
            tts_voices_path="",
            tts_executable_path="/usr/bin/piper",
        ))
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")
        mock_path.return_value.exists.return_value = True

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=1, stderr="Synthesis failed")

        adapter = TTSAdapter()
        result = adapter.speak("Hello world")

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "tts_process_error"

    def test_speak_piper_executable_not_found(self, mocker):
        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="piper",
            tts_voice_model_path="/models/voice.onnx",
            tts_voices_path="",
            tts_executable_path="/usr/bin/piper",
        ))
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")
        mock_path.return_value.exists.return_value = True
        mocker.patch("subprocess.run", side_effect=FileNotFoundError("piper not found"))

        adapter = TTSAdapter()
        result = adapter.speak("Hello world")

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "tts_executable_not_found"

    def test_speak_piper_timeout(self, mocker):
        import subprocess as sp

        mocker.patch("bananalyzer.integrations.tts.load_settings_safe", return_value=mocker.Mock(
            tts_enabled=True,
            tts_engine="piper",
            tts_voice_model_path="/models/voice.onnx",
            tts_voices_path="",
            tts_executable_path="/usr/bin/piper",
        ))
        mock_path = mocker.patch("bananalyzer.integrations.tts.Path")
        mock_path.return_value.exists.return_value = True
        mocker.patch("subprocess.run", side_effect=sp.TimeoutExpired(cmd=["piper"], timeout=30))

        adapter = TTSAdapter()
        result = adapter.speak("Hello world")

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "tts_timeout"


class TestTTSAdapterIntegrationModeController:

    def test_tts_not_called_when_disabled(self, mocker):
        mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=mocker.Mock(state="companion"))
        mocker.patch("bananalyzer.mode_controller.generate_response", return_value="Hello there")
        mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
        mocker.patch("bananalyzer.mode_controller.get_memory_prompt_block", return_value="")

        mock_settings = mocker.patch("bananalyzer.mode_controller.load_settings_safe")
        mock_settings.return_value = mocker.Mock(tts_enabled=False, screenpipe_enabled=False)

        mock_tts = mocker.patch("bananalyzer.mode_controller.TTSAdapter")
        mock_instance = mock_tts.return_value

        from bananalyzer.mode_controller import process_user_message
        response = process_user_message("Hi")

        assert response == "Hello there"
        mock_instance.speak_async.assert_not_called()

    def test_text_response_returned_even_when_tts_unavailable(self, mocker):
        mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=mocker.Mock(state="companion"))
        mocker.patch("bananalyzer.mode_controller.generate_response", return_value="Hello there")
        mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
        mocker.patch("bananalyzer.mode_controller.get_memory_prompt_block", return_value="")

        mock_settings = mocker.patch("bananalyzer.mode_controller.load_settings_safe")
        mock_settings.return_value = mocker.Mock(tts_enabled=True, screenpipe_enabled=False)

        mock_tts = mocker.patch("bananalyzer.mode_controller.TTSAdapter")
        mock_instance = mock_tts.return_value
        mock_instance.is_available.return_value = False
        mock_instance.health_check.return_value = HealthCheckResult(
            available=False,
            status="unavailable",
            last_check=datetime.now().isoformat(),
            last_error="TTS not available",
            degraded_mode=True,
        )

        mocker.patch("bananalyzer.mode_controller.emit_event")

        from bananalyzer.mode_controller import process_user_message
        response = process_user_message("Hi")

        assert response == "Hello there"

    def test_tts_speak_async_called_when_available(self, mocker):
        mocker.patch("bananalyzer.mode_controller.get_current_state", return_value=mocker.Mock(state="companion"))
        mocker.patch("bananalyzer.mode_controller.generate_response", return_value="Hello there")
        mocker.patch("bananalyzer.mode_controller.upsert_integration_health")
        mocker.patch("bananalyzer.mode_controller.get_memory_prompt_block", return_value="")

        mock_settings = mocker.patch("bananalyzer.mode_controller.load_settings_safe")
        mock_settings.return_value = mocker.Mock(tts_enabled=True, screenpipe_enabled=False)

        mock_tts = mocker.patch("bananalyzer.mode_controller.TTSAdapter")
        mock_instance = mock_tts.return_value
        mock_instance.is_available.return_value = True
        mock_instance.speak_async = mocker.MagicMock()

        from bananalyzer.mode_controller import process_user_message
        response = process_user_message("Hi")

        assert response == "Hello there"
        mock_instance.speak_async.assert_called_once_with("Hello there")

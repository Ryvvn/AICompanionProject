import subprocess

from bananalyzer.integrations.stt import STTAdapter


class TestSTTAdapterHealthCheck:

    def test_health_check_disabled_by_config(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=False,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))

        adapter = STTAdapter()
        result = adapter.health_check()

        assert result.available is False
        assert result.status == "unavailable"
        assert result.degraded_mode is True
        assert "disabled" in result.last_error.lower()

    def test_health_check_executable_missing(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/nonexistent/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = False
        mocker.patch("shutil.which", return_value=None)

        adapter = STTAdapter()
        result = adapter.health_check()

        assert result.available is False
        assert result.status == "unavailable"
        assert result.degraded_mode is True
        assert "executable not found" in result.last_error.lower()

    def test_health_check_model_missing(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.side_effect = lambda: False
        mocker.patch("shutil.which", return_value=None)

        adapter = STTAdapter()
        result = adapter.health_check()

        assert result.available is False
        assert result.status == "unavailable"
        assert "executable not found" in result.last_error.lower() or "model not found" in result.last_error.lower()

    def test_health_check_available(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = True

        adapter = STTAdapter()
        result = adapter.health_check()

        assert result.available is True
        assert result.status == "available"
        assert result.degraded_mode is False


class TestSTTAdapterIsAvailable:

    def test_is_available_when_disabled(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=False,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))

        adapter = STTAdapter()
        assert adapter.is_available() is False

    def test_is_available_when_executable_and_model_exist(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = True

        adapter = STTAdapter()
        assert adapter.is_available() is True

    def test_is_available_with_path_based_executable(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/local/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = True

        adapter = STTAdapter()
        assert adapter.is_available() is True


class TestSTTAdapterListen:

    def test_listen_when_unavailable(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=False,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))

        adapter = STTAdapter()
        result = adapter.listen()

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "stt_unavailable"

    def test_listen_audio_capture_fails(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = True
        mocker.patch.object(STTAdapter, "_record_audio", return_value=None)

        adapter = STTAdapter()
        result = adapter.listen()

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "stt_capture_failed"

    def test_listen_success_stdout(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = True
        mocker.patch.object(STTAdapter, "_record_audio", return_value="/tmp/test_audio.wav")

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stderr="", stdout="Hello world")

        mocker.patch("pathlib.Path.unlink")

        adapter = STTAdapter()
        result = adapter.listen()

        assert result.ok is True
        assert result.data == "Hello world"
        assert result.error is None

    def test_listen_success_fallback_file(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = True
        mocker.patch.object(STTAdapter, "_record_audio", return_value="/tmp/test_audio.wav")

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stderr="", stdout="")

        mocker.patch.object(STTAdapter, "_read_transcription_from_file", return_value="Hello from file")
        mocker.patch("pathlib.Path.unlink")

        adapter = STTAdapter()
        result = adapter.listen()

        assert result.ok is True
        assert result.data == "Hello from file"

    def test_listen_subprocess_failure(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = True
        mocker.patch.object(STTAdapter, "_record_audio", return_value="/tmp/test_audio.wav")

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=1, stderr="Model load failed", stdout="")

        mocker.patch("pathlib.Path.unlink")

        adapter = STTAdapter()
        result = adapter.listen()

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "stt_process_error"
        assert "Model load failed" in result.error["message"]

    def test_listen_executable_not_found(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = True
        mocker.patch.object(STTAdapter, "_record_audio", return_value="/tmp/test_audio.wav")
        mocker.patch("subprocess.run", side_effect=FileNotFoundError("whisper not found"))

        mocker.patch("pathlib.Path.unlink")

        adapter = STTAdapter()
        result = adapter.listen()

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "stt_executable_not_found"

    def test_listen_timeout(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = True
        mocker.patch.object(STTAdapter, "_record_audio", return_value="/tmp/test_audio.wav")
        mocker.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=["whisper"], timeout=60))

        mocker.patch("pathlib.Path.unlink")

        adapter = STTAdapter()
        result = adapter.listen()

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "stt_timeout"

    def test_listen_empty_transcription(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = True
        mocker.patch.object(STTAdapter, "_record_audio", return_value="/tmp/test_audio.wav")

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stderr="", stdout="")

        mocker.patch.object(STTAdapter, "_read_transcription_from_file", return_value=None)
        mocker.patch("pathlib.Path.unlink")

        adapter = STTAdapter()
        result = adapter.listen()

        assert result.ok is False
        assert result.error is not None
        assert result.error["code"] == "stt_empty_transcription"

    def test_listen_cleans_up_temp_files(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_instance = mock_path.return_value
        mock_instance.exists.return_value = True
        mock_instance.unlink = mocker.MagicMock()
        mocker.patch.object(STTAdapter, "_record_audio", return_value="/tmp/test_audio.wav")

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stderr="", stdout="Hello world")

        adapter = STTAdapter()
        result = adapter.listen()

        assert result.ok is True

    def test_listen_cleans_up_temp_files_on_failure(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_instance = mock_path.return_value
        mock_instance.exists.return_value = True
        mock_instance.unlink = mocker.MagicMock()
        mocker.patch.object(STTAdapter, "_record_audio", return_value="/tmp/test_audio.wav")

        mocker.patch("subprocess.run", side_effect=RuntimeError("Unexpected failure"))

        adapter = STTAdapter()
        result = adapter.listen()

        assert result.ok is False


class TestSTTAdapterWarmup:

    def test_warmup_disabled(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=False,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))

        adapter = STTAdapter()
        result = adapter.warmup()

        assert result.ok is False
        assert result.error["code"] == "stt_disabled"

    def test_warmup_unavailable(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/nonexistent/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = False
        mocker.patch("shutil.which", return_value=None)

        adapter = STTAdapter()
        result = adapter.warmup()

        assert result.ok is False
        assert result.error["code"] == "stt_unavailable"

    def test_warmup_success(self, mocker):
        mocker.patch("bananalyzer.integrations.stt.load_settings_safe", return_value=mocker.Mock(
            stt_enabled=True,
            stt_executable_path="/usr/bin/whisper",
            stt_model_path="/models/ggml-base.en.bin",
            stt_record_duration_seconds=5,
        ))
        mock_path = mocker.patch("bananalyzer.integrations.stt.Path")
        mock_path.return_value.exists.return_value = True
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0)

        adapter = STTAdapter()
        result = adapter.warmup()

        assert result.ok is True

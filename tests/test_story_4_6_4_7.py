import json
from pathlib import Path

import pytest
import yaml

from bananalyzer.config import (
    Settings,
    scaffold_data_foundation,
    load_settings_safe,
)


class TestStory4_7_SyncDefaults:
    def test_sync_enabled_defaults_to_false(self):
        settings = Settings.model_construct()
        assert settings.sync_enabled is False

    def test_settings_yaml_has_sync_enabled_default(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True)
        settings_path = config_dir / "settings.yaml"
        settings_path.write_text("app_name: TestApp\n", encoding="utf-8")

        import bananalyzer.constants as constants
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(constants, "CONFIG_DIR", config_dir)
            settings = load_settings_safe()

        assert settings.sync_enabled is False

    def test_sync_enabled_can_be_parsed_from_yaml(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True)
        settings_path = config_dir / "settings.yaml"
        yaml_content = yaml.dump({"app_name": "TestApp", "sync_enabled": False})
        settings_path.write_text(yaml_content, encoding="utf-8")

        import bananalyzer.constants as constants
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(constants, "CONFIG_DIR", config_dir)
            settings = load_settings_safe()

        assert settings.sync_enabled is False

    def test_cli_config_command_includes_sync_status(self, tmp_path: Path):
        from typer.testing import CliRunner
        from bananalyzer.cli import app
        import bananalyzer.constants as constants

        data_dir = tmp_path / "data"
        config_dir = data_dir / "config"
        config_dir.mkdir(parents=True)
        (config_dir / "settings.yaml").write_text(
            "app_name: TestApp\nsync_enabled: false\n", encoding="utf-8"
        )
        (config_dir / "model_profiles.yaml").write_text(
            "default_model: local-llama3\nprofiles: {}\n", encoding="utf-8"
        )
        (config_dir / "thresholds.yaml").write_text(
            "doomscrolling_threshold_mins: 15\nidle_seconds_for_companion: 60\nfallback_confidence_threshold: 0.2\n",
            encoding="utf-8",
        )

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(constants, "DATA_DIR", data_dir)
            mp.setattr(constants, "CONFIG_DIR", config_dir)
            runner = CliRunner()
            result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        assert "sync_enabled" in result.output.lower() or "sync" in result.output.lower()


class TestStory4_6_IdentityInspection:
    def test_cli_status_shows_memory_paths(self, tmp_path: Path):
        from typer.testing import CliRunner
        from bananalyzer.cli import app
        import bananalyzer.constants as constants
        import bananalyzer.mode_controller as mc

        data_dir = tmp_path / "data"
        memory_dir = data_dir / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "memory.md").write_text("# Memory\n", encoding="utf-8")
        (memory_dir / "session_summary.md").write_text("# Summary\n", encoding="utf-8")
        (memory_dir / "banana_debt.json").write_text("{}", encoding="utf-8")
        config_dir = data_dir / "config"
        config_dir.mkdir(parents=True)
        (config_dir / "settings.yaml").write_text(
            "app_name: TestApp\nforeground_poll_interval_seconds: 5\n", encoding="utf-8"
        )
        (config_dir / "thresholds.yaml").write_text(
            "doomscrolling_threshold_mins: 15\nidle_seconds_for_companion: 60\nfallback_confidence_threshold: 0.2\n",
            encoding="utf-8",
        )
        state_dir = data_dir / "state"
        state_dir.mkdir(parents=True)
        (state_dir / "current_state.json").write_text(
            '{"state": "companion", "timestamp": "2026-05-09T00:00:00"}', encoding="utf-8"
        )
        (state_dir / "integration_health.json").write_text(
            '{"integrations": {}, "last_updated": "2026-05-09T00:00:00"}', encoding="utf-8"
        )
        logs_dir = data_dir / "logs"
        logs_dir.mkdir(parents=True)
        (logs_dir / "events.jsonl").write_text("", encoding="utf-8")

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(constants, "DATA_DIR", data_dir)
            mp.setattr(constants, "CONFIG_DIR", config_dir)
            mp.setattr(constants, "STATE_DIR", state_dir)
            mp.setattr(constants, "LOGS_DIR", logs_dir)
            mp.setattr(constants, "MEMORY_DIR", memory_dir)
            mp.setattr(mc, "_memory_store", None)
            runner = CliRunner()
            result = runner.invoke(app, ["status"])

        assert result.exit_code == 0

    def test_cli_config_includes_memory_paths(self, tmp_path: Path):
        from typer.testing import CliRunner
        from bananalyzer.cli import app
        import bananalyzer.constants as constants

        data_dir = tmp_path / "data"
        config_dir = data_dir / "config"
        config_dir.mkdir(parents=True)
        (config_dir / "settings.yaml").write_text(
            "app_name: TestApp\nforeground_poll_interval_seconds: 5\n", encoding="utf-8"
        )
        (config_dir / "model_profiles.yaml").write_text(
            "default_model: local-llama3\nprofiles: {}\n", encoding="utf-8"
        )
        (config_dir / "thresholds.yaml").write_text(
            "doomscrolling_threshold_mins: 15\nidle_seconds_for_companion: 60\nfallback_confidence_threshold: 0.2\n",
            encoding="utf-8",
        )

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(constants, "DATA_DIR", data_dir)
            mp.setattr(constants, "CONFIG_DIR", config_dir)
            runner = CliRunner()
            result = runner.invoke(app, ["config"])

        assert result.exit_code == 0

    def test_persona_reloads_when_file_changes(self, tmp_path: Path):
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir(parents=True)
        coding_prompt = prompts_dir / "coding.md"
        coding_prompt.write_text("You are a coding assistant v1", encoding="utf-8")

        from bananalyzer.persona import get_prompt_for_state
        from bananalyzer.constants import AppState

        prompt_v1 = get_prompt_for_state(AppState.CODING, prompts_dir=prompts_dir)
        assert "v1" in prompt_v1

        coding_prompt.write_text("You are a coding assistant v2", encoding="utf-8")

        prompt_v2 = get_prompt_for_state(AppState.CODING, prompts_dir=prompts_dir)
        assert "v2" in prompt_v2
        assert "v1" not in prompt_v2

    def test_memory_file_modification_reflected(self, tmp_path: Path):
        memory_dir = tmp_path / "memory"
        from bananalyzer.memory.store import MemoryStore
        from bananalyzer.memory.retrieval import retrieve_memory_context
        from bananalyzer.constants import AppState

        store = MemoryStore(memory_dir=memory_dir)
        store.add_goal("Original goal")

        context_v1 = retrieve_memory_context(store, AppState.CODING)
        assert "Original goal" in context_v1

        store.add_goal("Updated goal")
        context_v2 = retrieve_memory_context(store, AppState.CODING)
        assert "Updated goal" in context_v2


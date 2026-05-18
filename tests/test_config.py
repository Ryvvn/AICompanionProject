import json
from pathlib import Path
from unittest.mock import patch

import yaml
import pytest

from bananalyzer.config import (
    scaffold_data_foundation,
    Settings,
    ModelProfiles,
    Thresholds,
    load_settings_safe,
    load_thresholds_safe,
)
import bananalyzer.constants as constants

@pytest.fixture
def temp_data_dir(tmp_path: Path):
    """Fixture to mock data directories to a temporary path."""
    data_dir = tmp_path / "data"
    
    with patch.multiple(
        constants,
        DATA_DIR=data_dir,
        CONFIG_DIR=data_dir / "config",
        STATE_DIR=data_dir / "state",
        LOGS_DIR=data_dir / "logs",
        MEMORY_DIR=data_dir / "memory",
        PROMPTS_DIR=data_dir / "prompts",
    ):
        with patch.multiple(
            "bananalyzer.config",
            CONFIG_DIR=data_dir / "config",
            STATE_DIR=data_dir / "state",
            LOGS_DIR=data_dir / "logs",
            MEMORY_DIR=data_dir / "memory",
            PROMPTS_DIR=data_dir / "prompts",
        ):
            yield data_dir


def test_scaffold_data_foundation_creates_directories_and_files(temp_data_dir: Path):
    # Run the scaffold function
    scaffold_data_foundation()
    
    # Verify directories
    assert (temp_data_dir / "config").is_dir()
    assert (temp_data_dir / "state").is_dir()
    assert (temp_data_dir / "logs").is_dir()
    assert (temp_data_dir / "memory").is_dir()
    assert (temp_data_dir / "prompts").is_dir()

    # Verify YAML files
    settings_file = temp_data_dir / "config" / "settings.yaml"
    assert settings_file.is_file()
    with open(settings_file, "r") as f:
        settings = yaml.safe_load(f)
        assert settings["app_name"] == "Bananalyzer"

    model_profiles_file = temp_data_dir / "config" / "model_profiles.yaml"
    assert model_profiles_file.is_file()
    with open(model_profiles_file, "r") as f:
        profiles = yaml.safe_load(f)
        assert profiles["default_model"] == "local-llama3"

    thresholds_file = temp_data_dir / "config" / "thresholds.yaml"
    assert thresholds_file.is_file()
    with open(thresholds_file, "r") as f:
        thresholds = yaml.safe_load(f)
        assert thresholds["doomscrolling_threshold_mins"] == 15

    # Verify JSON files
    current_state_file = temp_data_dir / "state" / "current_state.json"
    assert current_state_file.is_file()
    with open(current_state_file, "r") as f:
        assert json.load(f) == {}

    health_file = temp_data_dir / "state" / "integration_health.json"
    assert health_file.is_file()
    with open(health_file, "r") as f:
        assert json.load(f) == {}

    banana_debt_file = temp_data_dir / "memory" / "banana_debt.json"
    assert banana_debt_file.is_file()
    with open(banana_debt_file, "r") as f:
        assert json.load(f) == {}

    # Verify empty/text files
    assert (temp_data_dir / "logs" / "app.log").is_file()
    assert (temp_data_dir / "logs" / "events.jsonl").is_file()
    assert (temp_data_dir / "memory" / "memory.md").is_file()
    assert (temp_data_dir / "memory" / "session_summary.md").is_file()

def test_settings_models_load_from_yaml(temp_data_dir: Path):
    scaffold_data_foundation()

    settings_path = temp_data_dir / "config" / "settings.yaml"
    thresholds_path = temp_data_dir / "config" / "thresholds.yaml"
    model_profiles_path = temp_data_dir / "config" / "model_profiles.yaml"

    old_settings_yaml = Settings.model_config.get("yaml_file")
    old_thresholds_yaml = Thresholds.model_config.get("yaml_file")
    old_model_profiles_yaml = ModelProfiles.model_config.get("yaml_file")

    Settings.model_config["yaml_file"] = settings_path
    Thresholds.model_config["yaml_file"] = thresholds_path
    ModelProfiles.model_config["yaml_file"] = model_profiles_path

    try:
        settings = Settings()
        thresholds = Thresholds()
        profiles = ModelProfiles()
        assert settings.app_name == "Bananalyzer"
        assert settings.foreground_poll_interval_seconds == 5
        assert thresholds.doomscrolling_threshold_mins == 15
        assert profiles.default_model == "local-llama3"
    finally:
        Settings.model_config["yaml_file"] = old_settings_yaml
        Thresholds.model_config["yaml_file"] = old_thresholds_yaml


def test_voice_settings_defaults():
    settings = Settings.model_construct()
    assert settings.stt_enabled is False
    assert settings.tts_enabled is False
    assert settings.stt_executable_path == "whisper"
    assert settings.tts_executable_path == ""
    assert settings.tts_voices_path == ""
    assert settings.tts_voice == "af_heart"
    assert settings.tts_engine == "kokoro"
    assert settings.stt_record_duration_seconds == 5


def test_tts_engine_validator():
    settings = Settings(tts_engine="kokoro", tts_enabled=False, stt_enabled=False)
    assert settings.tts_engine == "kokoro"

    settings_piper = Settings(tts_engine="PIPER", tts_enabled=False, stt_enabled=False)
    assert settings_piper.tts_engine == "piper"


def test_stt_record_duration_validator():
    settings = Settings.model_construct(stt_record_duration_seconds=10)
    assert settings.stt_record_duration_seconds == 10


def test_no_gpu_libraries_in_voice_code():
    gpu_libs = ["torch", "tensorflow", "cuda_python", "cupy", "jax"]
    for lib in gpu_libs:
        try:
            __import__(lib)
            found = True
        except ImportError:
            found = False
        assert not found, f"GPU library '{lib}' is installed — voice code paths should not require GPU"


def test_intervention_intensity_validates_allowed_values():
    thresholds = Thresholds(
        doomscrolling_threshold_mins=15,
        idle_seconds_for_companion=60,
        fallback_confidence_threshold=0.2,
        intervention_intensity="high",
    )
    assert thresholds.intervention_intensity == "high"

    thresholds_low = Thresholds(
        doomscrolling_threshold_mins=15,
        idle_seconds_for_companion=60,
        fallback_confidence_threshold=0.2,
        intervention_intensity="LOW",
    )
    assert thresholds_low.intervention_intensity == "low"

    with pytest.raises(ValueError):
        Thresholds(
            doomscrolling_threshold_mins=15,
            idle_seconds_for_companion=60,
            fallback_confidence_threshold=0.2,
            intervention_intensity="extreme",
        )


def test_intervention_cooldown_validates_positive():
    thresholds = Thresholds(
        doomscrolling_threshold_mins=15,
        idle_seconds_for_companion=60,
        fallback_confidence_threshold=0.2,
        intervention_cooldown_seconds=600,
    )
    assert thresholds.intervention_cooldown_seconds == 600


def test_banana_debt_ratios_are_defaulted():
    thresholds = Thresholds(
        doomscrolling_threshold_mins=15,
        idle_seconds_for_companion=60,
        fallback_confidence_threshold=0.2,
    )
    assert thresholds.banana_debt_coding_ratio == -1.0
    assert thresholds.banana_debt_gaming_ratio == 2.0
    assert thresholds.banana_debt_doomscroll_ratio == 3.0


def test_gaming_threshold_new_field_exists():
    thresholds = Thresholds(
        doomscrolling_threshold_mins=15,
        idle_seconds_for_companion=60,
        fallback_confidence_threshold=0.2,
    )
    assert thresholds.gaming_threshold_mins == 30


def test_safe_loaders_fall_back_on_invalid_yaml(temp_data_dir: Path):
    settings_path = temp_data_dir / "config" / "settings.yaml"
    thresholds_path = temp_data_dir / "config" / "thresholds.yaml"

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    thresholds_path.parent.mkdir(parents=True, exist_ok=True)

    settings_path.write_text("app_name: Bananalyzer\nforeground_poll_interval_seconds: 0\n", encoding="utf-8")
    thresholds_path.write_text("doomscrolling_threshold_mins: 0\n", encoding="utf-8")

    old_settings_yaml = Settings.model_config.get("yaml_file")
    old_thresholds_yaml = Thresholds.model_config.get("yaml_file")
    Settings.model_config["yaml_file"] = settings_path
    Thresholds.model_config["yaml_file"] = thresholds_path
    try:
        settings = load_settings_safe()
        thresholds = load_thresholds_safe()
        assert settings.foreground_poll_interval_seconds == 5
        assert thresholds.doomscrolling_threshold_mins == 15
    finally:
        Settings.model_config["yaml_file"] = old_settings_yaml
        Thresholds.model_config["yaml_file"] = old_thresholds_yaml

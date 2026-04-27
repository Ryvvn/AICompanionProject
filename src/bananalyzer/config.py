import json
import logging
from pathlib import Path
from typing import Tuple, Type

import yaml
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from bananalyzer.constants import (
    CONFIG_DIR,
    STATE_DIR,
    LOGS_DIR,
    MEMORY_DIR,
    PROMPTS_DIR,
)

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Main application settings"""
    app_name: str = "Bananalyzer"

    model_config = SettingsConfigDict(yaml_file=CONFIG_DIR / "settings.yaml")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)


class ModelProfiles(BaseSettings):
    """Model profiles configuration"""
    default_model: str = "local-llama3"

    model_config = SettingsConfigDict(yaml_file=CONFIG_DIR / "model_profiles.yaml")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)


class Thresholds(BaseSettings):
    """Thresholds configuration"""
    doomscrolling_threshold_mins: int = 15

    model_config = SettingsConfigDict(yaml_file=CONFIG_DIR / "thresholds.yaml")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)


def _create_yaml_if_not_exists(path: Path, default_content: dict):
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(default_content, f, default_flow_style=False)


def _create_json_if_not_exists(path: Path, default_content: dict):
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_content, f, indent=2)


def _create_file_if_not_exists(path: Path, content: str = ""):
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


def scaffold_data_foundation():
    """Create all required local data directories and default files."""
    # Create directories
    for directory in [CONFIG_DIR, STATE_DIR, LOGS_DIR, MEMORY_DIR, PROMPTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Config files
    _create_yaml_if_not_exists(CONFIG_DIR / "settings.yaml", {"app_name": "Bananalyzer"})
    _create_yaml_if_not_exists(CONFIG_DIR / "model_profiles.yaml", {"default_model": "local-llama3"})
    _create_yaml_if_not_exists(CONFIG_DIR / "thresholds.yaml", {"doomscrolling_threshold_mins": 15})
    
    # State files
    _create_json_if_not_exists(STATE_DIR / "current_state.json", {})
    _create_json_if_not_exists(STATE_DIR / "integration_health.json", {})
    
    # Log files
    _create_file_if_not_exists(LOGS_DIR / "app.log")
    _create_file_if_not_exists(LOGS_DIR / "events.jsonl")
    
    # Memory files
    _create_file_if_not_exists(MEMORY_DIR / "memory.md")
    _create_file_if_not_exists(MEMORY_DIR / "session_summary.md")
    _create_json_if_not_exists(MEMORY_DIR / "banana_debt.json", {})

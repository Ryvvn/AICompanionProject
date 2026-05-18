import json
import logging
from pathlib import Path
from typing import Tuple, Type

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
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
    foreground_poll_interval_seconds: int = 5
    memory_update_interval_seconds: int = 300
    sync_enabled: bool = False
    mcp_endpoint_url: str = "http://127.0.0.1:8000/v1/context"
    mcp_endpoints: dict[str, str] = Field(
        default_factory=lambda: {
            "trae.exe": "http://127.0.0.1:8001/v1/context",
            "code.exe": "http://127.0.0.1:8000/v1/context",
            "cursor.exe": "http://127.0.0.1:8002/v1/context",
            "devenv.exe": "http://127.0.0.1:8003/v1/context",
            "default": "http://127.0.0.1:8000/v1/context",
        }
    )
    screenpipe_enabled: bool = False
    screenpipe_endpoint_url: str = "http://127.0.0.1:3030"
    screenpipe_poll_interval_seconds: int = 10
    code_context_max_lines: int = 200
    code_context_max_chars: int = 8000
    foreground_app_category_map: dict[str, str] = Field(
        default_factory=lambda: {
            "code.exe": "coding",
            "cursor.exe": "coding",
            "devenv.exe": "coding",
            "rider64.exe": "coding",
            "pycharm64.exe": "coding",
            "unity.exe": "coding",
            "steam.exe": "gaming",
            "pubg.exe": "gaming",
            "tslgame.exe": "gaming",
        }
    )
    prompt_files: dict[str, str] = Field(
        default_factory=lambda: {
            "coding": "coding.md",
            "gaming": "gaming.md",
            "doomscrolling": "doomscroll.md",
            "companion": "companion.md",  
            "fallback": "fallback.md",
        }
    )
    ollama_base_url: str = "http://localhost:11434"
    ollama_request_timeout_seconds: int = 120
    tts_enabled: bool = False
    tts_engine: str = "kokoro"
    tts_voice_model_path: str = ""
    tts_voices_path: str = ""
    tts_voice: str = "af_heart"
    tts_executable_path: str = ""
    stt_enabled: bool = False
    stt_executable_path: str = "whisper"
    stt_model_path: str = ""
    stt_record_duration_seconds: int = 5

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
        return (init_settings, YamlConfigSettingsSource(settings_cls),)

    @field_validator("foreground_poll_interval_seconds")
    @classmethod
    def _validate_foreground_poll_interval_seconds(cls, v: int) -> int:
        if v < 1:
            raise ValueError("foreground_poll_interval_seconds must be >= 1")
        return v

    @field_validator("tts_engine")
    @classmethod
    def _validate_tts_engine(cls, v: str) -> str:
        allowed = {"piper", "kokoro"}
        if v.lower() not in allowed:
            raise ValueError(f"tts_engine must be one of: {allowed}")
        return v.lower()

    @field_validator("stt_record_duration_seconds")
    @classmethod
    def _validate_stt_record_duration_seconds(cls, v: int) -> int:
        if v < 1:
            raise ValueError("stt_record_duration_seconds must be >= 1")
        if v > 120:
            raise ValueError("stt_record_duration_seconds must be <= 120")
        return v

    @field_validator("ollama_base_url")
    @classmethod
    def _validate_ollama_base_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("ollama_base_url must not be empty")
        return v.strip()

    @field_validator("ollama_request_timeout_seconds")
    @classmethod
    def _validate_ollama_request_timeout_seconds(cls, v: int) -> int:
        if v < 1:
            raise ValueError("ollama_request_timeout_seconds must be >= 1")
        return v

    @field_validator("foreground_app_category_map")
    @classmethod
    def _normalize_foreground_app_category_map(cls, v: dict[str, str]) -> dict[str, str]:
        normalized: dict[str, str] = {}
        for key, value in (v or {}).items():
            if key is None or value is None:
                continue
            normalized[str(key).strip().lower()] = str(value).strip()
        return normalized

    @model_validator(mode="after")
    def _validate_voice_config(self):
        warnings = []
        if self.tts_enabled:
            if self.tts_engine == "kokoro":
                if not self.tts_voice_model_path or not Path(self.tts_voice_model_path).exists():
                    warnings.append(f"TTS (kokoro) is enabled but model file not found at: '{self.tts_voice_model_path}'")
                if not self.tts_voices_path or not Path(self.tts_voices_path).exists():
                    warnings.append(f"TTS (kokoro) is enabled but voices file not found at: '{self.tts_voices_path}'")
            elif self.tts_engine == "piper":
                if not self.tts_executable_path or not Path(self.tts_executable_path).exists():
                    warnings.append(f"TTS (piper) is enabled but executable not found at: '{self.tts_executable_path}'")
                if not self.tts_voice_model_path or not Path(self.tts_voice_model_path).exists():
                    warnings.append(f"TTS (piper) is enabled but voice model not found at: '{self.tts_voice_model_path}'")
        if self.stt_enabled:
            if not self.stt_executable_path or not Path(self.stt_executable_path).exists():
                warnings.append(f"STT is enabled but executable not found at: '{self.stt_executable_path}'")
            if not self.stt_model_path or not Path(self.stt_model_path).exists():
                warnings.append(f"STT is enabled but model not found at: '{self.stt_model_path}'")
        for warning in warnings:
            logger.warning(warning)
        return self
    

class ModelProfile(BaseModel):
    model: str
    temperature: float = 0.3
    context_limit: int | None = None


class ModelProfiles(BaseSettings):
    """Model profiles configuration"""
    default_model: str = "local-llama3"
    profiles: dict[str, ModelProfile] = Field(default_factory=dict)

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
        return (init_settings, YamlConfigSettingsSource(settings_cls),)


class Thresholds(BaseSettings):
    """Thresholds configuration"""
    doomscrolling_threshold_mins: int = 15
    gaming_threshold_mins: int = 30
    idle_seconds_for_companion: int = 60
    fallback_confidence_threshold: float = 0.2
    intervention_cooldown_seconds: int = 300
    intervention_intensity: str = "medium"
    banana_debt_coding_ratio: float = -1.0
    banana_debt_gaming_ratio: float = 2.0
    banana_debt_doomscroll_ratio: float = 3.0

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
        return (init_settings, YamlConfigSettingsSource(settings_cls),)

    @field_validator("doomscrolling_threshold_mins", "gaming_threshold_mins", "idle_seconds_for_companion", "intervention_cooldown_seconds")
    @classmethod
    def _validate_positive_ints(cls, v: int) -> int:
        if v < 1:
            raise ValueError("threshold must be >= 1")
        return v

    @field_validator("fallback_confidence_threshold")
    @classmethod
    def _validate_confidence_threshold(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("fallback_confidence_threshold must be between 0 and 1")
        return v

    @field_validator("intervention_intensity")
    @classmethod
    def _validate_intensity(cls, v: str) -> str:
        allowed = {"low", "medium", "high"}
        if v.lower() not in allowed:
            raise ValueError(f"intervention_intensity must be one of: {allowed}")
        return v.lower()


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
    _create_yaml_if_not_exists(
        CONFIG_DIR / "settings.yaml",
        {
            "app_name": "Bananalyzer",
            "foreground_poll_interval_seconds": 5,
            "mcp_endpoint_url": "http://127.0.0.1:8000/v1/context",
            "mcp_endpoints": {
                "trae.exe": "http://127.0.0.1:8001/v1/context",
                "code.exe": "http://127.0.0.1:8000/v1/context",
                "cursor.exe": "http://127.0.0.1:8002/v1/context",
                "devenv.exe": "http://127.0.0.1:8003/v1/context",
                "default": "http://127.0.0.1:8000/v1/context",
            },
            "screenpipe_enabled": False,
            "screenpipe_endpoint_url": "http://127.0.0.1:3030",
            "screenpipe_poll_interval_seconds": 10,
            "foreground_app_category_map": {
                "Code.exe": "coding",
                "Cursor.exe": "coding",
                "Unity.exe": "coding",
                "Steam.exe": "gaming",
                "PUBG.exe": "gaming",
            },
            "prompt_files": {
                "coding": "coding.md",
                "gaming": "gaming.md",
                "doomscrolling": "doomscroll.md",
                "companion": "companion.md",
                "fallback": "fallback.md",
            },
            "ollama_base_url": "http://localhost:11434",
            "ollama_request_timeout_seconds": 120,
            "tts_enabled": False,
            "tts_engine": "kokoro",
            "tts_voice_model_path": "",
            "tts_voices_path": "",
            "tts_voice": "af_heart",
            "tts_executable_path": "",
            "stt_enabled": False,
            "stt_executable_path": "whisper",
            "stt_model_path": "",
            "stt_record_duration_seconds": 5,
        },
    )
    _create_yaml_if_not_exists(
        CONFIG_DIR / "model_profiles.yaml",
        {
            "default_model": "local-llama3",
            "profiles": {
                "coding": {"model": "local-llama3", "temperature": 0.2, "context_limit": 8192},
                "gaming": {"model": "local-llama3", "temperature": 0.6, "context_limit": 2048},
                "doomscrolling": {"model": "local-llama3", "temperature": 0.4, "context_limit": 1024},
                "companion": {"model": "local-llama3", "temperature": 0.7, "context_limit": 2048},
                "fallback": {"model": "local-llama3", "temperature": 0.3, "context_limit": 2048},
            },
        },
    )
    _create_yaml_if_not_exists(
        CONFIG_DIR / "thresholds.yaml",
        {
            "doomscrolling_threshold_mins": 15,
            "gaming_threshold_mins": 30,
            "idle_seconds_for_companion": 60,
            "fallback_confidence_threshold": 0.2,
            "intervention_cooldown_seconds": 300,
            "intervention_intensity": "medium",
            "banana_debt_coding_ratio": -1.0,
            "banana_debt_gaming_ratio": 2.0,
            "banana_debt_doomscroll_ratio": 3.0,
        },
    )
    
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


def get_config_paths() -> dict[str, Path]:
    return {
        "settings_yaml": CONFIG_DIR / "settings.yaml",
        "model_profiles_yaml": CONFIG_DIR / "model_profiles.yaml",
        "thresholds_yaml": CONFIG_DIR / "thresholds.yaml",
        "prompts_dir": PROMPTS_DIR,
    }


def load_settings_safe() -> Settings:
    try:
        return Settings()
    except Exception as e:
        logger.warning("Failed to load settings.yaml, using safe defaults: %s", e)
        return Settings.model_construct()


def load_thresholds_safe() -> Thresholds:
    try:
        return Thresholds()
    except Exception as e:
        logger.warning("Failed to load thresholds.yaml, using safe defaults: %s", e)
        return Thresholds.model_construct()


def load_model_profiles_safe() -> ModelProfiles:
    try:
        return ModelProfiles()
    except Exception as e:
        logger.warning("Failed to load model_profiles.yaml, using safe defaults: %s", e)
        return ModelProfiles.model_construct()

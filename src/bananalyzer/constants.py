from pathlib import Path

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"

# Subdirectories
CONFIG_DIR = DATA_DIR / "config"
STATE_DIR = DATA_DIR / "state"
LOGS_DIR = DATA_DIR / "logs"
MEMORY_DIR = DATA_DIR / "memory"
PROMPTS_DIR = DATA_DIR / "prompts"

# Canonical State Values
class AppState:
    CODING = "coding"
    GAMING = "gaming"
    DOOMSCROLLING = "doomscrolling"
    COMPANION = "companion"
    FALLBACK = "fallback"

    @classmethod
    def all_states(cls) -> list[str]:
        return [cls.CODING, cls.GAMING, cls.DOOMSCROLLING, cls.COMPANION, cls.FALLBACK]

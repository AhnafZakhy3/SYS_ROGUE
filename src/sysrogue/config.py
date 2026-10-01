"""Global configuration and game constants for SYS//ROGUE."""

from dataclasses import dataclass
from pathlib import Path

SAVE_SCHEMA_VERSION = 1
DEFAULT_SAVE_DIR = Path("saves")
DEFAULT_SAVE_FILENAME = "quicksave.json"

# Resource limits & defaults
DEFAULT_MAX_INTEGRITY = 100
DEFAULT_STARTING_INTEGRITY = 100
DEFAULT_MAX_CPU = 10
DEFAULT_STARTING_CPU = 10
DEFAULT_MAX_RAM = 10
DEFAULT_STARTING_RAM = 0
DEFAULT_MAX_BANDWIDTH = 10
DEFAULT_STARTING_BANDWIDTH = 10
DEFAULT_STARTING_CREDITS = 25
DEFAULT_STARTING_TRACE = 0
MAX_TRACE = 100

# Base player attributes (1-10 scale)
DEFAULT_PROCESSING = 5
DEFAULT_MEMORY = 5
DEFAULT_NETWORK = 5
DEFAULT_REVERSE_ENG = 4
DEFAULT_STEALTH = 5

# Trace Thresholds for Security States
TRACE_SUSPICIOUS_THRESHOLD = 25
TRACE_ALERT_THRESHOLD = 50
TRACE_LOCKDOWN_THRESHOLD = 80
TRACE_TERMINATED_THRESHOLD = 100

# Procedural World Constraints
MIN_WORLD_NODES = 12
MAX_WORLD_NODES = 18

@dataclass(frozen=True)
class GameConfig:
    seed: int | None = None
    is_casual: bool = False
    is_debug: bool = False
    no_color: bool = False
    save_path: Path = DEFAULT_SAVE_DIR / DEFAULT_SAVE_FILENAME

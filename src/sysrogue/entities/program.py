"""In-game software / program entity for SYS//ROGUE."""

from dataclasses import dataclass, field
from typing import Any

@dataclass
class Program:
    id: str
    name: str
    description: str
    cpu_cost: int = 1
    ram_cost: int = 1
    bandwidth_cost: int = 0
    trace_impact: int = 0
    category: str = "utility"  # recon, stealth, exploit, utility
    is_resident: bool = False
    is_loaded: bool = False
    cooldown: int = 0
    cooldown_remaining: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

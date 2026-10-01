"""Upgrade / Hardware patch entity for SYS//ROGUE."""

from dataclasses import dataclass, field
from typing import Any

@dataclass
class Upgrade:
    id: str
    name: str
    category: str  # hardware, firmware, kernel, protocol
    cost: int
    description: str
    stat_modifiers: dict[str, int] = field(default_factory=dict)
    resource_max_modifiers: dict[str, int] = field(default_factory=dict)
    rarity: str = "common"  # common, uncommon, rare, prototype
    is_installed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

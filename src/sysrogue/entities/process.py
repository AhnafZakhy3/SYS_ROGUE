"""Simulated process entity on a node."""

from dataclasses import dataclass, field
from typing import Any

@dataclass
class SimulatedProcess:
    pid: int
    name: str
    process_type: str = "system"  # system, user, security, narrative, daemon
    description: str = ""
    security_risk: int = 0
    memory_cost: int = 1
    is_active: bool = True
    is_hunter: bool = False
    interactable: bool = True
    interaction_hint: str = "Inspect or kill process"
    metadata: dict[str, Any] = field(default_factory=dict)

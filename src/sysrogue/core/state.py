"""Central game state and run statistics data structures for SYS//ROGUE."""

from dataclasses import dataclass, field
from typing import Any
from sysrogue.core.events import SecurityState
from sysrogue.entities.player import PlayerProcess
from sysrogue.world.node import NetworkNode

@dataclass
class RunStatistics:
    turns_taken: int = 0
    nodes_discovered: int = 1
    nodes_explored: int = 1
    files_inspected: int = 0
    files_decrypted: int = 0
    checks_attempted: int = 0
    checks_succeeded: int = 0
    trace_generated: int = 0
    programs_used: int = 0
    upgrades_acquired: int = 0
    encounters_survived: int = 0
    credits_earned: int = 0

@dataclass
class Objective:
    id: str
    title: str
    description: str
    is_primary: bool = True
    is_completed: bool = False
    is_failed: bool = False

@dataclass
class GameState:
    seed: int
    turn: int = 1
    current_node_id: str = "GATEWAY-01"
    player: PlayerProcess = field(default_factory=PlayerProcess)
    nodes: dict[str, NetworkNode] = field(default_factory=dict)
    security_state: SecurityState = SecurityState.CLEAR
    objectives: list[Objective] = field(default_factory=list)
    narrative_flags: dict[str, bool] = field(default_factory=dict)
    event_log: list[str] = field(default_factory=list)
    stats: RunStatistics = field(default_factory=RunStatistics)
    run_status: str = "ACTIVE"  # ACTIVE, WON, TERMINATED, ABORTED
    termination_reason: str = ""
    is_casual: bool = False
    is_debug: bool = False

    @property
    def current_node(self) -> NetworkNode:
        return self.nodes[self.current_node_id]

    def log(self, message: str) -> None:
        """Adds a message to the visible log buffer."""
        self.event_log.append(message)
        if len(self.event_log) > 100:
            self.event_log.pop(0)

    def get_recent_logs(self, count: int = 6) -> list[str]:
        return self.event_log[-count:]

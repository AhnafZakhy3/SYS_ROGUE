"""Security state transitions, trace mechanics, and encounter manager."""

from enum import Enum
from dataclasses import dataclass, field
from sysrogue.config import (
    TRACE_SUSPICIOUS_THRESHOLD,
    TRACE_ALERT_THRESHOLD,
    TRACE_LOCKDOWN_THRESHOLD,
    TRACE_TERMINATED_THRESHOLD,
)
from sysrogue.core.rng import GameRNG
from sysrogue.content.catalogs import EncounterDefinition, get_default_encounters
from sysrogue.entities.player import PlayerProcess
from sysrogue.world.node import NetworkNode

class SecurityState(str, Enum):
    CLEAR = "CLEAR"
    SUSPICIOUS = "SUSPICIOUS"
    ALERT = "ALERT"
    LOCKDOWN = "LOCKDOWN"
    TERMINATED = "TERMINATED"

@dataclass
class EventOutcome:
    title: str
    message: str
    trace_change: int = 0
    integrity_change: int = 0
    cpu_change: int = 0
    bandwidth_change: int = 0
    credits_change: int = 0
    node_revealed: str | None = None

class SecurityManager:
    """Tracks trace and evaluates system-wide security alert state."""

    @staticmethod
    def evaluate_state(trace: int, player_alive: bool) -> SecurityState:
        if not player_alive or trace >= TRACE_TERMINATED_THRESHOLD:
            return SecurityState.TERMINATED
        if trace >= TRACE_LOCKDOWN_THRESHOLD:
            return SecurityState.LOCKDOWN
        if trace >= TRACE_ALERT_THRESHOLD:
            return SecurityState.ALERT
        if trace >= TRACE_SUSPICIOUS_THRESHOLD:
            return SecurityState.SUSPICIOUS
        return SecurityState.CLEAR

class EncounterManager:
    """Picks and resolves encounters based on location, depth, and player stats."""

    def __init__(self, rng: GameRNG, encounters: list[EncounterDefinition] | None = None) -> None:
        self.rng = rng
        self.encounters = encounters if encounters is not None else get_default_encounters()

    def roll_encounter(
        self, player: PlayerProcess, current_node: NetworkNode, base_chance: float = 0.25
    ) -> EventOutcome | None:
        # Passive evasion check from heuristic evader upgrade
        if "heuristic_evader" in player.upgrades and self.rng.random() < 0.35:
            return None

        # Increase encounter chance based on current node security level and trace
        effective_chance = base_chance + (current_node.security_level * 0.03) + (player.trace * 0.002)
        if self.rng.random() > effective_chance:
            return None

        # Filter applicable encounters
        candidates = [
            e for e in self.encounters
            if current_node.depth >= e.min_depth
            and (not e.allowed_nodes or current_node.node_type in e.allowed_nodes)
        ]
        if not candidates:
            return None

        weights = [c.weight for c in candidates]
        chosen: EncounterDefinition = self.rng.choice(candidates)

        return self.resolve_encounter(chosen, player, current_node)

    def resolve_encounter(
        self, encounter: EncounterDefinition, player: PlayerProcess, current_node: NetworkNode
    ) -> EventOutcome:
        if encounter.stat_to_check is None:
            # Automatic positive/neutral event like power surge
            cpu_gain = player.max_cpu - player.cpu
            player.cpu = player.max_cpu
            return EventOutcome(
                title=f"EVENT: {encounter.name}",
                message=encounter.success_msg,
                cpu_change=cpu_gain,
            )

        # Check stat
        res = player.check_stat(encounter.stat_to_check, encounter.difficulty, self.rng)
        if res.success:
            credits_reward = 20 if "salvage" in encounter.success_msg or "cache" in encounter.id else 0
            if credits_reward:
                player.credits += credits_reward
            return EventOutcome(
                title=f"EVENT: {encounter.name} [RESOLVED]",
                message=f"{res.description}\n{encounter.success_msg}",
                credits_change=credits_reward,
            )
        else:
            trace_add = 15 if "admin" in encounter.id or "hunter" in encounter.id else 10
            dmg = 15 if "daemon" in encounter.id else (5 if "leak" in encounter.id else 0)

            # Check sandbox upgrade protection
            if "sandbox" in player.programs and player.programs["sandbox"].is_loaded:
                player.programs["sandbox"].is_loaded = False
                return EventOutcome(
                    title=f"EVENT: {encounter.name} [SANDBOXED]",
                    message=f"{res.description}\nSandbox Isolator absorbed the event impact. No trace or damage occurred!",
                )

            player.add_trace(trace_add)
            player.take_damage(dmg)
            return EventOutcome(
                title=f"EVENT: {encounter.name} [FAILED]",
                message=f"{res.description}\n{encounter.fail_msg}",
                trace_change=trace_add,
                integrity_change=-dmg,
            )

"""Player process entity and stat management for SYS//ROGUE."""

from dataclasses import dataclass, field
from typing import Any
from sysrogue.config import (
    DEFAULT_PROCESSING,
    DEFAULT_MEMORY,
    DEFAULT_NETWORK,
    DEFAULT_REVERSE_ENG,
    DEFAULT_STEALTH,
    DEFAULT_STARTING_INTEGRITY,
    DEFAULT_MAX_INTEGRITY,
    DEFAULT_STARTING_CPU,
    DEFAULT_MAX_CPU,
    DEFAULT_STARTING_RAM,
    DEFAULT_MAX_RAM,
    DEFAULT_STARTING_BANDWIDTH,
    DEFAULT_MAX_BANDWIDTH,
    DEFAULT_STARTING_CREDITS,
    DEFAULT_STARTING_TRACE,
    MAX_TRACE,
)
from sysrogue.core.rng import GameRNG
from sysrogue.entities.program import Program
from sysrogue.entities.upgrade import Upgrade

@dataclass
class StatCheckResult:
    stat_name: str
    base_val: int
    modifiers: int
    effective_val: int
    roll: int
    total_score: int
    difficulty: int
    success: bool
    margin: int
    description: str

@dataclass
class PlayerProcess:
    pid: int = 417
    name: str = "SYS_PROBE"

    # Base Core Attributes (Ratings 1-10)
    processing: int = DEFAULT_PROCESSING
    memory_stat: int = DEFAULT_MEMORY
    network: int = DEFAULT_NETWORK
    reverse_eng: int = DEFAULT_REVERSE_ENG
    stealth: int = DEFAULT_STEALTH

    # Spendable / Allocatable Resource Pools
    integrity: int = DEFAULT_STARTING_INTEGRITY
    max_integrity: int = DEFAULT_MAX_INTEGRITY
    cpu: int = DEFAULT_STARTING_CPU
    max_cpu: int = DEFAULT_MAX_CPU
    ram_used: int = DEFAULT_STARTING_RAM
    max_ram: int = DEFAULT_MAX_RAM
    bandwidth: int = DEFAULT_STARTING_BANDWIDTH
    max_bandwidth: int = DEFAULT_MAX_BANDWIDTH
    trace: int = DEFAULT_STARTING_TRACE
    credits: int = DEFAULT_STARTING_CREDITS

    # Software & Hardware state
    programs: dict[str, Program] = field(default_factory=dict)
    upgrades: dict[str, Upgrade] = field(default_factory=dict)
    keyring: list[str] = field(default_factory=list)
    temporary_effects: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_alive(self) -> bool:
        return self.integrity > 0 and self.trace < MAX_TRACE

    def get_effective_stat(self, stat_name: str) -> int:
        stat_map = {
            "processing": self.processing,
            "memory": self.memory_stat,
            "network": self.network,
            "reverse_eng": self.reverse_eng,
            "stealth": self.stealth,
        }
        val = stat_map.get(stat_name.lower(), 5)
        # Apply upgrade modifiers
        for upgrade in self.upgrades.values():
            val += upgrade.stat_modifiers.get(stat_name.lower(), 0)
        # Apply temporary effects
        for effect in self.temporary_effects:
            val += effect.get("modifiers", {}).get(stat_name.lower(), 0)
        return max(1, val)

    def check_stat(
        self, stat_name: str, difficulty: int, rng: GameRNG, modifier: int = 0
    ) -> StatCheckResult:
        base_val = getattr(self, stat_name.lower(), 5)
        effective = self.get_effective_stat(stat_name) + modifier
        roll = rng.d20()
        total = effective + roll
        success = total >= difficulty
        margin = total - difficulty
        desc = (
            f"Check [{stat_name.upper()}]: Skill({effective}) + Roll({roll}) = {total} "
            f"vs DC({difficulty}) -> {'SUCCESS' if success else 'FAILURE'}"
        )
        return StatCheckResult(
            stat_name=stat_name,
            base_val=base_val,
            modifiers=effective - base_val,
            effective_val=effective,
            roll=roll,
            total_score=total,
            difficulty=difficulty,
            success=success,
            margin=margin,
            description=desc,
        )

    def consume_cpu(self, amount: int) -> bool:
        if self.cpu >= amount:
            self.cpu -= amount
            return True
        return False

    def consume_bandwidth(self, amount: int) -> bool:
        if self.bandwidth >= amount:
            self.bandwidth -= amount
            return True
        return False

    def add_trace(self, amount: int) -> int:
        # Check if dampener upgrade is present
        if "signal_dampener" in self.upgrades and amount > 0:
            amount = max(1, amount // 2)
        self.trace = min(MAX_TRACE, max(0, self.trace + amount))
        return self.trace

    def take_damage(self, amount: int) -> int:
        self.integrity = max(0, self.integrity - amount)
        return self.integrity

    def repair_integrity(self, amount: int) -> int:
        self.integrity = min(self.max_integrity, self.integrity + amount)
        return self.integrity

    def restore_turn_resources(self) -> None:
        """Regenerate basic resources per turn."""
        self.cpu = min(self.max_cpu, self.cpu + 2)
        self.bandwidth = min(self.max_bandwidth, self.bandwidth + 1)

    def install_upgrade(self, upgrade: Upgrade) -> None:
        self.upgrades[upgrade.id] = upgrade
        upgrade.is_installed = True
        # Apply resource max modifiers
        for res, mod in upgrade.resource_max_modifiers.items():
            if hasattr(self, res):
                setattr(self, res, getattr(self, res) + mod)

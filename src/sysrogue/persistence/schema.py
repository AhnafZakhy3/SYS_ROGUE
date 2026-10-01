"""JSON serialization schema and converters for SYS//ROGUE GameState."""

from typing import Any
from sysrogue.config import SAVE_SCHEMA_VERSION
from sysrogue.core.events import SecurityState
from sysrogue.core.state import GameState, Objective, RunStatistics
from sysrogue.entities.file import VirtualFile
from sysrogue.entities.player import PlayerProcess
from sysrogue.entities.process import SimulatedProcess
from sysrogue.entities.program import Program
from sysrogue.entities.upgrade import Upgrade
from sysrogue.world.node import NetworkNode

def serialize_state(state: GameState) -> dict[str, Any]:
    """Converts GameState into a JSON-compatible dictionary."""
    p = state.player
    return {
        "save_version": SAVE_SCHEMA_VERSION,
        "seed": state.seed,
        "turn": state.turn,
        "current_node_id": state.current_node_id,
        "security_state": state.security_state.value,
        "run_status": state.run_status,
        "termination_reason": state.termination_reason,
        "is_casual": state.is_casual,
        "narrative_flags": state.narrative_flags,
        "event_log": state.event_log,
        "stats": {
            "turns_taken": state.stats.turns_taken,
            "nodes_discovered": state.stats.nodes_discovered,
            "nodes_explored": state.stats.nodes_explored,
            "files_inspected": state.stats.files_inspected,
            "files_decrypted": state.stats.files_decrypted,
            "checks_attempted": state.stats.checks_attempted,
            "checks_succeeded": state.stats.checks_succeeded,
            "trace_generated": state.stats.trace_generated,
            "programs_used": state.stats.programs_used,
            "upgrades_acquired": state.stats.upgrades_acquired,
            "encounters_survived": state.stats.encounters_survived,
            "credits_earned": state.stats.credits_earned,
        },
        "player": {
            "pid": p.pid,
            "name": p.name,
            "processing": p.processing,
            "memory_stat": p.memory_stat,
            "network": p.network,
            "reverse_eng": p.reverse_eng,
            "stealth": p.stealth,
            "integrity": p.integrity,
            "max_integrity": p.max_integrity,
            "cpu": p.cpu,
            "max_cpu": p.max_cpu,
            "ram_used": p.ram_used,
            "max_ram": p.max_ram,
            "bandwidth": p.bandwidth,
            "max_bandwidth": p.max_bandwidth,
            "trace": p.trace,
            "credits": p.credits,
            "keyring": p.keyring,
            "programs": {
                k: {
                    "id": v.id,
                    "name": v.name,
                    "description": v.description,
                    "cpu_cost": v.cpu_cost,
                    "ram_cost": v.ram_cost,
                    "bandwidth_cost": v.bandwidth_cost,
                    "trace_impact": v.trace_impact,
                    "category": v.category,
                    "is_resident": v.is_resident,
                    "is_loaded": v.is_loaded,
                    "cooldown": v.cooldown,
                    "cooldown_remaining": v.cooldown_remaining,
                }
                for k, v in p.programs.items()
            },
            "upgrades": {
                k: {
                    "id": v.id,
                    "name": v.name,
                    "category": v.category,
                    "cost": v.cost,
                    "description": v.description,
                    "stat_modifiers": v.stat_modifiers,
                    "resource_max_modifiers": v.resource_max_modifiers,
                    "rarity": v.rarity,
                    "is_installed": v.is_installed,
                }
                for k, v in p.upgrades.items()
            },
            "temporary_effects": p.temporary_effects,
        },
        "nodes": {
            k: {
                "id": v.id,
                "name": v.name,
                "node_type": v.node_type,
                "security_level": v.security_level,
                "depth": v.depth,
                "connections": v.connections,
                "services": v.services,
                "is_discovered": v.is_discovered,
                "is_inspected": v.is_inspected,
                "is_compromised": v.is_compromised,
                "firewall_active": v.firewall_active,
                "firewall_bypass_key": v.firewall_bypass_key,
                "files": {
                    fk: {
                        "id": fv.id,
                        "name": fv.name,
                        "path": fv.path,
                        "file_type": fv.file_type,
                        "content": fv.content,
                        "is_encrypted": fv.is_encrypted,
                        "is_hidden": fv.is_hidden,
                        "decrypted_content": fv.decrypted_content,
                        "decrypt_difficulty": fv.decrypt_difficulty,
                        "key_required": fv.key_required,
                    }
                    for fk, fv in v.files.items()
                },
                "processes": [
                    {
                        "pid": pv.pid,
                        "name": pv.name,
                        "process_type": pv.process_type,
                        "description": pv.description,
                        "security_risk": pv.security_risk,
                        "memory_cost": pv.memory_cost,
                        "is_active": pv.is_active,
                        "is_hunter": pv.is_hunter,
                        "interactable": pv.interactable,
                    }
                    for pv in v.processes
                ],
            }
            for k, v in state.nodes.items()
        },
        "objectives": [
            {
                "id": o.id,
                "title": o.title,
                "description": o.description,
                "is_primary": o.is_primary,
                "is_completed": o.is_completed,
                "is_failed": o.is_failed,
            }
            for o in state.objectives
        ],
    }

def deserialize_state(data: dict[str, Any]) -> GameState:
    """Restores GameState from a serialized dictionary."""
    if data.get("save_version") != SAVE_SCHEMA_VERSION:
        raise ValueError(f"Incompatible save schema version: got {data.get('save_version')}, expected {SAVE_SCHEMA_VERSION}")

    pd = data["player"]
    player = PlayerProcess(
        pid=pd.get("pid", 417),
        name=pd.get("name", "SYS_PROBE"),
        processing=pd.get("processing", 5),
        memory_stat=pd.get("memory_stat", 5),
        network=pd.get("network", 5),
        reverse_eng=pd.get("reverse_eng", 4),
        stealth=pd.get("stealth", 5),
        integrity=pd.get("integrity", 100),
        max_integrity=pd.get("max_integrity", 100),
        cpu=pd.get("cpu", 10),
        max_cpu=pd.get("max_cpu", 10),
        ram_used=pd.get("ram_used", 0),
        max_ram=pd.get("max_ram", 10),
        bandwidth=pd.get("bandwidth", 10),
        max_bandwidth=pd.get("max_bandwidth", 10),
        trace=pd.get("trace", 0),
        credits=pd.get("credits", 25),
        keyring=pd.get("keyring", []),
        temporary_effects=pd.get("temporary_effects", []),
    )

    for k, v in pd.get("programs", {}).items():
        player.programs[k] = Program(**v)
    for k, v in pd.get("upgrades", {}).items():
        player.upgrades[k] = Upgrade(**v)

    nodes: dict[str, NetworkNode] = {}
    for nk, nv in data.get("nodes", {}).items():
        files: dict[str, VirtualFile] = {}
        for fk, fv in nv.get("files", {}).items():
            files[fk] = VirtualFile(**fv)

        processes = [SimulatedProcess(**pv) for pv in nv.get("processes", [])]

        nodes[nk] = NetworkNode(
            id=nv["id"],
            name=nv["name"],
            node_type=nv["node_type"],
            security_level=nv.get("security_level", 1),
            depth=nv.get("depth", 0),
            connections=nv.get("connections", []),
            services=nv.get("services", []),
            is_discovered=nv.get("is_discovered", False),
            is_inspected=nv.get("is_inspected", False),
            is_compromised=nv.get("is_compromised", False),
            firewall_active=nv.get("firewall_active", False),
            firewall_bypass_key=nv.get("firewall_bypass_key"),
            files=files,
            processes=processes,
        )

    objectives = [Objective(**ov) for ov in data.get("objectives", [])]
    sd = data.get("stats", {})
    stats = RunStatistics(**sd)

    return GameState(
        seed=data["seed"],
        turn=data.get("turn", 1),
        current_node_id=data.get("current_node_id", "GATEWAY-01"),
        player=player,
        nodes=nodes,
        security_state=SecurityState(data.get("security_state", "CLEAR")),
        objectives=objectives,
        narrative_flags=data.get("narrative_flags", {}),
        event_log=data.get("event_log", []),
        stats=stats,
        run_status=data.get("run_status", "ACTIVE"),
        termination_reason=data.get("termination_reason", ""),
        is_casual=data.get("is_casual", False),
    )

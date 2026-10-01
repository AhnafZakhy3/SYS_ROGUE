"""Mission objectives, victory condition checks, and run summary generation."""

from sysrogue.core.state import GameState, Objective

class ProgressionSystem:
    """Tracks run objectives, victory criteria, and end-of-run summaries."""

    @staticmethod
    def initialize_objectives() -> list[Objective]:
        return [
            Objective(
                id="extract_archive",
                title="Operation Silicon Heist",
                description="Infiltrate the network, locate the Quarantine Archive Vault (VAULT-CORE), decrypt 'nexus_core.enc', and safely extract via GATEWAY-01.",
                is_primary=True,
                is_completed=False,
            ),
            Objective(
                id="stealth_run",
                title="Ghost in the Shell (Optional)",
                description="Complete the extraction without triggering total system LOCKDOWN.",
                is_primary=False,
                is_completed=False,
            ),
        ]

    @staticmethod
    def show_objectives(state: GameState) -> str:
        lines = [
            "ACTIVE MISSION OBJECTIVES",
            "========================",
        ]
        for obj in state.objectives:
            tag = "[PRIMARY] " if obj.is_primary else "[OPTIONAL]"
            status = "[COMPLETED]" if obj.is_completed else ("[FAILED]" if obj.is_failed else "[IN PROGRESS]")
            lines.append(f"{tag} {status:<12} {obj.title}")
            lines.append(f"          {obj.description}")
        return "\n".join(lines)

    @staticmethod
    def check_victory_condition(state: GameState) -> bool:
        """Evaluates whether victory condition has been met."""
        if state.run_status != "ACTIVE":
            return state.run_status == "WON"

        # Check primary objective:
        # Decrypted archive + at GATEWAY-01
        has_decrypted = state.narrative_flags.get("archive_decrypted", False)
        at_gateway = state.current_node_id == "GATEWAY-01"

        if has_decrypted and at_gateway:
            for obj in state.objectives:
                if obj.id == "extract_archive":
                    obj.is_completed = True
                if obj.id == "stealth_run":
                    obj.is_completed = not state.narrative_flags.get("triggered_lockdown", False)

            state.run_status = "WON"
            state.log("MISSION ACCOMPLISHED: Nexus Core successfully exfiltrated via Perimeter Gateway!")
            return True

        return False

    @staticmethod
    def generate_summary(state: GameState) -> str:
        s = state.stats
        p = state.player
        outcome_title = "MISSION VICTORY: EXFILTRATION COMPLETE" if state.run_status == "WON" else "PROCESS TERMINATED (PERMADEATH)"
        lines = [
            "============================================================",
            f"   SYS//ROGUE — {outcome_title}",
            "============================================================",
            f"Run Seed:          {state.seed}",
            f"Total Turns:       {state.turn}",
            f"Run Status:        {state.run_status}",
            f"Exit Reason:       {state.termination_reason if state.run_status == 'TERMINATED' else 'Successful Exfiltration'}",
            "─" * 60,
            "PLAYER METRICS:",
            f"  Final Integrity: {p.integrity}/{p.max_integrity}",
            f"  Final Trace:     {p.trace}/100",
            f"  Credits Held:    {p.credits} CR",
            f"  Upgrades Held:   {len(p.upgrades)}",
            "─" * 60,
            "SYSTEM STATISTICS:",
            f"  Nodes Discovered:   {s.nodes_discovered}",
            f"  Nodes Explored:     {s.nodes_explored}",
            f"  Files Inspected:    {s.files_inspected}",
            f"  Files Decrypted:    {s.files_decrypted}",
            f"  Stat Checks Won:    {s.checks_succeeded} / {s.checks_attempted}",
            f"  Total Trace Accrued:{s.trace_generated}",
            f"  Programs Activated: {s.programs_used}",
            f"  Encounters Survived:{s.encounters_survived}",
            "============================================================",
            "Type `restart` to initiate a new run, or `quit` to exit.",
            "============================================================",
        ]
        return "\n".join(lines)

"""Process inspection and interaction system."""

from sysrogue.core.rng import GameRNG
from sysrogue.core.state import GameState

class ProcessSystem:
    """Manages process table inspection and process control."""

    @staticmethod
    def list_processes(state: GameState) -> str:
        curr = state.current_node
        if not curr.processes:
            return "No active processes reported on this node."

        lines = [f"PROCESS TABLE FOR {curr.id}:", "─" * 60]
        lines.append(f"{'PID':<6} {'NAME':<18} {'TYPE':<10} {'RISK':<6} {'STATUS':<8} {'DESCRIPTION'}")
        lines.append("─" * 60)
        for p in curr.processes:
            status = "RUNNING" if p.is_active else "TERMINATED"
            lines.append(f"{p.pid:<6} {p.name:<18} {p.process_type:<10} {p.security_risk:<6} {status:<8} {p.description}")
        return "\n".join(lines)

    @staticmethod
    def inspect_target(state: GameState, target_str: str) -> tuple[bool, str]:
        curr = state.current_node
        target = target_str.strip()

        # 1. Check if target is a PID or process name
        for p in curr.processes:
            if str(p.pid) == target or p.name.lower() == target.lower():
                lines = [
                    f"PROCESS DETAIL: PID {p.pid} — {p.name}",
                    "─" * 40,
                    f"Type:        {p.process_type}",
                    f"Description: {p.description}",
                    f"Status:      {'Active' if p.is_active else 'Halted'}",
                    f"Risk Rating: {p.security_risk}/10",
                    f"Hunter:      {'YES - Engages during Alerts' if p.is_hunter else 'No'}",
                    f"Action:      Use `interact {p.pid}` to manipulate.",
                ]
                return True, "\n".join(lines)

        # 2. Check if target is a file
        f = curr.get_file(target)
        if f:
            lines = [
                f"FILE DETAIL: {f.name}",
                "─" * 40,
                f"Path:        {f.path}",
                f"Type:        {f.file_type}",
                f"Encrypted:   {'YES' if f.is_encrypted else 'No'}",
                f"Action:      Use `cat {f.name}` to read or `decrypt {f.name}` to unlock.",
            ]
            return True, "\n".join(lines)

        # 3. Check if target is a service
        for svc in curr.services:
            if target.lower() in svc.lower():
                return True, f"SERVICE DETAIL: {svc} running on port {svc.split(':')[-1]}."

        return False, f"Target '{target_str}' not found in local processes, files, or services. Type `look` for an overview."

    @staticmethod
    def interact_process(state: GameState, target_str: str, rng: GameRNG) -> tuple[bool, str]:
        curr = state.current_node
        target = target_str.strip()

        matched_proc = None
        for p in curr.processes:
            if str(p.pid) == target or p.name.lower() == target.lower():
                matched_proc = p
                break

        if not matched_proc:
            return False, f"Process '{target_str}' not found on this host. Use `ps` to see running processes."

        if not matched_proc.is_active:
            return False, f"Process '{matched_proc.name}' is already terminated."

        # Interaction: Attempt to terminate/neutralize the process
        if not state.player.consume_cpu(2):
            return False, "Process manipulation requires at least 2 CPU cycles."

        difficulty = 10 + matched_proc.security_risk
        stat_name = "processing" if matched_proc.process_type == "system" else "stealth"

        state.stats.checks_attempted += 1
        res = state.player.check_stat(stat_name, difficulty, rng)

        if res.success:
            state.stats.checks_succeeded += 1
            matched_proc.is_active = False
            loot = 10 + (matched_proc.security_risk * 5)
            state.player.credits += loot
            return True, (
                f"INTERACTION SUCCESS: Terminated process PID {matched_proc.pid} ({matched_proc.name})!\n"
                f"{res.description}\nSiphoned {loot} credits from process memory space."
            )
        else:
            state.player.add_trace(8)
            state.stats.trace_generated += 8
            if matched_proc.is_hunter:
                state.player.take_damage(10)
                return False, (
                    f"COUNTER-ATTACK: Hunter daemon '{matched_proc.name}' retaliated!\n"
                    f"{res.description}\nIntegrity -10, Trace +8."
                )
            return False, f"INTERACTION FAILED: Process signal was dropped.\n{res.description}\nTrace +8."

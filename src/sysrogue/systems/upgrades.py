"""Software execution and hardware upgrade management."""

from sysrogue.content.catalogs import get_default_upgrades
from sysrogue.core.state import GameState

class UpgradeSystem:
    """Manages program activation, upgrade purchasing, and inventory inspection."""

    @staticmethod
    def show_inventory(state: GameState) -> str:
        p = state.player
        lines = [
            "PROCESS INVENTORY & RUNTIME MODULES",
            "===================================",
            f"Active Credits: {p.credits} CR  |  Keyring Tokens: {', '.join(p.keyring) if p.keyring else 'None'}",
            "",
            f"INSTALLED PROGRAMS ({len(p.programs)}):",
            "─" * 45,
        ]
        for prog in p.programs.values():
            status = f"[COOLDOWN {prog.cooldown_remaining}]" if prog.cooldown_remaining > 0 else "[READY]"
            loaded = " (RESIDENT ACTIVE)" if prog.is_loaded else ""
            lines.append(f"  {status:<14} {prog.id:<12} {prog.name}{loaded}")
            lines.append(f"                 Cost: CPU:{prog.cpu_cost} RAM:{prog.ram_cost} NET:{prog.bandwidth_cost}")
            lines.append(f"                 {prog.description}")

        lines.append("")
        lines.append(f"INSTALLED UPGRADES ({len(p.upgrades)}):")
        lines.append("─" * 45)
        if not p.upgrades:
            lines.append("  No hardware or firmware upgrades installed yet.")
        for upg in p.upgrades.values():
            lines.append(f"  [INSTALLED] {upg.name} ({upg.category.upper()})")
            lines.append(f"              {upg.description}")

        return "\n".join(lines)

    @staticmethod
    def run_program(state: GameState, prog_id: str) -> tuple[bool, str]:
        pid = prog_id.strip().lower()
        if pid not in state.player.programs:
            available = ", ".join(state.player.programs.keys())
            return False, f"Program '{prog_id}' is not in your installed programs. Available: {available}"

        prog = state.player.programs[pid]

        if prog.cooldown_remaining > 0:
            return False, f"Program '{prog.name}' is cooling down ({prog.cooldown_remaining} turns remaining)."

        # Check resource costs
        if state.player.cpu < prog.cpu_cost:
            return False, f"Insufficient CPU cycles (requires {prog.cpu_cost}, you have {state.player.cpu})."
        if state.player.bandwidth < prog.bandwidth_cost:
            return False, f"Insufficient Bandwidth (requires {prog.bandwidth_cost}, you have {state.player.bandwidth})."

        state.player.consume_cpu(prog.cpu_cost)
        state.player.consume_bandwidth(prog.bandwidth_cost)
        if prog.trace_impact != 0:
            state.player.add_trace(prog.trace_impact)
            if prog.trace_impact > 0:
                state.stats.trace_generated += prog.trace_impact

        state.stats.programs_used += 1

        # Execute effect
        if pid == "cleaner":
            prog.cooldown_remaining = 3
            return True, f"Executed {prog.name}: Scrubbed active connection headers! Trace reduced by 20 points."

        elif pid == "overclock":
            state.player.cpu = min(state.player.max_cpu, state.player.cpu + 6)
            state.player.take_damage(5)
            prog.cooldown_remaining = 4
            return True, f"Executed {prog.name}: Forced bus cycle burst! Restored 6 CPU, took 5 thermal integrity damage."

        elif pid == "debugger":
            state.player.temporary_effects.append({
                "name": "Debugger Hook",
                "duration": 3,
                "modifiers": {"reverse_eng": 3},
            })
            prog.cooldown_remaining = 4
            return True, f"Executed {prog.name}: Hooked kernel breakpoints! +3 Reverse Engineering for 3 turns."

        elif pid == "sandbox":
            prog.is_loaded = True
            prog.cooldown_remaining = 5
            return True, f"Executed {prog.name}: Sandbox Isolator armed. Next failure will be quarantined."

        elif pid == "sniffer":
            prog.is_loaded = not prog.is_loaded
            status_txt = "ACTIVATED (Zero-bandwidth hops enabled)" if prog.is_loaded else "DEACTIVATED"
            return True, f"{prog.name} resident mode: {status_txt}."

        elif pid == "memscanner":
            # Scans processes on current node for secrets
            secrets_found = []
            for p in state.current_node.processes:
                if p.is_active:
                    secrets_found.append(f"PID {p.pid} ({p.name}): Memory space clean.")
            # If current node has encrypted vault or files, reveal hint
            if state.current_node.firewall_bypass_key:
                state.player.keyring.append(state.current_node.firewall_bypass_key)
                secrets_found.append(f"CAPTURED AUTH KEY: '{state.current_node.firewall_bypass_key}' from memory!")
            prog.cooldown_remaining = 3
            return True, f"Memory Scanner completed analysis:\n" + "\n".join(secrets_found)

        return True, f"Program '{prog.name}' executed."

    @staticmethod
    def show_or_buy_upgrades(state: GameState, upgrade_id: str | None = None) -> tuple[bool, str]:
        catalog = get_default_upgrades()

        if not upgrade_id:
            # Display store
            lines = [
                "UNDERGROUND HARDWARE & FIRMWARE VENDOR",
                "=====================================",
                f"Your Balance: {state.player.credits} CR",
                "Use `upgrade <id>` to purchase and install an item.",
                "",
                f"{'ID':<18} {'NAME':<28} {'COST':<8} {'RARITY':<10} {'STATUS'}",
                "─" * 75,
            ]
            for uid, upg in catalog.items():
                is_owned = uid in state.player.upgrades
                status = "[INSTALLED]" if is_owned else f"{upg.cost} CR"
                lines.append(f"{uid:<18} {upg.name:<28} {status:<8} {upg.rarity:<10} {upg.description}")
            return True, "\n".join(lines)

        uid = upgrade_id.strip().lower()
        if uid not in catalog:
            return False, f"Unknown upgrade '{upgrade_id}'. Type `upgrade` without arguments to see the vendor catalog."

        if uid in state.player.upgrades:
            return False, f"Upgrade '{catalog[uid].name}' is already installed."

        target_upg = catalog[uid]
        if state.player.credits < target_upg.cost:
            return False, f"Insufficient credits! Requires {target_upg.cost} CR, you have {state.player.credits} CR."

        state.player.credits -= target_upg.cost
        state.player.install_upgrade(target_upg)
        state.stats.upgrades_acquired += 1
        return True, f"PURCHASE COMPLETE: Installed '{target_upg.name}'! {target_upg.description}"

"""Screen panels layout generator for SYS//ROGUE."""

from sysrogue.core.events import SecurityState
from sysrogue.core.state import GameState
from sysrogue.ui.themes import AnsiTheme, render_gauge

class PanelRenderer:
    """Renders composite terminal UI blocks."""

    @staticmethod
    def render_header(state: GameState, no_color: bool = False) -> str:
        c = AnsiTheme
        sec_color = c.GREEN
        if state.security_state == SecurityState.SUSPICIOUS:
            sec_color = c.YELLOW
        elif state.security_state in (SecurityState.ALERT, SecurityState.LOCKDOWN):
            sec_color = c.RED

        title = c.color("SYS//ROGUE v0.1", c.CYAN + c.BOLD, no_color)
        pid = c.color(f"PID {state.player.pid}", c.WHITE, no_color)
        seed_txt = c.color(f"SEED: {state.seed}", c.DIM, no_color)
        turn_txt = c.color(f"TURN: {state.turn}", c.WHITE, no_color)
        sec_txt = c.color(f"SECURITY: {state.security_state.value}", sec_color + c.BOLD, no_color)

        tl, tr, bl, br, hz, vt, tm = ("+", "+", "+", "+", "-", "|", "+") if no_color else ("┌", "┐", "└", "┘", "─", "│", "┬")
        ml, mr = ("+", "+") if no_color else ("├", "┤")

        return (
            f"{tl}{hz * 76}{tr}\n"
            f"{vt}  {title:<30} {pid:<14} {seed_txt:<16} {turn_txt:<10}  {vt}\n"
            f"{vt}  {sec_txt:<74}{vt}\n"
            f"{ml}{hz * 40}{tm}{hz * 35}{mr}"
        )

    @staticmethod
    def render_dashboard(state: GameState, no_color: bool = False) -> str:
        c = AnsiTheme
        p = state.player
        node = state.current_node
        vt = "|" if no_color else "│"
        hz = "-" if no_color else "─"
        ml, mr = ("+", "+") if no_color else ("├", "┤")

        # Left Column: Player Resources
        cpu_gauge = render_gauge(p.cpu, p.max_cpu, width=10, no_color=no_color)
        net_gauge = render_gauge(p.bandwidth, p.max_bandwidth, width=10, no_color=no_color)
        hp_gauge = render_gauge(p.integrity, p.max_integrity, width=10, no_color=no_color)
        tr_gauge = render_gauge(p.trace, 100, width=10, no_color=no_color)

        hp_color = c.GREEN if p.integrity > 50 else (c.YELLOW if p.integrity > 25 else c.RED)
        tr_color = c.GREEN if p.trace < 25 else (c.YELLOW if p.trace < 60 else c.RED)

        l1 = f"{vt} CPU        {cpu_gauge} {p.cpu:>2}/{p.max_cpu:<2} {vt}"
        l2 = f"{vt} BANDWIDTH  {net_gauge} {p.bandwidth:>2}/{p.max_bandwidth:<2} {vt}"
        l3 = f"{vt} INTEGRITY  {c.color(hp_gauge, hp_color, no_color)} {p.integrity:>3}/{p.max_integrity:<3}{vt}"
        l4 = f"{vt} TRACE      {c.color(tr_gauge, tr_color, no_color)} {p.trace:>3}/100 {vt}"
        l5 = f"{vt} CREDITS    {p.credits:>4} CR  RAM: {p.ram_used:>2}/{p.max_ram:<2}  {vt}"

        # Right Column: Current Node Info
        r1 = f" HOST:      {node.id} ({node.node_type})"
        r2 = f" NAME:      {node.name[:24]}"
        r3 = f" SECURITY:  Level {node.security_level}/10"
        r4 = f" FIREWALL:  {'LOCKED' if node.firewall_active else 'CLEAR'}"
        r5 = f" CONTENTS:  {len(node.files)} files | {len(node.processes)} procs"

        lines = [
            f"{l1:<41} {r1:<34}{vt}",
            f"{l2:<41} {r2:<34}{vt}",
            f"{l3:<41} {r3:<34}{vt}",
            f"{l4:<41} {r4:<34}{vt}",
            f"{l5:<41} {r5:<34}{vt}",
            f"{ml}{hz * 76}{mr}",
        ]
        return "\n".join(lines)

    @staticmethod
    def render_logs(state: GameState, count: int = 5, no_color: bool = False) -> str:
        c = AnsiTheme
        logs = state.get_recent_logs(count)
        log_header = c.color("SYSTEM LOG TELEMETRY", c.CYAN, no_color)
        vt = "|" if no_color else "│"
        hz = "-" if no_color else "─"
        bl, br = ("+", "+") if no_color else ("└", "┘")

        lines = [f"{vt}  {log_header:<74}{vt}"]
        for log in logs[-count:]:
            clean_log = log.replace("\n", " ")[:72]
            lines.append(f"{vt}  > {clean_log:<71}{vt}")

        # Fill empty lines if few logs
        for _ in range(count - len(logs)):
            lines.append(f"{vt}  {' ' * 74}{vt}")

        lines.append(f"{bl}{hz * 76}{br}")
        return "\n".join(lines)

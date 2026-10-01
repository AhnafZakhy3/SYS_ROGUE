"""Exploration system: scanning, looking, and map generation."""

from sysrogue.core.state import GameState

class ExplorationSystem:
    """Manages node discovery, scanning, and topological awareness."""

    @staticmethod
    def scan(state: GameState) -> tuple[bool, str]:
        """Scan adjacent connections from the current node."""
        if not state.player.consume_bandwidth(1) or not state.player.consume_cpu(1):
            return False, "Scan failed: insufficient CPU or Bandwidth (requires 1 CPU, 1 NET)."

        curr = state.current_node
        curr.is_inspected = True
        discovered_count = 0
        lines = [f"SCANNING LOCAL SUBNET FROM {curr.id} ({curr.name})...", "─" * 50]

        for conn_id in curr.connections:
            target = state.nodes.get(conn_id)
            if target:
                if not target.is_discovered:
                    target.is_discovered = True
                    state.stats.nodes_discovered += 1
                    discovered_count += 1
                lines.append(
                    f"[HOST] {target.id:<10} Type: {target.node_type:<12} Security: {target.security_level}/10  "
                    f"Firewall: {'LOCKED' if target.firewall_active else 'OPEN'}"
                )
                if target.services:
                    lines.append(f"       Services: {', '.join(target.services)}")

        state.player.add_trace(2)
        state.stats.trace_generated += 2
        lines.append("─" * 50)
        lines.append(f"Scan complete. {discovered_count} new host(s) discovered. Trace +2.")
        return True, "\n".join(lines)

    @staticmethod
    def look(state: GameState) -> str:
        """Inspect the current node in detail."""
        curr = state.current_node
        lines = [
            f"LOCATION: {curr.id} — {curr.name.upper()}",
            f"TYPE:     {curr.node_type} (Security Level: {curr.security_level}/10)",
            f"FIREWALL: {'ACTIVE (Blocked)' if curr.firewall_active else 'BYPASS/NONE'}",
            "─" * 50,
            "ADJACENT CONNECTIONS:",
        ]
        for conn_id in curr.connections:
            target = state.nodes.get(conn_id)
            if target and target.is_discovered:
                lines.append(f"  -> {target.id} ({target.name}) [Security: {target.security_level}]")
            else:
                lines.append(f"  -> {conn_id} (Discovered route, host unidentified)")

        lines.append("─" * 50)
        lines.append(f"VIRTUAL FILES ({len(curr.files)}):")
        for f in curr.files.values():
            lock = "[ENCRYPTED]" if f.is_encrypted else "[READABLE]"
            lines.append(f"  {lock:<12} {f.path}")

        lines.append("─" * 50)
        lines.append(f"RUNNING PROCESSES ({len(curr.processes)}):")
        for p in curr.processes:
            stat = "ACTIVE" if p.is_active else "HALTED"
            hunter = " [HUNTER]" if p.is_hunter else ""
            lines.append(f"  PID {p.pid:<4} {p.name:<18} {stat:<8} {p.description}{hunter}")

        return "\n".join(lines)

    @staticmethod
    def render_map(state: GameState) -> str:
        """Render an ASCII graph map of all discovered nodes."""
        lines = [
            "NETWORK TOPOLOGY MAP",
            "====================",
            "Legend: [*] Current Node  [+] Discovered Node  [!] High Security (7+)",
            "",
        ]

        # Group discovered nodes by depth
        depth_nodes: dict[int, list[str]] = {}
        for node in state.nodes.values():
            if node.is_discovered:
                depth_nodes.setdefault(node.depth, []).append(node.id)

        for depth in sorted(depth_nodes.keys()):
            lines.append(f"DEPTH {depth}:")
            node_entries = []
            for nid in depth_nodes[depth]:
                n = state.nodes[nid]
                marker = "*" if nid == state.current_node_id else ("!" if n.security_level >= 7 else "+")
                node_entries.append(f"[{marker}] {nid} ({n.node_type[:4]})")
            lines.append("   " + "   ".join(node_entries))

            # Show connections to next depth
            conn_lines = []
            for nid in depth_nodes[depth]:
                n = state.nodes[nid]
                forward_conns = [c for c in n.connections if state.nodes[c].is_discovered and state.nodes[c].depth > depth]
                if forward_conns:
                    conn_lines.append(f"   {nid} -> {', '.join(forward_conns)}")
            if conn_lines:
                lines.extend(conn_lines)
            lines.append("")

        return "\n".join(lines)

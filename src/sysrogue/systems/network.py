"""Network movement and connection traversal system."""

from sysrogue.core.rng import GameRNG
from sysrogue.core.state import GameState

class NetworkSystem:
    """Handles node hops, firewall bypass, and routing."""

    @staticmethod
    def connect_node(state: GameState, target_input: str, rng: GameRNG) -> tuple[bool, str]:
        curr = state.current_node
        target_id = target_input.strip().upper()

        # Find target node
        target = state.nodes.get(target_id)
        if not target:
            # Check by partial name match
            matches = [n for n in state.nodes.values() if target_id in n.id.upper() or target_id in n.name.upper()]
            if len(matches) == 1:
                target = matches[0]
                target_id = target.id
            else:
                return False, f"Unknown node '{target_input}'. Type `map` to inspect discovered topology."

        # Validate connection adjacency
        if target_id not in curr.connections:
            return False, f"Host '{target_id}' is not directly connected to '{curr.id}'. You can only hop to adjacent nodes."

        # Bandwidth cost
        bw_cost = 1
        if "sniffer" in state.player.programs and state.player.programs["sniffer"].is_loaded:
            bw_cost = 0  # Sniffer protocol optimizes route

        if not state.player.consume_bandwidth(bw_cost):
            return False, f"Connection failed: insufficient Bandwidth (requires {bw_cost} NET)."

        # Firewall Validation
        if target.firewall_active:
            # Check if player has ice_breaker upgrade
            if "ice_breaker" in state.player.upgrades and target.security_level <= 3:
                target.firewall_active = False
                state.log(f"[ICE BREAKER] Automatically breached low-level firewall on {target.id}.")
            # Check if player has keyring bypass token
            elif target.firewall_bypass_key and target.firewall_bypass_key in state.player.keyring:
                target.firewall_active = False
                state.log(f"[KEYRING] Firewall unlocked using security token {target.firewall_bypass_key}.")
            else:
                # Perform Network stat check to breach firewall
                difficulty = 10 + target.security_level
                res = state.player.check_stat("network", difficulty, rng)
                state.stats.checks_attempted += 1
                if res.success:
                    state.stats.checks_succeeded += 1
                    target.firewall_active = False
                    state.log(f"FIREWALL BREACHED: {res.description}")
                else:
                    state.player.add_trace(10)
                    state.stats.trace_generated += 10
                    return False, f"Connection rejected by firewall on '{target.id}'!\n{res.description}\nTrace +10."

        # Traversal successful
        state.current_node_id = target_id
        target.is_discovered = True
        if not target.is_inspected:
            target.is_inspected = True
            state.stats.nodes_explored += 1

        state.player.add_trace(1)
        state.stats.trace_generated += 1
        msg = f"Connected successfully to {target.id} ({target.name}). Current security level: {target.security_level}/10."
        return True, msg

"""Procedural world graph generation for SYS//ROGUE."""

from collections import deque
from sysrogue.core.rng import GameRNG
from sysrogue.world.node import NetworkNode
from sysrogue.world.templates import (
    create_gateway_node,
    create_workstation_node,
    create_database_node,
    create_fileserver_node,
    create_backupserver_node,
    create_adminpanel_node,
    create_monitor_node,
    create_research_node,
)

START_NODE_ID = "GATEWAY-01"
OBJECTIVE_NODE_ID = "VAULT-CORE"

class WorldGenerator:
    """Generates a connected, solvable network graph."""

    def __init__(self, rng: GameRNG) -> None:
        self.rng = rng

    def generate(self, total_nodes: int = 14) -> dict[str, NetworkNode]:
        nodes: dict[str, NetworkNode] = {}

        # 1. Starting node (Gateway-01)
        gw_files, gw_procs = create_gateway_node(START_NODE_ID, "Perimeter Gateway", depth=0, is_extraction=True)
        nodes[START_NODE_ID] = NetworkNode(
            id=START_NODE_ID,
            name="Perimeter Gateway",
            node_type="gateway",
            security_level=1,
            depth=0,
            files=gw_files,
            processes=gw_procs,
            services=["ssh:22", "dns:53"],
            is_discovered=True,
            is_inspected=True,
        )

        # 2. Layered structure to guarantee solvable progression
        # Layers:
        # Layer 0: Gateway-01
        # Layer 1: 2-3 nodes (Workstations / File servers)
        # Layer 2: 3-4 nodes (Databases / Backups / Monitors)
        # Layer 3: 2-3 nodes (Admin panels / Research servers)
        # Layer 4: Objective Node (Vault-Core)
        layer_counts = [1, 3, 4, 3, 1]
        archetypes_pool = [
            "workstation", "database", "fileserver", "backupserver",
            "adminpanel", "monitor", "research"
        ]

        layers: list[list[str]] = [[START_NODE_ID]]
        node_counter = 1

        for depth in range(1, 4):
            count = layer_counts[depth]
            current_layer: list[str] = []
            for _ in range(count):
                node_id = f"NODE-{node_counter:02d}"
                node_counter += 1
                node_type = self.rng.choice(archetypes_pool)
                sec_level = min(9, depth * 2 + self.rng.randint(0, 1))

                files, procs = self._create_archetype_content(node_id, node_type, depth)

                node = NetworkNode(
                    id=node_id,
                    name=f"{node_type.capitalize()} #{node_counter}",
                    node_type=node_type,
                    security_level=sec_level,
                    depth=depth,
                    files=files,
                    processes=procs,
                    services=self._generate_services(node_type),
                    is_discovered=False,
                )
                nodes[node_id] = node
                current_layer.append(node_id)
            layers.append(current_layer)

        # Add Objective Vault Node at depth 4
        vault_files, vault_procs = create_research_node(OBJECTIVE_NODE_ID, "Quarantine Archive Vault", depth=4, is_target_vault=True)
        nodes[OBJECTIVE_NODE_ID] = NetworkNode(
            id=OBJECTIVE_NODE_ID,
            name="Quarantine Archive Vault",
            node_type="research",
            security_level=8,
            depth=4,
            files=vault_files,
            processes=vault_procs,
            services=["vault-auth:8443", "quarantine-ctl:9000"],
            is_discovered=False,
            firewall_active=True,
            firewall_bypass_key="MASTER_ACCESS_KEY_0x99AAFF",
        )
        layers.append([OBJECTIVE_NODE_ID])

        # 3. Connect layers to guarantee a forward DAG backbone
        for d in range(len(layers) - 1):
            curr_layer = layers[d]
            next_layer = layers[d + 1]

            # Ensure every node in curr connects to at least one in next
            for u in curr_layer:
                v = self.rng.choice(next_layer)
                self._connect_nodes(nodes[u], nodes[v])

            # Ensure every node in next connects to at least one in curr
            for v in next_layer:
                if not any(u in nodes[v].connections for u in curr_layer):
                    u = self.rng.choice(curr_layer)
                    self._connect_nodes(nodes[u], nodes[v])

        # 4. Add lateral cross-connections within same layer for exploration richness
        for d in range(1, len(layers) - 1):
            curr_layer = layers[d]
            if len(curr_layer) > 1:
                for i in range(len(curr_layer)):
                    j = (i + 1) % len(curr_layer)
                    if self.rng.random() < 0.6:
                        self._connect_nodes(nodes[curr_layer[i]], nodes[curr_layer[j]])

        # 5. Verify connectivity via BFS (Solvability assertion)
        assert self.is_solvable(nodes), "Generated network world graph must be connected and solvable!"

        return nodes

    def _connect_nodes(self, node_a: NetworkNode, node_b: NetworkNode) -> None:
        node_a.add_connection(node_b.id)
        node_b.add_connection(node_a.id)

    def _create_archetype_content(self, node_id: str, node_type: str, depth: int):
        if node_type == "workstation":
            return create_workstation_node(node_id, node_type, depth, self.rng)
        elif node_type == "database":
            return create_database_node(node_id, node_type, depth, self.rng)
        elif node_type == "fileserver":
            return create_fileserver_node(node_id, node_type, depth, self.rng)
        elif node_type == "backupserver":
            return create_backupserver_node(node_id, node_type, depth, self.rng)
        elif node_type == "adminpanel":
            return create_adminpanel_node(node_id, node_type, depth, self.rng)
        elif node_type == "monitor":
            return create_monitor_node(node_id, node_type, depth, self.rng)
        else:
            return create_research_node(node_id, node_type, depth, is_target_vault=False)

    def _generate_services(self, node_type: str) -> list[str]:
        services_map = {
            "workstation": ["ssh:22", "rdp:3389"],
            "database": ["mysql:3306", "redis:6379"],
            "fileserver": ["smb:445", "ftp:21", "nfs:2049"],
            "backupserver": ["rsync:873", "backup-rpc:9100"],
            "adminpanel": ["https:443", "snmp:161", "syslog:514"],
            "monitor": ["prometheus:9090", "snort-alert:7000"],
            "research": ["jupyter:8888", "grpc:50051"],
        }
        return services_map.get(node_type, ["telnet:23"])

    def is_solvable(self, nodes: dict[str, NetworkNode]) -> bool:
        """Verifies path exists from start to objective vault."""
        if START_NODE_ID not in nodes or OBJECTIVE_NODE_ID not in nodes:
            return False

        visited: set[str] = set()
        queue: deque[str] = deque([START_NODE_ID])

        while queue:
            curr_id = queue.popleft()
            if curr_id == OBJECTIVE_NODE_ID:
                return True
            if curr_id in visited:
                continue
            visited.add(curr_id)

            curr_node = nodes.get(curr_id)
            if curr_node:
                for neighbor in curr_node.connections:
                    if neighbor not in visited:
                        queue.append(neighbor)

        return False

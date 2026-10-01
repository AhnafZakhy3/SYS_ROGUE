"""Network node entity for SYS//ROGUE world graph."""

from dataclasses import dataclass, field
from typing import Any
from sysrogue.entities.file import VirtualFile
from sysrogue.entities.process import SimulatedProcess

@dataclass
class NetworkNode:
    id: str
    name: str
    node_type: str  # gateway, workstation, database, fileserver, backupserver, adminpanel, monitor, research
    security_level: int = 1
    depth: int = 0
    connections: list[str] = field(default_factory=list)
    files: dict[str, VirtualFile] = field(default_factory=dict)
    processes: list[SimulatedProcess] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    is_discovered: bool = False
    is_inspected: bool = False
    is_compromised: bool = False
    firewall_active: bool = False
    firewall_bypass_key: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_connection(self, target_id: str) -> None:
        if target_id not in self.connections and target_id != self.id:
            self.connections.append(target_id)

    def get_file(self, identifier: str) -> VirtualFile | None:
        """Find file by exact path or filename."""
        if identifier in self.files:
            return self.files[identifier]
        for f in self.files.values():
            if f.name.lower() == identifier.lower() or f.path.lower() == identifier.lower():
                return f
        return None

"""Node templates and archetype content builders."""

from sysrogue.entities.file import VirtualFile
from sysrogue.entities.process import SimulatedProcess
from sysrogue.core.rng import GameRNG

def create_gateway_node(node_id: str, name: str, depth: int, is_extraction: bool = False) -> tuple[dict[str, VirtualFile], list[SimulatedProcess]]:
    files = {
        "/etc/motd": VirtualFile(
            id=f"{node_id}_motd",
            name="motd",
            path="/etc/motd",
            file_type="text",
            content="SYS//GATEWAY v4.11 — Authorized access only. All sessions logged to IDS cluster.",
        ),
        "/var/log/routing.log": VirtualFile(
            id=f"{node_id}_routing_log",
            name="routing.log",
            path="/var/log/routing.log",
            file_type="log",
            content="[INFO] Gateway ingress operational. Border firewall filtering inbound SYN floods.",
        ),
    }
    if is_extraction:
        files["/root/extraction_portal.conf"] = VirtualFile(
            id=f"{node_id}_portal",
            name="extraction_portal.conf",
            path="/root/extraction_portal.conf",
            file_type="config",
            content="EXTRACTION GATEWAY ACTIVATED. Deliver 'nexus_core.enc' here to complete extraction.",
        )
    processes = [
        SimulatedProcess(pid=1, name="systemd", process_type="system", description="Core system manager", memory_cost=1),
        SimulatedProcess(pid=102, name="sshd", process_type="system", description="Secure shell server", memory_cost=2),
        SimulatedProcess(pid=210, name="packet_filter", process_type="security", description="Perimeter gateway firewall", memory_cost=2),
    ]
    return files, processes

def create_workstation_node(node_id: str, name: str, depth: int, rng: GameRNG) -> tuple[dict[str, VirtualFile], list[SimulatedProcess]]:
    user_names = ["dev_marcus", "eng_turing", "analyst_clara", "sec_kline"]
    user = rng.choice(user_names)
    notes = [
        "Remember to wipe /tmp before leaving shift. The security daemon flag was twitching today.",
        "Management pushed Project NEMESIS to the cold storage vault. Check /backup on deep nodes.",
        "The admin password hash was rotated again. Don't leave auth tokens in public logs!",
    ]
    files = {
        f"/home/{user}/notes.txt": VirtualFile(
            id=f"{node_id}_notes",
            name="notes.txt",
            path=f"/home/{user}/notes.txt",
            file_type="text",
            content=rng.choice(notes),
        ),
        "/tmp/session_cache.tmp": VirtualFile(
            id=f"{node_id}_cache",
            name="session_cache.tmp",
            path="/tmp/session_cache.tmp",
            file_type="text",
            content="0x4F9B 0x1102 SESSION_RECONNECT_TOKEN=TOKEN_7482_SEC",
        ),
    }
    processes = [
        SimulatedProcess(pid=1, name="init", process_type="system", description="System initialization"),
        SimulatedProcess(pid=332, name="bash", process_type="user", description=f"Interactive session for {user}"),
        SimulatedProcess(pid=405, name="vscode-server", process_type="user", description="Development workspace daemon"),
    ]
    return files, processes

def create_database_node(node_id: str, name: str, depth: int, rng: GameRNG) -> tuple[dict[str, VirtualFile], list[SimulatedProcess]]:
    files = {
        "/var/db/accounts.csv": VirtualFile(
            id=f"{node_id}_accounts",
            name="accounts.csv",
            path="/var/db/accounts.csv",
            file_type="text",
            content="uid,username,privilege,clearance\n1001,root,admin,LEVEL_5\n1002,nemesis_svc,service,LEVEL_9\n1003,guest,user,LEVEL_1",
        ),
        "/var/db/schema.sql": VirtualFile(
            id=f"{node_id}_schema",
            name="schema.sql",
            path="/var/db/schema.sql",
            file_type="text",
            content="CREATE TABLE secure_tokens (token_id INT, payload VARCHAR(256), hash CHAR(64));",
        ),
        "/var/db/transfers.enc": VirtualFile(
            id=f"{node_id}_transfers_enc",
            name="transfers.enc",
            path="/var/db/transfers.enc",
            file_type="encrypted",
            content="ENCRYPTED DATABASE BLOB — REQUIRES DECRYPTION",
            is_encrypted=True,
            decrypted_content="CREDIT_TRANSFER_LOG: Transferred 50,000 corporate credits to offshore vault.",
            decrypt_difficulty=12,
        ),
    }
    processes = [
        SimulatedProcess(pid=1, name="init", process_type="system", description="System init"),
        SimulatedProcess(pid=501, name="mysqld", process_type="system", description="Relational database engine", memory_cost=3),
        SimulatedProcess(pid=512, name="db_monitor", process_type="security", description="Transaction auditing monitor"),
    ]
    return files, processes

def create_fileserver_node(node_id: str, name: str, depth: int, rng: GameRNG) -> tuple[dict[str, VirtualFile], list[SimulatedProcess]]:
    files = {
        "/shares/public/readme.txt": VirtualFile(
            id=f"{node_id}_readme",
            name="readme.txt",
            path="/shares/public/readme.txt",
            file_type="text",
            content="Central file repository for SYS network. Confidential archives reside in /shares/classified.",
        ),
        "/shares/classified/project_nemesis_memo.txt": VirtualFile(
            id=f"{node_id}_memo",
            name="project_nemesis_memo.txt",
            path="/shares/classified/project_nemesis_memo.txt",
            file_type="text",
            content="PROJECT NEMESIS MEMO: The neural kernel architecture demonstrates runaway autonomy. Do not deploy to gateway.",
        ),
        "/shares/classified/vault_key.enc": VirtualFile(
            id=f"{node_id}_key",
            name="vault_key.enc",
            path="/shares/classified/vault_key.enc",
            file_type="encrypted",
            content="ENCRYPTED FILE — KEY MATERIAL LOCKED",
            is_encrypted=True,
            decrypted_content="KEY_MATERIAL: MASTER_ACCESS_KEY_0x99AAFF — Unlocks Vault Deep Archives.",
            decrypt_difficulty=11,
        ),
    }
    processes = [
        SimulatedProcess(pid=1, name="systemd", process_type="system", description="Core manager"),
        SimulatedProcess(pid=610, name="smbd", process_type="system", description="File share daemon", memory_cost=2),
        SimulatedProcess(pid=625, name="auditd", process_type="security", description="File access audit trail daemon"),
    ]
    return files, processes

def create_backupserver_node(node_id: str, name: str, depth: int, rng: GameRNG) -> tuple[dict[str, VirtualFile], list[SimulatedProcess]]:
    files = {
        "/backup/catalog.txt": VirtualFile(
            id=f"{node_id}_catalog",
            name="catalog.txt",
            path="/backup/catalog.txt",
            file_type="text",
            content="Snapshot 2026-09-30_WEEKLY: System state preserved. Archive vault snapshot synced.",
        ),
        "/backup/cold_storage/recovery_guide.txt": VirtualFile(
            id=f"{node_id}_recovery",
            name="recovery_guide.txt",
            path="/backup/cold_storage/recovery_guide.txt",
            file_type="text",
            content="In case of total intrusion lockdown, activate extraction protocol from GATEWAY-01 with core payload.",
        ),
    }
    processes = [
        SimulatedProcess(pid=1, name="init", process_type="system", description="System init"),
        SimulatedProcess(pid=710, name="rsyncd", process_type="system", description="Backup synchronization service"),
        SimulatedProcess(pid=715, name="snap_agent", process_type="system", description="Cold storage snapshot agent"),
    ]
    return files, processes

def create_adminpanel_node(node_id: str, name: str, depth: int, rng: GameRNG) -> tuple[dict[str, VirtualFile], list[SimulatedProcess]]:
    files = {
        "/admin/firewall_rules.conf": VirtualFile(
            id=f"{node_id}_fw_rules",
            name="firewall_rules.conf",
            path="/admin/firewall_rules.conf",
            file_type="config",
            content="RULE 101: DROP ALL UNREGISTERED INGRESS TO VAULT\nRULE 102: ESCALATE TRACE TO 100% ON PROBE DETECTION",
        ),
        "/admin/lockdown_override.enc": VirtualFile(
            id=f"{node_id}_override",
            name="lockdown_override.enc",
            path="/admin/lockdown_override.enc",
            file_type="encrypted",
            content="ENCRYPTED COMMAND FILE — ACCESS RESTRICTED",
            is_encrypted=True,
            decrypted_content="OVERRIDE_CODE: 'PURGE_TRACE_NOW' — Reduces Trace to 0 and clears lockdown state.",
            decrypt_difficulty=13,
        ),
    }
    processes = [
        SimulatedProcess(pid=1, name="init", process_type="system", description="System init"),
        SimulatedProcess(pid=808, name="ids_manager", process_type="security", description="Central Intrusion Detection Supervisor", security_risk=5),
        SimulatedProcess(pid=815, name="policy_enforcer", process_type="security", description="Security policy automated enforcer", is_hunter=True),
    ]
    return files, processes

def create_monitor_node(node_id: str, name: str, depth: int, rng: GameRNG) -> tuple[dict[str, VirtualFile], list[SimulatedProcess]]:
    files = {
        "/var/log/ids_telemetry.log": VirtualFile(
            id=f"{node_id}_ids_log",
            name="ids_telemetry.log",
            path="/var/log/ids_telemetry.log",
            file_type="log",
            content="[ALERT] Anomalous probe traffic detected propagating from Gateway. Hunter processes dispatched.",
        ),
        "/var/log/traceroute_dump.log": VirtualFile(
            id=f"{node_id}_trace_dump",
            name="traceroute_dump.log",
            path="/var/log/traceroute_dump.log",
            file_type="log",
            content="TRACE ROUTE: Host hops 12 -> 42 -> 77 -> VAULT. Threat probability: HIGH.",
        ),
    }
    processes = [
        SimulatedProcess(pid=1, name="init", process_type="system", description="System init"),
        SimulatedProcess(pid=905, name="snort_ids", process_type="security", description="Heuristic network analyzer", memory_cost=2),
        SimulatedProcess(pid=920, name="hunter_daemon", process_type="security", description="Active process hunter subroutine", is_hunter=True, security_risk=6),
    ]
    return files, processes

def create_research_node(node_id: str, name: str, depth: int, is_target_vault: bool = False) -> tuple[dict[str, VirtualFile], list[SimulatedProcess]]:
    if is_target_vault:
        files = {
            "/vault/nexus_core.enc": VirtualFile(
                id="target_archive",
                name="nexus_core.enc",
                path="/vault/nexus_core.enc",
                file_type="archive",
                content="[PRIMARY OBJECTIVE ARCHIVE] — Encrypted AI Core 'NEXUS'. Must be acquired and delivered to GATEWAY-01 to win.",
                is_encrypted=True,
                decrypted_content="NEXUS CORE ARCHIVE: Neural weights and source code successfully decrypted! Escape to GATEWAY-01.",
                decrypt_difficulty=14,
            ),
            "/vault/manifest.txt": VirtualFile(
                id=f"{node_id}_manifest",
                name="manifest.txt",
                path="/vault/manifest.txt",
                file_type="text",
                content="VAULT STORAGE MANIFEST:\nItem: NEXUS_CORE_V1\nStatus: Quarantined\nInstructions: Evacuate payload if system compromised.",
            ),
        }
    else:
        files = {
            "/research/experiment_notes.txt": VirtualFile(
                id=f"{node_id}_exp_notes",
                name="experiment_notes.txt",
                path="/research/experiment_notes.txt",
                file_type="text",
                content="Autonomous neural models exhibit unpredictable adaptive behavior when exposed to network stimuli.",
            ),
            "/research/kernel_patch.enc": VirtualFile(
                id=f"{node_id}_patch",
                name="kernel_patch.enc",
                path="/research/kernel_patch.enc",
                file_type="encrypted",
                content="ENCRYPTED KERNEL EXPERIMENT",
                is_encrypted=True,
                decrypted_content="RESEARCH DISCLOSURE: Prototype hypervisor exploit recovered (+50 credits).",
                decrypt_difficulty=12,
            ),
        }
    processes = [
        SimulatedProcess(pid=1, name="init", process_type="system", description="System init"),
        SimulatedProcess(pid=990, name="neural_worker", process_type="narrative", description="Experimental AI cluster process"),
        SimulatedProcess(pid=995, name="quarantine_lock", process_type="security", description="Vault quarantine security daemon"),
    ]
    return files, processes

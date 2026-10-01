"""Command handler implementations for all SYS//ROGUE actions."""

from sysrogue.commands.parser import ParsedCommand
from sysrogue.commands.registry import CommandRegistry
from sysrogue.core.rng import GameRNG
from sysrogue.core.state import GameState
from sysrogue.persistence.save import SaveManager
from sysrogue.systems.exploration import ExplorationSystem
from sysrogue.systems.filesystem import FilesystemSystem
from sysrogue.systems.network import NetworkSystem
from sysrogue.systems.process import ProcessSystem
from sysrogue.systems.progression import ProgressionSystem
from sysrogue.systems.upgrades import UpgradeSystem

def build_command_registry(rng: GameRNG) -> CommandRegistry:
    reg = CommandRegistry()

    # --- 1. HELP ---
    @reg.register("help", "help [command]", "Display available commands and syntax", consumes_turn=False, aliases=["?"])
    def handle_help(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        if cmd.args:
            sub = cmd.args[0]
            defn = reg.get_command(sub)
            if defn:
                aliases_txt = f" (Aliases: {', '.join(defn.aliases)})" if defn.aliases else ""
                turn_txt = "Consumes 1 Turn" if defn.consumes_turn else "Free Action"
                return True, f"COMMAND: {defn.name}{aliases_txt}\nUsage:       {defn.usage}\nType:        {turn_txt}\nDescription: {defn.description}"
            return False, f"Unknown command '{sub}'."

        lines = [
            "SYS//ROGUE COMMAND DIRECTORY",
            "============================",
            "Type `help <command>` for detailed syntax.",
            "",
            "EXPLORATION & NETWORK:",
            "  look               Inspect current node environment",
            "  scan               Scan local subnet and discover adjacent hosts (1 turn)",
            "  connect <node>     Traverse connection to adjacent host (1 turn)",
            "  map                Display network topology ASCII graph",
            "",
            "FILESYSTEM & CRYPTOGRAPHY:",
            "  ls                 List files in current node filesystem",
            "  cat <file>         Read plaintext file contents",
            "  decrypt <file>     Decrypt encrypted file or archive (1 turn)",
            "",
            "PROCESSES & INTERACTION:",
            "  ps                 Display active process table on current node",
            "  inspect <target>   Examine detailed telemetry of file, process, or service",
            "  interact <target>  Inject or terminate a process (1 turn)",
            "",
            "SOFTWARE & CHARACTER:",
            "  status             Show player process stats, integrity, and trace",
            "  inventory          Show installed programs, upgrades, and keyring",
            "  run <prog>         Execute an installed program (1 turn)",
            "  use <prog>         Alias for `run` (1 turn)",
            "  upgrade [id]       Browse vendor catalog or install an upgrade",
            "",
            "SYSTEM & META:",
            "  objective          Show primary and secondary mission objectives",
            "  log                Display recent event log history",
            "  save               Persist current run state to disk",
            "  load               Restore saved run from disk",
            "  restart            Abandon current session and start a new run",
            "  quit               Exit SYS//ROGUE",
        ]
        return True, "\n".join(lines)

    # --- 2. STATUS ---
    @reg.register("status", "status", "Display player stats, attributes, and resource meters", consumes_turn=False, aliases=["st"])
    def handle_status(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        p = state.player
        lines = [
            f"PROCESS TELEMETRY: PID {p.pid} ({p.name})",
            "========================================",
            "ATTRIBUTES (Core Ratings):",
            f"  Processing:         {p.get_effective_stat('processing'):>2} (Base: {p.processing})",
            f"  Memory Bus:         {p.get_effective_stat('memory'):>2} (Base: {p.memory_stat})",
            f"  Network Interface:  {p.get_effective_stat('network'):>2} (Base: {p.network})",
            f"  Reverse Eng:        {p.get_effective_stat('reverse_eng'):>2} (Base: {p.reverse_eng})",
            f"  Stealth Cloak:      {p.get_effective_stat('stealth'):>2} (Base: {p.stealth})",
            "",
            "ALLOCATABLE RESOURCES:",
            f"  Integrity (HP):     {p.integrity}/{p.max_integrity}",
            f"  CPU Cycles:         {p.cpu}/{p.max_cpu}",
            f"  Resident RAM:       {p.ram_used}/{p.max_ram}",
            f"  Bandwidth:          {p.bandwidth}/{p.max_bandwidth}",
            f"  Trace Exposure:     {p.trace}/100",
            f"  Credits:            {p.credits} CR",
            "",
            f"Active Security State: {state.security_state.value}",
        ]
        if p.temporary_effects:
            lines.append("ACTIVE TEMPORARY EFFECTS:")
            for eff in p.temporary_effects:
                lines.append(f"  * {eff.get('name')}: {eff.get('modifiers')} ({eff.get('duration')} turns left)")
        return True, "\n".join(lines)

    # --- 3. LOOK ---
    @reg.register("look", "look", "Inspect current node environment", consumes_turn=False, aliases=["l"])
    def handle_look(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        return True, ExplorationSystem.look(state)

    # --- 4. MAP ---
    @reg.register("map", "map", "Display network topology ASCII graph", consumes_turn=False, aliases=["m"])
    def handle_map(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        return True, ExplorationSystem.render_map(state)

    # --- 5. SCAN ---
    @reg.register("scan", "scan", "Scan local subnet and discover adjacent hosts", consumes_turn=True, aliases=["sc"])
    def handle_scan(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        return ExplorationSystem.scan(state)

    # --- 6. CONNECT ---
    @reg.register("connect", "connect <node_id>", "Traverse network connection to target node", consumes_turn=True, aliases=["conn", "cd"])
    def handle_connect(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        if not cmd.args:
            return False, "Usage: `connect <node_id>`. Example: `connect NODE-02`."
        return NetworkSystem.connect_node(state, cmd.args[0], rng)

    # --- 7. INSPECT ---
    @reg.register("inspect", "inspect <target>", "Examine detailed telemetry of a file, process, or service", consumes_turn=False, aliases=["info"])
    def handle_inspect(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        if not cmd.args:
            return False, "Usage: `inspect <target>`. Target can be a filename, PID, or process name."
        return ProcessSystem.inspect_target(state, cmd.arg_str)

    # --- 8. LS ---
    @reg.register("ls", "ls", "List files in current node filesystem", consumes_turn=False, aliases=["dir"])
    def handle_ls(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        return True, FilesystemSystem.list_files(state)

    # --- 9. CAT ---
    @reg.register("cat", "cat <filename>", "Read file contents", consumes_turn=False, aliases=["read", "type"])
    def handle_cat(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        if not cmd.args:
            return False, "Usage: `cat <filename>`. Example: `cat notes.txt`."
        return FilesystemSystem.read_file(state, cmd.arg_str)

    # --- 10. PS ---
    @reg.register("ps", "ps", "Display active process table on current node", consumes_turn=False, aliases=["procs"])
    def handle_ps(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        return True, ProcessSystem.list_processes(state)

    # --- 11. RUN ---
    @reg.register("run", "run <program_id>", "Execute an installed program", consumes_turn=True, aliases=["exec"])
    def handle_run(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        if not cmd.args:
            progs = ", ".join(state.player.programs.keys())
            return False, f"Usage: `run <program_id>`. Available programs: {progs}"
        return UpgradeSystem.run_program(state, cmd.args[0])

    # --- 12. USE (Alias for run) ---
    @reg.register("use", "use <program_id>", "Alias for `run <program>`", consumes_turn=True)
    def handle_use(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        return handle_run(state, cmd)

    # --- 13. INTERACT ---
    @reg.register("interact", "interact <pid_or_name>", "Interact with or terminate a simulated process", consumes_turn=True, aliases=["kill"])
    def handle_interact(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        if not cmd.args:
            return False, "Usage: `interact <pid_or_name>`. Example: `interact 501` or `interact hunter_daemon`."
        return ProcessSystem.interact_process(state, cmd.arg_str, rng)

    # --- 14. DECRYPT ---
    @reg.register("decrypt", "decrypt <filename>", "Attempt cryptanalysis on an encrypted file", consumes_turn=True, aliases=["crack"])
    def handle_decrypt(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        if not cmd.args:
            return False, "Usage: `decrypt <filename>`. Example: `decrypt vault_key.enc`."
        return FilesystemSystem.decrypt_file(state, cmd.arg_str, rng)

    # --- 15. UPGRADE ---
    @reg.register("upgrade", "upgrade [upgrade_id]", "Browse hardware vendor catalog or install an upgrade", consumes_turn=False, aliases=["shop", "store"])
    def handle_upgrade(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        target = cmd.args[0] if cmd.args else None
        return UpgradeSystem.show_or_buy_upgrades(state, target)

    # --- 16. INVENTORY ---
    @reg.register("inventory", "inventory", "Display owned programs, upgrades, and keyring tokens", consumes_turn=False, aliases=["inv", "i"])
    def handle_inventory(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        return True, UpgradeSystem.show_inventory(state)

    # --- 17. LOG ---
    @reg.register("log", "log [count]", "Display recent system event log telemetry", consumes_turn=False, aliases=["history"])
    def handle_log(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        count = int(cmd.args[0]) if cmd.args and cmd.args[0].isdigit() else 20
        logs = state.event_log[-count:]
        if not logs:
            return True, "No events recorded in system log yet."
        lines = [f"EVENT LOG TELEMETRY (Last {len(logs)} entries):", "─" * 50]
        for l in logs:
            lines.append(f"> {l}")
        return True, "\n".join(lines)

    # --- 18. OBJECTIVE ---
    @reg.register("objective", "objective", "Display mission objectives and completion status", consumes_turn=False, aliases=["goals", "obj"])
    def handle_objective(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        return True, ProgressionSystem.show_objectives(state)

    # --- 19. SAVE ---
    @reg.register("save", "save [filepath]", "Persist current run state to disk", consumes_turn=False)
    def handle_save(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        path = None
        if cmd.args:
            from pathlib import Path
            path = Path(cmd.args[0])
        return SaveManager.save_game(state, path)

    # --- 20. LOAD ---
    @reg.register("load", "load [filepath]", "Restore saved game state from disk", consumes_turn=False)
    def handle_load(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        path = None
        if cmd.args:
            from pathlib import Path
            path = Path(cmd.args[0])
        loaded_state, msg = SaveManager.load_game(path, is_casual=state.is_casual)
        if loaded_state:
            # Replace attributes in state
            state.__dict__.update(loaded_state.__dict__)
            return True, msg
        return False, msg

    # --- 21. QUIT ---
    @reg.register("quit", "quit", "Exit SYS//ROGUE", consumes_turn=False, aliases=["exit", "q"])
    def handle_quit(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        state.run_status = "ABORTED"
        return True, "Terminating player session. Farewell, operator."

    # --- 22. RESTART ---
    @reg.register("restart", "restart [new_seed]", "Initiate a clean new run", consumes_turn=False)
    def handle_restart(state: GameState, cmd: ParsedCommand) -> tuple[bool, str]:
        state.run_status = "RESTART"
        if cmd.args and cmd.args[0].isdigit():
            state.seed = int(cmd.args[0])
        else:
            state.seed = rng.randint(100_000, 999_999)
        return True, f"Restarting game with seed {state.seed}..."

    return reg

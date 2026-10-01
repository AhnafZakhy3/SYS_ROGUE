"""Core Game orchestrator for SYS//ROGUE."""

from sysrogue.commands.handlers import build_command_registry
from sysrogue.commands.parser import CommandParser
from sysrogue.commands.registry import CommandRegistry
from sysrogue.config import GameConfig
from sysrogue.content.catalogs import get_default_programs
from sysrogue.core.events import SecurityManager
from sysrogue.core.rng import GameRNG
from sysrogue.core.state import GameState
from sysrogue.core.turn import TurnManager
from sysrogue.entities.player import PlayerProcess
from sysrogue.persistence.save import SaveManager
from sysrogue.systems.progression import ProgressionSystem
from sysrogue.ui.renderer import TerminalRenderer
from sysrogue.world.generator import WorldGenerator, START_NODE_ID

class Game:
    """Manages the full gameplay lifecycle from initialization to victory/permadeath."""

    def __init__(self, config: GameConfig | None = None) -> None:
        self.config = config or GameConfig()
        self.rng = GameRNG(self.config.seed)
        self.registry: CommandRegistry = build_command_registry(self.rng)
        self.turn_manager = TurnManager(self.rng)
        self.renderer = TerminalRenderer(no_color=self.config.no_color)
        self.state: GameState = self._initialize_new_run(self.rng.seed)

    def _initialize_new_run(self, seed: int) -> GameState:
        generator = WorldGenerator(self.rng)
        world_nodes = generator.generate()

        player = PlayerProcess()
        # Install starting usable programs (cleaner, sniffer, debugger, overclock, memscanner)
        all_progs = get_default_programs()
        for pid in ("cleaner", "sniffer", "debugger", "overclock", "memscanner"):
            player.programs[pid] = all_progs[pid]

        objectives = ProgressionSystem.initialize_objectives()

        state = GameState(
            seed=seed,
            turn=1,
            current_node_id=START_NODE_ID,
            player=player,
            nodes=world_nodes,
            security_state=SecurityManager.evaluate_state(player.trace, player.is_alive),
            objectives=objectives,
            is_casual=self.config.is_casual,
            is_debug=self.config.is_debug,
        )
        state.log("Session initiated. Intrusion probe spawned at Perimeter Gateway.")
        state.log("Type `help` for command syntax, or `scan` to discover network hosts.")
        return state

    def execute_command(self, raw_input: str) -> tuple[bool, str]:
        """Processes a single command line string, returns (success, feedback)."""
        parsed = CommandParser.parse(raw_input)
        if not parsed:
            return False, ""

        cmd_def = self.registry.get_command(parsed.name)
        if not cmd_def:
            return False, f"Unknown command: '{parsed.name}'. Type `help` for available commands."

        # Execute handler
        success, message = cmd_def.handler(self.state, parsed)

        # Log action outcome
        if message:
            first_line = message.split("\n")[0]
            if parsed.name not in ("status", "look", "map", "ls", "ps", "help", "log", "inventory", "objective"):
                self.state.log(first_line)

        # Advance turn if command consumes turn
        if cmd_def.consumes_turn:
            self.turn_manager.advance_turn(self.state, is_active_action=True)

        # Check victory conditions
        ProgressionSystem.check_victory_condition(self.state)

        # Handle permadeath save cleanup
        if self.state.run_status == "TERMINATED" and not self.state.is_casual:
            SaveManager.delete_save(self.config.save_path)

        return success, message

    def run_interactive_loop(self) -> None:
        """Main terminal interactive loop."""
        while True:
            # Check terminal end-of-run states
            if self.state.run_status in ("WON", "TERMINATED"):
                summary = ProgressionSystem.generate_summary(self.state)
                print("\n" + summary)
                choice = input("\nEnter command (`restart` or `quit`): ").strip().lower()
                if choice == "restart":
                    self.state = self._initialize_new_run(self.rng.randint(100_000, 999_999))
                    continue
                else:
                    break

            if self.state.run_status == "RESTART":
                self.state = self._initialize_new_run(self.state.seed)
                continue

            if self.state.run_status == "ABORTED":
                break

            # Render UI
            screen = self.renderer.render_screen(self.state)
            print("\n" + screen)

            # Prompt
            prompt = self.renderer.format_prompt(self.state)
            try:
                user_input = input(prompt)
            except (KeyboardInterrupt, EOFError):
                print("\nSession interrupted. Exiting.")
                break

            success, feedback = self.execute_command(user_input)
            if feedback:
                print("\n" + feedback)

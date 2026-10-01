"""Application entry and CLI argument dispatcher for SYS//ROGUE."""

import argparse
import sys
from pathlib import Path
from sysrogue.config import GameConfig
from sysrogue.core.game import Game
from sysrogue.persistence.save import SaveManager

def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sysrogue",
        description="SYS//ROGUE — Single-player terminal roguelike in a simulated network world.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Custom integer seed for deterministic world generation and simulation.",
    )
    parser.add_argument(
        "--casual",
        action="store_true",
        help="Enable casual mode (allows non-destructive save checkpoints without permadeath save wipe).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors and styling for plain text terminal fallback.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable developer diagnostic mode and internal IDs.",
    )
    parser.add_argument(
        "--load",
        type=str,
        default=None,
        help="Path to an existing save file to resume immediately.",
    )
    return parser

def main(args: list[str] | None = None) -> int:
    # Ensure Windows console supports UTF-8 characters cleanly
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = build_cli_parser()
    parsed_args = parser.parse_args(args)

    config = GameConfig(
        seed=parsed_args.seed,
        is_casual=parsed_args.casual,
        is_debug=parsed_args.debug,
        no_color=parsed_args.no_color,
    )

    game = Game(config)

    # Optional immediate load
    if parsed_args.load:
        save_file = Path(parsed_args.load)
        loaded_state, msg = SaveManager.load_game(save_file, is_casual=config.is_casual)
        if loaded_state:
            game.state = loaded_state
            print(f"[INIT] {msg}")
        else:
            print(f"[ERROR] {msg}", file=sys.stderr)
            return 1

    game.run_interactive_loop()
    return 0

if __name__ == "__main__":
    sys.exit(main())

"""Disk I/O persistence management for saves."""

import json
from pathlib import Path
from sysrogue.config import DEFAULT_SAVE_DIR, DEFAULT_SAVE_FILENAME
from sysrogue.core.state import GameState
from sysrogue.persistence.schema import serialize_state, deserialize_state

class SaveManager:
    """Handles saving, loading, and ironman save file lifecycle."""

    @staticmethod
    def get_default_path() -> Path:
        DEFAULT_SAVE_DIR.mkdir(parents=True, exist_ok=True)
        return DEFAULT_SAVE_DIR / DEFAULT_SAVE_FILENAME

    @classmethod
    def save_game(cls, state: GameState, path: Path | None = None) -> tuple[bool, str]:
        target_path = path or cls.get_default_path()
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            data = serialize_state(state)
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True, f"Game state successfully saved to '{target_path}'."
        except Exception as e:
            return False, f"Failed to write save file: {e}"

    @classmethod
    def load_game(cls, path: Path | None = None, is_casual: bool = False) -> tuple[GameState | None, str]:
        target_path = path or cls.get_default_path()
        if not target_path.exists():
            return None, f"No save file found at '{target_path}'."

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            state = deserialize_state(data)

            # Ironman Suspend-Save check: if not in casual mode, consume save file
            if not is_casual and not state.is_casual:
                target_path.unlink(missing_ok=True)
                cls_msg = f"Save file loaded from '{target_path}' and consumed (Ironman mode active)."
            else:
                cls_msg = f"Save file loaded from '{target_path}' (Casual checkpoint mode)."

            return state, cls_msg
        except Exception as e:
            return None, f"Failed to restore save file: {e}"

    @classmethod
    def delete_save(cls, path: Path | None = None) -> None:
        target_path = path or cls.get_default_path()
        try:
            target_path.unlink(missing_ok=True)
        except OSError:
            pass

"""Command registry and dispatcher."""

from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class CommandDefinition:
    name: str
    aliases: list[str]
    usage: str
    description: str
    consumes_turn: bool
    handler: Callable[..., tuple[bool, str]]

class CommandRegistry:
    """Stores and resolves commands and their aliases."""

    def __init__(self) -> None:
        self._commands: dict[str, CommandDefinition] = {}
        self._aliases: dict[str, str] = {}

    def register(
        self,
        name: str,
        usage: str,
        description: str,
        consumes_turn: bool,
        aliases: list[str] | None = None,
    ) -> Callable:
        aliases_list = aliases or []

        def decorator(func: Callable[..., tuple[bool, str]]) -> Callable[..., tuple[bool, str]]:
            cmd = CommandDefinition(
                name=name.lower(),
                aliases=[a.lower() for a in aliases_list],
                usage=usage,
                description=description,
                consumes_turn=consumes_turn,
                handler=func,
            )
            self._commands[cmd.name] = cmd
            for alias in cmd.aliases:
                self._aliases[alias] = cmd.name
            return func

        return decorator

    def get_command(self, query: str) -> CommandDefinition | None:
        q = query.lower()
        if q in self._commands:
            return self._commands[q]
        if q in self._aliases:
            return self._commands[self._aliases[q]]
        return None

    def get_all_commands(self) -> list[CommandDefinition]:
        return sorted(list(self._commands.values()), key=lambda c: c.name)

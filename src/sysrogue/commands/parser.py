"""Command line parsing and tokenization for SYS//ROGUE."""

import shlex
from dataclasses import dataclass

@dataclass
class ParsedCommand:
    raw: str
    name: str
    args: list[str]

    @property
    def arg_str(self) -> str:
        return " ".join(self.args)

class CommandParser:
    """Parses raw user input strings safely."""

    @staticmethod
    def parse(user_input: str) -> ParsedCommand | None:
        trimmed = user_input.strip()
        if not trimmed:
            return None

        try:
            tokens = shlex.split(trimmed)
        except ValueError:
            # Fallback simple split if quotes are unclosed
            tokens = trimmed.split()

        if not tokens:
            return None

        command_name = tokens[0].lower()
        args = tokens[1:]

        return ParsedCommand(raw=trimmed, name=command_name, args=args)

import unittest
from sysrogue.commands.handlers import build_command_registry
from sysrogue.commands.parser import CommandParser
from sysrogue.core.game import Game
from sysrogue.config import GameConfig

class TestCommands(unittest.TestCase):
    def test_parser(self):
        cmd = CommandParser.parse("connect NODE-02")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "connect")
        self.assertEqual(cmd.args, ["NODE-02"])

        cmd_quotes = CommandParser.parse('cat "notes with space.txt"')
        self.assertIsNotNone(cmd_quotes)
        self.assertEqual(cmd_quotes.args, ["notes with space.txt"])

        self.assertIsNone(CommandParser.parse("   "))

    def test_all_22_commands_registered(self):
        game = Game(GameConfig(seed=12345))
        required = [
            "help", "status", "look", "map", "scan", "connect", "inspect",
            "ls", "cat", "ps", "run", "use", "interact", "decrypt",
            "upgrade", "inventory", "log", "objective", "save", "load",
            "quit", "restart"
        ]
        for cmd_name in required:
            defn = game.registry.get_command(cmd_name)
            self.assertIsNotNone(defn, f"Command '{cmd_name}' must be registered.")

    def test_invalid_command_graceful_handling(self):
        game = Game(GameConfig(seed=12345))
        success, msg = game.execute_command("nonexistent_hack_command --now")
        self.assertFalse(success)
        self.assertIn("Unknown command", msg)

if __name__ == "__main__":
    unittest.main()

import unittest
from sysrogue.config import GameConfig
from sysrogue.core.game import Game
from sysrogue.world.generator import OBJECTIVE_NODE_ID, START_NODE_ID

class TestGameLoop(unittest.TestCase):
    def test_basic_gameplay_flow(self):
        game = Game(GameConfig(seed=12345, no_color=True))
        self.assertEqual(game.state.current_node_id, START_NODE_ID)

        # 1. Look
        success, msg = game.execute_command("look")
        self.assertTrue(success)
        self.assertIn("GATEWAY-01", msg)

        # 2. Status
        success, msg = game.execute_command("status")
        self.assertTrue(success)
        self.assertIn("SYS_PROBE", msg)

        # 3. Scan
        success, msg = game.execute_command("scan")
        self.assertTrue(success)
        self.assertIn("SCAN COMPLETE", msg.upper())

        # 4. Movement: connect to first adjacent node
        adjacent = game.state.current_node.connections[0]
        success, msg = game.execute_command(f"connect {adjacent}")
        self.assertTrue(success)
        self.assertEqual(game.state.current_node_id, adjacent)

    def test_victory_condition_flow(self):
        game = Game(GameConfig(seed=12345))

        # Simulate getting and decrypting objective archive
        game.state.narrative_flags["archive_decrypted"] = True
        game.state.current_node_id = START_NODE_ID

        # Execute any active turn command to trigger victory check
        game.execute_command("status")
        from sysrogue.systems.progression import ProgressionSystem
        is_won = ProgressionSystem.check_victory_condition(game.state)
        self.assertTrue(is_won)
        self.assertEqual(game.state.run_status, "WON")

    def test_permadeath_flow(self):
        game = Game(GameConfig(seed=12345))

        # Take lethal damage
        game.state.player.take_damage(200)
        game.turn_manager.advance_turn(game.state, is_active_action=True)

        self.assertEqual(game.state.run_status, "TERMINATED")
        self.assertFalse(game.state.player.is_alive)

if __name__ == "__main__":
    unittest.main()

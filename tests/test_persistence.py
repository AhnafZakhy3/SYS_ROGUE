import unittest
from pathlib import Path
from sysrogue.core.game import Game
from sysrogue.config import GameConfig
from sysrogue.persistence.save import SaveManager
from sysrogue.persistence.schema import serialize_state, deserialize_state

class TestPersistence(unittest.TestCase):
    def test_serialization_roundtrip(self):
        game = Game(GameConfig(seed=888123))
        original_state = game.state
        original_state.player.credits = 150
        original_state.player.keyring.append("KEY_ABC")

        data = serialize_state(original_state)
        restored_state = deserialize_state(data)

        self.assertEqual(restored_state.seed, original_state.seed)
        self.assertEqual(restored_state.turn, original_state.turn)
        self.assertEqual(restored_state.player.credits, 150)
        self.assertIn("KEY_ABC", restored_state.player.keyring)
        self.assertEqual(list(restored_state.nodes.keys()), list(original_state.nodes.keys()))

    def test_ironman_save_consumption(self):
        game = Game(GameConfig(seed=444111, is_casual=False))
        test_save_path = Path("saves/test_ironman_save.json")

        # Save game
        success, msg = SaveManager.save_game(game.state, test_save_path)
        self.assertTrue(success)
        self.assertTrue(test_save_path.exists())

        # Load game in ironman mode (consumes save file)
        loaded_state, load_msg = SaveManager.load_game(test_save_path, is_casual=False)
        self.assertIsNotNone(loaded_state)
        # Verify save was consumed/deleted
        self.assertFalse(test_save_path.exists())

    def test_casual_checkpoint_retention(self):
        game = Game(GameConfig(seed=444111, is_casual=True))
        test_save_path = Path("saves/test_casual_save.json")

        SaveManager.save_game(game.state, test_save_path)
        self.assertTrue(test_save_path.exists())

        # Load game in casual mode (file remains on disk)
        loaded_state, load_msg = SaveManager.load_game(test_save_path, is_casual=True)
        self.assertIsNotNone(loaded_state)
        self.assertTrue(test_save_path.exists())

        # Cleanup
        SaveManager.delete_save(test_save_path)

if __name__ == "__main__":
    unittest.main()

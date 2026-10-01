import unittest
from sysrogue.core.state import GameState
from sysrogue.systems.upgrades import UpgradeSystem

class TestUpgrades(unittest.TestCase):
    def test_show_catalog(self):
        state = GameState(seed=123)
        success, catalog_view = UpgradeSystem.show_or_buy_upgrades(state)
        self.assertTrue(success)
        self.assertIn("cpu_bus_v2", catalog_view)
        self.assertIn("ice_breaker", catalog_view)

    def test_buy_upgrade_success(self):
        state = GameState(seed=123)
        state.player.credits = 100
        success, msg = UpgradeSystem.show_or_buy_upgrades(state, "cpu_bus_v2")
        self.assertTrue(success)
        self.assertIn("cpu_bus_v2", state.player.upgrades)
        self.assertEqual(state.player.credits, 80)
        self.assertEqual(state.player.max_cpu, 12)

    def test_insufficient_credits(self):
        state = GameState(seed=123)
        state.player.credits = 5
        success, msg = UpgradeSystem.show_or_buy_upgrades(state, "ice_breaker")
        self.assertFalse(success)
        self.assertIn("Insufficient credits", msg)

    def test_run_programs(self):
        state = GameState(seed=123)
        from sysrogue.content.catalogs import get_default_programs
        state.player.programs = get_default_programs()

        # Cleaner program reduces trace
        state.player.trace = 40
        success, msg = UpgradeSystem.run_program(state, "cleaner")
        self.assertTrue(success)
        self.assertEqual(state.player.trace, 20)

if __name__ == "__main__":
    unittest.main()

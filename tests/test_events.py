import unittest
from sysrogue.core.events import EncounterManager
from sysrogue.core.rng import GameRNG
from sysrogue.core.state import GameState
from sysrogue.world.node import NetworkNode

class TestEvents(unittest.TestCase):
    def test_encounter_resolution(self):
        rng = GameRNG(555)
        mgr = EncounterManager(rng)
        state = GameState(seed=555)
        node = NetworkNode(id="TEST-02", name="Research Lab", node_type="research", depth=2)

        # Force high encounter rate
        outcome = mgr.roll_encounter(state.player, node, base_chance=1.0)
        self.assertIsNotNone(outcome)
        self.assertTrue(len(outcome.title) > 0)

if __name__ == "__main__":
    unittest.main()

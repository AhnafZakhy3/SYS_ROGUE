import unittest
from sysrogue.core.rng import GameRNG
from sysrogue.world.generator import WorldGenerator, START_NODE_ID, OBJECTIVE_NODE_ID

class TestWorldGeneration(unittest.TestCase):
    def test_solvable_world_generation(self):
        rng = GameRNG(777123)
        gen = WorldGenerator(rng)
        nodes = gen.generate()

        self.assertIn(START_NODE_ID, nodes)
        self.assertIn(OBJECTIVE_NODE_ID, nodes)
        self.assertTrue(gen.is_solvable(nodes))

    def test_reproducible_world(self):
        nodes1 = WorldGenerator(GameRNG(9999)).generate()
        nodes2 = WorldGenerator(GameRNG(9999)).generate()

        self.assertEqual(list(nodes1.keys()), list(nodes2.keys()))
        for nid in nodes1:
            self.assertEqual(nodes1[nid].connections, nodes2[nid].connections)
            self.assertEqual(nodes1[nid].node_type, nodes2[nid].node_type)

    def test_connectivity_invariance_across_multiple_seeds(self):
        for seed in (101, 202, 303, 404, 505):
            nodes = WorldGenerator(GameRNG(seed)).generate()
            self.assertTrue(WorldGenerator(GameRNG(seed)).is_solvable(nodes))

if __name__ == "__main__":
    unittest.main()

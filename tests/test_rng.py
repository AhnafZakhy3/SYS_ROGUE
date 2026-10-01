import unittest
from sysrogue.core.rng import GameRNG

class TestGameRNG(unittest.TestCase):
    def test_deterministic_sequence(self):
        rng1 = GameRNG(424242)
        rng2 = GameRNG(424242)

        rolls1 = [rng1.randint(1, 100) for _ in range(50)]
        rolls2 = [rng2.randint(1, 100) for _ in range(50)]

        self.assertEqual(rolls1, rolls2)

    def test_d20_bounds(self):
        rng = GameRNG(12345)
        for _ in range(200):
            roll = rng.d20()
            self.assertGreaterEqual(roll, 1)
            self.assertLessEqual(roll, 20)

if __name__ == "__main__":
    unittest.main()

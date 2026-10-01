import unittest
from sysrogue.core.rng import GameRNG
from sysrogue.entities.player import PlayerProcess
from sysrogue.entities.upgrade import Upgrade

class TestPlayerProcess(unittest.TestCase):
    def test_resource_consumption_and_regeneration(self):
        p = PlayerProcess()
        self.assertEqual(p.cpu, 10)
        self.assertTrue(p.consume_cpu(4))
        self.assertEqual(p.cpu, 6)
        self.assertFalse(p.consume_cpu(10))

        p.restore_turn_resources()
        self.assertEqual(p.cpu, 8)

    def test_damage_and_trace(self):
        p = PlayerProcess()
        p.take_damage(25)
        self.assertEqual(p.integrity, 75)
        p.repair_integrity(10)
        self.assertEqual(p.integrity, 85)

        p.add_trace(30)
        self.assertEqual(p.trace, 30)
        p.add_trace(100)
        self.assertEqual(p.trace, 100)

    def test_stat_checks(self):
        p = PlayerProcess()
        rng = GameRNG(123)
        res = p.check_stat("reverse_eng", 10, rng)
        self.assertEqual(res.stat_name, "reverse_eng")
        self.assertIsInstance(res.success, bool)

    def test_upgrade_application(self):
        p = PlayerProcess()
        base_proc = p.get_effective_stat("processing")
        upg = Upgrade(
            id="test_chip",
            name="Test Chip",
            category="hardware",
            cost=10,
            description="Testing upgrade",
            stat_modifiers={"processing": 2},
            resource_max_modifiers={"max_cpu": 3},
        )
        p.install_upgrade(upg)
        self.assertEqual(p.get_effective_stat("processing"), base_proc + 2)
        self.assertEqual(p.max_cpu, 13)

if __name__ == "__main__":
    unittest.main()

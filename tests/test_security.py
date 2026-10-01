import unittest
from sysrogue.core.events import SecurityManager, SecurityState

class TestSecurity(unittest.TestCase):
    def test_state_transitions(self):
        # Trace < 25 -> CLEAR
        self.assertEqual(SecurityManager.evaluate_state(0, True), SecurityState.CLEAR)
        self.assertEqual(SecurityManager.evaluate_state(24, True), SecurityState.CLEAR)

        # Trace 25-49 -> SUSPICIOUS
        self.assertEqual(SecurityManager.evaluate_state(25, True), SecurityState.SUSPICIOUS)
        self.assertEqual(SecurityManager.evaluate_state(49, True), SecurityState.SUSPICIOUS)

        # Trace 50-79 -> ALERT
        self.assertEqual(SecurityManager.evaluate_state(50, True), SecurityState.ALERT)
        self.assertEqual(SecurityManager.evaluate_state(79, True), SecurityState.ALERT)

        # Trace 80-99 -> LOCKDOWN
        self.assertEqual(SecurityManager.evaluate_state(80, True), SecurityState.LOCKDOWN)
        self.assertEqual(SecurityManager.evaluate_state(99, True), SecurityState.LOCKDOWN)

        # Trace >= 100 or dead -> TERMINATED
        self.assertEqual(SecurityManager.evaluate_state(100, True), SecurityState.TERMINATED)
        self.assertEqual(SecurityManager.evaluate_state(10, False), SecurityState.TERMINATED)

if __name__ == "__main__":
    unittest.main()

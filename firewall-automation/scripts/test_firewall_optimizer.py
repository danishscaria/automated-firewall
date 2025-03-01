import unittest
from MyFirewallFunctionProj.firewall_optimizer import optimize_firewalls

class TestFirewallOptimizer(unittest.TestCase):
    def test_optimize_firewalls(self):
        try:
            solution = optimize_firewalls()
            self.assertIsInstance(solution, dict)
            self.assertIn("firewall_allocation", solution)
            self.assertIn("total_firewalls_deployed", solution)
            self.assertIn("allow_rule_dmz_backend", solution)
            self.assertIsInstance(solution["firewall_allocation"], dict)
            self.assertIsInstance(solution["total_firewalls_deployed"], int)
            self.assertIsInstance(solution["allow_rule_dmz_backend"], bool)
            print("Test passed: optimize_firewalls() returned a valid solution.")
        except Exception as e:
            self.fail(f"optimize_firewalls() raised an exception: {e}")

if __name__ == "__main__":
    print("Running TestFirewallOptimizer...")
    unittest.main(verbosity=2)
    print("Finished running tests.")
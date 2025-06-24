import sys
import unittest
from pathlib import Path

# Add the project root to the Python path to allow importing 'dw4'
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

class TestDW4Protocol(unittest.TestCase):
    """
    A suite of tests to validate the core functionality of the DW4 protocol engine.
    """

    def test_module_import(self):
        """
        Tests that the core dw4 module and its components can be imported without error.
        """
        print("\n- Testing module imports...")
        try:
            from dw4 import cli, config, git_handler, state_manager
            print("  Successfully imported all dw4 modules.")
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import dw4 modules: {e}")

    def test_workflow_manager_instantiation(self):
        """
        Tests that the WorkflowManager can be instantiated.
        This is a basic check to ensure the state file is read correctly.
        """
        print("- Testing WorkflowManager instantiation...")
        try:
            from dw4.state_manager import WorkflowManager
            manager = WorkflowManager()
            print(f"  Successfully instantiated WorkflowManager. Current stage: {manager.current_stage}")
            self.assertIsNotNone(manager.current_stage)
        except Exception as e:
            self.fail(f"Failed to instantiate WorkflowManager: {e}")

if __name__ == '__main__':
    print("--- Running DW4 Protocol Validation Tests ---")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDW4Protocol))
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    # Exit with a non-zero status if any tests failed
    if result.failures or result.errors:
        sys.exit(1)

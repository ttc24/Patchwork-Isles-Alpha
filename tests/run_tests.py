#!/usr/bin/env python3
"""
Comprehensive test runner for Patchwork Isles.
Runs all tests including unit tests, integration tests, and validation tests.
"""

import sys
import os
import unittest
import logging
from pathlib import Path

# Add the engine directory to the path so we can import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "engine"))
sys.path.insert(0, str(project_root / "tools"))

# Import test modules
import test_engine_core
import test_validation
import test_content_modules
import test_state_manager
import test_profile_manager

def setup_logging():
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_test_suite():
    """Create a test suite with all test modules."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test modules
    test_modules = [
        test_engine_core,
        test_validation,
        test_content_modules,
        test_state_manager,
        test_profile_manager
    ]
    
    for module in test_modules:
        suite.addTests(loader.loadTestsFromModule(module))
    
    return suite

def main():
    """Main test runner function."""
    setup_logging()
    
    print("🧪 Running Patchwork Isles Test Suite")
    print("=" * 50)
    
    # Create and run the test suite
    suite = create_test_suite()
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    # Print summary
    print("\\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.splitlines()[-1]}")
    
    if result.errors:
        print("\\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.splitlines()[-1]}")
    
    if result.wasSuccessful():
        print("\\n✅ All tests passed!")
        return 0
    else:
        print("\\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
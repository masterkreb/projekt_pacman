#!/usr/bin/env python3
"""
Test runner for the Pac-Man game unit tests.
Runs all tests following the Arrange-Act-Assert pattern.
"""

import unittest
import sys
import os

def run_tests():
    """Discover and run all tests in the tests directory."""
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    test_suite = loader.discover('tests', pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
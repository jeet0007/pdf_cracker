#!/usr/bin/env python3
"""
Test runner for PDF Cracker.
"""

import unittest
import sys
import os
from pathlib import Path

def discover_and_run_tests():
    """Discover and run all tests."""
    # Add src to path
    src_dir = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_dir))
    
    # Discover tests
    test_dir = Path(__file__).parent / 'tests'
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()

def run_specific_test(test_name):
    """Run a specific test module."""
    # Add src to path
    src_dir = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_dir))
    
    # Import and run specific test
    try:
        module = __import__(f'tests.{test_name}', fromlist=[test_name])
        suite = unittest.TestLoader().loadTestsFromModule(module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Failed to import test module '{test_name}': {e}")
        return False

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run PDF Cracker tests')
    parser.add_argument(
        'test',
        nargs='?',
        help='Specific test module to run (e.g., test_password_generator)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available test modules'
    )
    
    args = parser.parse_args()
    
    if args.list:
        # List available tests
        test_dir = Path(__file__).parent / 'tests'
        test_files = [f.stem for f in test_dir.glob('test_*.py')]
        print("Available test modules:")
        for test_file in sorted(test_files):
            print(f"  {test_file}")
        return 0
    
    print("🧪 PDF Cracker Test Runner")
    print("==========================")
    print()
    
    if args.test:
        print(f"Running specific test: {args.test}")
        success = run_specific_test(args.test)
    else:
        print("Running all tests...")
        success = discover_and_run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
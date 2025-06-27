#!/usr/bin/env python3
"""
Pytest-based test runner for PDF Cracker.
"""

import sys
import subprocess
from pathlib import Path


def run_pytest_command(args):
    """Run pytest with given arguments."""
    cmd = [sys.executable, '-m', 'pytest'] + args
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest pytest-cov")
        return False


def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run PDF Cracker tests with pytest')
    parser.add_argument(
        'test',
        nargs='?',
        help='Specific test to run (e.g., test_crunch_wrapper.py::TestCrunchWrapper::test_find_crunch)'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Run with coverage report'
    )
    parser.add_argument(
        '--slow',
        action='store_true',
        help='Include slow tests'
    )
    parser.add_argument(
        '--integration',
        action='store_true',
        help='Run only integration tests'
    )
    parser.add_argument(
        '--unit',
        action='store_true',
        help='Run only unit tests'
    )
    parser.add_argument(
        '--external',
        action='store_true',
        help='Include tests requiring external dependencies'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    print("🧪 PDF Cracker Pytest Runner")
    print("============================")
    print()
    
    # Build pytest command
    pytest_args = []
    
    if args.verbose:
        pytest_args.append('-v')
    
    if args.coverage:
        pytest_args.extend(['--cov=src', '--cov-report=term-missing', '--cov-report=html'])
    
    # Test selection by markers
    markers = []
    if not args.slow:
        markers.append('not slow')
    if args.integration:
        markers.append('integration')
    elif args.unit:
        markers.append('unit')
    if not args.external:
        markers.append('not external')
    
    if markers:
        pytest_args.extend(['-m', ' and '.join(markers)])
    
    # Specific test
    if args.test:
        pytest_args.append(args.test)
    else:
        pytest_args.append('tests/')
    
    print(f"Running: pytest {' '.join(pytest_args)}")
    print()
    
    success = run_pytest_command(pytest_args)
    
    if success:
        print("\n✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/")
    else:
        print("\n❌ Some tests failed!")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
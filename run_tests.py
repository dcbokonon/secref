#!/usr/bin/env python3
"""
Test runner for SecRef
Runs all tests with coverage reporting
"""

import sys
import os
import unittest
import argparse
from io import StringIO

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests(test_module=None, verbosity=2, with_coverage=False):
    """Run tests with optional coverage"""
    
    if with_coverage:
        try:
            import coverage
            cov = coverage.Coverage(source=['scripts', 'admin'])
            cov.start()
        except ImportError:
            print("Coverage module not installed. Run: pip install coverage")
            with_coverage = False
    
    # Discover and run tests
    if test_module:
        # Run specific test module
        suite = unittest.TestLoader().loadTestsFromName(f'tests.{test_module}')
    else:
        # Run all tests
        suite = unittest.TestLoader().discover('tests', pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    result = runner.run(suite)
    
    if with_coverage:
        cov.stop()
        
        # Print coverage report
        print("\n" + "="*70)
        print("COVERAGE REPORT")
        print("="*70)
        
        # Generate report
        report_stream = StringIO()
        cov.report(file=report_stream)
        print(report_stream.getvalue())
        
        # Save HTML report
        html_dir = os.path.join(os.path.dirname(__file__), 'tests', 'coverage_html')
        cov.html_report(directory=html_dir)
        print(f"\nDetailed HTML coverage report saved to: {html_dir}/index.html")
    
    return result.wasSuccessful()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run SecRef tests')
    parser.add_argument('test', nargs='?', help='Specific test module to run (e.g., test_database)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true', help='Minimal output')
    parser.add_argument('-c', '--coverage', action='store_true', help='Run with coverage analysis')
    
    args = parser.parse_args()
    
    # Determine verbosity
    verbosity = 2  # Default
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 3
    
    # Run tests
    success = run_tests(
        test_module=args.test,
        verbosity=verbosity,
        with_coverage=args.coverage
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
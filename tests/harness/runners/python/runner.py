#!/usr/bin/env python3
"""PTA Standards Conformance Test Runner.

Runs conformance tests against the Python beancount reference implementation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add this directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from loader import load_all_tests, filter_tests, TestCase
from executors.base import TestResult
from executors.syntax import SyntaxExecutor
from executors.validation import ValidationExecutor
from executors.bql import BQLExecutor
from executors.rustledger import RustledgerExecutor
from reporters.tap import TAPReporter
from reporters.json_reporter import JSONReporter


# Global to track implementation
_implementation = "beancount"


def get_executor(test: TestCase):
    """Get the appropriate executor for a test."""
    # If using rustledger, always use the rustledger executor
    if _implementation == "rustledger":
        return RustledgerExecutor()

    # For beancount, use type-specific executors
    test_type = test.get_test_type()
    if test_type == "bql":
        return BQLExecutor()
    elif test_type == "validation":
        return ValidationExecutor()
    else:
        return SyntaxExecutor()


def run_tests(
    tests: list[TestCase],
    fail_fast: bool = False,
) -> list[TestResult]:
    """Run a list of tests and return results."""
    results = []

    for test in tests:
        executor = get_executor(test)
        result = executor.execute(test)
        results.append(result)

        if fail_fast and not result.passed:
            break

    return results


def main():
    parser = argparse.ArgumentParser(
        description="PTA Standards Conformance Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all beancount v3 tests against Python beancount
  python runner.py --manifest ../../beancount/v3/manifest.json

  # Run against rustledger
  python runner.py --manifest ../../beancount/v3/manifest.json --impl rustledger

  # Run specific suite
  python runner.py --manifest ../../beancount/v3/manifest.json --suite validation

  # Filter by tags
  python runner.py --manifest ../../beancount/v3/manifest.json --tags booking,fifo

  # Run single test
  python runner.py --manifest ../../beancount/v3/manifest.json --test account-not-opened

  # Output as JSON
  python runner.py --manifest ../../beancount/v3/manifest.json --format json
""",
    )

    parser.add_argument(
        "--manifest",
        "-m",
        type=Path,
        required=True,
        help="Path to manifest.json file",
    )
    parser.add_argument(
        "--suite",
        "-s",
        type=str,
        help="Run only tests from specific suite (e.g., 'validation', 'syntax/valid')",
    )
    parser.add_argument(
        "--tags",
        "-t",
        type=str,
        help="Filter tests by tags (comma-separated)",
    )
    parser.add_argument(
        "--test",
        type=str,
        help="Run a single test by ID",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["tap", "json"],
        default="tap",
        help="Output format (default: tap)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output (show timing for all tests)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first failure",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List tests without running them",
    )
    parser.add_argument(
        "--impl",
        choices=["beancount", "rustledger"],
        default="beancount",
        help="Implementation to test against (default: beancount)",
    )

    args = parser.parse_args()

    # Set global implementation
    global _implementation
    _implementation = args.impl

    # Load tests
    if not args.manifest.exists():
        print(f"Error: Manifest file not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    tests = load_all_tests(args.manifest)

    # Apply filters
    tags = args.tags.split(",") if args.tags else None
    tests = filter_tests(tests, suite=args.suite, tags=tags, test_id=args.test)

    if not tests:
        print("No tests found matching filters", file=sys.stderr)
        sys.exit(1)

    # List mode
    if args.list:
        for test in tests:
            skip_marker = " [SKIP]" if test.skip else ""
            print(f"{test.id}: {test.description}{skip_marker}")
        print(f"\nTotal: {len(tests)} tests")
        sys.exit(0)

    # Build description map
    test_descriptions = {t.id: t.description for t in tests}

    # Run tests
    results = run_tests(tests, fail_fast=args.fail_fast)

    # Report results
    if args.format == "json":
        reporter = JSONReporter(verbose=args.verbose)
    else:
        reporter = TAPReporter(verbose=args.verbose)

    reporter.report(results, test_descriptions)
    reporter.summary(results)

    # Exit with appropriate code
    failed = sum(1 for r in results if not r.passed)
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()

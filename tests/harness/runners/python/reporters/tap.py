"""TAP (Test Anything Protocol) reporter."""

from __future__ import annotations

import sys
from typing import TextIO

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from executors.base import TestResult


class TAPReporter:
    """Reports test results in TAP format."""

    def __init__(self, output: TextIO = sys.stdout, verbose: bool = False):
        self.output = output
        self.verbose = verbose

    def report(self, results: list[TestResult], test_descriptions: dict[str, str]) -> None:
        """Output results in TAP format."""
        self.output.write("TAP version 14\n")
        self.output.write(f"1..{len(results)}\n")

        for i, result in enumerate(results, 1):
            description = test_descriptions.get(result.test_id, "")
            self._report_result(i, result, description)

    def _report_result(self, num: int, result: TestResult, description: str) -> None:
        """Output a single test result."""
        status = "ok" if result.passed else "not ok"
        desc = f"{result.test_id}: {description}" if description else result.test_id

        if result.skipped:
            self.output.write(f"{status} {num} - {desc} # SKIP {result.skip_reason or ''}\n")
        else:
            self.output.write(f"{status} {num} - {desc}\n")

            # Add YAML diagnostic block for failures or verbose mode
            if not result.passed or (self.verbose and result.duration_ms > 0):
                self.output.write("  ---\n")

                if not result.passed and result.error_message:
                    # Escape the message for YAML
                    msg = result.error_message.replace("\n", "\\n")
                    self.output.write(f"  message: \"{msg}\"\n")

                if not result.passed and result.expected:
                    self.output.write(f"  expected: {result.expected}\n")

                if not result.passed and result.actual:
                    self.output.write(f"  actual: {result.actual}\n")

                if result.duration_ms > 0:
                    self.output.write(f"  duration_ms: {result.duration_ms:.2f}\n")

                self.output.write("  ...\n")

    def summary(self, results: list[TestResult]) -> None:
        """Output summary statistics."""
        total = len(results)
        passed = sum(1 for r in results if r.passed and not r.skipped)
        failed = sum(1 for r in results if not r.passed)
        skipped = sum(1 for r in results if r.skipped)

        self.output.write(f"\n# Tests: {total}, Passed: {passed}, Failed: {failed}, Skipped: {skipped}\n")

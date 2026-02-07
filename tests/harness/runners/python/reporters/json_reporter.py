"""JSON reporter for test results."""

from __future__ import annotations

import json
import sys
from typing import TextIO

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from executors.base import TestResult


class JSONReporter:
    """Reports test results in JSON format."""

    def __init__(self, output: TextIO = sys.stdout, verbose: bool = False):
        self.output = output
        self.verbose = verbose

    def report(self, results: list[TestResult], test_descriptions: dict[str, str]) -> None:
        """Output results in JSON format."""
        total = len(results)
        passed = sum(1 for r in results if r.passed and not r.skipped)
        failed = sum(1 for r in results if not r.passed)
        skipped = sum(1 for r in results if r.skipped)

        output = {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            },
            "results": [],
        }

        for result in results:
            result_data = {
                "id": result.test_id,
                "description": test_descriptions.get(result.test_id, ""),
                "status": self._get_status(result),
                "duration_ms": round(result.duration_ms, 2),
            }

            if result.skipped:
                result_data["skip_reason"] = result.skip_reason

            if not result.passed:
                result_data["error"] = result.error_message
                if result.expected:
                    result_data["expected"] = result.expected
                if result.actual:
                    result_data["actual"] = result.actual

            output["results"].append(result_data)

        self.output.write(json.dumps(output, indent=2))
        self.output.write("\n")

    def _get_status(self, result: TestResult) -> str:
        """Get status string for a result."""
        if result.skipped:
            return "skip"
        return "pass" if result.passed else "fail"

    def summary(self, results: list[TestResult]) -> None:
        """JSON reporter includes summary in main output, so this is a no-op."""
        pass

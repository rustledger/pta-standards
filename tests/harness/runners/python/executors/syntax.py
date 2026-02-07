"""Syntax test executor - tests parsing without validation."""

from __future__ import annotations

import time
import tempfile
from pathlib import Path

from beancount import loader

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from loader import TestCase
from executors.base import BaseExecutor, TestResult


class SyntaxExecutor(BaseExecutor):
    """Executor for syntax-only tests (parse success/error)."""

    def execute(self, test: TestCase) -> TestResult:
        """Execute a syntax test."""
        if test.skip:
            return TestResult.skip(test)

        start_time = time.perf_counter()

        try:
            # Get input content
            if test.input.inline is not None:
                content = test.input.inline
                # Write to temp file for beancount loader
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".beancount", delete=False
                ) as f:
                    f.write(content)
                    temp_path = f.name
                entries, errors, options = loader.load_file(temp_path)
                Path(temp_path).unlink()
            else:
                file_path = test.input.get_file_path(test.base_path)
                if file_path is None:
                    return TestResult.failure(
                        test, "No input file or inline content specified"
                    )
                entries, errors, options = loader.load_file(str(file_path))

            duration_ms = (time.perf_counter() - start_time) * 1000

            # Determine actual parse result
            # For syntax tests, we consider any error as a parse failure
            parse_succeeded = len(errors) == 0
            actual_parse = "success" if parse_succeeded else "error"

            # Check against expected
            expected_parse = test.expected.parse

            if expected_parse is None:
                return TestResult.failure(
                    test,
                    "Test missing expected.parse field",
                    duration_ms=duration_ms,
                )

            # Check parse result
            if actual_parse != expected_parse:
                error_msgs = [str(e) for e in errors[:3]]
                return TestResult.failure(
                    test,
                    f"Expected parse={expected_parse}, got {actual_parse}",
                    actual={"parse": actual_parse, "errors": error_msgs},
                    expected={"parse": expected_parse},
                    duration_ms=duration_ms,
                )

            # Check error_contains if specified
            if test.expected.error_contains:
                success, msg = self.check_error_contains(
                    errors, test.expected.error_contains
                )
                if not success:
                    return TestResult.failure(
                        test,
                        msg or "Error message check failed",
                        actual={"errors": [str(e) for e in errors[:3]]},
                        expected={"error_contains": test.expected.error_contains},
                        duration_ms=duration_ms,
                    )

            # Check directive count if specified
            if test.expected.directives is not None:
                actual_count = len(entries)
                if actual_count != test.expected.directives:
                    return TestResult.failure(
                        test,
                        f"Expected {test.expected.directives} directives, got {actual_count}",
                        actual={"directives": actual_count},
                        expected={"directives": test.expected.directives},
                        duration_ms=duration_ms,
                    )

            return TestResult.success(test, duration_ms=duration_ms)

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return TestResult.failure(
                test,
                f"Executor error: {type(e).__name__}: {e}",
                duration_ms=duration_ms,
            )

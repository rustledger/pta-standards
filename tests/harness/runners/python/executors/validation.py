"""Validation test executor - tests parsing and semantic validation."""

from __future__ import annotations

import time
import tempfile
from pathlib import Path

from beancount import loader

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from loader import TestCase
from executors.base import BaseExecutor, TestResult


class ValidationExecutor(BaseExecutor):
    """Executor for validation tests (parse + semantic checks)."""

    def execute(self, test: TestCase) -> TestResult:
        """Execute a validation test."""
        if test.skip:
            return TestResult.skip(test)

        start_time = time.perf_counter()

        try:
            # Get input content
            if test.input.inline is not None:
                content = test.input.inline
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

            # Separate parse errors from validation errors
            # In beancount, loader.load_file returns all errors combined
            # Parse errors typically have certain types
            parse_error_types = {"ParserError", "ParserSyntaxError", "LexerError"}
            parse_errors = [
                e for e in errors if type(e).__name__ in parse_error_types
            ]
            validation_errors = [
                e for e in errors if type(e).__name__ not in parse_error_types
            ]

            # Check parse result first
            expected_parse = test.expected.parse
            if expected_parse is not None:
                parse_succeeded = len(parse_errors) == 0
                actual_parse = "success" if parse_succeeded else "error"

                if actual_parse != expected_parse:
                    error_msgs = [str(e) for e in parse_errors[:3]]
                    return TestResult.failure(
                        test,
                        f"Expected parse={expected_parse}, got {actual_parse}",
                        actual={"parse": actual_parse, "errors": error_msgs},
                        expected={"parse": expected_parse},
                        duration_ms=duration_ms,
                    )

            # Check validation result
            expected_validate = test.expected.validate
            if expected_validate is not None and expected_validate != "skip":
                # If parse failed, validation is implicitly error
                if len(parse_errors) > 0:
                    actual_validate = "error"
                else:
                    actual_validate = "success" if len(validation_errors) == 0 else "error"

                if actual_validate != expected_validate:
                    error_msgs = [str(e) for e in errors[:5]]
                    return TestResult.failure(
                        test,
                        f"Expected validate={expected_validate}, got {actual_validate}",
                        actual={
                            "validate": actual_validate,
                            "error_count": len(errors),
                            "errors": error_msgs,
                        },
                        expected={"validate": expected_validate},
                        duration_ms=duration_ms,
                    )

            # Check error count if specified
            if test.expected.error_count is not None:
                actual_count = len(errors)
                if actual_count != test.expected.error_count:
                    return TestResult.failure(
                        test,
                        f"Expected {test.expected.error_count} errors, got {actual_count}",
                        actual={"error_count": actual_count},
                        expected={"error_count": test.expected.error_count},
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
                        actual={"errors": [str(e) for e in errors[:5]]},
                        expected={"error_contains": test.expected.error_contains},
                        duration_ms=duration_ms,
                    )

            # Check accounts if specified
            if test.expected.accounts:
                from beancount.core import getters
                actual_accounts = set(getters.get_accounts(entries))
                expected_accounts = set(test.expected.accounts)
                if not expected_accounts.issubset(actual_accounts):
                    missing = expected_accounts - actual_accounts
                    return TestResult.failure(
                        test,
                        f"Missing expected accounts: {missing}",
                        actual={"accounts": sorted(actual_accounts)},
                        expected={"accounts": sorted(expected_accounts)},
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

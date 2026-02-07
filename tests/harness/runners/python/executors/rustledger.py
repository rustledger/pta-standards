"""Rustledger executor - tests against rustledger binary."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from loader import TestCase
from executors.base import BaseExecutor, TestResult


class RustledgerExecutor(BaseExecutor):
    """Executor that runs tests against rustledger binary."""

    def __init__(self):
        """Initialize with rustledger binary path."""
        self.binary = os.environ.get("RLEDGER_BIN", "rledger")

    def _run_check(self, file_path: str) -> tuple[bool, list[dict], str]:
        """Run rledger check on a file.

        Returns:
            Tuple of (success, errors, raw_output)
        """
        try:
            result = subprocess.run(
                [self.binary, "check", "--json", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse JSON output
            if result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    errors = data.get("errors", [])
                    return result.returncode == 0, errors, result.stdout
                except json.JSONDecodeError:
                    # Non-JSON output, check return code
                    pass

            # Fallback to checking stderr for errors
            if result.returncode != 0:
                error_lines = result.stderr.strip().split("\n") if result.stderr else []
                errors = [{"message": line} for line in error_lines if line]
                return False, errors, result.stderr or result.stdout

            return True, [], result.stdout

        except subprocess.TimeoutExpired:
            return False, [{"message": "Timeout after 30 seconds"}], ""
        except FileNotFoundError:
            return False, [{"message": f"Binary not found: {self.binary}"}], ""

    def _run_query(self, file_path: str, query: str) -> tuple[bool, list, list[dict], str]:
        """Run rledger query on a file.

        Returns:
            Tuple of (success, rows, errors, raw_output)
        """
        try:
            result = subprocess.run(
                [self.binary, "query", file_path, query, "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    if "error" in data:
                        return False, [], [{"message": data["error"]}], result.stdout
                    rows = data.get("rows", data.get("results", []))
                    return True, rows, [], result.stdout
                except json.JSONDecodeError:
                    pass

            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Query failed"
                return False, [], [{"message": error_msg}], result.stderr

            return True, [], [], result.stdout

        except subprocess.TimeoutExpired:
            return False, [], [{"message": "Timeout after 30 seconds"}], ""
        except FileNotFoundError:
            return False, [], [{"message": f"Binary not found: {self.binary}"}], ""

    def execute(self, test: TestCase) -> TestResult:
        """Execute a test against rustledger."""
        if test.skip:
            return TestResult.skip(test)

        start_time = time.perf_counter()

        try:
            # Get input content and write to temp file
            if test.input.inline is not None:
                content = test.input.inline
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".beancount", delete=False
                ) as f:
                    f.write(content)
                    temp_path = f.name
                file_path = temp_path
                cleanup = True
            else:
                file_path = test.input.get_file_path(test.base_path)
                if file_path is None:
                    return TestResult.failure(
                        test, "No input file or inline content specified"
                    )
                file_path = str(file_path)
                cleanup = False

            # Determine test type and execute
            test_type = test.get_test_type()

            if test_type == "bql":
                return self._execute_bql(test, file_path, start_time, cleanup)
            else:
                return self._execute_check(test, file_path, start_time, cleanup)

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return TestResult.failure(
                test,
                f"Executor error: {type(e).__name__}: {e}",
                duration_ms=duration_ms,
            )

    def _execute_check(
        self, test: TestCase, file_path: str, start_time: float, cleanup: bool
    ) -> TestResult:
        """Execute a parse/validation test."""
        try:
            success, errors, raw = self._run_check(file_path)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Check parse result
            actual_parse = "success" if success else "error"
            expected_parse = test.expected.parse

            if expected_parse is not None:
                if actual_parse != expected_parse:
                    error_msgs = [e.get("message", str(e)) for e in errors[:3]]
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
                actual_validate = "success" if success else "error"
                if actual_validate != expected_validate:
                    error_msgs = [e.get("message", str(e)) for e in errors[:5]]
                    return TestResult.failure(
                        test,
                        f"Expected validate={expected_validate}, got {actual_validate}",
                        actual={"validate": actual_validate, "errors": error_msgs},
                        expected={"validate": expected_validate},
                        duration_ms=duration_ms,
                    )

            # Check error_contains if specified
            if test.expected.error_contains:
                error_messages = [e.get("message", str(e)) for e in errors]
                all_errors = " ".join(error_messages)
                if test.expected.error_contains.lower() not in all_errors.lower():
                    return TestResult.failure(
                        test,
                        f"Expected error containing '{test.expected.error_contains}'",
                        actual={"errors": error_messages[:5]},
                        expected={"error_contains": test.expected.error_contains},
                        duration_ms=duration_ms,
                    )

            return TestResult.success(test, duration_ms=duration_ms)

        finally:
            if cleanup:
                Path(file_path).unlink(missing_ok=True)

    def _execute_bql(
        self, test: TestCase, file_path: str, start_time: float, cleanup: bool
    ) -> TestResult:
        """Execute a BQL query test."""
        try:
            query = test.input.query
            if not query:
                return TestResult.failure(test, "No query specified in input")

            success, rows, errors, raw = self._run_query(file_path, query)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Check query result
            expected_query = test.expected.query
            if expected_query is not None:
                actual_query = "success" if success else "error"
                if actual_query != expected_query:
                    error_msgs = [e.get("message", str(e)) for e in errors[:3]]
                    return TestResult.failure(
                        test,
                        f"Expected query={expected_query}, got {actual_query}",
                        actual={"query": actual_query, "errors": error_msgs},
                        expected={"query": expected_query},
                        duration_ms=duration_ms,
                    )

            # Check row count if specified
            if test.expected.row_count is not None:
                actual_count = len(rows)
                if actual_count != test.expected.row_count:
                    return TestResult.failure(
                        test,
                        f"Expected {test.expected.row_count} rows, got {actual_count}",
                        actual={"row_count": actual_count},
                        expected={"row_count": test.expected.row_count},
                        duration_ms=duration_ms,
                    )

            # Check error_contains if specified
            if test.expected.error_contains:
                error_messages = [e.get("message", str(e)) for e in errors]
                all_errors = " ".join(error_messages)
                if test.expected.error_contains.lower() not in all_errors.lower():
                    return TestResult.failure(
                        test,
                        f"Expected error containing '{test.expected.error_contains}'",
                        actual={"errors": error_messages[:5]},
                        expected={"error_contains": test.expected.error_contains},
                        duration_ms=duration_ms,
                    )

            return TestResult.success(test, duration_ms=duration_ms)

        finally:
            if cleanup:
                Path(file_path).unlink(missing_ok=True)

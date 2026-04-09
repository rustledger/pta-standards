"""Rustledger executor - tests against rustledger binary."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from executors.base import BaseExecutor, TestResult
from loader import TestCase


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
                [self.binary, "check", "--format", "json", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse JSON output
            if result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    # rustledger outputs {diagnostics: [...], error_count: N, warning_count: N}
                    diagnostics = data.get("diagnostics", data.get("errors", []))
                    error_diagnostics = [
                        d for d in diagnostics if d.get("severity", "error") == "error"
                    ]
                    has_errors = data.get("error_count", len(error_diagnostics)) > 0
                    return not has_errors, diagnostics, result.stdout
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
                [self.binary, "query", "--format", "json", file_path, query],
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
                with tempfile.NamedTemporaryFile(mode="w", suffix=".beancount", delete=False) as f:
                    f.write(content)
                    temp_path = f.name
                file_path = temp_path
                cleanup = True
            else:
                resolved_path = test.input.get_file_path(test.base_path)
                if resolved_path is None:
                    return TestResult.failure(test, "No input file or inline content specified")
                file_path = str(resolved_path)
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
            _success, errors, _raw = self._run_check(file_path)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Separate parse errors from validation errors using the `phase` field.
            # rustledger tags each diagnostic with "parse" or "validate" based on when
            # it was detected (lex/parse/load vs. semantic validation). This is more
            # accurate than classifying by code prefix alone — for example, E7001
            # (unknown option) fires during the load phase and is correctly tagged
            # phase="parse" even though its code starts with E.
            #
            # Fall back to the legacy code-prefix heuristic (P* = parse) for older
            # rustledger builds that don't emit the `phase` field, so the runner
            # remains backwards compatible.
            def _is_parse_error(e: dict) -> bool:
                phase = e.get("phase")
                if phase is not None:
                    return bool(phase == "parse")
                return bool(str(e.get("code", "")).startswith("P"))

            parse_errors = [e for e in errors if _is_parse_error(e)]
            validation_errors = [e for e in errors if not _is_parse_error(e)]

            # Check parse result
            parse_succeeded = len(parse_errors) == 0
            actual_parse = "success" if parse_succeeded else "error"
            expected_parse = test.expected.parse

            if expected_parse is not None and actual_parse != expected_parse:
                error_msgs = [e.get("message", str(e)) for e in parse_errors[:3]]
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
                actual_validate = "success" if len(validation_errors) == 0 else "error"
                if actual_validate != expected_validate:
                    error_msgs = [e.get("message", str(e)) for e in validation_errors[:5]]
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
                all_errors = " ".join(error_messages).lower()
                for substring in test.expected.error_contains:
                    if substring.lower() not in all_errors:
                        return TestResult.failure(
                            test,
                            f"Expected error containing '{substring}'",
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

            success, rows, errors, _raw = self._run_query(file_path, query)
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
                all_errors = " ".join(error_messages).lower()
                for substring in test.expected.error_contains:
                    if substring.lower() not in all_errors:
                        return TestResult.failure(
                            test,
                            f"Expected error containing '{substring}'",
                            actual={"errors": error_messages[:5]},
                            expected={"error_contains": test.expected.error_contains},
                            duration_ms=duration_ms,
                        )

            return TestResult.success(test, duration_ms=duration_ms)

        finally:
            if cleanup:
                Path(file_path).unlink(missing_ok=True)

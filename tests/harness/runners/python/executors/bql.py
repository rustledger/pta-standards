"""BQL test executor - tests Beancount Query Language."""

from __future__ import annotations

import time
import tempfile
from pathlib import Path

import beanquery

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from loader import TestCase
from executors.base import BaseExecutor, TestResult


class BQLExecutor(BaseExecutor):
    """Executor for BQL query tests."""

    def execute(self, test: TestCase) -> TestResult:
        """Execute a BQL test."""
        if test.skip:
            return TestResult.skip(test)

        start_time = time.perf_counter()
        temp_path = None

        try:
            # BQL tests require a query
            query = test.input.query
            if query is None:
                return TestResult.failure(
                    test, "BQL test missing query in input"
                )

            # Determine the file path for beanquery connection
            if test.input.file is not None:
                file_path = test.input.get_file_path(test.base_path)
                if file_path is None:
                    return TestResult.failure(test, "Could not resolve input file")
                dsn = f"beancount://{file_path}"
            elif test.input.inline is not None:
                content = test.input.inline
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".beancount", delete=False
                ) as f:
                    f.write(content)
                    temp_path = f.name
                dsn = f"beancount://{temp_path}"
            else:
                return TestResult.failure(
                    test, "BQL test requires input file or inline content"
                )

            # Execute the query using beanquery
            result_rows = None
            result_columns = None
            try:
                conn = beanquery.connect(dsn)
                cursor = conn.execute(query)
                result_columns = [col.name for col in cursor.description] if cursor.description else []
                result_rows = list(cursor)
                conn.close()
                query_succeeded = True
                query_error = None

            except Exception as e:
                query_succeeded = False
                query_error = str(e)
                result_columns = None
                result_rows = None

            duration_ms = (time.perf_counter() - start_time) * 1000

            # Clean up temp file
            if temp_path:
                Path(temp_path).unlink()

            # Check query result
            expected_query = test.expected.query
            if expected_query is not None:
                actual_query = "success" if query_succeeded else "error"

                if actual_query != expected_query:
                    return TestResult.failure(
                        test,
                        f"Expected query={expected_query}, got {actual_query}",
                        actual={
                            "query": actual_query,
                            "error": query_error,
                        },
                        expected={"query": expected_query},
                        duration_ms=duration_ms,
                    )

            # Check error_contains for query errors
            if not query_succeeded and test.expected.error_contains:
                error_lower = (query_error or "").lower()
                for substring in test.expected.error_contains:
                    if substring.lower() not in error_lower:
                        return TestResult.failure(
                            test,
                            f"Expected error containing '{substring}'",
                            actual={"error": query_error},
                            expected={"error_contains": test.expected.error_contains},
                            duration_ms=duration_ms,
                        )

            # Check row count if specified
            if query_succeeded and test.expected.row_count is not None:
                actual_count = len(result_rows) if result_rows else 0
                if actual_count != test.expected.row_count:
                    return TestResult.failure(
                        test,
                        f"Expected {test.expected.row_count} rows, got {actual_count}",
                        actual={"row_count": actual_count},
                        expected={"row_count": test.expected.row_count},
                        duration_ms=duration_ms,
                    )

            # Check columns if specified
            if query_succeeded and test.expected.columns:
                actual_columns = result_columns or []
                expected_columns = test.expected.columns
                if actual_columns != expected_columns:
                    return TestResult.failure(
                        test,
                        f"Column mismatch",
                        actual={"columns": actual_columns},
                        expected={"columns": expected_columns},
                        duration_ms=duration_ms,
                    )

            return TestResult.success(test, duration_ms=duration_ms)

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            # Clean up temp file on error
            if temp_path:
                try:
                    Path(temp_path).unlink()
                except:
                    pass
            return TestResult.failure(
                test,
                f"Executor error: {type(e).__name__}: {e}",
                duration_ms=duration_ms,
            )

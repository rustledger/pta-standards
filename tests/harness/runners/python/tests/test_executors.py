"""Integration tests for SyntaxExecutor, ValidationExecutor, and BQLExecutor.

These tests run against the real beancount/beanquery libraries.
"""

from __future__ import annotations

from pathlib import Path

from executors.bql import BQLExecutor
from executors.syntax import SyntaxExecutor
from executors.validation import ValidationExecutor
from loader import TestCase, TestExpected, TestInput


def _make_test(
    *,
    inline: str | None = None,
    file: str | None = None,
    query: str | None = None,
    parse: str | None = None,
    validate: str | None = None,
    query_expected: str | None = None,
    directives: int | None = None,
    error_contains: list[str] | None = None,
    error_count: int | None = None,
    accounts: list[str] | None = None,
    row_count: int | None = None,
    columns: list[str] | None = None,
    skip: bool = False,
) -> TestCase:
    return TestCase(
        id="test",
        description="test",
        input=TestInput(inline=inline, file=file, query=query),
        expected=TestExpected(
            parse=parse,
            validate=validate,
            query=query_expected,
            directives=directives,
            error_contains=error_contains or [],
            error_count=error_count,
            accounts=accounts or [],
            row_count=row_count,
            columns=columns or [],
        ),
        base_path=Path("."),
        skip=skip,
    )


VALID_LEDGER = (
    "2024-01-01 open Assets:Bank:Checking USD\n"
    "2024-01-01 open Income:Salary\n"
    "\n"
    '2024-01-15 * "Paycheck"\n'
    "  Assets:Bank:Checking  5000 USD\n"
    "  Income:Salary        -5000 USD\n"
)

INVALID_SYNTAX = "this is not valid beancount at all !!!"

UNBALANCED_TXN = (
    "2024-01-01 open Assets:Bank:Checking USD\n"
    "2024-01-01 open Expenses:Food\n"
    "\n"
    '2024-01-15 * "Groceries"\n'
    "  Expenses:Food         50 USD\n"
    "  Assets:Bank:Checking -40 USD\n"
)


class TestSyntaxExecutor:
    def setup_method(self):
        self.executor = SyntaxExecutor()

    def test_skip(self):
        test = _make_test(inline="x", parse="success", skip=True)
        result = self.executor.execute(test)
        assert result.passed is True
        assert result.skipped is True

    def test_valid_parse(self):
        test = _make_test(inline=VALID_LEDGER, parse="success")
        result = self.executor.execute(test)
        assert result.passed is True
        assert result.duration_ms > 0

    def test_invalid_parse_expected(self):
        test = _make_test(inline=INVALID_SYNTAX, parse="error")
        result = self.executor.execute(test)
        assert result.passed is True

    def test_parse_mismatch_expected_success(self):
        test = _make_test(inline=INVALID_SYNTAX, parse="success")
        result = self.executor.execute(test)
        assert result.passed is False
        assert result.error_message is not None and "Expected parse=success" in result.error_message

    def test_parse_mismatch_expected_error(self):
        test = _make_test(inline=VALID_LEDGER, parse="error")
        result = self.executor.execute(test)
        assert result.passed is False
        assert result.error_message is not None and "Expected parse=error" in result.error_message

    def test_directive_count(self):
        # 2 open + 1 transaction = 3 directives
        test = _make_test(inline=VALID_LEDGER, parse="success", directives=3)
        result = self.executor.execute(test)
        assert result.passed is True

    def test_directive_count_mismatch(self):
        test = _make_test(inline=VALID_LEDGER, parse="success", directives=99)
        result = self.executor.execute(test)
        assert result.passed is False
        assert result.error_message is not None and "directives" in result.error_message

    def test_missing_parse_field(self):
        test = _make_test(inline=VALID_LEDGER)
        result = self.executor.execute(test)
        assert result.passed is False
        assert result.error_message is not None and "missing" in result.error_message.lower()

    def test_no_input(self):
        test = _make_test(parse="success")
        result = self.executor.execute(test)
        assert result.passed is False


class TestValidationExecutor:
    def setup_method(self):
        self.executor = ValidationExecutor()

    def test_skip(self):
        test = _make_test(inline="x", validate="success", skip=True)
        result = self.executor.execute(test)
        assert result.passed is True
        assert result.skipped is True

    def test_valid_validation(self):
        test = _make_test(
            inline=VALID_LEDGER,
            parse="success",
            validate="success",
        )
        result = self.executor.execute(test)
        assert result.passed is True

    def test_validation_error_detected(self):
        test = _make_test(
            inline=UNBALANCED_TXN,
            parse="success",
            validate="error",
        )
        result = self.executor.execute(test)
        assert result.passed is True

    def test_validation_error_mismatch(self):
        test = _make_test(
            inline=VALID_LEDGER,
            parse="success",
            validate="error",
        )
        result = self.executor.execute(test)
        assert result.passed is False
        assert result.error_message is not None and "Expected validate=error" in result.error_message

    def test_accounts_check(self):
        test = _make_test(
            inline=VALID_LEDGER,
            parse="success",
            validate="success",
            accounts=["Assets:Bank:Checking", "Income:Salary"],
        )
        result = self.executor.execute(test)
        assert result.passed is True

    def test_accounts_missing(self):
        test = _make_test(
            inline=VALID_LEDGER,
            parse="success",
            validate="success",
            accounts=["Assets:DoesNotExist"],
        )
        result = self.executor.execute(test)
        assert result.passed is False
        assert result.error_message is not None and "Missing" in result.error_message

    def test_error_count(self):
        test = _make_test(
            inline=UNBALANCED_TXN,
            parse="success",
            validate="error",
            error_count=1,
        )
        result = self.executor.execute(test)
        assert result.passed is True


class TestBQLExecutor:
    def setup_method(self):
        self.executor = BQLExecutor()

    def test_skip(self):
        test = _make_test(inline="x", query="q", query_expected="success", skip=True)
        result = self.executor.execute(test)
        assert result.passed is True
        assert result.skipped is True

    def test_missing_query(self):
        test = _make_test(inline=VALID_LEDGER, query_expected="success")
        result = self.executor.execute(test)
        assert result.passed is False
        assert result.error_message is not None and "missing query" in result.error_message.lower()

    def test_select_all(self):
        test = _make_test(
            inline=VALID_LEDGER,
            query="SELECT *",
            query_expected="success",
        )
        result = self.executor.execute(test)
        assert result.passed is True

    def test_row_count(self):
        # 1 transaction with 2 postings = 2 rows
        test = _make_test(
            inline=VALID_LEDGER,
            query="SELECT * FROM postings",
            query_expected="success",
            row_count=2,
        )
        result = self.executor.execute(test)
        assert result.passed is True

    def test_row_count_mismatch(self):
        test = _make_test(
            inline=VALID_LEDGER,
            query="SELECT * FROM postings",
            query_expected="success",
            row_count=99,
        )
        result = self.executor.execute(test)
        assert result.passed is False
        assert result.error_message is not None and "rows" in result.error_message

    def test_query_error_expected(self):
        test = _make_test(
            inline=VALID_LEDGER,
            query="INVALID QUERY SYNTAX",
            query_expected="error",
        )
        result = self.executor.execute(test)
        assert result.passed is True

    def test_query_error_unexpected(self):
        test = _make_test(
            inline=VALID_LEDGER,
            query="INVALID QUERY SYNTAX",
            query_expected="success",
        )
        result = self.executor.execute(test)
        assert result.passed is False
        assert result.error_message is not None and "Expected query=success" in result.error_message

    def test_columns_check(self):
        test = _make_test(
            inline=VALID_LEDGER,
            query="SELECT date, account FROM postings",
            query_expected="success",
            columns=["date", "account"],
        )
        result = self.executor.execute(test)
        assert result.passed is True

    def test_columns_mismatch(self):
        test = _make_test(
            inline=VALID_LEDGER,
            query="SELECT date, account FROM postings",
            query_expected="success",
            columns=["date", "wrong_column"],
        )
        result = self.executor.execute(test)
        assert result.passed is False
        assert result.error_message is not None and "Column" in result.error_message

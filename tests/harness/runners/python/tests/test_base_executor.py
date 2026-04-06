"""Unit tests for the base executor and TestResult."""

from __future__ import annotations

from pathlib import Path

from executors.base import TestResult, BaseExecutor
from loader import TestCase, TestExpected, TestInput


def _make_test(id: str = "t1") -> TestCase:
    return TestCase(
        id=id,
        description="test",
        input=TestInput(inline="x"),
        expected=TestExpected(),
        base_path=Path("."),
    )


class TestTestResult:
    def test_skip(self):
        tc = _make_test()
        tc.skip_reason = "not ready"
        r = TestResult.skip(tc)
        assert r.passed is True
        assert r.skipped is True
        assert r.skip_reason == "not ready"
        assert r.test_id == "t1"

    def test_success(self):
        tc = _make_test()
        r = TestResult.success(tc, duration_ms=42.5)
        assert r.passed is True
        assert r.skipped is False
        assert r.duration_ms == 42.5

    def test_failure(self):
        tc = _make_test()
        r = TestResult.failure(
            tc,
            error_message="boom",
            actual={"parse": "error"},
            expected={"parse": "success"},
            duration_ms=10.0,
        )
        assert r.passed is False
        assert r.error_message == "boom"
        assert r.actual == {"parse": "error"}
        assert r.expected == {"parse": "success"}

    def test_failure_defaults(self):
        tc = _make_test()
        r = TestResult.failure(tc, error_message="err")
        assert r.actual == {}
        assert r.expected == {}


class TestCheckErrorContains:
    class ConcreteExecutor(BaseExecutor):
        def execute(self, test):
            pass

    def test_empty_substrings(self):
        e = self.ConcreteExecutor()
        ok, msg = e.check_error_contains(["some error"], [])
        assert ok is True
        assert msg is None

    def test_match_found(self):
        e = self.ConcreteExecutor()
        ok, msg = e.check_error_contains(["Account not opened"], ["not opened"])
        assert ok is True

    def test_match_case_insensitive(self):
        e = self.ConcreteExecutor()
        ok, msg = e.check_error_contains(["ACCOUNT NOT OPENED"], ["not opened"])
        assert ok is True

    def test_match_not_found(self):
        e = self.ConcreteExecutor()
        ok, msg = e.check_error_contains(["something else"], ["not opened"])
        assert ok is False
        assert "not opened" in msg

    def test_multiple_substrings_all_match(self):
        e = self.ConcreteExecutor()
        ok, msg = e.check_error_contains(
            ["Account not opened; balance error"],
            ["not opened", "balance"],
        )
        assert ok is True

    def test_multiple_substrings_partial_match(self):
        e = self.ConcreteExecutor()
        ok, msg = e.check_error_contains(
            ["Account not opened"],
            ["not opened", "balance"],
        )
        assert ok is False
        assert "balance" in msg

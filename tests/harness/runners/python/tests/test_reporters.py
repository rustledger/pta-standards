"""Unit tests for TAP and JSON reporters."""

from __future__ import annotations

import io
import json

from executors.base import TestResult
from reporters.tap import TAPReporter
from reporters.json_reporter import JSONReporter


def _make_results() -> tuple[list[TestResult], dict[str, str]]:
    results = [
        TestResult(test_id="t1", passed=True, duration_ms=5.0),
        TestResult(
            test_id="t2",
            passed=False,
            error_message="expected success",
            expected={"parse": "success"},
            actual={"parse": "error"},
            duration_ms=3.0,
        ),
        TestResult(
            test_id="t3",
            passed=True,
            skipped=True,
            skip_reason="not ready",
        ),
    ]
    descriptions = {
        "t1": "passing test",
        "t2": "failing test",
        "t3": "skipped test",
    }
    return results, descriptions


class TestTAPReporter:
    def test_report_format(self):
        results, descs = _make_results()
        buf = io.StringIO()
        reporter = TAPReporter(output=buf)
        reporter.report(results, descs)

        output = buf.getvalue()
        assert output.startswith("TAP version 14\n")
        assert "1..3" in output
        assert "ok 1 - t1: passing test" in output
        assert "not ok 2 - t2: failing test" in output
        assert "# SKIP not ready" in output

    def test_failure_diagnostics(self):
        results, descs = _make_results()
        buf = io.StringIO()
        reporter = TAPReporter(output=buf)
        reporter.report(results, descs)

        output = buf.getvalue()
        assert "message:" in output
        assert "expected:" in output
        assert "actual:" in output

    def test_summary(self):
        results, _ = _make_results()
        buf = io.StringIO()
        reporter = TAPReporter(output=buf)
        reporter.summary(results)

        output = buf.getvalue()
        assert "Passed: 1" in output
        assert "Failed: 1" in output
        assert "Skipped: 1" in output

    def test_verbose_shows_duration(self):
        results = [TestResult(test_id="t1", passed=True, duration_ms=5.0)]
        descs = {"t1": "test"}
        buf = io.StringIO()
        reporter = TAPReporter(output=buf, verbose=True)
        reporter.report(results, descs)

        output = buf.getvalue()
        assert "duration_ms:" in output


class TestJSONReporter:
    def test_report_structure(self):
        results, descs = _make_results()
        buf = io.StringIO()
        reporter = JSONReporter(output=buf)
        reporter.report(results, descs)

        data = json.loads(buf.getvalue())
        assert data["summary"]["total"] == 3
        assert data["summary"]["passed"] == 1
        assert data["summary"]["failed"] == 1
        assert data["summary"]["skipped"] == 1

    def test_result_details(self):
        results, descs = _make_results()
        buf = io.StringIO()
        reporter = JSONReporter(output=buf)
        reporter.report(results, descs)

        data = json.loads(buf.getvalue())
        r = data["results"]

        assert r[0]["status"] == "pass"
        assert r[0]["description"] == "passing test"

        assert r[1]["status"] == "fail"
        assert r[1]["error"] == "expected success"
        assert "expected" in r[1]
        assert "actual" in r[1]

        assert r[2]["status"] == "skip"
        assert r[2]["skip_reason"] == "not ready"

    def test_summary_is_noop(self):
        buf = io.StringIO()
        reporter = JSONReporter(output=buf)
        reporter.summary([])
        assert buf.getvalue() == ""

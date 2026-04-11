"""Unit tests for the test loader module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from loader import (
    TestCase,
    TestExpected,
    TestInput,
    filter_tests,
    load_manifest,
    load_test_suite,
)


@pytest.fixture
def tmp_manifest(tmp_path: Path) -> Path:
    """Create a minimal manifest.json for testing."""
    manifest = {
        "format": "beancount",
        "version": "3",
        "description": "Test manifest",
        "test_directories": ["suite_a"],
        "metadata": {"author": "test"},
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))

    # Create a test suite directory with tests.json
    suite_dir = tmp_path / "suite_a"
    suite_dir.mkdir()
    tests_json = {
        "suite": "suite_a",
        "tests": [
            {
                "id": "test-1",
                "description": "First test",
                "input": {"inline": "2024-01-01 open Assets:Bank"},
                "expected": {"parse": "success", "directives": 1},
                "tags": ["syntax", "open"],
            },
            {
                "id": "test-2",
                "description": "Second test",
                "input": {"file": "input.beancount"},
                "expected": {"parse": "error", "error_contains": ["invalid"]},
                "tags": ["syntax", "error"],
                "skip": True,
                "skip_reason": "Not yet implemented",
            },
        ],
    }
    (suite_dir / "tests.json").write_text(json.dumps(tests_json))
    (suite_dir / "input.beancount").write_text("bad input\n")
    return manifest_path


class TestTestInput:
    def test_inline_content(self):
        ti = TestInput(inline="hello")
        assert ti.get_content(Path(".")) == "hello"

    def test_file_content(self, tmp_path: Path):
        (tmp_path / "data.txt").write_text("file content")
        ti = TestInput(file="data.txt")
        assert ti.get_content(tmp_path) == "file content"

    def test_no_content_raises(self):
        ti = TestInput()
        with pytest.raises(ValueError, match=r"inline.*file"):
            ti.get_content(Path("."))

    def test_get_file_path_returns_none_for_inline(self):
        ti = TestInput(inline="x")
        assert ti.get_file_path(Path("/base")) is None

    def test_get_file_path_resolves(self):
        ti = TestInput(file="sub/file.bean")
        assert ti.get_file_path(Path("/base")) == Path("/base/sub/file.bean")


class TestTestCase:
    def test_get_test_type_syntax(self):
        tc = TestCase(
            id="t",
            description="d",
            input=TestInput(inline="x"),
            expected=TestExpected(parse="success"),
            base_path=Path("."),
        )
        assert tc.get_test_type() == "syntax"

    def test_get_test_type_validation(self):
        tc = TestCase(
            id="t",
            description="d",
            input=TestInput(inline="x"),
            expected=TestExpected(validate="success"),
            base_path=Path("."),
        )
        assert tc.get_test_type() == "validation"

    def test_get_test_type_bql(self):
        tc = TestCase(
            id="t",
            description="d",
            input=TestInput(inline="x"),
            expected=TestExpected(query="success"),
            base_path=Path("."),
        )
        assert tc.get_test_type() == "bql"


class TestLoadManifest:
    def test_load_manifest(self, tmp_manifest: Path):
        m = load_manifest(tmp_manifest)
        assert m.format == "beancount"
        assert m.version == "3"
        assert m.description == "Test manifest"
        assert m.test_directories == ["suite_a"]
        assert m.metadata == {"author": "test"}
        assert m.base_path == tmp_manifest.parent


class TestLoadTestSuite:
    def test_load_test_suite(self, tmp_manifest: Path):
        suite_path = tmp_manifest.parent / "suite_a" / "tests.json"
        tests = load_test_suite(suite_path)

        assert len(tests) == 2

        t1 = tests[0]
        assert t1.id == "test-1"
        assert t1.description == "First test"
        assert t1.input.inline == "2024-01-01 open Assets:Bank"
        assert t1.expected.parse == "success"
        assert t1.expected.directives == 1
        assert t1.tags == ["syntax", "open"]
        assert t1.skip is False
        assert t1.suite == "suite_a"

        t2 = tests[1]
        assert t2.id == "test-2"
        assert t2.skip is True
        assert t2.skip_reason == "Not yet implemented"
        assert t2.input.file == "input.beancount"
        assert t2.expected.error_contains == ["invalid"]


class TestFilterTests:
    def _make_tests(self):
        def tc(id, suite, tags):
            return TestCase(
                id=id,
                description=id,
                input=TestInput(inline="x"),
                expected=TestExpected(),
                base_path=Path("."),
                suite=suite,
                tags=tags,
            )

        return [
            tc("a", "syntax", ["open", "basic"]),
            tc("b", "syntax", ["error"]),
            tc("c", "validation", ["open"]),
        ]

    def test_no_filter(self):
        tests = self._make_tests()
        assert filter_tests(tests) == tests

    def test_filter_by_id(self):
        tests = self._make_tests()
        result = filter_tests(tests, test_id="b")
        assert len(result) == 1
        assert result[0].id == "b"

    def test_filter_by_suite(self):
        tests = self._make_tests()
        result = filter_tests(tests, suite="syntax")
        assert len(result) == 2

    def test_filter_by_tags(self):
        tests = self._make_tests()
        result = filter_tests(tests, tags=["open"])
        assert len(result) == 2

    def test_filter_combined(self):
        tests = self._make_tests()
        result = filter_tests(tests, suite="syntax", tags=["open"])
        assert len(result) == 1
        assert result[0].id == "a"

"""Test case and manifest loading."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TestInput:
    """Test input specification."""

    inline: str | None = None
    file: str | None = None
    query: str | None = None

    def get_content(self, base_path: Path) -> str:
        """Get the input content, resolving file paths if needed."""
        if self.inline is not None:
            return self.inline
        if self.file is not None:
            file_path = base_path / self.file
            return file_path.read_text()
        raise ValueError("Test input must have either 'inline' or 'file'")

    def get_file_path(self, base_path: Path) -> Path | None:
        """Get the file path if this is a file-based input."""
        if self.file is not None:
            return base_path / self.file
        return None


@dataclass
class TestExpected:
    """Expected test outcome."""

    parse: str | None = None  # "success" or "error"
    validate: str | None = None  # "success", "error", or "skip"
    query: str | None = None  # "success" or "error"
    error_count: int | None = None
    error_types: list[str] = field(default_factory=list)
    error_contains: list[str] = field(default_factory=list)
    directives: int | None = None
    accounts: list[str] = field(default_factory=list)
    balance: dict[str, dict[str, str]] = field(default_factory=dict)
    row_count: int | None = None
    columns: list[str] = field(default_factory=list)


@dataclass
class TestCase:
    """A single test case."""

    id: str
    description: str
    input: TestInput
    expected: TestExpected
    base_path: Path
    spec_ref: str | None = None
    tags: list[str] = field(default_factory=list)
    skip: bool = False
    skip_reason: str | None = None
    suite: str = ""

    def get_test_type(self) -> str:
        """Determine the test type based on expected fields."""
        if self.expected.query is not None:
            return "bql"
        if self.expected.validate is not None:
            return "validation"
        return "syntax"


@dataclass
class Manifest:
    """Test suite manifest."""

    format: str
    version: str
    description: str
    test_directories: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)
    base_path: Path = field(default_factory=Path)


def load_manifest(path: Path) -> Manifest:
    """Load a manifest.json file."""
    with open(path) as f:
        data = json.load(f)

    return Manifest(
        format=data.get("format", ""),
        version=data.get("version", ""),
        description=data.get("description", ""),
        test_directories=data.get("test_directories", []),
        metadata=data.get("metadata", {}),
        base_path=path.parent,
    )


def load_test_suite(path: Path) -> list[TestCase]:
    """Load a tests.json file and return list of TestCase objects."""
    with open(path) as f:
        data = json.load(f)

    suite_name = data.get("suite", path.parent.name)
    tests = []

    for test_data in data.get("tests", []):
        # Parse input
        input_data = test_data.get("input", {})
        test_input = TestInput(
            inline=input_data.get("inline"),
            file=input_data.get("file"),
            query=input_data.get("query"),
        )

        # Parse expected
        expected_data = test_data.get("expected", {})
        expected = TestExpected(
            parse=expected_data.get("parse"),
            validate=expected_data.get("validate"),
            query=expected_data.get("query"),
            error_count=expected_data.get("error_count"),
            error_types=expected_data.get("error_types", []),
            error_contains=expected_data.get("error_contains", []),
            directives=expected_data.get("directives"),
            accounts=expected_data.get("accounts", []),
            balance=expected_data.get("balance", {}),
            row_count=expected_data.get("row_count"),
            columns=expected_data.get("columns", []),
        )

        test_case = TestCase(
            id=test_data["id"],
            description=test_data["description"],
            input=test_input,
            expected=expected,
            base_path=path.parent,
            spec_ref=test_data.get("spec_ref"),
            tags=test_data.get("tags", []),
            skip=test_data.get("skip", False),
            skip_reason=test_data.get("skip_reason"),
            suite=suite_name,
        )
        tests.append(test_case)

    return tests


def load_all_tests(manifest_path: Path) -> list[TestCase]:
    """Load all tests from a manifest."""
    manifest = load_manifest(manifest_path)
    all_tests = []

    for test_dir in manifest.test_directories:
        tests_file = manifest.base_path / test_dir / "tests.json"
        if tests_file.exists():
            tests = load_test_suite(tests_file)
            all_tests.extend(tests)

    return all_tests


def filter_tests(
    tests: list[TestCase],
    suite: str | None = None,
    tags: list[str] | None = None,
    test_id: str | None = None,
) -> list[TestCase]:
    """Filter tests by suite, tags, or specific test ID."""
    result = tests

    if test_id is not None:
        result = [t for t in result if t.id == test_id]

    if suite is not None:
        result = [t for t in result if t.suite == suite or suite in str(t.base_path)]

    if tags:
        result = [t for t in result if any(tag in t.tags for tag in tags)]

    return result

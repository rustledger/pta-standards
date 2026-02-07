"""Base executor interface and common types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from loader import TestCase


@dataclass
class TestResult:
    """Result of executing a single test."""

    test_id: str
    passed: bool
    skipped: bool = False
    skip_reason: str | None = None
    actual: dict[str, Any] = field(default_factory=dict)
    expected: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    duration_ms: float = 0.0

    @classmethod
    def skip(cls, test: TestCase) -> TestResult:
        """Create a skipped test result."""
        return cls(
            test_id=test.id,
            passed=True,  # Skipped tests count as passed
            skipped=True,
            skip_reason=test.skip_reason,
        )

    @classmethod
    def success(cls, test: TestCase, duration_ms: float = 0.0) -> TestResult:
        """Create a successful test result."""
        return cls(
            test_id=test.id,
            passed=True,
            duration_ms=duration_ms,
        )

    @classmethod
    def failure(
        cls,
        test: TestCase,
        error_message: str,
        actual: dict[str, Any] | None = None,
        expected: dict[str, Any] | None = None,
        duration_ms: float = 0.0,
    ) -> TestResult:
        """Create a failed test result."""
        return cls(
            test_id=test.id,
            passed=False,
            error_message=error_message,
            actual=actual or {},
            expected=expected or {},
            duration_ms=duration_ms,
        )


class BaseExecutor(ABC):
    """Abstract base class for test executors."""

    @abstractmethod
    def execute(self, test: TestCase) -> TestResult:
        """Execute a test and return the result."""
        pass

    def check_error_contains(
        self, errors: list[Any], expected_substrings: list[str]
    ) -> tuple[bool, str | None]:
        """Check if error messages contain expected substrings.

        Returns (success, error_message).
        """
        if not expected_substrings:
            return True, None

        # Combine all error messages
        all_messages = " ".join(str(e) for e in errors).lower()

        for substring in expected_substrings:
            if substring.lower() not in all_messages:
                return False, f"Expected error containing '{substring}' not found in: {all_messages[:200]}"

        return True, None

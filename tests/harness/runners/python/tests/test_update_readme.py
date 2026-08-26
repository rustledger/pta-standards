"""Unit tests for the update_readme script."""

from __future__ import annotations

import sys
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "scripts"))

from update_readme import status_emoji, update_readme


class TestStatusEmoji:
    def test_zero_failures(self):
        assert status_emoji("0") == ":white_check_mark:"

    def test_nonzero_failures(self):
        assert status_emoji("3") == ":x:"


class TestUpdateReadme:
    def test_appends_when_no_markers(self, tmp_path: Path):
        readme = tmp_path / "README.md"
        readme.write_text("# My Project\n\nSome content.\n")

        update_readme(
            str(readme),
            beancount_version="3.0.0",
            beancount_base_passed="10",
            beancount_base_failed="0",
            beancount_addendum_passed="4",
            beancount_addendum_failed="0",
            rustledger_version="0.1.0",
            rustledger_base_passed="8",
            rustledger_base_failed="1",
            rustledger_addendum_passed="3",
            rustledger_addendum_failed="1",
        )

        content = readme.read_text()
        assert "CONFORMANCE-RESULTS-START" in content
        assert "CONFORMANCE-RESULTS-END" in content
        assert "3.0.0" in content
        assert "Beancount v3 Spec" in content
        assert "PTA Beancount v3 Addendum" in content

    def test_replaces_existing_section(self, tmp_path: Path):
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n\n"
            "<!-- CONFORMANCE-RESULTS-START -->\nOLD CONTENT\n"
            "<!-- CONFORMANCE-RESULTS-END -->\n\n"
            "Footer.\n"
        )

        update_readme(
            str(readme),
            beancount_version="3.1.0",
            beancount_base_passed="20",
            beancount_base_failed="0",
            beancount_addendum_passed="4",
            beancount_addendum_failed="0",
            rustledger_version="0.2.0",
            rustledger_base_passed="18",
            rustledger_base_failed="0",
            rustledger_addendum_passed="4",
            rustledger_addendum_failed="0",
        )

        content = readme.read_text()
        assert "OLD CONTENT" not in content
        assert "3.1.0" in content
        assert "Footer." in content
        assert content.count("CONFORMANCE-RESULTS-START") == 1

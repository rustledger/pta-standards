"""Unit tests for the update_readme script."""

from __future__ import annotations

from pathlib import Path

import sys

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "scripts"))

from update_readme import update_readme, status_emoji, MARKER_PATTERN


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
            beancount_passed="10",
            beancount_failed="0",
            beancount_skipped="2",
            rustledger_version="0.1.0",
            rustledger_passed="8",
            rustledger_failed="1",
            rustledger_skipped="3",
        )

        content = readme.read_text()
        assert "CONFORMANCE-RESULTS-START" in content
        assert "CONFORMANCE-RESULTS-END" in content
        assert "3.0.0" in content
        assert ":white_check_mark:" in content
        assert ":x:" in content

    def test_replaces_existing_section(self, tmp_path: Path):
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n\n"
            "<!-- CONFORMANCE-RESULTS-START -->\nOLD CONTENT\n<!-- CONFORMANCE-RESULTS-END -->\n\n"
            "Footer.\n"
        )

        update_readme(
            str(readme),
            beancount_version="3.1.0",
            beancount_passed="20",
            beancount_failed="0",
            beancount_skipped="0",
            rustledger_version="0.2.0",
            rustledger_passed="18",
            rustledger_failed="0",
            rustledger_skipped="0",
        )

        content = readme.read_text()
        assert "OLD CONTENT" not in content
        assert "3.1.0" in content
        assert "Footer." in content
        assert content.count("CONFORMANCE-RESULTS-START") == 1

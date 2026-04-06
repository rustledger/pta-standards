#!/usr/bin/env python3
"""Update README.md with conformance test results.

Replaces the section between CONFORMANCE-RESULTS-START and
CONFORMANCE-RESULTS-END markers with current test data.
"""

from __future__ import annotations

import argparse
import re
from datetime import UTC, datetime

RESULTS_TEMPLATE = """\
<!-- CONFORMANCE-RESULTS-START -->
## Conformance Test Results

Last updated: {date}

| Implementation | Version | Passed | Failed | Skipped | Status |
|---------------|---------|--------|--------|---------|--------|
| Python beancount | {beancount_version} | {beancount_passed} | {beancount_failed} | {beancount_skipped} | {beancount_status} |
| Rustledger | {rustledger_version} | {rustledger_passed} | {rustledger_failed} | {rustledger_skipped} | {rustledger_status} |

Tests run nightly against `main` branches. See [conformance documentation](formats/beancount/v3/conformance/) for details.
<!-- CONFORMANCE-RESULTS-END -->"""

MARKER_PATTERN = re.compile(
    r"<!-- CONFORMANCE-RESULTS-START -->.*?<!-- CONFORMANCE-RESULTS-END -->",
    re.DOTALL,
)


def status_emoji(failed: str) -> str:
    return ":white_check_mark:" if failed == "0" else ":x:"


def update_readme(
    readme_path: str,
    beancount_version: str,
    beancount_passed: str,
    beancount_failed: str,
    beancount_skipped: str,
    rustledger_version: str,
    rustledger_passed: str,
    rustledger_failed: str,
    rustledger_skipped: str,
) -> None:
    date = datetime.now(UTC).strftime("%Y-%m-%d")

    section = RESULTS_TEMPLATE.format(
        date=date,
        beancount_version=beancount_version,
        beancount_passed=beancount_passed,
        beancount_failed=beancount_failed,
        beancount_skipped=beancount_skipped,
        beancount_status=status_emoji(beancount_failed),
        rustledger_version=rustledger_version,
        rustledger_passed=rustledger_passed,
        rustledger_failed=rustledger_failed,
        rustledger_skipped=rustledger_skipped,
        rustledger_status=status_emoji(rustledger_failed),
    )

    with open(readme_path) as f:
        content = f.read()

    if MARKER_PATTERN.search(content):
        content = MARKER_PATTERN.sub(section, content)
    else:
        content = content.rstrip() + "\n\n" + section + "\n"

    with open(readme_path, "w") as f:
        f.write(content)

    print(f"Updated {readme_path} with results from {date}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update README with conformance results")
    parser.add_argument("--readme", default="README.md", help="Path to README.md")
    parser.add_argument("--beancount-version", required=True)
    parser.add_argument("--beancount-passed", required=True)
    parser.add_argument("--beancount-failed", required=True)
    parser.add_argument("--beancount-skipped", required=True)
    parser.add_argument("--rustledger-version", required=True)
    parser.add_argument("--rustledger-passed", required=True)
    parser.add_argument("--rustledger-failed", required=True)
    parser.add_argument("--rustledger-skipped", required=True)
    args = parser.parse_args()

    update_readme(
        readme_path=args.readme,
        beancount_version=args.beancount_version,
        beancount_passed=args.beancount_passed,
        beancount_failed=args.beancount_failed,
        beancount_skipped=args.beancount_skipped,
        rustledger_version=args.rustledger_version,
        rustledger_passed=args.rustledger_passed,
        rustledger_failed=args.rustledger_failed,
        rustledger_skipped=args.rustledger_skipped,
    )


if __name__ == "__main__":
    main()

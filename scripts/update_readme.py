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

### Beancount v3 Spec

| Implementation | Version | Passed | Failed | Status |
|---------------|---------|--------|--------|--------|
| Python beancount | {beancount_version} | {beancount_base_passed} | {beancount_base_failed} | {beancount_base_status} |
| Rustledger | {rustledger_version} | {rustledger_base_passed} | {rustledger_base_failed} | {rustledger_base_status} |

### PTA Beancount v3 Addendum

| Implementation | Version | Passed | Failed | Status |
|---------------|---------|--------|--------|--------|
| Python beancount | {beancount_version} | {beancount_addendum_passed} | {beancount_addendum_failed} | {beancount_addendum_status} |
| Rustledger | {rustledger_version} | {rustledger_addendum_passed} | {rustledger_addendum_failed} | {rustledger_addendum_status} |

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
    beancount_base_passed: str,
    beancount_base_failed: str,
    beancount_addendum_passed: str,
    beancount_addendum_failed: str,
    rustledger_version: str,
    rustledger_base_passed: str,
    rustledger_base_failed: str,
    rustledger_addendum_passed: str,
    rustledger_addendum_failed: str,
) -> None:
    date = datetime.now(UTC).strftime("%Y-%m-%d")

    section = RESULTS_TEMPLATE.format(
        date=date,
        beancount_version=beancount_version,
        beancount_base_passed=beancount_base_passed,
        beancount_base_failed=beancount_base_failed,
        beancount_base_status=status_emoji(beancount_base_failed),
        beancount_addendum_passed=beancount_addendum_passed,
        beancount_addendum_failed=beancount_addendum_failed,
        beancount_addendum_status=status_emoji(beancount_addendum_failed),
        rustledger_version=rustledger_version,
        rustledger_base_passed=rustledger_base_passed,
        rustledger_base_failed=rustledger_base_failed,
        rustledger_base_status=status_emoji(rustledger_base_failed),
        rustledger_addendum_passed=rustledger_addendum_passed,
        rustledger_addendum_failed=rustledger_addendum_failed,
        rustledger_addendum_status=status_emoji(rustledger_addendum_failed),
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
    parser.add_argument("--beancount-base-passed", required=True)
    parser.add_argument("--beancount-base-failed", required=True)
    parser.add_argument("--beancount-addendum-passed", required=True)
    parser.add_argument("--beancount-addendum-failed", required=True)
    parser.add_argument("--rustledger-version", required=True)
    parser.add_argument("--rustledger-base-passed", required=True)
    parser.add_argument("--rustledger-base-failed", required=True)
    parser.add_argument("--rustledger-addendum-passed", required=True)
    parser.add_argument("--rustledger-addendum-failed", required=True)
    args = parser.parse_args()

    update_readme(
        readme_path=args.readme,
        beancount_version=args.beancount_version,
        beancount_base_passed=args.beancount_base_passed,
        beancount_base_failed=args.beancount_base_failed,
        beancount_addendum_passed=args.beancount_addendum_passed,
        beancount_addendum_failed=args.beancount_addendum_failed,
        rustledger_version=args.rustledger_version,
        rustledger_base_passed=args.rustledger_base_passed,
        rustledger_base_failed=args.rustledger_base_failed,
        rustledger_addendum_passed=args.rustledger_addendum_passed,
        rustledger_addendum_failed=args.rustledger_addendum_failed,
    )


if __name__ == "__main__":
    main()

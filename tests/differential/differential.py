#!/usr/bin/env python3
"""Differential testing runner for PTA implementations.

Compares output from multiple implementations to find discrepancies.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ImplResult:
    """Result from running an implementation."""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    error_count: int = 0
    balances: dict[str, dict[str, str]] = field(default_factory=dict)


@dataclass
class Divergence:
    """A detected divergence between implementations."""
    id: str
    input_file: str
    dimension: str
    implementations: dict[str, Any]
    classification: str = "unknown"
    notes: str = ""


@dataclass
class Config:
    """Differential testing configuration."""
    implementations: dict[str, dict]
    comparisons: dict[str, dict]
    groups: dict[str, dict]

    @classmethod
    def load(cls, path: Path) -> "Config":
        with open(path) as f:
            data = json.load(f)
        return cls(
            implementations=data.get("implementations", {}),
            comparisons=data.get("comparisons", {}),
            groups=data.get("groups", {}),
        )


def run_implementation(impl_config: dict, input_file: Path, command_type: str = "parse") -> ImplResult:
    """Run an implementation on an input file."""
    cmd_template = impl_config.get("commands", {}).get(command_type)
    if not cmd_template:
        return ImplResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=f"No {command_type} command configured",
            duration_ms=0,
        )

    cmd = cmd_template.format(file=str(input_file))

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        duration_ms = (time.time() - start) * 1000

        return ImplResult(
            success=result.returncode == 0,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_ms=duration_ms,
        )
    except subprocess.TimeoutExpired:
        return ImplResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr="Timeout after 30 seconds",
            duration_ms=30000,
        )
    except Exception as e:
        return ImplResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=str(e),
            duration_ms=0,
        )


def normalize_output(output: str, config: dict) -> str:
    """Normalize implementation output for comparison."""
    lines = output.strip().split('\n')

    if config.get("strip_paths", True):
        # Remove file paths from error messages
        lines = [line.split(':')[-1] if ':' in line else line for line in lines]

    if config.get("sort_accounts", True):
        lines = sorted(lines)

    return '\n'.join(lines)


def compare_results(
    results: dict[str, ImplResult],
    comparison_config: dict,
) -> list[str]:
    """Compare results from multiple implementations.

    Returns list of differences found.
    """
    differences = []
    impl_names = list(results.keys())

    if len(impl_names) < 2:
        return []

    reference = impl_names[0]
    ref_result = results[reference]

    for impl in impl_names[1:]:
        impl_result = results[impl]

        # Compare exit codes if configured
        if comparison_config.get("compare", {}).get("exit_code", True):
            if ref_result.success != impl_result.success:
                differences.append(
                    f"Exit status differs: {reference}={ref_result.success}, {impl}={impl_result.success}"
                )

        # Compare error presence
        if comparison_config.get("compare", {}).get("has_errors", True):
            ref_has_errors = bool(ref_result.stderr.strip())
            impl_has_errors = bool(impl_result.stderr.strip())
            if ref_has_errors != impl_has_errors:
                differences.append(
                    f"Error presence differs: {reference}={ref_has_errors}, {impl}={impl_has_errors}"
                )

    return differences


def find_input_files(input_source: str, base_path: Path) -> list[Path]:
    """Find all input files from a source."""
    files = []

    if input_source == "conformance":
        # Look for .beancount files in conformance test directories
        for pattern in ["**/*.beancount", "**/*.ledger", "**/*.journal"]:
            files.extend(base_path.parent.glob(pattern))
    else:
        source_path = base_path / input_source
        if source_path.is_file():
            files = [source_path]
        elif source_path.is_dir():
            for ext in [".beancount", ".ledger", ".journal"]:
                files.extend(source_path.glob(f"**/*{ext}"))

    return sorted(files)


def run_differential_test(
    config: Config,
    input_file: Path,
    impl_names: list[str],
) -> tuple[bool, list[str]]:
    """Run differential test on a single input file.

    Returns (match, differences).
    """
    results = {}

    for impl_name in impl_names:
        impl_config = config.implementations.get(impl_name)
        if not impl_config:
            continue

        result = run_implementation(impl_config, input_file)
        results[impl_name] = result

    # Compare results
    parse_config = config.comparisons.get("parse", {})
    differences = compare_results(results, parse_config)

    return len(differences) == 0, differences


def main():
    parser = argparse.ArgumentParser(
        description="Differential testing for PTA implementations",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent / "config.json",
        help="Path to config.json",
    )
    parser.add_argument(
        "--group",
        type=str,
        help="Implementation group to test (e.g., 'beancount', 'ledger')",
    )
    parser.add_argument(
        "--impls",
        type=str,
        help="Comma-separated list of implementations to compare",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Single input file to test",
    )
    parser.add_argument(
        "--inputs",
        type=str,
        default="conformance",
        help="Input source: 'conformance', path to directory, or path to file",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Output report to JSON file",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of files to test",
    )

    args = parser.parse_args()

    # Load config
    if not args.config.exists():
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    config = Config.load(args.config)

    # Determine implementations to test
    if args.impls:
        impl_names = [i.strip() for i in args.impls.split(",")]
    elif args.group:
        group = config.groups.get(args.group)
        if not group:
            print(f"Error: Unknown group: {args.group}", file=sys.stderr)
            sys.exit(1)
        impl_names = group.get("implementations", [])
    else:
        # Default to beancount group
        impl_names = config.groups.get("beancount", {}).get("implementations", [])

    if len(impl_names) < 2:
        print("Error: Need at least 2 implementations to compare", file=sys.stderr)
        sys.exit(1)

    # Find input files
    if args.file:
        input_files = [args.file]
    else:
        input_files = find_input_files(args.inputs, args.config.parent)

    if args.limit:
        input_files = input_files[:args.limit]

    if not input_files:
        print("No input files found", file=sys.stderr)
        sys.exit(1)

    print(f"Testing {len(input_files)} files with implementations: {', '.join(impl_names)}")
    print()

    # Run tests
    divergences = []
    matching = 0
    diverging = 0
    errors = 0

    for i, input_file in enumerate(input_files, 1):
        if args.verbose:
            print(f"[{i}/{len(input_files)}] {input_file.name}...", end=" ")

        try:
            match, differences = run_differential_test(config, input_file, impl_names)

            if match:
                matching += 1
                if args.verbose:
                    print("OK")
            else:
                diverging += 1
                if args.verbose:
                    print("DIVERGE")
                    for diff in differences:
                        print(f"  - {diff}")

                divergences.append(Divergence(
                    id=f"div-{len(divergences)+1:03d}",
                    input_file=str(input_file),
                    dimension="parse",
                    implementations={impl: "see details" for impl in impl_names},
                    notes="; ".join(differences),
                ))
        except Exception as e:
            errors += 1
            if args.verbose:
                print(f"ERROR: {e}")

    # Print summary
    print()
    print("=" * 60)
    print(f"Results: {matching} matching, {diverging} diverging, {errors} errors")
    print(f"Total files: {len(input_files)}")

    # Write report if requested
    if args.report:
        report = {
            "run": {
                "timestamp": datetime.now().isoformat(),
                "implementations": impl_names,
                "input_count": len(input_files),
            },
            "summary": {
                "total_inputs": len(input_files),
                "matching": matching,
                "diverging": diverging,
                "errors": errors,
            },
            "divergences": [asdict(d) for d in divergences],
        }

        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nReport written to: {args.report}")

    # Exit with appropriate code
    sys.exit(1 if diverging > 0 or errors > 0 else 0)


if __name__ == "__main__":
    main()

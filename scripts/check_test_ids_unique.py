#!/usr/bin/env python3
"""Validate that test IDs are unique within each test manifest's scope.

Loads each manifest.json, iterates its test_directories, and verifies
that no test ID appears in more than one directory within the same
manifest. Exits non-zero if duplicates are found.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def find_duplicates(manifest_path: Path) -> dict[str, list[str]]:
    """Return {test_id: [directories]} for any ID that appears in more than one directory."""
    manifest = json.loads(manifest_path.read_text())
    base = manifest_path.parent
    id_dirs: dict[str, list[str]] = defaultdict(list)
    for directory in manifest.get("test_directories", []):
        tests_file = base / directory / "tests.json"
        if not tests_file.exists():
            continue
        data = json.loads(tests_file.read_text())
        for test in data.get("tests", []):
            id_dirs[test["id"]].append(directory)
    return {tid: dirs for tid, dirs in id_dirs.items() if len(dirs) > 1}


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    manifests = sorted((repo_root / "tests").rglob("manifest.json"))
    if not manifests:
        print("No manifest.json files found under tests/", file=sys.stderr)
        return 1

    total_dupes = 0
    for manifest_path in manifests:
        rel = manifest_path.relative_to(repo_root)
        dupes = find_duplicates(manifest_path)
        if dupes:
            print(f"{rel}: {len(dupes)} duplicate test ID(s)")
            for tid, dirs in sorted(dupes.items()):
                print(f"  {tid}: {dirs}")
            total_dupes += len(dupes)
        else:
            print(f"{rel}: OK")

    if total_dupes > 0:
        print(f"\nFound {total_dupes} duplicate test ID(s) total", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

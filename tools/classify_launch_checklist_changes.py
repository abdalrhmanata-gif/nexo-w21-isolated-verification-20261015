#!/usr/bin/env python3
"""Classify a changed-path list for the Flutter CI checklist-only fast path."""

from __future__ import annotations

import sys
from pathlib import Path


CHECKLIST_ONLY_PATHS = frozenset(
    {
        ".github/workflows/flutter.yml",
        "docs/ZAVQERA_CONTINUATION_HANDOFF_2026-10-15.md",
        "docs/ZAVQERA_LAUNCH_READINESS_CHECKLIST_2026-10-18.md",
        "tests/test_launch_checklist.py",
        "tests/test_launch_checklist_workflow.py",
        "tools/classify_launch_checklist_changes.py",
        "tools/validate_launch_checklist.py",
    }
)


def is_checklist_only(paths: list[str]) -> bool:
    normalized = [path.replace("\\", "/") for path in paths if path]
    return bool(normalized) and set(normalized) <= CHECKLIST_ONLY_PATHS


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: classify_launch_checklist_changes.py CHANGED_PATHS_FILE", file=sys.stderr)
        return 2
    paths = Path(sys.argv[1]).read_bytes().decode("utf-8").split("\0")
    result = "true" if is_checklist_only(paths) else "false"
    print(f"checklist_only={result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

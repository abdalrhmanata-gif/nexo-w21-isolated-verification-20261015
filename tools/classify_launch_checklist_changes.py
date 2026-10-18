#!/usr/bin/env python3
"""Classify a changed-path list for the Flutter CI checklist-only fast path."""

from __future__ import annotations

import re
import sys
from pathlib import Path


CHECKLIST_ONLY_PATHS = frozenset(
    {
        "docs/ZAVQERA_CONTINUATION_HANDOFF_2026-10-15.md",
        "docs/ZAVQERA_LAUNCH_READINESS_CHECKLIST_2026-10-18.md",
        "tests/test_launch_checklist.py",
        "tests/test_launch_checklist_workflow.py",
        "tools/validate_launch_checklist.py",
    }
)


def parse_change_records(data: bytes) -> list[tuple[str, str, str, str]] | None:
    """Parse `git diff --raw --no-renames -z`; reject incomplete data."""
    try:
        fields = data.decode("utf-8").split("\0")
    except UnicodeDecodeError:
        return None
    if not fields or fields[-1] != "":
        return None
    fields.pop()
    if not fields or len(fields) % 2:
        return None
    records: list[tuple[str, str, str, str]] = []
    for index in range(0, len(fields), 2):
        metadata = fields[index]
        path = fields[index + 1]
        if not metadata.startswith(":") or not path:
            return None
        parts = metadata[1:].split()
        if len(parts) != 5:
            return None
        old_mode, new_mode, _old_object, _new_object, status = parts
        if not re.fullmatch(r"[0-7]{6}", old_mode) or not re.fullmatch(r"[0-7]{6}", new_mode):
            return None
        if not re.fullmatch(r"[0-9a-fA-F]{7,64}", _old_object) or not re.fullmatch(
            r"[0-9a-fA-F]{7,64}", _new_object
        ):
            return None
        records.append((status, old_mode, new_mode, path))
    return records


def is_checklist_only(changes: list[tuple[str, str, str, str]] | None) -> bool:
    if not changes:
        return False
    for status, old_mode, new_mode, path in changes:
        normalized = path.replace("\\", "/")
        if normalized not in CHECKLIST_ONLY_PATHS or new_mode != "100644":
            return False
        if status == "A" and old_mode == "000000":
            continue
        if status == "M" and old_mode == "100644":
            continue
        return False
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: classify_launch_checklist_changes.py CHANGED_PATHS_FILE", file=sys.stderr)
        return 2
    changes = parse_change_records(Path(sys.argv[1]).read_bytes())
    result = "true" if is_checklist_only(changes) else "false"
    print(f"checklist_only={result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

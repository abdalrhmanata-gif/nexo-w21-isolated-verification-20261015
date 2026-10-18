#!/usr/bin/env python3
"""Validate that every launch gate has an auditable, actionable exit record."""

from __future__ import annotations

import re
import sys
from pathlib import Path


GATE_IDS = tuple("ABCDEFGHIJ")
FIELDS = (
    "Status",
    "Required evidence scope",
    "Exit condition",
    "Evidence / exact source SHA",
    "Accountable owner / independent reviewer",
    "Stop condition",
    "Closure action",
)
ALLOWED_STATUSES = {"PASS", "FAIL", "BLOCKED", "N/A"}
ALLOWED_SCOPES = {
    "EXACT_CANDIDATE_CI",
    "RUNTIME_SECURITY_REVIEW",
    "PROVIDER_CONTRACT_REVIEW",
    "HOSTED_READ_ONLY_CAPTURE",
    "AUTHORITATIVE_MIGRATION_PROVENANCE",
    "HOSTED_READ_ONLY_CAPTURE_AND_REVIEW",
    "APPLICATION_BACKUP_RESTORE",
    "OPERATIONAL_EXERCISE",
    "END_TO_END_ACCEPTANCE",
    "INDEPENDENT_RELEASE_APPROVAL",
}
PLACEHOLDERS = re.compile(r"\b(?:TODO|TBD|FIXME|REPLACE ME)\b", re.IGNORECASE)
SHA = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", re.IGNORECASE)


def validate_checklist(text: str) -> list[str]:
    errors: list[str] = []
    gates: dict[str, dict[str, str]] = {}
    current_id: str | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        heading = re.match(r"^###\s+Gate\s+([A-J])\s+—\s+.+$", line)
        if heading:
            gate_id = heading.group(1)
            if gate_id in gates:
                errors.append(f"line {line_number}: duplicate Gate {gate_id}")
            else:
                gates[gate_id] = {}
            current_id = gate_id
            continue
        if line.startswith("### ") or line.startswith("## "):
            current_id = None
            continue
        if current_id is None:
            continue
        field = re.match(r"^- \*\*(.+?):\*\*\s*(.*?)\s*$", line)
        if not field:
            continue
        name, value = field.groups()
        if name in gates[current_id]:
            errors.append(f"line {line_number}: Gate {current_id} repeats {name}")
        gates[current_id][name] = value

    if set(gates) != set(GATE_IDS):
        missing = sorted(set(GATE_IDS) - set(gates))
        extra = sorted(set(gates) - set(GATE_IDS))
        errors.append(f"gate set mismatch (missing={missing}, extra={extra})")

    for gate_id in GATE_IDS:
        if gate_id not in gates:
            continue
        record = gates[gate_id]
        for field in FIELDS:
            value = record.get(field, "").strip()
            if not value:
                errors.append(f"Gate {gate_id}: missing {field}")
            elif PLACEHOLDERS.search(value):
                errors.append(f"Gate {gate_id}: placeholder in {field}")

        status = record.get("Status", "").strip()
        if status not in ALLOWED_STATUSES:
            errors.append(f"Gate {gate_id}: invalid status {status!r}")
        if status == "N/A":
            approval = record.get("Accountable owner / independent reviewer", "")
            if not re.search(r"N/A approved by .+; independent review by .+", approval, re.IGNORECASE):
                errors.append(f"Gate {gate_id}: N/A lacks explicit owner/reviewer approval")

        evidence = record.get("Evidence / exact source SHA", "")
        if not SHA.search(evidence):
            errors.append(f"Gate {gate_id}: evidence must include a full 40-character source SHA")

        owner = record.get("Accountable owner / independent reviewer", "")
        if "/" not in owner or not owner.strip(" /"):
            errors.append(f"Gate {gate_id}: owner and independent reviewer must both be identified")

    decision_match = re.search(r"^##\s+Release decision:\s*(NO-GO|GO)\s*$", text, re.MULTILINE)
    if not decision_match:
        errors.append("release decision must be explicitly GO or NO-GO")
        return errors
    decision = decision_match.group(1)
    candidate_matches = re.findall(
        r"^\*\*Release candidate SHA:\*\*\s*(NONE|[0-9a-f]{40})(?:\s|$)",
        text,
        re.MULTILINE | re.IGNORECASE,
    )
    if len(candidate_matches) != 1:
        errors.append("checklist must declare exactly one release candidate SHA or NONE")
        candidate_sha = None
    else:
        candidate_sha = candidate_matches[0].lower()
        if candidate_sha == "none":
            candidate_sha = None

    for gate_id, record in gates.items():
        status = record.get("Status", "").strip()
        evidence = record.get("Evidence / exact source SHA", "").lower()
        scope = record.get("Required evidence scope", "").strip()
        if scope not in ALLOWED_SCOPES:
            errors.append(f"Gate {gate_id}: invalid required evidence scope {scope!r}")
        if status in {"PASS", "N/A"}:
            if candidate_sha is None:
                errors.append(f"Gate {gate_id}: {status} requires a selected release candidate SHA")
            elif candidate_sha not in evidence:
                errors.append(f"Gate {gate_id}: {status} evidence does not identify the current candidate SHA")
            if scope and f"scope={scope.lower()}" not in evidence:
                errors.append(f"Gate {gate_id}: {status} evidence does not claim required scope={scope}")
            for approval in ("independent_review=pass", "owner_approval=pass"):
                if approval not in evidence:
                    errors.append(f"Gate {gate_id}: {status} evidence lacks {approval}")

    if decision == "GO":
        if candidate_sha is None:
            errors.append("GO requires a selected full-SHA release candidate")
        incomplete = [
            gate_id for gate_id in GATE_IDS
            if gates.get(gate_id, {}).get("Status", "").strip() not in {"PASS", "N/A"}
        ]
        if incomplete:
            errors.append(f"GO requires every mandatory gate to PASS or approved N/A; unresolved={incomplete}")
    return errors


def main() -> int:
    checklist = Path(__file__).resolve().parents[1] / "docs" / "ZAVQERA_LAUNCH_READINESS_CHECKLIST_2026-10-18.md"
    errors = validate_checklist(checklist.read_text(encoding="utf-8"))
    if errors:
        print("LAUNCH_CHECKLIST=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"LAUNCH_CHECKLIST=PASS gates={len(GATE_IDS)} statuses=PASS/FAIL/BLOCKED/N/A")
    print("NOTE=structural validation only; reviewer must verify evidence authenticity and truth")
    return 0


if __name__ == "__main__":
    sys.exit(main())

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
SCOPE_LIMITATIONS = {
    "HOSTED_READ_ONLY_CAPTURE": re.compile(
        r"\b(?:no fresh (?:13-query )?hosted capture|not a fresh hosted capture|only in disposable|test-only|local-only)\b",
        re.IGNORECASE,
    ),
    "HOSTED_READ_ONLY_CAPTURE_AND_REVIEW": re.compile(
        r"\b(?:no fresh (?:13-query )?hosted capture|not a fresh hosted capture|only in disposable|test-only|local-only)\b",
        re.IGNORECASE,
    ),
    "APPLICATION_BACKUP_RESTORE": re.compile(
        r"\b(?:synthetic .*smoke test|not full application recovery|not application recovery|not a full application restore)\b",
        re.IGNORECASE,
    ),
    "PROVIDER_CONTRACT_REVIEW": re.compile(
        r"\b(?:fake-provider tests are not proof|fake provider only|no real-provider guarantees)\b",
        re.IGNORECASE,
    ),
}


def validate_checklist(text: str) -> list[str]:
    errors: list[str] = []
    gates: dict[str, dict[str, str]] = {}
    current_id: str | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        any_gate_heading = re.match(r"^###\s+Gate\s+([A-Z0-9]+)\s+—\s+.+$", line)
        heading = re.match(r"^###\s+Gate\s+([A-J])\s+—\s+.+$", line)
        if any_gate_heading and not heading:
            errors.append(f"line {line_number}: unsupported gate id {any_gate_heading.group(1)}")
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

    decision_matches = re.findall(r"^##\s+Release decision:\s*(NO-GO|GO)\s*$", text, re.MULTILINE)
    if len(decision_matches) != 1:
        errors.append("checklist must contain exactly one explicit GO or NO-GO release decision")
        return errors
    decision = decision_matches[0]
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
            candidate_claims = re.findall(r"\bcandidate_sha\s*=\s*([^\s;|]+)", evidence)
            if candidate_sha and (len(candidate_claims) != 1 or candidate_claims[0] != candidate_sha):
                errors.append(f"Gate {gate_id}: {status} evidence must bind candidate_sha to the selected candidate")
            scope_claims = re.findall(r"\bscope\s*=\s*([^\s;|]+)", evidence)
            if scope and (len(scope_claims) != 1 or scope_claims[0] != scope.lower()):
                errors.append(f"Gate {gate_id}: {status} evidence does not claim required scope={scope}")
            approval_patterns = (
                ("owner_approval", re.compile(r"\bowner_approval\s*=\s*pass\s+by\s+([^;|]+)", re.IGNORECASE)),
                ("independent_review", re.compile(r"\bindependent_review\s*=\s*pass\s+by\s+([^;|]+)", re.IGNORECASE)),
            )
            owner_field = record.get("Accountable owner / independent reviewer", "").lower()
            for approval, pattern in approval_patterns:
                matches = list(pattern.finditer(evidence))
                if len(matches) != 1:
                    errors.append(f"Gate {gate_id}: {status} evidence lacks {approval}=PASS by an accountable person/team")
                    continue
                approver = matches[0].group(1).strip().lower()
                if not approver or PLACEHOLDERS.search(approver) or approver in {"pending", "unassigned", "owner", "reviewer"}:
                    errors.append(f"Gate {gate_id}: {approval} must name an accountable person or team")
                elif approver not in owner_field:
                    errors.append(f"Gate {gate_id}: {approval} approver is absent from the owner/reviewer field")
            if "pending" in owner_field or "unassigned" in owner_field:
                errors.append(f"Gate {gate_id}: {status} cannot pass with an unassigned owner or reviewer")

            tested_sha_claims = re.findall(r"\btested_sha\s*=\s*([^\s;|]+)", evidence)
            tested_sha_values = [value for value in tested_sha_claims if re.fullmatch(r"[0-9a-f]{40}", value)]
            if tested_sha_claims and len(tested_sha_values) != len(tested_sha_claims):
                errors.append(f"Gate {gate_id}: malformed tested_sha evidence")
            if candidate_sha and any(value != candidate_sha for value in tested_sha_values):
                errors.append(f"Gate {gate_id}: tested_sha differs from the selected release candidate")
            if scope in SCOPE_LIMITATIONS and SCOPE_LIMITATIONS[scope].search(evidence):
                errors.append(f"Gate {gate_id}: evidence explicitly disclaims required scope={scope}")

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

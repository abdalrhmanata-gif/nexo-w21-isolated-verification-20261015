#!/usr/bin/env python3
"""Offline guard for the row-level ZAVQERA migration owner-decision intake.

This tool reads repository files only. It performs no network/database access and
never authorizes or executes a hosted change.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

EXPECTED_ROWS = 95
EXPECTED_METADATA = {
    "EXACT_VERSION_NAME_TUPLE": 46,
    "SAME_NAME_DIFFERENT_VERSION": 22,
    "SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER": 21,
    "HOSTED_TUPLE_ABSENT_FROM_SOURCE": 6,
}
EXPECTED_CLASSIFICATIONS = {
    "UNKNOWN": 46,
    "NAME_VERSION_CONFLICT": 22,
    "SOURCE_NOT_IN_LEDGER": 21,
    "HOSTED_ONLY_SOURCE_UNKNOWN": 6,
}
EXPECTED_CAPTURE_SHA256 = "9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d"
REQUIRED_COLUMNS = {
    "reconciliation_id", "source_version", "source_name", "hosted_version",
    "hosted_name", "metadata_relation", "existing_classification",
    "source_sql_sha256_in_review_output", "existing_owner_review_status",
    "authoritative_historical_source_uri",
    "source_git_blob_commit_or_archive_provenance", "verified_source_sql_sha256",
    "hosted_deployment_record_uri", "verified_deployed_sql_sha256",
    "evidence_artifact_sha256", "owner_disposition",
    "independent_reviewer_name_role", "reviewed_at_utc",
    "decision_rationale_and_evidence", "required_follow_up",
    "approved_for_offline_remediation_design", "hosted_change_authorized",
}
OWNER_EVIDENCE_FIELDS = (
    "authoritative_historical_source_uri",
    "source_git_blob_commit_or_archive_provenance",
    "verified_source_sql_sha256",
    "hosted_deployment_record_uri",
    "verified_deployed_sql_sha256",
    "evidence_artifact_sha256",
    "reviewed_at_utc",
    "decision_rationale_and_evidence",
)
LEDGER_FIELDS = (
    "reconciliation_id", "source_version", "source_name",
    "hosted_version", "hosted_name", "metadata_relation",
    "existing_classification", "source_sql_sha256_in_review_output",
    "existing_owner_review_status",
)


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        rows = [{key: (value or "") for key, value in row.items()} for row in reader]
    return headers, rows


def _read_ledger(path: Path) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    pattern = re.compile(r"^\| ZMR-\d{3} \|")
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not pattern.match(line):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) != len(LEDGER_FIELDS):
                raise ValueError(f"Unexpected ledger row width {len(cells)}: {line.rstrip()}")
            row = dict(zip(LEDGER_FIELDS, cells))
            result[row["reconciliation_id"]] = row
    return result


def validate(
    intake_path: Path,
    ledger_path: Path,
    instructions_path: Path,
) -> list[str]:
    errors: list[str] = []
    try:
        headers, rows = _read_csv(intake_path)
        ledger = _read_ledger(ledger_path)
        instructions = instructions_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        return [f"input_error: {exc}"]

    missing = REQUIRED_COLUMNS - set(headers)
    if missing:
        errors.append("missing_columns: " + ", ".join(sorted(missing)))

    if len(rows) != EXPECTED_ROWS:
        errors.append(f"row_count_expected_{EXPECTED_ROWS}_got_{len(rows)}")

    ids = [row.get("reconciliation_id", "") for row in rows]
    if len(set(ids)) != len(ids):
        errors.append("duplicate_reconciliation_id")
    expected_ids = {f"ZMR-{n:03d}" for n in range(1, EXPECTED_ROWS + 1)}
    if set(ids) != expected_ids:
        errors.append("reconciliation_ids_do_not_match_ZMR_001_to_095")

    if Counter(row.get("metadata_relation", "") for row in rows) != Counter(EXPECTED_METADATA):
        errors.append("metadata_relation_counts_mismatch")
    if Counter(row.get("existing_classification", "") for row in rows) != Counter(EXPECTED_CLASSIFICATIONS):
        errors.append("classification_counts_mismatch")

    for row in rows:
        rid = row.get("reconciliation_id", "<missing-id>")
        if row.get("owner_disposition") != "OPEN":
            errors.append(f"{rid}: owner_disposition_must_remain_OPEN")
        if row.get("independent_reviewer_name_role") != "UNASSIGNED":
            errors.append(f"{rid}: reviewer_must_remain_UNASSIGNED_until_independent_review")
        if row.get("approved_for_offline_remediation_design") != "NOT_REVIEWED":
            errors.append(f"{rid}: offline_design_approval_must_remain_NOT_REVIEWED")
        if row.get("hosted_change_authorized") != "NO — separate written authorization required":
            errors.append(f"{rid}: hosted_change_authorized_must_remain_NO")
        if row.get("existing_owner_review_status") != "PENDING":
            errors.append(f"{rid}: original_owner_review_status_must_remain_PENDING")
        for field in OWNER_EVIDENCE_FIELDS:
            if row.get(field, "").strip():
                errors.append(f"{rid}: owner_evidence_field_prematurely_filled:{field}")
        if row.get("required_follow_up") != "OWNER REVIEW REQUIRED":
            errors.append(f"{rid}: required_follow_up_must_remain_OWNER_REVIEW_REQUIRED")

    missing_ledger_ids = set(ledger) - set(ids)
    missing_intake_ids = set(ids) - set(ledger)
    if missing_ledger_ids or missing_intake_ids:
        errors.append(
            f"ledger_intake_id_difference: missing_from_intake={sorted(missing_ledger_ids)} "
            f"missing_from_ledger={sorted(missing_intake_ids)}"
        )
    intake_by_id = {row.get("reconciliation_id", ""): row for row in rows}
    for rid, baseline in ledger.items():
        row = intake_by_id.get(rid)
        if row is None:
            continue
        for field in LEDGER_FIELDS:
            if row.get(field, "").strip() != baseline.get(field, "").strip():
                errors.append(f"{rid}: immutable_ledger_field_changed:{field}")

    if EXPECTED_CAPTURE_SHA256 not in instructions:
        errors.append("capture_sha256_missing_from_intake_instructions")
    if "does not authorize a database write" not in instructions:
        errors.append("instructions_missing_non_authorization_statement")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--intake",
        type=Path,
        default=Path("docs/ZAVQERA_MIGRATION_OWNER_DECISION_INTAKE_2026-10-17.csv"),
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path("docs/ZAVQERA_MIGRATION_PROVENANCE_RECONCILIATION_LEDGER_2026-10-17.md"),
    )
    parser.add_argument(
        "--instructions",
        type=Path,
        default=Path("docs/ZAVQERA_MIGRATION_OWNER_DECISION_INTAKE_README_2026-10-17.md"),
    )
    args = parser.parse_args()
    errors = validate(args.intake, args.ledger, args.instructions)
    result = {
        "status": "PASS" if not errors else "FAIL",
        "network_requests": 0,
        "database_connections": 0,
        "hosted_write_authorized": False,
        "expected_rows": EXPECTED_ROWS,
        "error_count": len(errors),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Offline guard for the row-level ZAVQERA migration owner-decision intake.

Reads only local repository files. No network/database access. This validator
keeps the template fail-closed while permitting evidence-complete owner decisions.
It never authorizes or executes a hosted change.
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
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
UTC_TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
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
ALLOWED_OWNER_DISPOSITIONS = {
    "OPEN",
    "EXACT_SOURCE_BYTES_VERIFIED",
    "NAME_VERSION_CONFLICT_RESOLVED",
    "HOSTED_ONLY_SOURCE_RECOVERED",
    "SOURCE_ONLY_REVIEWED",
    "UNKNOWN_BLOCKING",
}
ALLOWED_OFFLINE_APPROVAL = {
    "NOT_REVIEWED",
    "APPROVED_FOR_OFFLINE_DESIGN",
    "REJECTED",
}
VERIFIED_BYTE_DISPOSITIONS = {
    "EXACT_SOURCE_BYTES_VERIFIED",
    "NAME_VERSION_CONFLICT_RESOLVED",
    "HOSTED_ONLY_SOURCE_RECOVERED",
}
SOURCE_EVIDENCE_DISPOSITIONS = {
    "EXACT_SOURCE_BYTES_VERIFIED",
    "NAME_VERSION_CONFLICT_RESOLVED",
    "HOSTED_ONLY_SOURCE_RECOVERED",
    "SOURCE_ONLY_REVIEWED",
}
LEDGER_FIELDS = (
    "reconciliation_id", "source_version", "source_name", "hosted_version",
    "hosted_name", "metadata_relation", "existing_classification",
    "source_sql_sha256_in_review_output", "existing_owner_review_status",
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    return headers, rows


def read_ledger(path: Path) -> dict[str, dict[str, str]]:
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


def valid_sha(value: str) -> bool:
    return bool(SHA256_PATTERN.fullmatch(value.strip()))


def validate(
    intake_path: Path,
    ledger_path: Path,
    instructions_path: Path,
) -> list[str]:
    errors: list[str] = []
    try:
        headers, rows = read_csv(intake_path)
        ledger = read_ledger(ledger_path)
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
        disposition = row.get("owner_disposition", "")
        reviewer = row.get("independent_reviewer_name_role", "")
        reviewed_at = row.get("reviewed_at_utc", "")
        rationale = row.get("decision_rationale_and_evidence", "")
        follow_up = row.get("required_follow_up", "")
        offline_approval = row.get("approved_for_offline_remediation_design", "")
        source_sha = row.get("verified_source_sql_sha256", "")
        deployed_sha = row.get("verified_deployed_sql_sha256", "")

        if disposition not in ALLOWED_OWNER_DISPOSITIONS:
            errors.append(f"{rid}: invalid_owner_disposition:{disposition}")
        if offline_approval not in ALLOWED_OFFLINE_APPROVAL:
            errors.append(f"{rid}: invalid_offline_design_approval:{offline_approval}")

        # The intake itself can never authorize a hosted change. Such an
        # authorization must be separate, explicit, scoped and recorded.
        if row.get("hosted_change_authorized") != "NO — separate written authorization required":
            errors.append(f"{rid}: hosted_change_authorized_must_remain_NO")

        if row.get("existing_owner_review_status") != "PENDING":
            errors.append(f"{rid}: immutable_ledger_owner_status_changed")

        if disposition == "OPEN":
            if reviewer and reviewer == "UNASSIGNED" and reviewed_at:
                errors.append(f"{rid}: unassigned_reviewer_cannot_have_review_timestamp")
            if reviewed_at and not UTC_TIMESTAMP_PATTERN.fullmatch(reviewed_at):
                errors.append(f"{rid}: reviewed_at_utc_must_be_iso8601_z")
            if offline_approval == "APPROVED_FOR_OFFLINE_DESIGN":
                if reviewer in ("", "UNASSIGNED") or not reviewed_at or not rationale:
                    errors.append(f"{rid}: offline_design_approval_requires_reviewer_date_and_rationale")
        else:
            if reviewer in ("", "UNASSIGNED"):
                errors.append(f"{rid}: disposition_requires_independent_reviewer")
            if not UTC_TIMESTAMP_PATTERN.fullmatch(reviewed_at):
                errors.append(f"{rid}: reviewed_disposition_requires_iso8601_utc_timestamp")
            if not rationale:
                errors.append(f"{rid}: reviewed_disposition_requires_rationale")
            if not follow_up:
                errors.append(f"{rid}: reviewed_disposition_requires_follow_up")
            if offline_approval == "APPROVED_FOR_OFFLINE_DESIGN" and (reviewer in ("", "UNASSIGNED") or not rationale):
                errors.append(f"{rid}: offline_design_approval_requires_reviewer_and_rationale")

        for field in ("verified_source_sql_sha256", "verified_deployed_sql_sha256", "evidence_artifact_sha256"):
            value = row.get(field, "")
            if value and not valid_sha(value):
                errors.append(f"{rid}: {field}_must_be_64_hex")

        if disposition == "NAME_VERSION_CONFLICT_RESOLVED" and row.get("metadata_relation") != "SAME_NAME_DIFFERENT_VERSION":
            errors.append(f"{rid}: NAME_VERSION_CONFLICT_RESOLVED_requires_conflict_row")
        if disposition == "HOSTED_ONLY_SOURCE_RECOVERED" and row.get("metadata_relation") != "HOSTED_TUPLE_ABSENT_FROM_SOURCE":
            errors.append(f"{rid}: HOSTED_ONLY_SOURCE_RECOVERED_requires_hosted_only_row")
        if disposition == "SOURCE_ONLY_REVIEWED" and row.get("metadata_relation") != "SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER":
            errors.append(f"{rid}: SOURCE_ONLY_REVIEWED_requires_source_only_row")

        if disposition in SOURCE_EVIDENCE_DISPOSITIONS:
            for field in (
                "authoritative_historical_source_uri",
                "source_git_blob_commit_or_archive_provenance",
                "verified_source_sql_sha256",
                "evidence_artifact_sha256",
            ):
                if not row.get(field, ""):
                    errors.append(f"{rid}: {disposition}_requires_{field}")
            if source_sha and not valid_sha(source_sha):
                errors.append(f"{rid}: invalid_verified_source_sha256")

        if disposition in VERIFIED_BYTE_DISPOSITIONS:
            for field in (
                "hosted_deployment_record_uri",
                "verified_deployed_sql_sha256",
            ):
                if not row.get(field, ""):
                    errors.append(f"{rid}: {disposition}_requires_{field}")
            if not valid_sha(source_sha):
                errors.append(f"{rid}: verified_source_sql_sha256_must_be_64_hex")
            if not valid_sha(deployed_sha):
                errors.append(f"{rid}: verified_deployed_sql_sha256_must_be_64_hex")
            if valid_sha(source_sha) and valid_sha(deployed_sha) and source_sha != deployed_sha:
                errors.append(f"{rid}: source_and_deployed_sql_sha256_mismatch")
            evidence_sha = row.get("evidence_artifact_sha256", "")
            if not valid_sha(evidence_sha):
                errors.append(f"{rid}: evidence_artifact_sha256_must_be_64_hex")

        if disposition == "SOURCE_ONLY_REVIEWED":
            # A source-only classification is not evidence the migration was
            # never deployed. The reviewer must state that limitation.
            limitation = rationale.lower()
            if "not prove" not in limitation and "does not prove" not in limitation and "doesn't prove" not in limitation:
                errors.append(f"{rid}: source_only_rationale_must_state_ledger_absence_does_not_prove_non_deployment")

        if offline_approval == "APPROVED_FOR_OFFLINE_DESIGN" and disposition == "UNKNOWN_BLOCKING":
            errors.append(f"{rid}: unresolved_unknown_row_cannot_be_approved_for_offline_design")

    expected_ids_in_ledger = set(ledger)
    if expected_ids_in_ledger != set(ids):
        errors.append(
            f"ledger_intake_id_difference: missing_from_intake={sorted(expected_ids_in_ledger - set(ids))} "
            f"missing_from_ledger={sorted(set(ids) - expected_ids_in_ledger)}"
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
    non_authorization_phrases = (
        "does not authorize a database write",
        "this CSV never authorizes a database write",
        "does not authorize a hosted change",
    )
    if not any(phrase in instructions for phrase in non_authorization_phrases):
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

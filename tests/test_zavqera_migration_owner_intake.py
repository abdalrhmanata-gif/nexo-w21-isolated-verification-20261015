from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_zavqera_migration_owner_intake import validate  # noqa: E402

INTAKE = ROOT / "docs" / "ZAVQERA_MIGRATION_OWNER_DECISION_INTAKE_2026-10-17.csv"
LEDGER = ROOT / "docs" / "ZAVQERA_MIGRATION_PROVENANCE_RECONCILIATION_LEDGER_2026-10-17.md"
INSTRUCTIONS = ROOT / "docs" / "ZAVQERA_MIGRATION_OWNER_DECISION_INTAKE_README_2026-10-17.md"
SHA_A = "a" * 64
SHA_B = "b" * 64


class MigrationOwnerIntakeGuardTests(unittest.TestCase):
    def _read_rows(self):
        with INTAKE.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or []), list(reader)

    def _mutated_copy(self, mutator):
        fieldnames, rows = self._read_rows()
        mutator(rows)
        temp = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", suffix=".csv", delete=False
        )
        with temp:
            writer = csv.DictWriter(temp, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        self.addCleanup(lambda: Path(temp.name).unlink(missing_ok=True))
        return Path(temp.name)

    @staticmethod
    def _complete_verified_bytes_decision(row):
        row["owner_disposition"] = "EXACT_SOURCE_BYTES_VERIFIED"
        row["authoritative_historical_source_uri"] = "https://evidence.example.test/source.sql"
        row["source_git_blob_commit_or_archive_provenance"] = "commit deadbeef; archived SQL digest verified by independent reviewer"
        row["verified_source_sql_sha256"] = SHA_A
        row["hosted_deployment_record_uri"] = "https://evidence.example.test/deployment-record"
        row["verified_deployed_sql_sha256"] = SHA_A
        row["evidence_artifact_sha256"] = SHA_B
        row["independent_reviewer_name_role"] = "Independent DB Owner (test fixture)"
        row["reviewed_at_utc"] = "2026-10-17T18:00:00Z"
        row["decision_rationale_and_evidence"] = "Authoritative historical SQL bytes and a trusted deployment record were independently examined."
        row["required_follow_up"] = "No follow-up on this test row; broader release gates remain open."

    def test_current_95_row_intake_passes(self):
        self.assertEqual(validate(INTAKE, LEDGER, INSTRUCTIONS), [])

    def test_unapproved_hosted_write_is_rejected(self):
        path = self._mutated_copy(
            lambda rows: rows[0].__setitem__("hosted_change_authorized", "YES")
        )
        errors = validate(path, LEDGER, INSTRUCTIONS)
        self.assertTrue(any("hosted_change_authorized_must_remain_NO" in e for e in errors))

    def test_premature_exact_bytes_claim_is_rejected(self):
        path = self._mutated_copy(
            lambda rows: rows[0].__setitem__("owner_disposition", "EXACT_SOURCE_BYTES_VERIFIED")
        )
        errors = validate(path, LEDGER, INSTRUCTIONS)
        self.assertTrue(any("EXACT_SOURCE_BYTES_VERIFIED_requires_authoritative_historical_source_uri" in e for e in errors))
        self.assertTrue(any("verified_source_sql_sha256_must_be_64_hex" in e for e in errors))

    def test_evidence_complete_exact_byte_review_is_accepted(self):
        path = self._mutated_copy(lambda rows: self._complete_verified_bytes_decision(rows[0]))
        self.assertEqual(validate(path, LEDGER, INSTRUCTIONS), [])

    def test_mismatched_source_and_deployed_digest_is_rejected(self):
        def mutate(rows):
            self._complete_verified_bytes_decision(rows[0])
            rows[0]["verified_deployed_sql_sha256"] = SHA_B
        path = self._mutated_copy(mutate)
        errors = validate(path, LEDGER, INSTRUCTIONS)
        self.assertTrue(any("source_and_deployed_sql_sha256_mismatch" in e for e in errors))

    def test_source_only_review_can_close_without_claiming_non_deployment(self):
        def mutate(rows):
            row = rows[47]  # ZMR-048: first source-only row; baseline columns remain immutable.
            row["owner_disposition"] = "SOURCE_ONLY_REVIEWED"
            row["authoritative_historical_source_uri"] = "https://evidence.example.test/source-only.sql"
            row["source_git_blob_commit_or_archive_provenance"] = "Commit abc123 and archive custody record"
            row["verified_source_sql_sha256"] = SHA_A
            row["evidence_artifact_sha256"] = SHA_B
            row["independent_reviewer_name_role"] = "Independent DB Owner (test fixture)"
            row["reviewed_at_utc"] = "2026-10-17T18:00:00Z"
            row["decision_rationale_and_evidence"] = "Source bytes verified; absence from the hosted ledger does not prove non-deployment."
            row["required_follow_up"] = "Keep source-versus-ledger deployment question open."
        path = self._mutated_copy(mutate)
        self.assertEqual(validate(path, LEDGER, INSTRUCTIONS), [])

    def test_source_only_review_cannot_claim_ledger_absence_proves_non_deployment(self):
        def mutate(rows):
            row = rows[47]
            row["owner_disposition"] = "SOURCE_ONLY_REVIEWED"
            row["authoritative_historical_source_uri"] = "https://evidence.example.test/source-only.sql"
            row["source_git_blob_commit_or_archive_provenance"] = "Commit abc123"
            row["verified_source_sql_sha256"] = SHA_A
            row["evidence_artifact_sha256"] = SHA_B
            row["independent_reviewer_name_role"] = "Independent DB Owner (test fixture)"
            row["reviewed_at_utc"] = "2026-10-17T18:00:00Z"
            row["decision_rationale_and_evidence"] = "This source was examined and is probably not deployed."
            row["required_follow_up"] = "None."
        path = self._mutated_copy(mutate)
        errors = validate(path, LEDGER, INSTRUCTIONS)
        self.assertTrue(any("source_only_rationale_must_state_ledger_absence_does_not_prove_non_deployment" in e for e in errors))

    def test_open_row_can_be_assigned_for_review_without_premature_closure(self):
        def mutate(rows):
            rows[0]["independent_reviewer_name_role"] = "Independent DB Owner — assigned, pending"
            rows[0]["decision_rationale_and_evidence"] = "Review requested; disposition remains OPEN."
        path = self._mutated_copy(mutate)
        self.assertEqual(validate(path, LEDGER, INSTRUCTIONS), [])

    def test_changed_baseline_tuple_is_rejected(self):
        path = self._mutated_copy(
            lambda rows: rows[0].__setitem__("source_name", "different_name")
        )
        errors = validate(path, LEDGER, INSTRUCTIONS)
        self.assertTrue(any("immutable_ledger_field_changed:source_name" in e for e in errors))

    def test_duplicate_or_missing_reconciliation_unit_is_rejected(self):
        def mutate(rows):
            rows[1]["reconciliation_id"] = rows[0]["reconciliation_id"]
        path = self._mutated_copy(mutate)
        errors = validate(path, LEDGER, INSTRUCTIONS)
        self.assertTrue(any("duplicate_reconciliation_id" in e for e in errors))
        self.assertTrue(any("reconciliation_ids_do_not_match_ZMR_001_to_095" in e for e in errors))


    def test_w4_archive_candidate_does_not_close_hosted_sql_provenance(self):
        with INTAKE.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        row = next(item for item in rows if item["reconciliation_id"] == "ZMR-008")
        self.assertEqual(row["source_version"], "20260921180052")
        self.assertEqual(row["hosted_version"], "20260921180138")
        self.assertEqual(row["existing_classification"], "NAME_VERSION_CONFLICT")
        self.assertEqual(row["existing_owner_review_status"], "PENDING")
        self.assertEqual(row["owner_disposition"], "OPEN")
        self.assertEqual(
            row["candidate_sql_sha256"],
            "3419a01a1b0ea66bd22877f478b61473cf1210006828ea3f28c5c08fb51ef0c8",
        )
        self.assertEqual(row["candidate_archive_sha256"],
                         "1781646022255f2eda2a8007676ebd157d70782fccabb6492ada6afc59245f4c")
        self.assertEqual(row["verified_source_sql_sha256"], "")
        self.assertEqual(row["hosted_deployment_record_uri"], "")
        self.assertEqual(row["verified_deployed_sql_sha256"], "")
        self.assertEqual(
            row["hosted_change_authorized"],
            "NO — separate written authorization required",
        )


if __name__ == "__main__":
    unittest.main()

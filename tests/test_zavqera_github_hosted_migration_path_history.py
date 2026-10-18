from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / "docs" / "ZAVQERA_MIGRATION_OWNER_DECISION_INTAKE_2026-10-17.csv"
MATRIX = ROOT / "docs" / "ZAVQERA_GITHUB_HOSTED_MIGRATION_PATH_HISTORY_2026-10-18.csv"
SOURCE_HEAD = "fbbcb080904acd88aad83a082803f627859026e2"
MISMATCH = "SAME_NAME_DIFFERENT_VERSION"
HOSTED_ONLY = "HOSTED_TUPLE_ABSENT_FROM_SOURCE"
EXPECTED_ROWS = 28
GIT_BLOB_SHA1 = re.compile(r"^[0-9a-f]{40}$")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), [
            {key: (value or "").strip() for key, value in row.items()}
            for row in reader
        ]


class GitHubHostedMigrationPathHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.intake_headers, cls.intake_rows = read_csv(INTAKE)
        cls.matrix_headers, cls.matrix_rows = read_csv(MATRIX)
        cls.intake_by_id = {
            row["reconciliation_id"]: row for row in cls.intake_rows
        }
        cls.matrix_by_id = {
            row["reconciliation_id"]: row for row in cls.matrix_rows
        }
        cls.expected = {
            row["reconciliation_id"]: row
            for row in cls.intake_rows
            if row["metadata_relation"] in {MISMATCH, HOSTED_ONLY}
        }

    def test_path_matrix_has_all_and_only_28_affected_rows(self) -> None:
        self.assertEqual(len(self.matrix_rows), EXPECTED_ROWS)
        self.assertEqual(len(self.matrix_by_id), EXPECTED_ROWS)
        self.assertEqual(set(self.matrix_by_id), set(self.expected))

    def test_matrix_required_columns_are_present(self) -> None:
        required = {
            "reconciliation_id",
            "metadata_relation",
            "source_file_path",
            "source_path_present_at_source_head",
            "source_git_blob_sha1",
            "source_size_bytes",
            "hosted_version_filename_path",
            "hosted_path_present_at_source_head",
            "hosted_path_history_commit_count_from_source_head",
            "source_checkout_head_sha",
            "interpretation",
        }
        self.assertTrue(required.issubset(set(self.matrix_headers)))

    def test_each_row_matches_immutable_intake_identity(self) -> None:
        for rid, matrix in self.matrix_by_id.items():
            with self.subTest(reconciliation_id=rid):
                intake = self.expected[rid]
                self.assertEqual(matrix["metadata_relation"], intake["metadata_relation"])
                expected_hosted_path = (
                    f"supabase/migrations/{intake['hosted_version']}_"
                    f"{intake['hosted_name']}.sql"
                )
                self.assertEqual(matrix["hosted_version_filename_path"], expected_hosted_path)
                self.assertEqual(matrix["source_checkout_head_sha"], SOURCE_HEAD)

    def test_absent_hosted_paths_stay_absent_and_have_zero_reachable_path_history(self) -> None:
        for rid, row in self.matrix_by_id.items():
            with self.subTest(reconciliation_id=rid):
                self.assertEqual(row["hosted_path_present_at_source_head"], "false")
                self.assertEqual(row["hosted_path_history_commit_count_from_source_head"], "0")
                self.assertTrue(row["interpretation"])
                self.assertIn("not prove", row["interpretation"].lower())

    def test_conflicts_keep_source_blob_metadata_separate_from_deployment_proof(self) -> None:
        for rid, row in self.matrix_by_id.items():
            if row["metadata_relation"] != MISMATCH:
                continue
            with self.subTest(reconciliation_id=rid):
                intake = self.expected[rid]
                expected_source_path = (
                    f"{intake['source_version']}_{intake['source_name']}.sql"
                )
                self.assertEqual(row["source_file_path"], expected_source_path)
                self.assertEqual(row["source_path_present_at_source_head"], "true")
                self.assertRegex(row["source_git_blob_sha1"], GIT_BLOB_SHA1)
                self.assertGreater(int(row["source_size_bytes"]), 0)
                self.assertIn("source-side", row["interpretation"].lower())
                self.assertNotIn("EXACT_SOURCE_BYTES_VERIFIED", row["interpretation"])

    def test_hosted_only_rows_do_not_fabricate_source_blob_metadata(self) -> None:
        hosted_only_rows = [
            row for row in self.matrix_by_id.values()
            if row["metadata_relation"] == HOSTED_ONLY
        ]
        self.assertEqual(len(hosted_only_rows), 6)
        for row in hosted_only_rows:
            with self.subTest(reconciliation_id=row["reconciliation_id"]):
                self.assertEqual(row["source_file_path"], "")
                self.assertEqual(row["source_path_present_at_source_head"], "false")
                self.assertEqual(row["source_git_blob_sha1"], "")
                self.assertEqual(row["source_size_bytes"], "")

    def test_every_matrix_row_still_has_an_unresolved_intake_disposition(self) -> None:
        for rid in self.matrix_by_id:
            with self.subTest(reconciliation_id=rid):
                intake = self.intake_by_id[rid]
                self.assertEqual(intake["owner_disposition"], "OPEN")
                self.assertEqual(intake["existing_owner_review_status"], "PENDING")
                self.assertEqual(
                    intake["hosted_change_authorized"],
                    "NO — separate written authorization required",
                )
                self.assertEqual(intake["verified_deployed_sql_sha256"], "")
                self.assertEqual(intake["hosted_deployment_record_uri"], "")


if __name__ == "__main__":
    unittest.main()

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


class MigrationOwnerIntakeGuardTests(unittest.TestCase):
    def _mutated_copy(self, mutator):
        with INTAKE.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)
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

    def test_current_95_row_intake_passes(self):
        self.assertEqual(validate(INTAKE, LEDGER, INSTRUCTIONS), [])

    def test_unapproved_hosted_write_is_rejected(self):
        path = self._mutated_copy(
            lambda rows: rows[0].__setitem__("hosted_change_authorized", "YES")
        )
        errors = validate(path, LEDGER, INSTRUCTIONS)
        self.assertTrue(any("hosted_change_authorized_must_remain_NO" in e for e in errors))

    def test_premature_exact_bytes_claim_is_rejected(self):
        def mutate(rows):
            rows[0]["owner_disposition"] = "EXACT_SOURCE_BYTES_VERIFIED"
            rows[0]["verified_source_sql_sha256"] = "a" * 64
        path = self._mutated_copy(mutate)
        errors = validate(path, LEDGER, INSTRUCTIONS)
        self.assertTrue(any("owner_disposition_must_remain_OPEN" in e for e in errors))
        self.assertTrue(any("owner_evidence_field_prematurely_filled" in e for e in errors))

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


if __name__ == "__main__":
    unittest.main()

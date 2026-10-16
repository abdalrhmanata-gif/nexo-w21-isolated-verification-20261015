import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "review_hosted_migration_ledger.py"
spec = importlib.util.spec_from_file_location("review_hosted_migration_ledger", SCRIPT)
review = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(review)


def save(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


class HostedLedgerReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.repo = self.base / "repo"
        self.evidence = self.base / "evidence"
        (self.repo / "supabase" / "migrations").mkdir(parents=True)
        self.evidence.mkdir()
        (self.repo / "supabase" / "migrations" / "20261013100000_w80_example.sql").write_text("select 1;\n")
        (self.repo / "supabase" / "migrations" / "20261015100000_w83_example.sql").write_text("select 2;\n")
        save(self.evidence / "summary.json", {
            "status": "CAPTURED_FOR_MANUAL_REVIEW", "queries_completed": 13,
            "query_pack_sha256": review.PACK_SHA256,
            "acl_provenance_query_sha256": review.ACL_PROVENANCE_SHA256,
            "access_token_saved": False
        })
        save(self.evidence / "run_metadata.json", {
            "observed_at_utc": "2026-10-15T18:00:00+00:00",
            "project_ref": review.PROJECT_REF, "token_saved": False,
            "acl_provenance_query_sha256": review.ACL_PROVENANCE_SHA256
        })
        save(self.evidence / "project_identity.json", {
            "id": review.PROJECT_REF, "name": review.PROJECT_NAME, "region": review.PROJECT_REGION
        })
        save(self.evidence / "read_only_role_gate.json", {
            "observed": {"current_user": "supabase_read_only_user", "transaction_read_only": True,
                         "migration_ledger_relation": "supabase_migrations.schema_migrations"}
        })
        save(self.evidence / "query_11.json", {"response": [
            {"version": "20261013100000", "name": "w80_example"},
            {"version": "20261015100000", "name": "w83_example"},
            {"version": "20261015120000", "name": "hosted_only"},
        ]})
        rows = []
        for role in review.ROLES:
            for privilege in review.PRIVILEGES:
                rows.append({
                    "evidence_kind": "EFFECTIVE_PRIVILEGE", "schema_name": "public",
                    "relation_name": "agent_executions", "owner_role": "postgres",
                    "row_level_security_enabled": True, "row_level_security_forced": False,
                    "grantee": role, "privilege_type": privilege,
                    "effective_privilege": role == "postgres", "is_grantable": None, "grantor": None
                })
        rows.append({
            "evidence_kind": "STORED_ACL", "schema_name": "public", "relation_name": "agent_executions",
            "owner_role": "postgres", "row_level_security_enabled": True, "row_level_security_forced": False,
            "grantee": "service_role", "privilege_type": "UPDATE", "effective_privilege": None,
            "is_grantable": False, "grantor": "postgres"
        })
        save(self.evidence / "query_12.json", {"response": rows})
        provenance = {
            "probe_name": "w86_acl_provenance_v1",
            "current_user": "supabase_read_only_user",
            "session_user": "supabase_read_only_user",
            "transaction_read_only": "on",
            "relation": {"exists": True, "schema_name": "public", "relation_name": "agent_executions",
                         "owner_role": "postgres", "row_level_security_enabled": True,
                         "row_level_security_forced": False, "stored_acl_is_null": False},
            "service_role_effective_privileges": {
                "SELECT": False, "INSERT": True, "UPDATE": True, "DELETE": True,
                "TRUNCATE": True, "REFERENCES": False, "TRIGGER": False, "MAINTAIN": False
            },
            "service_role_membership_paths": [
                {"role_name": "service_role", "depth": 0, "member_of_role": None, "all_edges_inherit": True},
                {"role_name": "w86_acl_probe_parent", "depth": 1, "member_of_role": "service_role", "all_edges_inherit": True}
            ],
            "table_acl_entries": [],
            "column_acl_entries": [],
            "service_role_inherited_table_acl_entries": [
                {"grantee_role": "w86_acl_probe_parent", "membership_depth": 1,
                 "all_membership_edges_inherit": True, "privilege_type": "UPDATE",
                 "is_grantable": False, "grantor": "postgres"}
            ],
            "service_role_inherited_column_acl_entries": [
                {"column_name": "id", "grantee_role": "w86_acl_probe_parent", "membership_depth": 1,
                 "all_membership_edges_inherit": True, "privilege_type": "SELECT",
                 "is_grantable": False, "grantor": "postgres"}
            ]
        }
        save(self.evidence / "query_13.json", {"response": [{"w86_acl_provenance": provenance}]})

    def tearDown(self):
        self.tmp.cleanup()

    def test_reconcile_finds_timestamp_conflict_and_hosted_only_name(self):
        (self.repo / "supabase" / "migrations" / "20261015100000_w83_example.sql").unlink()
        (self.repo / "supabase" / "migrations" / "20261014100000_w83_example.sql").write_text("select 2;\n")
        result = review.reconcile(self.evidence, self.repo)
        self.assertEqual(result["source_migration_count"], 2)
        self.assertEqual(result["hosted_ledger_row_count"], 3)
        self.assertEqual(result["exact_version_name_matches"], 1)
        self.assertEqual(len(result["same_name_different_version"]), 1)
        self.assertIn("hosted_only", result["hosted_names_absent_from_source"])
        self.assertEqual(result["effective_table_privilege_rows"], 32)
        self.assertEqual(len(result["effective_nonowner_write_grants"]), 0)
        self.assertEqual(len(result["stored_nonowner_write_acl_rows"]), 1)
        self.assertEqual(result["service_role_inherited_table_acl_rows"], 1)
        self.assertEqual(result["service_role_inherited_column_acl_rows"], 1)
        self.assertIn("w86_acl_probe_parent", result["service_role_inherited_table_acl_entries"][0]["grantee_role"])
        self.assertIsNone(result["source_checkout_head_sha"])
        self.assertIsNone(result["source_migrations_worktree_clean"])
        self.assertRegex(result["source_migration_manifest_sha256"], r"^[0-9a-f]{64}$")

    def test_source_migration_manifest_is_deterministic_and_content_sensitive(self):
        first = review.reconcile(self.evidence, self.repo)
        second = review.reconcile(self.evidence, self.repo)
        self.assertEqual(
            first["source_migration_manifest_sha256"],
            second["source_migration_manifest_sha256"],
        )
        migration = self.repo / "supabase" / "migrations" / "20261013100000_w80_example.sql"
        migration.write_text("select 999;\n", encoding="utf-8")
        changed = review.reconcile(self.evidence, self.repo)
        self.assertNotEqual(
            first["source_migration_manifest_sha256"],
            changed["source_migration_manifest_sha256"],
        )

    def test_git_checkout_head_and_dirty_migration_tree_are_reported(self):
        if shutil.which("git") is None:
            self.skipTest("git is unavailable")

        def git(*args):
            return subprocess.run(
                ["git", *args], cwd=self.repo, check=True, capture_output=True,
                text=True, encoding="utf-8", timeout=10,
            )

        git("init", "-q")
        git("config", "user.name", "ZAVQERA offline test")
        git("config", "user.email", "zavqera-test@example.invalid")
        git("add", "supabase/migrations")
        git("commit", "-qm", "test-only migration fixture")
        clean = review.reconcile(self.evidence, self.repo)
        self.assertRegex(clean["source_checkout_head_sha"], r"^[0-9a-f]{40,64}$")
        self.assertIs(clean["source_migrations_worktree_clean"], True)
        migration = self.repo / "supabase" / "migrations" / "20261013100000_w80_example.sql"
        migration.write_text("select 88;\n", encoding="utf-8")
        dirty = review.reconcile(self.evidence, self.repo)
        self.assertEqual(dirty["source_checkout_head_sha"], clean["source_checkout_head_sha"])
        self.assertIs(dirty["source_migrations_worktree_clean"], False)
        self.assertNotEqual(
            dirty["source_migration_manifest_sha256"],
            clean["source_migration_manifest_sha256"],
        )

    def test_effective_service_role_write_is_reported(self):
        payload = json.loads((self.evidence / "query_12.json").read_text())
        for row in payload["response"]:
            if row.get("evidence_kind") == "EFFECTIVE_PRIVILEGE" and row.get("grantee") == "service_role" and row.get("privilege_type") == "UPDATE":
                row["effective_privilege"] = True
        save(self.evidence / "query_12.json", payload)
        result = review.reconcile(self.evidence, self.repo)
        self.assertEqual(len(result["effective_nonowner_write_grants"]), 1)

    def test_rejects_old_ten_query_capture(self):
        summary = json.loads((self.evidence / "summary.json").read_text())
        summary["queries_completed"] = 10
        save(self.evidence / "summary.json", summary)
        with self.assertRaises(review.EvidenceError):
            review.reconcile(self.evidence, self.repo)

    def test_rejects_main_or_wrong_project(self):
        identity = json.loads((self.evidence / "project_identity.json").read_text())
        identity["name"] = "ZAVQERA Main"
        save(self.evidence / "project_identity.json", identity)
        with self.assertRaises(review.EvidenceError):
            review.reconcile(self.evidence, self.repo)

    def test_rejects_incomplete_acl_matrix(self):
        payload = json.loads((self.evidence / "query_12.json").read_text())
        payload["response"] = payload["response"][:-3]
        save(self.evidence / "query_12.json", payload)
        with self.assertRaises(review.EvidenceError):
            review.reconcile(self.evidence, self.repo)

    def test_rejects_wrong_read_only_identity_in_provenance(self):
        payload = json.loads((self.evidence / "query_13.json").read_text())
        payload["response"][0]["w86_acl_provenance"]["current_user"] = "postgres"
        save(self.evidence / "query_13.json", payload)
        with self.assertRaises(review.EvidenceError):
            review.reconcile(self.evidence, self.repo)

    def test_rejects_empty_ledger(self):
        save(self.evidence / "query_11.json", {"response": []})
        with self.assertRaises(review.EvidenceError):
            review.reconcile(self.evidence, self.repo)

    def test_report_is_no_go(self):
        result = review.reconcile(self.evidence, self.repo)
        rendered = review.render_markdown(result)
        self.assertIn("REVIEW REQUIRED / RELEASE NO-GO", rendered)
        self.assertIn("Same-name/different-version", rendered)
        self.assertIn("Source checkout HEAD", rendered)
        self.assertIn("Source migration manifest SHA-256", rendered)
        self.assertIn("service_role inherited table ACL rows: **1**", rendered)
        self.assertIn("inherited ACL row is a blocker", rendered)
        self.assertIn("not a full authorization proof", rendered)


if __name__ == "__main__":
    unittest.main()

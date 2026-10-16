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
                    "effective_privilege": role == "postgres" or (role == "service_role" and privilege == "UPDATE"),
                    "is_grantable": None, "grantor": None
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
                "SELECT": False, "INSERT": False, "UPDATE": True, "DELETE": False,
                "TRUNCATE": False, "REFERENCES": False, "TRIGGER": False, "MAINTAIN": False
            },
            "service_role_membership_paths": [
                {"role_name": "service_role", "depth": 0, "member_of_role": None, "all_edges_inherit": True, "all_edges_set_role": True},
                {"role_name": "w86_acl_probe_parent", "depth": 1, "member_of_role": "service_role", "all_edges_inherit": True, "all_edges_set_role": True}
            ],
            "table_acl_entries": [],
            "column_acl_entries": [],
            "service_role_inherited_table_acl_entries": [
                {"grantee_role": "w86_acl_probe_parent", "membership_depth": 1,
                 "all_membership_edges_inherit": True, "all_membership_edges_set_role": True, "privilege_type": "UPDATE",
                 "is_grantable": False, "grantor": "postgres"}
            ],
            "service_role_inherited_column_acl_entries": [
                {"column_name": "id", "grantee_role": "w86_acl_probe_parent", "membership_depth": 1,
                 "all_membership_edges_inherit": True, "all_membership_edges_set_role": True, "privilege_type": "SELECT",
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
        self.assertEqual(len(result["effective_nonowner_write_grants"]), 1)
        self.assertEqual(len(result["stored_nonowner_write_acl_rows"]), 1)
        self.assertEqual(result["service_role_inherited_table_acl_rows"], 1)
        self.assertEqual(result["service_role_inherited_column_acl_rows"], 1)
        self.assertEqual(result["w86_candidate_parent_acl_gate"], "BLOCKED_PARENT_ROLE_ACL")
        self.assertIs(result["hosted_write_authorized"], False)
        self.assertEqual(
            result["hosted_write_authorization_status"],
            "NOT_AUTHORIZED_BY_OFFLINE_REVIEWER",
        )
        self.assertIn("w86_acl_probe_parent", result["service_role_inherited_table_acl_entries"][0]["grantee_role"])
        self.assertIsNone(result["source_checkout_head_sha"])
        self.assertIsNone(result["source_migrations_worktree_clean"])
        self.assertRegex(result["source_migration_manifest_sha256"], r"^[0-9a-f]{64}$")

    def test_rejects_query12_privilege_mismatch_against_query13(self):
        payload = json.loads((self.evidence / "query_12.json").read_text(encoding="utf-8"))
        service_update = next(
            row for row in payload["response"]
            if row.get("evidence_kind") == "EFFECTIVE_PRIVILEGE"
            and row.get("grantee") == "service_role"
            and row.get("privilege_type") == "UPDATE"
        )
        service_update["effective_privilege"] = False
        save(self.evidence / "query_12.json", payload)
        with self.assertRaisesRegex(review.EvidenceError, "query 12 and query 13 service_role effective privilege maps disagree"):
            review.reconcile(self.evidence, self.repo)

    def test_rejects_query12_owner_mismatch_against_query13(self):
        payload = json.loads((self.evidence / "query_12.json").read_text(encoding="utf-8"))
        row = next(
            row for row in payload["response"]
            if row.get("evidence_kind") == "EFFECTIVE_PRIVILEGE"
            and row.get("grantee") == "service_role"
            and row.get("privilege_type") == "UPDATE"
        )
        row["owner_role"] = "service_role"
        row["effective_privilege"] = True
        save(self.evidence / "query_12.json", payload)
        with self.assertRaisesRegex(review.EvidenceError, "query 12 and query 13 relation identity/RLS metadata disagree"):
            review.reconcile(self.evidence, self.repo)

    def test_rejects_duplicate_query12_effective_privilege(self):
        payload = json.loads((self.evidence / "query_12.json").read_text(encoding="utf-8"))
        effective = next(row for row in payload["response"] if row.get("evidence_kind") == "EFFECTIVE_PRIVILEGE")
        payload["response"].append(dict(effective))
        save(self.evidence / "query_12.json", payload)
        with self.assertRaisesRegex(review.EvidenceError, "effective table ACL matrix incomplete, duplicated or unexpected"):
            review.reconcile(self.evidence, self.repo)

    def test_rejects_non_boolean_query12_effective_privilege(self):
        payload = json.loads((self.evidence / "query_12.json").read_text(encoding="utf-8"))
        effective = next(row for row in payload["response"] if row.get("evidence_kind") == "EFFECTIVE_PRIVILEGE")
        effective["effective_privilege"] = "false"
        save(self.evidence / "query_12.json", payload)
        with self.assertRaisesRegex(review.EvidenceError, "malformed boolean or privilege-source fields"):
            review.reconcile(self.evidence, self.repo)

    def test_rejects_non_boolean_effective_privilege_summary(self):
        payload = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        provenance = payload["response"][0]["w86_acl_provenance"]
        provenance["service_role_effective_privileges"]["UPDATE"] = "false"
        save(self.evidence / "query_13.json", payload)
        with self.assertRaises(review.EvidenceError):
            review.reconcile(self.evidence, self.repo)

    def test_rejects_inherited_acl_entry_without_matching_membership_path(self):
        payload = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        provenance = payload["response"][0]["w86_acl_provenance"]
        provenance["service_role_inherited_table_acl_entries"][0]["membership_depth"] = 2
        save(self.evidence / "query_13.json", payload)
        with self.assertRaisesRegex(review.EvidenceError, "does not match a reachable membership path"):
            review.reconcile(self.evidence, self.repo)

    def test_set_role_only_parent_acl_path_is_reported(self):
        payload = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        provenance = payload["response"][0]["w86_acl_provenance"]
        provenance["service_role_effective_privileges"]["UPDATE"] = False
        acl_payload = json.loads((self.evidence / "query_12.json").read_text(encoding="utf-8"))
        service_update = next(
            row for row in acl_payload["response"]
            if row.get("evidence_kind") == "EFFECTIVE_PRIVILEGE"
            and row.get("grantee") == "service_role"
            and row.get("privilege_type") == "UPDATE"
        )
        service_update["effective_privilege"] = False
        save(self.evidence / "query_12.json", acl_payload)
        provenance["service_role_membership_paths"][1]["all_edges_inherit"] = False
        provenance["service_role_membership_paths"][1]["all_edges_set_role"] = True
        provenance["service_role_inherited_table_acl_entries"][0]["all_membership_edges_inherit"] = False
        provenance["service_role_inherited_table_acl_entries"][0]["all_membership_edges_set_role"] = True
        provenance["service_role_inherited_column_acl_entries"][0]["all_membership_edges_inherit"] = False
        provenance["service_role_inherited_column_acl_entries"][0]["all_membership_edges_set_role"] = True
        save(self.evidence / "query_13.json", payload)

        result = review.reconcile(self.evidence, self.repo)
        self.assertEqual(result["service_role_set_role_path_count"], 1)
        self.assertEqual(result["service_role_inherited_table_acl_rows"], 1)
        self.assertEqual(result["service_role_inherited_column_acl_rows"], 1)
        self.assertEqual(result["w86_candidate_parent_acl_gate"], "BLOCKED_PARENT_ROLE_ACL")
        self.assertIs(result["hosted_write_authorized"], False)
        self.assertEqual(
            result["service_role_parent_role_acl_path_semantics"],
            "entries reachable through INHERIT or SET ROLE",
        )

    def test_rejects_parent_acl_row_without_set_role_path_evidence(self):
        payload = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        provenance = payload["response"][0]["w86_acl_provenance"]
        del provenance["service_role_inherited_table_acl_entries"][0]["all_membership_edges_set_role"]
        save(self.evidence / "query_13.json", payload)
        with self.assertRaises(review.EvidenceError):
            review.reconcile(self.evidence, self.repo)

    def test_rejects_missing_relation_owner_identity(self):
        payload = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        provenance = payload["response"][0]["w86_acl_provenance"]
        provenance["relation"].pop("owner_role")
        save(self.evidence / "query_13.json", payload)
        with self.assertRaises(review.EvidenceError):
            review.reconcile(self.evidence, self.repo)

    def test_rejects_missing_root_service_role_membership_path(self):
        payload = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        provenance = payload["response"][0]["w86_acl_provenance"]
        provenance["service_role_membership_paths"] = [
            item for item in provenance["service_role_membership_paths"]
            if item.get("depth") != 0
        ]
        save(self.evidence / "query_13.json", payload)
        with self.assertRaises(review.EvidenceError):
            review.reconcile(self.evidence, self.repo)

    def test_rejects_disconnected_or_duplicated_membership_paths(self):
        original = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        mutations = (
            ("disconnected parent", lambda paths: paths[1].update(member_of_role="unobserved_parent")),
            ("root claims parent", lambda paths: paths[0].update(member_of_role="fabricated_parent")),
            ("duplicate path", lambda paths: paths.append(dict(paths[1]))),
            ("non-string parent", lambda paths: paths[1].update(member_of_role=17)),
            ("missing parent field", lambda paths: paths[1].pop("member_of_role")),
            ("flags re-enabled after false edge", lambda paths: (
                paths[1].update(all_edges_inherit=False),
                paths.append({
                    "role_name": "nested_role", "depth": 2,
                    "member_of_role": "w86_acl_probe_parent",
                    "all_edges_inherit": True, "all_edges_set_role": True,
                }),
            )),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                payload = json.loads(json.dumps(original))
                paths = payload["response"][0]["w86_acl_provenance"]["service_role_membership_paths"]
                mutate(paths)
                save(self.evidence / "query_13.json", payload)
                with self.assertRaisesRegex(review.EvidenceError, "role/read-only/shape checks"):
                    review.reconcile(self.evidence, self.repo)

    def test_rejects_membership_path_without_valid_depth(self):
        payload = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        provenance = payload["response"][0]["w86_acl_provenance"]
        provenance["service_role_membership_paths"][1].pop("depth")
        save(self.evidence / "query_13.json", payload)
        with self.assertRaises(review.EvidenceError):
            review.reconcile(self.evidence, self.repo)
    def test_relation_owner_set_role_path_blocks_even_without_acl_entries(self):
        payload = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        provenance = payload["response"][0]["w86_acl_provenance"]
        provenance["relation"]["owner_role"] = "w86_acl_probe_parent"
        acl_payload = json.loads((self.evidence / "query_12.json").read_text(encoding="utf-8"))
        for acl_row in acl_payload["response"]:
            acl_row["owner_role"] = provenance["relation"]["owner_role"]
        save(self.evidence / "query_12.json", acl_payload)
        provenance["service_role_membership_paths"] = [
            {"role_name": "service_role", "depth": 0, "member_of_role": None,
             "all_edges_inherit": True, "all_edges_set_role": True},
            {"role_name": "w86_acl_probe_parent", "depth": 1, "member_of_role": "service_role",
             "all_edges_inherit": False, "all_edges_set_role": True},
        ]
        provenance["service_role_inherited_table_acl_entries"] = []
        provenance["service_role_inherited_column_acl_entries"] = []
        save(self.evidence / "query_13.json", payload)

        result = review.reconcile(self.evidence, self.repo)
        self.assertEqual(result["relation_owner_role"], "w86_acl_probe_parent")
        self.assertEqual(result["service_role_relation_owner_path_count"], 1)
        self.assertEqual(result["w86_candidate_parent_acl_gate"], "BLOCKED_RELATION_OWNER_PATH")
        self.assertIs(result["hosted_write_authorized"], False)
        self.assertTrue(any("can set role to the owner" in item.lower() for item in result["hosted_write_blockers"]))

    def test_relation_owner_inherit_path_blocks_even_without_set_role(self):
        payload = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        provenance = payload["response"][0]["w86_acl_provenance"]
        provenance["relation"]["owner_role"] = "w86_acl_probe_parent"
        acl_payload = json.loads((self.evidence / "query_12.json").read_text(encoding="utf-8"))
        for acl_row in acl_payload["response"]:
            acl_row["owner_role"] = provenance["relation"]["owner_role"]
        save(self.evidence / "query_12.json", acl_payload)
        provenance["service_role_membership_paths"] = [
            {"role_name": "service_role", "depth": 0, "member_of_role": None,
             "all_edges_inherit": True, "all_edges_set_role": True},
            {"role_name": "w86_acl_probe_parent", "depth": 1, "member_of_role": "service_role",
             "all_edges_inherit": True, "all_edges_set_role": False},
        ]
        provenance["service_role_inherited_table_acl_entries"] = []
        provenance["service_role_inherited_column_acl_entries"] = []
        provenance["service_role_effective_privileges"] = {
            privilege: True for privilege in review.PRIVILEGES
        }
        for acl_row in acl_payload["response"]:
            if acl_row.get("evidence_kind") == "EFFECTIVE_PRIVILEGE" and acl_row.get("grantee") == "service_role":
                acl_row["effective_privilege"] = True
        save(self.evidence / "query_12.json", acl_payload)
        save(self.evidence / "query_13.json", payload)

        result = review.reconcile(self.evidence, self.repo)
        self.assertEqual(result["relation_owner_role"], "w86_acl_probe_parent")
        self.assertEqual(result["service_role_relation_owner_path_count"], 1)
        self.assertEqual(result["w86_candidate_parent_acl_gate"], "BLOCKED_RELATION_OWNER_PATH")
        self.assertIs(result["hosted_write_authorized"], False)
        self.assertTrue(any("inherits owner authority" in item.lower() for item in result["hosted_write_blockers"]))
    def test_service_role_as_relation_owner_blocks_at_root_path(self):
        payload = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        provenance = payload["response"][0]["w86_acl_provenance"]
        provenance["relation"]["owner_role"] = "service_role"
        acl_payload = json.loads((self.evidence / "query_12.json").read_text(encoding="utf-8"))
        for acl_row in acl_payload["response"]:
            acl_row["owner_role"] = provenance["relation"]["owner_role"]
        save(self.evidence / "query_12.json", acl_payload)
        provenance["service_role_membership_paths"] = [
            {"role_name": "service_role", "depth": 0, "member_of_role": None,
             "all_edges_inherit": True, "all_edges_set_role": True},
        ]
        provenance["service_role_inherited_table_acl_entries"] = []
        provenance["service_role_inherited_column_acl_entries"] = []
        provenance["service_role_effective_privileges"] = {
            privilege: True for privilege in review.PRIVILEGES
        }
        for acl_row in acl_payload["response"]:
            if acl_row.get("evidence_kind") == "EFFECTIVE_PRIVILEGE" and acl_row.get("grantee") == "service_role":
                acl_row["effective_privilege"] = True
        save(self.evidence / "query_12.json", acl_payload)
        save(self.evidence / "query_13.json", payload)

        result = review.reconcile(self.evidence, self.repo)
        self.assertEqual(result["relation_owner_role"], "service_role")
        self.assertEqual(result["service_role_relation_owner_path_count"], 1)
        self.assertEqual(result["w86_candidate_parent_acl_gate"], "BLOCKED_RELATION_OWNER_PATH")
        self.assertIs(result["hosted_write_authorized"], False)
    def test_authenticated_parent_path_blocks_future_select_grant(self):
        payload = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        provenance = payload["response"][0]["w86_acl_provenance"]
        provenance["service_role_membership_paths"] = [
            {"role_name": "service_role", "depth": 0, "member_of_role": None,
             "all_edges_inherit": True, "all_edges_set_role": True},
            {"role_name": "authenticated", "depth": 1, "member_of_role": "service_role",
             "all_edges_inherit": False, "all_edges_set_role": True},
        ]
        provenance["service_role_inherited_table_acl_entries"] = []
        provenance["service_role_inherited_column_acl_entries"] = []
        save(self.evidence / "query_13.json", payload)

        result = review.reconcile(self.evidence, self.repo)
        self.assertEqual(result["service_role_authenticated_parent_path_count"], 1)
        self.assertEqual(result["w86_candidate_parent_acl_gate"], "BLOCKED_AUTHENTICATED_ROLE_PATH")
        self.assertIs(result["hosted_write_authorized"], False)
        self.assertTrue(any(
            "w86 grants select to authenticated" in item.lower()
            for item in result["hosted_write_blockers"]
        ))
        self.assertEqual(result["service_role_inherited_table_acl_rows"], 0)
        self.assertEqual(result["service_role_inherited_column_acl_rows"], 0)

    def test_no_parent_acl_observed_still_never_authorizes_hosted_write(self):
        payload = json.loads((self.evidence / "query_13.json").read_text(encoding="utf-8"))
        provenance = payload["response"][0]["w86_acl_provenance"]
        provenance["service_role_effective_privileges"]["UPDATE"] = True
        provenance["service_role_membership_paths"] = [
            item for item in provenance["service_role_membership_paths"]
            if item.get("depth") == 0
        ]
        provenance["service_role_inherited_table_acl_entries"] = []
        provenance["service_role_inherited_column_acl_entries"] = []
        save(self.evidence / "query_13.json", payload)

        result = review.reconcile(self.evidence, self.repo)
        self.assertEqual(result["w86_candidate_parent_acl_gate"], "NO_PARENT_ROLE_ACL_OBSERVED")
        self.assertIs(result["hosted_write_authorized"], False)
        self.assertEqual(
            result["hosted_write_authorization_status"],
            "NOT_AUTHORIZED_BY_OFFLINE_REVIEWER",
        )
        self.assertTrue(any("historical migration sql provenance" in item.lower()
                            for item in result["hosted_write_blockers"]))
        rendered = review.render_markdown(result)
        self.assertIn("NO_PARENT_ROLE_ACL_OBSERVED", rendered)
        self.assertIn("hosted writes remain unauthorized", rendered.lower())

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

    def test_runbook_documents_owner_authority_in_both_membership_modes(self):
        runbook_path = Path(__file__).resolve().parents[1] / "docs" / "ZAVQERA_HOSTED_MIGRATION_EFFECT_AUDIT_RUNBOOK_2026-10-15.md"
        runbook = runbook_path.read_text(encoding="utf-8")
        self.assertIn("REVIEW REQUIRED / NO-GO", runbook)
        self.assertIn("obtain owner authority through either `INHERIT` or `SET ROLE`", runbook)
        self.assertIn("any path from `service_role` to the table owner with either `INHERIT` or `SET ROLE` enabled", runbook)
        self.assertIn("no fresh hosted 13-query capture has been recorded", runbook)
        self.assertIn("There is no hosted-write authorization in this workflow.", runbook)
        self.assertIn("Historical 12-query offline comparison — obsolete, not a current procedure", runbook)
        historical = runbook.split("## Historical 12-query offline comparison — obsolete, not a current procedure", 1)[1]
        historical = historical.split("## Verified isolated SQL smoke", 1)[0]
        self.assertNotIn("$auditDir =", historical)
        self.assertIn("the current reviewer requires `query_13.json`", historical)
        self.assertIn("Current authoritative capture procedure — 13 queries", runbook)
    def test_report_is_no_go(self):
        result = review.reconcile(self.evidence, self.repo)
        rendered = review.render_markdown(result)
        self.assertIn("REVIEW REQUIRED / RELEASE NO-GO", rendered)
        self.assertIn("Same-name/different-version", rendered)
        self.assertIn("Source checkout HEAD", rendered)
        self.assertIn("Source migration manifest SHA-256", rendered)
        self.assertIn("service_role inherited table ACL rows: **1**", rendered)
        self.assertIn("W86 parent-role ACL gate: **BLOCKED_PARENT_ROLE_ACL**", rendered)
        self.assertIn("Hosted write authorized: **False**", rendered)
        self.assertIn("inherited ACL row is a blocker", rendered)
        self.assertIn("not complete proof of reachability", rendered)


if __name__ == "__main__":
    unittest.main()

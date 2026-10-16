import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "supabase_readonly_migration_effect_audit.py"
spec = importlib.util.spec_from_file_location("readonly_effect_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(audit)

PROJECT_REF = "a" * 20
TOKEN = "test-token-never-persist-this"
ENV = {
    "SUPABASE_PROJECT_REF": PROJECT_REF,
    "SUPABASE_ACCESS_TOKEN": TOKEN,
    "ZAVQERA_AUDIT_CONFIRMATION": "DEVELOPMENT_ONLY_READ_ONLY",
}


def valid_project(name="ZAVQERA Development"):
    return {"id": PROJECT_REF, "name": name, "region": "eu-west-1", "status": "ACTIVE_HEALTHY"}


def valid_role_row(**overrides):
    row = {
        "current_user": "supabase_read_only_user",
        "session_user": "supabase_read_only_user",
        "server_version_num": 170006,
        "transaction_read_only": True,
        "rolsuper": False,
        "rolcreatedb": False,
        "rolcreaterole": False,
        "rolbypassrls": True,
        "migration_ledger_relation": "supabase_migrations.schema_migrations",
    }
    row.update(overrides)
    return row


def valid_provenance_payload(inherited=True, **overrides):
    privileges = {
        "SELECT": False, "INSERT": False, "UPDATE": inherited, "DELETE": False,
        "TRUNCATE": False, "REFERENCES": False, "TRIGGER": False, "MAINTAIN": False,
    }
    payload = {
        "probe_name": "w86_acl_provenance_v1",
        "current_user": "supabase_read_only_user",
        "session_user": "supabase_read_only_user",
        "transaction_read_only": "on",
        "relation": {"exists": True, "owner_role": "postgres", "schema_name": "public",
                     "relation_name": "agent_executions", "stored_acl_is_null": False,
                     "row_level_security_enabled": True, "row_level_security_forced": False},
        "service_role_effective_privileges": privileges,
        "service_role_membership_paths": [{"role_name": "service_role", "depth": 0,
                                            "member_of_role": None, "all_edges_inherit": True,
                                            "all_edges_set_role": True}],
        "table_acl_entries": [],
        "column_acl_entries": [],
        "service_role_inherited_table_acl_entries": (
            [{"grantee_role": "w86_acl_probe_parent", "membership_depth": 1,
              "all_membership_edges_inherit": True, "all_membership_edges_set_role": True,
              "privilege_type": "UPDATE",
              "is_grantable": False, "grantor": "postgres"}] if inherited else []
        ),
        "service_role_inherited_column_acl_entries": (
            [{"column_name": "id", "grantee_role": "w86_acl_probe_parent", "membership_depth": 1,
              "all_membership_edges_inherit": True, "all_membership_edges_set_role": True,
              "privilege_type": "SELECT",
              "is_grantable": False, "grantor": "postgres"}] if inherited else []
        ),
    }
    if inherited:
        payload["service_role_membership_paths"].append({
            "role_name": "w86_acl_probe_parent", "depth": 1,
            "member_of_role": "service_role", "all_edges_inherit": True,
            "all_edges_set_role": True,
        })
    payload.update(overrides)
    return payload


class ReadOnlyEffectAuditTests(unittest.TestCase):
    def setUp(self):
        self.created_output = []

    def _capture_evidence_path(self, text):
        match = re.search(r"Evidence: (.+)", text)
        if match:
            path = Path(match.group(1).strip())
            self.created_output.append(path)

    def tearDown(self):
        for path in self.created_output:
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
            try:
                parent = path.parent
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
            except OSError:
                pass

    def _run_with_fake_api(self, fake_api):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, ENV, clear=False), \
             patch.object(audit, "request_json", side_effect=fake_api), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = audit.main()
        output = stdout.getvalue() + stderr.getvalue()
        self._capture_evidence_path(output)
        return code, output

    def test_checked_in_pack_is_pinned_to_thirteen_selects(self):
        root = Path(__file__).resolve().parents[1]
        statements, digest = audit.load_pack(root)
        self.assertEqual(len(statements), 13)
        self.assertEqual(digest, audit.PACK_SHA256)
        self.assertEqual(audit.ACL_PROVENANCE_SHA256,
                         "f9f56944ddd04dd135329ff930cf5259e215eb89f30784b75e03a93f221ff38e")
        self.assertTrue(all(re.match(r"(?is)^\s*SELECT\b", audit.no_comments(s).strip()) for s in statements))

    def test_acl_provenance_query_excludes_direct_grants_from_parent_acl_rows(self):
        root = Path(__file__).resolve().parents[1]
        sql_path = root / "supabase" / "tests" / "hosted_readonly_w86_acl_provenance_query.sql"
        sql = sql_path.read_text(encoding="utf-8")
        self.assertEqual(sql.count("AND rp.depth > 0"), 2)
        self.assertEqual(sql.count("'all_membership_edges_set_role', rp.can_set_role"), 2)
        self.assertNotIn("rp.depth = 0 OR rp.inherits_all OR rp.can_set_role", sql)
        self.assertIn("'service_role_effective_privileges'", sql)
        self.assertIn("'table_acl_entries'", sql)
        self.assertIn("'service_role_inherited_table_acl_entries'", sql)
        self.assertIn("'service_role_inherited_column_acl_entries'", sql)

    def test_powershell_wrapper_handles_token_locally_and_cleans_environment(self):
        wrapper_path = SCRIPT.parent / "run_zavqera_readonly_effect_audit.ps1"
        wrapper = wrapper_path.read_text(encoding="utf-8")
        self.assertIn("Read-Host", wrapper)
        self.assertIn("-AsSecureString", wrapper)
        self.assertIn("SecureStringToBSTR", wrapper)
        self.assertIn("ZeroFreeBSTR", wrapper)
        self.assertIn(r"Remove-Item Env:\SUPABASE_ACCESS_TOKEN", wrapper)
        self.assertLess(wrapper.index(r"Remove-Item Env:\SUPABASE_ACCESS_TOKEN"),
                        wrapper.index("py -3 $reviewer"))
        self.assertIn("DEVELOPMENT_ONLY_READ_ONLY", wrapper)
        self.assertIn("py -3 $runner --self-test", wrapper)
        self.assertIn("py -3 $runner 2>&1", wrapper)
        self.assertIn("Compress-Archive", wrapper)
        self.assertNotRegex(wrapper, r"sb_secret_[A-Za-z0-9_-]{20,}")

    def test_splitter_handles_literals_nested_comments_and_dollar_quotes(self):
        sql = "-- semicolon ;\nSELECT 'a;''b' AS x; /* outer ; /* inner ; */ end */ SELECT $$c;d$$ AS y;"
        self.assertEqual(len(audit.split_statements(sql)), 2)

    def test_project_identity_mismatch_stops_before_sql(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            return valid_project(name="ZAVQERA Main")
        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 3)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "GET")
        self.assertIn("no SQL sent", output)

    def test_wrong_effective_role_stops_after_first_read_only_query(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            return {"result": [valid_role_row(current_user="postgres")]}
        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5)
        posts = [call for call in calls if call[0] == "POST"]
        self.assertEqual(len(posts), 1)
        self.assertTrue(posts[0][1].endswith("/database/query/read-only"))

    def test_read_write_transaction_stops_after_first_query(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            return {"result": [valid_role_row(transaction_read_only=False)]}
        code, _ = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 1)

    def test_unknown_response_shape_fails_closed(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            return {"unknown_response": [{"current_user": "supabase_read_only_user"}]}
        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 1)
        self.assertIn("unknown response shape", output)

    def test_happy_path_uses_only_explicit_read_only_endpoint_and_never_persists_token(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((token, method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for _, verb, _, _ in calls if verb == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            if number == 11:
                return {"result": [
                    {"version": "20261013100000", "name": "w80_fail_closed_workspace_role_checks"},
                    {"version": "20261015100000", "name": "w83_workspace_invitation_privilege_correction"},
                ]}
            if number == 12:
                rows = []
                for role in ("anon", "authenticated", "service_role", "postgres"):
                    for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN"):
                        rows.append({
                            "evidence_kind": "EFFECTIVE_PRIVILEGE", "schema_name": "public",
                            "relation_name": "agent_executions", "owner_role": "postgres",
                            "row_level_security_enabled": True, "row_level_security_forced": False,
                            "grantee": role, "privilege_type": privilege,
                            "effective_privilege": role == "postgres" or (role == "service_role" and privilege == "UPDATE"),
                            "is_grantable": None, "grantor": None,
                        })
                rows.append({
                    "evidence_kind": "STORED_ACL", "schema_name": "public",
                    "relation_name": "agent_executions", "owner_role": "postgres",
                    "row_level_security_enabled": True, "row_level_security_forced": False,
                    "grantee": "postgres", "privilege_type": "SELECT", "effective_privilege": None,
                    "is_grantable": False, "grantor": "postgres",
                })
                return {"result": rows}
            if number == 13:
                return {"result": [{"w86_acl_provenance": valid_provenance_payload(inherited=True)}]}
            return {"result": [{"query_number": number, "ok": True}]}
        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 0)
        self.assertIn('"status": "CAPTURED_FOR_MANUAL_REVIEW"', output)
        self.assertIn('"service_role_inherited_table_acl_rows": 1', output)
        self.assertIn('"service_role_inherited_column_acl_rows": 1', output)
        posts = [call for call in calls if call[1] == "POST"]
        self.assertEqual(len(posts), 13)
        self.assertTrue(all(call[2].endswith("/database/query/read-only") for call in posts))
        self.assertFalse(any(call[2].endswith("/database/query") for call in posts))
        self.assertTrue(all(call[0] == TOKEN for call in calls))  # token is passed to the API client only
        evidence = self.created_output[-1]
        all_text = "\n".join(p.read_text(encoding="utf-8") for p in evidence.glob("*.json"))
        self.assertNotIn(TOKEN, all_text)
        metadata = json.loads((evidence / "run_metadata.json").read_text(encoding="utf-8"))
        self.assertFalse(metadata["token_saved"])

    def test_w66_acl_metadata_must_match_query13_relation_identity(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for verb, _, _ in calls if verb == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            if number < 11:
                return {"result": [{"query_number": number, "ok": True}]}
            if number == 11:
                return {"result": [
                    {"version": "20261013100000", "name": "w80_fail_closed_workspace_role_checks"},
                    {"version": "20261015100000", "name": "w83_workspace_invitation_privilege_correction"},
                ]}
            if number == 12:
                rows = []
                for role in ("anon", "authenticated", "service_role", "postgres"):
                    for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN"):
                        rows.append({
                            "evidence_kind": "EFFECTIVE_PRIVILEGE", "schema_name": "public",
                            "relation_name": "agent_executions", "owner_role": "service_role",
                            "row_level_security_enabled": True, "row_level_security_forced": False,
                            "grantee": role, "privilege_type": privilege,
                            "effective_privilege": False, "is_grantable": None, "grantor": None,
                        })
                return {"result": rows}
            return {"result": [{"w86_acl_provenance": valid_provenance_payload(inherited=False)}]}

        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5, output)
        self.assertIn("query 12 and query 13 relation identity/RLS metadata disagree", output)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 13)

    def test_w66_acl_non_boolean_effective_privilege_fails_closed(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for verb, _, _ in calls if verb == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            if number == 11:
                return {"result": [
                    {"version": "20261013100000", "name": "w80_fail_closed_workspace_role_checks"},
                    {"version": "20261015100000", "name": "w83_workspace_invitation_privilege_correction"},
                ]}
            if number < 12:
                return {"result": [{"query_number": number, "ok": True}]}
            if number == 12:
                rows = []
                for role in ("anon", "authenticated", "service_role", "postgres"):
                    for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN"):
                        rows.append({
                            "evidence_kind": "EFFECTIVE_PRIVILEGE", "schema_name": "public",
                            "relation_name": "agent_executions", "owner_role": "postgres",
                            "row_level_security_enabled": True, "row_level_security_forced": False,
                            "grantee": role, "privilege_type": privilege,
                            "effective_privilege": False, "is_grantable": None, "grantor": None,
                        })
                rows[0]["effective_privilege"] = "false"
                return {"result": rows}
            self.fail("query 13 must not run after malformed query 12")
        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5, output)
        self.assertIn("effective/stored ACL result set incomplete, duplicated, or malformed", output)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 12)

    def test_w66_acl_duplicate_effective_privilege_fails_closed(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for verb, _, _ in calls if verb == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            if number == 11:
                return {"result": [
                    {"version": "20261013100000", "name": "w80_fail_closed_workspace_role_checks"},
                    {"version": "20261015100000", "name": "w83_workspace_invitation_privilege_correction"},
                ]}
            if number < 12:
                return {"result": [{"query_number": number, "ok": True}]}
            if number == 12:
                rows = []
                for role in ("anon", "authenticated", "service_role", "postgres"):
                    for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN"):
                        rows.append({
                            "evidence_kind": "EFFECTIVE_PRIVILEGE", "schema_name": "public",
                            "relation_name": "agent_executions", "owner_role": "postgres",
                            "row_level_security_enabled": True, "row_level_security_forced": False,
                            "grantee": role, "privilege_type": privilege,
                            "effective_privilege": False, "is_grantable": None, "grantor": None,
                        })
                rows.append(dict(rows[0]))
                return {"result": rows}
            self.fail("query 13 must not run after duplicated query 12")
        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5, output)
        self.assertIn("effective/stored ACL result set incomplete, duplicated, or malformed", output)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 12)

    def test_w86_provenance_non_boolean_effective_privilege_fails_closed(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for verb, _, _ in calls if verb == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            if number == 11:
                return {"result": [
                    {"version": "20261013100000", "name": "w80_fail_closed_workspace_role_checks"},
                    {"version": "20261015100000", "name": "w83_workspace_invitation_privilege_correction"},
                ]}
            if number == 12:
                rows = []
                for role in ("anon", "authenticated", "service_role", "postgres"):
                    for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN"):
                        rows.append({
                            "evidence_kind": "EFFECTIVE_PRIVILEGE", "schema_name": "public",
                            "relation_name": "agent_executions", "owner_role": "postgres",
                            "row_level_security_enabled": True, "row_level_security_forced": False,
                            "grantee": role, "privilege_type": privilege,
                            "effective_privilege": False, "is_grantable": None, "grantor": None,
                        })
                return {"result": rows}
            provenance = valid_provenance_payload(inherited=False)
            provenance["service_role_effective_privileges"]["UPDATE"] = "false"
            return {"result": [{"w86_acl_provenance": provenance}]}

        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5)
        self.assertIn("ACL provenance result incomplete/unrecognized", output)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 13)

    def test_w86_provenance_acl_entry_must_match_membership_path(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for verb, _, _ in calls if verb == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            if number == 11:
                return {"result": [
                    {"version": "20261013100000", "name": "w80_fail_closed_workspace_role_checks"},
                    {"version": "20261015100000", "name": "w83_workspace_invitation_privilege_correction"},
                ]}
            if number == 12:
                rows = []
                for role in ("anon", "authenticated", "service_role", "postgres"):
                    for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN"):
                        rows.append({
                    "evidence_kind": "EFFECTIVE_PRIVILEGE", "schema_name": "public",
                    "relation_name": "agent_executions", "owner_role": "postgres",
                    "row_level_security_enabled": True, "row_level_security_forced": False,
                    "grantee": role, "privilege_type": privilege,
                    "effective_privilege": False, "is_grantable": None, "grantor": None,
                })
                return {"result": rows}
            provenance = valid_provenance_payload(inherited=True)
            provenance["service_role_inherited_table_acl_entries"][0]["membership_depth"] = 2
            return {"result": [{"w86_acl_provenance": provenance}]}

        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5)
        self.assertIn("does not match a reachable membership path", output)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 13)

    def test_w86_provenance_role_mismatch_fails_closed(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for verb, _, _ in calls if verb == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            if number == 11:
                return {"result": [{"version": "20261015100000", "name": "w83_workspace_invitation_privilege_correction"}]}
            if number == 12:
                rows = []
                for role in ("anon", "authenticated", "service_role", "postgres"):
                    for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN"):
                        rows.append({
                    "evidence_kind": "EFFECTIVE_PRIVILEGE", "schema_name": "public",
                    "relation_name": "agent_executions", "owner_role": "postgres",
                    "row_level_security_enabled": True, "row_level_security_forced": False,
                    "grantee": role, "privilege_type": privilege,
                    "effective_privilege": False, "is_grantable": None, "grantor": None,
                })
                return {"result": rows}
            return {"result": [{"w86_acl_provenance": valid_provenance_payload(inherited=False, current_user="postgres")}]}
        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5)
        self.assertIn("w86_acl_provenance", output)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 13)

    def test_w86_provenance_missing_relation_owner_fails_closed(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for verb, _, _ in calls if verb == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            if number == 11:
                return {"result": [{"version": "20261015100000", "name": "w83_workspace_invitation_privilege_correction"}]}
            if number == 12:
                rows = []
                for role in ("anon", "authenticated", "service_role", "postgres"):
                    for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN"):
                        rows.append({
                    "evidence_kind": "EFFECTIVE_PRIVILEGE", "schema_name": "public",
                    "relation_name": "agent_executions", "owner_role": "postgres",
                    "row_level_security_enabled": True, "row_level_security_forced": False,
                    "grantee": role, "privilege_type": privilege,
                    "effective_privilege": False, "is_grantable": None, "grantor": None,
                })
                return {"result": rows}
            provenance = valid_provenance_payload(inherited=False)
            provenance["relation"].pop("owner_role")
            return {"result": [{"w86_acl_provenance": provenance}]}
        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5)
        self.assertIn("ACL provenance result incomplete/unrecognized", output)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 13)
    def test_w86_provenance_missing_root_membership_path_fails_closed(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for verb, _, _ in calls if verb == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            if number == 11:
                return {"result": [{"version": "20261015100000", "name": "w83_workspace_invitation_privilege_correction"}]}
            if number == 12:
                rows = []
                for role in ("anon", "authenticated", "service_role", "postgres"):
                    for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN"):
                        rows.append({
                    "evidence_kind": "EFFECTIVE_PRIVILEGE", "schema_name": "public",
                    "relation_name": "agent_executions", "owner_role": "postgres",
                    "row_level_security_enabled": True, "row_level_security_forced": False,
                    "grantee": role, "privilege_type": privilege,
                    "effective_privilege": False, "is_grantable": None, "grantor": None,
                })
                return {"result": rows}
            provenance = valid_provenance_payload(inherited=False)
            provenance["service_role_membership_paths"] = []
            return {"result": [{"w86_acl_provenance": provenance}]}
        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5)
        self.assertIn("ACL provenance result incomplete/unrecognized", output)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 13)
    def test_api_query_error_stops_without_sending_later_queries(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for verb, _, _ in calls if verb == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            return {"error": {"message": "catalog access denied"}}
        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 4)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 2)
        self.assertIn("query_02", output)


    def test_empty_migration_ledger_fails_closed_before_table_acl_query(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for verb, _, _ in calls if verb == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            if number == 11:
                return {"result": []}
            return {"result": [{"should_not_execute": True}]}
        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5)
        self.assertIn("ledger query returned zero rows", output)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 11)

    def test_incomplete_w66_acl_matrix_fails_closed(self):
        calls = []
        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for verb, _, _ in calls if verb == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            if number == 11:
                return {"result": [{"version": "20261015100000", "name": "w83_workspace_invitation_privilege_correction"}]}
            if number == 12:
                return {"result": [{"evidence_kind": "EFFECTIVE_PRIVILEGE", "relation_name": "agent_executions",
                                    "grantee": "service_role", "privilege_type": "INSERT"}]}
            return {"result": []}
        code, output = self._run_with_fake_api(fake_api)
        self.assertEqual(code, 5)
        self.assertIn("effective/stored ACL result set incomplete", output)
        self.assertEqual(len([call for call in calls if call[0] == "POST"]), 12)

    def test_runbook_points_to_current_13_query_secure_wrapper(self):
        root = Path(__file__).resolve().parents[1]
        runbook = (root / "docs" / "ZAVQERA_HOSTED_MIGRATION_EFFECT_AUDIT_RUNBOOK_2026-10-15.md").read_text(encoding="utf-8")
        self.assertIn("Current status — 2026-10-16: REVIEW REQUIRED / NO-GO.", runbook)
        self.assertIn("no fresh hosted 13-query capture has been recorded", runbook)
        self.assertIn("`query_13.json`", runbook)
        self.assertIn("f9f56944ddd04dd135329ff930cf5259e215eb89f30784b75e03a93f221ff38e", runbook)
        current = runbook.split("## Current Windows PowerShell procedure — use only this procedure", 1)[1]
        current = current.split("## Expected output and interpretation", 1)[0]
        self.assertIn(r".\tools\run_zavqera_readonly_effect_audit.ps1", current)
        self.assertIn("Upload **only the ZIP**", current)
        self.assertNotIn("$secure = Read-Host", current)
        self.assertNotIn("py -3 tools/supabase_readonly_migration_effect_audit.py", current)
if __name__ == "__main__":
    unittest.main()

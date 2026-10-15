import contextlib
import importlib.util
import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "supabase_readonly_catalog_audit.py"
spec = importlib.util.spec_from_file_location("readonly_catalog_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(audit)

PROJECT_REF = "a" * 20
ENV = {
    "SUPABASE_PROJECT_REF": PROJECT_REF,
    "SUPABASE_ACCESS_TOKEN": "test-token-never-sent-to-network",
    "ZAVQERA_AUDIT_CONFIRMATION": "DEVELOPMENT_ONLY_READ_ONLY",
}


def valid_project(name="ZAVQERA Development"):
    return {"id": PROJECT_REF, "name": name, "region": "eu-west-1", "status": "ACTIVE_HEALTHY"}


def valid_role_row(user="supabase_read_only_user"):
    return {
        "current_user": user,
        "session_user": "supabase_read_only_user",
        "server_version_num": 170011,
        "transaction_read_only": True,
        "rolsuper": False,
        "rolcreatedb": False,
        "rolcreaterole": False,
        "rolbypassrls": True,
        "migration_ledger_relation": "supabase_migrations.schema_migrations",
    }


class ReadOnlyCatalogAuditTests(unittest.TestCase):
    def test_checked_in_query_pack_is_hash_pinned_and_select_only(self):
        root = Path(__file__).resolve().parents[1]
        queries, digest = audit.load_pack(root)
        self.assertEqual(len(queries), 8)
        self.assertEqual(digest, audit.PACK_SHA256)

    def test_splitter_ignores_semicolons_inside_quotes_and_comments(self):
        sql = "-- comment ;\nSELECT 'a;''b' AS x; /* nested ; /* still comment ; */ end */ SELECT $$c;d$$ AS y;"
        statements = audit.split_statements(sql)
        self.assertEqual(len(statements), 2)
        self.assertTrue(statements[0].lstrip().startswith("SELECT"))
        self.assertTrue(statements[1].lstrip().startswith("SELECT"))

    def test_read_only_api_rows_shape(self):
        self.assertEqual(
            audit.rows_from({"result": [{"current_user": "supabase_read_only_user"}]}),
            [{"current_user": "supabase_read_only_user"}],
        )

    def test_unknown_response_shape_fails_closed(self):
        self.assertIsNone(audit.rows_from({"unexpected": [{"current_user": "postgres"}]}))

    def test_ledger_mismatch_is_blocking(self):
        local = [
            ("20261015110000", "w84_postgres_function_default_acl_hardening"),
            ("20261015120000", "w85_test"),
        ]
        remote = {"result": [{"version": local[0][0], "name": local[0][1]}]}
        result = audit.compare_ledger(remote, local)
        self.assertEqual(result["comparison"], "MISMATCH_BLOCKING")
        self.assertEqual(result["local_count"], 2)
        self.assertEqual(result["remote_count"], 1)

    def test_project_identity_mismatch_stops_before_any_sql(self):
        calls = []

        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            return valid_project("ZAVQERA Main")

        with patch.dict(os.environ, ENV, clear=False), patch.object(audit, "request_json", side_effect=fake_api), contextlib.redirect_stderr(io.StringIO()):
            result = audit.main()
        self.assertEqual(result, 3)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "GET")

    def test_wrong_effective_role_stops_after_query_one(self):
        calls = []

        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            return {"result": [valid_role_row(user="postgres")]}

        with patch.dict(os.environ, ENV, clear=False), patch.object(audit, "request_json", side_effect=fake_api), contextlib.redirect_stderr(io.StringIO()):
            result = audit.main()
        self.assertEqual(result, 5)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1][0], "POST")
        self.assertIn("/database/query/read-only", calls[1][1])

    def test_happy_path_calls_only_explicit_read_only_endpoint(self):
        calls = []
        root = Path(__file__).resolve().parents[1]
        local_ledger = [{"version": v, "name": n} for v, n in audit.local_migrations(root)]

        def fake_api(token, method, path, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return valid_project()
            number = sum(1 for meth, _, _ in calls if meth == "POST")
            if number == 1:
                return {"result": [valid_role_row()]}
            if number == 7:
                return {"result": [{"migration_ledger_relation": "supabase_migrations.schema_migrations"}]}
            if number == 8:
                return {"result": local_ledger}
            return {"result": []}

        with patch.dict(os.environ, ENV, clear=False), patch.object(audit, "request_json", side_effect=fake_api), contextlib.redirect_stdout(io.StringIO()):
            result = audit.main()
        self.assertEqual(result, 0)
        posts = [call for call in calls if call[0] == "POST"]
        self.assertEqual(len(posts), 8)
        self.assertTrue(all("/database/query/read-only" in path for _, path, _ in posts))
        self.assertTrue(all(path.endswith("/database/query/read-only") for _, path, _ in posts))
        self.assertFalse(any(path.endswith("/database/query") for _, path, _ in posts))


if __name__ == "__main__":
    unittest.main()

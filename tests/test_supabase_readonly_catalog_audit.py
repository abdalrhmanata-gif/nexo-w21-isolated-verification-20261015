import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "supabase_readonly_catalog_audit.py"
spec = importlib.util.spec_from_file_location("readonly_catalog_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(audit)


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


if __name__ == "__main__":
    unittest.main()

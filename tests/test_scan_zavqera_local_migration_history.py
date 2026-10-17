from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from scan_zavqera_local_migration_history import scan_repository, ScanError  # noqa: E402

TARGET = "supabase/migrations/20260924165500_w30_reconstruct_missing_w5_history_tables.sql"
SQL_BYTES = b"-- historical candidate only; never execute from this test\nSELECT 1;\n"


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


class LocalMigrationHistoryScanTests(unittest.TestCase):
    def _repo(self) -> Path:
        path = Path(tempfile.mkdtemp(prefix="zavqera-local-history-"))
        run_git(path, "init", "-q")
        run_git(path, "config", "user.name", "ZAVQERA Audit Test")
        run_git(path, "config", "user.email", "zavqera-audit-test@example.invalid")
        return path

    def _write_candidate_commit(self, repo: Path) -> str:
        target = repo / TARGET
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(SQL_BYTES)
        run_git(repo, "add", TARGET)
        run_git(repo, "commit", "-qm", "test fixture historical migration source")
        return run_git(repo, "rev-parse", "HEAD")

    def test_reachable_source_is_reported_as_candidate_with_sql_hash_only(self):
        repo = self._repo()
        commit = self._write_candidate_commit(repo)
        result = scan_repository(repo)
        self.assertEqual(result["scan_status"], "COMPLETED_CANDIDATE_SCAN")
        matches = [item for item in result["candidates"] if item["path"] == TARGET and item["commit_sha"] == commit]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["sql_sha256"], hashlib.sha256(SQL_BYTES).hexdigest())
        self.assertEqual(matches[0]["migration_stem"], "w30_reconstruct_missing_w5_history_tables")
        self.assertNotIn("sql_text", matches[0])
        self.assertFalse(result["sql_content_emitted"])
        self.assertFalse(result["hosted_write_authorized"])

    def test_unreachable_commit_object_is_scanned(self):
        repo = self._repo()
        commit = self._write_candidate_commit(repo)
        run_git(repo, "update-ref", "-d", "refs/heads/master")
        run_git(repo, "update-ref", "-d", "refs/heads/main")
        run_git(repo, "reflog", "expire", "--expire=now", "--all")
        result = scan_repository(repo)
        matches = [item for item in result["candidates"] if item["commit_sha"] == commit and item["path"] == TARGET]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["commit_reachability"], "UNREACHABLE_COMMIT_OBJECT")
        self.assertEqual(matches[0]["sql_sha256"], hashlib.sha256(SQL_BYTES).hexdigest())

    def test_no_candidates_is_not_claimed_as_proof_source_never_existed(self):
        repo = self._repo()
        target = repo / "supabase" / "migrations" / "ordinary_migration.sql"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("select 1;\n", encoding="utf-8")
        run_git(repo, "add", ".")
        run_git(repo, "commit", "-qm", "no targeted migration")
        result = scan_repository(repo)
        self.assertEqual(result["candidates"], [])
        self.assertIn("does not prove that the SQL never existed", result["interpretation"])
        self.assertEqual(result["scan_status"], "COMPLETED_CANDIDATE_SCAN")

    def test_non_repository_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="zavqera-not-git-") as temp:
            with self.assertRaises(ScanError):
                scan_repository(temp)

    def test_commit_bound_fails_closed_without_negative_conclusion(self):
        repo = self._repo()
        self._write_candidate_commit(repo)
        with self.assertRaises(ScanError):
            scan_repository(repo, max_commits=0)


if __name__ == "__main__":
    unittest.main()

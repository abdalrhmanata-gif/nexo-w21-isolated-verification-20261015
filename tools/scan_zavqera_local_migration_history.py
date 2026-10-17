#!/usr/bin/env python3
"""Read-only local Git recovery scan for ZAVQERA historical migration sources.

Scans refs, reflogs, and unreachable commit objects in a local clone. It emits
metadata and SHA-256 digests only; it never prints or exports SQL source text,
contacts a network, or connects to a database.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

KNOWN_STEMS = {
    # 22 known same-name/different-version conflicts in the hosted migration ledger.
    "w10_deletion_integrity_read_boundary",
    "w16_audit_history_table_hardening",
    "w30_reconstruct_missing_w5_history_tables",
    "w30_server_only_quota_rls_deny_policy",
    "w36_enable_pro_plan_identity",
    "w41_seed_bounded_research_agent",
    "w42_workspace_rpc_authorization_parity",
    "w43_bounded_agent_execution_runtime",
    "w44_invitation_lifecycle",
    "w45_workspace_member_management",
    "w46_activity_security_hardening",
    "w46_workspace_activity_audit",
    "w47_atomic_workspace_bootstrap",
    "w48_seed_research_agent_for_new_workspaces",
    "w49_agent_execution_recovery",
    "w4_table_privilege_hardening",
    "w50_expired_execution_lease_fence",
    "w51_member_rpc_wrapper_permissions",
    "w7_authoritative_action_mutation",
    "w8_lifecycle_integrity_provenance",
    "w9_1_completed_outcome_guard",
    "w9_verification_outcome_lifecycle",
    # 6 hosted-only migration names.
    "w4_harden_profile_trigger_search_path",
    "w6_authoritative_mission_mutation_and_concurrency",
    "w35_plan_ai_allowances_5_50_300",
    "expose_anonymous_ai_guard_rpc",
    "w44_workspace_invitations_and_activity",
    "w46_invitation_activity_bindings",
}
VERSIONED_SQL = re.compile(
    r"^(?P<version>\d{14})_(?P<stem>[A-Za-z0-9_]+)\.sql$"
)
OID_HEX = re.compile(r"^[0-9a-f]{40,64}$")


class ScanError(RuntimeError):
    pass


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        error = result.stderr.decode("utf-8", errors="replace").strip()
        raise ScanError(f"git {' '.join(args[:3])} failed (exit {result.returncode}): {error}")
    return result


def object_bytes(repo: Path, oid: str) -> bytes:
    result = git(repo, "cat-file", "blob", oid)
    return result.stdout


def _candidate_path(path_bytes: bytes) -> tuple[str, str] | None:
    path = path_bytes.decode("utf-8", errors="replace")
    if not path.startswith("supabase/migrations/"):
        return None
    name = path.rsplit("/", 1)[-1]
    match = VERSIONED_SQL.fullmatch(name)
    if not match or match.group("stem") not in KNOWN_STEMS:
        return None
    return match.group("version"), match.group("stem")


def scan_repository(repo_path: str | Path, max_commits: int = 50000) -> dict[str, Any]:
    repo = Path(repo_path).expanduser().resolve()
    if not repo.is_dir():
        raise ScanError(f"Repository path is not a directory: {repo}")
    root = git(repo, "rev-parse", "--show-toplevel").stdout.decode().strip()
    if Path(root).resolve() != repo:
        # Accept a subdirectory inside a repository, but canonicalize to the root.
        repo = Path(root).resolve()

    reachable_output = git(repo, "rev-list", "--all", "--reflog", "--full-history").stdout
    commits = {
        line.decode("ascii", errors="ignore").strip()
        for line in reachable_output.splitlines()
        if OID_HEX.fullmatch(line.decode("ascii", errors="ignore").strip())
    }
    fsck = git(repo, "fsck", "--full", "--unreachable", "--no-reflogs", "--no-progress", check=False)
    fsck_text = (fsck.stdout + b"\n" + fsck.stderr).decode("utf-8", errors="replace")
    unreachable_commits = set(re.findall(r"(?:unreachable|dangling) commit ([0-9a-f]{40,64})", fsck_text))
    all_commits = commits | unreachable_commits
    if len(all_commits) > max_commits:
        raise ScanError(
            f"Found {len(all_commits)} commits, exceeding max_commits={max_commits}. "
            "Increase --max-commits and rerun; no negative conclusion is permitted."
        )

    candidates: dict[tuple[str, str], dict[str, Any]] = {}
    tree_errors: list[dict[str, str]] = []
    scanned_commits = 0
    for commit in sorted(all_commits):
        scanned_commits += 1
        tree = git(repo, "ls-tree", "-r", "-z", "--full-tree", "--name-only", commit, "--", "supabase/migrations", check=False)
        if tree.returncode != 0:
            tree_errors.append({"commit": commit, "error": tree.stderr.decode("utf-8", errors="replace").strip()})
            continue
        for path_bytes in tree.stdout.split(b"\x00"):
            if not path_bytes:
                continue
            matched = _candidate_path(path_bytes)
            if not matched:
                continue
            version, stem = matched
            path = path_bytes.decode("utf-8", errors="replace")
            ref = git(repo, "rev-parse", f"{commit}:{path}", check=False)
            blob_oid = ref.stdout.decode("ascii", errors="ignore").strip()
            if ref.returncode != 0 or not OID_HEX.fullmatch(blob_oid):
                tree_errors.append({"commit": commit, "error": f"could_not_resolve_blob_for:{path}"})
                continue
            try:
                digest = hashlib.sha256(object_bytes(repo, blob_oid)).hexdigest()
            except ScanError as exc:
                tree_errors.append({"commit": commit, "error": str(exc)})
                continue
            key = (commit, path)
            candidates[key] = {
                "migration_version": version,
                "migration_stem": stem,
                "path": path,
                "commit_sha": commit,
                "git_blob_oid": blob_oid,
                "sql_sha256": digest,
                "commit_reachability": (
                    "REF_OR_REFLOG_REACHABLE" if commit in commits else "UNREACHABLE_COMMIT_OBJECT"
                ),
            }

    fsck_failure = fsck.returncode not in (0, 1)
    return {
        "scan_status": "PARTIAL_REQUIRES_REVIEW" if tree_errors or fsck_failure else "COMPLETED_CANDIDATE_SCAN",
        "repository_root": str(repo),
        "scanner_scope": {
            "refs_and_reflogs_scanned": True,
            "unreachable_commit_objects_scanned": True,
            "known_migration_stems": len(KNOWN_STEMS),
            "commits_scanned": scanned_commits,
            "reachable_commit_objects": len(commits),
            "unreachable_commit_objects": len(unreachable_commits),
            "candidate_versions_or_paths_found": len(candidates),
            "tree_or_blob_errors": len(tree_errors),
            "git_fsck_exit_code": fsck.returncode,
        },
        "candidates": sorted(candidates.values(), key=lambda item: (item["migration_stem"], item["migration_version"], item["commit_sha"])),
        "errors": tree_errors,
        "no_network_requests": True,
        "no_database_connections": True,
        "sql_content_emitted": False,
        "hosted_write_authorized": False,
        "interpretation": (
            "A matching local Git object is only a recovery candidate. Verify chain of custody, "
            "authoritative deployment identity, project identity and actual SQL digest independently. "
            "A scan with zero candidates does not prove that the SQL never existed."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path, help="Path to a local Git clone; no network access is performed.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path. The report contains file paths and hashes, not SQL text.")
    parser.add_argument("--max-commits", type=int, default=50000, help="Fail closed above this bound (default: 50000).")
    args = parser.parse_args()
    if args.max_commits < 1:
        parser.error("--max-commits must be positive")
    try:
        report = scan_repository(args.repo, args.max_commits)
    except ScanError as exc:
        print(json.dumps({
            "scan_status": "FAILED_CLOSED",
            "error": str(exc),
            "no_network_requests": True,
            "no_database_connections": True,
            "sql_content_emitted": False,
            "hosted_write_authorized": False,
        }, indent=2, ensure_ascii=False))
        return 2
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        target = args.output.expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "candidates"}, indent=2, ensure_ascii=False))
    print(f"candidate_rows={len(report['candidates'])}")
    return 0 if report["scan_status"] == "COMPLETED_CANDIDATE_SCAN" else 1


if __name__ == "__main__":
    sys.exit(main())

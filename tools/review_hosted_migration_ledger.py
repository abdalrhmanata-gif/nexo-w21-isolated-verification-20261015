#!/usr/bin/env python3
"""Offline reconciliation of query 11/12/13 evidence against local migrations.

Reads evidence JSON, migration filenames/content hashes, and local Git metadata.
No network client, SQL execution, migration repair, deployment, or hosted mutation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

PROJECT_REF = "mrwmmbytcymqgwvcoywd"
PROJECT_NAME = "ZAVQERA Development"
PROJECT_REGION = "eu-west-1"
QUERY_COUNT = 13
PACK_SHA256 = "a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284"
ACL_PROVENANCE_SHA256 = "f9f56944ddd04dd135329ff930cf5259e215eb89f30784b75e03a93f221ff38e"
MIGRATION = re.compile(r"^(?P<version>[0-9]+)_(?P<name>.+)\.sql$")
ROLES = ("anon", "authenticated", "service_role", "postgres")
PRIVILEGES = ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN")
WRITE_PRIVILEGES = {"INSERT", "UPDATE", "DELETE", "TRUNCATE"}


class EvidenceError(ValueError):
    pass


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"cannot read {path.name}: {exc}") from None


def rows_from(payload):
    candidates = [payload]
    if isinstance(payload, dict):
        candidates = [payload[key] for key in ("result", "data", "rows") if key in payload] + candidates
    for obj in candidates:
        if isinstance(obj, list) and all(isinstance(row, dict) for row in obj):
            return obj
        if isinstance(obj, dict) and isinstance(obj.get("rows"), list):
            columns = obj.get("columns")
            if isinstance(columns, list):
                names = [item if isinstance(item, str) else item.get("name") for item in columns]
                if names and all(isinstance(name, str) for name in names) and all(
                    isinstance(row, (list, tuple)) and len(row) == len(names) for row in obj["rows"]
                ):
                    return [dict(zip(names, row)) for row in obj["rows"]]
            if all(isinstance(row, dict) for row in obj["rows"]):
                return obj["rows"]
    raise EvidenceError("unrecognized response shape")


def truthy_db(value):
    return value is True or (isinstance(value, str) and value.strip().lower() in {"true", "t", "on", "1"})


def verify_evidence(directory):
    summary = read_json(directory / "summary.json")
    metadata = read_json(directory / "run_metadata.json")
    identity = read_json(directory / "project_identity.json")
    gate = read_json(directory / "read_only_role_gate.json").get("observed", {})
    if summary.get("status") != "CAPTURED_FOR_MANUAL_REVIEW" or summary.get("queries_completed") != QUERY_COUNT:
        raise EvidenceError("requires a completed 13-query CAPTURED_FOR_MANUAL_REVIEW run")
    if summary.get("query_pack_sha256") != PACK_SHA256:
        raise EvidenceError("query pack SHA-256 mismatch")
    if summary.get("acl_provenance_query_sha256") != ACL_PROVENANCE_SHA256:
        raise EvidenceError("ACL provenance query SHA-256 mismatch")
    if metadata.get("acl_provenance_query_sha256") != ACL_PROVENANCE_SHA256:
        raise EvidenceError("run metadata ACL provenance query SHA-256 mismatch")
    if summary.get("access_token_saved") is not False or metadata.get("token_saved") is not False:
        raise EvidenceError("token-safety metadata missing or unexpected")
    if metadata.get("project_ref") != PROJECT_REF:
        raise EvidenceError("evidence is not scoped to the pinned Development project")
    if (identity.get("id"), identity.get("name"), identity.get("region")) != (PROJECT_REF, PROJECT_NAME, PROJECT_REGION):
        raise EvidenceError("project identity/region mismatch")
    if gate.get("current_user") != "supabase_read_only_user" or not truthy_db(gate.get("transaction_read_only")):
        raise EvidenceError("read-only role gate absent or failed")
    if gate.get("migration_ledger_relation") != "supabase_migrations.schema_migrations":
        raise EvidenceError("expected migration ledger relation not verified")
    return summary, metadata, identity


def source_migrations(repo_root):
    directory = repo_root / "supabase" / "migrations"
    if not directory.is_dir():
        raise EvidenceError(f"migration directory not found: {directory}")
    rows = []
    seen = set()
    bad_names = []
    for path in sorted(directory.glob("*.sql")):
        match = MIGRATION.fullmatch(path.name)
        if not match:
            bad_names.append(path.name)
            continue
        version, name = match.group("version"), match.group("name")
        pair = (version, name)
        if pair in seen:
            raise EvidenceError(f"duplicate source tuple: {version} / {name}")
        seen.add(pair)
        rows.append({"version": version, "name": name, "file": path.name,
                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    if bad_names:
        raise EvidenceError("unrecognized migration filenames: " + ", ".join(bad_names))
    if not rows:
        raise EvidenceError("no checked-in migration files found")
    return rows


def source_provenance(repo_root, source_rows):
    """Return deterministic local source identities without network access.

    The migration manifest hashes sorted filename/file-SHA pairs, so it remains
    informative even when the checkout is dirty or Git metadata is unavailable.
    """
    manifest_text = "".join(
        f"{row['file']}\t{row['sha256']}\n"
        for row in sorted(source_rows, key=lambda row: row["file"])
    )
    manifest_sha256 = hashlib.sha256(manifest_text.encode("utf-8")).hexdigest()

    head = None
    worktree_clean = None
    try:
        head_result = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
            check=False,
        )
        candidate = head_result.stdout.strip()
        if head_result.returncode == 0 and re.fullmatch(r"[0-9a-fA-F]{40,64}", candidate):
            head = candidate.lower()
            status_result = subprocess.run(
                ["git", "status", "--porcelain=v1", "--untracked-files=all", "--", "supabase/migrations"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=5,
                check=False,
            )
            if status_result.returncode == 0:
                worktree_clean = not status_result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        # A source directory can intentionally be supplied without a .git checkout.
        # Do not fail the evidence analysis; retain the content manifest.
        pass

    return {
        "source_checkout_head_sha": head,
        "source_migration_manifest_sha256": manifest_sha256,
        "source_migrations_worktree_clean": worktree_clean,
    }


def reconcile(directory, repo_root):
    summary, metadata, identity = verify_evidence(directory)
    ledger = rows_from(read_json(directory / "query_11.json").get("response"))
    acl_rows = rows_from(read_json(directory / "query_12.json").get("response"))
    provenance_rows = rows_from(read_json(directory / "query_13.json").get("response"))
    if len(provenance_rows) != 1 or not isinstance(provenance_rows[0].get("w86_acl_provenance"), dict):
        raise EvidenceError("query 13 ACL provenance result is missing or malformed")
    provenance = provenance_rows[0]["w86_acl_provenance"]
    relation = provenance.get("relation")
    membership_paths = provenance.get("service_role_membership_paths")
    effective_privileges = provenance.get("service_role_effective_privileges")
    inherited_table = provenance.get("service_role_inherited_table_acl_entries")
    inherited_column = provenance.get("service_role_inherited_column_acl_entries")
    if (
        provenance.get("probe_name") != "w86_acl_provenance_v1"
        or provenance.get("current_user") != "supabase_read_only_user"
        or provenance.get("session_user") != "supabase_read_only_user"
        or not truthy_db(provenance.get("transaction_read_only"))
        or not isinstance(relation, dict) or relation.get("exists") is not True
        or not isinstance(membership_paths, list)
        or not all(
            isinstance(item, dict)
            and isinstance(item.get("all_edges_inherit"), bool)
            and isinstance(item.get("all_edges_set_role"), bool)
            for item in membership_paths
        )
        or not isinstance(effective_privileges, dict)
        or set(effective_privileges) != set(PRIVILEGES)
        or not isinstance(inherited_table, list)
        or not isinstance(inherited_column, list)
        or not all(
            isinstance(item, dict)
            and isinstance(item.get("grantee_role"), str)
            and isinstance(item.get("membership_depth"), int)
            and item.get("membership_depth", 0) > 0
            and isinstance(item.get("all_membership_edges_inherit"), bool)
            and isinstance(item.get("all_membership_edges_set_role"), bool)
            for item in inherited_table + inherited_column
        )
    ):
        raise EvidenceError("query 13 ACL provenance payload failed role/read-only/shape checks")
    if not ledger:
        raise EvidenceError("hosted migration ledger returned zero rows")
    hosted = []
    seen = set()
    for row in ledger:
        version, name = row.get("version"), row.get("name")
        if not isinstance(version, str) or not version or not isinstance(name, str) or not name:
            raise EvidenceError("ledger row missing string version/name")
        pair = (version, name)
        if pair in seen:
            raise EvidenceError(f"duplicate hosted tuple: {version} / {name}")
        seen.add(pair)
        hosted.append({"version": version, "name": name})
    hosted.sort(key=lambda row: (row["version"], row["name"]))

    source = source_migrations(repo_root)
    source_identity = source_provenance(repo_root, source)
    source_by_pair = {(row["version"], row["name"]): row for row in source}
    hosted_by_pair = {(row["version"], row["name"]): row for row in hosted}
    source_pairs, hosted_pairs = set(source_by_pair), set(hosted_by_pair)
    source_names = {row["name"] for row in source}
    hosted_names = {row["name"] for row in hosted}
    conflicts = []
    for name in sorted(source_names & hosted_names):
        lv = sorted({row["version"] for row in source if row["name"] == name})
        hv = sorted({row["version"] for row in hosted if row["name"] == name})
        if set(lv) != set(hv):
            conflicts.append({"name": name, "local_versions": lv, "hosted_versions": hv,
                              "classification": "NOT_PROOF_OF_EQUAL_SQL"})

    effective = [row for row in acl_rows if row.get("evidence_kind") == "EFFECTIVE_PRIVILEGE"]
    parent_acl_path_found = bool(inherited_table or inherited_column)
    w86_parent_acl_gate = (
        "BLOCKED_PARENT_ROLE_ACL" if parent_acl_path_found else "NO_PARENT_ROLE_ACL_OBSERVED"
    )
    hosted_write_blockers = [
        "Historical migration SQL provenance remains unresolved; version/name ledger comparison does not prove deployed SQL equality.",
        "An independent database-owner review and separate explicit authorization are required before any hosted mutation.",
    ]
    if parent_acl_path_found:
        hosted_write_blockers.insert(
            0,
            "W86 direct revokes cannot remove privileges reachable through a parent role; do not apply this candidate as-is.",
        )
    stored = [row for row in acl_rows if row.get("evidence_kind") == "STORED_ACL"]
    actual_matrix = {(row.get("grantee"), row.get("privilege_type")) for row in effective}
    expected_matrix = {(role, privilege) for role in ROLES for privilege in PRIVILEGES}
    if len(effective) != len(expected_matrix) or actual_matrix != expected_matrix:
        raise EvidenceError("effective table ACL matrix incomplete or unexpected")
    if any(row.get("schema_name") != "public" or row.get("relation_name") != "agent_executions" for row in effective):
        raise EvidenceError("effective ACL rows refer to an unexpected relation")

    effective_write = [
        {key: row.get(key) for key in ("grantee", "privilege_type", "effective_privilege", "owner_role",
                                       "row_level_security_enabled", "row_level_security_forced")}
        for row in effective
        if row.get("grantee") != row.get("owner_role")
        and row.get("privilege_type") in WRITE_PRIVILEGES
        and truthy_db(row.get("effective_privilege"))
    ]
    stored_write = [
        {key: row.get(key) for key in ("grantee", "privilege_type", "is_grantable", "grantor")}
        for row in stored if row.get("grantee") in {"PUBLIC", "anon", "authenticated", "service_role"}
        and row.get("privilege_type") in WRITE_PRIVILEGES
    ]
    return {
        "status": "REQUIRES_MANUAL_REVIEW",
        "release_decision": "NO-GO",
        "captured_at_utc": metadata.get("observed_at_utc"),
        "project": identity,
        "query_pack_sha256": summary["query_pack_sha256"],
        "acl_provenance_query_sha256": ACL_PROVENANCE_SHA256,
        "service_role_membership_paths": membership_paths,
        "service_role_effective_privileges": effective_privileges,
        "service_role_set_role_path_count": sum(
            1 for item in membership_paths
            if isinstance(item, dict) and item.get("depth", 0) > 0 and item.get("all_edges_set_role") is True
        ),
        "service_role_inherited_table_acl_rows": len(inherited_table),
        "service_role_inherited_column_acl_rows": len(inherited_column),
        "service_role_parent_role_acl_path_semantics": "entries reachable through INHERIT or SET ROLE",
        "w86_candidate_parent_acl_gate": w86_parent_acl_gate,
        "hosted_write_authorized": False,
        "hosted_write_authorization_status": "NOT_AUTHORIZED_BY_OFFLINE_REVIEWER",
        "hosted_write_blockers": hosted_write_blockers,
        "service_role_inherited_table_acl_entries": inherited_table,
        "service_role_inherited_column_acl_entries": inherited_column,
        "source_checkout_head_sha": source_identity["source_checkout_head_sha"],
        "source_migration_manifest_sha256": source_identity["source_migration_manifest_sha256"],
        "source_migrations_worktree_clean": source_identity["source_migrations_worktree_clean"],
        "source_migration_count": len(source),
        "hosted_ledger_row_count": len(hosted),
        "exact_version_name_matches": len(source_pairs & hosted_pairs),
        "same_name_different_version": conflicts,
        "source_tuples_missing_from_hosted_ledger": [source_by_pair[p] for p in sorted(source_pairs - hosted_pairs)],
        "hosted_tuples_missing_from_source": [hosted_by_pair[p] for p in sorted(hosted_pairs - source_pairs)],
        "source_names_absent_from_hosted_ledger": sorted(source_names - hosted_names),
        "hosted_names_absent_from_source": sorted(hosted_names - source_names),
        "effective_table_privilege_rows": len(effective),
        "stored_table_acl_rows": len(stored),
        "effective_nonowner_write_grants": effective_write,
        "stored_nonowner_write_acl_rows": stored_write,
        "interpretation": [
            "Same-name/different-version is not proof that deployed SQL matches checked-in SQL.",
            "The migration ledger records version/name metadata, not historical SQL bytes.",
            "The source migration manifest SHA-256 covers sorted filename/file-SHA pairs and identifies migration contents even if Git metadata is unavailable.",
            "The source checkout HEAD and dirty flag are local Git metadata; the manifest is required to identify the actual source bytes.",
            "Direct table/column revokes do not remove privileges inherited from parent roles; any inherited ACL row is a blocker for the current W86 candidate and requires owner-reviewed resolution.",
            "Effective ACLs are a signal, not complete proof of reachability; review RLS, memberships, function ownership and trusted writers separately.",
            "The observed role has rolbypassrls=true; do not use this evidence credential for application-row reads.",
            "This is offline analysis only; it performs no SQL, hosted writes, migration repair, or deployment.",
        ],
    }


def render_markdown(result):
    lines = [
        "# ZAVQERA — Offline Hosted Migration Ledger and W66 ACL Review",
        "",
        "Disposition: **REVIEW REQUIRED / RELEASE NO-GO**. This report compares query 11/12 evidence with source filenames and hashes; it does not approve migrations or certify security.",
        "",
        f"- Captured UTC: {result['captured_at_utc']}",
        f"- Project: {result['project'].get('name')} ({result['project'].get('id')}), region {result['project'].get('region')}",
        f"- Source checkout HEAD: `{result['source_checkout_head_sha'] or 'UNAVAILABLE'}`",
        f"- Source migration manifest SHA-256: `{result['source_migration_manifest_sha256']}`",
        f"- Migration files clean in Git worktree: **{result['source_migrations_worktree_clean'] if result['source_migrations_worktree_clean'] is not None else 'UNKNOWN'}**",
        f"- Source files: **{result['source_migration_count']}**; hosted ledger rows: **{result['hosted_ledger_row_count']}**",
        f"- Exact version/name matches: **{result['exact_version_name_matches']}**",
        f"- Same-name/different-version candidates: **{len(result['same_name_different_version'])}**",
        f"- Effective ACL rows on public.agent_executions: **{result['effective_table_privilege_rows']}**",
        f"- service_role inherited table ACL rows: **{result['service_role_inherited_table_acl_rows']}**",
        f"- service_role inherited column ACL rows: **{result['service_role_inherited_column_acl_rows']}**",
        f"- W86 parent-role ACL gate: **{result['w86_candidate_parent_acl_gate']}**",
        f"- Hosted write authorized: **{result['hosted_write_authorized']}** (the offline reviewer never authorizes hosted writes)",
        f"- Stored ACL rows: **{result['stored_table_acl_rows']}**",
        "",
        "## Same-name/different-version candidates",
        "",
    ]
    for row in result["same_name_different_version"]:
        lines.append(f"- {row['name']}: source={','.join(row['local_versions'])}; hosted={','.join(row['hosted_versions'])}")
    if not result["same_name_different_version"]:
        lines.append("None detected.")
    lines.extend(["", "## W86 candidate preflight — not deployment authorization", ""])
    lines.extend([f"- {item}" for item in result["hosted_write_blockers"]])
    lines.extend(["", "This preflight is only a safety signal. Even when no parent-role ACL is observed, hosted writes remain unauthorized until historical migration provenance and owner approval are resolved.", ""])
    lines.extend(["", "## Hosted names absent from source", ""])
    lines.extend([f"- {name}" for name in result["hosted_names_absent_from_source"]] or ["None."])
    lines.extend(["", "## Effective non-owner write grants", ""])
    lines.extend([f"- {row['grantee']} {row['privilege_type']} effective={row['effective_privilege']}; owner={row['owner_role']}; RLS enabled={row['row_level_security_enabled']}; forced={row['row_level_security_forced']}" for row in result["effective_nonowner_write_grants"]] or ["None in the selected matrix; this is not a full authorization proof."])
    lines.extend(["", "## Stored non-owner write ACL entries", ""])
    lines.extend([f"- {row['grantee']} {row['privilege_type']} grantable={row['is_grantable']} grantor={row['grantor']}" for row in result["stored_nonowner_write_acl_rows"]] or ["None."])
    lines.extend(["", "## Source tuples absent from hosted ledger", ""])
    lines.extend([f"- {row['version']} {row['name']} (file SHA-256 {row['sha256']})" for row in result["source_tuples_missing_from_hosted_ledger"]] or ["None."])
    lines.extend(["", "## Hosted tuples absent from source", ""])
    lines.extend([f"- {row['version']} {row['name']}" for row in result["hosted_tuples_missing_from_source"]] or ["None."])
    lines.extend(["", "## Interpretation limits", ""])
    lines.extend([f"- {item}" for item in result["interpretation"]])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, required=True, help="13-query audit output folder")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1], help="checkout containing supabase/migrations")
    args = parser.parse_args(argv)
    try:
        result = reconcile(args.evidence_dir.resolve(), args.repo_root.resolve())
    except EvidenceError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    out_json = args.evidence_dir.resolve() / "ledger_acl_review.json"
    out_md = args.evidence_dir.resolve() / "ledger_acl_review.md"
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({
        "status": result["status"], "release_decision": result["release_decision"],
        "source_migration_count": result["source_migration_count"],
        "hosted_ledger_row_count": result["hosted_ledger_row_count"],
        "exact_version_name_matches": result["exact_version_name_matches"],
        "same_name_different_version_count": len(result["same_name_different_version"]),
        "source_tuples_missing_from_hosted_ledger": len(result["source_tuples_missing_from_hosted_ledger"]),
        "hosted_tuples_missing_from_source": len(result["hosted_tuples_missing_from_source"]),
        "source_checkout_head_sha": result["source_checkout_head_sha"],
        "source_migration_manifest_sha256": result["source_migration_manifest_sha256"],
        "source_migrations_worktree_clean": result["source_migrations_worktree_clean"],
        "effective_nonowner_write_grants": len(result["effective_nonowner_write_grants"]),
        "w86_candidate_parent_acl_gate": result["w86_candidate_parent_acl_gate"],
        "hosted_write_authorized": result["hosted_write_authorized"],
        "hosted_write_blocker_count": len(result["hosted_write_blockers"]),
        "output_json": str(out_json), "output_markdown": str(out_md),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

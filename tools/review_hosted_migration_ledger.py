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


def membership_paths_form_valid_chain(paths):
    """Reject broken, duplicate, or impossible recursive role-membership paths."""
    if not isinstance(paths, list) or not paths:
        return False
    roots = []
    for item in paths:
        if not isinstance(item, dict):
            return False
        name, depth = item.get("role_name"), item.get("depth")
        member = item.get("member_of_role")
        inherits, can_set = item.get("all_edges_inherit"), item.get("all_edges_set_role")
        if not isinstance(name, str) or not name or type(depth) is not int or depth < 0:
            return False
        if type(inherits) is not bool or type(can_set) is not bool:
            return False
        if "member_of_role" not in item:
            return False
        if depth == 0:
            roots.append(item)
            if name != "service_role" or member is not None or inherits is not True or can_set is not True:
                return False
        elif not isinstance(member, str) or not member:
            return False
    if len(roots) != 1:
        return False
    for item in paths:
        if item["depth"] == 0:
            continue
        if not any(
            parent["role_name"] == item["member_of_role"]
            and parent["depth"] == item["depth"] - 1
            and (not item["all_edges_inherit"] or parent["all_edges_inherit"])
            and (not item["all_edges_set_role"] or parent["all_edges_set_role"])
            for parent in paths
        ):
            return False
    return True

def truthy_db(value):
    return value is True or (isinstance(value, str) and value.strip().lower() in {"true", "t", "on", "1"})


def acl_entries_have_valid_shape(entries, *, inherited=False, column=False):
    """Validate explicit ACL projection fields before interpreting provenance."""
    if not isinstance(entries, list):
        return False
    grantee_key = "grantee_role" if inherited else "grantee"
    for item in entries:
        if not isinstance(item, dict):
            return False
        grantee = item.get(grantee_key)
        if not isinstance(grantee, str) or not grantee:
            return False
        if item.get("privilege_type") not in PRIVILEGES:
            return False
        if type(item.get("is_grantable")) is not bool:
            return False
        grantor = item.get("grantor")
        if not isinstance(grantor, str) or not grantor:
            return False
        if column:
            column_name = item.get("column_name")
            if not isinstance(column_name, str) or not column_name:
                return False
        if inherited:
            if type(item.get("membership_depth")) is not int or item["membership_depth"] <= 0:
                return False
            if type(item.get("all_membership_edges_inherit")) is not bool:
                return False
            if type(item.get("all_membership_edges_set_role")) is not bool:
                return False
    return True


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
    owner_role = relation.get("owner_role") if isinstance(relation, dict) else None
    membership_paths = provenance.get("service_role_membership_paths")
    effective_privileges = provenance.get("service_role_effective_privileges")
    table_acl = provenance.get("table_acl_entries")
    column_acl = provenance.get("column_acl_entries")
    inherited_table = provenance.get("service_role_inherited_table_acl_entries")
    inherited_column = provenance.get("service_role_inherited_column_acl_entries")
    if (
        provenance.get("probe_name") != "w86_acl_provenance_v1"
        or provenance.get("current_user") != "supabase_read_only_user"
        or provenance.get("session_user") != "supabase_read_only_user"
        or not truthy_db(provenance.get("transaction_read_only"))
        or not isinstance(relation, dict) or relation.get("exists") is not True
        or relation.get("schema_name") != "public"
        or relation.get("relation_name") != "agent_executions"
        or not isinstance(owner_role, str) or not owner_role
        or type(relation.get("row_level_security_enabled")) is not bool
        or type(relation.get("row_level_security_forced")) is not bool
        or type(relation.get("stored_acl_is_null")) is not bool
        or not isinstance(membership_paths, list)
        or not membership_paths_form_valid_chain(membership_paths)
        or not any(
            isinstance(item, dict)
            and item.get("role_name") == "service_role"
            and type(item.get("depth")) is int
            and item.get("depth") == 0
            for item in membership_paths
        )
        or not all(
            isinstance(item, dict)
            and isinstance(item.get("role_name"), str)
            and bool(item.get("role_name"))
            and type(item.get("depth")) is int
            and item.get("depth", -1) >= 0
            and isinstance(item.get("all_edges_inherit"), bool)
            and isinstance(item.get("all_edges_set_role"), bool)
            for item in membership_paths
        )
        or not isinstance(effective_privileges, dict)
        or set(effective_privileges) != set(PRIVILEGES)
        or not all(type(value) is bool for value in effective_privileges.values())
        or not acl_entries_have_valid_shape(table_acl, inherited=False, column=False)
        or not acl_entries_have_valid_shape(column_acl, inherited=False, column=True)
        or not acl_entries_have_valid_shape(inherited_table, inherited=True, column=False)
        or not acl_entries_have_valid_shape(inherited_column, inherited=True, column=True)
        or not isinstance(inherited_table, list)
        or not isinstance(inherited_column, list)
        or not all(
            isinstance(item, dict)
            and isinstance(item.get("grantee_role"), str)
            and type(item.get("membership_depth")) is int
            and item.get("membership_depth", 0) > 0
            and isinstance(item.get("all_membership_edges_inherit"), bool)
            and isinstance(item.get("all_membership_edges_set_role"), bool)
            for item in inherited_table + inherited_column
        )
    ):
        raise EvidenceError("query 13 ACL provenance payload failed role/read-only/shape checks")
    membership_keys = {
        (item["role_name"], item["depth"], item["all_edges_inherit"], item["all_edges_set_role"])
        for item in membership_paths
    }
    inherited_entries = inherited_table + inherited_column
    if any(
        (item["grantee_role"], item["membership_depth"],
         item["all_membership_edges_inherit"], item["all_membership_edges_set_role"])
        not in membership_keys
        or not (item["all_membership_edges_inherit"] or item["all_membership_edges_set_role"])
        for item in inherited_entries
    ):
        raise EvidenceError("inherited ACL entry does not match a reachable membership path")
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
    authenticated_parent_paths = [
        item for item in membership_paths
        if item.get("role_name") == "authenticated"
        and item.get("depth", 0) > 0
        and (item.get("all_edges_inherit") is True or item.get("all_edges_set_role") is True)
    ]
    authenticated_grant_path_found = bool(authenticated_parent_paths)
    relation_owner_paths = [
        item for item in membership_paths
        if item.get("role_name") == owner_role
        and (
            item.get("depth", 0) == 0
            or (item.get("depth", 0) > 0 and (item.get("all_edges_inherit") is True or item.get("all_edges_set_role") is True))
        )
    ]
    relation_owner_path_found = bool(relation_owner_paths)
    w86_parent_acl_gate = (
        "BLOCKED_RELATION_OWNER_PATH" if relation_owner_path_found
        else "BLOCKED_PARENT_ROLE_ACL" if parent_acl_path_found
        else "BLOCKED_AUTHENTICATED_ROLE_PATH" if authenticated_grant_path_found
        else "NO_PARENT_ROLE_ACL_OBSERVED"
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
    if relation_owner_path_found:
        hosted_write_blockers.insert(
            0,
            "service_role is the relation owner, inherits owner authority, or can SET ROLE to the owner of public.agent_executions; owner authority can restore ACLs and is not safely handled by direct table/column revokes. Do not apply W86 as-is.",
        )
    if authenticated_grant_path_found:
        hosted_write_blockers.insert(
            0,
            "service_role can reach authenticated through INHERIT or SET ROLE, and W86 grants SELECT to authenticated; do not apply this candidate as-is even if query 13 shows no current parent-role ACL entry.",
        )
    stored = [row for row in acl_rows if row.get("evidence_kind") == "STORED_ACL"]
    actual_matrix = {(row.get("grantee"), row.get("privilege_type")) for row in effective}
    expected_matrix = {(role, privilege) for role in ROLES for privilege in PRIVILEGES}
    if len(effective) != len(expected_matrix) or actual_matrix != expected_matrix:
        raise EvidenceError("effective table ACL matrix incomplete, duplicated or unexpected")
    if len(acl_rows) != len(effective) + len(stored):
        raise EvidenceError("ACL evidence contains an unrecognized row kind")
    if any(
        row.get("schema_name") != "public"
        or row.get("relation_name") != "agent_executions"
        or not isinstance(row.get("owner_role"), str) or not row.get("owner_role")
        or type(row.get("row_level_security_enabled")) is not bool
        or type(row.get("row_level_security_forced")) is not bool
        for row in acl_rows
    ):
        raise EvidenceError("ACL rows have malformed relation-owner or RLS metadata")
    if any(
        type(row.get("effective_privilege")) is not bool
        or row.get("is_grantable") is not None
        or row.get("grantor") is not None
        for row in effective
    ):
        raise EvidenceError("effective ACL row has malformed boolean or privilege-source fields")
    if any(
        not isinstance(row.get("grantee"), str) or not row.get("grantee")
        or row.get("privilege_type") not in PRIVILEGES
        or row.get("effective_privilege") is not None
        or type(row.get("is_grantable")) is not bool
        or not isinstance(row.get("grantor"), str) or not row.get("grantor")
        for row in stored
    ):
        raise EvidenceError("stored ACL row has malformed grantee, privilege, grantor or grantability fields")
    query12_metadata = {
        (
            row.get("schema_name"), row.get("relation_name"), row.get("owner_role"),
            row.get("row_level_security_enabled"), row.get("row_level_security_forced"),
        )
        for row in acl_rows
    }
    expected_relation_metadata = (
        relation["schema_name"], relation["relation_name"], owner_role,
        relation["row_level_security_enabled"], relation["row_level_security_forced"],
    )
    if query12_metadata != {expected_relation_metadata}:
        raise EvidenceError("query 12 and query 13 relation identity/RLS metadata disagree")
    query12_service_role_effective = {
        row["privilege_type"]: row["effective_privilege"]
        for row in effective
        if row["grantee"] == "service_role"
    }
    if query12_service_role_effective != effective_privileges:
        raise EvidenceError("query 12 and query 13 service_role effective privilege maps disagree")

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
        "service_role_authenticated_parent_path_count": len(authenticated_parent_paths),
        "relation_owner_role": owner_role,
        "service_role_relation_owner_path_count": len(relation_owner_paths),
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
            "W86 grants SELECT to authenticated after its preflight; any reachable INHERIT/SET ROLE path from service_role to authenticated is independently a blocker, even if that role has no ACL entry in the current capture.",
            "A service_role membership path to the relation owner with INHERIT or SET ROLE enabled, or service_role itself as relation owner, is a separate blocker because ownership authority can restore ACLs even when owner ACL rows are absent.",
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
        f"- service_role reachable authenticated parent paths: **{result['service_role_authenticated_parent_path_count']}**",
        f"- Relation owner role: **{result['relation_owner_role']}**; service_role owner-role paths: **{result['service_role_relation_owner_path_count']}**",
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

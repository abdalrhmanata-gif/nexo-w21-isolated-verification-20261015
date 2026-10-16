#!/usr/bin/env python3
"""Run the pinned ZAVQERA hosted migration-effect audit with SELECT-only SQL.

This supplemental pack gathers metadata not covered by the first eight-query audit.
It never uses the generic Supabase SQL endpoint, never stores/prints the access token,
and stops before query 2 unless project and effective read-only role gates pass.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

API = "https://api.supabase.com"
EXPECTED_PROJECT = "ZAVQERA Development"
EXPECTED_REGION = "eu-west-1"
READ_ONLY_ROLE = "supabase_read_only_user"
PACK_SHA256 = "a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284"
PACK_RELATIVE = Path("supabase/tests/hosted_readonly_migration_effect_audit_queries.sql")
ACL_PROVENANCE_SHA256 = "f9f56944ddd04dd135329ff930cf5259e215eb89f30784b75e03a93f221ff38e"
ACL_PROVENANCE_RELATIVE = Path("supabase/tests/hosted_readonly_w86_acl_provenance_query.sql")
OUTPUT_RELATIVE = Path("zavqera-readonly-effect-audit-output")
REF_RE = re.compile(r"^[a-z0-9]{20}$")


def split_statements(sql: str) -> list[str]:
    """Split SQL on semicolons outside quotes, dollar quotes, and nested comments."""
    out, buf = [], []
    i, state, dollar, depth = 0, "normal", "", 0
    while i < len(sql):
        ch = sql[i]
        nxt = sql[i + 1] if i + 1 < len(sql) else ""
        if state == "line":
            if ch == "\n":
                state = "normal"
                buf.append("\n")
            i += 1
            continue
        if state == "block":
            if ch == "/" and nxt == "*":
                depth += 1
                i += 2
                continue
            if ch == "*" and nxt == "/":
                depth -= 1
                i += 2
                if depth == 0:
                    state = "normal"
                continue
            i += 1
            continue
        if state == "single":
            buf.append(ch)
            if ch == "'":
                if nxt == "'":
                    buf.append(nxt)
                    i += 2
                    continue
                state = "normal"
            i += 1
            continue
        if state == "double":
            buf.append(ch)
            if ch == '"':
                if nxt == '"':
                    buf.append(nxt)
                    i += 2
                    continue
                state = "normal"
            i += 1
            continue
        if state == "dollar":
            if sql.startswith(dollar, i):
                buf.append(dollar)
                i += len(dollar)
                state = "normal"
            else:
                buf.append(ch)
                i += 1
            continue
        if ch == "-" and nxt == "-":
            state = "line"
            i += 2
            continue
        if ch == "/" and nxt == "*":
            state, depth = "block", 1
            i += 2
            continue
        if ch == "'":
            state = "single"
            buf.append(ch)
            i += 1
            continue
        if ch == '"':
            state = "double"
            buf.append(ch)
            i += 1
            continue
        if ch == "$":
            match = re.match(r"\$[A-Za-z_][A-Za-z0-9_]*\$|\$\$", sql[i:])
            if match:
                dollar = match.group(0)
                buf.append(dollar)
                i += len(dollar)
                state = "dollar"
                continue
        if ch == ";":
            part = "".join(buf).strip()
            if part:
                out.append(part)
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    if state in {"single", "double", "block", "dollar"}:
        raise ValueError(f"Unterminated SQL construct: {state}")
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return out


def no_comments(sql: str) -> str:
    """Strip SQL comments for the leading SELECT-only guard."""
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    return re.sub(r"--[^\n]*", "", sql)


def load_pack(root: Path) -> tuple[list[str], str]:
    path = root / PACK_RELATIVE
    raw = path.read_bytes().replace(b"\r\n", b"\n")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != PACK_SHA256:
        raise ValueError(f"approved query-pack hash mismatch ({digest}); stop for review")
    statements = split_statements(raw.decode("utf-8"))
    if len(statements) != 12:
        raise ValueError(f"expected exactly 12 base audit queries, found {len(statements)}")

    provenance_path = root / ACL_PROVENANCE_RELATIVE
    provenance_raw = provenance_path.read_bytes().replace(b"\r\n", b"\n")
    provenance_digest = hashlib.sha256(provenance_raw).hexdigest()
    if provenance_digest != ACL_PROVENANCE_SHA256:
        raise ValueError(f"approved ACL provenance query hash mismatch ({provenance_digest}); stop for review")
    provenance_statements = split_statements(provenance_raw.decode("utf-8"))
    if len(provenance_statements) != 1:
        raise ValueError(f"expected exactly 1 ACL provenance query, found {len(provenance_statements)}")
    statements.extend(provenance_statements)
    if len(statements) != 13:
        raise ValueError(f"expected exactly 13 total audit queries, found {len(statements)}")
    for number, statement in enumerate(statements, 1):
        if not re.match(r"(?is)^\s*SELECT\b", no_comments(statement).strip()):
            raise ValueError(f"query {number} is not a SELECT; refusing to run")
    return statements, digest


def request_json(token: str, method: str, path: str, body: dict | None = None):
    if not path.startswith("/v1/projects/"):
        raise ValueError("refusing request outside selected project's API path")
    if method == "POST" and not path.endswith("/database/query/read-only"):
        raise ValueError("refusing SQL request outside the explicit read-only endpoint")
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "ZAVQERA-read-only-effect-audit/1.0",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = response.read()
            status = response.status
    except HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"Supabase API HTTP {exc.code}: {message}") from None
    except URLError as exc:
        raise RuntimeError(f"Supabase API connection error: {exc.reason}") from None
    if not 200 <= status < 300:
        raise RuntimeError(f"Supabase API returned HTTP {status}")
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeError("Supabase API returned a non-JSON response") from None


def rows_from(payload):
    """Accept documented/common row shapes; unknown shapes fail closed."""
    candidates = [payload]
    if isinstance(payload, dict):
        for key in ("result", "data", "rows"):
            if key in payload:
                candidates.insert(0, payload[key])
    for obj in candidates:
        if isinstance(obj, list) and all(isinstance(row, dict) for row in obj):
            return obj
        if isinstance(obj, dict) and isinstance(obj.get("rows"), list):
            columns = obj.get("columns")
            if isinstance(columns, list):
                names = [value if isinstance(value, str) else value.get("name") for value in columns]
                if names and all(isinstance(name, str) for name in names):
                    if all(isinstance(row, (list, tuple)) and len(row) == len(names) for row in obj["rows"]):
                        return [dict(zip(names, row)) for row in obj["rows"]]
            if all(isinstance(row, dict) for row in obj["rows"]):
                return obj["rows"]
    return None


def as_bool(value) -> bool | None:
    if value is True or (isinstance(value, str) and value.strip().lower() in {"true", "t", "on", "1"}):
        return True
    if value is False or (isinstance(value, str) and value.strip().lower() in {"false", "f", "off", "0"}):
        return False
    return None


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if "--self-test" in sys.argv:
        root = Path(__file__).resolve().parents[1]
        sample = "-- ;\nSELECT 'a;b' AS x; /* nested ; /* still ; */ end */ SELECT $$c;d$$ AS y;"
        queries, digest = load_pack(root)
        if len(split_statements(sample)) != 2:
            raise AssertionError("SQL splitter self-test failed")
        print(f"SELF_TEST=PASS; queries={len(queries)}; base_sha256={digest}; acl_provenance_sha256={ACL_PROVENANCE_SHA256}; no network requests")
        return 0

    ref = os.getenv("SUPABASE_PROJECT_REF", "").strip()
    token = os.getenv("SUPABASE_ACCESS_TOKEN", "").strip()
    if not REF_RE.fullmatch(ref):
        print("BLOCKED: set SUPABASE_PROJECT_REF to the verified 20-character Development ref.", file=sys.stderr)
        return 2
    if not token:
        print("BLOCKED: SUPABASE_ACCESS_TOKEN missing; never paste a token into chat or commit it.", file=sys.stderr)
        return 2
    if os.getenv("ZAVQERA_AUDIT_CONFIRMATION") != "DEVELOPMENT_ONLY_READ_ONLY":
        print("BLOCKED: explicit Development + read-only confirmation is required.", file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parents[1]
    try:
        queries, pack_hash = load_pack(root)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"BLOCKED: query-pack validation failed: {exc}", file=sys.stderr)
        return 2

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = root / OUTPUT_RELATIVE / stamp
    out.mkdir(parents=True, exist_ok=False)
    observed_at = dt.datetime.now(dt.timezone.utc).isoformat()
    write_json(out / "run_metadata.json", {
        "observed_at_utc": observed_at,
        "project_ref": ref,
        "expected_project": EXPECTED_PROJECT,
        "expected_region": EXPECTED_REGION,
        "endpoint": "Supabase Management API /database/query/read-only (Beta)",
        "query_pack_sha256": pack_hash,
        "acl_provenance_query_sha256": ACL_PROVENANCE_SHA256,
        "query_count": len(queries),
        "token_saved": False,
        "scope": "catalog/migration-effect metadata, migration ledger, public.agent_executions ACL, and service_role inherited-role ACL provenance; no application rows",
    })

    def stop(stage: str, reason: str, code: int, completed: int) -> int:
        write_json(out / "stop.json", {
            "stage": stage, "reason": reason, "completed_queries": completed,
            "access_token_saved": False,
        })
        print(f"BLOCKED at {stage}: {reason}\nEvidence: {out}", file=sys.stderr)
        return code

    try:
        project = request_json(token, "GET", f"/v1/projects/{quote(ref, safe='')}")
        if not isinstance(project, dict) or not isinstance(project.get("name"), str):
            return stop("project_identity", "unrecognized project metadata; no SQL sent", 3, 0)
        identity = {key: project.get(key) for key in ("id", "name", "region", "status")}
        write_json(out / "project_identity.json", identity)
        if project.get("name") != EXPECTED_PROJECT or project.get("region") != EXPECTED_REGION:
            return stop("project_identity", "project name/region mismatch; no SQL sent", 3, 0)
        if project.get("id") is not None and str(project["id"]) != ref:
            return stop("project_identity", "returned project id mismatch; no SQL sent", 3, 0)
        if project.get("status") and str(project["status"]).upper() not in {"ACTIVE_HEALTHY", "ACTIVE"}:
            return stop("project_identity", "project is not active/healthy; no SQL sent", 3, 0)
    except Exception as exc:
        return stop("project_identity", str(exc), 3, 0)

    for index, query in enumerate(queries, 1):
        try:
            payload = request_json(
                token, "POST",
                f"/v1/projects/{quote(ref, safe='')}/database/query/read-only",
                {"query": query},
            )
        except Exception as exc:
            return stop(f"query_{index:02d}", str(exc), 4, index - 1)
        write_json(out / f"query_{index:02d}.json", {"query": query, "response": payload})
        if isinstance(payload, dict) and payload.get("error"):
            return stop(f"query_{index:02d}", "API response contains an error", 4, index)
        rows = rows_from(payload)
        if rows is None:
            return stop(f"query_{index:02d}", "unknown response shape; fail closed", 5, index)
        if index == 1:
            if len(rows) != 1:
                return stop("read_only_role_gate", "Query 1 must return exactly one row", 5, index)
            row = rows[0]
            gate = {
                "correct_effective_role": row.get("current_user") == READ_ONLY_ROLE,
                "transaction_read_only": as_bool(row.get("transaction_read_only")) is True,
                "not_superuser": as_bool(row.get("rolsuper")) is False,
                "cannot_create_database": as_bool(row.get("rolcreatedb")) is False,
                "cannot_create_roles": as_bool(row.get("rolcreaterole")) is False,
                "migration_ledger_visible": bool(row.get("migration_ledger_relation")),
            }
            write_json(out / "read_only_role_gate.json", {
                "checks": gate,
                "observed": {key: row.get(key) for key in (
                    "current_user", "session_user", "server_version_num", "transaction_read_only",
                    "rolsuper", "rolcreatedb", "rolcreaterole", "rolbypassrls",
                    "migration_ledger_relation",
                )},
            })
            if not all(gate.values()):
                return stop("read_only_role_gate", "role, read-only transaction, or ledger gate failed", 5, index)
        elif index == 11:
            if not rows:
                return stop("migration_ledger", "ledger query returned zero rows; do not infer an empty ledger", 5, index)
            if any(not isinstance(row.get("version"), str) or not row["version"]
                   or not isinstance(row.get("name"), str) or not row["name"] for row in rows):
                return stop("migration_ledger", "ledger response lacks nonempty version/name strings", 5, index)
        elif index == 12:
            effective = [row for row in rows if row.get("evidence_kind") == "EFFECTIVE_PRIVILEGE"]
            stored = [row for row in rows if row.get("evidence_kind") == "STORED_ACL"]
            actual = {(row.get("grantee"), row.get("privilege_type")) for row in effective}
            roles = ("anon", "authenticated", "service_role", "postgres")
            privileges = ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN")
            expected = {(role, privilege) for role in roles for privilege in privileges}
            base_shape_ok = all(
                row.get("schema_name") == "public"
                and row.get("relation_name") == "agent_executions"
                and isinstance(row.get("owner_role"), str) and bool(row.get("owner_role"))
                and type(row.get("row_level_security_enabled")) is bool
                and type(row.get("row_level_security_forced")) is bool
                for row in rows
            )
            effective_shape_ok = all(
                type(row.get("effective_privilege")) is bool
                and row.get("is_grantable") is None
                and row.get("grantor") is None
                for row in effective
            )
            stored_shape_ok = all(
                isinstance(row.get("grantee"), str) and bool(row.get("grantee"))
                and row.get("privilege_type") in privileges
                and row.get("effective_privilege") is None
                and type(row.get("is_grantable")) is bool
                and isinstance(row.get("grantor"), str) and bool(row.get("grantor"))
                for row in stored
            )
            if (
                len(effective) != len(expected)
                or actual != expected
                or len(rows) != len(effective) + len(stored)
                or not base_shape_ok
                or not effective_shape_ok
                or not stored_shape_ok
            ):
                return stop("w66_table_acl", "effective/stored ACL result set incomplete, duplicated, or malformed", 5, index)
        elif index == 13:
            if len(rows) != 1 or not isinstance(rows[0].get("w86_acl_provenance"), dict):
                return stop("w86_acl_provenance", "expected one structured ACL provenance result", 5, index)
            provenance = rows[0]["w86_acl_provenance"]
            relation = provenance.get("relation")
            memberships = provenance.get("service_role_membership_paths")
            effective = provenance.get("service_role_effective_privileges")
            inherited_table = provenance.get("service_role_inherited_table_acl_entries")
            inherited_column = provenance.get("service_role_inherited_column_acl_entries")
            if (
                provenance.get("probe_name") != "w86_acl_provenance_v1"
                or provenance.get("current_user") != READ_ONLY_ROLE
                or provenance.get("session_user") != READ_ONLY_ROLE
                or as_bool(provenance.get("transaction_read_only")) is not True
                or not isinstance(relation, dict) or relation.get("exists") is not True
                or relation.get("schema_name") != "public"
                or relation.get("relation_name") != "agent_executions"
                or not isinstance(relation.get("owner_role"), str) or not relation.get("owner_role")
                or type(relation.get("row_level_security_enabled")) is not bool
                or type(relation.get("row_level_security_forced")) is not bool
                or type(relation.get("stored_acl_is_null")) is not bool
                or not isinstance(memberships, list)
                or not any(item.get("role_name") == "service_role" and item.get("depth") == 0 for item in memberships if isinstance(item, dict))
                or not all(
                    isinstance(item, dict)
                    and isinstance(item.get("role_name"), str)
                    and bool(item.get("role_name"))
                    and type(item.get("depth")) is int
                    and item.get("depth", -1) >= 0
                    and isinstance(item.get("all_edges_inherit"), bool)
                    and isinstance(item.get("all_edges_set_role"), bool)
                    for item in memberships
                )
                or not isinstance(effective, dict)
                or set(effective) != {"SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN"}
                or not all(type(value) is bool for value in effective.values())
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
                return stop("w86_acl_provenance", "role gate or inherited ACL provenance result incomplete/unrecognized", 5, index)
            membership_keys = {
                (item["role_name"], item["depth"], item["all_edges_inherit"], item["all_edges_set_role"])
                for item in memberships
            }
            inherited_entries = inherited_table + inherited_column
            if any(
                (item["grantee_role"], item["membership_depth"],
                 item["all_membership_edges_inherit"], item["all_membership_edges_set_role"])
                not in membership_keys
                or not (item["all_membership_edges_inherit"] or item["all_membership_edges_set_role"])
                for item in inherited_entries
            ):
                return stop("w86_acl_provenance", "inherited ACL entry does not match a reachable membership path", 5, index)

    ledger_rows = rows_from(json.loads((out / "query_11.json").read_text(encoding="utf-8"))["response"])
    acl_rows = rows_from(json.loads((out / "query_12.json").read_text(encoding="utf-8"))["response"])
    provenance_rows = rows_from(json.loads((out / "query_13.json").read_text(encoding="utf-8"))["response"])
    provenance = provenance_rows[0]["w86_acl_provenance"]
    relation = provenance["relation"]
    query12_metadata = {
        (
            row.get("schema_name"), row.get("relation_name"), row.get("owner_role"),
            row.get("row_level_security_enabled"), row.get("row_level_security_forced"),
        )
        for row in acl_rows
    }
    expected_relation_metadata = (
        relation["schema_name"], relation["relation_name"], relation["owner_role"],
        relation["row_level_security_enabled"], relation["row_level_security_forced"],
    )
    if query12_metadata != {expected_relation_metadata}:
        return stop(
            "w66_w86_relation_metadata",
            "query 12 and query 13 relation identity/RLS metadata disagree",
            5,
            len(queries),
        )
    effective_acl_rows = [row for row in acl_rows if row.get("evidence_kind") == "EFFECTIVE_PRIVILEGE"]
    summary = {
        "status": "CAPTURED_FOR_MANUAL_REVIEW",
        "queries_completed": len(queries),
        "migration_ledger_rows": len(ledger_rows),
        "effective_table_privilege_rows": len(effective_acl_rows),
        "stored_table_acl_rows": len(acl_rows) - len(effective_acl_rows),
        "acl_provenance_query_sha256": ACL_PROVENANCE_SHA256,
        "service_role_membership_path_count": len(provenance["service_role_membership_paths"]),
        "service_role_set_role_path_count": sum(
            1 for item in provenance["service_role_membership_paths"]
            if isinstance(item, dict) and item.get("depth", 0) > 0 and item.get("all_edges_set_role") is True
        ),
        "service_role_inherited_table_acl_rows": len(provenance["service_role_inherited_table_acl_entries"]),
        "service_role_inherited_column_acl_rows": len(provenance["service_role_inherited_column_acl_entries"]),
        "service_role_parent_role_acl_path_semantics": "entries reachable through INHERIT or SET ROLE",
        "service_role_effective_privileges": provenance["service_role_effective_privileges"],
        "read_only_role_gate": "PASS",
        "project": EXPECTED_PROJECT,
        "region": EXPECTED_REGION,
        "query_pack_sha256": pack_hash,
        "next_step": "Manually compare catalog evidence to source; this script does not certify parity, remediate, or approve release.",
        "access_token_saved": False,
    }
    write_json(out / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    print(f"Evidence: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

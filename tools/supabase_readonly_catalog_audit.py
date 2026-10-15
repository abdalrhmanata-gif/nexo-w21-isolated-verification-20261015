#!/usr/bin/env python3
"""Run ZAVQERA's fixed SELECT-only catalog audit through Supabase's read-only Management API.

Requires Python 3.10+. Never uses the generic SQL endpoint, never prints/stores the
access token, verifies project name+region before SQL, verifies the effective read-only
role before continuing, and stops on ambiguous responses or migration-ledger drift.
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
PACK_SHA256 = "2462ff5f494b1acc6dd75e8290aa9eeb4fda4e4899a590e697d3c5a0be5790d2"
PACK_RELATIVE = Path("supabase/tests/hosted_readonly_catalog_audit_queries.sql")
REF_RE = re.compile(r"^[a-z0-9]{20}$")


def split_statements(sql: str) -> list[str]:
    """Split on semicolons outside SQL strings, identifiers, dollar quotes, and comments."""
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
            m = re.match(r"\$[A-Za-z_][A-Za-z0-9_]*\$|\$\$", sql[i:])
            if m:
                dollar = m.group(0)
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
    """Remove line/block comments; the checked-in pack contains no comment-only SQL."""
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    return re.sub(r"--[^\n]*", "", sql)


def load_pack(root: Path) -> tuple[list[str], str]:
    path = root / PACK_RELATIVE
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != PACK_SHA256:
        raise ValueError(f"approved query-pack hash mismatch ({digest}); stop for review")
    statements = split_statements(raw.decode("utf-8"))
    if len(statements) != 8:
        raise ValueError(f"expected exactly 8 audit queries, found {len(statements)}")
    for n, statement in enumerate(statements, 1):
        if not re.match(r"(?is)^\s*SELECT\b", no_comments(statement).strip()):
            raise ValueError(f"query {n} is not a SELECT statement; refusing to run")
    return statements, digest


def request_json(token: str, method: str, path: str, body: dict | None = None):
    if not path.startswith("/v1/projects/"):
        raise ValueError("refusing request outside the selected project's API path")
    data = json.dumps(body).encode() if body is not None else None
    request = Request(
        API + path, data=data, method=method,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json",
                 "Content-Type": "application/json", "User-Agent": "ZAVQERA-read-only-audit/1.0"},
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
    """Accept common row response forms; unknown shapes fail closed."""
    candidates = [payload]
    if isinstance(payload, dict):
        for key in ("result", "data", "rows"):
            if key in payload:
                candidates.insert(0, payload[key])
    for obj in candidates:
        if isinstance(obj, list) and all(isinstance(r, dict) for r in obj):
            return obj
        if isinstance(obj, dict) and isinstance(obj.get("rows"), list):
            names = obj.get("columns")
            if isinstance(names, list):
                names = [x if isinstance(x, str) else x.get("name") for x in names]
                if names and all(isinstance(n, str) for n in names):
                    return [dict(zip(names, r)) for r in obj["rows"] if isinstance(r, (list, tuple))]
            if all(isinstance(r, dict) for r in obj["rows"]):
                return obj["rows"]
    return None


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def local_migrations(root: Path) -> list[tuple[str, str]]:
    files = sorted((root / "supabase/migrations").glob("*.sql"))
    if not files:
        raise ValueError("no checked-in SQL migrations found")
    result = []
    for file in files:
        if "_" not in file.stem:
            raise ValueError(f"unexpected migration filename: {file.name}")
        version, name = file.stem.split("_", 1)
        if not re.fullmatch(r"\d{14}", version):
            raise ValueError(f"unexpected migration timestamp: {file.name}")
        result.append((version, name))
    return result


def compare_ledger(payload, local):
    rows = rows_from(payload)
    if rows is None:
        return {"comparison": "UNVERIFIED_RESPONSE_SHAPE"}
    remote = []
    for row in rows:
        if row.get("version") is None or row.get("name") is None:
            return {"comparison": "UNVERIFIED_LEDGER_COLUMNS", "remote_count": len(rows)}
        remote.append((str(row["version"]), str(row["name"])))
    missing, extra = sorted(set(local) - set(remote)), sorted(set(remote) - set(local))
    return {
        "comparison": "MATCH" if not missing and not extra else "MISMATCH_BLOCKING",
        "local_count": len(local), "remote_count": len(remote),
        "missing_from_remote": [{"version": v, "name": n} for v, n in missing],
        "extra_in_remote": [{"version": v, "name": n} for v, n in extra],
    }


def main() -> int:
    if "--self-test" in sys.argv:
        sample = "-- semicolon ;\nSELECT 'a;b' AS x; /* comment ; */ SELECT 2;"
        assert len(split_statements(sample)) == 2
        root = Path(__file__).resolve().parents[1]
        queries, digest = load_pack(root)
        print(f"SELF_TEST=PASS; queries={len(queries)}; sha256={digest}; no network requests")
        return 0

    ref = os.getenv("SUPABASE_PROJECT_REF", "").strip()
    token = os.getenv("SUPABASE_ACCESS_TOKEN", "").strip()
    if not REF_RE.fullmatch(ref):
        print("BLOCKED: set SUPABASE_PROJECT_REF to the verified 20-character Development ref.", file=sys.stderr)
        return 2
    if not token:
        print("BLOCKED: SUPABASE_ACCESS_TOKEN is missing; never paste it into chat or commit it.", file=sys.stderr)
        return 2
    if os.getenv("ZAVQERA_AUDIT_CONFIRMATION") != "DEVELOPMENT_ONLY_READ_ONLY":
        print("BLOCKED: explicitly confirm the selected ref is Development and the API token is read-only scoped.", file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parents[1]
    try:
        queries, pack_hash = load_pack(root)
        local = local_migrations(root)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"BLOCKED: input validation failed: {exc}", file=sys.stderr)
        return 2

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = root / "zavqera-readonly-audit-output" / stamp
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "run_metadata.json", {
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "project_ref": ref, "expected_project": EXPECTED_PROJECT, "expected_region": EXPECTED_REGION,
        "endpoint": "Supabase Management API /database/query/read-only (Beta)",
        "query_pack_sha256": pack_hash, "query_count": len(queries), "local_migration_count": len(local),
        "token_saved": False,
    })

    try:
        project = request_json(token, "GET", f"/v1/projects/{quote(ref, safe='')}")
        if not isinstance(project, dict) or not isinstance(project.get("name"), str):
            raise RuntimeError("project metadata shape unrecognized; no SQL executed")
        observed = {k: project.get(k) for k in ("id", "name", "region", "status")}
        write_json(out / "project_identity.json", observed)
        if project.get("name") != EXPECTED_PROJECT or project.get("region") != EXPECTED_REGION:
            raise RuntimeError("project name/region did not match Development baseline; no SQL executed")
        if project.get("id") is not None and str(project["id"]) != ref:
            raise RuntimeError("returned project ID does not match requested ref; no SQL executed")
        if project.get("status") and str(project["status"]).upper() not in {"ACTIVE_HEALTHY", "ACTIVE"}:
            raise RuntimeError("project is not active/healthy; no SQL executed")
    except Exception as exc:
        write_json(out / "stop.json", {"stage": "project_identity", "reason": str(exc), "sql_queries_executed": 0})
        print(f"BLOCKED before SQL: {exc}\nEvidence: {out}", file=sys.stderr)
        return 3

    results = []
    for index, query in enumerate(queries, 1):
        try:
            payload = request_json(token, "POST", f"/v1/projects/{quote(ref, safe='')}/database/query/read-only", {"query": query})
        except Exception as exc:
            write_json(out / f"query_{index:02d}_error.json", {"error": str(exc), "query_number": index})
            write_json(out / "stop.json", {"stage": f"query_{index:02d}", "reason": str(exc), "completed_queries": index - 1})
            print(f"BLOCKED at query {index}: {exc}\nEvidence: {out}", file=sys.stderr)
            return 4
        write_json(out / f"query_{index:02d}.json", {"query": query, "response": payload})
        results.append(payload)
        if isinstance(payload, dict) and payload.get("error"):
            write_json(out / "stop.json", {"stage": f"query_{index:02d}", "reason": "API response returned error", "completed_queries": index})
            print(f"BLOCKED at query {index}: response contains an error. Evidence: {out}", file=sys.stderr)
            return 4

        if index == 1:
            rows = rows_from(payload)
            if rows is None or len(rows) != 1:
                write_json(out / "stop.json", {"stage": "read_only_role_gate", "reason": "unknown response shape", "completed_queries": 1})
                print(f"BLOCKED: unknown Query 1 response shape; no further SQL sent. Evidence: {out}", file=sys.stderr)
                return 5
            row = rows[0]
            gate = {
                "current_user_is_read_only_role": row.get("current_user") == READ_ONLY_ROLE,
                "role_not_superuser": row.get("rolsuper") is False,
                "role_cannot_create_database": row.get("rolcreatedb") is False,
                "role_cannot_create_roles": row.get("rolcreaterole") is False,
            }
            write_json(out / "read_only_role_gate.json", {
                "checks": gate,
                "observed": {k: row.get(k) for k in ("current_user", "session_user", "server_version_num", "transaction_read_only", "rolsuper", "rolcreatedb", "rolcreaterole", "rolbypassrls")},
            })
            if not all(gate.values()):
                write_json(out / "stop.json", {"stage": "read_only_role_gate", "reason": "identity/capability gate failed", "completed_queries": 1})
                print(f"BLOCKED: read-only role gate failed; no further SQL sent. Evidence: {out}", file=sys.stderr)
                return 5

        if index == 7:
            rows = rows_from(payload)
            if rows is None or len(rows) != 1 or not rows[0].get("migration_ledger_relation"):
                write_json(out / "stop.json", {"stage": "ledger_presence_gate", "reason": "migration ledger missing or result shape unknown", "completed_queries": 7})
                print(f"BLOCKED: migration ledger not verified; Query 8 not sent. Evidence: {out}", file=sys.stderr)
                return 6

    ledger = compare_ledger(results[7], local)
    write_json(out / "migration_ledger_comparison.json", ledger)
    status = "CAPTURED_LEDGER_MATCH_REVIEW_REQUIRED" if ledger.get("comparison") == "MATCH" else "BLOCKED_MIGRATION_LEDGER_MISMATCH_OR_UNVERIFIED"
    summary = {
        "status": status, "queries_completed": 8, "read_only_role_gate": "PASS",
        "project": EXPECTED_PROJECT, "region": EXPECTED_REGION, "ledger_comparison": ledger.get("comparison"),
        "next_step": "Manual security review of all ACL/owner/search_path results is required; this runner does not certify the audit or remediate.",
    }
    write_json(out / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    print(f"Evidence: {out}")
    return 0 if status == "CAPTURED_LEDGER_MATCH_REVIEW_REQUIRED" else 7


if __name__ == "__main__":
    raise SystemExit(main())

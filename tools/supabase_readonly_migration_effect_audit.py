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
PACK_SHA256 = "7fbe8b65aeb75c446ca942277d0541de27de905e9b2172f304924e9029de6c62"
PACK_RELATIVE = Path("supabase/tests/hosted_readonly_migration_effect_audit_queries.sql")
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
    if len(statements) != 10:
        raise ValueError(f"expected exactly 10 supplemental audit queries, found {len(statements)}")
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
        print(f"SELF_TEST=PASS; queries={len(queries)}; sha256={digest}; no network requests")
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
        "query_count": len(queries),
        "token_saved": False,
        "scope": "catalog/migration-effect metadata; no application rows",
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

    summary = {
        "status": "CAPTURED_FOR_MANUAL_REVIEW",
        "queries_completed": len(queries),
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

# ZAVQERA — Hosted Read-Only Catalog Reconciliation Runbook (2026-10-15)

**Status: PREPARED, NOT EXECUTED AGAINST HOSTED DATABASES.** This is a SELECT-only runbook for a separately verified, project-scoped read-only connection. It is not a migration and authorizes no database or privilege changes.

## Why the connection must be configured first

Supabase documents a read-only MCP mode: set `read_only=true` and scope it to the exact project with `project_ref=<verified-development-project-ref>`. The official guidance says this mode runs queries as a read-only Postgres user and disables mutating tools: [Supabase MCP configuration](https://supabase.com/docs/guides/ai-tools/mcp).

The Management API also documents the experimental endpoint `POST /v1/projects/{ref}/database/query/read-only`, which runs SQL as `supabase_read_only_user` and requires `database:read` plus `database_read`: [Read-only query API](https://supabase.com/docs/reference/api/v1-read-only-query). The tool surface available in this session does not expose that endpoint or let this runbook inspect/change the connected MCP server URL. Its generic `execute_sql` tool is therefore **not** treated as proof of read-only connection configuration.

**Do not run any hosted query until the active connection itself is verified as project-scoped and read-only.** No query below was sent to hosted Development or Main/Production.

## Execution protocol

1. In Supabase MCP connection settings, configure an independently identifiable connection scoped to the verified Development `project_ref` with `read_only=true` (optionally restrict tools to `features=database,docs`). Do not guess the project ref from the project name.
2. Run **each SQL block separately** through that connection. Do not combine statements and do not substitute the normal unrestricted `execute_sql` connection.
3. Run Query 1 first. Continue only if `current_user = supabase_read_only_user` and the active MCP connection is independently confirmed to use `read_only=true` scoped to the verified Development ref. Stop if the role is a superuser, can create roles/databases, or the identity/configuration is uncertain. Record `rolbypassrls` and `transaction_read_only`: the disposable Supabase PG17 image reports `rolbypassrls=true` for its `supabase_read_only_user`, so bypass-RLS alone is not treated as a write privilege, but it means the SQL scope must remain restricted to the catalog and migration-ledger queries in this runbook—never query application rows. If the hosted role or its effective grants do not match the documented read-only identity, stop.
4. Capture query output with the exact project scope and UTC timestamp. Do not capture credentials, user rows, invitation tokens, or other application data.
5. Compare the migration ledger and catalog output to the reviewed candidate source. Any missing/extra migration, unexpected role/membership, ACL, owner, SECURITY DEFINER setting, or search-path difference is a stop condition. Do not remediate in place.

## Query 1 — Verify session and effective role

```sql
SELECT
  current_database() AS database_name,
  current_user AS current_user,
  session_user AS session_user,
  current_setting('server_version_num')::integer AS server_version_num,
  current_setting('transaction_read_only')::boolean AS transaction_read_only,
  r.rolsuper,
  r.rolcreatedb,
  r.rolcreaterole,
  r.rolcanlogin,
  r.rolbypassrls,
  (SELECT pg_catalog.to_regclass('supabase_migrations.schema_migrations')::text)
    AS migration_ledger_relation
FROM pg_catalog.pg_roles AS r
WHERE r.rolname = current_user;
```

**Gate:** require exactly one row; expected `current_user` is `supabase_read_only_user`. Stop if the role is missing or privileged, the query cannot read the required metadata, or the connection is not independently scoped to the intended Development project. Record the server version and transaction flag; do not attempt a write to test the connection.

## Query 2 — Relevant role attributes

```sql
SELECT
  r.rolname,
  r.rolsuper,
  r.rolinherit,
  r.rolcreaterole,
  r.rolcreatedb,
  r.rolcanlogin,
  r.rolreplication,
  r.rolbypassrls
FROM pg_catalog.pg_roles AS r
WHERE r.rolname IN (
  'postgres',
  'supabase_admin',
  'supabase_read_only_user',
  'anon',
  'authenticated',
  'service_role'
)
ORDER BY r.rolname;
```

## Query 3 — Role membership relevant to the audit

```sql
SELECT
  member.rolname AS member_role,
  granted.rolname AS granted_role,
  m.admin_option,
  m.inherit_option,
  m.set_option
FROM pg_catalog.pg_auth_members AS m
JOIN pg_catalog.pg_roles AS member ON member.oid = m.member
JOIN pg_catalog.pg_roles AS granted ON granted.oid = m.roleid
WHERE member.rolname IN (
        'postgres', 'supabase_admin', 'supabase_read_only_user',
        'anon', 'authenticated', 'service_role'
      )
   OR granted.rolname IN (
        'postgres', 'supabase_admin', 'supabase_read_only_user',
        'anon', 'authenticated', 'service_role'
      )
ORDER BY member.rolname, granted.rolname;
```

## Query 4 — Built-in global function ACL defaults

PostgreSQL's built-in defaults are not necessarily rows in `pg_default_acl`; inspect them separately from explicit default-ACL overrides.

```sql
SELECT
  creator.rolname AS creator_role,
  CASE WHEN acl.grantee = 0 THEN 'PUBLIC'
       ELSE pg_catalog.pg_get_userbyid(acl.grantee) END AS grantee,
  acl.privilege_type,
  acl.is_grantable
FROM pg_catalog.pg_roles AS creator
CROSS JOIN LATERAL pg_catalog.aclexplode(
  pg_catalog.acldefault('f', creator.oid)
) AS acl
WHERE creator.rolname IN ('postgres', 'supabase_admin')
ORDER BY creator.rolname, grantee, acl.privilege_type;
```

## Query 5 — Explicit global and per-schema default ACL overrides

```sql
SELECT
  creator.rolname AS creator_role,
  COALESCE(n.nspname, '<global>') AS schema_name,
  d.defaclobjtype AS object_type,
  CASE WHEN acl.grantee = 0 THEN 'PUBLIC'
       ELSE grantee.rolname END AS grantee,
  acl.privilege_type,
  acl.is_grantable
FROM pg_catalog.pg_default_acl AS d
JOIN pg_catalog.pg_roles AS creator ON creator.oid = d.defaclrole
LEFT JOIN pg_catalog.pg_namespace AS n ON n.oid = d.defaclnamespace
CROSS JOIN LATERAL pg_catalog.aclexplode(d.defaclacl) AS acl
LEFT JOIN pg_catalog.pg_roles AS grantee ON grantee.oid = acl.grantee
WHERE creator.rolname IN ('postgres', 'supabase_admin')
ORDER BY creator.rolname, schema_name, d.defaclobjtype, grantee, acl.privilege_type;
```

Interpret global defaults and schema-specific overrides together: per-schema default grants add to global defaults; a schema-specific revoke cannot remove a grant inherited from the global default ACL. This query reports policy only; it changes nothing.

## Query 6 — Existing user-defined routines, owner, security mode, path, and effective EXECUTE

```sql
SELECT
  n.nspname AS schema_name,
  p.proname AS routine_name,
  pg_catalog.pg_get_function_identity_arguments(p.oid) AS identity_arguments,
  p.prokind AS routine_kind,
  pg_catalog.pg_get_userbyid(p.proowner) AS owner_role,
  p.prosecdef AS security_definer,
  p.proconfig AS routine_settings,
  p.proacl::text AS stored_acl,
  pg_catalog.has_function_privilege('anon', p.oid, 'EXECUTE') AS anon_execute,
  pg_catalog.has_function_privilege('authenticated', p.oid, 'EXECUTE') AS authenticated_execute,
  pg_catalog.has_function_privilege('service_role', p.oid, 'EXECUTE') AS service_role_execute
FROM pg_catalog.pg_proc AS p
JOIN pg_catalog.pg_namespace AS n ON n.oid = p.pronamespace
WHERE p.prokind IN ('f', 'p')
  AND n.nspname NOT IN ('pg_catalog', 'information_schema')
  AND (
    n.nspname = 'public'
    OR pg_catalog.pg_get_userbyid(p.proowner) = 'supabase_admin'
    OR p.prosecdef
  )
ORDER BY n.nspname, p.proname, pg_catalog.pg_get_function_identity_arguments(p.oid);
```

This inventories all public routines plus non-system SECURITY DEFINER routines and routines owned by `supabase_admin`. Review each owner, `security_definer`, routine settings (especially a pinned `search_path`), stored ACL, and effective access for `anon`, `authenticated`, and `service_role`. A NULL stored ACL means PostgreSQL's default ACL semantics apply; do not interpret NULL as “no access.” The query does not invoke routine bodies.

## Query 7 — Confirm migration ledger relation before reading it

```sql
SELECT pg_catalog.to_regclass('supabase_migrations.schema_migrations')::text
  AS migration_ledger_relation;
```

Only if this returns the expected relation and the read-only identity gate passed, run this separate query:

```sql
SELECT version, name
FROM supabase_migrations.schema_migrations
ORDER BY version;
```

If the relation is absent or access is denied, report the ledger as **unverified**; do not switch to an unrestricted connection to force the query. Compare the returned rows with the exact checked-in migration set and stop on any difference.

## Evidence and exit criteria

Mark the hosted audit **PASS** only when all are true:

- The connection is independently confirmed project-scoped to the intended Development project and read-only.
- The session identity/capabilities pass Query 1.
- Role attributes, membership, built-in defaults, explicit default ACLs, routine ownership/security/search-path/ACL/effective grants and the migration ledger are captured.
- The exact migration ledger and relevant catalog state are compared to a reviewed source baseline; every mismatch is either explained by authoritative evidence or remains a blocker.

Otherwise report **BLOCKED / PARTIAL**, record the missing evidence, and stop. Do not create W86 or another migration, do not alter ACLs, and do not infer hosted state from the disposable PostgreSQL 17 runs. Keep `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed; PR #39 Draft/open/unmerged; Issue #23 open; launch **NO-GO**.


## Local PostgreSQL 17 smoke validation — 2026-10-15

**Result: PASS for local query compatibility only; hosted audit remains UNEXECUTED.**

- Query pack: [`supabase/tests/hosted_readonly_catalog_audit_queries.sql`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w80-forward-correction-20261015/supabase/tests/hosted_readonly_catalog_audit_queries.sql), blob SHA `c9c29ec8cff4ff1b5021628ea8b61be9d69b7393`. Content review split it into exactly **8 statements**, each beginning with `SELECT`; no DDL/DML/role-change statement was found.
- Exact isolated PG17 job: [W80 run 38759025529 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38759025529), code/workflow SHA `5556da5d852a5bece34fe172b18d0aae921bf1f5`.
- Captured artifact: [11985121817](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38759025529/artifacts/11985121817), digest `sha256:0211687245bd2abab6df5ed55daff033f04066716176a482adc943889d5199b0`.
- Artifact evidence records source query-pack SHA-256 `2462ff5f494b1acc6dd75e8290aa9eeb4fda4e4899a590e697d3c5a0be5790d2`, `hosted_readonly_query_pack_local_smoke_exit_code=0`, and `hosted_readonly_query_pack_local_smoke_status=0`.
- Same run: PostgreSQL `170011`; migration replay through W83 exit 0; W44 17/17, W46 8/8, W80 49/49 before and after W83 reapply; W84 21/21 after chain and after reapply; W85 12/12; the pre/post W83 catalog snapshots are identical (both SHA-256 `3c7cbd6ff0258079c135d6d6edf8bcb3e4f0d2e1a5a4b384fac2c71af45b3e91`); cleanup verified with no remaining containers/volumes.
- **Artifact gap closed:** the raw `W85_READONLY_CATALOG_QUERY_PACK.txt` was added to the artifact upload list in the only code diff after SHA `5556da5...`. Revalidation [run 38759493778 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38759493778) completed on SHA `1ada382e4c320d6b7f7815a30238fe99b1519305`; artifact [11984449025](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38759493778/artifacts/11984449025), digest `sha256:0ab752f5fe4876f3008786ea3e0e182d61749446283c68fce8133d94ee02223e`. I downloaded and inspected the ZIP: it now contains the 592-line raw query-pack output, the evidence report, W83 before/after catalog snapshots, and cleanup proof. The raw query log had no SQL errors; all eight statements completed. Evidence confirms query-pack exit 0, W44 17/17, W46 8/8, W80 49/49 before/after W83, W84 21/21 twice, W85 12/12, identical W83 pre/post snapshots and cleanup verified.
- This validates query execution on the **disposable local** PG17 stack only. It does not prove current hosted Development role identity, read-only transport, migration ledger, ACLs, function ownership or schema parity.

The hosted step is still **BLOCKED** until a separately verifiable connection is configured with the exact Development project ref and `read_only=true`. No hosted SQL was executed. Do not use generic `execute_sql` as a substitute; do not change hosted grants/migrations; do not create W86 from local-only results.


## Full W21 local launch gate — 2026-10-15

- Exact source/workflow SHA: `6c88b3683fc4f32bea611fafa6e226fc878af5e0`.
- [W21 Local Launch Gate run 38758953821 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38758953821).
- [W21 evidence artifact 11984937895](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38758953821/artifacts/11984937895), digest `sha256:ae51b190a638c4455918afebae6ac1b156b6a43a8b7b408b61beb4f730962daf`.
- [Browser diagnostics artifact 11985057666](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38758953821/artifacts/11985057666), digest `sha256:64c7b86f5d614eecbbef92a28713a57c4996dbec93cbfc3d90936551dd67e307`; inspected log reports **2 passed (2.6m)**.
- The run checked PostgreSQL 17, W83 read-only catalog report (`READ_ONLY_GUARD=CONFIRMED` in the disposable test session), Mission Authority security regressions, W85 as actual `supabase_admin`, quota/workspace checks, four actual-ledger concurrency races, fake-provider gateway integration, browser E2E, and teardown. Evidence records `supabase_stop_exit_code=0`, no remaining containers or volumes, and `cleanup_verified=true`.
- This W21 source predates only the W80 workflow artifact-list fix at `1ada382e4c320d6b7f7815a30238fe99b1519305`. The separate W80 run on SHA `1ada382e...` completed the query-pack smoke and retained its raw output artifact. These remain disposable-local results; neither run queried hosted Development.

**Still blocked:** hosted catalog reconciliation has not been run. Proceed only through an independently verified connection configured `project_ref=<verified-development-ref>&read_only=true`; do not substitute unrestricted `execute_sql`. Keep launch **NO-GO** until hosted ledger/catalog and production enforcement/provider gates are independently proven.


## Direct read-only Management API runner — 2026-10-15

**Purpose:** Remove dependence on reconfiguring this ChatGPT session's existing Supabase connector. This remains **not executed against hosted Development yet**.

### Official transport and permissions

Supabase documents the beta endpoint **POST /v1/projects/{ref}/database/query/read-only**. It executes SQL as **supabase_read_only_user**, requires OAuth scope **database:read** and fine-grained token permission **database_read**, and requires schema-qualified object references. [Official endpoint reference](https://supabase.com/docs/reference/api/v1-read-only-query).

The runner also performs a GET of **/v1/projects/{ref}** before sending any SQL to confirm the project's name and region. Supabase's scoped token documentation states that the project metadata endpoint is covered by **Project Settings (Read)**; use a token scoped to this project with only **Project Settings (Read)** and **Database (Read)**. [Scoped PAT guidance](https://supabase.com/docs/guides/platform/personal-access-tokens). Do not use a full-access token. Create/use the token locally; never paste it into chat, commit it, or add it to GitHub secrets.

### Added runner and safety properties

- Runner: [tools/supabase_readonly_catalog_audit.py](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w80-forward-correction-20261015/tools/supabase_readonly_catalog_audit.py).
- Tests: [tests/test_supabase_readonly_catalog_audit.py](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w80-forward-correction-20261015/tests/test_supabase_readonly_catalog_audit.py).
- Query pack: [supabase/tests/hosted_readonly_catalog_audit_queries.sql](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w80-forward-correction-20261015/supabase/tests/hosted_readonly_catalog_audit_queries.sql), fixed SHA-256 **2462ff5f494b1acc6dd75e8290aa9eeb4fda4e4899a590e697d3c5a0be5790d2**.
- The runner will not use the generic /database/query endpoint; it calls only /database/query/read-only. It checks the query pack's exact SHA-256 before any request and requires exactly eight SQL statements.
- It confirms the referenced project's API response says exactly **ZAVQERA Development**, region **eu-west-1**, and active/healthy status before SQL. Mismatches stop before SQL.
- It runs Query 1 first. It sends no further SQL unless current_user is **supabase_read_only_user**, and that role is not superuser and cannot create roles/databases. Unknown response shapes stop after Query 1.
- It will not run Query 8 unless Query 7 proves the migration ledger relation exists. The token is not written to output. The generated report directory is gitignored.
- It compares the returned migration ledger against the exact checked-in migration filenames. A mismatch remains a blocker. Even with a matching ledger, the report status is **CAPTURED_LEDGER_MATCH_REVIEW_REQUIRED**, not an overall security-audit PASS. Owner/security/path/ACL results need manual comparison with the reviewed expected-state matrix.
- A CI self-test runs only parser/hash/response-shape tests and explicitly makes **no network request**. The actual hosted audit requires the operator's local environment variables, so it cannot run from this repository's public GitHub Actions.

### Windows PowerShell execution

Run from a local checkout of this verification branch, with Python 3.10+:

~~~powershell
$env:SUPABASE_PROJECT_REF = Read-Host "Verified ZAVQERA Development project ref"
$secure = Read-Host "Scoped Supabase PAT (Project Settings Read + Database Read)" -AsSecureString
$env:SUPABASE_ACCESS_TOKEN = [System.Net.NetworkCredential]::new("", $secure).Password
$env:ZAVQERA_AUDIT_CONFIRMATION = "DEVELOPMENT_ONLY_READ_ONLY"

try {
    py -3 tools/supabase_readonly_catalog_audit.py --self-test
    if ($LASTEXITCODE -ne 0) { throw "Read-only audit self-test failed; no hosted query was run." }
    py -3 -m unittest discover -s tests -p "test_supabase_readonly_catalog_audit.py" -v
    if ($LASTEXITCODE -ne 0) { throw "Read-only audit unit tests failed; no hosted query was run." }
    py -3 tools/supabase_readonly_catalog_audit.py
    if ($LASTEXITCODE -ne 0) { throw "Audit stopped or found a blocking mismatch; inspect the local report." }
}
finally {
    Remove-Item Env:SUPABASE_ACCESS_TOKEN, Env:SUPABASE_PROJECT_REF, Env:ZAVQERA_AUDIT_CONFIRMATION -ErrorAction SilentlyContinue
}
~~~

Review that the project identity check passes before queries are sent. The script stores metadata/SQL responses only under zavqera-readonly-audit-output/<UTC timestamp>/; do not upload raw output anywhere until it has been reviewed and redacted. If the token lacks the required narrow permissions, if the API rejects the response format, or if any project/role/ledger gate fails, the script stops and records the blocker.

### ChatGPT connector limitation

OpenAI's current help article states custom MCP server connections are available on ChatGPT Business and Enterprise/Edu web workspaces, and not on mobile. This current session's already connected Supabase integration does not expose a read-only Management API action or its MCP URL configuration; therefore its generic execute_sql remains prohibited as a substitute. [OpenAI custom MCP availability](https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt).

**Status:** runner prepared in the temporary verification repository; check the exact-SHA W80 CI run before relying on its self-test. Hosted query still **not executed**. Keep Main/Production untouched; do not apply migrations or alter ACLs; launch remains **NO-GO**.

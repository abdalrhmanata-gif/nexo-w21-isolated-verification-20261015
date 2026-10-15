# ZAVQERA — Supplemental Hosted Migration-Effect Audit Runbook (2026-10-15)

**Status: the original 10-query version was executed; updated 12-query version is prepared but not yet executed against hosted Development.** Captured evidence identified catalog/history mismatches. Queries 11–12 now add the hosted migration ledger version/name pairs and the W66 table ACL inventory. This remains read-only and cannot approve a rollout.

## Repository and safety scope

- Repository: `abdalrhmanata-gif/nexo-w21-isolated-verification-20261015`
- Branch: `codex/w80-forward-correction-20261015`
- Project: `ZAVQERA Development`, ref `mrwmmbytcymqgwvcoywd`, region `eu-west-1`
- Pack: `supabase/tests/hosted_readonly_migration_effect_audit_queries.sql`
- Runner: `tools/supabase_readonly_migration_effect_audit.py`
- Tests: `tests/test_supabase_readonly_migration_effect_audit.py`
- Pack SHA-256 (LF-normalized, updated 12-query version): `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`
- All 12 fixed statements must begin with SELECT. The runner pins the digest, verifies the project identity before SQL and checks effective role/transaction guard before query 2.
- Only `POST /v1/projects/{ref}/database/query/read-only` is allowed for SQL. The normal SQL endpoint is never used.
- The observed read-only role has `rolbypassrls=true`; the pack is limited to catalog/ledger metadata. Do not add application-row queries.
- Never set the query target to Main/Production; never send a PAT through ChatGPT, GitHub, a file, command-line argument, or shell history.

## Windows PowerShell procedure

Run from the existing checkout in the PowerShell window. First pull the new docs/pack/runner/tests/workflow updates:

```powershell
git pull --ff-only origin codex/w80-forward-correction-20261015
```

Then run local self-test and isolated unit tests (no hosted network requests):

```powershell
py -3 tools/supabase_readonly_migration_effect_audit.py --self-test
if ($LASTEXITCODE -ne 0) { throw "Self-test failed; do not connect." }

py -3 -m unittest discover -s tests -p "test_supabase_readonly_migration_effect_audit.py" -v
if ($LASTEXITCODE -ne 0) { throw "Unit tests failed; do not connect." }
```

Only continue after both commands pass. Confirm your PAT is a **Scoped Personal Access Token** with scope limited to this one Development project and only these permissions:
- Project Settings — Read
- Database — Read (`database_read`)

If the token previously pasted into ChatGPT was not already revoked, revoke it first. A revoked token cannot be reused.

Set the project ref, receive the token through a hidden prompt, and run the supplemental audit. Paste one line at a time or paste this complete block; do not include token text anywhere in it.

```powershell
$env:SUPABASE_PROJECT_REF = "mrwmmbytcymqgwvcoywd"
$secure = Read-Host "Scoped Development PAT (hidden)" -AsSecureString
$env:SUPABASE_ACCESS_TOKEN = [System.Net.NetworkCredential]::new("", $secure).Password
$secure.Dispose()
$env:ZAVQERA_AUDIT_CONFIRMATION = "DEVELOPMENT_ONLY_READ_ONLY"

try {
    py -3 tools/supabase_readonly_migration_effect_audit.py
    $auditExitCode = $LASTEXITCODE
    Write-Host "EFFECT_AUDIT_EXIT_CODE=$auditExitCode"
}
finally {
    Remove-Item Env:SUPABASE_ACCESS_TOKEN, Env:SUPABASE_PROJECT_REF, Env:ZAVQERA_AUDIT_CONFIRMATION -ErrorAction SilentlyContinue
}
```

The secure prompt normally displays masking characters rather than the token. Do not echo the token or test it with other commands. After the script exits, the environment variables are removed. Revoke the PAT after the work is complete if it was created for this audit only.

## Expected output and interpretation

- `CAPTURED_FOR_MANUAL_REVIEW` means the metadata responses were captured, the project identity passed and query 1 confirmed the effective read-only role/transaction. It does **not** mean schema parity, migration history, security or launch passed.
- `BLOCKED at project_identity` means no SQL was sent.
- `BLOCKED at read_only_role_gate` means the runner stopped after query 1.
- `BLOCKED at query_NN` means the specific metadata query failed or returned an unknown response shape. Do not use the normal unrestricted SQL endpoint as a workaround.
- Results are written under `zavqera-readonly-effect-audit-output/<UTC timestamp>/`. The folder is gitignored. The report contains role/schema/function/trigger/default-ACL metadata and function definitions; it should not contain access tokens or application table rows.
- To share evidence for review, zip the newest evidence folder only and upload it in the project conversation. Do not include other files, credentials, shell history or connection configuration.

## Query coverage

1. Session role, transaction read-only, project database version and migration-ledger visibility.
2. Existence/owner/RLS state for tables affected by W66/W68–W82/W83.
3. Expected columns for dispatch, reconciliation, Research-JIT, budget reservations and W82 identity binding.
4. Expected constraints.
5. Relevant index presence and definition.
6. Exact candidate function signatures (present and forbidden legacy signatures), owner, SECURITY DEFINER, configured search path, and effective API-role EXECUTE.
7. Stored and effective USAGE on `private`.
8. W75/W76 provider-receipt trigger and trigger-function identity.
9. Definitions of relevant public/private routines, to distinguish catalog existence from implementation body.
10. Built-in and explicit function-default ACLs for `postgres` and `supabase_admin`.
11. Migration ledger `version,name` pairs only; SQL bodies are not returned.
12. Effective and expanded stored ACL rows for `public.agent_executions` (W66).

## After collection

Next, run the updated pack after CI/local PostgreSQL 17 syntax validation, then manually match ledger tuples to source files and classify the W66 effective/stored ACLs. Do not assume the ledger row count until the new capture is reviewed. A database/platform owner must independently review all unexpected privilege paths, function owners/modes, search paths, relation ACLs and default ACL policy.

No hosted remediation is authorized by this runbook. Do not run `supabase db push`, `migration repair`, manually edit `supabase_migrations.schema_migrations`, replay migrations against hosted Development, or change Supabase Main/Production. Any future hosted migration requires a separate reviewed plan and explicit owner authorization.

**Release remains NO-GO.** Keep PR #39 open/Draft/unmerged, Issue #23 open, and `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed.


## Offline comparison after the updated 12-query capture

After the updated audit completes and the evidence folder contains query_11.json and query_12.json, run this from the repository root in PowerShell:

```powershell
$auditDir = "C:\Users\oem\nexo-w21-isolated-verification-20261015\zavqera-readonly-effect-audit-output\<new-UTC-folder>"
py -3 tools/review_hosted_migration_ledger.py --evidence-dir $auditDir
```

This offline comparator verifies the project/query-pack evidence identity, compares every hosted ledger (version,name) tuple to checked-in migration filenames, records same-name/different-version candidates and inspects the captured W66 ACL matrix. It writes ledger_acl_review.json and ledger_acl_review.md inside that evidence folder. Its status is always REVIEW REQUIRED / NO-GO; it cannot certify historical SQL equality and it never connects to Supabase.

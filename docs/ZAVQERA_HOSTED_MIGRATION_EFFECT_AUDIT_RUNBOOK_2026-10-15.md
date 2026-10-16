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


## Verified isolated SQL smoke — 2026-10-15

The updated 12-query pack passed a full local smoke through disposable PostgreSQL 17 in [W80 run 38786902560](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38786902560). Evidence artifact digest: SHA-256 3847bca8e7eb28acd3fa0d54d6166b86b366ab6d1ae862a7b0449bcf17a67fc0. The artifact records migration_effect_readonly_query_pack_sha256=a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284 and local smoke exit/status 0.

This is syntax/catalog compatibility evidence on a disposable database only. It does not mean the pack was run against hosted Development; a fresh local user-run 12-query capture remains required.


## Completed 12-query hosted capture received — 2026-10-15

The user has now run the updated pack against Development and supplied evidence. ZIP SHA-256: `fff6f88aca42c73dc691ead099e969f3cfc911fea5504ce1291b6e04ae0320f6`; capture UTC `2026-10-15T18:45:25.121761+00:00`; query-pack SHA-256 `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`.

Queries 11/12 provide 74 hosted ledger tuples and direct W66 relation ACL evidence. The key finding is that `service_role` has all eight queried effective/stored privileges on `public.agent_executions`, including direct INSERT/UPDATE/DELETE/TRUNCATE, contrary to the checked-in W66 `REVOKE ALL`. Full review and counts are in `docs/ZAVQERA_HOSTED_12_QUERY_AUDIT_REVIEW_2026-10-15.md`. The tool status remains `CAPTURED_FOR_MANUAL_REVIEW`, not a release pass. Do not run hosted repair SQL or migrations.


## Updated Development capture — 13 queries, including inherited ACL provenance (2026-10-16)

The previous 12-query capture remains valid evidence for the 2026-10-15 observation, but it does not include role-membership inheritance paths. A fresh capture is required before any W86 hosted repair proposal.

The guarded runner now pins two files independently:
- Base 12-query pack SHA-256: a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284
- Query 13, supabase/tests/hosted_readonly_w86_acl_provenance_query.sql, SHA-256: ffdcc3f51ee20fb2ddb44e74f292df4767a76a9dff5e8cd30eef2adb8e9d4f64

From the repository root in PowerShell, first run: py -3 tools/supabase_readonly_migration_effect_audit.py --self-test

Expected self-test output: SELF_TEST=PASS; queries=13; base_sha256=a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284; acl_provenance_sha256=ffdcc3f51ee20fb2ddb44e74f292df4767a76a9dff5e8cd30eef2adb8e9d4f64; no network requests.

Then run the same guarded Development capture procedure described earlier in this runbook, using the verified Development project ref, explicit DEVELOPMENT_ONLY_READ_ONLY confirmation, and the scoped read-only Management API token locally. The runner verifies both SQL hashes, validates project identity and the read-only role before proceeding, sends only Management API database/query/read-only requests, saves query outputs 01–13, and never saves or prints the token. Do not paste a token into chat. Inspect the evidence ZIP for secrets before uploading it.

After capture, run the offline reviewer against the new evidence folder with: py -3 tools/review_hosted_migration_ledger.py --evidence-dir <new-evidence-folder>

The reviewer now requires query_13.json and the exact ACL provenance query hash. Review service_role_inherited_table_acl_rows, service_role_inherited_column_acl_rows, and the role-path entries in ledger_acl_review.json/.md. Any inherited ACL entry blocks the current W86 candidate; do not apply W86 as-is if one is present. The report remains REVIEW REQUIRED / NO-GO regardless of zero inherited rows.

## Verified local runner and query smoke — 2026-10-16

The 13-query runner, offline reviewer, and ACL provenance SQL passed W80 isolated PostgreSQL 17 validation on run 38858063330, source SHA f4d7fed423739db0d39ba576ca455c5d4a182169. Evidence artifact 12027554468, ZIP SHA-256 8147e0b3624b27bdd6dc83f566b665a8942a1b3aac3e3dd785de1a3fc45a483d; cleanup was verified. Flutter CI passed on the same SHA in run 38858068979. This is local/disposable validation only; a new hosted capture is still outstanding.


## Recommended Windows PowerShell helper

From the isolated audit repository root, run: `.\tools\run_zavqera_readonly_effect_audit.ps1`.

The helper first runs the no-network self-test, then prompts for the scoped token using hidden SecureString input, runs the pinned 13-query read-only capture, invokes the offline reviewer against the same checkout, and zips the evidence. It removes the token from the process environment and clears the temporary BSTR in a finally block. It performs no migrations or hosted writes. If the capture stops at a gate, it preserves partial evidence and reports the blocked stage; do not weaken the gate or change the SQL to make it pass.

# ZAVQERA — Supplemental Hosted Migration-Effect Audit Runbook (2026-10-15)

**Status: prepared; not executed against hosted Development.** The first 8-query audit has already completed and identified catalog/history mismatches. This supplemental 10-query pack expands metadata coverage. It is read-only only, does not change hosted state, and cannot approve a rollout.

## Repository and safety scope

- Repository: `abdalrhmanata-gif/nexo-w21-isolated-verification-20261015`
- Branch: `codex/w80-forward-correction-20261015`
- Project: `ZAVQERA Development`, ref `mrwmmbytcymqgwvcoywd`, region `eu-west-1`
- Pack: `supabase/tests/hosted_readonly_migration_effect_audit_queries.sql`
- Runner: `tools/supabase_readonly_migration_effect_audit.py`
- Tests: `tests/test_supabase_readonly_migration_effect_audit.py`
- Pack SHA-256 (LF-normalized): `7fbe8b65aeb75c446ca942277d0541de27de905e9b2172f304924e9029de6c62`
- All 10 fixed statements must begin with SELECT. The runner pins the digest, verifies the project identity before SQL and checks effective role/transaction guard before query 2.
- Only `POST /v1/projects/{ref}/database/query/read-only` is allowed for SQL. The normal SQL endpoint is never used.
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

## After collection

The next step is to merge the supplemental output with the first audit capture and source hashes into an effect matrix marked MATCH / DIFFERENT / NOT OBSERVED / UNKNOWN. A database/platform owner must independently review all unexpected privilege paths, function owners/modes, search paths, relation ACLs and default ACL policy.

No hosted remediation is authorized by this runbook. Do not run `supabase db push`, `migration repair`, manually edit `supabase_migrations.schema_migrations`, replay migrations against hosted Development, or change Supabase Main/Production. Any future hosted migration requires a separate reviewed plan and explicit owner authorization.

**Release remains NO-GO.** Keep PR #39 open/Draft/unmerged, Issue #23 open, and `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed.

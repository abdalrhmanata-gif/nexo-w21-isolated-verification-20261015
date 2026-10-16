# ZAVQERA — Supplemental Hosted Migration-Effect Audit Runbook (2026-10-15)

**Current status — 2026-10-16: REVIEW REQUIRED / NO-GO.** The supplied hosted evidence archive is an older 12-query capture and has no `query_13.json`. This branch contains the pinned 12-query base pack plus a separate, SHA-256-pinned SELECT-only ACL-provenance query 13 and the secure Windows capture wrapper. The isolated tests pass, but **no fresh hosted 13-query capture has been recorded**. The old capture must not be treated as evidence about inherited `INHERIT` / `SET ROLE` paths. The W86 candidate and offline reviewer were also strengthened to block the case where `service_role` is the table owner or can obtain owner authority through either `INHERIT` or `SET ROLE`, even when ordinary owner ACL rows are absent. Query 13 already returns the table owner and membership paths needed for that review. This runbook performs read-only metadata collection only; it never authorizes hosted changes or release.

## Repository and safety scope

- Repository: `abdalrhmanata-gif/nexo-w21-isolated-verification-20261015`
- Audit branch: `codex/migration-ledger-provenance-20261015` (older instructions on the W80 branch are superseded).
- Project: `ZAVQERA Development`, ref `mrwmmbytcymqgwvcoywd`, region `eu-west-1`
- Pack: `supabase/tests/hosted_readonly_migration_effect_audit_queries.sql`
- Runner: `tools/supabase_readonly_migration_effect_audit.py`
- Tests: `tests/test_supabase_readonly_migration_effect_audit.py`
- Base pack SHA-256 (12 SELECT statements): `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`
- Query 13 SHA-256 (role-path ACL provenance): `f9f56944ddd04dd135329ff930cf5259e215eb89f30784b75e03a93f221ff38e`
- The current runner executes 13 fixed SELECT statements. It pins both hashes, validates the target project before SQL, and requires the effective session to be `supabase_read_only_user` in a read-only transaction before accepting evidence.
- Only `POST /v1/projects/{ref}/database/query/read-only` is allowed for SQL. The normal SQL endpoint is never used.
- The observed read-only role has `rolbypassrls=true`; the pack is limited to catalog/ledger metadata. Do not add application-row queries.
- Never set the query target to Main/Production; never send a PAT through ChatGPT, GitHub, a file, command-line argument, or shell history.

## Current Windows PowerShell procedure — use only this procedure

The earlier inline-token procedure in the historical version of this runbook is superseded. Use the secure wrapper below; do not run the capture by manually placing the token in an environment variable, command argument, script, or chat.

From the isolated repository root:

```powershell
git fetch origin codex/migration-ledger-provenance-20261015
git switch codex/migration-ledger-provenance-20261015
git pull --ff-only origin codex/migration-ledger-provenance-20261015
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\run_zavqera_readonly_effect_audit.ps1
```

The wrapper runs the self-test before prompting, collects the scoped Development-only token using hidden SecureString input, executes the pinned 13-query read-only endpoint, clears its temporary token state, and runs the offline reviewer without inheriting the token. It creates a ZIP for evidence. Upload **only the ZIP**; never paste or upload a token.

If the token or local checkout is unavailable, stop. Do not substitute the normal Supabase SQL endpoint, make up query 13, or infer role-path results from the old capture. There is no hosted-write authorization in this workflow.

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
13. Relation owner identity, reachable role-membership paths and inherited table/column ACL provenance for `service_role`; covers `INHERIT`, `SET ROLE`, the `authenticated` future-grant target, and reachable table-owner authority.

## After collection

After a fresh 13-query capture, manually match ledger tuples to source files and classify the W66 effective/stored ACLs; also review `relation.owner_role`, any path from `service_role` to `authenticated`, and any path from `service_role` to the table owner with either `INHERIT` or `SET ROLE` enabled. A table-owner path or inherited ACL blocks W86 as-is. Existing isolated PostgreSQL 17/CI success validates the code pack only; it is not a substitute for hosted Development evidence. Do not assume the ledger row count until the new capture is reviewed. A database/platform owner must independently review all unexpected privilege paths, function owners/modes, search paths, relation ACLs and default ACL policy.

No hosted remediation is authorized by this runbook. Do not run `supabase db push`, `migration repair`, manually edit `supabase_migrations.schema_migrations`, replay migrations against hosted Development, or change Supabase Main/Production. Any future hosted migration requires a separate reviewed plan and explicit owner authorization.

**Release remains NO-GO.** Keep PR #39 open/Draft/unmerged, Issue #23 open, and `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed.


## Historical 12-query offline comparison — obsolete, not a current procedure

This section records the original 12-query workflow for context only. Do **not** run the old command below against a current evidence folder: the current reviewer requires `query_13.json` and will reject an archive containing only query 11/12.

For a new capture, use **Current authoritative capture procedure — 13 queries** near the end of this runbook. The secure wrapper invokes the offline reviewer against the newly created 13-query evidence folder automatically. The reviewer is offline-only, always reports REVIEW REQUIRED / NO-GO, and cannot authorize hosted writes.


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
- Query 13, supabase/tests/hosted_readonly_w86_acl_provenance_query.sql, SHA-256: f9f56944ddd04dd135329ff930cf5259e215eb89f30784b75e03a93f221ff38e

Use the secure wrapper in the **Current authoritative capture procedure — 13 queries** section below; it performs the no-network self-test before prompting. For a manual self-test without any token or network, run `py -3 tools/supabase_readonly_migration_effect_audit.py --self-test` from the audit repository root.

Expected self-test output: SELF_TEST=PASS; queries=13; base_sha256=a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284; acl_provenance_sha256=f9f56944ddd04dd135329ff930cf5259e215eb89f30784b75e03a93f221ff38e; no network requests.

Then run the current secure PowerShell wrapper below using the verified Development project ref and scoped read-only Management API token locally. Do not recreate the older inline-token instructions. The runner verifies both SQL hashes, validates project identity and the read-only role before proceeding, sends only Management API database/query/read-only requests, saves query outputs 01–13, and never saves or prints the token. Do not paste a token into chat. Inspect the evidence ZIP for secrets before uploading it.

After capture, run the offline reviewer against the new evidence folder with: py -3 tools/review_hosted_migration_ledger.py --evidence-dir <new-evidence-folder>

The reviewer now requires query_13.json and the exact ACL provenance query hash. Review service_role_inherited_table_acl_rows, service_role_inherited_column_acl_rows, and the role-path entries in ledger_acl_review.json/.md. Any inherited ACL entry blocks the current W86 candidate; do not apply W86 as-is if one is present. The report remains REVIEW REQUIRED / NO-GO regardless of zero inherited rows.

## Verified local runner and query smoke — 2026-10-16

The 13-query runner, offline reviewer, and ACL provenance SQL passed W80 isolated PostgreSQL 17 validation on run 38858063330, source SHA f4d7fed423739db0d39ba576ca455c5d4a182169. Evidence artifact 12027554468, ZIP SHA-256 8147e0b3624b27bdd6dc83f566b665a8942a1b3aac3e3dd785de1a3fc45a483d; cleanup was verified. Flutter CI passed on the same SHA in run 38858068979. This is local/disposable validation only; a new hosted capture is still outstanding.


## Recommended Windows PowerShell helper

From the isolated audit repository root, run: `.\tools\run_zavqera_readonly_effect_audit.ps1`.

The helper first runs the no-network self-test, then prompts for the scoped token using hidden SecureString input, runs the pinned 13-query read-only capture, invokes the offline reviewer against the same checkout, and zips the evidence. It removes the token from the process environment and clears the temporary BSTR in a finally block. It performs no migrations or hosted writes. If the capture stops at a gate, it preserves partial evidence and reports the blocked stage; do not weaken the gate or change the SQL to make it pass.


## Secure PowerShell wrapper validation — 2026-10-16

The PowerShell helper is now covered by a static regression test. It requests the scoped token through hidden SecureString input, clears the token environment variable and temporary BSTR immediately after the read-only capture, then launches the offline reviewer without inheriting the token. It also zips successful evidence and preserves partial evidence if a read-only gate stops the capture.

Latest exact-SHA validation: W80 isolated PostgreSQL 17 run 38858755502 — SUCCESS on c6fae906f9f57efe11ec7f010afb48b66ac850dc. The run reported 8 catalog-runner tests, 12 migration-effect runner/wrapper tests, and 10 offline-reviewer tests passing; self-test reported 13 queries with both pinned hashes and no network requests; the 13th query passed local PostgreSQL 17 smoke; full migration replay and cleanup verification passed. Artifact 12028448084, ZIP SHA-256 c7388aaa1d1ef85c9c70951db1c3c33cc46da376c2c7e0b1ebcd1e33aafd38f3. Flutter CI also passed on the same SHA: run 38858755489.

This is local/disposable evidence only. The next required action is a fresh 13-query capture against the verified read-only Development session; do not paste the token into chat or apply any hosted repair.


## Current authoritative capture procedure — 13 queries (supersedes earlier 12-query steps)

The older instructions above describe the 12-query runner. For the next capture, use this section and the secure wrapper only.

### 1. Update the isolated audit checkout

From the root of the **isolated verification repository** (not the original `Nexo` repo), run:

```powershell
git fetch origin codex/migration-ledger-provenance-20261015
git switch codex/migration-ledger-provenance-20261015
git pull --ff-only origin codex/migration-ledger-provenance-20261015
```

Do not merge this branch into the original application repository. It remains an isolated audit/review branch.

### 2. Run the local tests first — no hosted requests

```powershell
py -3 tools/supabase_readonly_migration_effect_audit.py --self-test
if ($LASTEXITCODE -ne 0) { throw "Self-test failed; do not connect." }

py -3 -m unittest discover -s tests -p "test_supabase_readonly_migration_effect_audit.py" -v
if ($LASTEXITCODE -ne 0) { throw "Runner tests failed; do not connect." }

py -3 -m unittest discover -s tests -p "test_review_hosted_migration_ledger.py" -v
if ($LASTEXITCODE -ne 0) { throw "Offline reviewer tests failed; do not connect." }
```

The self-test must identify **13 SELECT-only queries** and these pinned SHA-256 values:
- Base query pack (queries 1–12): `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`
- Query 13 inherited-ACL provenance: `f9f56944ddd04dd135329ff930cf5259e215eb89f30784b75e03a93f221ff38e`

If any command fails, stop. Do not edit the query pack, bypass a gate, or use the unrestricted SQL endpoint.

### 3. Run the secure wrapper

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\\tools\\run_zavqera_readonly_effect_audit.ps1
```

The wrapper re-runs the pinned self-test before prompting for the token. Enter only a scoped Management API PAT for **ZAVQERA Development** using the hidden prompt. The token is not an argument, is not printed, and is removed from the process environment immediately after capture; the temporary BSTR is zeroed. Never paste the token into ChatGPT, a GitHub issue/PR, a file, or shell history. Do not target Main/Production.

The wrapper runs the capture and then the offline ledger reviewer, zips the evidence directory, and prints the ZIP path. A blocked/failed capture still means stop and review the captured stage; never retry by relaxing the role gate or changing SQL.

### 4. Upload only the generated evidence ZIP

Upload the resulting `zavqera-readonly-effect-audit-output-<timestamp>.zip` to the project conversation. Do not upload the source checkout, shell history, credentials, config files, or unrelated files. Do not rename a prior 12-query ZIP to make it appear current.

The ZIP must contain `query_13.json` and metadata identifying both query-pack hashes. The offline reviewer must report its normal **REVIEW REQUIRED / NO-GO** status until all migration-history and ACL findings are resolved.

### 5. Mandatory W86 interpretation

- If query 13 reports any parent-role table/column ACL path reachable by `INHERIT` or `SET ROLE`, **W86 must not be applied as-is**. Preserve the evidence and request an owner-reviewed least-privilege decision for that role path.
- If query 13 reports no parent-role ACL reachable via `INHERIT` or `SET ROLE`, that only removes this specific blocker. Direct/stored grants, owner/grantor context, historical migration provenance, and all previously recorded schema/function mismatches still require review.
- The capture is read-only evidence, not permission to apply a migration. Do not perform hosted DDL, ACL changes, migration repair, deployment, or secret changes.

No hosted change is authorized by this procedure. Keep release **NO-GO** and the provider dispatch registry empty/fail-closed.

## Query 13 direct-vs-parent ACL scope correction — 2026-10-16

The pinned ACL provenance query was corrected so `service_role_inherited_table_acl_entries` and `service_role_inherited_column_acl_entries` contain only reachable parent roles (`depth > 0`) with an all-`INHERIT` or all-`SET ROLE` path. Each inherited table/column ACL record now carries both `all_membership_edges_inherit` and `all_membership_edges_set_role`, so the reviewer can distinguish the two reachability modes per grant. Direct `service_role` ACLs remain separately reported by the effective privilege map, `table_acl_entries`, and `column_acl_entries`; they must not be mislabeled as inherited grants.

- Query 13 SHA-256: `f9f56944ddd04dd135329ff930cf5259e215eb89f30784b75e03a93f221ff38e`.
- Offline reviewer and self-test pin this hash, and a regression test asserts that depth-zero direct ACLs are excluded from parent-role result arrays.
- The previously uploaded hosted evidence ZIP contains 12 queries and is not evidence for this corrected 13-query probe. No fresh hosted capture is recorded here. No hosted write is authorized; historical migration provenance and independent owner approval remain required.

## Latest exact-SHA audit runner proof — 2026-10-16

**Validated code/test SHA:** `438dc482863468798bfe1a108fcb1d9b7e836ac2`. Subsequent changes on this audit branch are documentation/PR metadata only.

- Query 13 SHA-256: `f9f56944ddd04dd135329ff930cf5259e215eb89f30784b75e03a93f221ff38e`. The 12-query base pack remains `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`.
- Parent-role ACL arrays include only `membership_depth > 0`; each parent table/column grant records both `all_membership_edges_inherit` and `all_membership_edges_set_role`. Direct role ACLs remain in the separate direct/effective result fields.
- W80/PostgreSQL 17.11: [run 38878829978](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38878829978) — **SUCCESS**. Flutter CI: [run 38878829957](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38878829957) — **SUCCESS** on the same SHA.
- Tests: catalog runner 8/8; read-only migration-effect runner and PowerShell wrapper 13/13; offline ledger/ACL reviewer 13/13. Self-test: `queries=13`, both pinned hashes, no network requests.
- Disposable database: 89 checked-in migration files replayed with only the documented local compatibility fixture; W44 17/17, W46 8/8, W80 49/49 before/after W83 reapply, W84 21/21 before/after reapply, W85 12/12; query13 local smoke passed and cleanup verified.
- Evidence artifact [12036577429](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38878829978/artifacts/12036577429), digest `sha256:bdc92bfda664dfaca535f475c4666ca042ffed52622dd1754d40a946324817bc`.

**Still blocked on fresh hosted evidence:** the supplied evidence ZIP has only 12 queries; this run is local/disposable and is not a hosted capture. Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\\tools\\run_zavqera_readonly_effect_audit.ps1` locally from the isolated repository checkout on `codex/migration-ledger-provenance-20261015`, using the hidden prompt for a scoped Development-only read-only token. Do not paste or upload the token; upload only the resulting evidence ZIP containing `query_13.json`. The reviewer never authorizes hosted writes (`hosted_write_authorized=false`), even if no parent-role ACL is observed. Historical migration SQL provenance and independent owner authorization remain required. No hosted write, migration repair, deployment, secret, billing, or DNS change was performed; release remains **NO-GO**.


## Additional W86 future-grant guard — 2026-10-16

W86 does not merely revoke the currently observed direct grants: after preflight it grants SELECT to `authenticated`. Therefore the reviewer must treat a reachable membership path from `service_role` to `authenticated` as an independent blocker when any path is reachable through all-INHERIT edges or all-SET ROLE edges, even if query 13 reports zero inherited table/column ACL rows. This specific case is now enforced in the W86 candidate and the offline reviewer.

- W86 PostgreSQL 17.11 disposable negative control: [W80 run 38889778593](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38889778593), exact code/test/workflow SHA `a94d104f71a4a6ba57233b92ba797b96aa7f3120`; expected fail-closed exit 3, no-mutation check passed, W86 21/21 after fixture cleanup, cleanup verified.
- Audit reviewer regression: [W80 run 38889843683](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38889843683), SHA `35342455b968bc72f964ce28df15049e364e0bad`; 14 offline reviewer tests passed, including the case of an authenticated parent path without any parent ACL rows.

This only strengthens the isolated candidate and offline report. If query 13 shows any inherited parent ACL, or any reachable service_role-to-authenticated path, do not apply W86 as-is. If neither is present, hosted writes still remain unauthorized until historical migration SQL provenance and an independent owner review/explicit authorization are complete. Hosted release remains **NO-GO**.


## Cross-query W66/W86 evidence consistency gate — 2026-10-16

The current capture runner and offline reviewer cross-check the two pinned read-only result sets before accepting the evidence for manual review:

- Query 12 must contain the complete, unique effective privilege matrix for `anon`, `authenticated`, `service_role`, and `postgres`, and every privilege result must have the expected boolean shape and relation metadata.
- Query 13 must identify `public.agent_executions`, the same owner role and RLS flags, and exactly typed booleans for the eight `service_role_effective_privileges` entries.
- The eight effective `service_role` privilege booleans in query 12 must equal the query-13 summary. Any disagreement blocks the capture/review; it is not safe to choose whichever query appears more plausible.
- Every inherited table/column ACL row must also match a concrete membership-path tuple with role name, exact integer depth, `INHERIT`, and `SET ROLE` flags. Owner-authority paths and paths to `authenticated` remain independent W86 blockers.

The two queries are separate read-only API requests, not a single atomic catalog snapshot. Consistency checks catch malformed or contradictory responses but do **not** prove transaction-level snapshot identity, deployed historical SQL equality, or authorize hosted changes. A fresh Development-only 13-query capture, manual migration-source reconciliation, independent database-owner review, and separate authorization remain mandatory. Release stays **NO-GO**.

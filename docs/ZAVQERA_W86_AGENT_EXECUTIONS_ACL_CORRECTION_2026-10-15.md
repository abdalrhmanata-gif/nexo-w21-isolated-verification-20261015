# ZAVQERA W86 — Forward-only agent execution ACL correction candidate

**Disposition: ISOLATED CANDIDATE ONLY / HOSTED RELEASE NO-GO**

Date: 2026-10-15  
Base evidence commit: `b0068d7f677c56fb45f9752b3679497159eabd93`  
Target evidence: 12-query read-only capture, ZIP SHA-256 `fff6f88aca42c73dc691ead099e969f3cfc911fea5504ce1291b6e04ae0320f6`  
Hosted project observed: ZAVQERA Development, `mrwmmbytcymqgwvcoywd`, PostgreSQL 17.6  
Candidate migration: `supabase/migrations/20261015120000_w86_agent_executions_acl_correction.sql`

## 1. Why this candidate exists

The 2026-10-15 read-only capture showed `service_role` has effective `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`, `TRIGGER`, and PostgreSQL 17 `MAINTAIN` on `public.agent_executions`. The stored table ACL separately showed entries for all eight privileges granted to `service_role` by `postgres`.

That contradicts the stated intent of both W65 and W66: authenticated users retain RLS-governed history reads, but mutations and execution state transitions must pass through guarded RPCs; `service_role` is not granted direct table access.

The hosted migration history is not reconciled (89 checked-in migration files versus 74 ledger rows, 46 exact version/name matches, 22 same-name timestamp conflicts, and 6 hosted-only names absent from the current source tree). This candidate therefore does not assert how the drift arose and is not authorization to alter the hosted project.

## 2. Proposed forward correction

W86 intentionally repeats the desired final ACL, not W66's historical application event:

1. Revoke all table-level privileges from `PUBLIC`, `anon`, `authenticated`, and `service_role`.
2. Revoke any column-level privileges from those same API principals. A table-level revoke by itself does not clear separate per-column grants.
3. Re-grant only table-level `SELECT` to `authenticated`, leaving RLS to govern row visibility.
4. Do not change any function EXECUTE grants. The public and private guarded completion RPCs are independently asserted to remain executable by `service_role`, while the public trusted wrapper remains unavailable to `anon` and `authenticated`.

The migration is designed to be idempotent on the expected schema. It fails if the table or required roles are absent rather than pretending the ACL is repaired. It must be reviewed with the actual `agent_executions` ownership and any column-ACL evidence before any hosted application.

## 3. Regression assertions

`supabase/tests/w86_agent_executions_acl_correction.sql` contains 20 pgTAP assertions for disposable PostgreSQL 17:

- All eight effective table privileges denied to `service_role`, including `MAINTAIN`.
- Effective column-level `SELECT`, `INSERT`, `UPDATE`, and `REFERENCES` denied to `service_role`.
- No stored table ACL entry for `PUBLIC` or `service_role`.
- `authenticated` retains SELECT, but has no table write/control privileges.
- `anon` has none of the checked table privileges.
- The intended guarded completion functions remain executable by `service_role`; neither `anon` nor `authenticated` can execute the public trusted completion wrapper.
- The existing W66 11-assertion test will also be rerun after W86 applies.

The isolated W80 workflow is extended to apply the full checked-in migration chain on a brand-new local Supabase/PostgreSQL 17 stack, run W66 and W86 tests after migration replay, preserve test evidence, and prove disposable-resource cleanup. A passing workflow demonstrates only isolated-source behavior, not hosted parity.

## 4. Boundaries and stop conditions

- Do not apply W86 to hosted Development or Main/Production as part of this change.
- Do not use `supabase db push`, migration repair, manual SQL on hosted, or edits to `supabase_migrations.schema_migrations`.
- Do not treat a W86 pass as a resolution of the 22 timestamp mismatches, the six hosted-only migrations, missing authority-budget schema, missing columns/constraints/indexes, legacy RPCs, W83/function grants, or W84 `supabase_admin` default ACL findings.
- Reconcile exact historical SQL provenance and repeat read-only catalog capture before any hosted plan.
- Any hosted write requires separate explicit owner approval after review of the whole migration range, deployment order, backup/recovery, and post-apply acceptance matrix.

## 5. Decision

**Candidate correction prepared for isolated testing only. Hosted release remains NO-GO.** Keep `TRUSTED_DISPATCH_ADAPTERS = Object.freeze({})` empty/fail-closed, original PR #39 open/Draft/unmerged, and original Issue #23 open. No hosted object, secret, deployment, billing setting, DNS record, or migration ledger has been changed.


## 6. Isolated PG17 verification complete — 2026-10-15

**Exact source/test/workflow SHA:** `8dbaa7cb27abbb15144f6b81f1bb8538dd2ce5be`  
**Workflow:** [W80 isolated PostgreSQL 17 pgTAP run 38790810307](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38790810307) — **SUCCESS**.  
**Flutter/Web validation:** [Flutter CI run 38790810387](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38790810387) — **SUCCESS**.

Verified from the uploaded evidence artifact (artifact ID `11999338335`, ZIP SHA-256 `906c3bf9035432cb26a3852969cb342dca23800718bf7bbc5cc7ebdac275a58f`):

- Complete checked-in migration replay exit code 0 on disposable PostgreSQL `170011` (PostgreSQL 17.11).
- W66 regression: 11/11 PASS before and after the W86 reapplication.
- W86 ACL regression: 20/20 PASS before and after the W86 reapplication.
- W86 reapplication exit code 0; output contains `REVOKE`, `DO`, `GRANT`.
- W84: 21/21 PASS before and after its reapplication.
- W85 `supabase_admin` diagnostic: 12/12 PASS.
- W44: 17/17 before and after W83 reapplication; W46: 8/8; W80: 49/49 before and after W83 reapplication.
- Both pinned read-only query packs passed the disposable PostgreSQL syntax/catalog smoke.
- Temporary Supabase stack stopped, no project containers or volumes remained: `cleanup=VERIFIED`.

The isolated verification PR is [#1 — W86 ACL boundary candidate](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/1), OPEN / DRAFT / UNMERGED. A later documentation-only commit may change the branch head; the exact tested code/workflow SHA remains the one above.

**Disposition unchanged:** these are disposable-environment results, not proof of hosted Development parity. No hosted write was made. Do not apply W86 until migration-history/source provenance is reconciled and separate owner approval is recorded. Original repository PR #39 stays OPEN/DRAFT/UNMERGED; Issue #23 stays OPEN; `TRUSTED_DISPATCH_ADAPTERS` remains empty/fail-closed; release remains NO-GO.

## 6. Verified isolated regression execution — 2026-10-15

**Tested workflow/source SHA:** `6a0795b0635a1063900192d92abca22580891199`  
**Migration blob:** `f870dd83a82c27057bf24390c254713d3fe29182`  
**W66 test blob:** `8a5c06feedc672f65ef26b9bf33461607d5b74c3`  
**W86 test blob:** `20cc2999f4e0a849e44d7ce977ceb9aee0b636d6`  
**W80 run:** https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38793355077 — SUCCESS.  
**Evidence artifact:** `12000544561`, `zavqera-w80-isolated-pgtap-6a0795b0635a1063900192d92abca22580891199`.

The workflow seeded deliberately permissive table privileges and a stored column-level ACL for `service_role` in the disposable PostgreSQL 17.11 database. Its fixture check returned `W86_DRIFT_FIXTURE_PASS`; then the W86 migration ran successfully (`REVOKE / DO / GRANT`). After repair, W66 passed 11/11 and W86 passed 20/20. W86 was reapplied again; W66 passed 11/11 and W86 passed 20/20 a second time.

Other gates on the same execution also passed: W84 21/21 before and after reapply, W85 12/12, W44 17/17 twice, W46 8/8 twice, W80 49/49 twice, migration replay through all checked-in SQL, and disposable-stack cleanup (`cleanup=VERIFIED`). PostgreSQL reported `server_version_num=170011` (17.11).

The artifact-packaging run also passed on workflow/source SHA `24af5583113e606bf8ec80f179cca0854073abac`: https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38793792365. It includes the raw W66/W86 drift-repair test-output files. Final artifact ID `12000309494`; ZIP SHA-256 `669bc1f5e29424c00736cb1c24b257c638abc45d238bd7331b4096316746a2d2`. The evidence file records `W86_DRIFT_FIXTURE_PASS`, repair and reapply exit code 0, W66 11/11 and W86 20/20 after both repair and reapply, full-chain migration replay, other regression counts, and cleanup `VERIFIED`.

**Scope limit:** This evidence proves the correction against a deliberately seeded ACL drift in disposable PostgreSQL only. It does not prove hosted Development has been changed or reconciled, and it does not resolve the historic migration-ledger conflicts or other missing hosted schema/function contracts.



## Verification addendum — injected ACL-drift negative control (2026-10-15)

A follow-up isolated workflow now proves active repair, rather than only asserting the already-hardened post-migration state:

1. After the complete candidate migration chain runs on a brand-new local Supabase/PostgreSQL 17 stack, it injects the specific privilege drift **into the disposable database only**: all table privileges for `service_role`, plus a column-level grant on one real `agent_executions` column.
2. A pre-repair catalog assertion must return `W86_DRIFT_FIXTURE_PASS`, proving that effective INSERT/UPDATE/DELETE/TRUNCATE/MAINTAIN and stored column-level grants were recreated. If this seed/check fails, CI stops.
3. The workflow applies the W86 SQL a second time to that simulated drift state. It then runs W66 (11 assertions) and W86 (20 assertions); both pass.
4. It reapplies W86 once more and runs both test suites again. W66 is 11/11 and W86 is 20/20 a second time. The SQL replay exit codes are zero and disposable cleanup is verified, with no containers or volumes left.

Evidence:
- W80 isolated PostgreSQL 17 run [38793355077](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38793355077) — **SUCCESS** on source/workflow commit `6a0795b0635a1063900192d92abca22580891199`.
- Artifact `12000544561`, ZIP digest `sha256:b11c8228c7f771c4513081a8a778e4728319b99e3f0381d65ba07c9584b9c2b4`.
- Verified artifact evidence: `w86_drift_fixture_check_exit_code=0`; file output exactly `W86_DRIFT_FIXTURE_PASS`; `w86_drift_repair_exit_code=0`; W66/W86 each passed after repair and after reapply; `cleanup=VERIFIED`.

The final W80 workflow run on commit `24af5583113e606bf8ec80f179cca0854073abac` is [run 38793792365](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38793792365) — **SUCCESS**. Latest artifact `12000309494`, ZIP digest `sha256:669bc1f5e29424c00736cb1c24b257c638abc45d238bd7331b4096316746a2d2`, includes the two drift-repair pgTAP log files. Evidence from that exact run confirms PostgreSQL 17 migration replay PASS; simulated drift seed/check PASS; W86 repair and reapply exit codes 0; W66 11/11 and W86 20/20 both after repair and after reapply; W84 21/21 before/after reapply; W85 12/12; W44 17/17, W46 8/8, W80 49/49 before/after W83 reapply; read-only pack smoke PASS; and cleanup `VERIFIED`.

The negative control is still **disposable/local-only**. It reproduces the ACL state and corrects it on a local stack; it is not a hosted repair. The original hosted Development remains unmodified and release remains NO-GO.



## Verification addendum — inherited-role fail-closed guard (2026-10-16)

The W86 candidate now performs a recursive role-membership/ACL preflight **before any REVOKE or GRANT**. It has no arbitrary depth cutoff; cycle detection prevents repeated role traversal. If a parent role has table-level or column-level ACL entries reachable through either automatic `INHERIT` or a `SET ROLE` membership path, the migration raises an explicit exception before changing ACLs. This is intentionally fail-closed: revoking direct grants from `service_role` cannot remove privileges available through a parent role.

The disposable W80 workflow deliberately seeded `w86_acl_probe_parent`, granted it to `service_role WITH INHERIT FALSE, SET TRUE`, then granted table UPDATE and column SELECT. The read-only provenance query correctly returned `W86_ACL_PROVENANCE_SET_ROLE_ACL_PASS`; effective `service_role` UPDATE was false, but the parent-role ACL path remained available via `SET ROLE`. W86 exited nonzero with the expected message before any REVOKE or GRANT:
`W86 refused: service_role can obtain agent_executions privileges via parent roles (INHERIT or SET ROLE): column id SELECT via role w86_acl_probe_parent; table UPDATE via role w86_acl_probe_parent`.
The workflow verified this was an expected guard rejection, removed the disposable role fixture, reapplied W86 successfully, and reran the W66/W86 tests.

**Latest full local PostgreSQL 17.11 evidence:**
- W80 isolated PostgreSQL 17 run [38857452731](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38857452731) — **SUCCESS**, source/workflow SHA `687189c05773318e6ca9e4475eda7cf96b185d3d`.
- Evidence artifact ID `12027962020`, ZIP SHA-256 `503add2e33ae0fff000c02b8c2953b716be0cd3b48a0cd9246116607da21b352`.
- Expected inherited-ACL guard failure exit code: 3; marker `W86_INHERITED_ACL_GUARD_PASS`; role-fixture cleanup exit code 0; W86 reapply exit code 0.
- W66 11/11 and W86 20/20 after seeded direct/column drift repair, after W86 reapply, and again after inherited-role fixture cleanup.
- W84 21/21 before/after reapply; W85 12/12; W44 17/17; W46 8/8; W80 49/49; full migration replay passed; read-only query packs passed; cleanup `VERIFIED`.
- Flutter CI on the same source/workflow SHA also passed: [run 38857457330](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38857457330).

This proves fail-closed handling in the disposable stack only. **Before any hosted repair is even proposed**, the new read-only ACL provenance query must be captured against Development and reviewed. If it reports any inherited table/column ACLs, W86 must not be applied as-is; the source role/grant and least-privilege resolution need independent owner review. Historical migration provenance remains unresolved. No hosted database write was performed, and release remains **NO-GO**.


## Hosted evidence gate updated — 2026-10-16

The current capture procedure is documented in [the 13-query audit runbook](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/migration-ledger-provenance-20261015/docs/ZAVQERA_HOSTED_MIGRATION_EFFECT_AUDIT_RUNBOOK_2026-10-15.md) and implemented in [audit PR #2](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2). Query 13 is pinned at SHA-256 `700939087d9708fc3d6a72ebe10064b4c0db7f5d26b08556c7e641e1aa09a919`; it records service_role membership paths and inherited table/column ACLs. Local W80 validation passed on `f4d7fed423739db0d39ba576ca455c5d4a182169`, but the old hosted ZIP remains 12-query evidence. A fresh 13-query capture under the verified read-only Development session is still required. No hosted repair is authorized by these tests.


### SET ROLE-only negative control — 2026-10-16

- W80 isolated PostgreSQL 17 run [38865144782](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38865144782) — **SUCCESS** on candidate/workflow SHA `a5f899ffff202eb0eda7954cec9ad12d82d252dc`.
- Artifact [12031370300](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38865144782/artifacts/12031370300), SHA-256 `8bccecd95878f0fa56309b01f0118d7f19fdc9eccbbdb5180ed5947f9775bc98`.
- Membership fixture used `INHERIT FALSE, SET TRUE`. Query 13 observed `all_edges_inherit=false`, `all_edges_set_role=true`; the JSON assertion returned `W86_ACL_PROVENANCE_SET_ROLE_ACL_PASS`.
- The migration's guard rejected the parent-role ACL path before ACL mutation (expected exit code 3). The disposable role was removed, W86 then reapplied successfully, and W66 11/11 plus W86 20/20 passed after cleanup. Full chain, W84/W85/W44/W46/W80 tests, read-only query smoke, and disposable cleanup also passed.
- Flutter CI: [run 38865152105](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38865152105) — **SUCCESS**.

The hosted query 13 now also reports whether each membership path supports `SET ROLE`. Updated query digest in the audit branch: `700939087d9708fc3d6a72ebe10064b4c0db7f5d26b08556c7e641e1aa09a919`. The old hosted evidence remains a 12-query capture; a fresh 13-query capture is still mandatory.


## Additional fail-closed guard: migration-created authenticated SELECT path — 2026-10-16

A further code review found that checking only currently existing inherited ACL rows was insufficient for one edge case: W86 itself grants table SELECT to `authenticated` after its preflight. If `service_role` can reach `authenticated` through an `INHERIT` or `SET ROLE` path while `authenticated` currently has no ACL entry, the migration's own grant could create a new access path after the check.

The candidate now fails closed **before any ACL mutation** whenever such a path to `authenticated` exists, even if the parent currently has no table/column ACL row. The regression suite includes a new 21st assertion that successful W86 state has no reachable `authenticated` parent path. The isolated W80 workflow seeds the edge `GRANT authenticated TO service_role WITH INHERIT FALSE, SET TRUE` with authenticated table/column privileges first revoked, requires W86 to stop before changing ACLs, checks that authenticated SELECT remains absent, then removes the fixture and re-applies W86.

### Exact-SHA verification — PASS

- Source/test/workflow SHA: `a94d104f71a4a6ba57233b92ba797b96aa7f3120`.
- W80 PostgreSQL 17.11: [run 38889778593](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38889778593) — **SUCCESS**.
- Evidence artifact [12041540640](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38889778593/artifacts/12041540640), ZIP SHA-256 `2601c4c5a01a9120bd646875b42da8c2395cf241b3e130a202012e21b9923ee6`.
- Expected W86 guard rejection exit code 3; marker `W86_AUTHENTICATED_PARENT_GUARD_PASS`; no-mutation marker `W86_AUTHENTICATED_PARENT_NO_MUTATION_PASS`; fixture cleanup exit code 0; W86 reapply exit code 0.
- After cleanup/reapply: W66 11/11 and W86 21/21; W84 21/21; W85 12/12; W44 17/17; W46 8/8; W80 49/49; full checked-in migration replay passed; disposable cleanup `VERIFIED`.
- Flutter CI: [run 38889786282](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38889786282) — **SUCCESS** on the same SHA.

This remains disposable/local verification only. It is not evidence of hosted Development parity or permission to apply W86. Fresh 13-query Development evidence, historical SQL provenance reconciliation, independent owner review, and separate explicit authorization remain mandatory. Hosted release remains **NO-GO**.

## Additional fail-closed guard — relation owner role path (2026-10-16)

Static review identified a case where revoking ACL entries is not enough: `service_role` must not itself own `public.agent_executions` or be able to `SET ROLE` to its owner. Ownership authority can restore grants even if ordinary ACL rows are empty. W86 now checks the relation's actual owner against every reachable service-role membership path and refuses before any ACL mutation when the owner is the root role or a parent role reachable via `SET ROLE`.

The isolated W80 workflow now includes a disposable negative control that transfers table ownership to a temporary role, removes that role's table/column ACL rows, grants `SET ROLE` membership to `service_role`, and expects W86 to reject the migration while proving the subsequent `authenticated SELECT` grant was not applied. The fixture is cleaned up and W66/W86 tests are rerun afterward. Validation of this new guard is pending the workflow result; do not treat this addendum as a pass claim.

Release remains **NO-GO**. No hosted database was changed, and the W86 candidate remains unmerged.

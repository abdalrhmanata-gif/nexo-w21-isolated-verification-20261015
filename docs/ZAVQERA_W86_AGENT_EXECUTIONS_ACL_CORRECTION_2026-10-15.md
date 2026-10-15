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

A later workflow-only commit `24af5583113e606bf8ec80f179cca0854073abac` adds the raw W66/W86 drift-repair test-output files to the artifact list. Its rerun is separately tracked; it does not change the W86 SQL or the test assertions. Do not state that the later artifact-packaging rerun passed until its own action run completes.

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

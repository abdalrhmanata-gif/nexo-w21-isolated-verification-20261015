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

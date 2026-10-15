# ZAVQERA — Hosted 12-Query Migration and W66 ACL Audit Review

**Disposition: REVIEW REQUIRED / RELEASE NO-GO.** This report reviews the fresh 12-query read-only capture from ZAVQERA Development. It does not authorize migrations or certify production security.

## Evidence identity and scope

- Captured UTC: `2026-10-15T18:45:25.121761+00:00`.
- Project: `ZAVQERA Development`; ref `mrwmmbytcymqgwvcoywd`; region `eu-west-1`; status `ACTIVE_HEALTHY`.
- PostgreSQL server_version_num: `170006` (PostgreSQL 17.6).
- Query-pack SHA-256: `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`.
- Uploaded ZIP SHA-256: `fff6f88aca42c73dc691ead099e969f3cfc911fea5504ce1291b6e04ae0320f6`.
- Status `CAPTURED_FOR_MANUAL_REVIEW`; all 12 queries returned; read-only role gate PASS; token not saved.
- Effective/session role: `supabase_read_only_user`; `transaction_read_only=true`; not superuser and cannot create databases or roles. **`rolbypassrls=true`**; retain this audit scope as catalog/ledger metadata only. No application rows were queried, and no write/migration/deployment occurred.
- The offline comparator reports against 89 checked-in migration files. The emitted evidence does not itself record the source Git HEAD used by the local comparator; treat source hashes and filename comparisons as tied to the checkout used during that comparison.

## Executive findings

### 1. Migration ledger does not match current source filenames

| Measure | Observed |
|---|---:|
| Source migration files | 89 |
| Hosted ledger rows | 74 |
| Exact `version + name` matches | 46 |
| Same-name, different-version candidates | 22 |
| Source tuples absent from exact hosted ledger | 43 |
| Hosted tuples absent from exact source | 28 |
| Source names absent by exact name | 21 |
| Hosted names absent by exact name | 6 |

The count arithmetic is internally consistent: 46 exact tuples + 43 source-only tuples = 89 source files; 46 exact tuples + 28 hosted-only tuples = 74 ledger rows. The 22 timestamp conflicts are represented as non-exact tuples on both sides. A same-name candidate is **not proof that deployed SQL equals the checked-in SQL**; the ledger stores version/name metadata, not migration bytes.

The 22 conflicting names are recorded in the historical reconciliation document. The six hosted ledger names without a matching current source file are:

- `20261007105825_expose_anonymous_ai_guard_rpc`
- `20261005053351_w35_plan_ai_allowances_5_50_300`
- `20261008150359_w44_workspace_invitations_and_activity`
- `20261008161103_w46_invitation_activity_bindings`
- `20260921180227_w4_harden_profile_trigger_search_path`
- `20260924171437_w6_authoritative_mission_mutation_and_concurrency`

A search across all 23 current branch refs of the original `abdalrhmanata-gif/Nexo` repository found none of these six filenames in a branch-tip migration tree; exact-path commit-history queries also returned no entries. That does not rule out a deleted ref, external artifact, or local backup. Recover the exact historic SQL/verified artifact; do not reconstruct it from names.

### 2. Authority budgets and claim-bound execution schema are missing

- `public.mission_authority_budgets` and `public.mission_authority_budget_reservations` are absent.
- All 26 selected expected columns are absent.
- Ten of 11 selected constraints are absent. The existing `ai_usage_reservations_state_check` is not the candidate definition: it permits `reserved`, `consumed`, `released`, but does not include the candidate `unknown` state.
- All eight selected expected indexes are absent.
- The `agent_execution_success_receipt_guard` trigger and its guard function are absent.
- Of 40 tested function signatures, 23 fail the expected existence matrix: 19 expected signatures are absent and four forbidden legacy signatures remain.

The four legacy signatures still observed are `private/public.reserve_ai_generation(text)` and `private/public.complete_read_only_research_execution(uuid,text,jsonb,jsonb,text,text)`. Both one-argument reservation variants report effective EXECUTE for `authenticated` and `service_role`; the public legacy research completion variant reports effective EXECUTE for both as well.

### 3. W66 direct table privilege hardening is not reflected

The source migration `20261011160000_w66_service_role_table_privilege_hardening.sql` says to revoke **all privileges** on `public.agent_executions` from `service_role`, so state mutation must use guarded RPCs. The fresh query 12 explicitly measured 32 effective role/privilege combinations and 17 stored ACL entries. It shows:

- `service_role` has **all eight queried effective privileges** on `public.agent_executions`: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`, `TRIGGER`, and PostgreSQL 17 `MAINTAIN`.
- Stored ACL entries also explicitly include all eight privileges for `service_role`, granted by `postgres`.
- In particular, effective direct `INSERT`, `UPDATE`, `DELETE`, and `TRUNCATE` are true; this contradicts W66’s expected effect. Direct access can bypass the intended guarded execution boundary.
- `authenticated` has `SELECT`, consistent with the workspace-history read path; `anon` has none of the queried privileges.
- The table has RLS enabled but `FORCE ROW LEVEL SECURITY` is false. ACLs alone are not a full reachability proof, but they are sufficient to show the W66 revoke has not taken effect for `service_role`.

**Treat W66 as a critical hosted security blocker.** Do not apply a casual one-off revoke. First reconcile migration provenance/ownership, prepare a reviewed forward-only migration plan, test on disposable PostgreSQL 17 with the existing W66 pgTAP assertions and dependent runtime tests, then seek separate authorization for any hosted change.

### 4. Function security and default ACL drift persists

- `private.can_edit_workspace(uuid,uuid)` is SECURITY DEFINER but its configured search path is `public, private`, not the candidate `pg_catalog, public, private`. The captured body does not use the candidate’s `coalesce(..., false)` fail-closed return.
- `private` schema USAGE is effectively true for `authenticated` and `service_role`, false for `anon`; each helper’s EXECUTE and owner/security properties require per-function review.
- The `public.get_workspace_invitation(text)` security mode and invitation-wrapper service-role grants remain inconsistent with candidate W83 expectations.
- Explicit public-schema default function ACL entries for both creators `postgres` and `supabase_admin` still grant EXECUTE to `anon`, `authenticated`, and `service_role`. W84 hardens postgres-created defaults only; `supabase_admin` remains an owner-policy decision.

## Recommended disposition and sequence

1. Keep **NO-GO**. Leave `TRUSTED_DISPATCH_ADAPTERS = Object.freeze({})` empty/fail-closed; keep original PR #39 open/Draft/unmerged and Issue #23 open.
2. Preserve this ZIP and the earlier 10-query capture as immutable read-only evidence; record hashes and capture times.
3. Recover historical source provenance for the six hosted-only ledger names and resolve all 22 timestamp differences through SQL hash/full diff, not filename similarity.
4. Treat W66 direct `service_role` table grants as the first critical correction to plan. Build a forward-only candidate; do not edit `supabase_migrations.schema_migrations`, do not run `db push` or migration repair, and do not execute repair SQL on hosted Development.
5. Re-run W66/W83/W84, authority-budget, dispatch/reconciliation and guarded provider-boundary tests on disposable PostgreSQL 17. Have the platform/database owner review the W84 `supabase_admin` default ACL policy.
6. Only after separate review and explicit owner approval should a hosted maintenance plan be considered.

## Evidence files and related reports

- Uploaded capture ZIP SHA-256: `fff6f88aca42c73dc691ead099e969f3cfc911fea5504ce1291b6e04ae0320f6`.
- Query result 11 contains 74 `version,name` rows; result 12 contains 32 effective ACL rows and 17 stored ACL rows.
- Companion: `docs/ZAVQERA_HOSTED_MIGRATION_HISTORY_RECONCILIATION_2026-10-15.md`.
- Companion: `docs/ZAVQERA_HOSTED_CANDIDATE_EFFECT_MATRIX_2026-10-15.md`.
- The capture and this report do not certify provider idempotency, external-effect reconciliation, deployed egress enforcement, or production readiness.

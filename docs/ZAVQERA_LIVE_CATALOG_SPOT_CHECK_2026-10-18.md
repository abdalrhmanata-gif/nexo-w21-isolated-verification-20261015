# ZAVQERA Development — Live catalog spot-check (2026-10-18)

**Disposition: CURRENT DATABASE STILL NO-GO. No write or migration was performed.**

## Scope and method

At **2026-10-18 11:00:35 UTC**, the connected Supabase project was confirmed as:

- Project: ZAVQERA Development; ref `mrwmmbytcymqgwvcoywd`
- Region: `eu-west-1`
- Status: `ACTIVE_HEALTHY`
- Database: PostgreSQL 17.6 (`server_version_num=170006`; Supabase reported version 17.6.1.166)

I queried project metadata and migration inventory, listed public/private table metadata, read catalog ACLs and role memberships, checked selected routine signatures and grants, and retrieved Supabase security/performance advisors. The SQL submitted in this spot-check consisted of SELECT-only catalog queries; no application table rows were queried, and no INSERT, UPDATE, DELETE, DDL, migration, deployment, secret change or merge was attempted.

**Important limitation:** The Supabase MCP SQL session reported `current_user=postgres`, `session_user=postgres`, and `transaction_read_only=off`. Thus, although the statements I sent were SELECT-only, the session itself was not server-enforced read-only and is not the scoped audit-role capture. This is a supplemental spot-check, not a replacement for the pinned 13-query read-only audit procedure. The restricted read-only runner remains the method for future formal recapture.

## Live findings

### 1. Hosted migration ledger

- The database reports **74 migration rows**.
- The latest ledger entry remains **W65 — `20261011150000`**.
- The hosted ledger still contains the known differently-versioned entries, including W4 `20260921180138`, W6 `20260924171437`, and W30 reconstruction `20261004083051`.
- W66 (`20261011160000`) and later candidate migrations are not present in the current hosted migration list. This is a statement about the current ledger only; it does not, by itself, prove that a migration was never manually applied or later reverted.

### 2. Direct privileges on `public.agent_executions`

The live effective-privilege query returned:

| Role | SELECT | INSERT | UPDATE | DELETE | TRUNCATE | REFERENCES | TRIGGER | MAINTAIN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `anon` | no | no | no | no | no | no | no | no |
| `authenticated` | yes | no | no | no | no | no | no | no |
| `service_role` | **yes** | **yes** | **yes** | **yes** | **yes** | **yes** | **yes** | **yes** |

The stored table ACL confirms direct grants from `postgres` to `service_role` for all eight privileges; `authenticated` has direct SELECT, and the catalog query showed no separate column-specific ACL rows. Table metadata confirms owner `postgres`, RLS enabled, RLS not forced, and no user-defined trigger on this table. Specifically, `agent_execution_success_receipt_guard` is absent.

**Assessment:** The known direct privilege boundary problem still exists at the time of this live check. RLS being enabled does not remove a privileged service-role table grant. This finding supports keeping W86 as an isolated candidate for review, not applying it to Development.

### 3. Missing Mission Authority schema

The live table inventory again did not find:

- `public.mission_authority_budgets`
- `public.mission_authority_budget_reservations`

The existing `public.agent_executions` and `public.ai_usage_reservations` relations are present, but the new expected budget/dispatch/reconciliation structures remain inconsistent with the current candidate contract. The prior 13-query comparison reports 26 expected columns, 10 of 11 queried constraints, and all eight queried indexes absent relative to the candidate expectations. This spot-check independently reconfirmed the two missing relations, not every individual expected column/index.

### 4. Current legacy routine evidence

The current catalog query found these older overloads:

- `private.reserve_ai_generation(p_request_id text)`: owner `postgres`, SECURITY DEFINER, search path `pg_catalog, public`; EXECUTE effective for `authenticated` and `service_role`, not `anon`.
- `public.reserve_ai_generation(p_request_id text)`: owner `postgres`, SECURITY INVOKER; EXECUTE effective for `authenticated` and `service_role`, not `anon`.
- `private.complete_read_only_research_execution(p_execution_id uuid, p_status text, p_result jsonb, p_evidence jsonb, p_error_code text, p_error_message text)`: owner `postgres`, SECURITY DEFINER; EXECUTE effective for `authenticated`, not `anon` or `service_role`.
- `public.complete_read_only_research_execution` with the same six-argument identity: SECURITY INVOKER; EXECUTE effective for `authenticated` and `service_role`, not `anon`.

No new overloads under the queried reserve/claim/reconcile/budget routine names appeared in that result. This confirms the known overload/contract mismatch is not resolved. It does not, by itself, prove exploitability or justify dropping a function.

### 5. Schema usage and default ACLs

- Effective `private` schema USAGE: `anon=false`, `authenticated=true`, `service_role=true`.
- Effective `public` schema CREATE: false for `anon`, `authenticated`, and `service_role`.
- `pg_default_acl` still contains eight public-schema function EXECUTE rows across creator roles `postgres` and `supabase_admin`, including `anon`, `authenticated`, `postgres`, and `service_role`.

These settings require owner-approved least-privilege rationale and forward-looking function-creation tests; no ACL was changed.

### 6. Supabase advisors

- Security advisor: one warning, `auth_leaked_password_protection` — leaked-password protection is disabled. Remediation reference: https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection
- Performance advisor: 15 informational `unused_index` findings. Do not drop indexes solely on this observation; use an approved workload baseline and owner review.

## Decision and next action

The live catalog spot-check is materially consistent with the 2026-10-17 evidence. It does **not** clear any blocking gate:

1. Keep release **NO-GO** and `hosted_write_authorized=false`.
2. Do not apply W86 or any other migration, repair the hosted ledger manually, revoke routines, or change grants from this spot-check.
3. Complete a formal read-only capture through the pinned, scoped read-only runner if a fresh 13-query evidence bundle is needed; preserve its output and hashes.
4. Continue independent owner review and historical migration/deployment provenance recovery. The 22 version conflicts and six hosted-only entries remain unresolved without authoritative source and deployment evidence.
5. Before proposing hosted remediation, establish the intended release contract, test the exact full candidate migration range on disposable PostgreSQL, and document a verified backup/recovery and post-change acceptance plan.

`TRUSTED_DISPATCH_ADAPTERS` remains empty/fail-closed. PR #1 and PR #2 remain open/draft/unmerged. No hosted writes, migrations, deployment or secret changes were made by this review.


## Follow-up W86 role-path preflight spot-check — 2026-10-18

A second catalog-only SELECT reproduced the W86 recursive role-path logic for `service_role`, `anon`, `authenticated`, and the owner of `public.agent_executions`. The result at the time of the check was:

- Table owner: `postgres`.
- No reachable parent-role path reported from `service_role` under the candidate's INHERIT/SET ROLE reachability rule.
- No `service_role` path to `authenticated` or table owner was reported.
- No `anon` path to `authenticated` and no `anon`/`authenticated` path to table owner was reported.
- No inherited parent table/column ACL privilege rows were reported.
- Effective direct privileges remain: `service_role` SELECT=true and INSERT=true; `authenticated` SELECT=true; `anon` SELECT=false.

This clears only those role-path predicates at the instant of this supplemental spot-check. It does **not** clear the direct `service_role` table ACL, absent success-receipt trigger/budget tables, old callable overloads, historical SQL provenance, owner review, or write authorization. The query used the same MCP session which reported `transaction_read_only=off`; although it was SELECT-only, it was not session-enforced read-only. Formal evidence still must come from the pinned runner and scoped read-only capture.

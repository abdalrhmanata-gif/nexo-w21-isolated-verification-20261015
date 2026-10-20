# ZAVQERA — Hosted 13-query evidence review (2026-10-17)

**Disposition: REVIEW REQUIRED / RELEASE NO-GO.** This is an offline review of the user's uploaded evidence ZIP. No new database connection, SQL execution, hosted write, migration, deployment, or secret change was performed during this review.

## Evidence identity and integrity

- Uploaded ZIP: 20261017T151516202599Z.zip
- ZIP SHA-256: 9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d
- ZIP integrity: passed; all 13 files query_01.json through query_13.json are present.
- Capture time (UTC): 2026-10-17T15:15:16.204988+00:00
- Project: ZAVQERA Development (mrwmmbytcymqgwvcoywd), region eu-west-1, status ACTIVE_HEALTHY
- PostgreSQL: server_version_num=170006
- Query pack SHA-256: a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284
- Query 13 SHA-256: 806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b
- Offline source HEAD recorded by reviewer: fbbcb080904acd88aad83a082803f627859026e2
- Source migration manifest SHA-256: 0d05ab7285edc975084ddbc595d1af7d2dd0752cc27e94d8fe0549170419be38; Git migration tree clean: true
- Capture role gate: PASS (current_user=session_user=supabase_read_only_user, transaction read-only, not superuser, cannot create roles/databases, ledger visible).
- The capture role reports rolbypassrls=true. The captured queries are metadata-only and the transaction was read-only; do not reuse this credential for application-row reads.
- Metadata says token_saved=false; a basic scan did not find recognizable Supabase secret/API token strings in the ZIP. This scan is not a universal secret scanner.

## Critical observed blockers

### 1. service_role has direct public.agent_executions privileges

- Effective privileges are true for all eight captured table privileges: SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER, and PostgreSQL 17 MAINTAIN.
- The stored table ACL contains direct service_role grants for these privileges, including the write/control privileges. Query 12 and query 13 agree.
- Relation owner is postgres; RLS is enabled but not forced.
- Query 13 found no service_role parent-role ACL entries, no reachable parent membership path beyond the root role, no service_role path to the table owner, and no service_role path to authenticated.
- Therefore the specific W86 inherited/owner-path preflight reports NO_PARENT_ROLE_ACL_OBSERVED, but this is not authorization to apply W86. The direct grants remain present in the captured Development state.

### 2. The deployed catalog materially differs from the candidate contract

- Two required relations are absent: public.mission_authority_budgets and public.mission_authority_budget_reservations.
- All 26 queried expected columns are absent: 12 on agent_executions, 2 on ai_usage_reservations, 5 on mission_authority_budget_reservations, and 7 on mission_authority_budgets.
- 10 of 11 queried constraints are absent. The only observed one is ai_usage_reservations_state_check, whose current definition allows reserved, consumed, and released.
- All 8 queried expected indexes are absent.
- The trigger agent_execution_success_receipt_guard is absent.
- These findings indicate the hosted schema does not currently match the queried candidate expectations for dispatch/reconciliation/research claim fields and authority-budget accounting.

### 3. Function-signature/ACL expectations mismatch

- Query 6 compares 40 pinned routine expectations: 36 expected to exist and 4 expected absent.
- Only 17/40 expectation rows match; 23 mismatch.
- 19 expected signatures are absent:
  - private.claim_agent_execution_dispatch(uuid)
  - private.claim_agent_execution_reconciliation(uuid)
  - private.claim_read_only_research_execution(uuid,uuid,text)
  - private.complete_read_only_research_execution(uuid,uuid,text,jsonb,jsonb,text,text)
  - private.configure_mission_authority_budget(uuid,uuid,uuid,bigint,numeric,numeric,text,timestamptz,timestamptz)
  - private.guard_external_execution_success_receipt()
  - private.reconcile_agent_execution_outcome(uuid,uuid,text,jsonb,jsonb)
  - private.reserve_agent_execution_budget(uuid,uuid)
  - private.reserve_ai_generation(text,text,text)
  - private.revoke_mission_authority_budget(uuid)
  - private.settle_agent_execution_budget(uuid,text,jsonb)
  - public.claim_agent_execution_dispatch(uuid)
  - public.claim_agent_execution_reconciliation(uuid)
  - public.claim_read_only_research_execution(uuid,uuid,text)
  - public.complete_read_only_research_execution(uuid,uuid,text,jsonb,jsonb,text,text)
  - public.configure_mission_authority_budget(uuid,uuid,uuid,bigint,numeric,numeric,text,timestamptz,timestamptz)
  - public.reconcile_agent_execution_outcome(uuid,uuid,text,jsonb,jsonb)
  - public.reserve_ai_generation(text,text,text)
  - public.revoke_mission_authority_budget(uuid)
- 4 signatures expected absent are still present:
  - private.complete_read_only_research_execution(uuid,text,jsonb,jsonb,text,text)
  - private.reserve_ai_generation(text)
  - public.complete_read_only_research_execution(uuid,text,jsonb,jsonb,text,text)
  - public.reserve_ai_generation(text)
- In particular, the old private.reserve_ai_generation(text) SECURITY DEFINER routine exists and grants EXECUTE to authenticated and service_role; its public.reserve_ai_generation(text) wrapper also exists and grants EXECUTE to those roles. The old private.complete_read_only_research_execution(uuid,text,jsonb,jsonb,text,text) routine exists SECURITY DEFINER with authenticated EXECUTE, and its public wrapper is present with authenticated/service_role EXECUTE. The function body on disk in the evidence has auth/mission/authority checks for completion, so this is recorded as signature/contract drift requiring owner review—not asserted as a proven exploit. Do not drop or replace functions before dependency and behavior review.
- The private schema effective USAGE projection is anon=False, authenticated=True, service_role=True. This context should be reviewed alongside the routine ACLs and Supabase exposed-schema configuration.
- Query 10 reports 8 explicit default-ACL EXECUTE rows for schema public across creator roles postgres and supabase_admin, including anon, authenticated, and service_role. Reconcile these with the intended default-function-privilege policy before future function creation.

### 4. Migration provenance cannot be reconciled from the ledger alone

- Checked-in migration sources: 89; hosted ledger rows: 74.
- Exact version/name matches: 46.
- Same-name/different-version conflicts: 22.
- Hosted-only names: 6.
- Source tuples absent from the hosted ledger: 43.
- The ledger contains migration version/name metadata, not historical SQL bytes. Do not infer deployed SQL equality or reconstruct missing historical migrations from current files or similar names.

## Safe disposition and next actions

1. Keep release NO-GO, hosted_write_authorized=false, and trusted dispatch adapters empty/fail-closed.
2. Do not apply W86 or any migration to hosted Development or Main/Production. The no-parent-role finding is only one prerequisite gate; schema/function drift and historical provenance remain unresolved.
3. Ask an independent database owner to review the exact 13-query ZIP, especially the missing budget/claim structures, missing trigger, legacy callable overloads/default ACLs, and direct service_role table grants.
4. Recover authoritative historical migration SQL sources and map the 22 same-name/different-version conflicts plus six hosted-only names. Keep unresolved entries explicitly UNKNOWN.
5. Only after those steps, create a reviewed forward-only remediation plan with least-privilege ACLs, migration ordering, backup/recovery plan, and post-change acceptance tests. Separate explicit authorization is still required before any hosted write.

## Existing project references

- Audit PR #2 (open/draft/unmerged): https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2
- W86 candidate PR #1 (open/draft/unmerged): https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/1

This report summarizes catalog metadata only. It does not certify application behavior, provider-boundary enforcement, Mission Authority correctness, deployed SQL equivalence, or release readiness.

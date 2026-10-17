# ZAVQERA — Hosted remediation gates and acceptance plan (2026-10-17)

**Status: PLAN ONLY — NOT AUTHORIZED FOR EXECUTION. Release: NO-GO.** This document translates the reviewed Development catalog capture into a controlled sequence. It does not contain executable SQL, authorize a write, or establish that a particular legacy signature is exploitable.

## 1. Evidence baseline to preserve

Before additional work, preserve the exact source inputs and hashes together:

- Capture archive: 20261017T151516202599Z.zip
- Archive SHA-256: 9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d
- Capture time UTC: 2026-10-17T15:15:16.204988+00:00
- Target project: ZAVQERA Development / mrwmmbytcymqgwvcoywd / eu-west-1
- Target PostgreSQL version: 17.6 (server_version_num 170006)
- Base query pack SHA-256: a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284
- Query 13 SHA-256: 806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b
- Source HEAD: fbbcb080904acd88aad83a082803f627859026e2
- Source migration manifest SHA-256: 0d05ab7285edc975084ddbc595d1af7d2dd0752cc27e94d8fe0549170419be38

The read-only capture role reports rolbypassrls=true. Keep its use scoped to the pinned metadata-only audit. Never reuse this credential for application-row reads and never include tokens in issues, commits, logs, or report files.

## 2. Mandatory control state

Until all gates in this plan are independently satisfied:

- Keep hosted_write_authorized=false.
- Do not apply W86 or any other migration to hosted Development or Main/Production.
- Do not edit the hosted migration ledger to make it match checked-in filenames.
- Do not drop, rename, replace or revoke routine permissions merely because a signature differs from a candidate expectation.
- Keep TRUSTED_DISPATCH_ADAPTERS empty/fail-closed.
- Keep PR #1 and PR #2 OPEN/DRAFT/UNMERGED.
- All investigation after this capture remains offline or explicitly read-only with a separately reviewed scope.

## 3. Workstream A — establish historical migration provenance

### Recorded discrepancy

- Checked-in source migrations: 89.
- Hosted ledger rows: 74.
- Exact version/name tuples: 46.
- Same-name/different-version conflicts: 22.
- Hosted-only names: 6.
- Source tuples absent from the hosted ledger: 43. The 22 conflicts are included among the unmatched source tuples; do not add these counts together as if they were disjoint.

### Required artifact

Create a row-per-migration reconciliation ledger for all source and hosted rows. Every row must record source version/name, hosted version/name if any, authoritative source location, source Git commit/blob SHA or archive provenance, SQL SHA-256 where actual SQL exists, classification, reviewer, and supporting evidence.

Allowed classifications:

1. EXACT_SOURCE_BYTES_VERIFIED — exact historical SQL bytes are linked to a trusted source and a verified deployment record.
2. NAME_VERSION_CONFLICT — same name but version differs; requires authoritative resolution.
3. HOSTED_ONLY_SOURCE_UNKNOWN — a hosted ledger tuple has no recovered authoritative source.
4. SOURCE_NOT_IN_LEDGER — checked-in tuple is not in the hosted ledger; this alone does not prove it was never deployed.
5. UNKNOWN — sources are incomplete or contradictory.

A ledger version/name tuple is metadata, not SQL-byte evidence. Current function definitions, neighboring migrations, branch names, timestamps, or similar filenames cannot substitute for an authoritative historical SQL source. Do not reconstruct SQL from guesses.

### Gate A passes only when

- Every one of the 74 hosted ledger rows is classified and evidence-linked.
- All 22 timestamp/version conflicts have an evidence-backed disposition.
- All six hosted-only names have an authoritative source or remain explicitly UNKNOWN and block release.
- All checked-in source rows are explained without pretending that ledger absence proves non-deployment.
- An independent reviewer approves the reconciliation, and the evidence bundle records its exact source HEAD and manifest hash.

If authoritative sources cannot be recovered, the valid decision is to keep NO-GO or design a separately reviewed database re-baselining project; editing migration history alone is not an acceptable shortcut.

## 4. Workstream B — validate the current security and schema discrepancy

The latest capture confirms direct service_role grants on public.agent_executions for all eight captured PostgreSQL 17 privileges: SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER and MAINTAIN. RLS is enabled but not forced. Query 13 found no inherited parent ACL, no service_role path to the table owner and no service_role path to authenticated. That clears only the corresponding W86 role-path preflight; it does not authorize a migration.

The catalog comparison also found:
- Missing relations: public.mission_authority_budgets and public.mission_authority_budget_reservations.
- 26 expected columns absent.
- 10 of 11 expected constraints absent; the one observed state constraint allows reserved, consumed and released.
- All eight queried expected indexes absent.
- Trigger agent_execution_success_receipt_guard absent.
- 23 of 40 routine expectation rows mismatched: 19 expected signatures absent, four signatures expected absent still present.
- Eight explicit default EXECUTE ACL rows for public functions across creators postgres and supabase_admin.
- private schema effective USAGE: anon=false, authenticated=true, service_role=true.

### Required owner review

An independent database owner must review, at minimum:
1. Whether service_role is intended to write directly to agent_executions or only through guarded RPCs.
2. The legacy reserve_ai_generation(text) SECURITY DEFINER routine and public wrapper, including dependencies, callers, auth checks, and permission grants.
3. The legacy complete_read_only_research_execution(uuid,text,jsonb,jsonb,text,text) overloads and wrappers. Their signature mismatch alone is not proof of exploitability; review their bodies and runtime callers before any removal.
4. The private-schema USAGE posture, exposed-schema configuration and the default function EXECUTE ACLs.
5. The missing Mission Authority budget/reservation objects, dispatch/reconciliation claims, and success-receipt trigger against the intended product contract.
6. Required user-facing behavior and provider boundary guarantees if any object changes or disappears.

The owner review must state which observed differences are intended legacy state, accidental drift, or unresolved. No permission or function should be removed based on names alone.

## 5. Workstream C — prepare candidate changes offline

After Gate A and owner review of Workstream B:

- Build a migration-by-migration target-state matrix from authoritative SQL and product contracts, not from a partial checklist alone.
- Split ACL containment from schema/function restoration so each change has a narrow purpose and a separately reviewable diff.
- Preserve W86 as a candidate, not an instruction to apply. Confirm its preflight against a fresh read-only catalog snapshot immediately before any owner-authorized change.
- Do not create a new migration that silently assumes the two missing budget tables, 26 columns, trigger, or 19 routines are present. Choose explicit, dependency-aware ordering from actual migration source.
- Review all CREATE OR REPLACE / DROP / ALTER changes for routine identity, function owner, SECURITY DEFINER status, search_path, grants, RLS behavior, foreign keys, uniqueness/idempotency and dependent application calls.
- Produce a rollback/forward-recovery plan backed by captured current definitions and grants. Do not rely on reconstructing old permissions from memory; do not describe rollback as safe until it is tested.

No hosted SQL is to be written from this planning phase.

## 6. Workstream D — isolated acceptance

Test in disposable PostgreSQL 17 first. Current evidence is PG 17.6 on hosted Development; existing CI evidence uses a disposable PG 17.11 environment. Document that minor-version difference and add a PG 17.6 validation run if the exact container/runtime can be supported before proposing execution.

Required automated gates:
- Fresh database migration replay from authoritative source inputs, without hand-editing source migrations.
- All applicable W44/W46/W80/W84/W85/W86 pgTAP checks, including repeated-apply/idempotency and exact no-mutation negative controls.
- A catalog assertion for every desired table, column, constraint, index, trigger, routine signature, function owner/security mode, EXECUTE ACL, default ACL and relation/table/column ACL.
- Owner-path, INHERIT/SET ROLE, anon/authenticated grant-target and mixed-path refusal tests.
- App/server integration tests proving dispatch and reconciliation require current authority, budget reservations are concurrency safe/idempotent, research claims remain read-only, and success receipt verification cannot be bypassed.
- Positive-path and denial-path tests, including expired/revoked authority, duplicate/idempotency replay, failed/unknown provider outcome, and concurrent requests.
- Artifact cleanup verification and secret redaction.
- Exact source commit and artifact digests recorded in the evidence report.

Passing disposable tests demonstrate only the candidate in the isolated environment. They do not alone prove hosted database equivalence or authorize a hosted write.

## 7. Workstream E — explicit execution gate

No hosted action can begin until every item below is true:

- [ ] Gate A historical migration provenance independently approved.
- [ ] Independent database-owner review approved the exact remediation diff and its security rationale.
- [ ] Exact target project identity and fresh read-only preflight reviewed.
- [ ] A restorable pre-change backup/snapshot is confirmed, and the recovery procedure is tested.
- [ ] Candidate is fully tested in the isolated PostgreSQL environment with exact source commit/artifact hashes.
- [ ] Application release compatibility and maintenance/rollback plan are approved.
- [ ] An explicit, separate written authorization names the exact project, migrations/SQL, sequence, time window, operator and rollback conditions.
- [ ] Post-change read-only assertions and application acceptance tests are ready to run.
- [ ] Main/Production is explicitly out of scope unless a later separate authorization says otherwise.

If any item is missing, stop without making changes.

## 8. Post-change acceptance (only after separate authorization)

A future owner-authorized change must capture before/after values and fail the release if any desired state is not exact:
- service_role cannot directly perform unapproved table/column operations on agent_executions; only approved guarded RPC pathways remain.
- RLS and policy checks are effective and no role-membership path reintroduces blocked access.
- Required budget/reservation schema, dispatch/reconciliation functions, success receipt trigger and indexes exist with exact definitions and intended owners/grants.
- Legacy overloads have an explicitly reviewed disposition; no unintended executable wrapper remains.
- Default function privileges follow the reviewed policy for both postgres and supabase_admin.
- Mission Authority/provider integration suites pass and negative controls prove refusal before mutation.
- Evidence confirms only the explicitly authorized target changed; no other project was touched.
- If acceptance fails, follow the pre-approved recovery path and keep launch blocked.

## 9. Current next action

The highest-value next action is an independent database-owner review of the uploaded archive and this plan, concurrent with authoritative historical migration-source recovery. Use [`ZAVQERA_INDEPENDENT_DB_OWNER_REVIEW_WORKSHEET_2026-10-17.md`](ZAVQERA_INDEPENDENT_DB_OWNER_REVIEW_WORKSHEET_2026-10-17.md) to record evidence-backed dispositions; it is intentionally unsigned and defaults every owner gate to OPEN. The audit PR can preserve the evidence and organize planning, but it cannot replace the owner decision or authorize database changes.

**Current final disposition: NO-GO. hosted_write_authorized=false. No hosted migration is authorized or performed by this document.**

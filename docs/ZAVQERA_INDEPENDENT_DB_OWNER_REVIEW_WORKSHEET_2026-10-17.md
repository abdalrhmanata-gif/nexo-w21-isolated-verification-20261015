# ZAVQERA Development — Independent Database-Owner Review Worksheet
**Date:** 2026-10-17  
**Status:** NOT REVIEWED / NOT APPROVED  
**Purpose:** Record an independent, evidence-backed owner decision on the captured Development catalog and unresolved migration provenance. This worksheet is deliberately unsigned and does not authorize any database change.

## 0. Non-negotiable boundaries

- Current release disposition remains **NO-GO**.
- `hosted_write_authorized=false`.
- Do not apply W86 or another migration to hosted Development or Main/Production while any gate below remains open.
- Do not edit `supabase_migrations.schema_migrations` to make names or timestamps match.
- Do not drop, replace, or revoke routines/permissions solely because a signature differs from an expected candidate signature.
- Keep `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed.
- No token, connection string, API key, user data, or raw credential may be entered in this worksheet or a GitHub comment.
- This document does not substitute for a separate, explicit written authorization naming an exact target, change set, operator, maintenance window, backup/recovery plan, and post-change acceptance procedure.

## 1. Evidence identity — preserve before review

| Field | Captured value |
|---|---|
| Evidence archive | `20261017T151516202599Z.zip` |
| Archive SHA-256 | `9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d` |
| Capture UTC | `2026-10-17T15:15:16.204988Z` |
| Project | ZAVQERA Development |
| Project ref | `mrwmmbytcymqgwvcoywd` |
| Region / DB status | `eu-west-1` / `ACTIVE_HEALTHY` at capture time |
| PostgreSQL | `server_version_num=170006` (17.6) |
| Base 12-query pack SHA-256 | `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284` |
| Query 13 SHA-256 | `806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b` |
| Offline source HEAD recorded by capture reviewer | `fbbcb080904acd88aad83a082803f627859026e2` |
| Raw source-manifest SHA-256 in capture | `0d05ab7285edc975084ddbc595d1af7d2dd0752cc27e94d8fe0549170419be38` |
| LF-normalized manifest digest from portability reconciliation | `555db007d0c25ee7bf6ed4f983766eea1dde170a7ef5d0e12cc710d5838c7094` |

**Important:** The raw-vs-LF digest difference is explained as a line-ending representation difference in the source manifest; normalization makes current-checkout manifest comparisons portable. It does **not** prove that historical deployed SQL bytes equal the current checked-in SQL. The database capture says the audit role had `rolbypassrls=true`; the captured query set is metadata-only and the capture was transaction-read-only. Keep that credential scoped to the pinned metadata audit and do not reuse it for application-row reads.

## 2. Reviewer independence and decision record

Complete only by an owner with authority over the Development database and sufficient context to approve or reject the intended database state. If the reviewer did not independently examine the archive and the supporting source/contracts, mark this section **NOT REVIEWED**.

- Reviewer name / role: **[blank — owner to complete]**
- Review date (UTC): **[blank — owner to complete]**
- Independence / authority basis: **[blank — owner to complete]**
- Evidence archive hash recomputed by reviewer: **[blank — owner to complete]**
- Supporting contract/release commit reviewed: **[blank — owner to complete]**
- Overall outcome: **[OPEN / REJECTED / REVIEWED—MORE EVIDENCE REQUIRED / APPROVED FOR OFFLINE REMEDIATION DESIGN ONLY]**
- Rationale and evidence locations: **[blank — owner to complete]**

The strongest possible outcome in this worksheet is approval to proceed with **offline remediation design**. It cannot authorize a hosted write.

## 3. Observed Development discrepancies — owner disposition required

For each numbered item, record a disposition as **INTENDED LEGACY STATE**, **ACCIDENTAL DRIFT**, or **UNRESOLVED**; cite direct evidence; identify the expected target state and its authoritative source; then specify whether further read-only investigation is needed. Do not default an unreviewed item to “intended” or “safe”.

### A. Direct privileges on `public.agent_executions`

**Observed in capture:** The stored/effective ACL reports `service_role` has all eight queried privileges: SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER and PostgreSQL 17 MAINTAIN. The table is owned by `postgres`; RLS is enabled but not forced. Query 13 found no inherited parent-role ACL, no path from `service_role` to the table owner, and no `service_role` path to `authenticated`.

Owner decisions:
- Are direct table writes by `service_role` intended, or must writes be available only through reviewed guarded RPCs?
- For each privilege, state ALLOW/DENY and cite the intended service contract and approved callers.
- Is the RLS/ownership posture intentional for this service-role access pattern? Explain the trust boundary; do not treat RLS being enabled as proof that service_role access is contained.
- What evidence proves the final decision (exact grant inventory and trusted application/worker call path)?

Disposition: **[blank]**  
Evidence / rationale: **[blank]**  
Required follow-up: **[blank]**

### B. Missing Mission Authority schema and integrity controls

**Observed in capture:** Two expected relations are absent: `public.mission_authority_budgets` and `public.mission_authority_budget_reservations`. All 26 queried expected columns are absent (12 on `agent_executions`, 2 on `ai_usage_reservations`, 5 on the absent reservation relation, and 7 on the absent budgets relation). Ten of eleven queried constraints are absent; the observed `ai_usage_reservations_state_check` permits `reserved`, `consumed`, and `released`. All eight queried expected indexes are absent. Trigger `agent_execution_success_receipt_guard` is absent.

Owner decisions:
- Identify the authoritative migration/source and product invariant for every missing relation, column, constraint, index, and trigger.
- State which are required for the currently intended deployed application versus only a later candidate.
- Confirm dependency and rollout ordering; do not assume that applying an individual newest migration will be safe against this catalog.
- Specify exact post-change assertions and the negative controls that must prove refusal before mutation.

Disposition: **[blank]**  
Authoritative source(s): **[blank]**  
Evidence / rationale: **[blank]**  
Required follow-up: **[blank]**

### C. Routine signature and permission mismatches

**Observed in capture:** Query 6 checks 40 pinned routine expectations: 36 expected present and four expected absent. Seventeen of forty rows match; 23 mismatch (19 expected signatures absent and four signatures expected absent still present). Captured legacy routines include `private.reserve_ai_generation(text)` and its public wrapper, and `private.complete_read_only_research_execution(uuid,text,jsonb,jsonb,text,text)` and its wrapper. The named private routines are SECURITY DEFINER and have the EXECUTE grants recorded in the capture. The report describes auth/mission/authority checks in the on-disk completion body, so signature drift alone is **not** a proven exploit.

Owner decisions:
- For each affected signature, record current existence, intended existence, exact caller(s), dependency evidence, owner, SECURITY DEFINER status, safe `search_path`, and required EXECUTE grantees.
- Review public wrappers, private routine behavior, and exposed-schema configuration together.
- For each of the four unexpected signatures, explicitly record KEEP / RESTRICT / REPLACE / REMOVE and why; no action may be based on the name alone.
- For each of the 19 missing signatures, state whether a trusted caller requires it and identify its authoritative source.

Disposition: **[blank]**  
Routine-by-routine review location: **[blank]**  
Evidence / rationale: **[blank]**  
Required follow-up: **[blank]**

### D. Private-schema USAGE and default EXECUTE privileges

**Observed in capture:** The effective private-schema USAGE projection is `anon=false`, `authenticated=true`, `service_role=true`. Query 10 reports eight explicit default-ACL EXECUTE rows for schema `public`, across creator roles `postgres` and `supabase_admin`, including `anon`, `authenticated`, and `service_role`.

Owner decisions:
- Confirm intended schema exposure and whether authenticated/service_role USAGE on `private` is necessary.
- Reconcile each default ACL against an explicit policy for both creator roles.
- Document the effect on future functions without assuming current routine ACLs will be retroactively changed.

Disposition: **[blank]**  
Authoritative policy / evidence: **[blank]**  
Required follow-up: **[blank]**

### E. Historical migration provenance

**Observed in reconciliation:** 89 checked-in source migration files and 74 hosted ledger rows; 46 exact version/name metadata tuples, 22 same-name/different-version conflicts, 21 source-only tuples, and six hosted-only tuples. There are 43 source tuples absent from the exact hosted tuple set because the 22 source halves of conflicts are included among the unmatched source tuples; do not double-count them. The hosted ledger holds version/name metadata, not historical SQL bytes. No row is established as `EXACT_SOURCE_BYTES_VERIFIED`.

Owner decisions:
- Identify the trusted source of deployed SQL and deployment provenance for each hosted migration row.
- For each of the 22 conflicts and six hosted-only names, link the original SQL blob/archive and deployment identity, or leave the classification explicitly **UNKNOWN**.
- Confirm how all 74 hosted rows and 89 source rows are explained without treating absence from the ledger as proof that a source migration never ran.
- If source recovery is impossible, decide whether to keep NO-GO or commission a separately reviewed database re-baselining project. Do not manually rewrite migration history.

Disposition: **[blank]**  
Trusted archive/deployment source: **[blank]**  
Independent reconciliation reviewer: **[blank]**  
Required follow-up: **[blank]**

### F. Read-only audit role and capture hygiene

**Observed in capture metadata:** The capture role reports `rolbypassrls=true`; the 13 pinned queries are metadata-only, and the transaction was read-only. The ZIP scan did not find recognizable Supabase secret/API token strings, but the scan is not universal.

Owner decisions:
- Confirm the role's intended metadata-only scope and credential lifecycle.
- Confirm the credential will not be reused for application-row reads and that no credential was committed or included in the ZIP.
- Record any credential revocation/rotation decision through the owner's standard secret-handling process, not in this worksheet.

Disposition: **[blank]**  
Evidence / rationale: **[blank]**  
Required follow-up: **[blank]**

## 4. Independent gate checklist

Mark each item only with evidence. **OPEN** is the default.

| Gate | Status | Required supporting evidence |
|---|---|---|
| Evidence ZIP identity and hashes independently verified | OPEN | Recomputed SHA-256 and integrity result |
| Direct service_role grants disposition approved | OPEN | Exact ACL evidence and reviewed intended callers |
| Missing relations/columns/constraints/indexes/trigger disposition approved | OPEN | Authoritative source, invariant mapping and dependency review |
| 40 routine expectations individually reconciled | OPEN | Per-signature existence, body, owner, security mode, callers and grants |
| Private schema USAGE and both default ACL creator policies approved | OPEN | Exact catalog evidence and written least-privilege rationale |
| 22 version conflicts resolved with trusted evidence or explicitly UNKNOWN | OPEN | Source/blob/archive plus deployment link per row |
| Six hosted-only tuples recovered or explicitly UNKNOWN | OPEN | Source/blob/archive plus deployment link per row |
| 74 hosted ledger rows classified and evidence-linked | OPEN | Reconciliation ledger + independent approval |
| 89 source migrations accounted for without false non-deployment assumptions | OPEN | Row-level mapping + independent approval |
| Isolated acceptance covers exact candidate/PG version and all affected grants/schema/routines | OPEN | Exact-SHA test evidence, negative controls and cleanup proof |
| Pre-change backup/recovery plan is restorable and tested | OPEN | Owner-confirmed snapshot and recovery rehearsal evidence |
| Separate change authorization issued for an exact, scoped future write | OPEN | Written target/change/operator/window/backup/recovery/post-check authorization |

## 5. Required decision output

The independent reviewer should produce a signed comment or controlled review record containing:

1. The archive SHA-256 and exact source/release commits reviewed.
2. A decision for every discrepancy in Sections A–F; unresolved items must remain explicitly open.
3. Trusted historical-source evidence or an explicit statement that SQL-byte provenance cannot be recovered.
4. A distinction between approval for offline candidate design and authorization to perform a hosted write.
5. A list of evidence still required before an exact remediation candidate can be approved.

## 6. Execution stop conditions

Stop without making a hosted change if the owner is unavailable, independence is unclear, any historical row is still incorrectly represented as byte-verified, routine or grant intent is unclear, the candidate assumes absent objects exist, an acceptance test is missing, a restorable backup is unconfirmed, or explicit change authorization is not present.

## 7. Source records

- Hosted capture review: [ZAVQERA_HOSTED_13_QUERY_CAPTURE_REVIEW_2026-10-17.md](ZAVQERA_HOSTED_13_QUERY_CAPTURE_REVIEW_2026-10-17.md)
- Remediation gates and acceptance plan: [ZAVQERA_HOSTED_REMEDIATION_GATES_2026-10-17.md](ZAVQERA_HOSTED_REMEDIATION_GATES_2026-10-17.md)
- Historical migration source recovery scan: [ZAVQERA_HISTORICAL_MIGRATION_SOURCE_RECOVERY_SCAN_2026-10-17.md](ZAVQERA_HISTORICAL_MIGRATION_SOURCE_RECOVERY_SCAN_2026-10-17.md)
- Row-level reconciliation ledger: [ZAVQERA_MIGRATION_PROVENANCE_RECONCILIATION_LEDGER_2026-10-17.md](ZAVQERA_MIGRATION_PROVENANCE_RECONCILIATION_LEDGER_2026-10-17.md)
- Isolated audit PR #2: https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2

**Final statement:** Until an independent owner completes and approves the review, all these discrepancies remain open, no hosted write is authorized, trusted dispatch adapters remain empty/fail-closed, and release remains **NO-GO**.


## 8. Row-by-row migration decision intake

To prevent a broad approval note from hiding unresolved individual rows, use the companion 95-row intake file:

- [Row-level decision intake CSV](ZAVQERA_MIGRATION_OWNER_DECISION_INTAKE_2026-10-17.csv)
- [Intake instructions and controlled dispositions](ZAVQERA_MIGRATION_OWNER_DECISION_INTAKE_README_2026-10-17.md)
- Source ledger: [migration provenance reconciliation ledger](ZAVQERA_MIGRATION_PROVENANCE_RECONCILIATION_LEDGER_2026-10-17.md)

The CSV preserves all 95 current reconciliation units and initializes each owner disposition as `OPEN`, reviewer as `UNASSIGNED`, and hosted change authorization as `NO — separate written authorization required`. Fill historical source/blob/archive evidence, actual SQL SHA-256, deployment reference, deployed SQL digest, independent reviewer, UTC review time, decision rationale and follow-up only when supported by evidence. `EXACT_SOURCE_BYTES_VERIFIED` is permitted only when both authoritative historic SQL bytes and a trusted deployment record establish exact identity. Metadata tuple matches, normalized manifests, current schema, similar names and local tests are not sufficient. A `SOURCE_ONLY_REVIEWED` disposition must not imply that ledger absence proves non-deployment.


The same CSV is guarded by an offline, no-network validator and tamper-regression tests: [validator](../tools/validate_zavqera_migration_owner_intake.py), [tests](../tests/test_zavqera_migration_owner_intake.py), and [CI workflow](../.github/workflows/zavqera-owner-intake-validation.yml). The guard proves the intake has not been silently altered; it does not close any owner or historical-source gate.


---

## 9. Evidence-based reviewer assessment — 2026-10-18

**Review type:** Independent analytical review of the recorded 2026-10-17 13-query metadata capture and related checked-in reports. This is not a live database review or a representation that the author is the legal/administrative database owner. No new connection was opened and no SQL was executed in this review. The capture’s archive SHA-256 is `9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d`.

**Overall disposition: REVIEWED — MORE EVIDENCE REQUIRED. Release remains NO-GO. No hosted changes authorized.**

### 9.1 Evidence-supported findings

| Area | Assessment from the captured evidence | Provisional disposition | Evidence required to close |
|---|---|---|---|
| Direct `service_role` privileges on `public.agent_executions` | The capture reports direct table privileges for SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER and MAINTAIN; RLS is enabled but not forced. Query 13 reports no inherited ACL path, owner path, or role path to authenticated. | **UNRESOLVED — security-significant grant exists.** The captured state is established for capture time; intent and exploitability are not established. | Owner-approved privilege matrix, exact SQL grants/ACL before and after expected state, authoritative caller/adapter mapping, isolated negative tests proving disallowed direct DML fails and approved guarded RPC flow works. |
| Missing Mission Authority relations/columns/constraints/indexes/trigger | Two budget relations, 26 expected columns, 10 of 11 queried constraints, eight indexes and the success-receipt trigger are reported absent relative to the audited candidate expectations. | **UNRESOLVED — material contract/catalog drift relative to candidate.** Not yet proven to be unintended production drift because candidate-vs-current release applicability has not been independently established. | Identify the exact intended release/contract commit and map every expected object to authoritative migration and application caller; document whether required for the current deployed product or only a future candidate; isolated full replay and catalog assertions. |
| Routine signatures and grants | 23/40 expectation rows mismatch: 19 expected signatures absent and four signatures expected absent remain present. The report notes SECURITY DEFINER legacy routines and EXECUTE grants. | **UNRESOLVED — high-risk permission/interface drift requiring routine-by-routine analysis.** Signature mismatch alone is not proof of exploit. | For every signature: definition/body, owner, SECURITY DEFINER, fixed safe search_path, all EXECUTE grants, exposed-schema configuration, dependent callers, behavior tests, and explicit KEEP/RESTRICT/REPLACE/REMOVE decision by authorized owner. |
| Private-schema USAGE and default ACLs | Effective `private` USAGE is reported false for anon and true for authenticated/service_role; eight public-schema default EXECUTE ACL rows are reported for creator roles postgres and supabase_admin. | **UNRESOLVED — least-privilege policy not evidenced.** Cannot classify as intentional. | Approved exposure policy; per-creator default ACL matrix; tests for existing and future routine privileges; app/RPC compatibility review. |
| Migration history | 89 source files, 74 hosted rows, 46 exact metadata tuples, 22 version conflicts and six hosted-only names. The full Library ZIP scan found one source-side W4 candidate but no per-migration deployment record tying it to the differently versioned hosted row. | **UNRESOLVED — no exact source/deployed SQL equivalence proven for the ledger.** | Authoritative historical SQL per row plus trusted deployment evidence tying bytes to project/version/time; independent row-by-row review. Keep UNKNOWN where missing. |
| Audit-role/capture hygiene | Capture was described as read-only and metadata-only; role reports `rolbypassrls=true`. ZIP scan found no recognizable token string but was explicitly not universal. | **CONDITIONAL — procedure is read-only, but elevated audit-role attribute and credential hygiene need owner confirmation.** | Confirm least-privileged metadata-only scope, credential owner and lifecycle, verify credential was not committed/disclosed through owner’s secret-handling procedures, and rotate/revoke if exposure is suspected. No credential belongs in review files. |
| Mission Authority enforcement boundary | The database metadata capture cannot prove provider-independent JIT authorization at every external side effect, correct lease/revision/approval/budget enforcement, concurrency safety, or outcome reconciliation. | **NOT ESTABLISHED by this evidence.** | Separate application/server/adapter source audit and isolated authenticated E2E tests including bypass attempts, stale/revoked authority, approval denial, budget races, replay/idempotency and unknown provider outcomes. |

### 9.2 Intentional legacy versus accidental drift

The supplied evidence does not establish that any of sections A–F is an *intentional* legacy state. Nor does it independently prove the observed discrepancies are accidental changes from a previously approved target. Therefore, this review does **not** label them as intentional or accidental. Provisional classifications remain **UNRESOLVED** until the owner identifies the authoritative target contract/release and documents rationale using the evidence listed above.

### 9.3 Gate decision

- Evidence archive identity and completeness: **REPORTED PASS in the existing review**; independent recomputation of the ZIP SHA was not performed in this new review.
- Read-only capture protocol and 13-query evidence: **REPORTED PASS**, based on the checked-in review; not a fresh hosted recapture.
- Direct grants / schema / routines / default ACL owner decisions: **OPEN**.
- Historical SQL provenance (22 conflicts and six hosted-only): **OPEN / BLOCKING**.
- Independent authorization, restorable backup and recovery rehearsal: **OPEN**.
- Exact isolated remediation candidate and full negative/positive acceptance evidence: **OPEN**.
- Explicit separate authorization for any hosted change: **NOT PROVIDED; writes remain prohibited**.

**Final recommendation:** Do not apply W86 or another migration, do not revise the hosted migration ledger, and do not revoke/drop/replace a routine based only on this capture. Proceed first with authorized-owner review and source provenance recovery. Only then develop and test a forward-only, least-privilege remediation candidate in disposable PostgreSQL, with a verified recovery plan. This assessment approves **neither schema remediation nor release**; at most it establishes a documented interim review assessment.


### 9.4 Exact source-checkout GitHub path-history sweep — 2026-10-18

A further check compared the **exact source checkout HEAD recorded in the existing capture review**, `fbbcb080904acd88aad83a082803f627859026e2`, rather than relying only on current branch names.

- The recursive tree was not truncated (641 entries) and contains 89 migration SQL files.
- All 89/89 source-version filename tuples in the 95-row intake exist in that exact source tree. This establishes checked-in source-file presence at that commit; it does not establish what was deployed.
- Of the 74 hosted filename tuples, 46 exact-version/name paths exist at that source tree; all 22 different-version hosted paths and all six hosted-only paths are absent.
- GitHub commit-path-history lookups for each of the exact 28 absent hosted-version filenames at that source HEAD returned zero commits. The detailed [sweep report](ZAVQERA_GITHUB_HOSTED_MIGRATION_PATH_HISTORY_2026-10-18.md) and [28-row comparison CSV](ZAVQERA_GITHUB_HOSTED_MIGRATION_PATH_HISTORY_2026-10-18.csv) record the exact path-by-path result and source Git blob SHAs where a source counterpart exists.

#### W4 source-history caveat

The source-side W4 file path `20260921180052_w4_table_privilege_hardening.sql` has Git blob SHA `2745a06c66b9f325683beaa973e10f6d21631555` at the captured source HEAD. GitHub path history reports one commit for that source path: [`772f011624c199adc021a61d039a4cf13e9a3740`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/commit/772f011624c199adc021a61d039a4cf13e9a3740), dated 2026-09-25, with subject `merge: stage ZAVQERA integration without historical artifact`. The subject does not establish that the SQL is wrong, but this commit is not a per-migration deployment receipt and does not bridge the source filename `20260921180052` to hosted ledger version `20260921180138`.

**Updated interpretation:** current source bytes are recoverable in the captured checkout, but the path-history sweep does not recover the bytes bearing the 28 exact hosted-version filenames. This is a bounded reachable-history result, not proof that no such SQL ever existed in any deleted/unreachable ref, external repository, private/local clone, backup or deployment system. Do not populate deployed SQL digests or resolve the affected dispositions from this result alone. Keep the 22 conflicts and six hosted-only rows **OPEN / UNKNOWN**, and release **NO-GO**.


---

## 10. GitHub visible-branch source recovery — 2026-10-18

The supplementary scan [ZAVQERA_GITHUB_BRANCH_SOURCE_RECOVERY_SCAN_2026-10-18.md](ZAVQERA_GITHUB_BRANCH_SOURCE_RECOVERY_SCAN_2026-10-18.md) inspected all 23 branch tips returned by the original `abdalrhmanata-gif/Nexo` repository's branch listing at the scan time. All recursive trees were complete (`truncated=false`).

- No exact hosted filename was found for any of the 22 same-name/version conflicts or six hosted-only ledger tuples (0/28 contested paths across the 23 visible branch-tip trees).
- The 22 source-side conflict filenames were present in migration-bearing branch snapshots; the blob SHAs for each source-side conflict filename matched the scan baseline wherever present. No alternate source blob was observed in these visible branch tips.
- This is only current visible-ref/path/blob evidence. It does not scan deleted/unreachable Git objects, owner-device reflogs/stashes/unpushed refs, external/private repos, deployment artifacts or backups, and it does not prove what SQL was executed.

**Disposition unchanged:** All historical deployed-byte rows remain unresolved pending trusted deployment/source evidence. Do not rewrite the hosted ledger or infer equality from names. Release remains **NO-GO**, and no hosted change is authorized. The next recovery attempt must target the external/local artifact classes explicitly excluded by this scan, or record that the historic bytes cannot be established and design a separately reviewed re-baselining path.

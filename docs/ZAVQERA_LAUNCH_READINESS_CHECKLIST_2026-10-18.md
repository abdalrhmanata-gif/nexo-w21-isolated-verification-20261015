# ZAVQERA launch readiness checklist — 2026-10-18

## Release decision: NO-GO

**Release candidate SHA:** NONE (no release candidate selected; the review workspace still has an untracked local output directory)

Every gate below is mandatory. Status describes current evidence only; no older-SHA result is attributed to a newer source. `N/A` requires documented approval by the accountable owner and independent reviewer. A `PASS` is valid only for the exact source SHA and scope stated in its evidence field. No gate authorizes hosted writes, migration rollout, production deployment, or provider activation.

### Gate A — Candidate identity and reproducible verification

- **Status:** BLOCKED
- **Required evidence scope:** EXACT_CANDIDATE_CI
- **Exit condition:** A clean, explicitly selected release-candidate commit is recorded; all required build/test jobs pass on that exact SHA; artifacts identify the same SHA and are retained.
- **Evidence / exact source SHA:** W86/W80 run `39136888615`, SHA `e123ead90684b64a9809ad6d4ba7b8ddcb155155`, W86 25/25 and W80 49/49, artifact `12140396685` (disposable PostgreSQL 17.11 only). Recovery smoke run `39139497594`, SHA `dcffaf1a138b1ddfee596fbdc0c76081272ce985`, artifact `12141246974`. Current PR #3 source head `a7ecca32a989b90c6e2ddd0b63af678cbd9bc2db` passed Flutter CI run `39149257963` (PR run; full `verify` job succeeded, including Flutter app verification, adapter tests 20/20, Web Unit 372 passed / 0 failed / 1 skipped, typecheck, checklist validator and 31 Python tests). This isolated Draft-branch verification is not a selected release-candidate result or W21 evidence.
- **Accountable owner / independent reviewer:** Release owner / independent release reviewer (named assignment pending).
- **Stop condition:** Candidate SHA is missing, dirty, differs from CI evidence, or an artifact cannot be matched to it.
- **Closure action:** Select and freeze a clean candidate SHA, run only required jobs that lack exact-SHA evidence, inspect artifacts, and record the matching results and reviewer.

### Gate B — Application authorization and Mission Authority

- **Status:** BLOCKED
- **Required evidence scope:** RUNTIME_SECURITY_REVIEW
- **Exit condition:** Every privileged Mission Action path is authenticated and authorized before privileged resources or dispatch; denial/uncertainty tests prove zero provider calls; all in-scope external effects have documented authority boundaries and independent security approval.
- **Evidence / exact source SHA:** PR #39 head `9d752a59f0683ea7149633138dc85bb33cf9a41b`; W21 `39003340724`, Web Unit `39003340729`, Web CI `39003340878`, Flutter `39003340769` passed on that recorded head. This is scoped branch evidence; it does not prove universal Mission Authority enforcement.
- **Accountable owner / independent reviewer:** Application security owner / independent security reviewer (named assignment pending).
- **Stop condition:** Any privileged path bypasses authorization, uncertainty permits effects, or planning/research/email effects lack a reviewed boundary.
- **Closure action:** Inventory each external effect, fix any demonstrated bypass with regression tests, and obtain independent review against a frozen source SHA.

### Gate C — Dispatch, idempotency, and provider safety

- **Status:** BLOCKED
- **Required evidence scope:** PROVIDER_CONTRACT_REVIEW
- **Exit condition:** Production dispatch remains fail-closed until adapter registration is explicitly authorized; enabled adapters, if any, prove authenticated receipts, idempotency, authoritative reconciliation, safe handling of UNKNOWN, and crash recovery in isolated tests and provider-specific review.
- **Evidence / exact source SHA:** PR #39 source `9d752a59f0683ea7149633138dc85bb33cf9a41b`; `TRUSTED_DISPATCH_ADAPTERS` is empty/fail-closed on that source. Fake-provider tests are not proof of real-provider guarantees.
- **Accountable owner / independent reviewer:** Dispatch security owner and provider integration owner / independent security reviewer (named assignments pending).
- **Stop condition:** Registry is non-empty without approval, a denial/UNKNOWN path can call or retry a provider, or real-provider semantics lack evidence.
- **Closure action:** Keep registry empty; separately approve a provider-specific contract, implement only after approval, and verify with isolated contract tests and independent review before activation.

### Gate D — Hosted database privileges and schema state

- **Status:** BLOCKED
- **Required evidence scope:** HOSTED_READ_ONLY_CAPTURE
- **Exit condition:** The recorded Development capture and relevant schema/privilege findings receive independent database-platform review, all privilege and contract differences receive evidence-backed dispositions against an approved target, and any final-candidate snapshot is captured and reviewed before release authorization. A capture alone does not satisfy this gate.
- **Evidence / exact source SHA:** The persisted 2026-10-17 13-query capture review is [PR #2 comment 6235721455](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6235721455); report, remediation plan and evidence status are linked in [comment 6235818612](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6235818612) and [database-owner assessment 6248200418](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6248200418). Capture ZIP SHA-256 `9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d`; base query pack SHA-256 `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`; query 13 SHA-256 `806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b`. The offline report records capture source HEAD `fbbcb080904acd88aad83a082803f627859026e2`, migration-manifest SHA-256 `0d05ab7285edc975084ddbc595d1af7d2dd0752cc27e94d8fe0549170419be38`, project `mrwmmbytcymqgwvcoywd` / `ZAVQERA Development`, region `eu-west-1`, and PostgreSQL 17.6. Reported findings: direct `service_role` grants for all eight `agent_executions` table privileges while RLS is enabled but not forced; two expected relations, 26 columns, 10/11 constraints, eight indexes and a receipt-guard trigger missing; 23/40 routine expectation rows mismatched; eight explicit default EXECUTE ACL rows; and migration reconciliation counts of 89 source files / 74 ledger rows, 46 exact matches, 22 version conflicts, six hosted-only names, and 43 source tuples absent from the ledger. Query 13 found no inherited `service_role` table/column ACL entries or path to `authenticated`/the table owner; this clears only that captured parent-role-path preflight. The capture role also reported `rolbypassrls=true`, requiring owner confirmation of restricted, metadata-only use. The owner disposition is **REVIEWED — MORE EVIDENCE REQUIRED**, not independent approval. The archived report says ZIP integrity passed; this turn did not independently recompute that archive hash.
- **Accountable owner / independent reviewer:** Authorized Development database owner / independent database-platform reviewer (named assignments pending).
- **Stop condition:** Identity, region, read-only role, query/hash/count, ACL, role-membership path, routine grant, or provenance check is wrong, missing, or uncertain.
- **Closure action:** Obtain independent review of the persisted capture, owner confirmation of capture-role handling, and documented dispositions for each privilege/schema/function mismatch. Keep hosted writes unauthorized; do not apply W86 or other migrations based on the parent-path result alone.

### Gate E — Historical migration provenance

- **Status:** BLOCKED
- **Required evidence scope:** AUTHORITATIVE_MIGRATION_PROVENANCE
- **Exit condition:** Every current migration and hosted ledger entry has an evidence-backed mapping, including historical rename/timestamp changes; SQL effects are classified as confirmed, likely, or unresolved, and no unresolved item is treated as equivalent.
- **Evidence / exact source SHA:** Historical W86 review checkpoint `61208ffcdb3a6154aa616cdd152b78221bbeaca6` contains `docs/ZAVQERA_HOSTED_MIGRATION_HISTORY_RECONCILIATION_2026-10-15.md`; that report is not part of this isolated launch branch. Its recorded unresolved set is 22 timestamp conflicts and six hosted-only ledger names without recoverable exact-path SQL in reviewed refs. The report is historical evidence, not proof of deployed SQL equivalence.
- **Accountable owner / independent reviewer:** Migration-history owner / independent database-platform reviewer (named assignments pending).
- **Stop condition:** Any ledger version/name lacks authoritative source/deployment evidence or a proposed mapping depends on guessed SQL equivalence.
- **Closure action:** Obtain authoritative historical SQL/deployment records, reconcile each item with provenance, and independently review the mapping before any separately authorized rollout proposal.

### Gate F — Read-only Development audit and owner review

- **Status:** BLOCKED
- **Required evidence scope:** HOSTED_READ_ONLY_CAPTURE_AND_REVIEW
- **Exit condition:** A complete capture for the approved target is preserved with verifiable identity, role/read-only state, query hashes/count and outputs; an independent database-platform reviewer records findings and evidence-backed dispositions. Refresh only for final-candidate verification after the target state is defined, or if the Development state changes before that review; the existing 2026-10-17 capture is not absent and should not be repeated merely due to stale checklist text.
- **Evidence / exact source SHA:** Existing capture/review is documented at [PR #2 comment 6235721455](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6235721455); persisted report/remediation plan at [comment 6235818612](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6235818612); owner assessment at [comment 6248200418](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6248200418). ZIP SHA-256 `9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d`; base pack `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`; query 13 `806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b`; recorded capture-source HEAD `fbbcb080904acd88aad83a082803f627859026e2`; migration manifest `0d05ab7285edc975084ddbc595d1af7d2dd0752cc27e94d8fe0549170419be38`. Capture integrity/read-only gates are reported as passed in the offline review, but its role had `rolbypassrls=true`; owner confirmation and independent review remain outstanding. Owner status is **REVIEWED — MORE EVIDENCE REQUIRED**.
- **Accountable owner / independent reviewer:** Authorized Development database owner / independent database-platform reviewer (named assignments pending).
- **Stop condition:** Wrong project/region, non-read-only role, hash/count mismatch, missing result, token exposure, privilege path, or provenance anomaly.
- **Closure action:** First obtain a qualified independent reviewer for the existing package and require explicit dispositions for all listed findings. Use the pinned procedure below for a new capture only at final-candidate verification or after a material Development-state change; preserve NO-GO on any mismatch.

### Gate G — Backup and recovery readiness

- **Status:** BLOCKED
- **Required evidence scope:** APPLICATION_BACKUP_RESTORE
- **Exit condition:** An authorized, isolated restore rehearsal restores the approved application backup and verifies required schema, roles, extensions, auth/storage dependencies, representative synthetic data, and application operation; backup retention and measured RPO/RTO are approved and evidenced.
- **Evidence / exact source SHA:** W80 recovery smoke run `39139497594`, source SHA `dcffaf1a138b1ddfee596fbdc0c76081272ce985`, artifact `12141246974`: synthetic PostgreSQL 17.11 custom-format dump/restore verified two parent rows, two child rows, five constraints, and fixture cleanup. It is not full application recovery or backup-retention/RPO/RTO evidence.
- **Accountable owner / independent reviewer:** Backup/recovery owner / independent recovery reviewer (named assignments pending).
- **Stop condition:** Rehearsal uses hosted/customer data, restore is incomplete, required dependencies are absent, integrity checks fail, or recovery objectives are unmeasured.
- **Closure action:** Define an authorized isolated backup source and recovery objectives, run an end-to-end restore drill with synthetic or approved data, capture verification/cleanup evidence, and obtain independent review.

### Gate H — Production operations and incident readiness

- **Status:** BLOCKED
- **Required evidence scope:** OPERATIONAL_EXERCISE
- **Exit condition:** Production runbooks, alert ownership, incident escalation, rollback/recovery procedures, access controls, and operational acceptance are reviewed and exercised for the approved release candidate.
- **Evidence / exact source SHA:** Operations guide [`ZAVQERA_LAUNCH_RUNBOOK.md`](ZAVQERA_LAUNCH_RUNBOOK.md) is present at launch branch source `ea35fa39da580ac26881e1005ff439942aeaacd0`. No production exercise or operational acceptance is evidenced by the cited W80/W86 runs.
- **Accountable owner / independent reviewer:** Operations owner and incident-response owner / independent operations reviewer (named assignments pending).
- **Stop condition:** Any critical alert/runbook lacks an accountable responder, rollback cannot be exercised safely, or production access/recovery procedure is unreviewed.
- **Closure action:** Assign owners, exercise the procedures in a non-production environment, record results and remediate failures before independent operational sign-off.

### Gate I — User-facing flow and support acceptance

- **Status:** BLOCKED
- **Required evidence scope:** END_TO_END_ACCEPTANCE
- **Exit condition:** Each launch-promised user flow is classified as end-to-end, prototype, or UI-only; critical supported flows pass on the release candidate, and product, privacy, accessibility, and support acceptance is recorded.
- **Evidence / exact source SHA:** PR #39 application test evidence is scoped to `9d752a59f0683ea7149633138dc85bb33cf9a41b` and its listed CI runs. No complete release-candidate flow inventory or named product/privacy/accessibility/support acceptance is recorded here.
- **Accountable owner / independent reviewer:** Product owner and support/accessibility/privacy owners / independent QA reviewer (named assignments pending).
- **Stop condition:** A launch-promised flow is prototype/UI-only without disclosure, a critical flow fails, or required owner acceptance is absent.
- **Closure action:** Inventory and classify promised flows, verify critical paths on the frozen candidate, resolve findings, and record owner acceptance with evidence.

### Gate J — Independent release authorization

- **Status:** BLOCKED
- **Required evidence scope:** INDEPENDENT_RELEASE_APPROVAL
- **Exit condition:** Gates A-I are PASS or explicitly approved N/A with evidence, all mandatory independent reviews are recorded against the exact release-candidate SHA, and the authorized release owner records a go decision.
- **Evidence / exact source SHA:** Current published PR #3 source head `a7ecca32a989b90c6e2ddd0b63af678cbd9bc2db` has passing Flutter CI run `39149257963`. PR #3 remains open / Draft / unmerged, has no submitted review and no requested individual or team reviewer, and the PR author is the repository owner. Public Issue #4 requests a review of the validator/CI changes but has no comments or recorded reviewer activity; it is not database or release approval. No independent reviewer is established, no release candidate or release authorization is selected, and prior artifacts remain scoped to their exact commits above.
- **Accountable owner / independent reviewer:** Authorized release owner / independent security, database, recovery, and operations reviewers (named assignments pending).
- **Stop condition:** Any mandatory gate is FAIL/BLOCKED, evidence SHA is stale or absent, an approval is missing, or a safety constraint is violated.
- **Closure action:** Close each prerequisite gate, assemble the evidence index keyed by exact SHA, obtain independent approvals, and record the authorized decision. Until then, keep release NO-GO.

## State and safety constraints

- Live GitHub state checked 2026-10-18: original Nexo PR #1 and #2 are closed/merged (pre-existing); PR #39 is OPEN / Draft / unmerged at `9d752a59f0683ea7149633138dc85bb33cf9a41b`; Issue #23 is OPEN. No PR or issue state was changed in this work.
- Isolated verification PR #1 is OPEN / Draft / unmerged at `e123ead90684b64a9809ad6d4ba7b8ddcb155155`; isolated audit PR #2 is OPEN / Draft / unmerged at `a3d68afb31a8c0ef373f7810e05a1286c30048dd`.
- Isolated launch-readiness PR #3 is OPEN / Draft / unmerged at `a7ecca32a989b90c6e2ddd0b63af678cbd9bc2db`; Flutter CI run `39149257963` succeeded. No independent review or reviewer request is recorded.
- `hosted_write_authorized=false`. No hosted Development/Production writes, migrations, ledger edits, provider calls, emails, deployment, DNS, billing, or credential handling are authorized by this checklist. Keep `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed.
- W80/W86 results are disposable/repository evidence only. They do not establish hosted parity, universal production egress, real-provider guarantees, complete application recovery, backup retention, RPO/RTO, or launch authorization.

## Single next action

Obtain a qualified independent database-platform reviewer to review the existing 2026-10-17 capture and the 2026-10-18 owner assessment, then record evidence-backed dispositions for each unresolved ACL, schema, routine, default-privilege, capture-role, and migration-provenance finding. Public [Issue #4](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/issues/4) requests review of PR #3's validator and CI classification; it is not a database-evidence review request and cannot satisfy Gates D/F. No qualified database reviewer or approval is inferred.

## Pinned 13-query procedure for future final-candidate verification

The guarded runner, query pack, secure PowerShell wrapper, and offline reviewer are in isolated audit PR #2 at exact head `a3d68afb31a8c0ef373f7810e05a1286c30048dd`. Query pack SHA-256 is `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`; query 13 SHA-256 is `806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b`. A complete capture already exists for 2026-10-17. Do not run this procedure now merely to recreate it; use it for a fresh final-candidate snapshot once the target is frozen and immediately before final review/any separately authorized rollout decision, or sooner only if the Development state materially changes. It does not authorize a hosted write.

Run in a new PowerShell window from a parent folder suitable for a clean disposable checkout. The wrapper prompts for the project-scoped read-only Management API token using hidden input; never put a token in the command, chat, files, arguments, or shell history.

```powershell
$repoUrl = "https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015.git"
$branch = "codex/migration-ledger-provenance-20261015"
$expectedSha = "a3d68afb31a8c0ef373f7810e05a1286c30048dd"
$auditRoot = Join-Path (Get-Location) "nexo-w21-isolated-audit-13q-a3d68"
if (Test-Path -LiteralPath $auditRoot) { throw "Choose a new empty sibling directory; existing data is preserved." }

git clone --no-checkout $repoUrl $auditRoot
if ($LASTEXITCODE -ne 0) { throw "Clone failed; stop." }
git -C $auditRoot fetch --no-tags origin $branch
if ($LASTEXITCODE -ne 0) { throw "Audit branch fetch failed; stop." }
git -C $auditRoot checkout --detach $expectedSha
if ($LASTEXITCODE -ne 0) { throw "Exact reviewed audit SHA checkout failed; stop." }
$actualSha = (git -C $auditRoot rev-parse HEAD).Trim()
if ($actualSha -ne $expectedSha) { throw "Expected $expectedSha, got $actualSha; stop." }
git -C $auditRoot status --short --branch

Push-Location $auditRoot
try {
    py -3 .\tools\supabase_readonly_migration_effect_audit.py --self-test
    if ($LASTEXITCODE -ne 0) { throw "13-query no-network self-test failed; do not connect." }
    py -3 -m unittest discover -s tests -p "test_supabase_readonly_migration_effect_audit.py" -v
    if ($LASTEXITCODE -ne 0) { throw "Runner tests failed; do not connect." }
    py -3 -m unittest discover -s tests -p "test_review_hosted_migration_ledger.py" -v
    if ($LASTEXITCODE -ne 0) { throw "Offline reviewer tests failed; do not connect." }
    powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\run_zavqera_readonly_effect_audit.ps1
    if ($LASTEXITCODE -ne 0) { throw "Capture stopped or wrapper failed; preserve partial evidence and stop." }
} finally {
    Pop-Location
}
```

The only intended target is Development ref `mrwmmbytcymqgwvcoywd` (`eu-west-1`) through the pinned Management API `/database/query/read-only` endpoint. The helper removes the token from its process environment and zeroes the temporary BSTR before invoking the offline reviewer. It makes no database writes. Do not use a generic SQL endpoint or substitute another query pack.

### Owner evidence review and stop conditions

- Require the self-test to report `SELF_TEST=PASS`, `queries=13`, both exact hashes above, and no network requests. Require both unittest commands and the wrapper to exit 0; preserve console output and inspect the offline review result.
- Inspect the evidence ZIP before sharing. It must contain one capture, a `CAPTURED_FOR_MANUAL_REVIEW` summary with `queries_completed=13`, `query_01.json` through `query_13.json`, project identity, run metadata, read-only gate, and `ledger_acl_review.json` / `.md`. Confirm token-saved fields are false and no token, connection config, shell history, or application-row data is included.
- Confirm project ID/name/region exactly match `mrwmmbytcymqgwvcoywd` / `ZAVQERA Development` / `eu-west-1`; query 1 shows `current_user=supabase_read_only_user` and `transaction_read_only=true`.
- Confirm both pack hashes; query 11 contains only ledger version/name tuples; query 12 is W66 ACL evidence; query 13 includes `public.agent_executions` owner/effective privileges, service-role membership paths with INHERIT/SET ROLE semantics, and inherited table/column ACL provenance.
- Stop and keep NO-GO on wrong project/region, role/read-only failure, hash/count mismatch, missing/unknown query, token leakage, inherited `service_role` table/column ACL, or a path to table-owner authority through INHERIT or SET ROLE. Preserve partial evidence; do not alter the runner/query or retry through a more privileged endpoint.
- Even if all 13 queries capture without an inherited ACL, the offline reviewer remains `REVIEW REQUIRED / NO-GO`. An independent database/platform owner must review role paths, owner identity, routine signatures/owners/security modes/search paths/EXECUTE grants, W66 ACLs, default ACLs, ledger mappings, and historical SQL provenance. This does not authorize hosted migration or privilege changes.

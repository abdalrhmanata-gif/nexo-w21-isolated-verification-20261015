# ZAVQERA launch readiness checklist — 2026-10-18

## Release decision: NO-GO

**Release candidate SHA:** NONE (current checkout is dirty; no release candidate selected)

Every gate below is mandatory. Status describes current evidence only; no older-SHA result is attributed to a newer source. `N/A` requires documented approval by the accountable owner and independent reviewer. A `PASS` is valid only for the exact source SHA and scope stated in its evidence field. No gate authorizes hosted writes, migration rollout, production deployment, or provider activation.

### Gate A — Candidate identity and reproducible verification

- **Status:** BLOCKED
- **Required evidence scope:** EXACT_CANDIDATE_CI
- **Exit condition:** A clean, explicitly selected release-candidate commit is recorded; all required build/test jobs pass on that exact SHA; artifacts identify the same SHA and are retained.
- **Evidence / exact source SHA:** W86/W80 run `39136888615`, SHA `e123ead90684b64a9809ad6d4ba7b8ddcb155155`, W86 25/25 and W80 49/49, artifact `12140396685` (disposable PostgreSQL 17.11 only). Recovery smoke run `39139497594`, SHA `dcffaf1a138b1ddfee596fbdc0c76081272ce985`, artifact `12141246974`. Current review checkout HEAD `61208ffcdb3a6154aa616cdd152b78221bbeaca6` has uncommitted changes; it is not a tested release candidate.
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
- **Exit condition:** The authorized owner captures current Development state using the pinned 13-query read-only audit; project identity, effective role/read-only state, routine grants, ACLs, and migration ledger are independently reviewed with no unexplained privilege path or schema discrepancy.
- **Evidence / exact source SHA:** Candidate W86 W80 run `39136888615` tested SHA `e123ead90684b64a9809ad6d4ba7b8ddcb155155` only in disposable PostgreSQL. Audit runner branch PR #2 head `a3d68afb31a8c0ef373f7810e05a1286c30048dd`; no fresh 13-query hosted capture is recorded here. Prior recorded hosted W66 observation showed all eight queried `service_role` table privileges, including INSERT/UPDATE/DELETE/TRUNCATE.
- **Accountable owner / independent reviewer:** Authorized Development database owner / independent database-platform reviewer (named assignments pending).
- **Stop condition:** Identity, region, read-only role, query/hash/count, ACL, role-membership path, routine grant, or provenance check is wrong, missing, or uncertain.
- **Closure action:** Owner runs the pinned read-only capture from a clean checkout and an independent reviewer signs off on complete evidence. Do not make hosted changes under this checklist.

### Gate E — Historical migration provenance

- **Status:** BLOCKED
- **Required evidence scope:** AUTHORITATIVE_MIGRATION_PROVENANCE
- **Exit condition:** Every current migration and hosted ledger entry has an evidence-backed mapping, including historical rename/timestamp changes; SQL effects are classified as confirmed, likely, or unresolved, and no unresolved item is treated as equivalent.
- **Evidence / exact source SHA:** Reconciliation material in the current review checkout at `61208ffcdb3a6154aa616cdd152b78221bbeaca6`; recorded unresolved set is 22 timestamp conflicts and six hosted-only ledger names without recoverable exact-path SQL in reviewed refs. This documentation checkout has uncommitted changes and is not a tested release candidate.
- **Accountable owner / independent reviewer:** Migration-history owner / independent database-platform reviewer (named assignments pending).
- **Stop condition:** Any ledger version/name lacks authoritative source/deployment evidence or a proposed mapping depends on guessed SQL equivalence.
- **Closure action:** Obtain authoritative historical SQL/deployment records, reconcile each item with provenance, and independently review the mapping before any separately authorized rollout proposal.

### Gate F — Read-only Development audit and owner review

- **Status:** BLOCKED
- **Required evidence scope:** HOSTED_READ_ONLY_CAPTURE_AND_REVIEW
- **Exit condition:** The pinned 13-query pack runs against the exact intended Development project through the read-only endpoint; all expected outputs and hashes are present; an independent owner reviews the result and records a decision.
- **Evidence / exact source SHA:** Audit branch PR #2 head `a3d68afb31a8c0ef373f7810e05a1286c30048dd`; pinned base pack SHA-256 `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`, query 13 SHA-256 `806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b`. This is prepared tooling, not evidence of a fresh capture.
- **Accountable owner / independent reviewer:** Authorized Development database owner / independent database-platform reviewer (named assignments pending).
- **Stop condition:** Wrong project/region, non-read-only role, hash/count mismatch, missing result, token exposure, privilege path, or provenance anomaly.
- **Closure action:** Run the owner procedure in a clean checkout, inspect the evidence package for identity, query completeness, hashes and secret absence, then record independent review. Preserve NO-GO on any mismatch.

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
- **Evidence / exact source SHA:** Operations guide in the current review checkout at `61208ffcdb3a6154aa616cdd152b78221bbeaca6`; current checkout has uncommitted changes. No production exercise or operational acceptance is evidenced by the cited W80/W86 runs.
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
- **Evidence / exact source SHA:** Current review checkout HEAD `61208ffcdb3a6154aa616cdd152b78221bbeaca6` is dirty and is not a release candidate. Prior exact-SHA artifacts are scoped to their respective commits above. No release authorization is recorded.
- **Accountable owner / independent reviewer:** Authorized release owner / independent security, database, recovery, and operations reviewers (named assignments pending).
- **Stop condition:** Any mandatory gate is FAIL/BLOCKED, evidence SHA is stale or absent, an approval is missing, or a safety constraint is violated.
- **Closure action:** Close each prerequisite gate, assemble the evidence index keyed by exact SHA, obtain independent approvals, and record the authorized decision. Until then, keep release NO-GO.

## State and safety constraints

- Live GitHub state checked 2026-10-18: original Nexo PR #1 and #2 are closed/merged (pre-existing); PR #39 is OPEN / Draft / unmerged at `9d752a59f0683ea7149633138dc85bb33cf9a41b`; Issue #23 is OPEN. No PR or issue state was changed in this work.
- Isolated verification PR #1 is OPEN / Draft / unmerged at `e123ead90684b64a9809ad6d4ba7b8ddcb155155`; isolated audit PR #2 is OPEN / Draft / unmerged at `a3d68afb31a8c0ef373f7810e05a1286c30048dd`.
- `hosted_write_authorized=false`. No hosted Development/Production writes, migrations, ledger edits, provider calls, emails, deployment, DNS, billing, or credential handling are authorized by this checklist. Keep `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed.
- W80/W86 results are disposable/repository evidence only. They do not establish hosted parity, universal production egress, real-provider guarantees, complete application recovery, backup retention, RPO/RTO, or launch authorization.

## Single next action

The authorized Development database owner should run and independently review the pinned 13-query read-only capture at audit branch PR #2 SHA `a3d68afb31a8c0ef373f7810e05a1286c30048dd`, using the owner procedure below. Stop on any identity, read-only, hash, ACL, role-path, or provenance mismatch. This action requires no hosted write and does not authorize remediation.

## Prepared owner-run 13-query Development audit

The pinned audit runner, query pack, secure PowerShell wrapper, and offline reviewer are in isolated audit PR #2 at exact head `a3d68afb31a8c0ef373f7810e05a1286c30048dd`. Query pack SHA-256 is `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`; query 13 SHA-256 is `806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b`. This is prepared tooling, not a fresh hosted capture.

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

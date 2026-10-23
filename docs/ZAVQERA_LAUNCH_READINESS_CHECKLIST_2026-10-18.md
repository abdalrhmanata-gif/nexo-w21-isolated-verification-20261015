# ZAVQERA launch readiness checklist — 2026-10-18

## Release decision: NO-GO

**Release candidate SHA:** NONE (no release candidate selected; the review workspace still has an untracked local output directory)

Every gate below is mandatory. Status describes current evidence only; no older-SHA result is attributed to a newer source. `N/A` requires documented approval by the accountable owner and independent reviewer. A `PASS` is valid only for the exact source SHA and scope stated in its evidence field. No gate authorizes hosted writes, migration rollout, production deployment, or provider activation.

**Status correction — 2026-10-20:** Isolated audit PR #2 (`codex/migration-ledger-provenance-20261015`, HEAD `73ac8f13a4f31848a380d14f00f4459d82a3b2f5`) is now **MERGED**. This preserves the audit artifacts only; it does not represent independent database-owner approval or resolve migration provenance. Launch-readiness PR #3 remains **OPEN / Draft / Unmerged** at the current reviewed head, and no independent review submission is recorded. All gates remain BLOCKED; `candidate_sha=NONE`, `hosted_write_authorized=false`, and release remains NO-GO.


### Gate A — Candidate identity and reproducible verification

- **Status:** BLOCKED
- **Required evidence scope:** EXACT_CANDIDATE_CI
- **Exit condition:** A clean, explicitly selected release-candidate commit is recorded; all required build/test jobs pass on that exact SHA; artifacts identify the same SHA and are retained.
- **Evidence / exact source SHA:** Latest verified code/test SHA `ed7f06d6d731967ab47f7ecf7af6d68b0dbeb34f`; later commits in this branch update documentation only and do not modify the restore script, application/test code, or CI workflows. Exact-head [W21 run `39246765511`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39246765511) passed 27/27 steps (evidence artifact [`12184505245`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39246765511/artifacts/12184505245)); [Web Unit `39246770477`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39246770477), [Web CI `39246770487`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39246770487), and [Flutter CI `39246770614`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39246770614) all passed on the same SHA. Browser E2E passed 2/2; extension inventory and extension-schema relation signatures matched in the disposable restore smoke; fixture, dump, temporary restore database, containers and volumes were cleaned up. This is isolated Draft-branch validation only: `candidate_sha=NONE`; no approved release candidate or independent approval exists.
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
- **Evidence / exact source SHA:** The persisted 2026-10-17 13-query capture review is [PR #2 comment 6235721455](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6235721455); report, remediation plan and evidence status are linked in [comment 6235818612](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6235818612) and [database-owner assessment 6248200418](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6248200418). Capture ZIP SHA-256 `9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d`; base query pack SHA-256 `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`; query 13 SHA-256 `806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b`. The offline report records capture source HEAD `fbbcb080904acd88aad83a082803f627859026e2`, migration-manifest SHA-256 `0d05ab7285edc975084ddbc595d1af7d2dd0752cc27e94d8fe0549170419be38`, project `mrwmmbytcymqgwvcoywd` / `ZAVQERA Development`, region `eu-west-1`, and PostgreSQL 17.6. Reported findings: direct `service_role` grants for all eight `agent_executions` table privileges while RLS is enabled but not forced; two expected relations, 26 columns, 10/11 constraints, eight indexes and a receipt-guard trigger missing; 23/40 routine expectation rows mismatched; eight explicit default EXECUTE ACL rows; and migration reconciliation counts of 89 source files / 74 ledger rows, 46 exact matches, 22 version conflicts, six hosted-only names, and 43 source tuples absent from the ledger. Query 13 found no inherited `service_role` table/column ACL entries or path to `authenticated`/the table owner; this clears only that captured parent-role-path preflight. The capture role also reported `rolbypassrls=true`, requiring owner confirmation of restricted, metadata-only use. The owner disposition is **REVIEWED — MORE EVIDENCE REQUIRED**, not independent approval. The user-supplied handoff ZIP was rechecked locally: outer bundle SHA-256 `73b70bff63a6a2517f8c1f8c945103586fc06ce6713741bc904dd2fa2bbebe68`; all 19 entries listed in `SHA256SUMS.txt` matched; embedded capture ZIP SHA-256 `9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d`; ZIP CRC validation passed and `query_01.json` through `query_13.json` are present. A heuristic scan found no recognizable API-token, JWT, or PostgreSQL-URI credential patterns; this is not a complete sensitivity/redaction review. The archive is available in this local Codex session but has not been delivered to an independent reviewer. Do not publish it publicly; provide it through an appropriate private channel after a human sensitivity review.
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
- **Evidence / exact source SHA:** Exact-head [W21 run `39246765511`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39246765511) on `ed7f06d6d731967ab47f7ecf7af6d68b0dbeb34f` passed 27/27 steps; [evidence artifact `12184505245`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39246765511/artifacts/12184505245). The synthetic PostgreSQL 17 restore smoke returned `restore_smoke=PASS`: 52 source/52 restored application/auth/migration relations; source/restored signatures matched for the synthetic auth user/profile, workspace owner membership, DRAFT mission and two ordered PENDING actions; auth-profile trigger was enabled and application trigger modes matched. Extension parity is now proven within this isolated test: 2 source/2 restored relations (`pg_stat_statements`, `pg_stat_statements_info`) and identical inventory (`pg_stat_statements 1.11`, `pgcrypto 1.3`, `uuid-ossp 1.1`). Browser E2E passed 2/2 in 2.2 minutes. Synthetic fixture, source sentinel, dump and temporary restore database were removed; `restore_cleanup_verified=true`, `remaining_containers=none`, `remaining_volumes=none`. The one synthetic user had no auth identity row; this is not representative production-user-data recovery, full managed Supabase/Storage recovery, retained off-site backup proof or measured RPO/RTO. Independent recovery review and operational acceptance remain missing, so this gate remains BLOCKED.
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
- **Evidence / exact source SHA:** Current isolated PR #3 source head `c9c4afbc47732472cd267a7680f1ca091a25c652` has passing Web Unit `39306737378`, Web CI `39306737247`, and Flutter CI `39306737356`. The exact-code W21 run remains `39246765511` on `ed7f06d6d731967ab47f7ecf7af6d68b0dbeb34f`; the only later changes through `c9c4afb` are three documentation files, so W21 is not attributed to `c9c4afb`. PR #3 is OPEN / Draft / Unmerged, with no requested reviewer and no submitted review. Issue #4 is OPEN; its two comments are owner-authored invitations and there is no independent response. No independent reviewer or release authorization is established, and all artifacts remain scoped to their recorded commits.
- **Accountable owner / independent reviewer:** Authorized release owner / independent security, database, recovery, and operations reviewers (named assignments pending).
- **Stop condition:** Any mandatory gate is FAIL/BLOCKED, evidence SHA is stale or absent, an approval is missing, or a safety constraint is violated.
- **Closure action:** Close each prerequisite gate, assemble the evidence index keyed by exact SHA, obtain independent approvals, and record the authorized decision. Until then, keep release NO-GO.

## State and safety constraints

- Live GitHub state checked 2026-10-20: canonical Nexo PR #39 is OPEN / Draft / unmerged at `9d752a59f0683ea7149633138dc85bb33cf9a41b`; PR #40 is OPEN / Draft / unmerged at `3c9a9ab11a22c39ae270ff0ae1efea94e0627976`; Issue #23 remains OPEN. PR #40 was updated only by fast-forward; it was not marked ready or merged.
- Isolated PR #1 is OPEN / Draft / unmerged at `e123ead90684b64a9809ad6d4ba7b8ddcb155155`; PR #2 at `73ac8f13a4f31848a380d14f00f4459d82a3b2f5`; and PR #3 at `c9c4afbc47732472cd267a7680f1ca091a25c652`. All three have no submitted reviews. PR #3 has no requested reviewer; Issue #4 is OPEN with two owner-authored invitations and no independent response.
- PR #3 exact-head Web Unit `39306737378`, Web CI `39306737247`, and Flutter CI `39306737356` succeeded. W21 remains exact-code SHA `ed7f06d6d731967ab47f7ecf7af6d68b0dbeb34f`, run `39246765511`; only three documentation files differ through `c9c4afb`. PR #40 baseline `fcaf4b0b2b5f9bb09f2b3a47988e8f66bacb0201` passed Web Unit `39308859605`, Web CI `39308859627`, Flutter CI `39308859494`, and W83 `39308859609` with 28/28. Updated PR head `3c9a9ab11a22c39ae270ff0ae1efea94e0627976` passed Web Unit `39408110877`, Web CI `39408110602`, Flutter CI `39408110868`, and W83 `39408110610`. Artifact `12257454881` (digest `sha256:b900a957ae54dffbd8580e4ee77f8c0d94c148391e3f58368fd4fe797d1bfecf`) records disposable PostgreSQL 17.11, 43/43 pgTAP, successful replay through and after W83, REST wrapper checks, and verified cleanup. Its tested merge-ref source SHA is `78d880b8aa53a83146f866b7bb9a369b085eda82`; this is isolated CI evidence, not hosted parity or migration approval.
- `hosted_write_authorized=false`. No hosted Development/Production writes, migrations, ledger edits, provider calls, emails, deployment, DNS, billing, or credential handling are authorized by this checklist. Keep `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed.
- W80/W86 results are disposable/repository evidence only. They do not establish hosted parity, universal production egress, real-provider guarantees, complete application recovery, backup retention, RPO/RTO, or launch authorization.

## Single next action

Obtain a qualified independent database-platform reviewer to inspect the reported 2026-10-17 capture, persisted findings, the 2026-10-18 owner assessment, and the 2026-10-20 catalog spot-check, then record evidence-backed dispositions for each unresolved ACL, schema, routine, default-privilege, capture-role, and migration-provenance finding. The capture comment records ZIP SHA-256 `9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d`, but the raw ZIP is not available through the fetched PR comment/files or checked validation artifacts here; treat its hash and findings as owner-reported until a reviewer inspects the archive. Public [Issue #4](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/issues/4) requests review of PR #3's validator and CI classification; it is not a database-evidence review request and cannot satisfy Gates D/F. No qualified database reviewer or approval is inferred.

## Pinned 13-query procedure for future final-candidate verification

The guarded runner, query pack, secure PowerShell wrapper, and offline reviewer are in isolated audit PR #2 at exact head `a3d68afb31a8c0ef373f7810e05a1286c30048dd`. Query pack SHA-256 is `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`; query 13 SHA-256 is `806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b`. A complete capture already exists for 2026-10-17. Do not run this procedure now merely to recreate it; use it for a fresh final-candidate snapshot once the target is frozen and immediately before final review/any separately authorized rollout decision, or sooner only if the Development state materially changes. It does not authorize a hosted write.

Run in a new PowerShell window from a parent folder suitable for a clean disposable checkout. The wrapper prompts for the project-scoped read-only Management API token using hidden input; never put a token in the command, chat, files, arguments, or shell history.

```powershell
$repoUrl = "https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015.git"
$branch = "codex/migration-ledger-provenance-20261015"
$expectedSha = "73ac8f13a4f31848a380d14f00f4459d82a3b2f5"
$auditRoot = Join-Path (Get-Location) "nexo-w21-isolated-audit-13q-73ac8"
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

The only intended target is Development ref `mrwmmbytcymqgwvcoywd` (`eu-west-1`) through the pinned Management API `/database/query/read-only` endpoint. Use a project-scoped token for this project only, with exactly **Project Settings: Read** and **Database: Read**. If scoped permissions are unavailable, stop; do not use a classic PAT. The helper removes the token from its process environment and zeroes the temporary BSTR before invoking the offline reviewer. It makes no database writes. Do not use a generic SQL endpoint or substitute another query pack.

### Owner evidence review and stop conditions

- Require the self-test to report `SELF_TEST=PASS`, `queries=13`, both exact hashes above, and no network requests. Require both unittest commands and the wrapper to exit 0; preserve console output and inspect the offline review result.
- Inspect the evidence ZIP before sharing. It must contain one capture, a `CAPTURED_FOR_MANUAL_REVIEW` summary with `queries_completed=13`, `query_01.json` through `query_13.json`, project identity, run metadata, read-only gate, and `ledger_acl_review.json` / `.md`. Confirm token-saved fields are false and no token, connection config, shell history, or application-row data is included.
- Confirm project ID/name/region exactly match `mrwmmbytcymqgwvcoywd` / `ZAVQERA Development` / `eu-west-1`; query 1 shows `current_user=supabase_read_only_user` and `transaction_read_only=true`.
- Confirm both pack hashes; query 11 contains only ledger version/name tuples; query 12 is W66 ACL evidence; query 13 includes `public.agent_executions` owner/effective privileges, service-role membership paths with INHERIT/SET ROLE semantics, and inherited table/column ACL provenance.
- Stop and keep NO-GO on wrong project/region, role/read-only failure, hash/count mismatch, missing/unknown query, token leakage, inherited `service_role` table/column ACL, or a path to table-owner authority through INHERIT or SET ROLE. Preserve partial evidence; do not alter the runner/query or retry through a more privileged endpoint.

## Latest verified code/test-head evidence — 2026-10-19

All four automated CI workflows passed on exact HEAD `ed7f06d6d731967ab47f7ecf7af6d68b0dbeb34f`:
- [W21 Local Launch Gate `39246765511`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39246765511) — **SUCCESS, 27/27 steps**; [evidence artifact `12184505245`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39246765511/artifacts/12184505245).
- [Web Unit `39246770477`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39246770477), [Web CI `39246770487`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39246770487), and [Flutter CI `39246770614`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39246770614) — all **SUCCESS** on that same SHA.
- Browser E2E: **2 passed (2.2 minutes)**. Isolated PostgreSQL 17 pgTAP, Mission Authority, quota/workspace security, four actual-ledger concurrency proofs and W72 fake-provider integration passed.
- Logical restore: `restore_smoke=PASS`; 52 source / 52 restored application-auth-migration relations. The expected, source and restored synthetic application fixture signatures matched; the enabled auth-profile trigger and application trigger-mode signature matched. The source and restored `extensions` schema each contained two relations, with identical signatures `pg_stat_statements:v,pg_stat_statements_info:v`. The installed extension inventories matched exactly: `pg_stat_statements:1.11:extensions,pgcrypto:1.3:extensions,uuid-ossp:1.1:extensions`; `extension_parity=true`.
- Cleanup proof: `synthetic_fixture_removed=true`, `source_sentinel_removed=true`, `restore_database_removed=true`, `dump_removed=true`, `restore_cleanup_verified=true`, `remaining_containers=none`, `remaining_volumes=none`.

This closes only the **isolated synthetic PostgreSQL logical-restore smoke**, including the previously failing extension-schema parity assertion. It does **not** establish representative production-user-data recovery, complete managed Supabase/Storage/auth-identity recovery (the synthetic user had no auth identity), independent off-site backup retention, measured RPO/RTO, staffed operations/rollback acceptance, or independent review. Hosted Development schema/privilege drift and historic SQL/migration provenance remain unresolved. PR #3 remains **OPEN / Draft / Unmerged**; no release candidate is selected (`candidate_sha=NONE`). Public production remains **NO-GO**; preserve `hosted_write_authorized=false` and keep `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed. Passing isolated CI does not authorize hosted writes, migrations or release.

## Supabase Development Security Advisor refresh — 2026-10-19

A read-only check of project `mrwmmbytcymqgwvcoywd` (`ZAVQERA Development`, `eu-west-1`, PostgreSQL 17, `ACTIVE_HEALTHY`) returned a **CRITICAL** Supabase Security Advisor finding, `rls_disabled`, for `private.anonymous_ai_visitors`, `private.anonymous_ai_ip_windows`, and `private.anonymous_ai_reservations`. Read-only table metadata independently confirms `rls_enabled=false` for all three.

The source migration `supabase/migrations/20261006120927_anonymous_ai_plan_guard.sql` creates these tables without enabling RLS, but explicitly revokes table privileges from `PUBLIC`, `anon`, and `authenticated`; it also revokes those roles' EXECUTE privileges on the private helper functions. Therefore the advisor warning is a **mandatory unresolved security review**, not yet proof of effective client access. Effective live ACLs, schema exposure, role inheritance, and function owner/security/EXECUTE paths must be verified using the pinned 13-query read-only audit and reviewed independently.

**Stop condition:** do not run the advisor's suggested `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` statements blindly, and do not use a generic SQL endpoint to bypass the audit's least-privilege gate. No hosted DDL, migration, grants, revokes, or policy changes are authorized. Track the resolution in [Issue #5](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/issues/5). The separate `auth_leaked_password_protection` advisor warning also remains **WARN / Disabled**.

Public production remains **NO-GO** until the effective-access question is resolved with evidence and independent review.

## Live evidence refresh — 2026-10-20

- Current launch branch / PR #3 is `codex/launch-readiness-gates-20261018` at `c9c4afbc47732472cd267a7680f1ca091a25c652`, OPEN / Draft / Unmerged, based on `codex/mission-action-runtime-seam-test-20261014`. Web Unit `39306737378`, Web CI `39306737247`, and Flutter CI `39306737356` passed on this exact SHA. The Flutter job ran the validator/regression step successfully and reports 38 Python tests. W21 remains the separate exact code/test run `39246765511` on `ed7f06d6d731967ab47f7ecf7af6d68b0dbeb34f`; the only changes from that SHA to `c9c4afb` are three documentation files, so report the W21 result only against `ed7f06d`.
- Audit PR #1 is OPEN / Draft / Unmerged at `e123ead90684b64a9809ad6d4ba7b8ddcb155155`. PR #2 is OPEN / Draft / Unmerged at `73ac8f13a4f31848a380d14f00f4459d82a3b2f5`; PR #3 is OPEN / Draft / Unmerged at `c9c4afbc47732472cd267a7680f1ca091a25c652`. No submitted independent review exists on PRs #1/#2/#3 or canonical PRs #39/#40; Issue #4 remains open with owner-authored invitations and no reviewer response. Product PR #39 remains OPEN / Draft / Unmerged at `9d752a59f0683ea7149633138dc85bb33cf9a41b`, and Issue #23 remains OPEN.
- Audit PR #2 advanced five documentation-only commits after pinned code SHA `a3d68afb31a8c0ef373f7810e05a1286c30048dd`. The current runner blob `ce2a62e869d6909401a49e572cb586db9fa6563d`, audit-script blob `941c9c576a8f3d1d51544288d385332c21e4e3b9`, and query-13 blob `2a73dc8c2d63ae0d7baec986745b37c4d2d8607e` match the pinned checkpoint. The current owner-intake README requires a single-project scoped token with Project Settings: Read and Database: Read; if those options are unavailable, stop and do not substitute a classic PAT.
- The 2026-10-17 capture comment records ZIP SHA-256 `9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d` and says the ZIP was uploaded/reviewed. The raw ZIP was not exposed as a downloadable link in the fetched PR comment/files; the current PR #2 validation runs have no artifacts. Treat the capture hash/findings as owner-reported until the actual archive is accessible and independently inspected. The 2026-10-20 PR #2 catalog-only comment `6287650214` is supplemental, not a complete 13-query archive. Do not repeat the capture just because the checklist was stale; recover the recorded archive if possible, otherwise the authorized owner must publish a new verified 13-query archive using the pinned script.
- The latest catalog comment reports W83 unapplied; private anonymous-AI tables have RLS disabled but no direct anon/authenticated table SELECT/INSERT grants observed; `authenticated` has private-schema USAGE; private helper EXECUTE was observed only for `postgres`; public quota functions remain SECURITY DEFINER, pinned to `pg_catalog`, service-role-only; `agent_executions` retains service-role full table privileges with RLS enabled and authenticated SELECT; leaked-password protection remains disabled. The capture role's `rolbypassrls=true` handling and all catalog discrepancies remain for review.
- API exposed-schema settings were not queried in the 2026-10-20 catalog check. Available Supabase project metadata returns project identity, region and PostgreSQL version only; the checked source branch has no `supabase/config.toml`. Thus external PostgREST reachability of `private.is_workspace_member(uuid,uuid)` remains unknown. Its source and catalog evidence confirm SECURITY DEFINER, authenticated EXECUTE/private-schema USAGE, and an explicit `p_user_id`; RLS uses its default `auth.uid()`. This is a potential membership-enumeration path only if externally callable, not a confirmed exploit.
- Migration tuple `20261007105825_expose_anonymous_ai_guard_rpc` / ZMR-090 remains `HOSTED_ONLY_SOURCE_UNKNOWN` / `PENDING`. W83 is a separate candidate and provides no historical SQL/deployment evidence. All gates A–J remain BLOCKED, release candidate SHA is NONE, and the release decision remains **NO-GO**.


## Anonymous AI quota RPC candidate validation — 2026-10-19

Canonical source candidate: [Nexo PR #40](https://github.com/abdalrhmanata-gif/Nexo/pull/40), current head `fcaf4b0b2b5f9bb09f2b3a47988e8f66bacb0201`, remains **OPEN / Draft / Unmerged** with no submitted review. This candidate is not applied to Development.

- The forward-only W83 candidate creates three `SECURITY INVOKER` wrappers in `public`, delegating to existing `SECURITY DEFINER` helpers in `private`, pins wrapper `search_path` to `pg_catalog`, grants `service_role` private-schema USAGE and helper/wrapper EXECUTE, and revokes helper/wrapper EXECUTE from `PUBLIC`, `anon`, and `authenticated`. It does not configure the Supabase API exposed-schema list. The hosted exposure setting is not verified.
- The quota caller is marked `server-only` and supports modern `sb_secret_...` keys via `apikey` only, plus legacy JWT API keys via `apikey` and `Authorization: Bearer`. Unsupported key formats fail closed.
- On exact head `fcaf4b0b2b5f9bb09f2b3a47988e8f66bacb0201`, [Web Unit `39308859605`](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/39308859605), [Web CI/build `39308859627`](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/39308859627), [Flutter CI `39308859494`](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/39308859494), and [W83 isolated PostgreSQL 17 + Supabase REST + pgTAP `39308859609`](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/39308859609) all **PASS**. W83 artifact [`12214867931`](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/39308859609/artifacts/12214867931), digest `sha256:9f70103d16d17c97201166cbc23238936924e17aeeca9757c23bee7edaa2a378`.
- The W83 isolated workflow runs a clean local PostgreSQL 17 stack, replays checked-in migrations plus a documented local-only historical-auth compatibility fixture through W83, runs the 28-assertion pgTAP test, replays later migrations, exercises REST reserve/consume/release behavior, and verifies cleanup. The REST exercise uses local legacy JWT headers; modern secret-key behavior is unit-tested, not a hosted call. pgTAP asserts wrapper security mode and ACLs; a separate Node source test checks wrapper `search_path`. The pgTAP suite does not catalog-check wrapper `proconfig`, function owners, or overload counts; this is a review/test-scope limitation, not proof of an exploit.

This establishes the candidate's isolated migration, ACL-contract, and legacy-key REST behavior only. It does **not** establish the hosted Development key format, API-exposed schema settings, effective live ACLs, or hosted migration parity. The 2026-10-20 owner catalog spot-check [PR #2 comment 6287650214](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6287650214) reports W83 unapplied; RLS disabled on the three private anonymous-AI tables but no observed direct `anon`/`authenticated` table SELECT/INSERT grants; private helper EXECUTE only for `postgres`; and leaked-password protection disabled. These are owner-authored observations, not independent review. `private.is_workspace_member(uuid,uuid)` is SECURITY DEFINER, has `authenticated` EXECUTE and private-schema USAGE, and accepts explicit `p_user_id`; policies call its default `auth.uid()`. Whether PostgREST exposes `private` or another external call path exists is unknown, so membership enumeration remains a concern to verify, not a confirmed exploit. Historical migration provenance and independent security review remain unresolved.

**Decision remains NO-GO for hosted migration and public launch.** No hosted database/API settings/secrets or deployment changed. Keep PR #40 Draft/Unmerged, preserve `hosted_write_authorized=false`, and do not apply the candidate until read-only live evidence, provenance reconciliation, independent review, and explicit release authorization are complete.

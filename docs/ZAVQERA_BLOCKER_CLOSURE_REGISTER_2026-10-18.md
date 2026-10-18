# ZAVQERA — four-blocker closure register (2026-10-18)

**Disposition: NO-GO.** This register is the current evidence-backed closure record for the four remaining public-launch blockers. Isolated CI is green; no hosted write is authorized. It does not substitute for owner decisions or independent reviews.

## 1. Hosted Development security/schema drift — OPEN / HIGH

**Evidence:** [13-query capture review](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6235721455), [persisted remediation gates](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6235818612). ZIP SHA-256: `9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d`.

**Observed:** direct effective `service_role` privileges on all eight table operations for `public.agent_executions`; RLS enabled but not forced; two expected relations missing; 26 expected columns missing; 10/11 expected constraints absent; eight indexes and the success-receipt guard trigger absent; only 17/40 expected routine records match; four legacy overloads expected absent remain; eight explicit default EXECUTE ACL rows require policy disposition; captured audit role has `rolbypassrls=true`. Query 13 found no `service_role` parent-role/table-owner path in that capture, but that does not close the direct grants or broader drift.

**Required closure evidence:** an independent database-platform reviewer issues a per-finding severity/disposition with exact catalog rows and rationale; the authorized Development owner reviews exact function definitions, dependency impact, ACL intent, and chosen forward-only diff; the historic source/migration chain is independently mapped first; a restorable pre-change backup is confirmed; only then, a separate written authorization names the exact target and change. After authorized execution, a new read-only capture and application assertions prove every desired grant/schema/function state and no unrelated project changed. No SQL or migration may be improvised from catalog mismatches.

## 2. Historical migration provenance — OPEN / UNKNOWN

**Known counts:** 89 source migration files versus 74 hosted ledger rows; 46 exact version/name matches; 22 same-name/different-version conflicts; six hosted-only names; 43 source tuples absent from exact hosted ledger tuples. Expanded checked-in branch, GitHub Actions artifact, and Library archive scans recovered no trustworthy deployment receipt/SQL digest for the conflicts. One W4 source candidate matches the current checked-in bytes, but does not prove the differing hosted W4 version contains those bytes.

**Required source:** owner-controlled Git clones and reflogs/stashes/unpushed refs; private/deleted/external source repositories; original release archives; and database-owner deployment/backup/change records containing exact SQL or digest-to-version linkage. For each conflict, preserve deployed filename/version, SQL byte SHA-256, source ref/commit, execution receipt, and independent reviewer disposition. Keep rows UNKNOWN unless the byte/provenance chain is verified. Never edit `supabase_migrations.schema_migrations` or reconstruct an old migration from a similar current file.

References: [source recovery scan](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6236449154), [latest owner-intake checkpoint](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6249321121).

## 3. Independent review — OPEN / EXTERNAL DEPENDENCY

There is no submitted review on PR #3, no database-owner approval on PR #2, and no comments on Issue #4 before the public invitation. GitHub rejected formal reviewer assignment to `Farenhytee` because review assignment requires repository collaboration. A public invitation is now posted at [Issue #4, comment 6253639531](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/issues/4#issuecomment-6253639531), based on the public Database Sentinel project's stated read-only Supabase audit scope.

**Required closure evidence:** reviewer confirms willingness, discloses expertise/conflicts, and submits separately attributable written findings on (a) PR #3 validator/CI fail-closed paths and (b) the PR #2 captured Development database evidence. The project owner must respond to each severity finding and record disposition. A requested review, self-review, tool report, or owner worksheet does not count as independent approval.

## 4. Backup/recovery, operations and product acceptance — OPEN

**Completed technical evidence:** [W21 39154053027](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39154053027) passed all 26 steps at code/test HEAD `0fd69902305ef9603e90aef4ae446a95161306d1`. It verified disposable PostgreSQL 17 replay, database and concurrency regressions, W72 fake-provider integration, browser E2E 2/2, fail-closed unregistered-adapter behavior, and cleanup with no remaining containers/volumes. [Web Unit](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39154055655), [Web CI/build](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39154055648), and [Flutter CI](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39154055664) also passed at that HEAD.

**Still required:**

- Approved, encrypted pre-change backup/snapshot and an actual restore rehearsal to a separate disposable target; record restore start/end, errors, measured recovery point, achieved RPO/RTO, application data/ownership/RLS/function/sequence checks, and safe auth/session validation. No restore has been run.
- An operations/incident tabletop or controlled exercise with named on-call/contact, alert route, triage, escalation, rollback and owner acceptance. Do not invent a staffed incident channel.
- End-to-end acceptance evidence that distinguishes CI browser passes from owner-run local Docker execution and from human usability sessions. T01-T05 currently have owner-confirmed PASS labels but no recorded detailed observations. Capture actual observations without invented quotations, timings, retention or conversion.
- Written decisions on backend/environment, current production URL/publish state, capacity/billing, canonical domain/DNS/TLS and whether the CI E2E evidence satisfies the selected launch stage. No DNS, billing, secrets, or deployment changes are pre-authorized.

## Non-negotiable execution boundary

`hosted_write_authorized=false`; `TRUSTED_DISPATCH_ADAPTERS` stays empty/fail-closed. No hosted SQL/migration/ledger edit, privilege repair, real provider action, production deployment, secret/billing/DNS change, or protected PR merge is included in this register. The current W21 green result cannot close any hosted-parity, provenance, independent-review, restore, operations, or release-authorization gate.

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

- **Completed narrow CI check:** W21 run 39157505523 passed a disposable PostgreSQL 17 logical dump/restore smoke; the database and dump were removed, with cleanup verified. This was a synthetic/empty-data allowlisted-schema smoke only, and the `extensions` schema relation count differed (source 2, restored 0), explicitly outside the strict parity assertion. It does not prove a representative application restore, hosted schema parity, extension parity, or RPO/RTO.
- **Still required:** an approved, encrypted pre-change backup/snapshot and an actual data-bearing application restore rehearsal to a separate target; record restore start/end, errors, recovery point, measured RPO/RTO, application ownership/RLS/function/sequence checks, and safe auth/session validation.
- An operations/incident tabletop or controlled exercise with named on-call/contact, alert route, triage, escalation, rollback and owner acceptance. Do not invent a staffed incident channel.
- End-to-end acceptance evidence that distinguishes CI browser passes from owner-run local Docker execution and from human usability sessions. T01-T05 currently have owner-confirmed PASS labels but no recorded detailed observations. Capture actual observations without invented quotations, timings, retention or conversion.
- Written decisions on backend/environment, current production URL/publish state, capacity/billing, canonical domain/DNS/TLS and whether the CI E2E evidence satisfies the selected launch stage. No DNS, billing, secrets, or deployment changes are pre-authorized.

## Non-negotiable execution boundary

`hosted_write_authorized=false`; `TRUSTED_DISPATCH_ADAPTERS` stays empty/fail-closed. No hosted SQL/migration/ledger edit, privilege repair, real provider action, production deployment, secret/billing/DNS change, or protected PR merge is included in this register. The current W21 green result cannot close any hosted-parity, provenance, independent-review, restore, operations, or release-authorization gate.


## Latest isolated PostgreSQL restore-smoke evidence — 2026-10-18

At exact source/test HEAD `86b8b49ee3dd16371ca607089f49de8ba0778f9f`, [W21 run 39157505523](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39157505523) completed **SUCCESS (27/27 steps)**. The W21 workflow also passed disposable PostgreSQL 17/pgTAP, Mission Authority/quota/workspace regressions, four concurrency checks, fake-provider gateway integration, browser E2E (2/2), and cleanup; evidence reports no remaining containers or volumes.

The new logical backup/restore smoke passed using a custom-format dump (476,290 bytes; SHA-256 `c19fc303fa9b24eabb6985dfe522a12dbb0977afb7147919b5010d17c8db0afc`) kept entirely inside the CI-labeled disposable PostgreSQL container. It restored to a separate temporary database, verified **51 source vs 51 restored** relations across the application/auth/migration inventory, matched row counts for the checked core relations, and confirmed `restore_database_removed=true`, `dump_removed=true`, `restore_cleanup_verified=true`. The migration ledger count in this disposable test was 88. This is not the hosted Development schema/ledger or evidence of historical deployment provenance.

**Scope limits:** the two source relations in schema `extensions` are explicitly reported separately (source 2, restore 0) and are not part of the strict application-relation parity assertion; extension-member parity is therefore not proven. Core data tables and auth users/identities were empty in this disposable smoke. It is not a representative production-data restore, full Supabase managed-schema restore, measured RPO/RTO exercise, or recovery acceptance.

The other exact-head workflows also passed: [Web Unit](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39157509792), [Web CI/build](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39157509751), and [Flutter CI](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39157509777).

The four public-launch blockers remain open: hosted Development privilege/schema drift; unresolved historic migration source/provenance; no independent security/database review; and no full recovery/RPO/RTO, staffed operations exercise, detailed T01–T05 observations, or accountable release approval. Keep `hosted_write_authorized=false`, `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed, and public release **NO-GO**.

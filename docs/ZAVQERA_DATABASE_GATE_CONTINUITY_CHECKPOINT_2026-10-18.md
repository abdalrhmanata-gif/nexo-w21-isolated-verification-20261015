# ZAVQERA — Database Gate / Continuity Checkpoint (2026-10-18)

**Decision: RELEASE NO-GO. `hosted_write_authorized=false`. `TRUSTED_DISPATCH_ADAPTERS` remains empty/fail-closed.**

This checkpoint records verified repository/evidence state as of 2026-10-18. It is not authorization for a hosted change.

## Current repository state

- Isolated verification repository: `abdalrhmanata-gif/nexo-w21-isolated-verification-20261015`
- Audit branch: `codex/migration-ledger-provenance-20261015`
- Current audit PR #2 head when this checkpoint was prepared: `4191c04abf695da64b35ca23c68a81a710538202`.
- PR #2 is OPEN / DRAFT / UNMERGED; base `codex/w80-forward-correction-20261015`.
- W86 candidate PR #1 is OPEN / DRAFT / UNMERGED; candidate head tested at `0dc44842f9eaa25d0f34628b1c5c3de0741b41cf`.
- No hosted DB write/migration, migration-ledger rewrite, deployment, secret change or PR merge was performed.

## New path-history recovery result

The 13-query evidence report records source checkout HEAD `fbbcb080904acd88aad83a082803f627859026e2`. The recursive tree at that exact commit was complete (641 entries, not truncated) and included 89 migration SQL files.

- All 89/89 source version/name filenames in the 95-row decision intake exist in that exact source tree.
- Of 74 hosted ledger version/name rows, 46 exact filename paths exist in that tree.
- The other 28 are the 22 same-name/different-version rows plus six hosted-only rows.
- GitHub path-history queries against the exact recorded source HEAD returned zero commits for all 28 exact hosted-version filenames.
- The source-side W4 path is present with Git blob SHA `2745a06c66b9f325683beaa973e10f6d21631555` (559 bytes), but path history records only commit `772f011624c199adc021a61d039a4cf13e9a3740` with subject “merge: stage ZAVQERA integration without historical artifact”. That commit is not a per-migration deployment receipt; it does not prove what SQL bytes were executed under hosted version `20260921180138`.

Reports:
- [Exact-source-head GitHub migration path-history report](ZAVQERA_GITHUB_HOSTED_MIGRATION_PATH_HISTORY_2026-10-18.md)
- [28-row path/source matrix](ZAVQERA_GITHUB_HOSTED_MIGRATION_PATH_HISTORY_2026-10-18.csv)
- [Independent DB review assessment](ZAVQERA_INDEPENDENT_DB_OWNER_REVIEW_WORKSHEET_2026-10-17.md)
- [13-query hosted capture review](ZAVQERA_HOSTED_13_QUERY_CAPTURE_REVIEW_2026-10-17.md)
- [Full Library ZIP recovery report](ZAVQERA_LIBRARY_ARCHIVE_MIGRATION_SOURCE_RECOVERY_2026-10-17.md)

This is a bounded finding over the recorded Git source tree and reachable path history. It does not exclude deleted/unreachable refs, external/private repositories, developer-device clones, backups or deployment-system artifacts. Do not infer deployed SQL identity from the filenames, source Git blob SHA or catalog metadata. Keep all 22 conflicts and six hosted-only rows unresolved unless authoritative historical source bytes and trusted deployment evidence are recovered.

## Isolated candidate verification

Current W86 ACL correction candidate:
`supabase/migrations/20261015120000_w86_agent_executions_acl_correction.sql`, blob `33cacbecdaa2c5dfc1dc1a04cc061c58849bf562`, on PR #1 head `0dc44842f9eaa25d0f34628b1c5c3de0741b41cf`.

- [W80 isolated PostgreSQL 17 run 39025388240 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39025388240).
- Test environment reports `server_version_num=170011` (PostgreSQL 17.11).
- W66 privilege boundary: 11/11 PASS; current W86 correction: 23/23 PASS after seeded direct/column-ACL drift repair and again after reapplication, with repeated checks after injected role-path fixtures.
- Negative-control log markers passed for role-membership/owner paths, mixed `INHERIT`/`SET ROLE` cases and no-mutation guards.
- Disposable stack cleanup: verified.
- Evidence artifact: [12097808111](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39025388240/artifacts/12097808111).
- [Flutter CI for exact candidate SHA — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39025391888).

These results apply only to the disposable PostgreSQL environment. They do not demonstrate that hosted Development has been repaired, that its historical SQL is reconciled, or that release is authorized.

## Latest exact audit-branch CI

For audit PR #2 head `4191c04abf695da64b35ca23c68a81a710538202`:
- [Owner intake validation run 39115774591 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39115774591).
- [Flutter CI run 39115774589 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39115774589).

These validate the documentation/intake/tooling state; they do not resolve historic source evidence or hosted schema intent.

## Remaining release gates

1. Independent authorized DB-owner decisions for all observed grant, relation/column/constraint/index/trigger, routine signature/grant, private-schema USAGE, and default-ACL differences. No difference is labeled intentional or accidental without an authoritative target contract/release and rationale.
2. For each of the 22 version conflicts and six hosted-only rows, recover original SQL bytes plus a trusted deployment record linking those bytes to the exact Development project/version. If unrecoverable, record that explicitly and keep release blocked; do not edit `supabase_migrations.schema_migrations` to force alignment.
3. Complete routine-by-routine dependency/body/owner/SECURITY DEFINER/search_path/EXECUTE review and verify current application callers.
4. Build a forward-only least-privilege remediation candidate from the confirmed target state. Test complete migration replay, all affected catalog assertions, positive/negative behaviors and idempotent reapplication in disposable PostgreSQL. The captured Development is PostgreSQL 17.6; local CI evidence is 17.11, so explain/test the minor-version difference.
5. Review and rehearse a restorable backup/recovery plan and post-change read-only assertions.
6. Only after all prior gates, obtain separate written authorization naming exact project, change set, operator, window, backup/recovery and acceptance checks. No such authorization is present in this record.

## Stop conditions

Do not apply W86 or any other migration to hosted Development/Main/Production, do not revoke/drop/replace routines based only on signature differences, do not modify hosted migration history, do not enable trusted dispatch adapters, and do not merge PR #1/#2 while gates remain open.

**Status at handoff:** evidence scanning, path-history capture, interim analytic review and isolated candidate verification are documented. The remaining blockers require original deployment/source artifacts and an authorized human database-owner decision; they cannot be resolved by further inference from the same sources.


## Post-checkpoint execution update — 2026-10-18

The path-history recovery sweep and the new offline matrix validator have now been completed after the initial checkpoint was written.

- Latest verified documentation/source-history commit before this update: `592403e45bf5759e41635eaafb6d63e8f7034b8c`.
- The independent path-history report now includes a second query set against the original `abdalrhmanata-gif/Nexo` repository at `codex/mission-action-runtime-seam-test-20261014`, HEAD `9d752a59f0683ea7149633138dc85bb33cf9a41b`; all 28 exact hosted-version filenames again returned zero reachable commits.
- Added `tests/test_zavqera_github_hosted_migration_path_history.py`; the owner-intake CI now has a dedicated offline matrix check. The first run correctly exposed an over-strict assertion for the six hosted-only row descriptions; the test assertion was corrected without altering evidence rows or their dispositions.
- Exact HEAD owner intake validation [run 39116416968](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39116416968) passed 11 owner-intake tests, 5 synthetic local-Git-history tests and 7 path-history matrix tests, plus the no-network intake validator. Flutter CI [run 39116416970](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39116416970) also passed on SHA `8efe66b726142032d239426343bbbcb7dd9ecdb5`.
- The report-only corroboration commit `592403e45bf5759e41635eaafb6d63e8f7034b8c) has its exact-head owner intake validation [run 39116766669 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39116766669) and Flutter CI [run 39116766667 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39116766667).
- The isolated W86 candidate's [PostgreSQL 17.11 W80 run 39025388240](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39025388240) remains a local-only proof: W66 11/11, W86 23/23, negative controls and disposable cleanup passed. This is not a hosted deployment result.

Current review disposition remains **REVIEWED — MORE EVIDENCE REQUIRED**. The 22 name/version conflicts and six hosted-only rows remain unresolved; direct grants, catalog drift, routine/default-ACL intent, and independent owner decisions remain open. PR #1 and PR #2 remain OPEN/DRAFT/UNMERGED. No hosted DB/ledger write, migration, deployment, secret change or merge has occurred. `hosted_write_authorized=false`; trusted dispatch adapters remain empty/fail-closed; release remains **NO-GO**.


### Additional action-artifact recovery pass — verified contents (2026-10-18)

Five distinct diagnostic ZIP artifacts associated with selected W18/W19 migration-era original-repository runs were downloaded and their actual member lists inspected. Four contained only `pubspec.lock`; the W4–W16 baseline artifact contained only `pubspec.lock` and `.dart_tool/package_config.json`. None contained SQL migration files, database deployment receipts, schema dumps, or SQL hash manifests. Exact artifact IDs, run IDs and SHA-256 hashes are listed in the [expanded path-history recovery report](ZAVQERA_GITHUB_HOSTED_MIGRATION_PATH_HISTORY_2026-10-18.md).

Scope note: this inspects those five specific artifacts only, not every artifact attached to all 108 Actions runs in the date window. It narrows the sampled-artifact avenue; it does not establish all historic artifacts are empty.

Latest report commit for these findings: `5921eae01c7fe6f16d25f98aa925826fe050e0b9`. The 28-row matrix remains protected by seven offline regression tests; latest green exact-head checks on the previous source-history commit are preserved above. The new report/checkpoint changes trigger the owner validation workflow again, and their resulting exact-head checks must be verified before calling the new head validated.

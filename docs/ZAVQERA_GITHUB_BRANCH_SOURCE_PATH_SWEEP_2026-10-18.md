# ZAVQERA — GitHub branch/source-path sweep (2026-10-18)

**Disposition: ADDITIONAL GIT-ACCESSIBLE SOURCE SEARCH COMPLETE; HISTORICAL DEPLOYED SQL PROVENANCE STILL UNKNOWN; RELEASE NO-GO.**

## Scope and method

This pass followed the 2026-10-17 full Library ZIP recovery and the evidence-based review recorded in the independent database-owner worksheet. It was read-only; no database connection, SQL execution, migration, deployment, secret change, ledger rewrite or PR merge occurred.

1. Retrieved the visible branch inventory for the original repository `abdalrhmanata-gif/Nexo`: 23 branch heads. Recursively inspected branch-head Git trees, including the branches carrying current W4–W82 migration sources, W80/W86 work, deployment branches, and the integration/runtime-test branch. Trees queried for the source-bearing branches returned successfully without truncation.
2. Compared the 95-row migration owner-intake register against the exact captured-source commit `fbbcb080904acd88aad83a082803f627859026e2` in the isolated audit repository. Its recursive Git tree was complete (641 entries, not truncated).
3. For this exact captured-source ref, confirmed all **89/89 source-side migration filenames** in the row-level register exist under `supabase/migrations`. The tree contains 89 SQL migrations. Of 74 hosted ledger rows, **46 exact version/name filenames** exist in this source tree. The remaining **28 hosted filename paths** comprise the 22 timestamp/version conflicts and six hosted-only rows.
4. Queried GitHub's commit-by-path endpoint on the captured-source ref for those 28 hosted-version filenames. All 28 returned **zero commits for that path on this ref**. This is evidence that the captured source history does not expose these deployed-version files; it is not proof that no such file ever existed in a private clone, deleted/unreachable ref, release package, deployment system or backup.

## Key result: W4 row ZMR-008 remains unresolved

- Source-side file present: `supabase/migrations/20260921180052_w4_table_privilege_hardening.sql`.
- Git blob SHA: `2745a06c66b9f325683beaa973e10f6d21631555`; 559 bytes.
- Archived LF SQL SHA-256: `3419a01a1b0ea66bd22877f478b61473cf1210006828ea3f28c5c08fb51ef0c8`.
- Hosted ledger row uses `20260921180138_w4_table_privilege_hardening`.
- The hosted-version path returned no commit history on the captured-source ref; the 23 branch-head sweep found the source-side `180052` file recurring but did not recover a separate `180138` SQL artifact or per-migration deployment receipt.
- Therefore ZMR-008 remains `NAME_VERSION_CONFLICT` / `OPEN` / owner review `PENDING`. Keep `verified_source_sql_sha256` (verified historic source reference), `hosted_deployment_record_uri` and `verified_deployed_sql_sha256` blank until evidence that satisfies the intake rules is provided. Candidate metadata is not deployment proof.

## Updated status table

| Reconciliation group | Register count | GitHub tree/path result | Decision |
|---|---:|---|---|
| Source migration filenames | 89 | 89/89 found at captured source commit | Current source-side files accounted for at that commit; does not prove they ran on hosted DB |
| Exact hosted/source version-name filenames | 46 | 46 hosted filenames present | Filename equality only; SQL deployment byte identity remains unproven without deployment provenance |
| Same-name/version conflicts | 22 | Source-side filename exists; hosted-version path absent from captured commit tree and path-history query | Keep all unresolved / owner review pending |
| Hosted-only filenames | 6 | No file in captured source tree; path-history queries on captured ref returned zero | Keep UNKNOWN/blocking until authoritative source and deployment provenance recovered |
| Historical deployed SQL byte identity | 0 rows proven by this pass | No new deploy receipt or deployed SQL byte digest found | Not established |

## What this pass does NOT establish

- It does not establish that the observed mismatches are intentional legacy state or accidental database drift.
- It does not prove that a migration with an absent current pathname was never used or deployed.
- It does not prove that the current source SQL is the SQL executed in the hosted project.
- It does not independently recompute the hosted evidence ZIP hash, create a new live capture, or approve any schema/ACL remediation.
- It does not satisfy owner review or authorize hosted writes.

## Next action after the GitHub-visible search

Do not keep guessing at filenames or rewrite the 95-row intake. The next meaningful source recovery should use evidence stores not represented by accessible branch trees: an owner-controlled clone/reflog, deployment workspace/archive, CI deployment artifact/log, Supabase CLI migration bundle, release artifact, or a trusted backup. For each recovered object, preserve source identity and chain of custody; obtain an independent digest; and tie it to the exact Development project and migration version through a trusted deployment record. If no reliable evidence exists, record the affected bytes as `UNKNOWN_BLOCKING`.

## Mandatory controls remain

- `hosted_write_authorized=false`.
- `TRUSTED_DISPATCH_ADAPTERS` stays empty/fail-closed.
- Do not apply W86 or any migration to hosted Development/Main/Production.
- Do not edit `supabase_migrations.schema_migrations` to make versions match.
- Keep audit PR #2 and W86 PR #1 OPEN/DRAFT/UNMERGED; keep original PR #39 and Issue #23 open.
- Release remains **NO-GO**.

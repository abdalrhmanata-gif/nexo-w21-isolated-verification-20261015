# ZAVQERA — GitHub hosted-migration path-history sweep (2026-10-18)

**Disposition: no historical deployed SQL recovered from the captured source checkout's path history; provenance remains unresolved. No database or migration was changed.**

## Scope and reproducibility

- Repository: `abdalrhmanata-gif/nexo-w21-isolated-verification-20261015`
- Captured source checkout HEAD: `fbbcb080904acd88aad83a082803f627859026e2` ([commit](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/commit/fbbcb080904acd88aad83a082803f627859026e2))
- Tree endpoint: `git/trees/fbbcb080904acd88aad83a082803f627859026e2?recursive=1`; `truncated=false`, 641 tree entries.
- Source migration inventory: 89 `.sql` files directly under `supabase/migrations/`.
- Intake: 95 reconciliation rows in `docs/ZAVQERA_MIGRATION_OWNER_DECISION_INTAKE_2026-10-17.csv`.
- Exact source-path comparison: **89/89** version/name source filenames exist at the captured source HEAD. This indicates the currently checked-in source inventory is present; it does not establish what SQL bytes were executed in Development.
- Hosted tuple path comparison: **46/74** hosted version/name paths exist in that source tree. The other **28** are the 22 same-name/version conflicts plus six hosted-only names.

For each of the 28 absent hosted-version filenames, queried the GitHub path-history endpoint at the captured source HEAD:
`GET /repos/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/commits?path=supabase/migrations/<exact-hosted-version_filename>.sql&sha=fbbcb080904acd88aad83a082803f627859026e2&per_page=100`.

**Result: 28/28 returned zero commits.** Thus no reachable path history for those exact hosted-version filenames was recovered from this source checkout. This is a bounded repository-history finding, not proof that no file existed in any deleted/unreachable ref, external repository, local clone, backup, or deployment system.

Detailed row-by-row comparison, including available source Git blob SHAs and file sizes, is recorded in [the accompanying CSV](ZAVQERA_GITHUB_HOSTED_MIGRATION_PATH_HISTORY_2026-10-18.csv).

## Important W4 source-history detail

The source-version path `supabase/migrations/20260921180052_w4_table_privilege_hardening.sql` is present at the captured source HEAD with Git blob SHA `2745a06c66b9f325683beaa973e10f6d21631555` (559 bytes). GitHub's path-history endpoint reports one matching commit at that source HEAD:

- [`772f011624c199adc021a61d039a4cf13e9a3740`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/commit/772f011624c199adc021a61d039a4cf13e9a3740), dated 2026-09-25T21:11:21Z.
- Commit subject: `merge: stage ZAVQERA integration without historical artifact`.

The commit subject does not prove the SQL was wrong or fabricated. It does mean this repository evidence alone must not be treated as a historical deployment receipt or as proof that hosted version `20260921180138` used the same bytes. The hosted filename itself returned zero path-history commits, and no per-migration deployment receipt/hash has been supplied.

## Interpretation by row class

| Class | Rows | What this sweep establishes | What it does not establish |
|---|---:|---|---|
| Same-name/different-version | 22 | The source-version filenames are present in the captured source tree; the different hosted-version filenames are absent; their exact path-history queries return zero commits. | Whether deployed SQL was identical, semantically equivalent, modified, applied under another filename, or never retained in Git. |
| Hosted-only tuple | 6 | The hosted-version filenames are absent from the source tree and yielded zero path-history commits at the captured source HEAD. | A definitive source reconstruction or proof that the migrations were never applied. |
| Exact version/name metadata tuple | 46 | The matching filenames exist in the captured source tree. | Exact historical SQL-byte identity with the deployed operations; the ledger is metadata, not a SQL deployment receipt. |

## Decision and next evidence required

1. Keep every affected row open/unknown where authoritative evidence remains absent. Do not populate `verified_deployed_sql_sha256` or a deployment URI from current source-file names or Git blob IDs.
2. Request original deployment job logs/artifacts, the exact migration SQL payload used by the deployment tool, database-owner records linking project ref `mrwmmbytcymqgwvcoywd` to the migration events, and any original developer clone/archive that predates the staging merge.
3. If those records cannot be recovered, make the owner decision explicit that SQL-byte provenance is unrecoverable and commission a separately reviewed, forward-only reconciliation/re-baselining plan. Do not edit `supabase_migrations.schema_migrations` to force a match.
4. Keep W86 and all other hosted migrations blocked pending the independent owner review, migration-chain assessment, isolated acceptance, recovery rehearsal, and separate written authorization naming the exact target/change set/operator/window.

This sweep did not connect to Supabase, execute SQL, change a hosted database, deploy, alter secrets, or merge a PR. `hosted_write_authorized=false`; release remains **NO-GO**.

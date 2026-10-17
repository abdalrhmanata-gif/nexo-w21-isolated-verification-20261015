# Local historical migration-source recovery runbook — 2026-10-17

**Purpose:** Recover possible original SQL files from pre-existing local Git clones, reflogs, and unreachable commits without network or database access. This is a candidate search only; it does not change a database or the hosted migration ledger.

## Known target set

The scanner checks the 22 same-name/version conflict stems plus six hosted-only migration stems recorded in the hosted reconciliation report. It matches timestamps independently of the suffix; do not substitute similar names that are not on that list.

## New offline scanner

- Script: [tools/scan_zavqera_local_migration_history.py](../tools/scan_zavqera_local_migration_history.py)
- Tests: [tests/test_scan_zavqera_local_migration_history.py](../tests/test_scan_zavqera_local_migration_history.py)
- CI: [owner-intake validation workflow](../.github/workflows/zavqera-owner-intake-validation.yml)

From a Windows PowerShell terminal, for each existing local clone or backup clone:

~~~powershell
python tools/scan_zavqera_local_migration_history.py --repo "D:\path\to\existing\Nexo" --output "D:\path\to\evidence\local-migration-history-scan.json"
~~~

Use the repository's own clone path. The command runs no git fetch, pull, remote API, database query, or hosted change. It scans:
1. Commits reachable from local refs and reflogs.
2. Unreachable commit objects reported by local git fsck.
3. Candidate SQL paths matching the 28 known historical name stems.

It emits only commit IDs, paths, Git blob object IDs, and SHA-256 of candidate SQL bytes. It never prints or uploads SQL text. The commit limit fails closed if reached; increase --max-commits and repeat rather than interpreting a bounded scan as a negative result.

## Required interpretation

- COMPLETED_CANDIDATE_SCAN means the chosen local clone's eligible commit trees were scanned without reported tree/blob errors. It does not prove all external archives or deleted storage were searched.
- PARTIAL_REQUIRES_REVIEW means inspect the error list and repeat or repair the local clone before relying on the result.
- FAILED_CLOSED means no negative conclusion is allowed.
- Zero candidates does not prove that historical SQL never existed.
- A candidate is not authoritative merely because its filename/version resembles a hosted row. The database owner must establish custody and the original commit/archive, then match it to a trusted deployment record for the exact Development project. Only actual equal 64-hex source/deployed SQL digests can support byte-equivalence classification.
- Never change supabase_migrations.schema_migrations, infer SQL from function bodies, or run recovered migration files against any hosted project during this source-recovery step.

## Local evidence already checked in this working environment

On 2026-10-17, an offline recursive ZIP scan examined 21 ZIP archives under this working environment's /mnt/data, including 13 nested ZIP members (nested depth capped at four). All 21 ZIP integrity checks passed; zero candidate files matched the targeted historic migration stems. Scan report: ZAVQERA_LOCAL_ARCHIVE_MIGRATION_SOURCE_SCAN_2026-10-17.json in the conversation working files. This covers the current task workspace only, not every archive or local clone on the user's computer.

## Disposition

If no authoritative candidate is recovered, keep the 22 conflicts and six hosted-only rows UNKNOWN, keep every independent-owner status PENDING, preserve hosted_write_authorized=false, keep TRUSTED_DISPATCH_ADAPTERS empty/fail-closed, and maintain release NO-GO.

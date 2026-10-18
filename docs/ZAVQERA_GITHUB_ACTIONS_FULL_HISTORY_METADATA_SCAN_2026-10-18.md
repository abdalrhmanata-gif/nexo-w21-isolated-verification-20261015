# ZAVQERA — Complete original-repository GitHub Actions metadata scan (2026-10-18)

**Disposition: no hosted migration deployment receipt or historical SQL archive was identified in the repository's available Actions-run metadata or the sampled relevant artifacts. Historical SQL-byte provenance remains UNKNOWN; release NO-GO.**

## Scope and coverage

Repository: `abdalrhmanata-gif/Nexo`.

The GitHub Actions runs endpoint reported 10,590 total workflow runs. The metadata was reviewed over all 106 pages (105 pages with 100 records and a final page of 90). The previously documented first 30 pages covered 3,000 records from 2026-10-17 through 2026-10-10. This follow-up inspected pages 31–106, another 7,590 records, ranging from 2026-10-10T16:34:02Z down to 2026-09-14T10:35:12Z. All requested pages returned normally, with no missing pages.

The review filtered workflow names and branches for migration/database/SQL/Supabase/PostgreSQL/pgTAP/backup/schema/deployment keywords. Visible relevant workflow families were principally CI, W21 local/disposable E2E, W25 isolated PostgreSQL tests, browser tests, and Netlify web preview deployment. No dedicated workflow named as a hosted Supabase migration/apply/release pipeline was found in the reviewed run metadata.

**Scope limit:** a workflow name and its metadata are not a complete artifact/content scan. The review did not download every artifact from all 10,590 runs. Artifact inspection below is targeted and bounded.

## Targeted artifact results

### W25 isolated PostgreSQL workflow

- Run [38068185915](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38068185915), 2026-10-10T16:34:02Z, workflow name `ZAVQERA W25 Isolated PostgreSQL Atomic Fence`.
- Artifact inventory returned zero artifacts.

This provides no source archive or deployment receipt.

### W21 local launch evidence — 2026-10-01

- Run [36913583208](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/36913583208).
- Artifact [11189605074](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/36913583208/artifacts/11189605074), ZIP SHA-256 `c23cb75a6f58ee2f7c575b8aa80d277285fc68526489f2717519493fa0cd9beb`.
- ZIP has a single member, `W21_EVIDENCE.txt` (1,638 bytes). It records `result=failure`, source SHA `5dec647cf9979327e9959b9b91d5be1ab72ea9a3`, PostgreSQL major 17, a list of checksums, and `cleanup=NOT_VERIFIED_OR_RUN_DID_NOT_REACH_TEARDOWN`.
- The file is test evidence metadata, not a migration source bundle or hosted deployment receipt. The fact that a checksum list includes source-side hashes does not tie SQL bytes to a hosted migration ledger entry.

### W21 isolated browser E2E evidence — 2026-10-04

- Run [37187981840](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/37187981840).
- Artifact [11297772709](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/37187981840/artifacts/11297772709), ZIP SHA-256 `8cee140d87b4fb8747ae9c3a14fb1ec8d6e4e1c0ab4df2e2812510fbf96dd4bc`.
- ZIP has one 258-byte `W21_EVIDENCE.txt` member: `result=failure`, source SHA `8766deb1eb09e9077cb3cf822a1b45916836e261`, `migration_source=repo-migrations`, PostgreSQL major 17 and `cleanup=VERIFIED`.
- This only establishes that the local test workflow used the repository's migration files; it does not establish hosted deployment.

## Combined recovery conclusion

Across the 23 visible source-repository branch tips, all 112 ZIP objects in the Library, the Library SQL filename inventory and the full 10,590-run Actions metadata index, no authoritative SQL bytes or per-migration deployment record were established for the 22 timestamp/version conflicts or six hosted-only migration rows.

The exact hosted-version filenames remain absent from the 23 visible branch-tip trees. The one W4 source-side candidate remains `20260921180052_w4_table_privilege_hardening.sql`, 559-byte LF SHA-256 `3419a01a1b0ea66bd22877f478b61473cf1210006828ea3f28c5c08fb51ef0c8`, while the hosted tuple is `20260921180138_w4_table_privilege_hardening`; the candidate is not proof of the hosted bytes.

## Required next step

A user/DB-owner-controlled source is now required: existing local clone/ref logs/stashes/unpushed refs, external/private/deleted repository, deployment logs or archives that retained executed SQL, or controlled backup/change records. Run the local scanner from the existing owner-controlled clone using the documented local runbook; it scans refs/reflogs and unreachable commit objects without network or database access. A candidate must then be tied to the exact target project/version by a trusted deployment record.

If no authoritative historic bytes or deployment record can be produced, keep the affected rows OPEN/UNKNOWN and commission a separately reviewed re-baselining decision; do not invent SQL or rewrite the hosted migration ledger.

`hosted_write_authorized=false`. `TRUSTED_DISPATCH_ADAPTERS` remains empty/fail-closed. No hosted SQL, migration, deployment or secret change was performed by this scan. Release remains **NO-GO**.

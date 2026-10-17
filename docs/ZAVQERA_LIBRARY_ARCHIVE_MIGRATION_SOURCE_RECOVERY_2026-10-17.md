# ZAVQERA — Library archive migration-source recovery findings (2026-10-17)

**Disposition: SOURCE-SIDE CANDIDATE FOUND; HOSTED SQL-BYTE PROVENANCE STILL UNKNOWN; RELEASE NO-GO.** This is a metadata/hash review of archived files. No recovered SQL was executed. No hosted database or migration ledger was changed.

## Archive and candidate identity

- Library archive name: `ZAVQERA_W4_DB_READY_PACK.zip`.
- Archive object recorded in the Library on 2026-09-21 at 18:03:33 UTC; internal ZIP member timestamps are 2026-09-21 18:03 UTC.
- Archive SHA-256: `1781646022255f2eda2a8007676ebd157d70782fccabb6492ada6afc59245f4c`.
- Member: `zavqera_w4_pack/supabase/migrations/20260921180052_w4_table_privilege_hardening.sql`.
- Member size: 559 bytes.
- SQL SHA-256 in the archive (LF line endings): `3419a01a1b0ea66bd22877f478b61473cf1210006828ea3f28c5c08fb51ef0c8`.
- Current audited GitHub source path: [same source-side migration](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/migration-ledger-provenance-20261015/supabase/migrations/20260921180052_w4_table_privilege_hardening.sql); GitHub content is the same 559-byte LF representation, with Git blob SHA `2745a06c66b9f325683beaa973e10f6d21631555`.

## Exact comparison result

The archive member's 559-byte LF representation matches the current checked-in source text. The raw SQL digest recorded for this source row by the Windows working-tree reviewer is `43b8aeac20e00ce8170f5064a8622a66f7cee58c6cc25d4ff0afeb59b83ed044`; reproducing CRLF endings (including the final CRLF) yields that digest (566 bytes). This is a line-ending representation difference, not evidence of a SQL logic difference.

## Why the historic hosted row is NOT resolved

The reconciliation ledger row ZMR-008 is:

`source 20260921180052 / w4_table_privilege_hardening` vs `hosted 20260921180138 / w4_table_privilege_hardening` — `NAME_VERSION_CONFLICT` — owner review `PENDING`.

The W4 pack's `docs/W4_STATUS.md` says that eight W4 migrations were applied to the Development project and reports the intended table/RLS/grant state. However, the archive does not include a per-migration deployment receipt or digest of the SQL bytes executed under hosted version `20260921180138`. The pack therefore gives a historical source-side artifact and contemporaneous deployment-context claim; it does not prove the hosted row's exact timestamp/version used these exact bytes.

**Required classification:** keep ZMR-008 `NAME_VERSION_CONFLICT`, owner review `PENDING`; keep `verified_deployed_sql_sha256` and `hosted_deployment_record_uri` blank. Do not classify `EXACT_SOURCE_BYTES_VERIFIED`, rewrite migration history, or infer the hosted row was equivalent because the filename suffix/text matches.

## Whole-Library scan scope

Expanded scan after the initial selected-pack pass:
- All 43 ZIP files in the current Library listing created on/after 2026-09-20 were materialized and scanned, recursively inspecting nested ZIPs through depth 4.
- Outer ZIP integrity: 43/43 passed; nested ZIP integrity checks: 180/180 passed.
- ZIP members inspected: 12,468; extracted member bytes processed: 63,842,487; read/integrity errors: 0; depth/size caps hit: 0.
- Candidate path occurrences: 2, but unique migration stem/version/SQL-hash tuples: 1. Both occurrences refer to the same `20260921180052_w4_table_privilege_hardening.sql` source candidate with LF SHA-256 `3419a01a1b0ea66bd22877f478b61473cf1210006828ea3f28c5c08fb51ef0c8`; the second occurrence is nested in a continuity bundle.
- This expands the earlier 10-archive/228-member scan. It is still not exhaustive across all 111 ZIPs in the Library (older archives were outside the selected creation-date window), external/private/deleted repositories, or every owner-machine clone.
- Machine-readable summaries: `ZAVQERA_LIBRARY_ARCHIVE_MIGRATION_SOURCE_SCAN_2026-10-17_EXPANDED.json` (expanded scan) and `ZAVQERA_LIBRARY_ARCHIVE_MIGRATION_SOURCE_SCAN_2026-10-17.json` (initial targeted scan).

## Next recovery gate

Recover the original SQL/commit/archive for hosted version `20260921180138` and a trusted deployment record that ties it to the exact Development project, or keep the row open/UNKNOWN for deployed bytes. Continue the same process for the other 21 timestamp conflicts and six hosted-only names. No hosted write is authorized; trusted dispatch adapters stay empty/fail-closed; release remains **NO-GO**.
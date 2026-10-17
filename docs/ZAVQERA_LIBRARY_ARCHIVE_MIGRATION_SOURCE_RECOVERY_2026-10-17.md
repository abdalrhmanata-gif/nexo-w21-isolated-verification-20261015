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

## Full Library ZIP snapshot scan — final (2026-10-17)

- Scanned all 112 ZIP objects present in the Library index at the time of the scan, including archives created before and after 2026-09-20. Every outer ZIP passed integrity validation: 112/112; zero failures.
- Outer archives contained 79 unique content hashes. Recursive scan inspected 86 unique ZIP payloads (including nested ZIPs) and 4,572 members / 24,630,444 declared uncompressed member-bytes; 130 nested-archive occurrences were seen and 123 duplicate payloads were skipped after content-hash deduplication.
- Target stems: all 22 known same-name/different-version conflict names plus all six hosted-only migration names. Only one unique SQL source candidate was found: `20260921180052_w4_table_privilege_hardening.sql`, 559 bytes, LF SHA-256 `3419a01a1b0ea66bd22877f478b61473cf1210006828ea3f28c5c08fb51ef0c8`.
- No alternative SQL bytes or filename/version for hosted `20260921180138_w4_table_privilege_hardening` were found. Name mentions in replay/catalog documents are not original SQL bytes and are not counted as recovered source.
- Read/integrity errors: 0; member-size, total-uncompressed or nesting-depth caps: 0. No network/database requests occurred and no hosted writes were authorized.
- Machine-readable full-snapshot report: `ZAVQERA_LIBRARY_ARCHIVE_MIGRATION_SOURCE_SCAN_2026-10-17_ALL_112.json`; SHA-256 `24c01040a5ae4f4376a99a5205999d4a6d6c5fd499a1abc84cbaf819071c7cd6`.
- This covers the 112 ZIP objects visible in the Library index at scan time. It does not cover deleted/unindexed storage, private or external repositories not archived here, or every user-device clone.

## Next recovery gate

Recover the original SQL/commit/archive for hosted version `20260921180138` and a trusted deployment record that ties it to the exact Development project, or keep the row open/UNKNOWN for deployed bytes. Continue the same process for the other 21 timestamp conflicts and six hosted-only names. No hosted write is authorized; trusted dispatch adapters stay empty/fail-closed; release remains **NO-GO**.
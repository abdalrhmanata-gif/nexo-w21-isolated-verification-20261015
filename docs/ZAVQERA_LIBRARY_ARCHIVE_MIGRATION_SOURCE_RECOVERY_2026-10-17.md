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

- Examined 10 selected source/verification ZIP archives from the Library, including W4/W5 readiness packs, replay source packs and historical NEXO source packs.
- ZIP integrity checks: 10/10 passed.
- ZIP members inspected: 228.
- Target stems: the known 22 version-conflict names plus six hosted-only names.
- Source-side candidate matches: 1 (the W4 file above).
- The scan did not search every one of the 110 ZIP files indexed in the Library, nor any external/private/deleted repositories or all owner-machine clones. Its result is bounded and must not be represented as an exhaustive archive search.
- Report JSON in the working container: `/mnt/data/ZAVQERA_LIBRARY_ARCHIVE_MIGRATION_SOURCE_SCAN_2026-10-17.json`.

## Next recovery gate

Recover the original SQL/commit/archive for hosted version `20260921180138` and a trusted deployment record that ties it to the exact Development project, or keep the row open/UNKNOWN for deployed bytes. Continue the same process for the other 21 timestamp conflicts and six hosted-only names. No hosted write is authorized; trusted dispatch adapters stay empty/fail-closed; release remains **NO-GO**.
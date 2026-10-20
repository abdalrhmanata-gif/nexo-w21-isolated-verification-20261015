# Row-level migration owner decision intake — instructions

This file accompanies `ZAVQERA_MIGRATION_OWNER_DECISION_INTAKE_2026-10-17.csv`, containing exactly 95 reconciliation units copied from the published 2026-10-17 ledger table.

## Evidence identity

- Hosted capture archive SHA-256: `9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d`
- Raw source-manifest SHA-256 recorded at capture: `0d05ab7285edc975084ddbc595d1af7d2dd0752cc27e94d8fe0549170419be38`
- Normalized current-source manifest SHA-256: `555db007d0c25ee7bf6ed4f983766eea1dde170a7ef5d0e12cc710d5838c7094`
- Migration provenance ledger: [2026-10-17 row-level reconciliation](ZAVQERA_MIGRATION_PROVENANCE_RECONCILIATION_LEDGER_2026-10-17.md)
- Independent owner worksheet: [Review worksheet](ZAVQERA_INDEPENDENT_DB_OWNER_REVIEW_WORKSHEET_2026-10-17.md)
- Remediation and release gates: [Gated remediation plan](ZAVQERA_HOSTED_REMEDIATION_GATES_2026-10-17.md)

## Column handling

The first nine columns preserve the existing reconciliation values. Do not replace the source/hosted versions or the classifications merely to make the list appear consistent.

Populate the following only after independent evidence review:

- `authoritative_historical_source_uri`: durable, access-controlled path to the original SQL source.
- `source_git_blob_commit_or_archive_provenance`: exact commit/blob or archive identity and chain of custody.
- `verified_source_sql_sha256`: digest computed from actual recovered SQL bytes.
- `hosted_deployment_record_uri`: trusted deployment/owner evidence tying the SQL bytes to the exact project and migration.
- `verified_deployed_sql_sha256`: digest of actual deployed SQL bytes if trustworthy evidence exists. Do not substitute a schema definition or a source digest.
- `evidence_artifact_sha256`: digest of the supporting evidence bundle.
- `independent_reviewer_name_role`, `reviewed_at_utc`, `decision_rationale_and_evidence`, and `required_follow_up`: reviewer and audit trail.

## Candidate archive fields — not deployment proof

Seven `candidate_*` columns record source-archive leads independently from verified evidence fields. The W4 archive lead for ZMR-008 records:
- Archive: `ZAVQERA_W4_DB_READY_PACK.zip`, SHA-256 `1781646022255f2eda2a8007676ebd157d70782fccabb6492ada6afc59245f4c`.
- Member SQL source version `20260921180052`, SHA-256 `3419a01a1b0ea66bd22877f478b61473cf1210006828ea3f28c5c08fb51ef0c8`.
- Hosted ledger version `20260921180138` differs. The archive's W4 status says eight W4 migrations were applied, but includes no per-row deployment receipt or hash linking those bytes to the hosted version.

Accordingly, candidate metadata is populated, but `authoritative_historical_source_uri`, `verified_source_sql_sha256`, `hosted_deployment_record_uri`, and `verified_deployed_sql_sha256` remain blank; the row remains `NAME_VERSION_CONFLICT` / `OPEN` / `PENDING`. The source reviewer digest `43b8aeac20e00ce8170f5064a8622a66f7cee58c6cc25d4ff0afeb59b83ed044` reflects CRLF line endings (566 bytes), while the archived/current GitHub LF source is 559 bytes with digest `3419a01a1b0ea66bd22877f478b61473cf1210006828ea3f28c5c08fb51ef0c8`. This is only a source representation match, not proof of deployed SQL-byte identity. See [the source-recovery analysis](ZAVQERA_LIBRARY_ARCHIVE_MIGRATION_SOURCE_RECOVERY_2026-10-17.md).
## Controlled owner disposition values

Use exactly one of the following values in `owner_disposition` only when evidence supports it:

- `OPEN` — review not complete.
- `EXACT_SOURCE_BYTES_VERIFIED` — only when authoritative historic SQL bytes and a trusted deployment record prove exact identity.
- `NAME_VERSION_CONFLICT_RESOLVED` — the source/hosted version conflict is resolved by authoritative evidence and the rationale is recorded.
- `HOSTED_ONLY_SOURCE_RECOVERED` — the authoritative source for the hosted-only ledger row is recovered and linked.
- `SOURCE_ONLY_REVIEWED` — the source-only row is reviewed without inferring that its absence from the hosted ledger proves it was never deployed.
- `UNKNOWN_BLOCKING` — evidence is missing, contradictory, or cannot establish the required conclusion.

A source/hosted version-name match by itself is not byte provenance. Current routine bodies, similar filenames, nearby timestamps, matching schema state, local tests, or normalized manifest hashes cannot be substituted for historical SQL plus trusted deployment evidence.

Keep `approved_for_offline_remediation_design` as `NOT_REVIEWED` until the owner explicitly decides otherwise. The `hosted_change_authorized` column is deliberately initialized to `NO — separate written authorization required`; this CSV never authorizes a database write. Do not use this template to store credentials, connection strings, API keys, application data, or secrets.

## Required output

For every row that is not fully resolved, leave it visibly `OPEN` or mark it `UNKNOWN_BLOCKING`, identify the missing evidence and its owner, and keep release **NO-GO**. The independent owner signs off on the reconciliation separately; filling a row is not itself approval. Any future hosted change requires a separate written authorization naming the exact target, SQL/change set, operator, time window, backup/recovery procedure, and acceptance checks.

## Offline validator and regression tests

The intake has a dependency-free, offline validator and tamper-regression test suite:

- Validator: [validate_zavqera_migration_owner_intake.py](../tools/validate_zavqera_migration_owner_intake.py)
- Tests: [test_zavqera_migration_owner_intake.py](../tests/test_zavqera_migration_owner_intake.py)
- GitHub Actions gate: [zavqera-owner-intake-validation.yml](../.github/workflows/zavqera-owner-intake-validation.yml)

From the repository root, run:

```powershell
python -m unittest discover -s tests -p 'test_zavqera_migration_owner_intake.py' -v
python tools/validate_zavqera_migration_owner_intake.py
```

The validator cross-checks all 95 IDs and immutable baseline fields against the source ledger and enforces the 46/22/21/6 metadata and classification counts. OPEN rows may be assigned to a reviewer while remaining pending. Reviewed dispositions are accepted only when their required evidence and reviewer rationale are present; `EXACT_SOURCE_BYTES_VERIFIED`, `NAME_VERSION_CONFLICT_RESOLVED`, and `HOSTED_ONLY_SOURCE_RECOVERED` require actual source/deployment evidence and equal valid 64-character SQL SHA-256 digests. `SOURCE_ONLY_REVIEWED` must not imply that ledger absence proves non-deployment. The validator rejects incomplete or contradictory evidence, altered baseline tuples, duplicate/missing rows, invalid dispositions, or any attempt to authorize a hosted write. It makes no network requests or database connections. This gate protects intake integrity; it does not establish source facts that have not been supplied or substitute for an independent owner review.


## Management API token: least-privilege prerequisite

Before running `tools/run_zavqera_readonly_effect_audit.ps1`, create a **scoped** Supabase Personal Access Token for the single Development project only, with exactly these read permissions:

- **Project Settings — Read**: needed to verify the project name, region and status before any SQL is sent.
- **Database — Read**: needed for the Management API's explicit `/database/query/read-only` endpoint.

Do not grant any write permissions, organization-wide scope, secrets/billing access, or unrelated project access. Supabase documents scoped PATs as public alpha and rolling out gradually. If the token-creation screen does not offer scoped permissions, **stop**; do not substitute a classic token, because classic PATs carry the account's full access across current and future projects. See the official [Supabase Personal Access Tokens documentation](https://supabase.com/docs/guides/platform/personal-access-tokens).

The wrapper requests the token through hidden SecureString input, checks the project identity and the effective database role/transaction read-only state, and the audit script pins all 13 SELECT statements by SHA-256. These checks reduce risk but do not make a broad token safe; least-privilege token scope is a prerequisite. Never paste the token into chat, a ticket, an issue, a log, or a repository. If the capture is blocked, preserve the partial evidence and stop; do not loosen the role gate or modify the SQL pack.

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

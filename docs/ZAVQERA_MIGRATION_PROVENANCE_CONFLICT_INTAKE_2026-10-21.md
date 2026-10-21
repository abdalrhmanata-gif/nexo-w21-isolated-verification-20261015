# ZAVQERA Historical Migration Provenance Intake — 2026-10-21

Status: **OPEN / UNKNOWN where evidence is absent**. This document is an intake protocol, not evidence that any migration was deployed, not approval to modify a database, and not authorization for a hosted write.

## Scope and fixed safety boundary

The latest continuity checkpoint reports 89 checked-in migration source files versus 74 hosted migration-ledger rows, including 22 same-name/different-timestamp conflicts and six hosted-only names. These are filename/version observations only; they do not prove SQL-byte equivalence or execution history. Preserve the existing ledger as evidence; never edit `supabase_migrations.schema_migrations` to make it match a local inventory.

Do not apply W86 or any other migration to hosted Development or Production from this intake. No hosted SQL, DDL, grants, migration, ledger, secrets, auth, billing, DNS, provider calls, or deployments are authorized. Do not touch `zavqera-readonly-audit-output/` or W86. Keep `hosted_write_authorized=false`, `candidate_sha=NONE`, and trusted dispatch adapters empty/fail-closed.

## One record per disputed hosted ledger row

Create a separate record for every conflict or hosted-only tuple. Do not combine multiple migrations into one record.

| Field | Required value / rule |
|---|---|
| Intake ID | Stable unique ID from the existing provenance register; never renumber prior records |
| Hosted ledger tuple | Exact timestamp and migration name as observed in the read-only capture |
| Hosted ledger evidence | Capture filename, capture UTC timestamp, source project identifier, query identifier, and archive SHA-256 |
| Candidate source tuple(s) | Exact source filename(s), repository, branch/ref, commit SHA, and path; list alternatives separately |
| Source bytes | Exact file size, line-ending convention, and SHA-256 of raw bytes; do not normalize before preserving the original digest |
| Deployed SQL bytes | Exact bytes only if obtained from an authoritative deployment archive/receipt/backup; otherwise `UNKNOWN` |
| Deployed SQL digest | SHA-256 of exact deployed bytes; otherwise `UNKNOWN` |
| Deployment receipt | Immutable URL/record ID, execution timestamp, actor/system, target environment, and digest-to-ledger linkage; otherwise `MISSING` |
| Source provenance | How the artifact was obtained (owner clone, reflog/stash, private/deleted repository, release archive, deployment archive, backup, or other) and chain-of-custody notes |
| Comparison result | `BYTE_IDENTICAL`, `BYTE_DIFFERENT`, or `UNKNOWN`; use identical only when both raw byte streams and trusted linkage are available |
| Independent reviewer | Reviewer identity, relevant expertise, conflict disclosure, review date, and separate attributable finding; author self-review is not independent |
| Disposition | `OPEN`, `SOURCE_CANDIDATE_ONLY`, `PROVEN_BYTE_IDENTICAL`, `PROVEN_DIFFERENT`, or `UNRECOVERABLE_UNKNOWN` |
| Hosted authorization | Must remain `NO` in this intake |
| Evidence references | Exact file/line, immutable URL, artifact ID, and digest for every material assertion |

## Acceptance rules

1. A similarly named migration, a matching current source file, a ledger timestamp, a successful disposable replay, or a passing CI run is **not** a deployment receipt.
2. Never infer the deployed SQL from a later migration or reconstruct it from its filename.
3. For a claimed byte match, retain both raw files and calculate SHA-256 over each exact byte stream. Record line endings; do not silently normalize CRLF/LF.
4. A source-only artifact can be recorded as `SOURCE_CANDIDATE_ONLY`, but the deployed-byte digest and deployment receipt remain `UNKNOWN` / `MISSING`.
5. A row without enough evidence remains `OPEN` or `UNRECOVERABLE_UNKNOWN`; missing evidence is not proof that deployment did not occur.
6. Have an independent database/security reviewer adjudicate the evidence and reasoning per row. An owner's worksheet, this template, and the author's own checks do not satisfy independent review.
7. Any future remediation requires a separate minimal forward-only proposal, reviewed before/after assertions, owner-controlled backup and restore validation, and explicit written authorization naming the exact target and change. This intake grants none of those permissions.

## Evidence collection sequence

- [ ] Preserve the current read-only hosted capture and verify its archive SHA-256.
- [ ] Export the exact hosted ledger tuples from that capture; do not query or alter the ledger as part of this document workflow.
- [ ] Search owner-controlled local clones, reflogs, stashes, unpushed refs, private/deleted/external repositories, release archives, backups, deployment receipts, and change records.
- [ ] For each candidate, preserve original bytes, size, source ref/commit, and SHA-256.
- [ ] Link each hosted tuple to a trusted deployment receipt and deployed SQL digest; if unavailable, leave unknown.
- [ ] Obtain a separate reviewer disposition for each material finding.
- [ ] Reconcile counts only after preserving the per-row records; document overlaps and avoid presenting overlapping counts as disjoint totals.
- [ ] Keep launch NO-GO until every mandatory gate is supported by evidence and accountable approval.

## Current known example: W4 candidate is not closure

The continuity package identifies a source-side candidate for `20260921180052_w4_table_privilege_hardening.sql` with LF SHA-256 `3419a01a1b0ea66bd22877f478b61473cf1210006828ea3f28c5c08fb51ef0c8`. The hosted tuple is reported as `20260921180138_w4_table_privilege_hardening`. No per-row deployment receipt or digest for the hosted version was recovered. Record this as a source candidate only; do not claim deployed-byte equivalence.

## Decision summary

- Public release: **NO-GO**
- `candidate_sha`: `NONE`
- `hosted_write_authorized`: `false`
- Trusted dispatch adapters: **empty / fail-closed**
- Historical SQL provenance: **OPEN / UNKNOWN until evidence-backed per-row adjudication**

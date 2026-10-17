# ZAVQERA — Migration review source provenance (2026-10-15)

**Purpose:** Make a future offline ledger comparison reproducible at the level of checked-in migration content. This does not resolve historical migration conflicts or authorize a hosted database change.

## Fields added to `ledger_acl_review.json`, Markdown, and CLI summary

- `source_checkout_head_sha`: local `git rev-parse --verify HEAD` result, if available. It is `null` when the supplied source directory has no valid local Git checkout.
- `source_migration_manifest_sha256`: deterministic SHA-256 of UTF-8 manifest lines sorted by migration filename; each line is `filename<TAB>per-file-SHA256<LF>`. Every `.sql` file physically present directly under `supabase/migrations` is included, including untracked or ignored files; the scoped Git-clean flag distinguishes a committed migration tree from local additions and edits.
- `source_migrations_worktree_clean`: `true` or `false` from local Git status scoped to `supabase/migrations`; `null` if Git metadata is not available.

The manifest covers the actual file bytes through each per-file SHA, so it remains useful when a migration file is modified but not committed. The Git HEAD identifies the recorded commit; the clean flag distinguishes the committed migration tree from local edits. Git calls are local only; the tool does not contact a remote or run SQL.

## Tests added

- Identical migration filenames and contents produce the same manifest SHA.
- Changing migration contents changes the manifest SHA.
- When Git is available, the review records the local HEAD and reports a clean migration directory.
- Editing a migration after commit preserves the HEAD value, flips the scoped clean flag to `false`, and changes the content manifest.
- Input folders without Git metadata continue to work; HEAD and clean flag are explicitly unavailable rather than inferred.
- Rendered Markdown and CLI JSON include the provenance fields.

## Limits and safe use

The previously uploaded 12-query capture and its review ZIP do not acquire a source Git HEAD retroactively. The historical comparisons (89 source files, 74 hosted ledger rows, 46 exact tuples, 22 same-name timestamp differences and six hosted-only names) must remain associated with the captured evidence and the source checkout used by each separate review. Do not infer deployed SQL equality from a filename, timestamp, branch tip or newly generated manifest.

To create a reproducible *new offline comparison*, rerun `tools/review_hosted_migration_ledger.py --evidence-dir <capture-folder> --repo-root <exact-checkout>`, then preserve `ledger_acl_review.json`, `ledger_acl_review.md`, the source commit SHA, manifest SHA, exact evidence ZIP SHA and query-pack SHA together. Do not alter the source evidence ZIP or any hosted migration ledger.

## Release / security boundary

This tool change is offline evidence-quality work only. It does not fix `service_role` privileges on `public.agent_executions`, repair missing tables/functions, resolve historical SQL provenance, or certify Mission Authority enforcement. No hosted database write, migration, deployment, secret, billing or DNS change is authorized or performed. Keep the launch **NO-GO**, original PR #39 OPEN/DRAFT/UNMERGED, Issue #23 OPEN and `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed.


## Follow-up: 13-query read-only capture with ACL inheritance provenance — 2026-10-16

The migration-effect runner now executes the original 12 pinned SELECT queries plus one separately pinned W86 ACL provenance SELECT. The original pack remains SHA-256 `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`; the added query `supabase/tests/hosted_readonly_w86_acl_provenance_query.sql` is pinned at SHA-256 `ffdcc3f51ee20fb2ddb44e74f292df4767a76a9dff5e8cd30eef2adb8e9d4f64`. The runner validates both hashes and requires 13 SELECT-only statements in total. The query reports role membership paths, effective privileges, direct table/column ACL entries, and ACL entries inherited by `service_role`; it does not read application rows.

The offline reviewer now requires `query_13.json`, validates its role/read-only gate and pinned query hash, and records inherited table/column ACL counts and entries in the Markdown/JSON review. Any inherited ACL row is a blocker for the current W86 candidate; this audit captures and reports the state, but does not remediate it or authorize a hosted write.

**Exact-SHA verification:** W80 isolated PostgreSQL 17 workflow [run 38858063330](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38858063330) — SUCCESS on `f4d7fed423739db0d39ba576ca455c5d4a182169`. The workflow ran the read-only runner unit tests, self-test (`queries=13`), offline ledger-review tests, full local PostgreSQL 17 migration replay/regression suite, local smoke of the new ACL provenance SQL, and cleanup verification. Evidence artifact `12027554468`, ZIP SHA-256 `8147e0b3624b27bdd6dc83f566b665a8942a1b3aac3e3dd785de1a3fc45a483d`. Flutter CI also passed on the same SHA: [run 38858068979](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38858068979).

This does not retroactively add the new query to the previously uploaded 12-query ZIP. To review the current hosted role path, rerun the guarded runner on the verified read-only Development connection and preserve the resulting 13-query output with its two query hashes and exact source manifest/HEAD. No token should be pasted into chat or saved in evidence.

## Current source-provenance guard — 2026-10-17

The scoped Git cleanliness check now includes ignored paths as well as tracked modifications and ordinary untracked files. This is necessary because the reviewer enumerates every `*.sql` file under `supabase/migrations`, including files that a local `.gitignore` rule may hide from ordinary `git status`. An ignored migration file therefore changes the manifest and must also set `source_migrations_worktree_clean` to `false`; the reviewer must not describe that source tree as fully Git-clean.

Regression test: `test_ignored_untracked_migration_file_is_not_reported_clean`. The test creates an ignored, validly named migration in a temporary Git checkout and checks that the source manifest changes while the clean flag becomes false. This is offline provenance validation only.

For the current PR #2 branch snapshot, the authoritative query pins validated by the runner self-test are:
- Base query pack SHA-256: `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`.
- Query 13 ACL-provenance SHA-256: `806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b`.

Older query digests in preceding dated sections describe historical snapshots and must not be used for a new capture. No hosted database was queried or modified by this source-provenance change; historical migration SQL provenance remains unresolved and release remains **NO-GO**.

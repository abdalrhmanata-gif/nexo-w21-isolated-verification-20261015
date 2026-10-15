# ZAVQERA — Migration review source provenance (2026-10-15)

**Purpose:** Make a future offline ledger comparison reproducible at the level of checked-in migration content. This does not resolve historical migration conflicts or authorize a hosted database change.

## Fields added to `ledger_acl_review.json`, Markdown, and CLI summary

- `source_checkout_head_sha`: local `git rev-parse --verify HEAD` result, if available. It is `null` when the supplied source directory has no valid local Git checkout.
- `source_migration_manifest_sha256`: deterministic SHA-256 of UTF-8 manifest lines sorted by migration filename; each line is `filename<TAB>per-file-SHA256<LF>`. All checked-in `.sql` files under `supabase/migrations` are included.
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

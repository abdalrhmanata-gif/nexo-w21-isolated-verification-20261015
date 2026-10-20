# ZAVQERA Four-Blocker Remediation Checkpoint

**Observed:** 2026-10-20  
**Purpose:** preserve current release evidence and the exact external dependencies still required.  
**Status:** evidence checkpoint only; not an independent review, production approval, or authorization to change hosted systems.

## Decision

**Public launch: NO-GO.** Keep `candidate_sha=NONE`, `hosted_write_authorized=false`, and `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed. No hosted database writes, migration/ACL changes, Auth setting changes, paid provider calls, billing activation, production deployment, or protected merge were performed.

## 1. Independent security/database review — OPEN

- Review intake: https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/issues/4
- Audit PR #3: https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/3
- Main release gate: https://github.com/abdalrhmanata-gif/Nexo/issues/31
- No independently attributable review submission was found in the evidence checked.
- A formal GitHub reviewer request for `Farenhytee` and `eugenicum` was rejected with HTTP 422 because GitHub review requests are limited to repository collaborators. No collaborator access was granted. Existing public invitations are not approvals.

**Acceptance evidence:** an independent reviewer states relevant expertise/conflicts and files findings against exact source/evidence SHAs, with severity, rationale, and disposition. The author cannot self-certify this gate.

## 2. Hosted migration provenance and Supabase security — OPEN

### Filename/ledger reconciliation pinned to a source SHA

Compared source filenames at `abdalrhmanata-gif/Nexo@51c3c911b9f7eda344067f1c7d804d8ab83d61ff` against the current read-only Development migration ledger:

- Source SQL migration files: **87**
- Hosted ledger rows: **74**
- Exact version/name tuple matches: **46**
- Source tuples absent as exact hosted tuples: **41**
- Hosted tuples not exact source tuples: **28**
- Same-name/version conflicts among the latter: **22**
- Hosted-only names: **6**

These are counts of filenames/ledger tuples only. They do **not** prove SQL-byte equivalence, ordering equivalence, successful deployment receipts, or schema parity. The earlier 89-source count belongs to a different/later source snapshot and must be pinned to its own SHA.

### Current read-only Supabase findings

- Development project `mrwmmbytcymqgwvcoywd`: ACTIVE_HEALTHY, PostgreSQL 17.6.1.166, `eu-west-1`.
- Supabase Security Advisor: `auth_leaked_password_protection` WARN / disabled.
- A fresh table/advisor lookup reports CRITICAL `rls_disabled` for:
  - `private.anonymous_ai_visitors` (385 rows reported)
  - `private.anonymous_ai_ip_windows` (384 rows reported)
  - `private.anonymous_ai_reservations` (386 rows reported)
- Earlier catalog/ACL evidence recorded no direct grants to `anon`, `authenticated`, or `service_role`, and no `USAGE` on schema `private` for `anon`. Therefore the generic RLS advisory must be independently reconciled against effective ACLs, inherited grants, schema/API exposure, SECURITY DEFINER routines, and call paths before selecting remediation.

**Acceptance evidence:** independent review of source SQL, deployment receipts and hashes, the complete approved read-only capture, current catalog/ACL/routine evidence, and an ordered migration reconciliation. Any remediation requires a separately reviewed change and explicit authorization. Do not blindly enable RLS without checking required server-only reservation/quota paths.

## 3. Operational verification — OPEN

### OpenAI and quota/cost

- Netlify environment metadata shows `OPENAI_API_KEY` is configured with masked values in branch-deploy, deploy-preview, and production contexts, but empty in dev.
- The key's validity, model access, cost/budget, successful live request, quota accounting, failure accounting, and abuse behavior are unverified.
- No provider request was made and no paid usage was triggered.

**Acceptance evidence:** owner-authorized bounded non-production budget; controlled test account and secret; successful and failed provider requests; evidence of reservation/consume/release accounting, retries, rate limits, and sanitized logs. Never expose secret values.

### Password reset and recovery

- Repository routes exist for `/auth/forgot-password` and `/auth/reset-password`; their existence does not prove the hosted email/callback flow works.
- Existing operations documentation states hosted auth/browser E2E has not been executed and representative backup/recovery is not verified.
- A prior disposable restore smoke used synthetic data; it is not a production-data or full managed-schema restore. RPO/RTO are not measured or accepted.
- Supabase organization plan is Free; no paid upgrade or backup target is authorized.

**Acceptance evidence:** an owner-approved test identity/inbox; hosted reset email and callback/expired-link checks; an explicitly approved isolated restore target; independently retained backup; application/Auth/Storage recovery evidence; timed drill and owner-accepted measured RPO/RTO. Do not use production restore as an experiment.

## 4. Billing/webhooks and final approval — OPEN

- Billing contract PR #42: https://github.com/abdalrhmanata-gif/Nexo/pull/42 — OPEN / Draft / Unmerged, design-only.
- Pricing UI states paid billing is not enabled; Plus/Pro CTAs are not purchasable.
- No payment SDK, verified provider webhook lifecycle, or payment-backed entitlement source is implemented/verified.
- The contract proposes Stripe Checkout/Billing, but no provider account, price IDs, live/test keys, tax/legal configuration, or verified webhook endpoint is established.
- No billing credentials, provider account, migration, paid service, live payment, deployment, or merge was created.

**Acceptance evidence:** confirm merchant eligibility, legal entity, currency, VAT/tax, cancellation/refund and customer terms; implement provider-specific checkout and raw-body signature verification; persist event IDs idempotently and handle out-of-order events; derive entitlements only from verified provider state; enforce quota atomically; pass test-mode purchase/failure/cancellation/duplicate-event/cross-user tests; verify test webhook delivery; complete an independent schema/security review. Live billing activation requires separate explicit owner approval.

## Safe next sequence

1. Obtain an actual independent security/database review on the exact source and evidence SHAs.
2. Complete the approved read-only Development capture and historical SQL/deployment-receipt reconciliation; do not apply migrations while provenance is unresolved.
3. Resolve the RLS/ACL/function exposure finding through a reviewed remediation and explicit authorization.
4. Obtain explicit non-production cost budget and an approved test identity/inbox; run real OpenAI/quota and hosted password-reset tests.
5. Approve a restore target, retained backup, operators and retention; conduct a timed representative recovery drill and record RPO/RTO.
6. Complete payment-provider/legal setup and test-mode webhook/subscription lifecycle; keep live billing disabled until test evidence and review pass.
7. Obtain explicit release approval only after all gates close.

A green isolated CI run, public reviewer invitation, masked secret, or successful synthetic restore is not a substitute for the evidence above.

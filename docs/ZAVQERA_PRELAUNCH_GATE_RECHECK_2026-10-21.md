# ZAVQERA Pre-Launch Gate Recheck — 2026-10-21

## Decision

**PUBLIC LAUNCH: NO-GO.** This is a repository/evidence review, not a launch authorization. Keep `candidate_sha=NONE`, `hosted_write_authorized=false`, and `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed.

No production deployment, merge, hosted database mutation, migration application, ACL/RLS/auth/config change, secret read or modification, billing action, DNS change, provider API call, or mutating quota RPC is authorized by this review.

## Recheck method and limits

Checked current GitHub PR metadata, the latest documented exact-head workflow runs, and the independent-review record on 2026-10-21. Statements below are tied to specific SHAs. Green disposable/isolated CI is not proof of hosted database parity or production readiness. No independent reviewer submission was recorded for isolated audit PR #3 at the time of this check.

## Gate matrix

| Gate | Current evidence | Status | Required closure evidence |
|---|---|---|---|
| Fail-closed AI provider gate | Main repo PR #45, HEAD `7ee74ebdd58c6cbfadb0f6d6a5b7196505ab0aa6`; AI Plan Function CI run 39474956527 and Flutter CI run 39474956481 succeeded on that SHA. Gate returns HTTP 503 before provider call. | PASS for safety guard only; feature is intentionally unavailable through the direct Flutter path | Select and implement one authoritative server-side request path, then prove quota reservation/settlement, both-client behavior, concurrency and uncertain-outcome recovery in isolated tests. Do not enable the constant alone. |
| Explicit model configuration | Main repo PR #44, HEAD `3e39c3cd6aea415ada3dc37e43109dd71258cb14`, OPEN/Draft/Unmerged | OPEN | Confirm exact-head CI and review; ensure missing/blank `OPENAI_MODEL` fails before any provider request. |
| Anonymous quota RPC path | Main repo PR #40, HEAD `3c9a9ab11a22c39ae270ff0ae1efea94e0627976`, OPEN/Draft/Unmerged. Isolated PG17/PostgREST/pgTAP run 39408110610 passed 28/28 assertions on this SHA. | Isolated contract PASS; hosted behavior unverified | Independent review, read-only verification of live exposed-schema/request routing and key type metadata (never secret value), provenance reconciliation, and explicit approval before any hosted migration. Never test via mutating RPC. |
| Reservation identity / concurrency | Main repo PR #43, HEAD `51c3c911b9f7eda344067f1c7d804d8ab83d61ff`; W21 run 39444539214 and Flutter CI runs 39444539220 / 39444545887 succeeded on that SHA. | Isolated exact-head PASS | Independent review and hosted migration provenance/parity; do not infer hosted safety from disposable CI. |
| Paid billing / entitlements | Main repo PR #42, HEAD `40b7398eca1310328e7a44e1b9b86a32eb26c679`, OPEN/Draft/Unmerged. Repository evidence says paid billing is not implemented and there is no verified payment-backed entitlement projection. | BLOCKED | Implement and independently review verified subscription-to-entitlement projection, checkout/webhook handling, idempotency, refunds/cancellations, abuse controls and test-mode evidence before charging customers. |
| Hosted migration provenance | Published Development evidence reports 89 checked-in source migrations vs 74 hosted ledger rows, 22 version conflicts and six hosted-only names in the captured snapshot. Counts are snapshot-specific and must be reconciled against pinned source and live evidence. | BLOCKED | Produce a row-by-row mapping of source SQL raw-byte hashes, deployed migration identity/hash, trusted deployment receipt and reviewer disposition. Preserve UNKNOWN where evidence is missing. Do not rewrite the hosted ledger to force alignment. |
| Hosted Development security/schema drift | Published evidence includes direct `service_role` grants on `public.agent_executions`, missing expected relations/columns/constraints/indexes/trigger, routine/default EXECUTE ACL drift and an audit role with `rolbypassrls=true`. Anonymous AI tables in `private` have RLS disabled in catalog despite no direct table grants to anon/authenticated in the observed ACL. | BLOCKED pending independent adjudication | Independent least-privilege review of effective grants, role membership, exposed schemas, function owner/security mode/search_path and callable paths. Do not blindly enable RLS or modify grants. |
| Anonymous AI reservation tables / quota wrappers | Audit issue #5 records `relrowsecurity=false` and `relforcerowsecurity=false` for three private tables; issue #6 records public SECURITY DEFINER wrappers executable by postgres/service_role, while anon/authenticated cannot execute them. Netlify key values are masked and the key prefix/type is not verified; route profile and exposed-schema configuration remain unverified. | BLOCKED pending independent review and safe read-only evidence | Reconcile source migrations, live catalog and gateway settings. Keep keys secret; record only key type/prefix metadata. No DDL, grants, API settings, secret changes or quota-mutating calls. |
| Independent review | Isolated audit PR #3 at HEAD `0c9f3fdf47fa8af0e50fe879c9630d5b2d3a8c88` has Web Unit 39593164561, Web CI 39593164529 and Flutter CI 39593164545 successful. Review-submission list returned empty. | BLOCKED | Obtain attributable independent security/database and launch-gate reviews with findings, severity and disposition. Owner-authored notes and CI are not independent approval. |
| Recovery / operations | Published seeded restore smoke covered 52/52 application/auth/migration relations with a synthetic sentinel; extension-managed relation parity was not proven (source 2, restored 0). This is not a representative production-data/Storage restore. Measured RPO/RTO and operations acceptance remain open. | BLOCKED | Restore a representative sanitized application + Storage backup in an isolated environment, verify extensions and integrity, measure RPO/RTO, test incident/rollback procedures, and obtain operations acceptance. |
| Production provider and customer acceptance | No provider live-call/cost certification or complete end-to-end release evidence is established by the cited isolated runs. | BLOCKED | Run authorized, budget-capped pre-production tests with verified credentials and explicit cost ceilings; test auth, malformed output, timeout, retries, idempotency, policy review and mission completion. Keep external actions behind explicit authority/approval. |
| Release owner sign-off | No evidence in this recheck of an approved release candidate SHA, independent sign-off, rollback owner, incident owner, or production deployment authorization. | BLOCKED | Pin an exact candidate SHA and artifacts; record named accountable approvals, rollback plan, monitoring, support/incident ownership, privacy/terms, and go/no-go decision. |

## Current PR status snapshot

- Main PR #45: OPEN / Draft / Unmerged, HEAD `7ee74ebdd58c6cbfadb0f6d6a5b7196505ab0aa6`.
- Main PR #44: OPEN / Draft / Unmerged, HEAD `3e39c3cd6aea415ada3dc37e43109dd71258cb14`.
- Main PR #42: OPEN / Draft / Unmerged, HEAD `40b7398eca1310328e7a44e1b9b86a32eb26c679`.
- Main PR #40: OPEN / Draft / Unmerged, HEAD `3c9a9ab11a22c39ae270ff0ae1efea94e0627976`.
- Main PR #43: OPEN / Draft / Unmerged, HEAD `51c3c911b9f7eda344067f1c7d804d8ab83d61ff`.
- Isolated audit PR #3: OPEN / Draft / Unmerged, HEAD `0c9f3fdf47fa8af0e50fe879c9630d5b2d3a8c88`; exact-head Web Unit/Web CI/Flutter CI succeeded; review submissions empty.
- Isolated audit PR #2 is merged, but its merge preserves audit artifacts only; it is not independent approval or hosted provenance reconciliation.

## Mandatory no-go conditions

Do not launch, deploy, merge protected work, enable provider calls, or apply hosted migrations until every BLOCKED gate has evidence-backed closure and accountable approval. Keep the current fail-closed behavior. A green CI check, a merged audit-artifact PR, a masked deployment variable, or a successful disposable restore is not a substitute for missing hosted evidence.

## Safe next actions

1. Obtain an independent reviewer who can submit an attributable review; read-only issue discussion is welcome but is not a submitted approval.
2. Complete source-to-hosted migration provenance mapping without changing the ledger.
3. Complete independent review of hosted ACL/RLS/routine/schema drift and the anonymous quota call path.
4. Decide and implement one authoritative AI planning/quota path for both web and Flutter; keep provider dispatch disabled until isolated tests cover failure and reconciliation.
5. Implement and test billing/entitlement lifecycle only if paid launch is in scope; otherwise launch free-only with no paid claims or charges.
6. Complete representative recovery, RPO/RTO, provider-cost, operational and user-acceptance evidence.
7. Re-run the full launch gate on the exact release SHA, then record independent review and explicit owner go/no-go.

**Disposition:** NO-GO remains the only evidence-supported release decision on 2026-10-21.

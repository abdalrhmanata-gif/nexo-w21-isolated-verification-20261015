# ZAVQERA Universal Egress Boundary — Implementation Plan (2026-10-15)

**Status:** Design/acceptance plan only. This document does not claim universal egress mediation is implemented or proven.
**Candidate:** PR #39, Draft / unmerged.
**Non-negotiable:** Keep the provider adapter registry empty until the runtime boundary and provider contract pass review. No live credentials, hosted Supabase changes, production deployment, or PR merge are part of this work.

## 1. Current evidence and its limit

The current candidate has source-graph tests for Mission Action API routes, a deny-by-default trusted adapter registry, an authenticated internal worker route, a request-body ceiling, and an actual-route integration test under Docker `--network none`. Commit `843855a75e7a1e5b1a06456b7e42347357969020` added adversarial egress probes under `--network none` for direct `fetch`, Node HTTP/HTTPS, TCP/TLS sockets, DNS resolution, and a child-process socket attempt; Web Unit, Web CI, Flutter CI and W21 passed on that source/test checkpoint (runs 38688489190, 38688489262, 38688489297, and 38688482588). The newer test-only topology prototype under `tool/mission-executor/` runs an executor only on an internal Docker network, a fake provider on a separate egress network, and a fixed-destination fake gateway on both. The new topology step passed in W21 run 38689614876; full W21 is still running on `d97d2e97ca1f4f1d6e7a92ef788766ccb97a0562`. Web Unit and Web CI passed on `d97d2e9`; Flutter CI was still running at this note. The current branch also inventories other network-capable app routes and identity/session entrypoints separately.

These controls are useful defense-in-depth, but they do **not** establish a universal runtime egress boundary:
- Static source analysis cannot prove the absence of every dynamically loaded, native, transitive dependency, or future runtime path.
- A test container with networking disabled proves only that tested route's behavior in that test environment.
- The Next.js/Netlify application runtime can still make ordinary outbound requests for separately authorized workflows (for example, AI planning/research, password-range lookup, identity/session operations, and invitation email). These are distinct effects and must not be misrepresented as Mission Action dispatch.
- The real provider registry is intentionally empty. No real provider receipt or reconciliation behavior has been tested.

## 2. Required target architecture

Mission Action side effects must run in a **separate executor runtime** whose network policy is controlled independently of the web application. The web app must not possess direct provider credentials or a direct route to provider APIs for Mission Action execution.

Target flow:

1. Authenticated web request records an intent; it cannot perform the external effect.
2. A trusted executor receives a narrow, signed/strongly authenticated execution envelope containing immutable execution ID, mission/action IDs, audience, authority revision, idempotency key, expiry, and payload digest.
3. The executor verifies the envelope and atomically claims the JIT authorization/lease from the authoritative ledger before any provider operation.
4. The executor can reach provider APIs only through an explicitly controlled egress gateway or equivalent network policy. Direct internet egress from the executor is denied by default.
5. Provider requests carry stable provider idempotency identifiers where supported. The executor persists dispatch-start evidence before sending and stores provider receipt evidence after a response.
6. A timeout or lost response becomes `UNKNOWN`, never an automatic retry. Reconciliation must query authoritative provider state or prove `NOT_SENT` before retry authority can be released.
7. The result is accepted only when the receipt is bound to the same execution, audience, request digest, and provider account/context. Untrusted adapter output cannot authorize itself.
8. All egress decisions and execution transitions are auditable. No request-supplied URL, adapter code, transport, or provider configuration can select a destination or bypass the gateway.

## 3. Acceptance gates

### Gate A — source inventory (partial evidence exists)
- Enumerate every production entrypoint: API routes, server actions, middleware, scheduled jobs, worker handlers, and any native/CLI runtime entrypoints.
- Trace static local imports and flag outbound-capable transports, dynamic loaders, child processes, native loading, provider SDKs, and unknown third-party packages.
- Every exception must have an explicit effect classification, rationale, owner, and test.
- This gate is a regression detector, not a substitute for runtime network enforcement.

### Gate B — isolated executor runtime (not implemented/proven)
- Create a separate executor service/runtime; do not add it as a privileged capability to the public web process.
- Default-deny outbound networking. Permit only the egress gateway and the minimum ledger/control-plane endpoints needed to claim and record results.
- Keep provider credentials only in the executor/gateway secret scope, never in browser bundles or general web runtime.
- Prove from inside the deployed-equivalent executor that direct provider DNS/HTTPS/socket attempts fail and the approved gateway path succeeds.
- Verify the same denial from every supported process, child process, native module, and worker context.

### Gate C — provider contract (not tested against a real provider)
- Fake-provider contract tests must cover duplicate requests, replay, timeouts before/after send, malformed/missing receipts, receipt-binding mismatch, provider 429/5xx, cancellation races, and reconciliation after `UNKNOWN`.
- Require provider-specific evidence for idempotency and authoritative lookup. If the provider cannot establish whether an effect happened, the action remains `UNKNOWN` and cannot be retried automatically.
- A real adapter can be proposed only after Gates A–C pass; registration remains disabled until a separate security review approves the provider and account scope.

### Gate D — release evidence (not complete)
- Re-run Web Unit, Web CI, Flutter CI, and W21 on one exact code SHA; keep artifact links and SHA together.
- Validate hosted Development schema parity using read-only inspection or a separately approved safe procedure; do not change hosted Development or Production as part of this plan.
- Verify deployed executor egress policy, secret separation, logging/redaction, rollback, and recovery behavior.
- Keep launch **NO-GO** until every required gate has evidence and review.

## 4. Current disposition

| Control | Current status |
|---|---|
| Authenticated internal worker HTTP gate | Implemented for the candidate route; tests exist |
| Static Mission Action source-graph guard | Regression coverage exists; not universal runtime proof |
| Adapter registry | Empty / fail-closed |
| Real-provider idempotency and receipt contract | Not verified |
| Separate network-restricted executor and enforced egress gateway | Production runtime not implemented/proven; disposable Docker topology prototype exists and its isolated-network step passed, with full W21 still running |
| W21 on current branch head | Not yet confirmed for `843855a75e7a1e5b1a06456b7e42347357969020`; prior verified pass is on ancestor `43edddf6050ac56ad9d1d8f4120f9d389a333c8a` |
| Hosted Development parity | Not established |
| Launch | **NO-GO** |

## 5. Next concrete work order

1. Preserve the empty registry and keep PR #39 Draft.
2. Complete W21 on the current exact source/test SHA and retain the full evidence/cleanup artifact.
3. Extend the local topology prototype to cover dynamic loaders and transitive/native dependency paths; current probes cover selected Node network APIs and one child process only.
4. Expand fake-provider contract tests for timeout boundaries, malformed receipts, receipt-binding mismatch, provider 429/5xx, cancellation races, and reconciliation after `UNKNOWN`.
5. Only then design the production executor/control-plane integration; keep it separate from the public web process and do not deploy or register a real provider.

## Exact source/test checkpoint — 2026-10-15 — `f146b11914b81f68ed025ac96d99befb0c2c8362`

This checkpoint supersedes the older running-status statements above.

### Exact-head CI

All three workflows passed on code/test SHA `f146b11914b81f68ed025ac96d99befb0c2c8362`:
- Web Unit: [run 38697461636](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38697461636) — SUCCESS.
- Web CI: [run 38697461610](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38697461610) — SUCCESS.
- Flutter CI: [run 38697461393](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38697461393) — SUCCESS.

### New disposable executor/gateway contract probes

The topology under `tool/mission-executor/` remains test-only; no production runtime or deployment configuration was changed. The isolated-network step in [W21 run 38697454403](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38697454403) passed on this exact SHA, with these cases:
- Direct egress denial using static Node networking APIs, ESM dynamic imports, CommonJS `createRequire`, HTTP/HTTPS/TLS, and a fresh child process.
- Fixed-destination gateway dispatch to the fake provider with request-supplied destinations rejected.
- Stable replay/idempotency binding and exact provider request counters to detect hidden retries.
- Simulated accepted-then-lost response, missing/malformed/mismatched receipts, 429/500 responses, client cancellation, and reconciliation through a separate fixed-destination lookup endpoint.
- Reconciliation receipt-binding mismatch rejection, exact expected dispatch/reconciliation counts, and cleanup verification in the smoke-script trap.

The full W21 run on `f146b11914b81f68ed025ac96d99befb0c2c8362` had also passed the disposable PostgreSQL 17/pgTAP gate, Mission Authority execution security regressions, AI quota/plan/workspace security, actual-ledger concurrent idempotency, atomic budget, dispatch-claim and reconciliation-claim races, and W72 persistent fake-provider gateway integration. At the time this checkpoint was written, the browser E2E step was still running; cleanup verification and evidence upload were not yet confirmed. Do not mark the full W21 gate successful until the run concludes successfully.

The reconciliation endpoint is a fake-provider contract test, not a production service. Its `NOT_FOUND` response is not treated as proof that an external effect was never sent. The executor smoke test does not automatically retry dispatch after an unknown result. The test harness's fake provider stores receipts in process memory; this proves only the explicit test scenario, not provider-side durability or real provider semantics.

### Current release disposition

- `TRUSTED_DISPATCH_ADAPTERS` remains empty; no real provider is registered or enabled.
- Hosted Supabase Development schema parity remains unverified, and no hosted project was modified.
- Production-deployed network policy, provider credential separation, real-provider idempotency, receipt authenticity, authoritative reconciliation and proven `NOT_SENT` semantics remain unverified.
- Universal outbound-effect mediation across every production entrypoint remains **NOT ESTABLISHED**.
- PR #39 remains Draft/open/unmerged; Issue #23 remains OPEN.
- Launch remains **NO-GO**.

## W21 exact-source/test result — completed 2026-10-15

Full W21 Local Launch Gate **PASSED** on the exact code/test SHA `f146b11914b81f68ed025ac96d99befb0c2c8362`: [run 38697454403](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38697454403).

Completed steps on that SHA include the isolated executor/network topology; disposable PostgreSQL 17 migration replay and pgTAP; Mission Authority execution security regressions; AI quota/plan/workspace security; actual-ledger concurrent idempotency, authority-budget, one-time dispatch-claim and one-time reconciliation-claim races; W72 persistent gateway integration with fake providers; full launch-gate browser E2E; disposable stack cleanup and cleanup verification; and evidence + browser-diagnostics uploads.

Artifacts:
- [W21 evidence](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38697454403/artifacts/11955043175)
- [Browser diagnostics](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38697454403/artifacts/11954987983)

The three exact-head CI workflows also passed on `f146b11914b81f68ed025ac96d99befb0c2c8362` (Web Unit run 38697461636; Web CI run 38697461610; Flutter CI run 38697461393). A documentation-only commit was subsequently added to record this result; the full W21 result applies to the exact source/test SHA above, not to a newly tested production deployment.

This is a local/disposable evidence pass, **not** production certification. No hosted Supabase schema parity, deployed network policy, real provider idempotency, real receipt authenticity or authoritative real-provider reconciliation was tested. `NOT_FOUND` is not equivalent to `NOT_SENT`; no automatic retry is permitted after an unknown outcome without stronger provider-specific evidence. The trusted provider registry remains empty and launch remains **NO-GO**.

## Test-only gateway authentication follow-up — 2026-10-15

**Source/test SHA:** `3527f31f795bfb2321627343f8f6fb25cbccc4bf`.

The disposable Docker smoke harness now generates a fresh 256-bit random token for every run and passes it only to the isolated executor and the fake gateway. The fake gateway rejects `POST /v1/execute` and `POST /v1/reconcile` with HTTP 401 when the authorization header is absent or the token is invalid, before reading the request body or forwarding to the fake provider. The smoke test asserts all four denial cases. The provider's exact dispatch/reconciliation counters fail if those denied requests are forwarded.

This is test-fixture authentication only. It is not the production identity/signature protocol, does not prove a caller's ledger authority, and is not evidence of production credential isolation. The token is per-run and is not forwarded to the fake provider.

### CI on the authentication follow-up SHA

All three GitHub Actions workflows passed on `3527f31f795bfb2321627343f8f6fb25cbccc4bf`:

- Web Unit: [run 38700344037](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38700344037) — SUCCESS.
- Web CI: [run 38700344198](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38700344198) — SUCCESS.
- Flutter CI: [run 38700343936](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38700343936) — SUCCESS.

The latest **confirmed full W21 pass remains** run 38697454403 on source/test SHA `f146b11914b81f68ed025ac96d99befb0c2c8362`. A full W21 result for the new authentication follow-up SHA is not confirmed in this checkpoint and must not be inferred from the three workflows above.

### Updated disposition

- Test-only gateway authentication: implemented in the disposable smoke harness and covered by Web Unit/Web CI/Flutter CI on SHA `3527f31`; full W21 on this exact SHA remains unconfirmed.
- Production executor, production gateway identity, production network policy, live-provider behavior, and hosted schema parity: not established.
- Provider registry: empty / fail-closed.
- Issue #23: remains OPEN. PR #39: remains Draft/open/unmerged.
- Launch: **NO-GO**.

## Direct fake-provider IP isolation follow-up — 2026-10-15

**Exact code/test SHA:** `b184b91540c80be8a07b455bddaeca9080fad4f0`.

The disposable topology now discovers the running fake provider's actual IPv4 address and passes that address to the isolated executor test. Before testing normal gateway dispatch, the executor attempts a direct TCP connection to the discovered provider IP on port 9090; the test fails if the connection succeeds and passes only for a recognized network-denial error. The existing approved gateway path must still succeed afterward. This closes the weakness where a negative probe to a reserved TEST-NET address could fail even if the test did not prove isolation from the actual fake provider container.

### Exact-SHA CI

All three workflows passed on `b184b91540c80be8a07b455bddaeca9080fad4f0`:

- Web Unit — PASS: [run 38701026107](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38701026107). The run includes the Docker `--network none` worker-route/adversarial-egress test step.
- Web CI — PASS: [run 38701026169](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38701026169).
- Flutter CI — PASS: [run 38701026080](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38701026080).

The confirmed full W21 pass remains [run 38697454403](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38697454403) on earlier code/test SHA `f146b11914b81f68ed025ac96d99befb0c2c8362`. A full W21 result for `b184b91540c80be8a07b455bddaeca9080fad4f0` is not confirmed in this record and must not be inferred from the three workflows above.

### Updated disposition

- Test-only fake gateway authentication and direct-IP isolation probes: implemented and covered by exact-SHA CI above.
- Production executor/gateway identity, deployed network policy, real-provider contract, provider credential separation, authoritative real-provider reconciliation, and hosted Development schema parity: not established.
- Universal production egress mediation: **NOT ESTABLISHED**.
- Provider registry: empty / fail-closed.
- PR #39: Draft/open/unmerged. Issue #23: OPEN.
- Launch: **NO-GO**.



## Exact-source/test checkpoint — UDP and HTTP/2 — 2026-10-15

**Code/test SHA:** `5dc99d6dfb3ba37ced235482fa7e6a461489b0ae`.

The disposable topology now verifies a direct HTTP/2 connection attempt to the actual fake-provider IPv4 address is denied and that a UDP datagram submitted by the isolated executor is not received by a bound fake-provider UDP canary (`udpProbeCount === 0`). The provider's UDP endpoint is bound before HTTP readiness is exposed, avoiding a false pass from probing an unbound destination.

Exact-SHA results:
- Web Unit — [38706603498](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38706603498) — SUCCESS.
- Web CI — [38706603331](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38706603331) — SUCCESS.
- Flutter CI — [38706597163](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38706597163) — SUCCESS.
- Full W21 — [38706597203](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38706597203) — SUCCESS.

Artifacts: [W21 evidence 11958244046](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38706597203/artifacts/11958244046), [browser diagnostics 11958393754](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38706597203/artifacts/11958393754).

This closes only the new test-fixture coverage gap. Universal production egress mediation, the production executor/gateway and network policy, production credential separation, real-provider idempotency and authoritative reconciliation, and hosted Development schema parity remain unproven. Launch stays **NO-GO**.


## Production entrypoint graph guard — exact source/test SHA `c50b9db5610f483f63abdb1504465711c8e3b74e`

The local Mission Action dependency-graph test now treats App Router routes, root/nested page and layout/metadata handlers, middleware, instrumentation and every detected `"use server"` module as source roots. It additionally rejects new conventional background/worker/job/cron/scheduled/task/queue/platform-function paths until reviewed and inventoried. The regression explicitly asserts root `app/page.tsx` and `app/layout.tsx` are in the entrypoint set and that only the authenticated internal worker route can reach the persistent dispatch gateway/worker boundary/registry.

Exact-SHA CI passed:
- [Web Unit 38708716964](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716964)
- [Web CI 38708723357](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708723357)
- [Flutter CI 38708716868](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716868)

W21 [run 38708716869](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716869) was still running its browser E2E at the time of this update; no full-gate claim is made on `c50b9db` yet. The previous completed W21 pass on parent source/test SHA `3e4f6a573e3be3df86b7fa5d6035b2a7eb989e92` is [run 38707978336](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38707978336), with [evidence artifact 11959556889](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38707978336/artifacts/11959556889) and [browser diagnostics 11959343783](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38707978336/artifacts/11959343783).

Static source reachability remains a regression detector, not universal runtime egress proof. Production network enforcement, native/transitive runtime coverage, deployed credential separation, real-provider contract evidence, and hosted Development schema parity remain open. Release stays **NO-GO**.

## Static dependency-edge parser hardening — 2026-10-15

The source-graph regression now extracts module edges with the TypeScript AST rather than regular expressions. It covers import/export declarations, TypeScript `import name = require("...")`, literal dynamic imports, and literal CommonJS `require`, while ignoring import-shaped strings and comments. This closes a parser omission in the static graph guard; it remains static evidence and does not establish runtime or production egress enforcement.

Local verification on commit `9e71be9a90f572129411a585812860196d01e817`: focused worker-boundary test **27/27 PASS**; Web Unit **368 passed, 0 failed, 1 skipped**; `git diff --check` PASS. Exact-SHA CI/W21 is pending. The commit remains local because publishing this PR branch triggers automatic Vercel Preview deployments, which this continuation prohibits. Provider registry remains empty; launch **NO-GO**.

## Completed W21 checkpoint — production-entrypoint graph guard — 2026-10-15

**Exact source/test SHA:** `c50b9db5610f483f63abdb1504465711c8e3b74e`.

All exact-SHA gates passed:
- Web Unit: [38708716964](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716964).
- Web CI: [38708723357](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708723357).
- Flutter CI: [38708716868](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716868).
- Full W21: [38708716869](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716869).

W21 successfully completed browser E2E, disposable PostgreSQL 17/pgTAP, execution/authority regressions, quota/workspace checks, ledger races, W72 fake-provider integration, container cleanup verification and evidence uploads:
- [Evidence artifact 11959867882](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716869/artifacts/11959867882)
- [Browser diagnostics 11959932304](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716869/artifacts/11959932304)

The expanded static entrypoint guard explicitly includes the root App Router page/layout. The guard is only source-reachability regression evidence; it does not establish universal runtime egress enforcement or production/provider certification. Production network policy, deployed credential separation, real-provider idempotency/receipt/reconciliation, and hosted Development parity remain unproven. Launch remains **NO-GO**.

## Latest exact-source verification — `dad0734e1fbc76a31d40ac66b19dd7332963a78a`

The AST graph parser includes constant no-substitution template literals in `import()`/`require()` dependency edges. Template literals with substitutions are not treated as resolved edges and remain flagged by the computed-loader guard. Coverage includes import/export/type declarations, TypeScript import-equals, quoted and constant-template dynamic imports/CommonJS loads, and misleading comment/string text.

Exact-source local results: `node --test test/mission-authority-worker-auth.test.mjs` exit 0 (**27/27**); `npm test` from `apps/web` exit 0 (**368 passed, 0 failed, 1 skipped**, OS-level egress isolation skipped because Docker is unavailable); `git diff --check` exit 0. W21 has not run on this SHA: Docker, Supabase CLI and `psql` are unavailable. Its disposable PostgreSQL 17/pgTAP, database-backed race/security tests, fake-provider Docker integration and network isolation are unverified for this commit. The Web Unit's Node-only cases are not substitutes.

No safe remote exact-commit run is available: workflow dispatch would resolve the remote branch, still at `9d752a59f0683ea7149633138dc85bb33cf9a41b`, and the new commits are not pushed. Pushing the PR branch triggers automatic Vercel Preview deployments, so no push or dispatch was made. Production-wide egress enforcement, production provider guarantees/recovery, and hosted schema parity remain blockers; release **NO-GO**.

## Adversarial AST guard hardening — `f5115fb11969859156f2b78e995befbb762538d5`

The local Mission Action import-graph guard now resolves configured TypeScript `paths` and the existing `@/` root alias, extension/index forms, and slash-normalized paths; rejects unresolved local executable imports and AST parse errors; skips erased type-only edges/declaration files/assets; and parses JavaScript, JSX, TypeScript and TSX with the matching grammar. Every module reachable from inventoried production entrypoints is checked for unreviewed dynamic loading/code generation and restricted runtime imports. New regression tests cover forbidden re-export reachability, unresolved aliases, `module.require`, `module._compile`, `module.createRequire` and aliases, `process.mainModule`, computed global/module loading, `eval`, `Function`, Reflect capability recovery/construction, WebAssembly compilation/instantiation, and harmless comments/strings/`require.resolve`.

Exact local checks on this source/test SHA: focused Node test exit 0 (**31 passed**); Web Unit `npm test` exit 0 (**372 passed, 0 failed, 1 skipped**); `git diff --check` exit 0. The single skip is Docker-backed OS network isolation.

W21 did **not** run on this SHA. The required local executables `docker`, `supabase`, `psql`, and `pg_prove` are unavailable. Therefore no exact-SHA PG17 migration replay/pgTAP, database races/security proofs, Docker fake-provider integration, W21 browser E2E or cleanup verification is claimed. No remote run was dispatched because it would not contain this local commit and publishing can trigger deploy previews.

This test remains a source-graph guard. It cannot prove arbitrary package/transitive/native behavior or all reflective/runtime loading forms, nor does it establish production-wide egress mediation. PR #39 is still OPEN / Draft / unmerged at remote head `9d752a59f0683ea7149633138dc85bb33cf9a41b`; Issue #23 remains OPEN; the adapter registry remains empty. Continue with exact-SHA disposable W21 verification on an isolated runner; release remains **NO-GO**.

## Exact-SHA isolated W21 result — 2026-10-15

W21 [run 38729334501](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38729334501) completed SUCCESS on `f5115fb11969859156f2b78e995befbb762538d5` in the temporary public verification repository [`nexo-w21-isolated-verification-20261015`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015), not Nexo. It replayed **88 checked-in migrations** into disposable PostgreSQL 17 and passed **41 pgTAP invocations / 594 assertion executions**, executor/network isolation, Mission Authority and quota/workspace SQL regressions, four actual-ledger concurrency races, W72 fake-provider PostgreSQL integration, two browser E2E tests, disposable cleanup and cleanup verification. No hosted database, real provider, external email, or deployment was targeted.

- [Evidence artifact 11969313879](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38729334501/artifacts/11969313879) confirms exact SHA, repository migration source, PG 17, `supabase_stop_exit_code=0`, no remaining project containers/volumes and cleanup verification.
- [Browser diagnostics artifact 11969373883](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38729334501/artifacts/11969373883) reports 2 passed in 2.7 minutes and fixture cleanup verified.
- Matching Web Unit [run 38729380832](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38729380832) succeeded on the same SHA: 372/373 tests passed, none failed, one skipped; Docker egress tests and TypeScript typecheck passed.

The tested tree includes W80's role-check migration but no `supabase/tests/w80_*.sql` file; W21 did **not** run the dedicated 49-assertion W80 privilege regression. Treat W80-specific pgTAP evidence as still missing. This result is isolated fake-provider evidence and does not establish deployed egress enforcement, real-provider guarantees, authoritative reconciliation, hosted schema parity, or universal Mission Authority. The verification repository and evidence are retained; no commit was pushed to Nexo. PR #39 remains OPEN/Draft/unmerged, Issue #23 OPEN, adapters empty/fail-closed, and release **NO-GO**.


## W80 invitation-helper privilege regression — current-source evidence — 2026-10-15

The canonical pgTAP file `supabase/tests/w80_invitation_helper_privileges.sql` was recovered from history (blob `6baa7b4915769e196366c3480227c66b99f8f051`), not reconstructed. It defines 49 assertions over overload counts, effective EXECUTE by anon/authenticated/service_role, exact ACL grantees, owner/security/search_path, wrapper delegation, private-schema USAGE, and the anonymous token-lookup call.

A prior isolated run, [38608523334](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38608523334), passed 49/49 for source `0c56de7…` with W80 migration blob `c90a0ad…`; its [artifact 11916637686](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38608523334/artifacts/11916637686) records PostgreSQL 17 and verified cleanup. It is not evidence for the current branch's different W80 migration.

The new exact current-source run is [38733275159](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38733275159) at `ec16dc5de69805cadccd1653984802768b22f3f5`; inspect [artifact 11970459254](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38733275159/artifacts/11970459254). It checked out test blob `6baa7b…` and migration blob `fef9822…`, replayed 87 checked-in SQL migrations plus one documented local-only historical auth-trigger compatibility fixture, observed PostgreSQL `170011` (17.0), and replayed later migrations successfully. The W80 pgTAP result was **49 planned / 49 reported / 10 failed / 39 passed**. Failed assertions: 5, 8, 11, 14, 27–30, 40 and 49. The artifact lists their names and records cleanup verified, zero containers and zero volumes.

The failure demonstrates a real contract discrepancy in the current branch: service_role retains direct EXECUTE on all four public invitation RPCs, the exact public ACLs include service_role, the public token lookup is not the narrow postgres-owned SECURITY DEFINER bridge expected by the reviewed contract, and anon receives `42501` when the invoker wrapper attempts to access `private`. The historical `c90a0ad…` W80 migration has the narrow bridge/revocations; the current branch's `fef9822…` does not. Keep these source revisions distinct in review.

The isolated workflow path `.github/workflows/zavqera-w80-isolated-pgtap.yml` is explicitly wired (manual `workflow_dispatch`, plus path-limited push on the verification branch), checks out the exact SHA, uses read-only contents permissions, initializes a brand-new local PG17 stack, runs the single W80 test at its dependency point, captures exact source/test/migration hashes plus the full 87-file manifest, verifies the runtime server version, applies later migrations, and checks cleanup in an always-run step. It uses neither hosted schema dumps/credentials nor provider/email/deployment effects. Its only supplemental schema setup is the disclosed, local-only historical auth-trigger fixture; no hosted object was read or changed. W80 run was push-triggered, not manually dispatched.

W21 [run 38732655783](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38732655783) passed on `cc42a33…`, but its workflow explicitly selects W30, W29, W36, W82, W44–W70 and does not run the dedicated W80 test. Do not treat it as a W80 pass. Flutter CI [38733275032](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38733275032) passed on `ec16dc5…`.

No W80 migration behavior was changed in this task. The minimal safe correction should be a separate forward-only migration after W82 (candidate W83), reviewed against all environment ledgers before implementation: recreate the qualified token-lookup helper and narrow definer wrapper with pinned `search_path`; enforce the reviewed exact EXECUTE matrix (authenticated mutations, anon/authenticated GET, no service_role/PUBLIC direct grants); retain no anon private-schema USAGE; and test the resulting state with the canonical W80 assertions plus a correction-specific test. Do not rewrite the historical W80 migration or hosted ledger. Preconditions include read-only confirmation of each deployed version/signature/owner/ACL and review of the production state; stop on any mismatch. No rollback is claimed. This is a separate code/schema change requiring review and explicit rollout authorization.

This SQL ACL result is one invitation-function boundary only. It neither proves nor disproves universal Mission Authority egress enforcement, production provider guarantees, receipt/reconciliation/recovery semantics, or hosted schema parity. PR #39 remains open/Draft/unmerged at its original SHA, Issue #23 remains open, the provider registry stays empty, and release remains **NO-GO**.

## W83 correction verification — invitation helper privilege boundary — 2026-10-15

The W80 failure is now traced and corrected in a **new local forward migration**, `supabase/migrations/20261015100000_w83_workspace_invitation_privilege_correction.sql`, source/test SHA `16b6c655f21c36b11757c827e36ff39494916b14`. No historical migration or the unchanged canonical W80 test was edited.

The prior failures map to two source defects. Assertions 5/8/11/14 and 27–30 showed that each `public` invitation RPC retained direct `service_role` EXECUTE, although checked-in W44/W80 never grant that role; the clean local Supabase bootstrap/replay exposes these ACL entries, while their exact hosted origin remains unverified. The authenticated app callers use the cookie-bound publishable client and the RPCs validate `auth.uid()`, so service_role access is unnecessary. W83 revokes only those four direct grants. Assertion 40 showed the public GET remained SECURITY INVOKER; assertion 49 then failed with `42501` because anon has no `private` schema USAGE. W83 restores only the reviewed public GET SECURITY DEFINER bridge with pinned `pg_catalog, public` path and retains the private token helper and anon schema boundary. The helper keeps its 64-character token validation and limited metadata behavior; qualified table columns avoid the previously documented `status` ambiguity.

The related W44 test was adjusted to state the reviewed exception precisely: three mutation wrappers remain SECURITY INVOKER; public GET alone is SECURITY DEFINER; private helper role grants and pinned paths remain checked. The unchanged W80 test still has 49 assertions.

Exact isolated evidence: [run 38734947527](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38734947527) at SHA `16b6c655f21c36b11757c827e36ff39494916b14`; [artifact 11973300579](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38734947527/artifacts/11973300579). The clean disposable PG17 stack replayed all **88** checked-in migrations through W83; server version was `170011`; W83 reapplication succeeded; W44 passed **17/17**; unchanged W80 passed **49/49**; replay after W83 exited 0; cleanup verified zero containers and volumes. No hosted database or live external service was touched.

Local Web Unit on the exact commit: `npm test` exit **0**, **372 passed, 0 failed, 1 skipped**; focused invitation test `node --test test/invitation-email.test.mjs` exit **0**, **7/7**; `git diff --check` exit **0**. The skip is Docker OS-level egress isolation. Workflow YAML parsing and `bash -n` on all five run blocks passed.

This is not a W21 exact-SHA result: W21's previous successful run was on another SHA and did not invoke the W80 test. PR #39 remains open/Draft/unmerged at its original SHA, Issue #23 remains open, provider adapters remain empty, and release remains **NO-GO**. The next safe step is read-only per-environment migration/function-state reconciliation, followed by separate review/authorization before any hosted rollout. W83 has only run in the disposable CI database.

## W83 paired PG17 verification and hosted-parity gate — 2026-10-15

The new exact-source isolated verification revision is `8510654bd6da55394f5a13f64cfcfb06b0ad62c8` on the temporary verification repository only. Dedicated W80 run [38737023310](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38737023310) passed on that SHA; artifact [11973343485](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38737023310/artifacts/11973343485) confirms PostgreSQL 17.0, 88 checked-in timestamp-ordered migrations plus the disclosed local-only auth-trigger compatibility fixture (89 ledger rows), replay exit 0, W44/W80 **17/17 and 49/49 both before and after** W83 reapplication, reapply exit 0, full remainder replay exit 0, and verified teardown. The two pre/post catalog snapshots match byte-for-byte. This is database privilege evidence for the eight invitation functions, not the W21 launch gate or hosted schema parity.

The run observed default function ACLs that give `service_role EXECUTE` on newly created `public` functions for owners `postgres` and `supabase_admin`. These ACLs do not currently grant EXECUTE on the eight reviewed invitation functions after W83. W83 does not alter defaults, and the canonical W80 test does not assert default ACL policy. The authorized database owner must classify this policy and compare it on each hosted environment before any future privileged function rollout. The run also confirms the sole public SECURITY DEFINER wrapper is token-gated GET; its existing private helper marks expired pending invitations as EXPIRED before returning limited metadata. Preserve this lifecycle write in the security review; W83 does not add it.

The operator-only read-only query is `supabase/tests/w83_invitation_catalog_reconciliation.sql`, with preconditions, expected-state matrix, stop rules and recovery limitations in `docs/ZAVQERA_W83_READ_ONLY_RECONCILIATION_2026-10-15.md`. It must only be run by an authorized owner through an independently validated read-only service alias. No hosted call or state inspection was made by this task. W66 service-role table controls, W67/W81 legacy RPC controls, W82 reservation identity, other schema/migration parity and universal production egress/provider/recovery guarantees remain separate unresolved gates. PR #39 stays OPEN/Draft/unmerged, Issue #23 OPEN, adapter registry empty/fail-closed, and release **NO-GO**.


## W21 exact-source test-coverage correction — 2026-10-15

The isolated W21 workflow now explicitly stages and executes canonical W80 and W81 pgTAP tests, and the workflow regression test requires W66/W67/W80/W81/W82 tests to remain wired. On exact temporary-verification SHA `77e4ca26157137dfcd3146a066f8503cd72c1c67`, the complete [W21 run 38740599618](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740599618) passed. [W21 evidence/cleanup](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740599618/artifacts/11975193299); [browser diagnostics](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740599618/artifacts/11975083311).

Verified on this SHA: W30 PG17 launch gate; W63–W81 Mission Authority regression group including canonical W80 (**49/49**) and W81 (**23/23**); W82 quota/reservation/workspace suite; four ledger concurrency proofs; W72 fake-provider integration; browser E2E (**2 passed, 2.3m**); disposable-resource cleanup (`stop exit 0`, no remaining containers/volumes, cleanup verified). Flutter CI also passed on the same SHA: [run 38740599747](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740599747). Web Unit/typecheck and the new workflow guard passed on predecessor SHA `f2adb2444193eb22e98c6902fa1c9df5a1a854f9`: [run 38740358556](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740358556), 372 passed, 0 failed, 1 Docker-required test skipped.

The first post-coverage run found that W30's old blanket denial for anonymous-executable SECURITY DEFINER functions contradicted the intentionally reviewed invitation GET bridge. W30 now excludes only the exact `public.get_workspace_invitation(text)` signature from the broad denial assertions and has a dedicated assertion for owner, pinned path, delegation, token validation, role grants and anon's lack of private-schema USAGE. The next run exposed a contaminated W81 test fixture; the authority-change scenario now restores the test Agent's read-only authority before the independent unclaimed-failure/UNKNOWN scenarios, and asserts exact `RESEARCH_JIT_CLAIM_REQUIRED`. The final exact-SHA W21 run passed after both fixes. See [handoff details](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/e32d2afb9f20214e4ac87ead7e670df0af656968/docs/ZAVQERA_CONTINUATION_HANDOFF_2026-10-15.md).

This evidence is from the temporary verification repository only. It is not hosted-schema parity and does not prove universal production egress enforcement or real-provider outcome guarantees. No commit was pushed to original Nexo. PR #39 remains OPEN/Draft/unmerged; Issue #23 remains OPEN; trusted provider registry remains empty and fail-closed; release remains **NO-GO**.


## Database privilege defaults checkpoint W84 — 2026-10-15

The isolated W83 catalog report uncovered a future-function privilege surface separate from direct ACLs on existing RPCs: PostgreSQL's built-in function default grants EXECUTE to PUBLIC, and scoped defaults in public also named anon, authenticated and service_role for functions created by postgres and supabase_admin.

A narrow candidate migration, 20261015110000_w84_postgres_function_default_acl_hardening.sql, now removes the PUBLIC global default and the named API-role defaults in the public schema for future functions created by postgres only. It does not alter existing function OIDs/ACLs and does not change supabase_admin defaults. The 21-assertion W84 pgTAP test passes on W21; dedicated run [38748554496](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748554496) replayed migrations through W84, passed W84 21/21, reapplied W84 successfully, passed 21/21 again, and verified cleanup. [Evidence artifact 11980312862](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748554496/artifacts/11980312862).

Full W21 pass on the code/test SHA 7f28798b35f23787446194da3ff1804ece62e716: [run 38746026089](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38746026089), [evidence 11980335837](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38746026089/artifacts/11980335837). Browser E2E passed (2 tests), isolated egress and fake-provider cases passed, and resource cleanup was verified. Web Unit and Flutter passed on follow-up guard SHA f012e5584511de40b954297eeb20f9b54cbeb5e6; the latest W21 rerun for that SHA was still at E2E on last inspection after 17 successful steps and is not counted as complete.

**Unresolved:** the supabase_admin default ACL baseline remains unchanged and must be reviewed by an authorized database/platform owner; do not attempt an unapproved privilege mutation. Hosted ledger/catalog reconciliation, universal production egress mediation, and production provider contract evidence remain separate release gates. All these changes are confined to the temporary verification repository. Original Nexo PR #39 remains OPEN/Draft/unmerged, Issue #23 remains OPEN, trusted provider adapters stay empty/fail-closed, and release remains NO-GO.

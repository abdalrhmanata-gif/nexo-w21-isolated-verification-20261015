# ZAVQERA — Continuation Handoff (2026-10-15)

**Purpose:** Authoritative transfer note for the next ChatGPT conversation. Read this first, then verify live GitHub state before any action. This supplements the older `ci/CI_HANDOFF.md`; that file is not the complete/current Mission Authority checkpoint.

## 1. Working rules — non-negotiable

- Do not merge any PR automatically. Keep PR #39 Draft/open/unmerged.
- Keep GitHub Issue #23 **OPEN**.
- Do not modify hosted Supabase Development or Main/Production; no hosted migration, schema mutation, or write test.
- Do not deploy, change Netlify configuration, alter secrets, add credentials, register/enable real providers, or change billing/DNS.
- Keep `TRUSTED_DISPATCH_ADAPTERS` empty and fail-closed.
- Do not spend paid-service/API credits or introduce external paid services. Prefer repository + local/disposable tests.
- Be concise in Arabic and report concrete verified actions, not promises. Make no claims beyond exact SHA and evidence.
- Launch decision remains **NO-GO** until universal outbound/effect enforcement and provider-contract evidence are proven.

## 2. Product and architecture context

ZAVQERA (repository name still Nexo) is an AI Mission Planner / Delegation Layer for personal and business workspaces from day one. A Mission is the unit of work and carries goal, authority/allowed and prohibited actions, budget, expiry, and evidence/outcome. Conceptual flow: User Goal → Intent → Identity → Authority → Policy → Authorization → Plan → Action → Execution → Evidence → Verification → Outcome.

Core domain/application contracts must remain provider-, backend-, storage-, queue/worker-, UI-framework-, and vendor-neutral. Do not couple the core to Flutter, Supabase, PostgreSQL, OpenAI, or a specific external provider. Existing direction includes approval engine, workspace membership roles (Owner/Admin/Member/Viewer), Agent Registry, Mission Templates, and separate personal/business workspaces.

Repository: https://github.com/abdalrhmanata-gif/Nexo  
Current working deployment reported by user (Netlify): https://zavqera-alternative-web-deployment--unique-kringle-3ce321.netlify.app/app  
Supabase Development was previously reported ACTIVE_HEALTHY (PostgreSQL 17, eu-west-1), but hosted Development schema parity with candidate migrations is **not verified**. Main/Production remains untouched.

## 3. Exact live checkpoint verified 2026-10-15

### PR #39 — current implementation/review focus

PR: https://github.com/abdalrhmanata-gif/Nexo/pull/39  
Title: `[Mission Authority] Compose worker/JIT boundary with fake transport`  
State: **OPEN, DRAFT, NOT MERGED**.  
Head branch: `codex/mission-action-runtime-seam-test-20261014`  
Base branch: `codex/w80-sql-review-base-20261014` at `5e2094fd27c7de60496729956af562651de93137`.

- Latest code/test checkpoint: `b184b91540c80be8a07b455bddaeca9080fad4f0`.
- Latest docs-only PR head: `7fc9f6a114fa4736d3fa1287707f16f6f6908873` (commit records direct fake-provider-IP isolation evidence and release boundary).
- Web Unit PASS on code/test SHA: https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38701026107
- Web CI PASS on code/test SHA: https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38701026169
- Flutter CI PASS on code/test SHA: https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38701026080
- Web Unit PASS on latest docs head: https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38701277323
- Web CI PASS on latest docs head: https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38701277242
- Flutter CI PASS on latest docs head: https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38701277300
- Latest confirmed **full W21 Local Launch Gate PASS**: https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38697454403 — on older code/test SHA `f146b11914b81f68ed025ac96d99befb0c2c8362`. **W21 on `b184b91` is not confirmed.** Never treat Web Unit/Web CI/Flutter CI as a substitute for W21.

The PR description at its current head contains additional technical evidence and links. Read it before continuing.

### Other PRs — leave unchanged

- PR #29: https://github.com/abdalrhmanata-gif/Nexo/pull/29 — OPEN/DRAFT/UNMERGED, `zavqera/ai-planner-integration` at `5e2094fd27c7de60496729956af562651de93137`, base `zavqera/alternative-web-deployment` at `46dc6029f084fb000ba511478d6e8aec3eb532b3`. AI Mission Planner; 281 changed files in prior recorded snapshot. Do not alter.
- PR #36: https://github.com/abdalrhmanata-gif/Nexo/pull/36 — OPEN/DRAFT/UNMERGED; isolated W80 PostgreSQL 17 verification workflow, head `81ef820d160bfef04edbbab181fc562de203f7fa`, base `main` at `f64a87addb25a7455c6acde446b81bb3427d43cc`. Do not alter.
- PR #37: https://github.com/abdalrhmanata-gif/Nexo/pull/37 — OPEN/DRAFT/UNMERGED; W80 invitation RPC grants/lookup boundary, head `2e7dcccf9679ecc78f2b522064a4b121135645c4`, base review branch at `5e2094fd27c7de60496729956af562651de93137`. Do not alter.
- Issue #23: https://github.com/abdalrhmanata-gif/Nexo/issues/23 — “Implement and prove the Mission Authority JIT enforcement boundary”; verified OPEN. Keep open. A project-status comment was added earlier (comment ID `6185088230`).

Re-query all statuses and SHAs at the start of the next conversation because GitHub may have changed since this snapshot.

## 4. Candidate implementation evidence in PR #39

- Shared authenticated worker HTTP gate/handler: `apps/web/lib/mission-authority/trusted-worker-http.mjs`; trusted dependencies are supplied statically by trusted caller.
- Actual protected internal Next.js worker POST route tested. Cases include authorization; malformed/extra input; execution ID validation; unregistered audience rejected before privileged-client creation; oversized/chunked request bodies without `Content-Length`; Research preflight/claim/completion failing closed without trusted DB credentials.
- Streaming body parser caps request body at 160 KB and cancels when exceeded.
- Route test runs under Docker `--network none`; selected direct Node networking, HTTP(S)/TLS/socket, DNS and child-process egress probes are denied in that test environment.
- Recursive Server Action inventory currently identifies `apps/web/app/app/missions/new/page.tsx` as authenticated workspace mission creation; verifies cookie-bound session, workspace owner binding/atomic RPC and no import path to dispatcher/registry.
- Outbound-effect inventory separately classifies AI planning/research, password-range lookup, invitation email and identity/session routes; do **not** claim all of these are Mission Action dispatch or already universally mediated.
- Pure reason-code inventory covers 158 exact source entries → 75 canonical outputs. It is not a production response layer; unknown/raw inputs fail closed; `ALLOW` is a decision, not a reason, and ambiguous approval semantics remain unchanged.
- `apps/web/lib/mission-authority/provider-adapter-registry.mjs` keeps `TRUSTED_DISPATCH_ADAPTERS = Object.freeze({})`; no live provider is registered.

### Test-only executor/gateway topology

The disposable prototype under `tool/mission-executor/` places the executor on an internal Docker network, the fake provider on a separate egress network, and a fixed-destination fake gateway on both. This is local/fake-provider evidence only, not a production-deployed executor or proof of universal production egress enforcement.

Its PR description records tests for:
- direct egress denial via static Node networking, ESM dynamic import, CommonJS `createRequire`, HTTP/HTTPS/TLS, TCP socket and fresh child-process attempts; direct connection attempts to the actual fake-provider container IP fail;
- approved fixed-gateway path, rejection of caller-supplied destinations, replay/payload binding and exact provider request counters;
- 256-bit per-run fake bearer token for dispatch and reconciliation (wrong/missing token rejected before parsing/forwarding);
- accepted-then-lost response, missing/malformed/mismatched receipts, provider 429/500, timeout/cancellation and separate fixed-destination reconciliation endpoint;
- reconciliation receipt-binding mismatch and disposable container/network cleanup.

Do not extend the evidence beyond tested cases. Native modules, arbitrary transitive dependencies and every runtime/process context are not universally covered.

## 5. Important source-of-truth documents

Read from the current PR #39 branch/head and verify their current URLs/content:
- Universal egress plan: https://github.com/abdalrhmanata-gif/Nexo/blob/7fc9f6a114fa4736d3fa1287707f16f6f6908873/docs/ZAVQERA_UNIVERSAL_EGRESS_BOUNDARY_PLAN_2026-10-15.md
- Mission Authority implementation audit (older checkpoint; compare it against current PR body and current plan before relying on its SHA/status): https://github.com/abdalrhmanata-gif/Nexo/blob/d45fc33c5210d666a0fedaf5020c9b9fd90c9143/docs/ZAVQERA_MISSION_AUTHORITY_IMPLEMENTATION_AUDIT_2026-10-14.md
- Decision interface/reason-code proposal: https://github.com/abdalrhmanata-gif/Nexo/blob/43edddf6050ac56ad9d1d8f4120f9d389a333c8a/docs/ZAVQERA_MISSION_AUTHORITY_DECISION_INTERFACE_v0.1.md
- Current PR #39 description: https://github.com/abdalrhmanata-gif/Nexo/pull/39
- W21 full evidence and artifacts: https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38697454403

## 6. What is still NOT established

- Universal production egress/effect mediation over all entrypoints, jobs, workers, SDK/native transports and runtime dependency paths.
- A production-isolated executor and enforced production egress gateway/network policy.
- Provider credential separation and secret scope in a deployed architecture.
- Real-provider idempotency guarantees, authentic receipt binding, authoritative reconciliation, and trustworthy proof of `NOT_SENT`.
- Full W21 passing on current code/test SHA `b184b91540c80be8a07b455bddaeca9080fad4f0`.
- Hosted Supabase Development schema parity with candidate migrations.

A fake reconciliation `NOT_FOUND` is not proof an external effect was never sent. An unknown external outcome remains `UNKNOWN`; do not auto-retry without provider-specific authoritative evidence.

## 7. Next work order for the next conversation

1. Read this file, fetch the current PR #39 body/head, Issue #23 state, branch heads and Actions runs. Do not assume this snapshot is still the live state.
2. Keep PR #39 Draft/open and keep the registry empty. Do not touch PR #29/#36/#37, hosted Supabase, Production, deployment, secrets or billing.
3. Try to obtain a full W21 result against the exact current code/test SHA (`b184b91540c80be8a07b455bddaeca9080fad4f0`) only if the workflow can be dispatched safely on the intended branch and permissions allow it. Do not make artificial code edits just to trigger a workflow. If W21 is not feasible, state the blocker rather than pretending it passed.
4. Inspect the existing `tool/mission-executor/` scripts and its newest W21 output; determine missing adversarial coverage (native/transitive loader/process contexts, DNS, socket variants) and expand only with reproducible disposable tests.
5. Expand fake-provider contract tests for all uncertain-send boundaries, cancellation races, duplicate/replay semantics and receipt binding. Preserve exact counters and cleanup guarantees.
6. Only after candidate tests are complete, plan—not deploy—the production executor/control-plane architecture, default-deny networking, fixed allowlisted gateway, narrow signed/strongly authenticated execution envelope, JIT claim, durable dispatch evidence, receipt validation and reconciliation.
7. Re-run Web Unit, Web CI, Flutter CI and W21 on one exact source/test SHA and link artifacts with that SHA. Validate hosted schema parity using read-only inspection or a separately approved safe procedure only; never mutate hosted projects.
8. Keep launch **NO-GO** until every required gate has evidence and review.

## 8. Paste this instruction into the next chat

“استأنف مشروع ZAVQERA من ملف الاستئناف هذا باعتباره نقطة البداية الحالية. تحقّق أولاً من الحالة الحية لـ PR #39 وIssue #23 ونتائج Actions على GitHub، ولا تعتمد على أرقام قديمة دون التحقق. تابع التنفيذ العملي بدقة وباختصار. ممنوع دمج أي PR أو تعديل Supabase Development/Main/Production أو النشر أو الأسرار أو إضافة مزود حقيقي. أبقِ سجل المزودات فارغاً وPR #39 Draft وIssue #23 مفتوحة. فرّق دائماً بين نجاح Web Unit/Web CI/Flutter CI وبين نجاح W21 الكامل؛ أحدث W21 مؤكد هنا على SHA أقدم من أحدث كود. أبقِ قرار الإطلاق NO-GO حتى إثبات حدود egress الشاملة وعقد المزود.” 


## 9. Verified continuation update — 2026-10-15

**Exact code/test SHA:** `1ff2eb66753575f6771c2acda9cfdfb6d9597c4b`.
### New adversarial coverage

Updated only `tool/mission-executor/isolated-executor-smoke.mjs` to add:
- a fresh ESM child process that attempts a TCP connection to the actual listening fake-provider IP on port 9090; the probe must fail with a recognized network-denial result;
- a Node `worker_threads` context making the same direct-provider-IP attempt; connection success, timeout without a classifiable denial, or unexpected exit fails the test.

The W21 isolated executor/fake-gateway step passed with both probes on this exact SHA. This is test-only Docker/fake-provider evidence; it is not proof of a deployed production egress boundary.

### Exact-SHA CI — PASS

- Web Unit: [run 38704593127](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38704593127) — SUCCESS.
- Web CI: [run 38704593180](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38704593180) — SUCCESS.
- Flutter CI: [run 38704593035](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38704593035) — SUCCESS.

### Full W21 — PASS on the same source/test SHA

[W21 Local Launch Gate run 38704584466](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38704584466) — SUCCESS on `1ff2eb66753575f6771c2acda9cfdfb6d9597c4b`.

Completed successfully: isolated executor/network topology including the ESM-child and worker-thread probes; disposable PostgreSQL 17/pgTAP; Mission Authority execution security; AI quota/workspace security; actual-ledger idempotency, budget, dispatch-claim and reconciliation-claim races; W72 persistent fake-provider integration; browser E2E; cleanup and cleanup verification; evidence uploads.

- W21 evidence: [artifact 11957672919](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38704584466/artifacts/11957672919).
- Browser diagnostics: [artifact 11957942588](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38704584466/artifacts/11957942588).

Two intermediate test-development commits failed W21 because of defects in the newly added probe (newline escaping and an unqualified `spawnSync` reference). Those defects were corrected; use only the final passing SHA and run above as evidence for this change.

### Disposition remains unchanged

- PR #39: OPEN / DRAFT / UNMERGED.
- Issue #23: OPEN.
- `TRUSTED_DISPATCH_ADAPTERS`: empty / fail-closed.
- No real provider or credential enabled; no hosted Supabase, Production, deployment, secrets, billing, or DNS changed.
- Universal production egress mediation, deployed executor/network policy, credential separation, real-provider idempotency/receipt authenticity/authoritative reconciliation, and hosted Development schema parity remain unproven.
- Launch remains **NO-GO**. A fake-provider `NOT_FOUND` is not proof of `NOT_SENT`; never automatically retry an unknown external outcome without authoritative provider-specific evidence.


## 10. Verified UDP and HTTP/2 egress coverage — 2026-10-15

**Exact code/test SHA:** `5dc99d6dfb3ba37ced235482fa7e6a461489b0ae`.

The disposable fake-provider topology now adds two distinct outbound-transport probes:
- **HTTP/2:** the executor attempts a direct HTTP/2 connection to the actual fake-provider container IPv4 address. Establishing the connection is a hard test failure; only a recognized network-denial outcome passes.
- **UDP:** the fake provider binds a UDP canary before its HTTP health endpoint becomes ready. The executor submits a datagram to the actual provider IP and the test orchestrator then reads the provider's private in-container metrics. The assertion requires `udpProbeCount === 0`; local `send()` callback success is not treated as proof of network delivery or denial.

Files changed for this checkpoint: `tool/mission-executor/fake-provider.mjs`, `tool/mission-executor/isolated-executor-smoke.mjs`, and `tool/mission-executor/egress-isolation-smoke.sh`.

### Exact-SHA validation — all PASS

- Web Unit: [run 38706603498](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38706603498) — SUCCESS.
- Web CI: [run 38706603331](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38706603331) — SUCCESS.
- Flutter CI: [run 38706597163](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38706597163) — SUCCESS.
- Full W21 Local Launch Gate: [run 38706597203](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38706597203) — SUCCESS on the same SHA.

W21 completed the HTTP/2 and UDP isolation probes; disposable PostgreSQL 17/pgTAP; Mission Authority security regressions; quota/workspace security; actual-ledger idempotency, budget, dispatch-claim and reconciliation-claim races; W72 fake-provider integration; browser E2E; disposable stack cleanup and cleanup verification; and evidence uploads.

- W21 evidence: [artifact 11958244046](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38706597203/artifacts/11958244046).
- Browser diagnostics: [artifact 11958393754](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38706597203/artifacts/11958393754).

These remain local/disposable fake-provider results. They do not establish production egress enforcement, native/transitive dependency behavior in every runtime, deployed credential separation, or any real-provider contract. The registry remains empty and launch remains **NO-GO**.


## 11. Full production-entrypoint graph guard — 2026-10-15

**Exact source/test SHA:** `c50b9db5610f483f63abdb1504465711c8e3b74e`.

Expanded `apps/web/test/mission-authority-worker-auth.test.mjs` so the Mission Action dispatch graph guard no longer treats API routes as its only roots. It now includes:
- all App Router `route.ts` handlers;
- nested and root App Router page/layout/template/default/loading/error/not-found/global-error and metadata entrypoints;
- middleware and instrumentation entrypoints;
- every module containing a Next.js `"use server"` directive;
- conventional background/worker/job/cron/scheduled/task/queue/platform-function locations, with a fail-closed assertion that any such new source location must be explicitly reviewed and inventoried.

The test asserts that root `app/page.tsx` and `app/layout.tsx` are actually included in the entrypoint set. For every discovered entrypoint it traverses statically declared local imports and permits reachability to the persistent Mission Action dispatch gateway / worker boundary / provider registry only from `app/api/internal/agent-executions/[executionId]/route.ts`.

This is an expanded static import-graph regression guard, not a full runtime trace or proof of all transitive package/native/runtime behavior.

### Exact-SHA CI — PASS

- Web Unit: [run 38708716964](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716964) — SUCCESS.
- Duplicate push Web Unit: [run 38708723370](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708723370) — SUCCESS.
- Web CI / typecheck / production build: [run 38708723357](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708723357) — SUCCESS.
- Flutter CI: [run 38708716868](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716868) — SUCCESS.
- Duplicate pull-request Flutter CI: [run 38708723245](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708723245) — SUCCESS.

### W21 on this source/test SHA — IN PROGRESS at documentation time

[W21 Local Launch Gate run 38708716869](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716869) is running on this exact SHA. Its executor/fake-gateway egress step, disposable PG17 preparation, and pgTAP plus Mission Authority/AI quota/ledger-race/fake-provider integration steps passed; browser E2E and subsequent disposable-stack cleanup/evidence steps have not yet been confirmed complete in this checkpoint. Do not infer a full W21 PASS until this run concludes.

Last completed full W21 PASS before this new root-entrypoint assertion was [run 38707978336](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38707978336) on source/test SHA `3e4f6a573e3be3df86b7fa5d6035b2a7eb989e92`, with evidence [artifact 11959556889](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38707978336/artifacts/11959556889) and browser diagnostics [artifact 11959343783](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38707978336/artifacts/11959343783).

Provider registry remains empty/fail-closed. PR #39 remains OPEN / DRAFT / UNMERGED; Issue #23 remains OPEN. No hosted Supabase, Production, deployment settings, secrets, billing, DNS, or real-provider credentials changed. Launch remains **NO-GO**.


## 12. W21 completion — production-entrypoint graph guard — 2026-10-15

**Exact code/test SHA:** `c50b9db5610f483f63abdb1504465711c8e3b74e`.

The root App Router addition was validated on this exact SHA:
- Web Unit: [run 38708716964](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716964) — SUCCESS.
- Web CI: [run 38708723357](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708723357) — SUCCESS.
- Flutter CI: [run 38708716868](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716868) — SUCCESS.
- Full W21 Local Launch Gate: [run 38708716869](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716869) — SUCCESS on the same SHA.

W21 completed the isolated egress topology; disposable PostgreSQL 17/pgTAP; Mission Authority security regressions; quota/workspace security; concurrent idempotency, atomic budget, dispatch-claim and reconciliation-claim races; W72 fake-provider PostgreSQL integration; browser E2E; disposable-stack cleanup and cleanup verification; and evidence uploads.

Artifacts:
- W21 evidence: [artifact 11959867882](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716869/artifacts/11959867882).
- Browser diagnostics: [artifact 11959932304](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38708716869/artifacts/11959932304).

Two intermediate commits in this entrypoint-graph workstream failed because of test-code regex/escaping defects; they were corrected before `c50b9db5610f483f63abdb1504465711c8e3b74e`. The PASS claims in this section apply only to `c50b9db5610f483f63abdb1504465711c8e3b74e`.

The new regression includes root `app/page.tsx` and `app/layout.tsx`, nested pages/layouts/metadata, route handlers, middleware, instrumentation and detected Server Actions, and fails if an unreviewed background/worker/job/cron/queue/function path appears. This remains static source-graph evidence, not an instrumented runtime trace.

**Disposition unchanged:** PR #39 OPEN / DRAFT / UNMERGED; Issue #23 OPEN; `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed; no real provider enabled; no hosted Supabase/Production/deployment/secrets changed; launch **NO-GO**.

## Static dependency-graph parser hardening — 2026-10-15

**Local code/test commit:** `9e71be9a90f572129411a585812860196d01e817` (the previous remote head remains `9d752a59f0683ea7149633138dc85bb33cf9a41b`).

Inspection found the Mission Action source-graph guard extracted import edges with regular expressions. That missed the valid TypeScript `import name = require("...")` form and could mistake import-like text in comments/strings for a dependency. Replaced that parser with TypeScript AST extraction for import/export declarations, import-equals, literal dynamic imports, and literal CommonJS `require`; added a regression covering all forms and comment/string decoys. The existing full-entrypoint reachability and outbound-capability checks remain unchanged.
Local validation on this code commit:
- Focused `node --test test/mission-authority-worker-auth.test.mjs` from `apps/web`: **27 passed, 0 failed**.
- `npm test` from `apps/web`: **368 passed, 0 failed, 1 skipped** (369 total).
- `git diff --check`: PASS.
- `TRUSTED_DISPATCH_ADAPTERS` remains an empty frozen object.

This makes static edge parsing more complete; it does not cover computed/runtime loading, arbitrary transitive/native behavior, or prove production-wide egress enforcement. Local Web Unit passed on this source, but exact-SHA GitHub CI/W21 evidence is pending. The change is committed locally and not published: prior pushes to this PR branch caused automatic Vercel Preview deployments, and this continuation prohibits deployments. PR #39 remains Draft/open/unmerged, Issue #23 open, hosted Supabase untouched, and release **NO-GO**.

## Exact-commit AST guard verification — 2026-10-15

**Code/test SHA:** `dad0734e1fbc76a31d40ac66b19dd7332963a78a`. This commit is local; remote PR #39 still points to `9d752a59f0683ea7149633138dc85bb33cf9a41b`.

Review found that no-substitution template literals in `import(`./module`)` and `require(`./module`)` were not recorded as statically known edges. Updated the AST parser to treat those as constant module specifiers and added coverage proving template literals with substitutions remain excluded from static edge resolution and are flagged as computed dynamic imports by the capability guard. Together with the prior tests, coverage now exercises import declarations/type imports, re-exports, TypeScript import-equals, quoted and constant-template dynamic imports/CommonJS loads, and comment/string decoys.

Exact-source local checks on `dad0734e1fbc76a31d40ac66b19dd7332963a78a`:
- From `apps/web`: `node --test test/mission-authority-worker-auth.test.mjs` — exit **0**, **27 passed, 0 failed**.
- From `apps/web`: `npm test` — exit **0**, **368 passed, 0 failed, 1 skipped** (369 total). The skipped test is OS-level egress isolation, which requires Docker.
- `git diff --check` — exit **0**.

W21 was not run on this SHA locally or remotely. Docker, Supabase CLI and `psql` are unavailable, so disposable PostgreSQL 17/pgTAP, database-backed concurrency/security races, Docker fake-provider integration and network-isolation components could not run. Node-only tests in Web Unit passed but are not a substitute for those W21 components.

No safe remote exact-commit path was found: `workflow_dispatch` is available in W21/Web Unit, but the remote branch does not contain this commit; using it would test the old remote SHA. Publishing this PR branch has previously triggered automatic Vercel Preview deployments, which this task forbids. No push or dispatch was made. Current PR #39 is still OPEN/DRAFT/UNMERGED at the recorded remote SHA; Issue #23 remains OPEN; provider registry remains empty; release **NO-GO**.

## Adversarial Mission Action AST guard audit — 2026-10-15

**Exact source/test commit:** `f5115fb11969859156f2b78e995befbb762538d5`. It adds coverage for `module._compile`, `module.createRequire`, WebAssembly `Module` and `Instance` construction, and the corresponding fail-closed loader classifications. The source/test commit is local only; nothing was pushed.

Changed `apps/web/test/mission-authority-worker-auth.test.mjs` only for the code/test commit. The graph resolver now reads the web TypeScript configuration, applies configured `paths` mappings plus the existing `@/` root convention, normalizes slash styles, follows source extensions and `index.*`, restricts traversal to the source root, and skips declaration files and known non-executable assets. It uses JS/JSX/TS/TSX grammars, ignores erased type-only imports, and rejects syntax errors before trusting AST results. Unresolved local executable imports now fail the graph test closed.

The all-production-entrypoint graph now scans each reachable source module for runtime loader/code-generation constructs and restricted runtime imports. Covered forms include static imports/re-exports, TS import-equals, literal dynamic imports and CommonJS loads, `module.require`, aliases/destructuring, computed global/module properties, `process.mainModule`, `createRequire`, computed import/require, `eval`, `Function`, `Reflect.get`/descriptors/construct, and WebAssembly compile/instantiate capabilities. Regression fixtures prove forbidden local reachability through re-exports and fail-closed unresolved aliases, and ensure comments, strings, metadata keys, `require.resolve`, and ordinary `Reflect.construct(Date, ...)` do not create false loader edges.

Local checks on the exact source/test content at `f5115fb11969859156f2b78e995befbb762538d5`:

- From `apps/web`: `node --test test/mission-authority-worker-auth.test.mjs` — exit **0**, **31 passed, 0 failed**.
- From `apps/web`: `npm test` — exit **0**, **372 passed, 0 failed, 1 skipped** (373 total). The skipped test requires OS-level Docker network isolation.
- From repository root: `git diff --check` — exit **0** before commit.
- Provider registry source still defines `TRUSTED_DISPATCH_ADAPTERS = Object.freeze({})`.

W21 was not run on this exact source/test commit. Rechecked local tools: `docker`, `supabase`, `psql`, and `pg_prove` are all `NOT_FOUND`; therefore disposable PostgreSQL 17 migration replay/pgTAP, database concurrency/security components, Docker fake-provider integration, W21 browser E2E and teardown verification remain unperformed for this SHA. No remote workflow was dispatched: the branch was not pushed, and any remote run would not verify this exact local source. Node Web Unit is not W21 evidence.

Remaining AST limitations: this is a source-level import/capability guard. It cannot prove behavior of arbitrary transitive package/native code, reflective patterns outside the enumerated AST forms, generated/evaluated code after opaque transformations, or runtime/process contexts not represented by the production-entrypoint inventory. The real W21 disposable runtime check is the next verification action once an isolated runner with the required tools can test this exact source without a deploy preview.

Live GitHub state was checked after the audit: PR #39 remains OPEN / Draft / unmerged with head `9d752a59f0683ea7149633138dc85bb33cf9a41b`; Issue #23 remains OPEN. No remote refs, hosted Supabase, deployment settings, provider credentials, or external effects changed. `TRUSTED_DISPATCH_ADAPTERS` remains empty and release remains **NO-GO**. The working branch is `codex/mission-action-runtime-seam-test-20261014`; documentation is committed locally and unpublished.

## Exact-SHA isolated W21 execution — 2026-10-15

**Verified source/test SHA:** `f5115fb11969859156f2b78e995befbb762538d5`. The W21 job checked out this full SHA. To run GitHub Actions without another push to Nexo, this exact existing commit was pushed only to the temporary public verification repository [`nexo-w21-isolated-verification-20261015`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015), then the existing W21 and Web Unit workflows were manually dispatched. No deployment integration, secrets, or provider credentials were configured there; the repository and evidence are retained.

- W21 — [run 38729334501](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38729334501) — SUCCESS on the exact SHA. It replayed **88 checked-in migrations** in order, from `20260921175955_w4_core_tables_and_indexes.sql` through `20261014130000_w82_ai_generation_reservation_identity.sql`, against disposable PostgreSQL 17. Logs show **41 pgTAP invocations / 594 assertion executions, all passing**. Executor/network isolation, Mission Authority and quota/workspace SQL regressions, the idempotency/budget/dispatch-claim/reconciliation-claim races, W72 fake-provider integration, browser E2E, cleanup, and cleanup verification all succeeded. Initial public ECR rate limits were retried successfully.
- Evidence: [artifact 11969313879](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38729334501/artifacts/11969313879). Inspected contents confirm the SHA, repository-migration source, PostgreSQL major 17, `supabase_stop_exit_code=0`, no remaining containers/volumes, and `cleanup_verified=true`.
- Browser diagnostics: [artifact 11969373883](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38729334501/artifacts/11969373883). Inspected log reports **2 passed (2.7m)** and cleanup VERIFIED, including removal of 2 users, 1 mission, 4 actions, 1 verification and 1 outcome fixtures.
- Web Unit — [run 38729380832](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38729380832) — SUCCESS on the same SHA. Docker `--network none` worker/egress tests and controlled-adapter tests passed; `npm test` reported **373 total, 372 passed, 0 failed, 1 skipped**; TypeScript typecheck passed.

**W80-specific limitation:** the exact `f5115fb` tree replays `20261013100000_w80_fail_closed_workspace_role_checks.sql`, but contains no `supabase/tests/w80_*.sql` file, and W21 did not invoke a dedicated 49-assertion W80 test. The W30 launch pgTAP (38 assertions) and other passing SQL regressions do not prove that later dedicated W80 privilege contract. Keep this gap open. Next, verify the reviewed W80 pgTAP commit in this same isolated repository only after confirming the test and runner wiring are present at the exact SHA.

Live original-repository state rechecked: PR #39 remains OPEN / Draft / unmerged at head `9d752a59f0683ea7149633138dc85bb33cf9a41b`; Issue #23 remains OPEN. The only remote write was to the temporary verification repository. Hosted Supabase, deployment settings and external providers were untouched; no real provider or invitation email was used. Adapter registry stays empty/fail-closed. W21 narrows local migration/runtime uncertainty but does not establish hosted schema parity, universal production egress enforcement, real-provider guarantees, or production readiness. Release remains **NO-GO**.


## W80 dedicated invitation privilege verification — 2026-10-15

### Canonical test and provenance

The recovered canonical test is `supabase/tests/w80_invitation_helper_privileges.sql` (Git blob `6baa7b4915769e196366c3480227c66b99f8f051`). Its history begins at `a671aeb` and includes subsequent ACL/effective-privilege corrections. The exact test blob appears in source commit `0c56de7c84d41c43f77d86e84dea67f2d88f6ec7`; the test was not reconstructed. It has `plan(49)`: two overload-count assertions, 24 effective `EXECUTE` checks, eight exact non-owner ACL checks, eight owner/security/search-path checks, four wrapper-delegation checks, two schema-usage checks, and one anonymous-wrapper invocation.

The test contract is: authenticated users can use create/accept/revoke; anonymous and authenticated callers can use the token-gated GET; service_role has no direct EXECUTE on these eight public/private helpers; only the reviewed GET path has the anon exception; no extra overloads or ACL grantees exist; helpers are postgres-owned SECURITY DEFINER functions with pinned `search_path`; the public GET is the narrow postgres-owned SECURITY DEFINER bridge; anon has no private-schema USAGE.

A historical isolated W80 run already succeeded against a different W80 migration source: [run 38608523334](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38608523334), [artifact 11916637686](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/38608523334/artifacts/11916637686). The artifact identifies source commit `0c56de7…`, the same test blob `6baa7b…`, and W80 migration blob `c90a0adfa8906b4de2a6b10eebaa5e28efdf69aa`; it records PostgreSQL 17, 49/49 passing, later migrations successful, and cleanup verified. This is historical evidence for that source, not the current local branch.

### Current-source isolated run — FAIL, exact evidence

The canonical test and dedicated workflow were added locally in code commit `b533460681957484a691a6d1698d1fb82522b1e4` (its earlier code commit `3dfa2c8` adds the two files; `fb1cac9` scopes the source-update trigger; `b533460` records exact failing counts). The verification branch was pushed only to the retained isolated repository `abdalrhmanata-gif/nexo-w21-isolated-verification-20261015`. No commit was pushed to Nexo. The exact W80 workflow source SHA is `ec16dc5de69805cadccd1653984802768b22f3f5`.

- W80 [run 38733275159](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38733275159) — **FAIL**, and [artifact 11970459254](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38733275159/artifacts/11970459254) was inspected.
- The run used test blob `6baa7b…` but the current branch's checked-in W80 migration blob `fef98228e9b54a7a5edd2b21c3db1b089822c70c`. Migration manifest SHA-256: `4774e6e1381f7ea1d41e0df193d05c4bf4a150550a3a7edea306fb6a0821d763`.
- The runner observed PostgreSQL `server_version_num=170011` (major 17). All **87 checked-in migration files** replayed through W80 with exit 0; the later migration replay also exited 0. The workflow adds the documented local-only historical auth-trigger compatibility fixture `20260921180005_e2e_historical_auth_compat.sql`; it is not a checked-in migration or a hosted schema snapshot.
- pgTAP planned and reported 49 assertions; **10 failed, 39 passed**. Failures were assertions 5, 8, 11, 14, 27–30, 40 and 49: service_role can execute all four public invitation RPCs; each exact public ACL contains service_role; the public token lookup is not the expected postgres-owned SECURITY DEFINER wrapper with pinned path; and anonymous invocation fails with `42501 permission denied for schema private`.
- The parser correction records `w80_assertions_failed=10` and all ten assertion labels in the artifact. Disposable cleanup succeeded: Supabase stop exit 0, no remaining project containers or volumes, `cleanup=VERIFIED`.
- The dedicated workflow is `.github/workflows/zavqera-w80-isolated-pgtap.yml`. It retains manual `workflow_dispatch` and has a path-limited push trigger on the isolated verification branch. It checks out `${{ github.sha }}`, has `contents: read`, initializes a fresh local PostgreSQL 17 stack, explicitly runs only the canonical W80 pgTAP file at the W80 dependency point, records migration/test hashes and a full migration manifest, checks the runtime PostgreSQL version, replays later migrations, and always records cleanup. It has no hosted DB URL/credentials, schema dump, provider, email delivery, or deployment step. The observed W80 run was push-triggered (not manually dispatched). Netlify deploy did not run; its branch filters exclude this `codex/*` branch.

The W21 workflow [run 38732655783](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38732655783) succeeded on `cc42a33b34eb5ba00438b1025bd72cba8a19ad6c`; Flutter CI [run 38733275032](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38733275032) succeeded on `ec16dc5…`. W21's source explicitly copies/runs W30, W29, W36, W82, W44–W70 selected tests and does **not** copy or invoke `w80_invitation_helper_privileges.sql`; its pass is not W80 evidence.

### Security discrepancy and next safe change

The current branch's W80 migration (`fef9822…`) does not contain the invitation-helper revocations and narrow GET wrapper present in the historically tested migration (`c90a0ad…`). The runtime results prove the current migration leaves service_role EXECUTE grants on public invitation RPCs and lets the anonymous wrapper reach into `private` as an invoker. No migration or application behavior was changed in this verification task, and no hosted database was touched.

Keep the correction separate and forward-only. After a fresh read-only review of every environment's migration ledger and function state, propose a new migration after the current W82 chain (candidate W83; generate its timestamp/name with the Supabase CLI only in the separately authorized change). It should recreate the qualified token lookup helper and narrow, pinned-search_path definer GET wrapper, revoke service_role/PUBLIC grants as required by the reviewed ACL matrix, preserve authenticated mutation calls and anon/authenticated GET calls, and include a regression that passes the 49 W80 contract assertions on the post-correction state. Stop on any signature, ownership, grant, ledger, or environment mismatch. Do not edit the historical W80 file retroactively or claim a rollback path. This correction and its migration approval are separate work; hosted application requires its own approval/preflight.

**Disposition at the `ec16dc5` verification checkpoint:** PR #39 was OPEN/Draft/unmerged at remote head `9d752a59f0683ea7149633138dc85bb33cf9a41b`; Issue #23 was OPEN. No Nexo ref, hosted Supabase, deployment setting, provider, email, DNS or billing state changed. The adapter registry remained empty/fail-closed. W80 privilege validation was **FAILING** on that source; the later W83 verification is recorded below. Release remains **NO-GO**.

## W80 privilege root cause and forward correction — 2026-10-15

**Implementation/test SHA:** `16b6c655f21c36b11757c827e36ff39494916b14` on `codex/w80-forward-correction-20261015`. This commit has only the W83 forward migration, the corrected W44 regression expectation, and the isolated W44/W80 verification workflow changes. It was pushed only to the retained temporary verification repository; no Nexo ref was pushed.

### Failure mapping and provenance

The prior exact-source run failed assertions 5, 8, 11, 14 and 27–30 because all four `public` invitation RPCs had a direct `service_role` EXECUTE ACL. Assertions 5/8/11/14 observed `has_function_privilege(...)=true`; assertions 27–30 observed the exact ACL grantees included `service_role` in addition to the reviewed authenticated/anon grantees. Checked-in W44/W80 SQL grants authenticated/anon as needed and never grants service_role. The clean local Supabase replay nevertheless supplied those direct ACL entries. Their exact origin in hosted environments is unverified; they are consistent with Supabase function/default ACL bootstrap behavior, not a checked-in grant migration. W83 revokes only the observed direct service_role EXECUTE grants from these four public functions. The app uses the cookie-bound publishable-key server client for invitation RPCs; helper bodies check `auth.uid()`, so no application path requires service_role for these calls.

Assertion 40 failed because `public.get_workspace_invitation(text)` was SECURITY INVOKER while anon is deliberately denied `private` schema USAGE. Assertion 49 therefore failed with SQLSTATE `42501` before token lookup. The migration history shows this boundary was previously addressed in a later W80 source revision by making the public GET a postgres-owned SECURITY DEFINER bridge with pinned `pg_catalog, public` path and keeping the private helper token-validating/metadata-limited. The current branch's historical W80 migration omitted that fix. W83 reproduces the reviewed narrow call path, retains the private helper role ACL and anon's lack of private-schema USAGE, and qualifies the helper's output-column references to avoid the known `status` ambiguity. Historical W80 source was not edited.

### Correction and exact disposable evidence

- New forward-only migration: `supabase/migrations/20261015100000_w83_workspace_invitation_privilege_correction.sql` (blob `286b1518c89c5882b9231d09e378009170c38191`). It changes no tables or RLS and makes no broad grants. `REVOKE EXECUTE` is idempotent; both functions use `CREATE OR REPLACE` with the reviewed signatures and pinned path.
- W44 test now expects the sole GET wrapper exception to SECURITY DEFINER; all three mutation wrappers remain SECURITY INVOKER. The original 49-assertion W80 test is unchanged (blob `6baa7b4915769e196366c3480227c66b99f8f051`).
- Dedicated workflow `.github/workflows/zavqera-w80-isolated-pgtap.yml` replays the clean repository chain through W83, checks PG17, reapplies W83 once through local `psql` to prove idempotence, then runs W44 and unchanged W80, replays any later migrations and verifies cleanup. It uses local disposable Supabase only, read-only repository token permissions, no hosted DB, provider, email, or deployment credentials.
- Exact run: [W80 run 38734947527](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38734947527), exact SHA `16b6c655f21c36b11757c827e36ff39494916b14`; [artifact 11973300579](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38734947527/artifacts/11973300579), digest `sha256:09f928ab53b0d0e49fcb8d1fbc8a5bbccd6dd7dbd47bfbf0702f1053da7fab7c`.
- Artifact confirms 88 checked-in migration files replayed through W83 (exit 0), PostgreSQL `server_version_num=170011`, W83 repeated execution exit 0, W44 **17/17 PASS**, unchanged W80 **49/49 PASS**, later migration replay exit 0, Supabase stop exit 0, zero remaining project containers/volumes, cleanup **VERIFIED**. Migration manifest SHA-256: `b4b097e6c26d8acef5c87277178a837a23f2654e8440a695d8f8ad82b663603b`.
- Local exact-commit app checks: `npm test` from `apps/web` exit 0, **372 passed / 0 failed / 1 skipped (373 total)**; focused `node --test test/invitation-email.test.mjs` exit 0, **7/7**; `git diff --check` exit 0. The skipped test is Docker OS-level egress isolation. Workflow YAML parsed, and `bash -n` passed on all five workflow run blocks.

This is disposable PostgreSQL evidence only. The prior W21 run on another SHA did not execute the dedicated W80 assertion file; W21 is not claimed on this SHA. No hosted Development/Production state was inspected or changed. PR #39 remains OPEN/Draft/unmerged at `9d752a59f0683ea7149633138dc85bb33cf9a41b`; Issue #23 remains OPEN; provider registry remains empty; release remains **NO-GO**.

Before any canonical rollout, perform read-only reconciliation of every environment's migration ledger and current function owner/signature/security/search_path/ACL state. Stop on any mismatch. W83 is not applied to a hosted database, and this isolated pass does not establish hosted parity, universal Mission Authority enforcement, production egress, provider guarantees, or production readiness.

## W83 paired verification and read-only reconciliation — 2026-10-15

**Exact test/workflow SHA:** `8510654bd6da55394f5a13f64cfcfb06b0ad62c8`, on local branch `codex/w80-forward-correction-20261015`; pushed only to the temporary `nexo-w21-isolated-verification-20261015` repository branch for isolated CI. The Nexo origin branch and PR #39 were not modified.

- W80 isolated workflow [run 38737023310](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38737023310) **SUCCESS**; [artifact 11973343485](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38737023310/artifacts/11973343485), digest `sha256:717a30b6926606d4ce92201bc9e8dde621091babe966cd6b214b644e60552636`.
- Disposable PostgreSQL 17 (`170011`); timestamp-ordered replay: 88 checked-in migration files plus one disclosed local-only auth-trigger compatibility fixture; 89 local ledger rows; replay through W83 exit 0 and remainder replay exit 0.
- Before W83 reapplication: W44 **17/17**, W80 **49/49**, both exit 0. Reapplied W83 exit 0. After reapplication: W44 **17/17**, W80 **49/49**, both exit 0. Pre/post catalog reports are byte-identical (SHA-256 `fd22a28c084fcdbcfbed354fa2e2d31630aa42db0e08d22fe7dd2d0d51081844`). Cleanup: Supabase stop exit 0, no project containers/volumes, `VERIFIED`.
- Read-only operator SQL: `supabase/tests/w83_invitation_catalog_reconciliation.sql`; procedure and expected-state matrix: `docs/ZAVQERA_W83_READ_ONLY_RECONCILIATION_2026-10-15.md`. It reads ledger versions/names, eight exact functions, owners/security/volatility/search_path, ACLs and effective EXECUTE, private-schema USAGE, role membership, and function default ACLs in a read-only transaction. It was executed only against the disposable CI stack, never hosted Development/Production.- The disposable catalog output separately shows `service_role EXECUTE` in default function ACLs for creators `postgres` and `supabase_admin` in `public`. W83 does not modify defaults, and W80 does not assert future-function defaults. This does not grant EXECUTE on the eight current functions after W83; hosted policy/provenance is unknown and needs owner/security review before future SECURITY DEFINER functions are added.
- Local `npm test` from `apps/web`: exit **0**, 372 passed, 0 failed, 1 skipped (373 total; Docker OS egress test skipped). YAML parse and `bash -n` for all five workflow blocks passed; `git diff --check` passed before documentation updates. Docker/Supabase CLI/psql/pg_prove remain unavailable locally, so no local PostgreSQL pass is claimed. This is the dedicated W80 workflow, not the complete W21 Local Launch Gate.
- Independent review: `public.get_workspace_invitation` is the sole public SECURITY DEFINER exception and calls a fully qualified private helper under pinned `pg_catalog, public`; it returns token-gated invitation metadata. The existing private helper marks a matching expired PENDING invitation as EXPIRED before returning; W83 does not introduce this behavior, so the endpoint is not strictly read-only with respect to application data. Mutation wrappers remain SECURITY INVOKER, and app callers use the cookie-bound server client. Keep expiry mutation and token disclosure in scope for the database security owner's review.
- W66 service-role table boundaries and W81/W82-specific security properties are not newly proven by this invitation suite. Hosted migration-ledger parity, W66/W67/W81/W82 environment state, default-ACL policy, production egress/provider guarantees and universal Mission Authority remain blockers. PR #39 remains OPEN/Draft/unmerged at `9d752a59f0683ea7149633138dc85bb33cf9a41`; Issue #23 remains OPEN; adapters empty/fail-closed; release **NO-GO**.


## Exact-SHA W21 launch gate after W80/W81 coverage correction — 2026-10-15

**Result: SUCCESS. Exact code/workflow/test SHA:** `77e4ca26157137dfcd3146a066f8503cd72c1c67` on temporary verification branch `codex/w80-forward-correction-20261015` in `abdalrhmanata-gif/nexo-w21-isolated-verification-20261015` only.

- Full W21 Local Launch Gate: [run 38740599618](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740599618) — SUCCESS.
- W21 evidence and cleanup artifact: [11975193299](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740599618/artifacts/11975193299).
- Browser diagnostics: [11975083311](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740599618/artifacts/11975083311).
- Flutter CI on the exact same SHA: [run 38740599747](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740599747) — SUCCESS.
- Web Unit and the workflow coverage regression passed on the immediate predecessor `f2adb2444193eb22e98c6902fa1c9df5a1a854f9`: [run 38740358556](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740358556). The suite reported 372 passed, 0 failed, 1 skipped (373 total); the skipped test requires Docker-backed egress isolation. TypeScript typecheck and the separate `--network none` adversarial egress integration step passed. The later `77e4ca` change is only the SQL W81 fixture; the exact-SHA W21 run re-executed the relevant SQL tests.

### What this run actually proved

- W30 PostgreSQL 17 launch-gate pgTAP — PASS after a narrow change to treat only exact signature `public.get_workspace_invitation(text)` as the reviewed SECURITY DEFINER exception. The test now separately checks postgres ownership, pinned `search_path=pg_catalog, public`, delegation to the private token helper, token validation, permitted role EXECUTE, no `service_role` EXECUTE, and no anon schema USAGE.
- Mission Authority SQL regression group — PASS, including W66, W67, W80 and W81. The unchanged W80 test returned PASS for its 49-assertion contract; the W81 test's 23-test plan completed successfully.
- The W81 false start was a test-fixture isolation bug, not a reason to weaken the policy: its authority-change scenario changed a shared Agent to require external effects/approval, then did not restore it before later unclaimed failure/UNKNOWN scenarios. The test now restores the initial read-only authority before starting the independent scenarios and checks the exact `RESEARCH_JIT_CLAIM_REQUIRED` error rather than treating any SQLSTATE 42501 as success.
- AI quota/plan/workspace tests, including W82 reservation identity, — PASS.
- Concurrent idempotency, atomic authority-budget, one-time dispatch-claim and one-time reconciliation-claim proofs — PASS.
- W72 persistent gateway integration with fake providers — PASS.
- Browser E2E: `2 passed (2.3m)`.
- Cleanup: `supabase_stop_exit_code=0`, `remaining_containers=none`, `remaining_volumes=none`, `cleanup_verified=true`.

### Workflow durability improvements

The temporary verification workflow now copies and explicitly invokes the canonical `supabase/tests/w80_invitation_helper_privileges.sql` and `supabase/tests/w81_read_only_research_jit_claim.sql`. The workflow guard test also requires W66/W67/W80/W81/W82 SQL tests to remain wired into the W21 workflow, preventing a future green W21 run from silently omitting those contracts.

Two prior W21 runs are retained as honest regression evidence: [run 38739418494](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38739418494) exposed the stale blanket W30 assumption; [run 38739915781](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38739915781) exposed the contaminated W81 fixture. Both were corrected before the successful exact-SHA run above.

### Boundaries and remaining blockers

This is the full W21 disposable PG17/fake-provider gate for the exact temporary verification SHA, not a proof of hosted Supabase Development/Production parity or universal production runtime isolation. The W81 fixture fix and W30 policy exception have only been pushed to this temporary verification repository, not to the original Nexo repository or the user's local Windows checkout.

Still outstanding: authorized owner-run read-only reconciliation for hosted migration ledgers, invitation function ACLs, role memberships and default function ACLs; independent W66/W67/W81/W82 hosted-state evidence; broad Mission Authority acceptance across every external effect; deployed universal egress enforcement; real-provider idempotency, receipt authenticity and authoritative reconciliation.

Original repository `abdalrhmanata-gif/Nexo` was not changed. PR #39 remains OPEN/Draft/unmerged at original head `9d752a59f0683ea7149633138dc85bb33cf9a41b`; Issue #23 remains OPEN. `TRUSTED_DISPATCH_ADAPTERS` remains empty/fail-closed. No hosted Supabase migration or external provider/email action was executed. Release remains **NO-GO**.


## W84 default-function ACL hardening — isolated verification checkpoint (2026-10-15)

**W84 candidate result: PASS in disposable PostgreSQL 17. Hosted rollout: NOT AUTHORIZED.**

- W83's read-only catalog report confirmed that PostgreSQL's built-in function default ACL baseline includes PUBLIC EXECUTE for both postgres and supabase_admin; schema-specific default ACL entries also granted anon, authenticated and service_role in public. W83 fixed the existing invitation function ACL boundary; it did not fix future-function defaults.
- Added migration 20261015110000_w84_postgres_function_default_acl_hardening.sql. It changes defaults for functions created by role postgres only: removes PUBLIC EXECUTE globally and removes the API-role defaults in the public schema. Existing function ACLs are not changed. It does not alter supabase_admin defaults.
- Added test w84_postgres_function_default_acl_hardening.sql, plan 21. The full W21 run executed the test successfully: Files=1, Tests=21; All tests successful; Result: PASS.
- Dedicated full migration/reapply verification: [W80 isolated PG17 run 38748554496](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748554496), tested workflow/source SHA aa1f65abba8c7edef0b5cd71edf0d65f44c72637. After full migration replay through W84, W84 passed 21/21; applying the W84 SQL file a second time returned success; W84 passed 21/21 again. The same run repeated unchanged W44 17/17, W46 8/8, and W80 49/49 before/after W83 idempotent reapplication and verified disposable-resource cleanup. [W80 evidence artifact 11980312862](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748554496/artifacts/11980312862).
- Full W21 Local Launch Gate passed on 7f28798b35f23787446194da3ff1804ece62e716: [run 38746026089](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38746026089), [evidence and cleanup 11980335837](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38746026089/artifacts/11980335837), [browser diagnostics 11979301234](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38746026089/artifacts/11979301234). It includes W83's explicit READ_ONLY_GUARD=CONFIRMED, W84 ledger entry, catalog inventory, W80/W81/W82 regressions, W72 fake-provider integration, four ledger races, E2E 2 passed, and cleanup with no remaining containers/volumes.
- Web Unit and Flutter CI also passed on follow-up workflow-guard SHA f012e5584511de40b954297eeb20f9b54cbeb5e6: [Web Unit 38748602160](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748602160), [Flutter CI 38748602109](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748602109). The follow-up W21 rerun has now completed SUCCESS on workflow-guard SHA f012e5584511de40b954297eeb20f9b54cbeb5e6: [W21 run 38748602250](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748602250), [evidence/cleanup artifact 11979329724](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748602250/artifacts/11979329724), and [browser diagnostics 11981135811](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748602250/artifacts/11981135811). All 27 reported workflow steps completed successfully, including the full browser E2E (2 passed in 2.6m), W83 read-only catalog report with READ_ONLY_GUARD=CONFIRMED, W84 migration and 21/21 pgTAP test, W80/W81/W82 regression coverage, ledger races, W72 fake-provider integration, and cleanup (no remaining containers or volumes). Web Unit [38748602160](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748602160) and Flutter CI [38748602109](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748602109) also passed on that same SHA.

### Residual ACL and release gates

The catalog report identifies supabase_admin as a separate superuser/function creator whose built-in and scoped default ACLs remain unchanged by W84. That surface requires explicit platform/database-owner review; do not try to change it by impersonating the role or broadening the migration. W84 is not a substitute for authorized, independently identified, read-only reconciliation in hosted Development/Production.

No hosted Supabase database was queried or modified. No migration was applied outside disposable CI. Original abdalrhmanata-gif/Nexo remains unchanged; PR #39 remains OPEN/Draft/unmerged at its previous head; Issue #23 remains OPEN; TRUSTED_DISPATCH_ADAPTERS remains empty/fail-closed. Universal deployed egress enforcement, hosted migration/ACL parity, and real-provider idempotency/receipt/reconciliation evidence remain outstanding. Release NO-GO.

## Superseding checkpoint — W85 `supabase_admin` default function ACL audit and W21 — 2026-10-15

Read the full evidence note: [`docs/ZAVQERA_SUPABASE_ADMIN_DEFAULT_ACL_AUDIT_2026-10-15.md`](ZAVQERA_SUPABASE_ADMIN_DEFAULT_ACL_AUDIT_2026-10-15.md).

Exact tested source/test SHA: `eb723c68ef73f54758ddb37d34ec713ba9e9d4d5`.

- Dedicated isolated PostgreSQL 17 workflow [38755183112](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183112) — **SUCCESS**; artifact [11982114807](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183112/artifacts/11982114807).
- W85 directly connected as the actual `supabase_admin` creator role and passed **12/12 pgTAP assertions** with no failures. The disposable role's built-in default includes `PUBLIC EXECUTE`, while its scoped `public` default ACL explicitly includes `anon`, `authenticated`, and `service_role`. The test-created function was rolled back and disposable cleanup verified.
- Full W21 [run 38755183191](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183191) — **SUCCESS on the same SHA**. PostgreSQL 17 migration replay, read-only W83 catalog report, Mission Authority/quota/workspace regressions, W85, four ledger concurrency proofs, W72 fake-provider integration, browser E2E (**2 passed in 2.7m**) and cleanup all passed. W21 evidence/cleanup artifact [11982878731](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183191/artifacts/11982878731); browser diagnostics [11982529470](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183191/artifacts/11982529470).
- Web Unit [38755183119](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183119) and Flutter CI [38755183147](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183147) also passed on that SHA.
- Harness corrections: the audit must connect directly as `supabase_admin` (attempting `SET ROLE` from `postgres` was rejected), and raw `psql -qAt` output is required so the shell TAP counter does not falsely fail on aligned table output.
- **No hosted default ACL was modified. No W86 migration was created.** The local image demonstrates a privilege surface only. PostgreSQL applies defaults based on the role that actually creates the function; Supabase documents `supabase_admin` as an internal role and hosted Dashboard SQL as executing under `postgres`. Do not infer hosted defaults from this disposable image or modify this internal role without an authorized, independent, read-only hosted catalog/ownership review.
- Trusted adapter registry remains empty/fail-closed. Original Nexo PR #39 remains OPEN / Draft / UNMERGED; Issue #23 remains OPEN. No hosted Supabase, deployment, secret, billing/DNS or original Nexo change was performed. Launch remains **NO-GO** because hosted parity and production-wide Mission Authority/provider guarantees remain unproven.

**Next safe operational step:** separately authorized, read-only hosted catalog reconciliation (project identity, migration ledger, function owner/security/search_path/ACL, default ACLs and role-membership paths), with stop-on-mismatch. This does not authorize hosted mutation.



## Read-only hosted catalog reconciliation — 2026-10-15

**Current disposition: PREPARED / HOSTED QUERY BLOCKED BY CONNECTION CONFIGURATION.**

- Runbook with individually runnable SELECT-only catalog queries: [ZAVQERA_HOSTED_READONLY_CATALOG_RECONCILIATION_2026-10-15.md](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w80-forward-correction-20261015/docs/ZAVQERA_HOSTED_READONLY_CATALOG_RECONCILIATION_2026-10-15.md).
- Current Supabase guidance documents a project-scoped MCP endpoint using `project_ref=<verified-development-project-ref>&read_only=true`, which runs queries as a read-only PostgreSQL user and disables mutation tools: [Supabase MCP configuration](https://supabase.com/docs/guides/ai-tools/mcp).
- Supabase also documents the experimental read-only Management API endpoint `POST /v1/projects/{ref}/database/query/read-only` running as `supabase_read_only_user`; it is not exposed as an action in the current connected Supabase tool surface: [Read-only query API](https://supabase.com/docs/reference/api/v1-read-only-query).
- The current connected tool surface does not expose the active server URL/read-only configuration or a way to reconfigure it in-session. Therefore, do **not** call generic `execute_sql` against hosted Development as a substitute. No hosted SQL was executed, and no hosted database, migration, ACL, secrets, deployment, billing or DNS was changed.
- Next operational step: activate an independently verifiable, project-scoped `read_only=true` connection for the exact Development project; run Query 1 in the runbook first; continue only after the read-only role identity/capability gate passes. Stop on any ambiguity, catalog/ledger mismatch, or permission denial.
- Existing W85/W21 artifacts remain disposable-local evidence only; hosted parity is still unverified. Do not create a forward migration from local defaults alone. Keep `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed, PR #39 OPEN/Draft/unmerged, Issue #23 OPEN and release **NO-GO**.


## Hosted read-only catalog query-pack validation — 2026-10-15

- Prepared the hosted catalog read-only runbook and eight-statement SELECT-only pack. The exact query pack is `supabase/tests/hosted_readonly_catalog_audit_queries.sql` (blob `c9c29ec8cff4ff1b5021628ea8b61be9d69b7393`); it was manually content-checked as exactly 8 SELECT statements, with no DDL/DML/role-change statement.
- Local disposable PostgreSQL 17 smoke result: [W80 run 38759025529 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38759025529), SHA `5556da5d852a5bece34fe172b18d0aae921bf1f5`, artifact [11985121817](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38759025529/artifacts/11985121817). Evidence confirms query-pack source SHA-256 `2462ff5f494b1acc6dd75e8290aa9eeb4fda4e4899a590e697d3c5a0be5790d2`, local smoke exit 0, W44 17/17, W46 8/8, W80 49/49 before/after W83, W84 21/21 twice, W85 12/12, and clean teardown. The W83 before/after catalog snapshots match exactly.
- Review found the workflow evidence file reported query-pack exit 0, but the artifact upload list omitted the raw `W85_READONLY_CATALOG_QUERY_PACK.txt`. Added the missing path in commit `1ada382e4c320d6b7f7815a30238fe99b1519305` (the sole diff from `5556da5...`). The re-run [38759493778](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38759493778) completed **SUCCESS** on SHA `1ada382e4c320d6b7f7815a30238fe99b1519305`; artifact [11984449025](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38759493778/artifacts/11984449025), digest `sha256:0ab752f5fe4876f3008786ea3e0e182d61749446283c68fce8133d94ee02223e`. I downloaded and inspected the ZIP; the raw 592-line query log is included, the local smoke exit is 0, and disposable cleanup is verified. All W44/W46/W80/W84/W85 counts remain passing.
- **Hosted reconciliation has not been executed.** Current connected tool surface does not provide a demonstrably project-scoped `read_only=true` endpoint/configuration, so generic `execute_sql` remains prohibited as a workaround. Use the configured Supabase MCP URL pattern `https://mcp.supabase.com/mcp?project_ref=<verified-development-ref>&read_only=true` only after the exact Development ref is independently verified and connection identity/permissions are checked; do not use a Production ref. Official docs: [Supabase MCP configuration](https://supabase.com/docs/guides/ai-tools/mcp) and [read-only query API](https://supabase.com/docs/reference/api/v1-read-only-query).
- No hosted DB, migration, ACL, secrets, deployment, billing or DNS writes were made. Keep PR #39 OPEN/Draft/unmerged; Issue #23 OPEN; `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed; launch **NO-GO**.


## Full W21 local launch gate — 2026-10-15

- Exact source/workflow SHA: `6c88b3683fc4f32bea611fafa6e226fc878af5e0`.
- [W21 Local Launch Gate run 38758953821 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38758953821).
- [W21 evidence artifact 11984937895](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38758953821/artifacts/11984937895), digest `sha256:ae51b190a638c4455918afebae6ac1b156b6a43a8b7b408b61beb4f730962daf`.
- [Browser diagnostics artifact 11985057666](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38758953821/artifacts/11985057666), digest `sha256:64c7b86f5d614eecbbef92a28713a57c4996dbec93cbfc3d90936551dd67e307`; inspected log reports **2 passed (2.6m)**.
- The run checked PostgreSQL 17, W83 read-only catalog report (`READ_ONLY_GUARD=CONFIRMED` in the disposable test session), Mission Authority security regressions, W85 as actual `supabase_admin`, quota/workspace checks, four actual-ledger concurrency races, fake-provider gateway integration, browser E2E, and teardown. Evidence records `supabase_stop_exit_code=0`, no remaining containers or volumes, and `cleanup_verified=true`.
- This W21 source predates only the W80 workflow artifact-list fix at `1ada382e4c320d6b7f7815a30238fe99b1519305`. The separate W80 run on SHA `1ada382e...` completed the query-pack smoke and retained its raw output artifact. These remain disposable-local results; neither run queried hosted Development.

**Still blocked:** hosted catalog reconciliation has not been run. Proceed only through an independently verified connection configured `project_ref=<verified-development-ref>&read_only=true`; do not substitute unrestricted `execute_sql`. Keep launch **NO-GO** until hosted ledger/catalog and production enforcement/provider gates are independently proven.


## Read-only audit gate review — 2026-10-15

Reviewed the prepared runbook against the actual isolated PG17 evidence. The local Supabase image reports `rolbypassrls=true` for `supabase_read_only_user`; the runbook was corrected in commit `0a8c19006e01b41180da7446ef57fd33c441654c` to record this role attribute rather than automatically disqualifying the documented role as write-capable. If the exact official read-only role is used, the audit remains restricted to the eight reviewed catalog/migration-ledger SELECT statements; no application-row queries. A project-scoped `read_only=true` connection must still be independently verified. Do not run generic `execute_sql` against hosted Development.

Latest runbook link: [ZAVQERA_HOSTED_READONLY_CATALOG_RECONCILIATION_2026-10-15.md](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w80-forward-correction-20261015/docs/ZAVQERA_HOSTED_READONLY_CATALOG_RECONCILIATION_2026-10-15.md). Hosted database state is still unverified; release **NO-GO**.


## Final checkpoint — hosted read-only audit still blocked — 2026-10-15

Live verification at this checkpoint:- W80 query-pack smoke and artifact retention: [run 38759493778 PASS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38759493778), SHA `1ada382e4c320d6b7f7815a30238fe99b1519305`, artifact [11984449025](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38759493778/artifacts/11984449025), digest `sha256:0ab752f5fe4876f3008786ea3e0e182d61749446283c68fce8133d94ee02223e`. Inspected ZIP includes raw 592-line SELECT query-pack output, evidence, before/after catalog reports and cleanup proof. Local PG17 smoke exit 0; W44 17/17; W46 8/8; W80 49/49 before/after W83; W84 21/21 twice; W85 12/12; clean teardown.
- Full local W21 gate: [run 38758953821 PASS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38758953821), exact SHA `6c88b3683fc4f32bea611fafa6e226fc878af5e0`; evidence artifact [11984937895](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38758953821/artifacts/11984937895), digest `sha256:ae51b190a638c4455918afebae6ac1b156b6a43a8b7b408b61beb4f730962daf`; browser diagnostic [11985057666](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38758953821/artifacts/11985057666), digest `sha256:64c7b86f5d614eecbbef92a28713a57c4996dbec93cbfc3d90936551dd67e307`, 2 passed (2.6m), cleanup verified.
- Current PR state rechecked via GitHub API: Nexo PR #39 remains OPEN / Draft / not merged at head `9d752a59f0683ea7149633138dc85bb33cf9a41b`; Issue #23 remains OPEN. The provider registry at that exact PR branch is `apps/web/lib/mission-authority/provider-adapter-registry.mjs`, blob `d27f4e955c3ed72fc8756d20aeffae4f232061a4`; it still contains `const TRUSTED_DISPATCH_ADAPTERS = Object.freeze({});`.
- Most recent runbook includes a corrected note that the disposable image's `supabase_read_only_user` reports `rolbypassrls=true`; keep catalog-only scope and do not query application rows. The local value is not evidence of the hosted role's attributes.

**Hard blocker remains:** the current ChatGPT tool surface cannot activate or independently verify a project-scoped Supabase MCP connection configured with `read_only=true`. The hosted catalog/ledger/ACL audit was not run. Do not use the generic SQL tool as a substitute; do not create W86, change hosted ACLs, or apply migrations. Release **NO-GO**.


## Direct read-only Management API path and guarded runner — 2026-10-15

The hosted audit still cannot be executed by this conversation's connected Supabase tool: its only Postgres action is generic **execute_sql**, and the connection is not independently proven project-scoped/read-only. Do not use it as a substitute.

### Safe alternative prepared

- Official beta endpoint: [Supabase read-only query API](https://supabase.com/docs/reference/api/v1-read-only-query) — POST /v1/projects/{ref}/database/query/read-only, executing as **supabase_read_only_user**; requires **database:read** plus fine-grained **database_read**.
- GET project metadata first to verify exactly **ZAVQERA Development**, region **eu-west-1**, and active/healthy status. Scoped token needs Project Settings (Read) plus Database (Read); no token is saved or uploaded. See [Supabase scoped PAT guidance](https://supabase.com/docs/guides/platform/personal-access-tokens).
- Guarded local runner: [tools/supabase_readonly_catalog_audit.py](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w80-forward-correction-20261015/tools/supabase_readonly_catalog_audit.py). Tests: [tests/test_supabase_readonly_catalog_audit.py](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w80-forward-correction-20261015/tests/test_supabase_readonly_catalog_audit.py).
- It pins the query pack SHA-256 **2462ff5f494b1acc6dd75e8290aa9eeb4fda4e4899a590e697d3c5a0be5790d2**, sends exactly eight SELECT-only queries to the explicit /database/query/read-only endpoint, gates on role identity before continuing, gates on ledger relation before Query 8, compares local vs hosted ledger versions/names, and saves results only to a gitignored local output folder. It never calls the generic write-capable /database/query route.
- Output status **CAPTURED_LEDGER_MATCH_REVIEW_REQUIRED** does not mean the security audit passed; every captured function owner/security/search_path/ACL must still be manually compared with the signed-off expected-state matrix. Ledger mismatch is blocking. It does not remediate.
- W80 runner self-tests (no hosted network) succeeded at SHA **d9ede7b795bfb6ac80ecfbafcc2a5145caca5946**: [run 38761978084 SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38761978084). Artifact [11987045224](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38761978084/artifacts/11987045224), digest **sha256:d00e9217878fb93f513c1e3fd5c8508f8b4683c81d1eb8891602d2d89303d80f**; logs confirm the pinned eight-query pack hash and no-network self-test. That SHA had the first five unit tests. Fail-closed mocked API tests and cross-platform line-ending normalization were then added. The latest exact code/test W80 validation [run 38762280083 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38762280083) completed on SHA **7c99e12cbb8b94ad90d302067ebac68274869d5d**. It passed 8/8 unit tests and the pinned eight-query self-test without network requests. The full disposable PostgreSQL 17 checks passed: W44 17/17, W46 8/8, W80 49/49 before/after W83, W84 21/21 twice, W85 12/12, query-pack smoke exit 0, and verified cleanup. Artifact [11986073172](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38762280083/artifacts/11986073172), digest **sha256:0e659ebdfa725ea7aa941d9a973db0145897e2be9bb83b7823b4411f953a9406**. This closes local runner testing/portability only; hosted Development remains unqueried.
- The public verification-repository workflow does not and must not receive the user's Management API token. Actual hosted execution happens locally only after the owner creates a project-scoped token with narrow read permissions. Do not put the token into ChatGPT, GitHub Actions secrets, the repository, or output artifacts.

Windows commands and cleanup instructions are documented in the [hosted read-only audit runbook](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w80-forward-correction-20261015/docs/ZAVQERA_HOSTED_READONLY_CATALOG_RECONCILIATION_2026-10-15.md). The official OpenAI guide says custom MCP server connections are for Business and Enterprise/Edu web workspaces and not mobile; the existing tool connection in this session cannot be reconfigured in-place. [OpenAI custom MCP availability](https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt).

**Remaining owner operation:** in the verified Development project, create a scoped Management API token with only Project Settings Read and Database Read, then run the committed script locally without sharing the token. If token scope, project identity, response format or role gate is ambiguous, stop. No hosted query has run in this conversation; no hosted database/ACL, Main/Production, deployment, secrets, billing, or DNS was changed. PR #39 remains OPEN/Draft/unmerged, Issue #23 OPEN, adapter registry empty/fail-closed, launch **NO-GO**.


## Read-only runner tests and remaining boundary — 2026-10-15

- Latest confirmed expanded mocked API unit suite: [W80 run 38762249277 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38762249277), exact SHA `11a61a91e86d705e3503aee61bdd8fb9f717d801`. Logs confirm 8/8 unit tests passed, including project-identity mismatch stopping before SQL, incorrect current_user stopping after Query 1, and simulated success using the explicit read-only endpoint for all eight queries. Pinned SQL pack hash `2462ff5f494b1acc6dd75e8290aa9eeb4fda4e4899a590e697d3c5a0be5790d2` passed; self-test made no network call.
- Commit `7c99e12cbb8b94ad90d302067ebac68274869d5d` normalizes CRLF to LF before checking the pinned query-pack hash, so PowerShell/Windows checkouts remain supported. [W80 run 38762280083 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38762280083) completed on that exact code/test SHA. Logs confirm 8/8 unit tests and the pinned-pack self-test passed without network requests. The disposable PostgreSQL 17 checks also passed: W44 17/17, W46 8/8, W80 49/49 before/after W83, W84 21/21 twice, W85 12/12, query-pack smoke exit 0, and verified teardown. Artifact [11986073172](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38762280083/artifacts/11986073172), digest `sha256:0e659ebdfa725ea7aa941d9a973db0145897e2be9bb83b7823b4411f953a9406`. This closes local runner portability/tests only; it does not query or prove hosted Development.
- All of these CI checks run without Supabase credentials against mocked runner responses and, separately, the disposable local PostgreSQL 17 migration stack. They do not query or prove hosted Development.

**Next required owner operation, no secret sharing:** create a project-scoped Supabase Management API token with only Project Settings Read and Database Read, then run the local runner using the verified Development project ref. Do not put the token in chat, GitHub, or a repository file. A result of CAPTURED_LEDGER_MATCH_REVIEW_REQUIRED still requires manual ACL/owner/search_path review; any ledger or role mismatch remains blocking.



## Hosted migration history reconciliation — 2026-10-15 (read-only evidence)

- Hosted read-only audit was executed 2026-10-15T17:18:09Z against project ref `mrwmmbytcymqgwvcoywd` (ZAVQERA Development, eu-west-1), with `supabase_read_only_user`, `transaction_read_only=true`, PostgreSQL `server_version_num=170006`. Eight fixed SELECT-only queries completed; the access token was not stored in the evidence ZIP.
- Evidence ZIP SHA-256: `dfc507963929356f9cbdeacc343a564dcd647addf17bd811d3543ff2a2237c36`.
- Current migration files = 89; hosted ledger rows = 74; exact version+name tuples = 46; same-name timestamp conflicts = 22; local names without a same-name host row = 21; host names without same-name local files = 6. Thus the original ledger comparison is blocking (43 source tuples missing exact host counterparts and 28 host tuples missing exact source counterparts).
- Independent catalog drift observed: W80 `private.can_edit_workspace(uuid,uuid)` configured search_path is `public, private` while current W80 expects `pg_catalog, public, private`; W82 catalog retains single-argument public/private `reserve_ai_generation(text)` instead of the three-argument identity-bound signature; W83 `public.get_workspace_invitation(text)` remains SECURITY INVOKER and the four public invitation wrappers have effective service_role EXECUTE. Public-schema function default ACLs grant EXECUTE to anon/authenticated/service_role for creators postgres and supabase_admin; W84 only changes postgres defaults and leaves supabase_admin owner-managed. W66 direct table ACL state was not covered by these eight queries and requires a separate read-only check.
- Detailed reconciliation findings and exact pair lists: [ZAVQERA_HOSTED_MIGRATION_HISTORY_RECONCILIATION_2026-10-15.md](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w80-forward-correction-20261015/docs/ZAVQERA_HOSTED_MIGRATION_HISTORY_RECONCILIATION_2026-10-15.md).
- Next work is an offline historical source/content-hash manifest and effect matrix, then disposable PostgreSQL 17 replay and W21/W80/W82/W83/W84 tests. Do not run hosted `db push`, `migration repair`, manually edit the ledger, or reapply migrations until deployed SQL sources are recovered and effects reconciled. No database changes were performed by this audit.
- Keep launch **NO-GO**, do not merge PR #39, keep Issue #23 open, keep `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed, and leave original Nexo plus hosted Development/Main untouched.


## Hosted candidate migration effect matrix — 2026-10-15

- Added [ZAVQERA_HOSTED_CANDIDATE_EFFECT_MATRIX_2026-10-15.md](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w80-forward-correction-20261015/docs/ZAVQERA_HOSTED_CANDIDATE_EFFECT_MATRIX_2026-10-15.md) on the temporary verification branch. It maps W66–W84 candidate SQL to captured catalog evidence and labels every unqueried effect as unknown.
- Current capture confirms signature/ACL drift for W67, W79, W80, W81, W82 and W83; expected W68–W70/W74 claim/budget function signatures are absent from the captured routine inventory. W71/W73/W75–W78 have partial results where function bodies or trigger/table catalogs were not queried. W66 relation ACL remains explicitly unverified.
- Next self-contained engineering step: design and locally test a second pinned SELECT-only catalog pack that covers relation/table ACLs, migration-effect columns/constraints, expected signature existence, private schema USAGE, trigger definitions and targeted function definitions. It must use only the explicit read-only API endpoint, verify project identity/effective role/read-only transaction, and fail closed. Do not broaden the existing tested eight-query pack silently.
- Historical SQL content recovery for 22 same-name timestamp conflicts and six host-only ledger names remains pending. Name-only mappings are not accepted as SQL equivalence proof.
- No hosted change. No original Nexo change. PR #39 remains open/Draft/unmerged; Issue #23 remains open; provider registry remains empty/fail-closed; launch remains NO-GO.


## Supplemental read-only effect audit pack — 2026-10-15

- Added pinned 10-query pack `supabase/tests/hosted_readonly_migration_effect_audit_queries.sql`, LF-normalized SHA-256 `7fbe8b65aeb75c446ca942277d0541de27de905e9b2172f304924e9029de6c62`.
- Added guarded stdlib-only runner `tools/supabase_readonly_migration_effect_audit.py` and tests `tests/test_supabase_readonly_migration_effect_audit.py`. Local tests/self-test run as part of [W80 isolated PostgreSQL 17 run 38779442480](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38779442480); the full workflow completed SUCCESS on exact workflow SHA `d7de58b829da1d11bce36b99c6cd07945f75b44c`, including the guarded runner/unit-test step, disposable migration replay through the documented W83 boundary, W44/W80 assertions, W83 reapply and verified cleanup. Evidence artifact [11995725697](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38779442480/artifacts/11995725697), digest `sha256:3720af9dc6abbade132bfcf9734bcca0867da6638f29bb6e7cf40f7d7aba1858`. Commits after that tested SHA up to latest head are docs-only.
- The runner requires the same exact project-scoped read-only PAT shape as the first audit, verifies project name/region before SQL, permits only the explicit read-only query endpoint, checks effective role/read-only transaction before query 2, and reports `CAPTURED_FOR_MANUAL_REVIEW` (not PASS). It stores no token; local output directory is ignored.
- Windows runbook: [ZAVQERA_HOSTED_MIGRATION_EFFECT_AUDIT_RUNBOOK_2026-10-15.md](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w80-forward-correction-20261015/docs/ZAVQERA_HOSTED_MIGRATION_EFFECT_AUDIT_RUNBOOK_2026-10-15.md).
- No supplemental hosted query was executed yet. Ask only for the resulting sanitized evidence ZIP after the owner/operator runs the new local procedure; never ask for the PAT.
- No hosted migration or source-repo mutation. PR #39 stays OPEN/Draft/unmerged; Issue #23 stays OPEN; dispatch adapters remain empty/fail-closed; launch is NO-GO.

## Latest hosted read-only effects audit — 2026-10-15 17:58 UTC

- User-provided evidence ZIP SHA-256: `5294a52f2695a938a291f3317c379aadf060d9f0aa6c07f7a029ff7865035384`; pinned query-pack SHA-256: `7fbe8b65aeb75c446ca942277d0541de27de905e9b2172f304924e9029de6c62`.
- Read-only audit completed all 10 queries for `ZAVQERA Development`, project ref `mrwmmbytcymqgwvcoywd`, region `eu-west-1`; token not saved and no app rows were queried. The observed role has `rolbypassrls=true`, so keep this evidence path strictly constrained to its fixed catalog-only pack.
- Manual comparison result: **NO-GO**. Missing budget/reservation tables; all 26 selected columns absent, 10/11 selected constraints missing, all 8 selected indexes missing; W75/W76 provider receipt trigger/function absent; 23/40 expected/forbidden routine signature mismatches; W80 function body/path is old; W82 legacy one-argument AI reservation functions remain and new identity-bound signature/columns are absent; W83 invitation wrapper security mode and service_role grants mismatch; W84 postgres public-schema defaults still grant EXECUTE to API roles.
- **Scope gaps:** this pack does not enumerate migration-ledger rows and does not query effective table ACLs on `public.agent_executions`; W66 direct table hardening remains unverified by this ZIP. Continue using the historical migration reconciliation report for ledger provenance.
- Detailed review: `docs/ZAVQERA_HOSTED_READONLY_EFFECT_AUDIT_REVIEW_2026-10-15.md`.
- No hosted migration, data write, deployment, secret change, or source-code change was performed. Keep `TRUSTED_DISPATCH_ADAPTERS = Object.freeze({})` empty/fail-closed and do not apply repair SQL until historical provenance is reconciled and a forward-only plan passes disposable PG17 verification.


## Next hosted audit extension — 2026-10-15

- The completed 10-query capture is documented in `docs/ZAVQERA_HOSTED_READONLY_EFFECT_AUDIT_REVIEW_2026-10-15.md` (evidence ZIP SHA-256 `5294a52f2695a938a291f3317c379aadf060d9f0aa6c07f7a029ff7865035384`). It confirms selected schema/function/default ACL gaps; release remains NO-GO.
- The pinned SELECT-only pack is extended to 12 queries: query 11 captures migration ledger `version,name` pairs only; query 12 inspects effective table privileges and expanded stored ACL for `public.agent_executions` (W66). Updated query-pack SHA-256: `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`.
- The observed read-only role reports `rolbypassrls=true`; keep the runner restricted to its fixed metadata queries. No application rows, token persistence, hosted writes, migrations, deployment, or secret changes.
- The updated 12-query pack is **not yet run against hosted Development**. First verify the new runner guards/unit tests and disposable PostgreSQL 17 syntax smoke. Then capture once, review ledger row/name mismatches against source; never repair the ledger by name alone.
- PR #39 remains OPEN/Draft/unmerged; Issue #23 remains OPEN; `TRUSTED_DISPATCH_ADAPTERS = Object.freeze({})` remains empty/fail-closed; release remains NO-GO.


## Offline evidence comparator — prepared on 2026-10-15

- Added tools/review_hosted_migration_ledger.py and test_review_hosted_migration_ledger.py to turn the next 12-query read-only capture into a row-by-row version/name comparison plus W66 table ACL review.
- This comparator is fully offline, verifies the pinned Development identity and query-pack digest, refuses old 10-query evidence/empty ledger/incomplete ACL matrix, and writes JSON/Markdown within the evidence folder.
- Use it only after the updated 12-query audit capture completes. It does not prove deployed SQL equality, make database changes, or lift release NO-GO.


## Verified dual-pack PostgreSQL 17 smoke and current gate status — 2026-10-15

- **Current verification commit:** 9039d887550b8de8d7eebb61932116679a7294fc.
- **W80 isolated PostgreSQL 17:** PASS — [run 38786902560](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38786902560); evidence artifact 11997538732, digest SHA-256: 3847bca8e7eb28acd3fa0d54d6166b86b366ab6d1ae862a7b0449bcf17a67fc0.
- Fresh disposable PostgreSQL replay used the 89 checked-in migration files plus the documented local-only historical compatibility fixture. Replay through W83 and remaining migrations succeeded; cleanup verified no project containers/volumes remain.
- W80: 49/49 pgTAP assertions passed before and after idempotent reapply. W44: 17/17 before/after. W46: 8/8 before/after. W84: 21/21 after chain and after reapply. W85 supabase_admin ACL audit: 12/12.
- Both read-only catalog packs passed local disposable PG17 smoke. Legacy pack SHA-256 2462ff5f494b1acc6dd75e8290aa9eeb4fda4e4899a590e697d3c5a0be5790d2; updated 12-query migration-effect pack SHA-256 a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284; both local smoke exit codes 0.
- Offline reviewer tests: 7/7 PASS. Supplemental audit runner tests: 10/10 PASS; runner self-test reports 12 queries/no network requests. Flutter CI: [run 38786902611](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38786902611) PASS.
- W21 Local Launch Gate: [run 38785230311](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38785230311) PASS on 17247b0ffce11576990f3858bee1950a8afe80fd. Commits after that W21 run only update offline review tooling/docs and the W80 workflow; no product migrations, web app, executor, or trusted adapter code changed.
- **Not yet done:** the updated 12-query pack has NOT been run against hosted Development. The earlier 10-query hosted capture still defines the current observed mismatches. Hosted catalog/ledger parity and release remain NO-GO.

## Hosted-only migration source search — 2026-10-15

A read-only inventory covered all 23 current branch refs in the original abdalrhmanata-gif/Nexo repository (including duplicate commit heads). None of the six hosted-only migration names below appears as a file in any current branch-tip tree. GitHub path-history lookups for the exact named paths also returned no commits. This confirms the deployed source is not recoverable from those current branch heads; it does not prove the files never existed in any external artifact, local checkout or deleted ref.

- 20261007105825_expose_anonymous_ai_guard_rpc
- 20261005053351_w35_plan_ai_allowances_5_50_300
- 20261008150359_w44_workspace_invitations_and_activity
- 20261008161103_w46_invitation_activity_bindings
- 20260921180227_w4_harden_profile_trigger_search_path
- 20260924171437_w6_authoritative_mission_mutation_and_concurrency

Do not reconstruct their SQL from names or neighboring versions. Historical provenance is still a blocker.


## Fresh 12-query Development capture — 2026-10-15 18:45 UTC

- User uploaded ZIP `zavqera-readonly-effect-audit-12q.zip`; SHA-256 `fff6f88aca42c73dc691ead099e969f3cfc911fea5504ce1291b6e04ae0320f6`. Capture timestamp `2026-10-15T18:45:25.121761+00:00`; pinned pack SHA `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`; all 12 queries complete; token not saved; no application rows queried. Role is `supabase_read_only_user`, transaction read-only, with `rolbypassrls=true`.
- Ledger/source comparison: 89 source files; 74 hosted rows; 46 exact `version,name` tuples; 22 same-name/different-version candidates; 43 source tuples absent from hosted exact tuples; 28 hosted tuples absent from source exact tuples; 21 source names absent by exact name; six hosted-only names absent from current source.
- **Critical W66 finding:** effective and stored ACLs on `public.agent_executions` still grant `service_role` all eight queried privileges, including SELECT/INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER/MAINTAIN. The checked-in W66 migration intends REVOKE ALL; this confirms its hosted effect is not present. Four direct write privileges are effective (INSERT/UPDATE/DELETE/TRUNCATE).
- Continued schema drift: two mission authority budget tables absent; all 26 selected expected columns absent; ten of 11 selected constraints absent (the remaining state constraint is an outdated definition); all eight selected indexes absent; W75/W76 receipt trigger absent; 23/40 tested function-signature expectations differ; W80/W82/W83/W84 function/ACL mismatches remain.
- Full review: `docs/ZAVQERA_HOSTED_12_QUERY_AUDIT_REVIEW_2026-10-15.md`. The previous report's statement that the updated pack was awaiting its first hosted capture is superseded by this capture.
- **Disposition stays NO-GO.** No hosted migration, ledger edit, deployment, secret change, or source product-code mutation occurred. Keep PR #39 OPEN/Draft/unmerged, Issue #23 OPEN and `TRUSTED_DISPATCH_ADAPTERS = Object.freeze({})` empty.


## 13. Current checkpoint — W86 inherited-role guard and 13-query capture (2026-10-16)

**Current decision: HOSTED RELEASE NO-GO. No hosted change authorized.**

### W86 candidate verification

- W86 review: [isolated PR #1](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/1) — OPEN / DRAFT / UNMERGED.
- Current W86 branch head: `b2f5e412204d74b1f6f5b39039b1326b945d5cb1`; the migration/workflow code itself was last fully tested on `687189c05773318e6ca9e4475eda7cf96b185d3d`. Seven commits after that tested SHA are docs-only.
- Full local PostgreSQL 17.11 W80/W86: [run 38857452731](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38857452731) — SUCCESS; artifact [12027962020](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38857452731/artifacts/12027962020), digest `503add2e33ae0fff000c02b8c2953b716be0cd3b48a0cd9246116607da21b352`.
- Deliberately seeded direct table/column ACL drift was repaired; W66 passed 11/11 and W86 20/20 after repair and after reapply.
- Deliberately seeded inheritable parent-role table UPDATE and column SELECT caused W86 to stop **before any ACL mutation** with the expected exception. The read-only provenance probe returned `W86_ACL_PROVENANCE_INHERITED_ACL_PASS`; the temporary role fixture was cleaned; W86 then applied successfully and W66/W86 tests passed again.
- W84 21/21 before/after reapply, W85 12/12, W44 17/17, W46 8/8, W80 49/49, full local migration replay and disposable cleanup all passed. Flutter CI passed on the same tested SHA.
- This is disposable/local evidence only, not proof that Development matches the candidate.

### 13-query read-only Development capture — still required

- Audit/review branch: `codex/migration-ledger-provenance-20261015`; latest docs update commit: `9250bb24ec172f5c4a83ac721b5d3abb578a65e1`.
- Audit PR: [isolated PR #2](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2) — OPEN / DRAFT / UNMERGED.
- Query 13 is pinned to SHA-256 `700939087d9708fc3d6a72ebe10064b4c0db7f5d26b08556c7e641e1aa09a919`; base queries 1–12 remain SHA-256 `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`.
- A secure Windows PowerShell wrapper is checked in: `tools/run_zavqera_readonly_effect_audit.ps1`. The current authoritative run steps are the final section of `docs/ZAVQERA_HOSTED_MIGRATION_EFFECT_AUDIT_RUNBOOK_2026-10-15.md`; it supersedes earlier 12-query instructions.
- Current workflow/runner local validation: [W80 run 38858755502](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38858755502) — SUCCESS on `c6fae906f9f57efe11ec7f010afb48b66ac850dc`; Flutter CI [run 38858755489](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38858755489) — SUCCESS on the same SHA. The later branch head only adds documentation.
- **The supplied hosted ZIP is still the old 12-query capture.** No fresh 13-query Development capture has been received. Do not treat the disposable query-13 smoke or simulated inherited-role fixture as hosted evidence.

### Required next action

On the user's Windows machine, from the root of the isolated audit repository (not the original `Nexo` repository):

```powershell
git fetch origin codex/migration-ledger-provenance-20261015
git switch codex/migration-ledger-provenance-20261015
git pull --ff-only origin codex/migration-ledger-provenance-20261015

powershell -NoProfile -ExecutionPolicy Bypass -File .\\tools\\run_zavqera_readonly_effect_audit.ps1
```

The wrapper runs the self-test before asking for the scoped Development-only PAT via a hidden prompt. Never paste or upload the token. Upload only the newly generated evidence ZIP containing `query_13.json`. If local tests/self-test fail, stop. If query 13 reports any inherited ACLs, W86 must not be applied as-is; require owner-reviewed least-privilege remediation.

### Live guardrails rechecked 2026-10-16

- Original repo PR #39: OPEN / DRAFT / UNMERGED, head `9d752a59f0683ea7149633138dc85bb33cf9a41b`.
- Original repo Issue #23: OPEN.
- Isolated W86 PR #1: OPEN / DRAFT / UNMERGED.
- Isolated audit PR #2: OPEN / DRAFT / UNMERGED.
- `TRUSTED_DISPATCH_ADAPTERS = Object.freeze({})` remains empty/fail-closed.
- No hosted database write, migration, ledger repair, deployment, secret, billing, or DNS change occurred.
- Historical SQL provenance remains unresolved: 22 same-name timestamp conflicts and six hosted-only migration names remain blockers.
- Release remains **NO-GO**.


## 14. W86 SET ROLE-only guard verified — 2026-10-16

This section supersedes earlier W86 notes that covered only automatic INHERIT paths.

- Current W86 branch head: `bafd61297bcb2836e9962cfa1b45a2f37bc1d1ac`; W86 migration/workflow code was tested on `a5f899ffff202eb0eda7954cec9ad12d82d252dc`. Subsequent W86 branch commits were documentation-only.
- W80 local PostgreSQL 17.11: [run 38865144782](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38865144782) — SUCCESS. Evidence artifact [12031370300](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38865144782/artifacts/12031370300), digest `8bccecd95878f0fa56309b01f0118d7f19fdc9eccbbdb5180ed5947f9775bc98`.
- The disposable fixture grants a parent role to `service_role WITH INHERIT FALSE, SET TRUE`, then gives that parent table UPDATE and column SELECT. Query 13 proves `all_edges_inherit=false` and `all_edges_set_role=true`; W86 refuses before any ACL mutation with the expected fail-closed error. After fixture cleanup, W86 reapplies successfully and W66 11/11 plus W86 20/20 pass.
- Full migration replay, W84 21/21 before/after reapply, W85 12/12, W44 17/17, W46 8/8, W80 49/49, local read-only query smoke and cleanup all pass. Flutter CI [run 38865152105](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38865152105) also passed.
- Query 13 now tracks both `INHERIT` and `SET ROLE` paths. Pinned query digest is `700939087d9708fc3d6a72ebe10064b4c0db7f5d26b08556c7e641e1aa09a919`; base query pack digest remains `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`.
- Fresh hosted Development 13-query evidence is still outstanding. The supplied ZIP is the old 12-query capture. Do not infer hosted role-membership state from the disposable fixture or local smoke.

**Next and only required external step:** run the secure wrapper from the isolated audit checkout root on Windows, using the hidden prompt for the scoped Development-only PAT, then upload only the resulting ZIP containing `query_13.json`. Never share the token. Any parent-role ACL reachable via INHERIT or SET ROLE blocks W86 as-is. Historical SQL provenance (22 timestamp conflicts and six hosted-only migration names) remains unresolved. No hosted write; release **NO-GO**.


## 15. SET ROLE provenance test suite and 13-query smoke — PASS (2026-10-16)

- W80 local PostgreSQL 17.11: [run 38866102409](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38866102409) — **SUCCESS** on exact code/test SHA `9503a117890edd6597cf234c23f011f48ead9a56`.
- Artifact [12030744508](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38866102409/artifacts/12030744508), ZIP SHA-256 `df13702d2a28e09e3d0208919e70501ce666c07388385a1847f76cb5d8cef67f`.
- Flutter CI: [run 38866102406](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38866102406) — **SUCCESS** on the same SHA.
- Runner tests: catalog 8/8; migration-effect/PowerShell wrapper 12/12; offline migration reviewer 11/11. Self-test: `queries=13`, base hash `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`, query 13 hash `700939087d9708fc3d6a72ebe10064b4c0db7f5d26b08556c7e641e1aa09a919`, no network requests.
- Disposable PostgreSQL 17.11 full migration replay exit code 0; W44 17/17, W46 8/8, W80 49/49 before/after W83 reapply; W84 21/21 before/after reapply; W85 12/12; query 13 local smoke passed; cleanup `VERIFIED`.
- This validates the updated query pack and offline review only against disposable/local evidence. It is **not** a hosted Development capture and does not clear the W86 gate.

The only external dependency remains: run the secure PowerShell wrapper locally with the scoped Development-only token and upload the resulting fresh ZIP containing `query_13.json`. Do not share the token. Historical SQL provenance (22 timestamp conflicts and six hosted-only names) remains unresolved; no hosted write; release remains **NO-GO**.

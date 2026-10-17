# ZAVQERA — START HERE for next conversation (2026-10-16)

**Use this file as the entrypoint, not as a replacement for the full handoff.** Read the linked comprehensive handoff and current PR descriptions before making changes. It preserves the current exact checkpoint and the required next action so that another conversation does not repeat or undo work.

## 1. Current mission and architecture

ZAVQERA (repository name still Nexo) is an AI Mission Planner / Delegation Layer for both personal and business workspaces from day one. A Mission is the unit of work; it carries the goal, authority, permitted/prohibited actions, budget, expiry, and evidence/outcome. The architecture intent is:

`User Goal → Intent → Identity → Authority → Policy → Authorization → Plan → Action → Execution → Evidence → Verification → Outcome`

Keep the core domain/application provider-, backend-, storage-, queue/worker-, UI-framework-, and vendor-neutral. Never treat client checks, static Dart policy, signed passports, or invocation envelopes alone as server enforcement.

## 2. Read these authoritative records first

1. **Full continuation handoff** (large document containing the project history, architecture/constraints, earlier adversarial tests, W86 work, audit pack, exact hashes, and next-step instructions):  
   https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/migration-ledger-provenance-20261015/docs/ZAVQERA_CONTINUATION_HANDOFF_2026-10-15.md

2. **Audit PR #2** — pinned source-provenance and 13-query read-only capture/reviewer:  
   https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2

3. **Isolated W86 PR #1** — forward-only ACL correction candidate with inherited ACL guards:  
   https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/1  
   Supporting candidate notes:  
   https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/codex/w86-agent-executions-acl-correction-20261015/docs/ZAVQERA_W86_AGENT_EXECUTIONS_ACL_CORRECTION_2026-10-15.md

4. **Original repository status — do not modify/merge**:  
   PR #39: https://github.com/abdalrhmanata-gif/Nexo/pull/39  
   Issue #23: https://github.com/abdalrhmanata-gif/Nexo/issues/23

## 3. Verified live checkpoint as of 2026-10-16

- Isolated verification repository: `abdalrhmanata-gif/nexo-w21-isolated-verification-20261015`.
- Audit branch: `codex/migration-ledger-provenance-20261015`; PR #2 is OPEN / DRAFT / UNMERGED. Its latest previously verified docs-only commit was `c668ad9ae26e246d31e4420c9f1f6371b8deb3cb` before this START-HERE record was added. The code/test workflow revision validated immediately before that was `438dc482863468798bfe1a108fcb1d9b7e836ac2`.
- W80/PostgreSQL 17.11 exact source/test run: [38878829978](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38878829978) — SUCCESS. Evidence artifact [12036577429](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38878829978/artifacts/12036577429), SHA-256 `bdc92bfda664dfaca535f475c4666ca042ffed52622dd1754d40a946324817bc`.
- Flutter CI: [38878829957](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38878829957) — SUCCESS on the same code/test SHA.
- The verified audit tooling reports catalog runner 8/8, migration-effect runner/PowerShell wrapper 13/13, offline ledger/ACL reviewer 13/13. The self-test pins a 13-query flow and both query hashes with no network requests. The disposable PostgreSQL 17.11 migration replay, W44 17/17, W46 8/8, W80 49/49 before/after W83 reapply, W84 21/21 before/after reapply, W85 12/12, query-13 local smoke, and disposable cleanup passed. These are isolated/local results, not hosted Development evidence.
- W86 candidate code/test was separately verified against PostgreSQL 17.11, including the SET ROLE-only inherited-ACL negative control: [run 38865144782](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38865144782). The fixture uses an edge with `INHERIT FALSE, SET TRUE`, confirms the read-only provenance query sees parent-role table UPDATE/column SELECT, and W86 fails closed before mutation. After fixture cleanup, W86 reapplies and W66 11/11 + W86 20/20 pass. This proves the guard on disposable PostgreSQL, not on hosted Development.
- Original PR #39 is OPEN / DRAFT / UNMERGED; original Issue #23 is OPEN. PR #1 and PR #2 in the isolated repo are also OPEN / DRAFT / UNMERGED at the last verified state. Re-check live status before future actions.

## 4. Immediate next step — requires the user's local Windows environment

The 2026-10-15 evidence ZIP uploaded earlier is SHA-256 `fff6f88aca42c73dc691ead099e969f3cfc911fea5504ce1291b6e04ae0320f6` and contains only **12** queries. It does **not** include the newly required query 13, so it cannot clear the W86 inherited-role preflight.

On the user's Windows machine, from the root of an up-to-date checkout of the **isolated repository** on branch `codex/migration-ledger-provenance-20261015`, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\run_zavqera_readonly_effect_audit.ps1
```

Use the script's hidden prompt for the scoped, Development-only read-only token. Do **not** paste the token into chat, commit it, or include it in the ZIP. The wrapper runs local self-tests, executes the pinned SELECT-only capture, launches the offline reviewer after clearing the token, and packages evidence. Upload **only the generated evidence ZIP** containing `query_13.json` to the next conversation; do not upload the token or unrelated database data.

Pinned query hashes for the capture to use:
- Base 12-query pack SHA-256: `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`.
- Query 13 inherited-ACL provenance SQL SHA-256: `f9f56944ddd04dd135329ff930cf5259e215eb89f30784b75e03a93f221ff38e`.

After the ZIP is provided, inspect its project identity, query 13, role path and stored/effective ACL results, source manifest and reviewer disposition. If any parent-role table/column ACL is reachable through automatic INHERIT or SET ROLE, **do not apply W86 as-is**. Also block W86 if query 13 shows a reachable membership path from service_role to authenticated via INHERIT or SET ROLE, even when authenticated currently has no ACL entry: W86 itself grants SELECT to authenticated after preflight, which could create a new access path. Require independent database-owner review of membership/ACL provenance. Even if neither path appears, the capture does not authorize hosted changes.

## 5. Why release is still NO-GO

The previous 12-query read-only hosted Development capture (PostgreSQL 17.6; capture time `2026-10-15T18:45:25.121761+00:00`) showed `service_role` with effective SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER, and MAINTAIN on `public.agent_executions`. W66 source expects direct table privileges revoked; this is a critical mismatch. A forward-only correction W86 has been created and hardened to fail closed on inherited grants, but it has **not** been applied to hosted Development.

Historical migration provenance is still unresolved:
- 89 checked-in migration files vs 74 hosted ledger rows.
- 46 exact version+name tuples; 22 same-name timestamp conflicts.
- 43 source tuples absent from the exact hosted ledger; 28 hosted tuples absent from current source tuples.
- Six hosted-only migration names have no current-source file.
- The bounded exact-path recovery check searched 28 historical names over 23 visible original-repository branch refs (644 checks, zero commits found). This does not rule out deleted/private refs, local Git objects/reflogs, or external deployment/release archives. Do not infer historical SQL from filenames or current equivalents.

Other outstanding differences from the prior 12-query capture include absent authority-budget tables and selected columns/constraints/indexes, old reservation-state constraint, missing execution success guard, forbidden legacy Research completion/reservation RPCs and EXECUTE grants, SECURITY DEFINER/search-path differences, and `supabase_admin` default function ACLs. The large handoff contains the detailed matrix.

## 6. Non-negotiable guardrails

- Do not apply W86 or any migration to hosted Supabase Development or Main/Production; no ad-hoc SQL, `supabase db push`, migration repair, or manual ledger edits.
- No writes to any hosted DB, no deployment, no secrets, provider registration, billing, or DNS actions.
- Keep `TRUSTED_DISPATCH_ADAPTERS = Object.freeze({})` empty/fail-closed.
- Do not merge or close original PR #39; keep it OPEN/DRAFT/UNMERGED. Keep original Issue #23 OPEN.
- Do not modify the original repository in this verification task. Work in the temporary isolated verification repository only.
- No Codex credits or paid external services. Never ask for, receive, or echo a token in chat.
- A green isolated CI run is not proof of hosted schema parity, production enforcement, or real-provider semantics. An unknown external outcome remains `UNKNOWN`; do not blindly retry.
- Release remains **NO-GO** until hosted schema/effect parity, historical source provenance, Mission Authority enforcement, and provider-specific idempotency/receipt/reconciliation proof are reviewed.

## 7. Paste this message into the next ChatGPT conversation

> استأنف ZAVQERA من ملف البداية هذا أولًا: `docs/ZAVQERA_NEXT_CHAT_START_HERE_2026-10-16.md` ثم اقرأ ملف الاستئناف الكامل المرتبط فيه. تحقّق من الحالة الحية للـPRs وActions قبل أي تعديل. الخطوة العملية التالية هي مراجعة ZIP جديد لالتقاط القراءة فقط ذي 13 استعلامًا؛ الـZIP القديم يحوي 12 فقط ولا يكفي. يجب تشغيل `tools/run_zavqera_readonly_effect_audit.ps1` محليًا على Windows من المستودع المعزول `codex/migration-ledger-provenance-20261015` باستخدام المطالبة المخفية للتوكن، ثم رفع ZIP الناتج فقط — لا ترسل التوكن في الدردشة. حلّل query_13 وقرّر إن كانت صلاحيات الأدوار الموروثة عبر INHERIT أو SET ROLE تمنع تطبيق W86. ممنوع أي كتابة على Supabase المستضاف أو دمج PR أو تغيير PR #39/Issue #23؛ أبقِ TRUSTED_DISPATCH_ADAPTERS فارغًا وقرار الإطلاق NO-GO. لا تعِد العمل المنجز، ولا تدّع نجاحًا مستضافًا اعتمادًا على اختبارات PostgreSQL المحلية.


## 8. Additional W86 guard verified after the original checkpoint

Static review identified a future-grant edge case: W86 grants SELECT to authenticated after preflight. The candidate and offline reviewer now block any service_role → authenticated membership path reachable through INHERIT or SET ROLE, even if authenticated has no current table/column ACL row.

- W86 code/test/workflow tested on `a94d104f71a4a6ba57233b92ba797b96aa7f3120`; W80 PostgreSQL 17.11 [run 38889778593](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38889778593) SUCCESS.
- Evidence artifact [12041540640](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38889778593/artifacts/12041540640), ZIP SHA-256 `2601c4c5a01a9120bd646875b42da8c2395cf241b3e130a202012e21b9923ee6`. The guard exited 3 as expected before mutation; no-mutation marker passed; after cleanup, W66 11/11 and W86 21/21 passed; cleanup verified.
- Offline reviewer/test update on audit branch `35342455b968bc72f964ce28df15049e364e0bad`: [W80 run 38889843683](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38889843683) SUCCESS; job log confirms 14 reviewer tests passed, including `test_authenticated_parent_path_blocks_future_select_grant`.
- These remain isolated/local checks. No hosted migration or write is authorized; historical SQL provenance remains unresolved; PR #1/#2 stay draft/open/unmerged; PR #39 and Issue #23 stay open; provider registry empty; release NO-GO.


## 9. Current continuation addendum — 2026-10-16

This update supersedes earlier “latest SHA/test count” statements in older sections; retain the preceding text as history, not current status.

- Latest code/test verification before handoff-document refresh: `1cd269094a41cdd5bb1cbea3e8aa411ebd160658`.
- W80 / disposable PostgreSQL 17 [run 38934043664 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38934043664), Flutter CI [run 38934043547 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38934043547).
- Pre-database tests: catalog 8/8, effect runner/wrapper 23/23, offline reviewer 29/29. Both pinned self-tests passed without network requests. PostgreSQL replay through W83 and later migrations passed; W44 17/17, W46 8/8, W80 49/49 before and after W83 reapply; W84 21/21 before and after reapply; W85 12/12; three read-only query-pack smoke tests and cleanup passed. Artifact [12060416195](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38934043664/artifacts/12060416195), SHA-256 `b0162b26fd9bc4757e962f4f43253623f33f6d1ff62bd4bf03af0c280d91f94c`.
- The ACL evidence collector/reviewer enforce query12/query13 relation identity, RLS, and effective-`service_role` privilege equality; membership ancestry must be connected and cumulative flags coherent. Identical projected rows are allowed when ancestry branches converge; this is not write authorization.
- PR #2 is OPEN/DRAFT/UNMERGED and changes audit tooling/tests/docs plus the SELECT-only query 13, not executable migrations or app files. PR #1 remains OPEN/DRAFT/UNMERGED; its isolated W86 candidate negative controls passed at W80 [38901754218](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38901754218), artifact [12046597051](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38901754218/artifacts/12046597051), SHA-256 `d499b6a733d5e3d8aa8ea9cd981f196f4ccdb5a2f589d6d131bae299e8caabae`. Owner authority by either INHERIT or SET ROLE is refused before ACL mutation.

**Non-bypassable blocker:** the hosted Development ZIP still has 12 queries and no `query_13.json`. Once the local Windows machine is available, use the secure wrapper from the isolated repository and upload only the generated 13-query ZIP. Do not paste the token into chat, use the unrestricted SQL endpoint, or infer hosted role paths from local PostgreSQL. After capture, manually reconcile source migration provenance and require independent database-owner review and separate explicit authorization.

No hosted Supabase writes were performed. `hosted_write_authorized=false`; `TRUSTED_DISPATCH_ADAPTERS` remains empty/fail-closed; PR #1/#2 remain open/draft/unmerged; original PR #39 and Issue #23 remain open; release stays **NO-GO**. The updated portable checkpoint is `ZAVQERA_EXECUTION_CHECKPOINT_2026-10-16.md` in the current ChatGPT conversation.

## 10. Current checkpoint — hosted 13-query capture reviewed and remediation gated (2026-10-17)

This section supersedes prior statements in this handoff that say the current hosted evidence has only 12 queries. A new guarded Windows capture was uploaded and reviewed offline.

### Capture identity and W86 result

- Uploaded archive: 20261017T151516202599Z.zip
- ZIP SHA-256: 9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d
- Capture time UTC: 2026-10-17T15:15:16.204988+00:00
- Target: ZAVQERA Development, project ref mrwmmbytcymqgwvcoywd, region eu-west-1, PostgreSQL server_version_num=170006 (PostgreSQL 17.6).
- Base query-pack SHA-256: a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284
- Query 13 SHA-256: 806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b
- Offline reviewer source HEAD: fbbcb080904acd88aad83a082803f627859026e2; migration-manifest SHA-256: 0d05ab7285edc975084ddbc595d1af7d2dd0752cc27e94d8fe0549170419be38.
- Read-only role gate passed; metadata reports token_saved=false. The audit role has rolbypassrls=true, so do not reuse this credential for application-row reads.
- Query 13 reports no service_role parent-role table/column ACLs, no path to the table owner, and no path from service_role to authenticated. W86's specific parent/owner-path preflight gate reports NO_PARENT_ROLE_ACL_OBSERVED. This is one cleared gate, not authorization to apply W86.

### Confirmed hosted Development drift — release still NO-GO

- service_role retains direct effective SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER and MAINTAIN on public.agent_executions; RLS is enabled but not forced.
- Missing relations: public.mission_authority_budgets and public.mission_authority_budget_reservations.
- All 26 queried expected columns are absent; 10 of 11 expected constraints and all 8 expected indexes are absent; agent_execution_success_receipt_guard trigger is absent.
- Query 6 has only 17/40 routine expectations matching (23 mismatches): 19 expected signatures absent and four legacy signatures expected absent remain present. Old reserve_ai_generation(text) SECURITY DEFINER routines and legacy read-only research completion overloads require independent body, dependency and ACL review; signature drift alone is not proof of exploitability.
- Query 10 reports eight explicit default EXECUTE ACL rows for public routines across postgres and supabase_admin.
- Historical ledger provenance: 89 source migrations, 74 hosted ledger rows, 46 exact version/name tuples, 22 same-name/different-version conflicts, six hosted-only names, and 43 source tuples absent from the hosted ledger. The 22 version-conflict source tuples are included in the 43; these groups must not be added as disjoint counts. Ledger metadata does not prove deployed SQL-byte equality.

### New persistent documents in this audit PR

- Full offline capture review: docs/ZAVQERA_HOSTED_13_QUERY_CAPTURE_REVIEW_2026-10-17.md
- Controlled remediation/acceptance plan: docs/ZAVQERA_HOSTED_REMEDIATION_GATES_2026-10-17.md
- PR #2 is still OPEN/DRAFT/UNMERGED; current branch is codex/migration-ledger-provenance-20261015. The exact tested source/test SHA for the ignored-migration-file provenance correction was a9fa8d484015f17fdb454e5dff6838547fe63c30:
  - W80 isolated PostgreSQL 17: run 39026148527 SUCCESS; artifact 12098333981; ZIP digest sha256:16066fd85754408f2aff997952706445b34195f3669128d95e97eb4c88b2be81.
  - Flutter CI on that tested SHA: run 39026148532 SUCCESS.
  - Test counts: catalog 8/8, 13-query capture runner 27/27, ledger reviewer 36/36. 13-query local self-test passed without network requests; migration replay, required pgTAP flow and disposable cleanup passed.
- Later handoff/report documentation commits do not change tested runner/reviewer source. Exact current-head Flutter CI also passed (run 39026246970). PR #1 remains OPEN/DRAFT/UNMERGED.

### Required disposition and next move

Keep hosted_write_authorized=false. Do not apply W86 or any migration to hosted Development or Main/Production. Do not edit the hosted ledger to make tuples match. The next step is independent database-owner review plus authoritative recovery of historic SQL source for the 22 timestamp/version conflicts and six hosted-only names. Then finalize a dependency-aware, forward-only remediation plan with verified backup/restore, isolated PG17 testing, exact pre/post catalog assertions, and separate written authorization naming the target project and change set. If historical source remains unknown, release remains NO-GO; do not infer it from current functions or filenames.

No hosted database was modified during the capture review or planning. TRUSTED_DISPATCH_ADAPTERS stays empty/fail-closed.

## 11. Current checkpoint — expanded historical migration recovery search (2026-10-17)

New report committed on the same audit branch:
- `docs/ZAVQERA_HISTORICAL_MIGRATION_SOURCE_RECOVERY_SCAN_2026-10-17.md`
- Commit: `4ce56b22f08e768a8ddba7c92a482b9559dcf4ce`

This pass went beyond exact hosted filename lookups:
- Recursively scanned all 23 visible `abdalrhmanata-gif/Nexo` branch-head trees. All scans completed with `truncated=false`.
- Compared the suffix/name independently of the timestamp. The 22 conflict names exist in current-source branches only with the checked-in/source-side versions; no hosted timestamp version path appeared in any visible branch-head tree.
- None of the six hosted-only names appeared in those branch-head trees.
- Queried commit history for all 22 current-source paths on `zavqera/ai-planner-integration`: 21 paths return one commit; W50 returns two commits for the same current source path.
- The earliest bulk-integration commit for W4 table privilege hardening, W7, W8, W9, W9.1 and W10 is `772f011624c199adc021a61d039a4cf13e9a3740` (“merge: stage ZAVQERA integration without historical artifact”); these files are marked added. Its parent `fcac980c9909c1a083007ed120d4742584fbcb4e` has no `supabase/migrations` files.
- Bounded Actions search: 2,000 run records (pages 1–20 of 10,590 records, spanning 2026-10-17T04:41:56Z to 2026-10-12T10:37:25Z). Sampled W21 artifacts are only 326–328 byte evidence and 661–743 byte browser-diagnostics archives; three sampled W25 runs have no artifacts. No historic SQL source archive was identified in these checks.

**Result: no authoritative historical SQL recovered.** This is a bounded public-branch-head/Actions inventory, not proof that no external/private/local archive exists. The 22 timestamp conflicts and six hosted-only names remain **UNKNOWN** until owner-controlled authoritative source/deployment provenance is produced.

Keep `hosted_write_authorized=false`, do not edit the hosted migration ledger, and do not apply W86 or any migration to hosted Development/Main. PR #1 and PR #2 remain OPEN/DRAFT/UNMERGED; release remains **NO-GO**.

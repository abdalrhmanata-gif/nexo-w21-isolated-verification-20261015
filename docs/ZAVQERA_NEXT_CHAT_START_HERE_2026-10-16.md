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
- Initial report commit: `4ce56b22f08e768a8ddba7c92a482b9559dcf4ce`; expanded and normalized final scan report: `69cea504b73165f58ab40719a210c8484319ab32`.

This pass went beyond exact hosted filename lookups:
- Recursively scanned all 23 visible `abdalrhmanata-gif/Nexo` branch-head trees. All scans completed with `truncated=false`.
- Compared the suffix/name independently of the timestamp. The 22 conflict names exist in current-source branches only with the checked-in/source-side versions; no hosted timestamp version path appeared in any visible branch-head tree.
- None of the six hosted-only names appeared in those branch-head trees.
- Queried commit history for all 22 current-source paths on `zavqera/ai-planner-integration`: 21 paths return one commit; W50 returns two commits for the same current source path.
- The earliest bulk-integration commit for W4 table privilege hardening, W7, W8, W9, W9.1 and W10 is `772f011624c199adc021a61d039a4cf13e9a3740` (“merge: stage ZAVQERA integration without historical artifact”); these files are marked added. Its parent `fcac980c9909c1a083007ed120d4742584fbcb4e` has no `supabase/migrations` files.
- Bounded Actions search: 3,000 run records (pages 1–30 of 10,590 records, spanning 2026-10-17T04:41:56Z to 2026-10-10T16:34:02Z). Sampled W21 evidence archives were 243 bytes in sampled Oct 10 runs and 326–328 bytes in sampled Oct 11–15 runs; sampled browser diagnostics were 660–743 bytes. Three sampled W25 runs had no artifacts. No historic SQL source archive was identified in these checks.

**Result: no authoritative historical SQL recovered.** This is a bounded public-branch-head/Actions inventory, not proof that no external/private/local archive exists. The 22 timestamp conflicts and six hosted-only names remain **UNKNOWN** until owner-controlled authoritative source/deployment provenance is produced.

Keep `hosted_write_authorized=false`, do not edit the hosted migration ledger, and do not apply W86 or any migration to hosted Development/Main. PR #1 and PR #2 remain OPEN/DRAFT/UNMERGED; release remains **NO-GO**.

## 12. Follow-up origin-reference search (2026-10-17)

The historical-source scan report was expanded/normalized at commit `69cea504b73165f58ab40719a210c8484319ab32`, incorporating the following bounded checks:
- GitHub matching tag refs in original `Nexo`: zero visible tags.
- Original PR #12 (“Integrate ZAVQERA W4-W16 baseline into main (clean, artifact-free)”) remains open/unmerged; the early migration import commit added the current migration paths rather than providing historical-renamed source bytes. PR #12 was read-only and not modified.
- Owner-scoped code search for six hosted-only migration names returned zero indexed results; this is only supporting negative evidence because code search is visibility/index limited.\n- Actions run scan now covers pages 1–30 (3,000 records); selected W21 artifact inventories include Oct 10–15 and still contain no SQL source archive.

No authoritative historic SQL has been recovered. The result remains UNKNOWN; no hosted write or ledger edit is authorized. Exact-current-head CI must be rechecked for the latest documentation-only commit before asserting final validation.

## 11. Conversation transfer checkpoint — final verified state for 2026-10-17 (18:30 Europe/Oslo)

**Read this section first in a new chat, then read the complete execution checkpoint and the reports linked below.** This section supersedes stale HEAD/run/state descriptions in earlier parts of this handoff; older text is retained as project history, not erased.

### Current repository state

- Isolated audit repo: https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015
- Audit/provenance PR #2: https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2 — OPEN / DRAFT / UNMERGED.
- Current PR #2 HEAD: `4a7f0d025764c1e81a95d02bd0f3481902a02426`, branch `codex/migration-ledger-provenance-20261015`.
- Exact-HEAD Flutter CI push run [39049023551 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39049023551) and PR run [39049027426 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39049027426). These completed successful MVP verification, controlled-adapter tests, web tests and web typecheck.
- W86 candidate PR #1: https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/1 — OPEN / DRAFT / UNMERGED; HEAD `0dc44842f9eaa25d0f34628b1c5c3de0741b41cf`, base `codex/w80-forward-correction-20261015`.
- Do not merge either audit PR. Original repo PR #39 and Issue #23 remain open; do not modify them as an incidental part of the database audit.
- Persistence comment with the capture review and gated remediation plan: https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/pull/2#issuecomment-6235818612. The source-recovery expanded report/previous progress is also recorded in PR #2 comments and `docs/ZAVQERA_HISTORICAL_MIGRATION_SOURCE_RECOVERY_SCAN_2026-10-17.md`.

### Fresh hosted Development capture — integrity and findings

- Local archive: `/mnt/data/20261017T151516202599Z.zip`
- Archive SHA-256: `9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d`
- Capture time: `2026-10-17T15:15:16.204988+00:00` UTC; ZIP CRC passed; query_01.json through query_13.json all present.
- Target: `ZAVQERA Development`, project ref `mrwmmbytcymqgwvcoywd`, region `eu-west-1`, status `ACTIVE_HEALTHY`, PostgreSQL 17.6 (`server_version_num=170006`).
- Base query pack SHA-256: `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`.
- Query 13 SHA-256: `806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b`.
- Capture role's read-only gate passed; `token_saved=false`. It has `rolbypassrls=true`; keep use limited to the pinned metadata-only audit, never application-row reads.

**W86 preflight — one narrow prerequisite passed, not authorization:** query 13 observed no parent-role ACL rows reachable from `service_role`, no `service_role` path to relation owner, and no membership path to `authenticated`. Thus the W86 parent-role/owner-path gate is `NO_PARENT_ROLE_ACL_OBSERVED`. Direct grants remain and the broader schema/source issues are unresolved.

**Remaining hosted Development drift:**
- `service_role` has direct/effective `SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER, MAINTAIN` on `public.agent_executions`; RLS is enabled but not forced.
- Missing relations `public.mission_authority_budgets` and `public.mission_authority_budget_reservations`.
- 26 expected columns absent; 10/11 queried expected constraints absent; all 8 queried expected indexes absent; `agent_execution_success_receipt_guard` trigger absent.
- Routine expectations: 17/40 match, 23 mismatch; 19 expected signatures absent and 4 legacy signatures expected absent remain present. Legacy `reserve_ai_generation(text)` SECURITY DEFINER routines and old six-argument Research completion overloads require owner review of body, dependency and ACL. Signature drift alone is not proof of exploitability; do not drop/revoke based on names alone.
- Eight explicit default function EXECUTE ACL rows appear for creators `postgres` and `supabase_admin`. Effective private-schema USAGE projection: anon=false, authenticated=true, service_role=true.
- Migration provenance: 89 checked-in source migration files vs 74 hosted ledger rows; 46 exact version/name matches; 22 same-name/different-version conflicts; 6 hosted-only names; 43 source tuples absent from the hosted ledger. The 22 conflict tuples overlap the set of 43 unmatched source tuples. The ledger only records version/name metadata and does not establish equality of deployed SQL bytes.

### Historical SQL source recovery was expanded, but not achieved

- Report: `docs/ZAVQERA_HISTORICAL_MIGRATION_SOURCE_RECOVERY_SCAN_2026-10-17.md` (see PR branch); it includes the exact conflicts/hosted-only names and the bounded search scopes.
- Scan expanded to 3,000 Actions run records (pages 1–30, timestamp range recorded in the report), sampled W21 artifacts and W25 runs, visible branch-head migration trees, tag refs, migration import history and owner-scoped exact-name searches. No authoritative historical SQL source archive was recovered. This is a bounded public/repo/CI search, **not proof that SQL never existed**, and not exhaustive of private owner-controlled clones, reflogs, backups, deployment archives or other external stores.
- The original Nexo tag query returned zero visible tags. PR #12 remains open/unmerged; migration files appear as the initial imported source rather than recovered historical renamed bytes. Treat every unresolved conflict and all six hosted-only names as `UNKNOWN`; do not reconstruct old SQL from adjacent/current migrations or edit the hosted ledger to force a match.

### Latest persistent documents

1. `docs/ZAVQERA_HOSTED_13_QUERY_CAPTURE_REVIEW_2026-10-17.md` — offline capture facts and full observed findings.
2. `docs/ZAVQERA_HOSTED_REMEDIATION_GATES_2026-10-17.md` — controlled sequence: historic provenance, owner review, offline remediation design, isolated acceptance, then separate execution authorization. Planning only; contains no authorization to execute hosted SQL.
3. `docs/ZAVQERA_HISTORICAL_MIGRATION_SOURCE_RECOVERY_SCAN_2026-10-17.md` — expanded source recovery attempts and explicit limits.
4. `docs/ZAVQERA_NEXT_CHAT_START_HERE_2026-10-16.md` — this handoff, with historical sections retained and this section authoritative for current status.

### Next steps — continue without re-asking already answered questions

1. Read the full local portable checkpoint `ZAVQERA_EXECUTION_CHECKPOINT_2026-10-17_UPDATED.md`, not just this summary, and preserve the history/addenda. Then inspect the local query ZIP and the reports above if their contents are needed.
2. Continue *only* from evidence-backed, non-mutating work. The highest-value unresolved task is to recover authoritative history from a database owner or owner-controlled original clone/reflog/backup/deployment bundle; any recovered SQL must have a trusted provenance chain and match a deployment identity. Keep unresolved rows `UNKNOWN`.
3. Require an independent database-owner review of the 13-query capture and exact remediation plan. Do not run SQL, apply W86 or any other migration, modify the hosted migration ledger, or change privileges/functions in hosted Development/Main.
4. Preserve PostgreSQL 17 corrected mixed-membership reachability semantics. The path `service_role --SET ROLE--> intermediate --INHERIT--> parent` can be reachable even when homogeneous cumulative flags are both false; do not revert the recurrence to homogeneous-only logic.
5. Keep `hosted_write_authorized=false`, `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed, release **NO-GO**, PR #1/#2 open/draft/unmerged. No paid services, no Codex credits, no credentials in chat, and no Main/Production changes.

No hosted writes, migrations, deployment or secret changes were made during the 13-query review or historical-source scan.


## 2026-10-17 — source manifest cross-platform reconciliation and regression gates

This addendum supersedes earlier comments that could not resolve the reported source HEAD. Keep the older notes as history, but use this update for current interpretation.

- The captured raw-checkout migration manifest SHA remains `0d05ab7285edc975084ddbc595d1af7d2dd0752cc27e94d8fe0549170419be38`.
- The Linux/LF checkout manifest independently calculated in CI is `555db007d0c25ee7bf6ed4f983766eea1dde170a7ef5d0e12cc710d5838c7094`. A regression test confirmed the captured manifest equals the simulated CRLF checkout form and differs from LF form. This explains the hash difference as line-ending representation; it does **not** prove deployed SQL bytes.
- The reported source HEAD `fbbcb080904acd88aad83a082803f627859026e2` is resolvable as a commit in the isolated audit repository: https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/commit/fbbcb080904acd88aad83a082803f627859026e2. It has 89 migration files. Commit comparison to the newer audit branch showed no path changes under `supabase/migrations`.
- Reviewer tool change commit: `15df03da787e6bd0900bce015ca09bac2220086f` adds `source_migration_manifest_lf_normalized_sha256` alongside the existing raw checkout-byte manifest. Test commit: `5d08941a5ac06098c8d5f693ceb4accaeaff2fc4` adds explicit CRLF capture matching and an LF-normalization regression. The ledger addendum is at commit `9b7dbd1dfc6313511f64647d6a7d3a854994b54d`.
- The W80 job on code/test SHA `5d08941a5ac06098c8d5f693ceb4accaeaff2fc4` passed the pre-database audit test step and had progressed to disposable migration replay at last observation; do not claim the full W80 run passed until its final result is confirmed. Flutter CI on the same code/test SHA passed push run [39052699725](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39052699725) and PR run [39052703565](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39052703565). Documentation-head CI on `9b7dbd1dfc6313511f64647d6a7d3a854994b54d` is being rechecked.
- Row-level reconciliation consistency regression passed in W80; current row counts remain 95: 46 metadata matches still `UNKNOWN` for SQL bytes, 22 conflicts, 21 source-only, six hosted-only; all owner review states remain `PENDING`.

No hosted database write, SQL, migration, deployment or merge occurred. `hosted_write_authorized=false`; `TRUSTED_DISPATCH_ADAPTERS` stays empty/fail-closed; PR #1/#2 stay OPEN/DRAFT/UNMERGED; Main/Production untouched; release remains **NO-GO**.

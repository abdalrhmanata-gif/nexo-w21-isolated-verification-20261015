# ZAVQERA launch runbook

Scope: operations for the tested MVP, not public-launch authorization.
Read [final launch gate](ZAVQERA_FINAL_LAUNCH_GATE.md) before inviting users.
Overall public production status is **OWNER DECISION REQUIRED**. Use the
[owner decision sheet](ZAVQERA_OWNER_LAUNCH_DECISIONS.md); no option is selected.
Only Development `mrwmmbytcymqgwvcoywd` is authorized for inspection here.
No main changes, Supabase Main access, paid resources, DNS, credential rotation
or deployment promotion without explicit owner approval.

## Operating record and contact

Release owner: project owner with Netlify/Supabase administrative access.
**Incident contact/channel, backup contact and coverage hours: owner must assign.**
The Netlify account owner receives deploy-request emails; this is not a verified
incident escalation service. Do not publish private account contact details.
Record a private reachable channel before real user intake.

Working branch URL:
https://zavqera-alternative-web-deployment--unique-kringle-3ce321.netlify.app

Site ID: `53e470f1-30da-497e-85f6-16179db4c985`.
Known-good W21 runtime: `a89d0a1b1516fffc53c981c594202da602b33808`.
Known-good artifact: `6abe25c07d794f000812021c` (ready).
Primary https://unique-kringle-3ce321.netlify.app is **not currently the working
application**; its checked routes return 404. Do not advertise it as ready.

## Deployment verification

1. Confirm clean tracked tree, intended branch and protected main SHA. Review
   changed paths against the tested runtime; docs/tests alone need no new deploy.
2. Run from apps/web: `npm test`, `npm run typecheck`, `npm run lint`,
   `npm run build`. Record counts and exact commit.
3. In Netlify Deploys verify `state=ready`, exact `commit_ref` and branch. A
   successful build or Git push alone is not deployment evidence.
4. Check the intended URL's published artifact separately from branch artifacts.
   Project production currently tracks an older main artifact. Do not switch
   production branch or publish a branch artifact under this runbook alone.
5. Inspect environment **keys and contexts**, never export values: production,
   branch and preview settings may differ. Currently production points to
   Development; owner decision is required before real public records.

Provider now reports production deploys paused by operational-credit limits.
Do not assume a production redeploy/rollback rebuild will work. Escalate the
capacity decision; neither purchase nor modify the subscription automatically.

## Health smoke

Run only safe anonymous GETs; choose the explicit approved URL:

```powershell
$base = 'https://zavqera-alternative-web-deployment--unique-kringle-3ce321.netlify.app'
foreach ($path in @('/', '/auth/sign-in', '/app', '/app/missions/new',
  '/app/missions/00000000-0000-4000-8000-000000000000')) {
  curl.exe --silent --output NUL --write-out "$path %{http_code} %{redirect_url}\n" "$base$path"
}
```

Expect public pages 200 and protected paths 307 to same-origin sign-in. Check
`/api/status` for server runtime/configured flags only. Never treat configuration
booleans as database connectivity, successful auth or completion evidence.
Do not log cookies, Authorization headers, user mission data or full error payloads.

## Auth and isolated full-loop check

Review `apps/web/README.md` before setup. **Never run E2E on hosted Development.**
No shared test password is required; two users are generated through local sign-up.

One-time owner setup (fresh, dedicated workdir only):

```powershell
supabase --version
docker version --format '{{.Server.Version}}'
New-Item -ItemType Directory -Path C:\zavqera-e2e
supabase init --workdir C:\zavqera-e2e
```

Use native Supabase on PATH, not just a `.cmd` shim. Configure
`supabase\config.toml`: project_id `zavqera-e2e-local`, db major_version 17,
local email confirmations disabled. Never link this workdir to a hosted project.
Create `C:\zavqera-e2e\ZAVQERA_E2E_DISPOSABLE` containing only the project ID;
this consents to destruction of that local stack, not any other project.

Obtain the current schema-only public/private snapshot using the exact
Development-only dump instructions in the README through a private secure shell.
No data/roles/managed auth schema export. Restore the documented application auth
trigger in that same snapshot. Put exactly one reviewed
`<14-digit timestamp>_development_schema.sql` in the workdir migrations directory.
Check W20/W21 definitions, grants and policy/trigger against current evidence.
Do not replay the incomplete repository history or commit the snapshot.

From apps/web in a fresh shell without hosted or privileged credentials:

```powershell
npx playwright install chromium
$env:ZAVQERA_E2E_MODE = 'disposable-full-loop'
$env:ZAVQERA_E2E_SUPABASE_WORKDIR = 'C:\zavqera-e2e'
npm run test:e2e
```

Do not set `NEXT_PUBLIC_SUPABASE_*`; the harness derives local values.
Unset service-role/secret/access-token/database-password variables and legacy
E2E user variables; preflight lists names without values. Free port 3210 first,
without killing unrelated processes. Exit 2 means blocked, not skipped success.

The harness checks sign-in/out, cookies, mission/actions, next action, Waiting,
follow-up leave/return, verification/outcome, cancellation, UI/direct-RPC refusal,
cross-user rejection and teardown. Do not weaken failures.
Capture test status and sanitized fixture-ID ledger plus cleanup proof.
No browser execution occurred on this host during launch preparation.

After interruption, cleanup only the explicitly consented local project:

```powershell
supabase stop --no-backup --workdir C:\zavqera-e2e
docker ps -aq --filter label=com.supabase.cli.project=zavqera-e2e-local
docker volume ls -q --filter label=com.supabase.cli.project=zavqera-e2e-local
```

Both Docker queries must return no IDs. If not, stop and inspect those exact
resources; never use global prune, broad deletion or disable history protections.
Hard process termination can prevent teardown; the next preflight cleans before
starting. Until verified, mark CLEANUP NOT VERIFIED.

## Monitoring and incident response

Current monitoring is **PARTIAL**, not an alerting SLA:

| Signal | Existing surface | Operator action |
|---|---|---|
| Deployment | Netlify Deploys, build logs, GitHub preview commit checks | Check exact SHA/state before sharing; investigate failed/paused builds |
| App/SSR/API errors | Netlify Logs / Functions / Next.js server handler logs | Filter by deployment and incident time; inspect status/exception without exporting user data |
| Database/auth | Development Logs Explorer and Auth logs | Check time window, permission failures, connection errors and sign-in failure patterns |
| Security posture | Development Security Advisor | Read-only rerun; record changes rather than blindly applying suggested grants |
| Availability | Manual safe smoke above | Owner sets review cadence or authorizes a no-cost monitor |
| Notifications | Netlify preview commit checks and deploy-request owner emails | Not proof of runtime/uptime alerts; owner chooses recipient/incident channel |

No new paid monitoring or log drain enabled. Do not claim zero runtime errors
from available dashboard links; no comprehensive user-log audit was performed.

For an incident: record UTC time, affected URL, deploy/commit, symptoms and
sanitized request IDs. Notify the assigned owner; halt invitations/releases.
Classify access/data-integrity issues as urgent. Preserve logs securely, avoid
reproducing against personal records, and isolate impact only through an
owner-authorized operational change. Check provider status and plan limits before
changing code. Close only after regression, safe smoke, relevant auth/SQL proof
and cleanup; communicate residual impact honestly.

## Rollback

**Procedure ready; execution not rehearsed.**
Do not roll back W21's completion guard or reapply W20.

- For a new runtime regression, prefer a focused revert commit on the allowed
  branch, run the full gate and deploy after authorization/capacity check.
- For urgent artifact rollback, owner inspects the known-good Netlify deploy,
  confirms source/environment/database compatibility and exact target URL before
  using provider publish/rollback controls. Publishing a branch artifact may
  affect the primary URL: do not assume it changes only the branch alias.
- A primary-production operation requires explicit approval; no main merge or
  force push is a prerequisite. Never publish the known-broken old main artifact
  merely because its metadata says ready.
- Verify ready artifact and routes after rollback. Existing deploy publish
  behavior during plan pause is untested; do not promise emergency recovery time.
- Database changes require a separately reviewed, data-preserving forward fix or
  restoration plan. An application rollback does not restore database contents.

## Database safety and backup/recovery

Compare the two unselected strategies, proposed recovery targets and restore
requirements in [backup/recovery](ZAVQERA_PRODUCTION_BACKUP_AND_RECOVERY.md).

Current Development has W20 `20261001081755` and W21 `20261001091146`.
Verify exact target before each read/write. Existing history mismatch prevents
trustworthy empty replay: no broad `db push`, no invented old migrations.
Ownership, fixed search_path, function grants, locking/version checks,
verification/outcome rules and append-only history must remain intact.

**Recovery coverage is missing for public user data.** Backups dashboard says
Free Plan does not include project backups. No external backup or restore drill
was verified. Schema-only E2E dumps and Git do not recover user records.

Owner must choose data retention, backup frequency, secure encrypted storage,
access policy, recovery-point and recovery-time objectives; authorize any cost
separately. A backup plan must account for database data, auth recovery and any
external storage actually used. Test restore in an explicitly authorized
disposable target, not Supabase Main or the live Development project. Record
restored counts/integrity/auth behavior and timing without putting data in Git.
Do not accept public records until backup and restoration evidence meets the
owner's approved objectives.

## Domain and owner-only changes

Use the [domain launch plan](ZAVQERA_DOMAIN_LAUNCH_PLAN.md) for hostname,
DNS/TLS and auth checks. The [operations procedure](ZAVQERA_PRODUCTION_OPERATIONS.md)
and [E2E checklist](ZAVQERA_E2E_OWNER_RUN_CHECKLIST.md) provide operator handoffs.

Custom domain: **NOT CONFIGURED**. A Netlify branch URL is usable for an approved
controlled beta, not proof of branded production readiness.
After the owner chooses/owns a domain and authorizes connection: Netlify project
Domain management -> Add domain; use the exact DNS records Netlify provides at
the existing DNS provider, verify TLS, choose canonical hostname and redirects,
then authorize matching Supabase Site URL/redirect allowlist updates.
Test confirmation/callback/logout on that origin. Do not guess DNS records,
purchase a domain or alter auth redirect settings automatically.

Production backend selection, data migration, paid backup/password protection,
Netlify capacity, domain/DNS, visitor restrictions, alert destinations and
credential rotation remain owner-only decisions. Resolve the primary 404
deployment before announcing that URL. Production currently targets Development;
never silently point it to Supabase Main.

## Secrets and known limitations

Use provider secret stores or private operator environment; never chat, Git,
schema dumps with data, logs or screenshots containing credentials.
Publishable Supabase keys may be browser-visible; service-role keys, database
passwords and management tokens may not. Never add privileged `NEXT_PUBLIC_*`.
Show key names, scopes and target-match booleans, not values.

Current automated browser evidence (2026-10-18): W21 passed on exact source
HEAD `0fd69902305ef9603e90aef4ae446a95161306d1` ([run 39154053027](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39154053027));
both browser E2E tests passed. The isolated route check denied the unregistered
Mission Action adapter with HTTP 503, `unregistered_adapter_denied`, and
`providerCall=not_attempted`. Evidence confirms PostgreSQL 17, repository
migrations only, cleanup exit code 0, no residual containers/volumes, and
`cleanup_verified=true`. Web Unit (374 tests: 373 pass, 0 fail, 1 skipped),
Web CI/build, Flutter CI, and 37 launch-validator regression tests also passed
on that source HEAD: [Web Unit](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39154055655),
[Web CI](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39154055648),
[Flutter CI](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39154055664).

Current isolated CI evidence (2026-10-18): [W21 run 39157505523](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39157505523) passed 27/27 steps, including browser E2E 2/2, a limited empty-data logical dump/restore smoke, and verified cleanup. This does not establish full application restore, extension parity, hosted Development parity, production auth/SMTP, real-provider behavior, or RPO/RTO.

Still open: no representative data-bearing backup/restore rehearsal or measured RPO/RTO; no staffed incident channel or operations exercise; the primary URL has a recorded 404, production publishing was recorded as paused, no custom domain is configured, leaked-password protection is disabled, intentional SECURITY DEFINER advisor warnings require disposition, and historical hosted migration replay differs. T01-T05 have owner-confirmed PASS labels but no detailed session observations. These limits do not authorize weakening security, modifying protected systems, or expanding product scope.


## Latest isolated restore-smoke result — 2026-10-18

## Latest isolated PostgreSQL restore-smoke evidence — 2026-10-18

At exact source/test HEAD `86b8b49ee3dd16371ca607089f49de8ba0778f9f`, [W21 run 39157505523](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39157505523) completed **SUCCESS (27/27 steps)**. The W21 workflow also passed disposable PostgreSQL 17/pgTAP, Mission Authority/quota/workspace regressions, four concurrency checks, fake-provider gateway integration, browser E2E (2/2), and cleanup; evidence reports no remaining containers or volumes.

The new logical backup/restore smoke passed using a custom-format dump (476,290 bytes; SHA-256 `c19fc303fa9b24eabb6985dfe522a12dbb0977afb7147919b5010d17c8db0afc`) kept entirely inside the CI-labeled disposable PostgreSQL container. It restored to a separate temporary database, verified **51 source vs 51 restored** relations across the application/auth/migration inventory, matched row counts for the checked core relations, and confirmed `restore_database_removed=true`, `dump_removed=true`, `restore_cleanup_verified=true`. The migration ledger count in this disposable test was 88. This is not the hosted Development schema/ledger or evidence of historical deployment provenance.

**Scope limits:** the two source relations in schema `extensions` are explicitly reported separately (source 2, restore 0) and are not part of the strict application-relation parity assertion; extension-member parity is therefore not proven. Core data tables and auth users/identities were empty in this disposable smoke. It is not a representative production-data restore, full Supabase managed-schema restore, measured RPO/RTO exercise, or recovery acceptance.

The other exact-head workflows also passed: [Web Unit](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39157509792), [Web CI/build](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39157509751), and [Flutter CI](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39157509777).

The four public-launch blockers remain open: hosted Development privilege/schema drift; unresolved historic migration source/provenance; no independent security/database review; and no full recovery/RPO/RTO, staffed operations exercise, detailed T01–T05 observations, or accountable release approval. Keep `hosted_write_authorized=false`, `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed, and public release **NO-GO**.


## Superseding seeded restore-smoke evidence — 2026-10-19

At exact code/test HEAD `6cd8bf6044c2a6f2ac173f19b9d8fb78f2af7f2f`, [W21 run 39222501670](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39222501670) completed **SUCCESS, 27/27 steps**.

- Disposable PostgreSQL 17 replay and pgTAP succeeded; Mission Authority and quota/workspace suites succeeded; four concurrency proofs and W72 fake-provider integration succeeded.
- Browser E2E: **2 passed (2.6 minutes)**. Cleanup evidence states `remaining_containers=none`, `remaining_volumes=none`, `cleanup_verified=true`.
- A custom-format allowlisted-schema dump (477,328 bytes; SHA-256 `4c6e134de68aac8b769aad1147da5a7c086e19327c70b19d34e3e965adac5b3b`) was restored to a separate temporary database. It proved `source_app_relation_count=52` and `restored_app_relation_count=52`, and the exact synthetic row matched (`sentinel_row_matched=true`). It also checked core relation row counts: `public.w21_restore_smoke_sentinel=1`; the app business tables and auth users/identities were empty; `supabase_migrations.schema_migrations=88`.
- The temporary database, dump file and source sentinel were removed and verified: `restore_database_removed=true`, `dump_removed=true`, `source_sentinel_removed=true`, `restore_cleanup_verified=true`.
- Schema `extensions` remains outside strict relation parity: source has 2 relations there and restore has 0. Extension-member/managed-schema parity is **not proven**. This is a disposable, synthetic-data logical restore smoke—not a complete Supabase backup/restore, representative production data recovery, measured RPO/RTO, or recovery acceptance.
- All other exact-head workflows succeeded: [Web Unit 39222509610](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39222509610) (**374 tests; 373 pass, 0 fail, 1 skipped**), [Web CI 39222509604](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39222509604), and [Flutter CI 39222509681](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39222509681).

This reduces uncertainty for the isolated restore path but does not resolve the four public-release blockers: hosted Development DB/security drift; historical migration provenance; missing independent security/database approval; and full data-bearing recovery/RPO/RTO, staffed operations exercise, detailed T01–T05 observations and accountable release approval. Preserve `hosted_write_authorized=false`, keep `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed, and keep public production **NO-GO**.


## Superseding current-head evidence — 2026-10-19 — `7c0a9fe06d8fcefb0310447ccb52c92c1be6543b`

On exact current launch-gate HEAD `7c0a9fe06d8fcefb0310447ccb52c92c1be6543b`, the following GitHub Actions runs all completed **SUCCESS**:

- [W21 Local Launch Gate 39223464834](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39223464834): **27/27 steps**; PostgreSQL 17 replay and pgTAP, Mission Authority/quota/workspace security tests, four concurrency proofs, W72 fake-provider gateway, browser E2E **2 passed (2.4 minutes)**, and disposable-stack cleanup.
- [Web CI/build 39223471551](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39223471551): success.
- [Web Unit 39223471584](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39223471584): success.
- [Flutter CI 39223471648](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39223471648): success.

W21 evidence artifact `W21_EVIDENCE.txt` was downloaded and inspected. It reports `result=success`, exact `git_sha=7c0a9fe06d8fcefb0310447ccb52c92c1be6543b`, `postgres_major=17`, `cleanup_verified=true`, `remaining_containers=none`, and `remaining_volumes=none`. The allowlisted custom-format logical dump was 477,328 bytes (SHA-256 `b1920bf974a2fa7d6e65d10a2c7f2a34d8ae5e5166f646437af36c6348ec4903`). It restored into a separate disposable database and verified 52 source/52 restored application/auth/migration relations plus an exact synthetic sentinel row. The source sentinel, restore database and dump were deleted and each cleanup check passed.

**Limits:** schema `extensions` reports 2 source relations and 0 restored relations and remains outside strict relation parity. Business tables and auth users/identities were empty apart from the synthetic test row; disposable migration row count was 88. This is not a representative production-data backup, complete managed Supabase recovery, extension-parity proof, measured RPO/RTO, hosted Development parity, or independent release approval. The four blockers below remain open; public production remains **NO-GO**.

### Operator decision still required

This restore smoke used only a synthetic sentinel and an allowlisted schema set. Before a limited beta or public release, the accountable owner must approve a representative backup source, separately named restore target, retention/access policy, acceptance checks, and measured recovery objectives; then perform and record a data-bearing recovery exercise and an incident/rollback tabletop. This update does not choose or execute any hosted action.

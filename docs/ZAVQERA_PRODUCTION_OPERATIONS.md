# Minimum production operations

2026-10-01. **Procedure ready; monitoring PARTIAL; public launch not authorized.**
No monitoring purchase, integration or schedule was enabled.
Use the [launch runbook](ZAVQERA_LAUNCH_RUNBOOK.md) for exact safe smoke commands
and [owner decisions](ZAVQERA_OWNER_LAUNCH_DECISIONS.md) before activation.

## Ownership and cadence

Incident owner/backup contact/channel/coverage hours: **UNASSIGNED**.
The project owner must assign a reachable primary and cover privately before
public intake. Netlify's configured deploy-request owner emails and preview
commit checks are not application-error or uptime alerts.

Proposed minimum: verify before/after each deployment, at the start of every
controlled-beta session, daily during user intake, and immediately after a
report. Owner must assign this cadence; it is not unattended monitoring.

| Step | Procedure | Evidence / escalation |
|---|---|---|
| 1. Deployment | Netlify site `unique-kringle-3ce321`: verify artifact state, source SHA, branch and target URL separately | Known-good branch artifact `6abe25c07d794f000812021c` / `a89d0a1`; old main artifact is not approved rollback |
| 2. Public health | Anonymous GET `/`, `/auth/sign-in`, protected `/app` and mission routes using runbook | Branch: 200 public, 307 same-origin sign-in protected. Primary currently 404; do not classify that as a new branch regression |
| 3. Authentication | Run the isolated [E2E checklist](ZAVQERA_E2E_OWNER_RUN_CHECKLIST.md) for signup/signin/signout, callback, refresh/return and cross-user checks | Automated disposable browser E2E passed 2/2 on W21 run 39227492355 (head `f7eeb4a3be927e848307715845f4eb35d5b41382`). This is CI evidence only; a hosted auth-only check still requires an owner-approved account, and no hosted fixture was created. |
| 4. Provider logs | Review Netlify Deploys/build and server/function logs plus approved Supabase Auth/Postgres Logs Explorer time window | Record UTC, deployment, status and sanitized request ID; never dump personal records, cookies or JWTs |
| 5. Escalation | Notify assigned incident owner for repeated 5xx/auth failure, data integrity/ownership concern, failed backup or capacity pause | Security/data-loss concerns urgent: halt invitations/releases, preserve restricted evidence; changes require authorization |
| 6. Rollback | Follow runbook: focused branch revert or owner-approved known-good artifact publish; recheck compatibility, capacity and URL | Procedure prepared, not rehearsed. Never force push, modify main, undo W21 guard or restore a database as routine code rollback |
| 7. Incident ownership | Record responsible person, impact, containment approval, communication and resolution time | Missing coverage must remain visible; no fabricated on-call SLA |
| 8. Secrets | Use private provider/owner secret stores; keep evidence metadata-only | No privileged NEXT_PUBLIC variables, full payload exports or pasted credentials |

If authorized to inspect a hosted account, sign in manually without exposing
credentials, confirm return/refresh, sign out and check protected-route redirect.
Do not edit that person's missions. This limited check does not replace local
full-loop/cross-user E2E. Confirmation-email and new-domain checks are a separate
owner-coordinated auth smoke, not permission to leave synthetic hosted fixtures.

## Current operational limits

Production, branch deploys and deploy previews all map to Development.
Primary production serves the old main artifact and checked routes return 404.
Netlify explicitly reports production deploys paused by operational-credit
limits. Read provider status first; do not press Deploy/Publish to probe capacity.
Owner chooses wait or upgrade; upgrade does not itself approve promotion.

No verified uptime monitor, runtime-alert destination, comprehensive live error
review, backup receipt or restore rehearsal exists. Review provider retention
and usage limits before relying on logs; avoid enabling paid logging.
Five intentional SECURITY DEFINER advisor warnings and disabled leaked-password
protection remain documented in the final gate, not silently waived.

For resolution: prove the selected artifact and safe health routes, rerun
relevant tests, confirm auth/data boundary when impacted, verify recovery/cleanup,
and record any remaining limitation. Only the owner may approve renewed intake.
Reference [backup plan](ZAVQERA_PRODUCTION_BACKUP_AND_RECOVERY.md) and
[domain plan](ZAVQERA_DOMAIN_LAUNCH_PLAN.md) for recovery and hostname changes.


## Superseding current CI evidence — 2026-10-19

[W21 run 39227492355](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39227492355) passed 27/27 steps on `f7eeb4a3be927e848307715845f4eb35d5b41382`; [Web Unit 39227497784](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39227497784), [Web CI 39227497878](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39227497878), and [Flutter CI 39227497796](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39227497796) also passed on the same head. Browser E2E passed 2/2, and disposable cleanup verified no remaining containers or volumes.

**The operational gate is still blocked:** incident owner, backup contact/channel and coverage remain UNASSIGNED; rollback has not been rehearsed; hosted authentication/SMTP/OAuth and custom-domain redirects have not been validated. Passing disposable CI does not substitute for the owner-run operations/incident exercise or authorize production publish.

## Superseding isolated recovery verification — 2026-10-19

[W21 run 39240788125](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39240788125) passed **27/27 steps** on exact code/test HEAD `41c4a3cdf1f290ed1e958fd44873333b3910ac23`. The recovery smoke restored a linked synthetic auth user/profile, workspace owner membership, mission and two mission actions; the expected/source/restored relationship fingerprints matched. Post-data constraints and trigger definitions were restored and checked. It verified fixture/sentinel/database/dump removal, and the full stack reported no remaining containers or volumes. [Web Unit](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39240794770), [Web CI](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39240795362), and [Flutter CI](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/39240794970) also passed on the same HEAD. The browser E2E run passed **2/2 tests in 2.3 minutes**.

This improves only isolated synthetic-data recovery evidence. Extension parity remains unproven (2 source extension-schema relations, 0 restored); no representative production data, full managed-Supabase recovery, retained off-site backup, measured RPO/RTO, staffed incident/rollback drill, hosted-auth/SMTP/OAuth/domain validation or independent sign-off has been demonstrated. Incident owner and backup contact/coverage remain unassigned. Public release remains **NO-GO**.

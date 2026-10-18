# ZAVQERA — GitHub branch-tip historical migration source scan (2026-10-18)

**Disposition: no disputed hosted-version SQL paths recovered in the visible original-repository branch snapshots. Hosted SQL-byte provenance remains UNKNOWN; release NO-GO.**

## Scope and method

- Repository scanned: `abdalrhmanata-gif/Nexo`.
- Ref snapshot: the 23 branch refs returned by GitHub's branch listing on 2026-10-18, identified in the table below by branch name and tip SHA.
- For every tip, fetched its recursive Git tree. All 23 tree responses had `truncated=false`.
- Counted blobs under `supabase/migrations/*.sql`; compared the exact filenames from the 95-row migration decision intake, including the 22 source-side names implicated in same-name/version conflicts and the 28 contested hosted filenames (22 version-conflict hosted tuples plus six hosted-only tuples).
- Compared Git blob SHAs for each source-side conflict file against baseline branch `codex/egress-gateway-auth-staging-20261015`, tip `b184b91540c80be8a07b455bddaeca9080fad4f0`.
- This was a read-only GitHub tree/path/blob-metadata review. No file contents were executed, and no Supabase connection, SQL, hosted mutation, migration, deployment or secret change was performed.

## Branch-tip coverage

| Branch | Tip SHA | Tree blobs | Migration SQL files | Exact disputed hosted filenames found |
|---|---|---:|---:|---:|
| `abdalrhmanata-gif-import-nexo-v1-9` | `9219518b853a4125721b4292067840a685c7e74a` | 108 | 0 | 0 |
| `abdalrhmanata-gif-netlify-alternative-deployment` | `bc7dd99ad49a580392b8b64fd165cc2802be9c59` | 256 | 16 | 0 |
| `agent-origin-main-clean-2df7` | `1de719f9cd1f4b15f22efc7e880c9374056a8c79` | 253 | 16 | 0 |
| `codex/egress-gateway-auth-staging-20261015` | `b184b91540c80be8a07b455bddaeca9080fad4f0` | 608 | 87 | 0 |
| `codex/mission-action-runtime-seam-test-20261014` | `9d752a59f0683ea7149633138dc85bb33cf9a41b` | 611 | 87 | 0 |
| `codex/w66-w82-dev-audit-refresh-20261014` | `5aea5611bbb975b971a9c7f7947d4c47b1cb438b` | 593 | 87 | 0 |
| `codex/w80-pgtap-verification-20261014` | `0c56de7c84d41c43f77d86e84dea67f2d88f6ec7` | 596 | 87 | 0 |
| `codex/w80-sql-privilege-fix-20261014` | `2e7dcccf9679ecc78f2b522064a4b121135645c4` | 594 | 87 | 0 |
| `codex/w80-sql-review-base-20261014` | `5e2094fd27c7de60496729956af562651de93137` | 593 | 87 | 0 |
| `codex/zavqera-windows-path-guards` | `5c1d093d6b2c33c41e5446d10f2c5ed8256be996` | 582 | 85 | 0 |
| `followthrough-action-loop` | `0e1daf921e72d248962d68d9cf29af26591ca166` | 114 | 0 | 0 |
| `main` | `f64a87addb25a7455c6acde446b81bb3427d43cc` | 119 | 0 | 0 |
| `zavqera/ai-planner-integration` | `1b02272a7281b2e9ebf9020cd21a8ac9de3e577e` | 612 | 87 | 0 |
| `zavqera/alternative-web-deployment` | `46dc6029f084fb000ba511478d6e8aec3eb532b3` | 321 | 19 | 0 |
| `zavqera/controlled-adapter-ci-validation` | `96a6803b69dbe62e886bfe04fc4fee5c818e9565` | 313 | 19 | 0 |
| `zavqera/first-user-validation-execution-kit` | `9402265722126333bdb684e5bd4fc0e4aff9a001` | 252 | 16 | 0 |
| `codex/w80-workflow-enablement-20261014` | `81ef820d160bfef04edbbab181fc562de203f7fa` | 120 | 0 | 0 |
| `zavqera/integrate-origin-main-clean` | `bb095b716c29d4c13e83d5c817bf2676d127d61a` | 253 | 16 | 0 |
| `zavqera/netlify-preview-candidate` | `1c4e4b37f7378443ec1faaea169b1279469ceaa7` | 393 | 39 | 0 |
| `zavqera/next-phase-first-user-validation` | `ff567e524c8358148922c8780674c16e2be67020` | 251 | 16 | 0 |
| `zavqera/openai-responses-integration` | `45d335e4c8a7a6b9627795e51fcb73fdde453f43` | 131 | 0 | 0 |
| `zavqera/public-preview-deployment` | `6f66b3b3c317fa7787753a8668c84ab8a076b959` | 255 | 16 | 0 |
| `zavqera/web-technical-validation-ci` | `c61536c08014712877cefb9cfe8a4fdfc7bd7de1` | 253 | 16 | 0 |

## Findings

1. **0 of 28 exact contested hosted filename paths** were present in any of the 23 visible branch-tip trees. This includes the hosted versions of all 22 same-name/different-version rows and all six hosted-only rows.
2. The **22 source-side filenames** for the version-conflict rows were present in the migration-bearing, 87-file branches. For each source-side conflict file present in a scanned branch, its Git blob SHA matched the baseline branch above; no alternate source blob was observed across the scanned branch tips.
3. The broadest original-repository branch snapshots contain 87 SQL migration files; they do not contain all the files in the 89-row intake source set. In particular, the audit branch's later W83/W84 sources must not be treated as part of these older original-repository snapshots without their separate source identity.
4. These results add no deployment receipt, executed-SQL digest or mapping from any source blob to a hosted migration event. A missing filename from visible branch tips does not prove that SQL was never executed, and a matching source filename/blob does not prove its bytes were deployed.

## Disposition per unresolved class

- **ZMR-008 and the other 21 same-name/version conflicts:** retain `NAME_VERSION_CONFLICT`; source bytes may be available under the source version, but the historical hosted SQL remains unverified.
- **Six hosted-only tuples (ZMR-090–ZMR-095):** keep their source as UNKNOWN; no exact source path was found among the current 23 branch tips.
- Do not change the hosted migration ledger, rewrite timestamps, infer equivalent bytes from names, or generate synthetic historical migrations.
- Release remains **NO-GO**; `hosted_write_authorized=false`; `TRUSTED_DISPATCH_ADAPTERS` remains empty/fail-closed.

## Next recovery action

Stop repeating the same visible-ref and Library-ZIP searches. The next search needs evidence outside these snapshots: original developer-machine clones including reflogs/stashes/unpushed branches, external/private/deleted repositories accessible to the owner, deployment job logs/artifacts, controlled migration deployment archives, and backup/change records. Preserve each candidate's chain of custody and SHA-256. Only a trusted deployment record that ties actual SQL bytes to the exact project/migration can close a deployed-byte row.

This report is a branch-tip file-path/blob-identity check only. It is not a live database review, SQL equivalence finding, owner approval or release approval.


## Supplementary GitHub Actions artifact check — 2026-10-18

To test whether recent original-repository validation artifacts held overlooked SQL, I reviewed artifact metadata for the 11 `ZAVQERA W21 Local Launch Gate` runs surfaced in the recent Oct 15–17 run window. They contain only tiny `zavqera-w21-evidence` artifacts (326–328 bytes) and/or `zavqera-w21-browser-diagnostics` artifacts (742–744 bytes); no artifact in this reviewed set was a migration/source archive by name or size.

I downloaded and unpacked one pair from run `39003536607` for content inspection:

- Evidence artifact [12090475405](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/39003536607/artifacts/12090475405), ZIP SHA-256 `77107ebae0517f9a4d349de8dccb6ea1507c4a38a67c89aabaf53ae44f32cdde`. It contains only `W21_EVIDENCE.txt` (264 bytes) recording a successful local E2E run, tested source SHA `bd40ab09498dd07088eb77d862dbf6da9cc69370`, PostgreSQL major 17, disposable project ID, and verified container/volume cleanup.
- Browser diagnostics artifact [12089583550](https://github.com/abdalrhmanata-gif/Nexo/actions/runs/39003536607/artifacts/12089583550), ZIP SHA-256 `a847a4833ab30eb231fda96f016f110c297fe092897484420bd7dcfb017bdd32`. It contains only `test-e2e.log` (972 bytes), showing the unregistered adapter was denied before provider call, two browser E2E tests passed, and disposable fixtures were cleaned up.

These artifacts are useful as **local behavior/cleanup evidence**, not as historical hosted migration sources or deployment receipts. The W21 run records do not close any of the 22 hosted-version conflicts or six hosted-only migration rows. This artifact check is limited to the 11 recent W21 runs surfaced for inspection; it is not a claim that every artifact from every repository workflow was downloaded or unpacked.

**Recovery decision:** the current visible Git branch snapshots, the 112-archive Library scan, and this bounded W21 artifact check produced no historic deployed-SQL bytes or trusted per-migration deployment receipt. The next viable evidence source is outside those checked materials: owner-device Git clones/reflogs/stashes/unpushed refs, external/private/deleted repositories, deployment-run logs/artifacts that recorded actual SQL, or controlled backups/change records. If none can establish the historical bytes, keep the affected rows UNKNOWN and require a separately reviewed re-baselining decision rather than inventing SQL.

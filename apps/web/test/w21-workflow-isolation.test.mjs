import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
const workflow = readFileSync(
  join(repoRoot, ".github", "workflows", "zavqera-w21-e2e.yml"),
  "utf8",
);

test("W21 can only test a disposable repository-migration stack", () => {
  assert.match(workflow, /^\s*workflow_dispatch:\s*$/m);
  assert.match(workflow, /^permissions:\s*\r?\n\s+contents:\s*read\s*$/m);
  assert.doesNotMatch(workflow, /\$\{\{\s*secrets\./i,
    "W21 must not receive repository or environment secrets");
  for (const credential of [
    "ZAVQERA_DEVELOPMENT_DB_URL",
    "SUPABASE_DEV_SERVICE_ROLE_KEY",
    "SUPABASE_ACCESS_TOKEN",
    "OPENAI_API_KEY",
    "RESEND_API_KEY",
    "NETLIFY_AUTH_TOKEN",
  ]) {
    assert.doesNotMatch(workflow, new RegExp(`(?:^|\\n)\\s*(?:-\\s*)?${credential}\\s*[:=]`, "i"),
      `W21 must not assign hosted or external credential ${credential}`);
  }
  assert.doesNotMatch(workflow, /mrwmmbytcymqgwvcoywd|supabase\.co|netlify\.app|api\.openai\.com|api\.resend\.com/i,
    "W21 must not target hosted Development, Production, or provider endpoints");
  assert.doesNotMatch(workflow, /\bsupabase\s+(?:link|db\s+(?:push|dump|pull))\b/i,
    "W21 must not link, dump, pull, or push a hosted database");
  assert.match(workflow, /cp -R "\$GITHUB_WORKSPACE\/supabase\/migrations\/." "\$workdir\/supabase\/migrations\/"/);
  assert.match(workflow, /supabase start[^\n]*--workdir "\$ZAVQERA_E2E_SUPABASE_WORKDIR"/);
  assert.match(workflow, /supabase test db/);
  assert.match(workflow, /ZAVQERA_AI_PROVIDER_MODE=mock/);
  assert.match(workflow, /unset NEXT_PUBLIC_SUPABASE_URL NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY/);
  assert.match(workflow, /supabase stop --no-backup --workdir "\$ZAVQERA_E2E_SUPABASE_WORKDIR"/);
  assert.match(workflow, /cleanup_verified=true/);
  assert.doesNotMatch(workflow, /netlify (?:deploy|build)|deploy-to-production|production-deploy/i);

  const requiredPgTapTests = [
    "w66_service_role_table_privilege_hardening.sql",
    "w67_legacy_research_rpc_privilege_hardening.sql",
    "w80_invitation_helper_privileges.sql",
    "w81_read_only_research_jit_claim.sql",
    "w82_ai_generation_reservation_identity.sql",
    "w84_postgres_function_default_acl_hardening.sql",
  ];
  for (const testFile of requiredPgTapTests) {
    assert.ok(
      workflow.includes(`cp "$GITHUB_WORKSPACE/supabase/tests/${testFile}" "$workdir/supabase/tests/${testFile}"`),
      `W21 must copy ${testFile} into the disposable database workdir`,
    );
  }

  const missionAuthorityRegressionList = workflow.split("for test_file in \\\n")[1]?.split("\n          do")[0] ?? "";
  for (const testFile of [
    "w66_service_role_table_privilege_hardening.sql",
    "w67_legacy_research_rpc_privilege_hardening.sql",
    "w80_invitation_helper_privileges.sql",
    "w81_read_only_research_jit_claim.sql",
    "w84_postgres_function_default_acl_hardening.sql",
  ]) {
    assert.ok(
      missionAuthorityRegressionList.includes(`supabase/tests/${testFile}`),
      `W21 must explicitly execute ${testFile}`,
    );
  }

  const quotaRegressionStep = workflow.split("Run AI quota, plan and workspace security tests")[1]?.split("Run actual-ledger concurrent idempotency proof")[0] ?? "";
  assert.ok(
    quotaRegressionStep.includes("supabase test db supabase/tests/w82_ai_generation_reservation_identity.sql"),
    "W21 must explicitly execute W82 AI generation reservation identity pgTAP",
  );

  const catalogReport = "w83_invitation_catalog_reconciliation.sql";
  assert.ok(
    workflow.includes(`cp "$GITHUB_WORKSPACE/supabase/tests/${catalogReport}" "$workdir/supabase/tests/${catalogReport}"`),
    "W21 must stage the read-only W83 catalog report",
  );
  const catalogStep = workflow.split("Run W83 read-only catalog reconciliation on disposable PG17")[1]?.split("Run Mission Authority execution security regressions")[0] ?? "";
  for (const required of [
    "docker exec -u postgres",
    "psql -X -v ON_ERROR_STOP=1",
    "READ_ONLY_GUARD=CONFIRMED",
    "20261015100000",
    "20261015110000",
    "W84 expected for future functions created by postgres",
    "Default ACL overrides",
    "Built-in function EXECUTE default ACL baseline",
  ]) {
    assert.ok(catalogStep.includes(required), `W21 catalog reconciliation must include ${required}`);
  }
  assert.ok(
    workflow.includes('cat "$RUNNER_TEMP/W83_LOCAL_CATALOG_RECONCILIATION.txt" >> "$RUNNER_TEMP/W21_EVIDENCE.txt"'),
    "W21 must preserve the catalog snapshot in its evidence artifact",
  );

});


const w80Workflow = readFileSync(
  join(repoRoot, ".github", "workflows", "zavqera-w80-isolated-pgtap.yml"),
  "utf8",
);

test("W84 default ACL hardening is replayed and explicitly re-applied in disposable PG17", () => {
  assert.ok(
    w80Workflow.includes('cp "${GITHUB_WORKSPACE}/supabase/tests/w84_postgres_function_default_acl_hardening.sql"'),
    "The W80 isolated PG17 workflow must stage the W84 pgTAP test",
  );
  assert.ok(
    w80Workflow.includes('echo "expected_w84_pgtap_assertions=21"'),
    "W80 evidence must pin W84 to its 21-assertion contract",
  );
  assert.ok(w80Workflow.includes("run_pgtap W84_AFTER_CHAIN supabase/tests/w84_postgres_function_default_acl_hardening.sql 21"),
    "W80 must test W84 after full migration replay");
  assert.ok(w80Workflow.includes("w84_idempotent_reapply_exit_code="),
    "W80 must preserve W84 reapplication exit code");
  assert.ok(w80Workflow.includes("run_pgtap W84_AFTER_REAPPLY supabase/tests/w84_postgres_function_default_acl_hardening.sql 21"),
    "W80 must rerun all W84 assertions after reapplication");
  assert.ok(w80Workflow.includes('[ "${w84_status}" -ne 0 ]'),
    "Any W84 test or reapplication failure must fail the isolated workflow");
});

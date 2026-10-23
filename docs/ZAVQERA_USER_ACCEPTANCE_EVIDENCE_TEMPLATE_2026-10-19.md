# ZAVQERA — human user-acceptance evidence capture template

**Status: TEMPLATE ONLY / NO SESSION RECORDED / NOT RELEASE EVIDENCE.**

The launch runbook records historical owner-confirmed PASS labels for T01–T05 but explicitly says detailed session observations were not recorded. This template does not validate or replace those historical labels. It creates a place to capture a new, reproducible session without inventing what T01–T05 mean or claiming a test was run.

## Rules before recording

- Copy each test's title, scenario, acceptance criteria, and steps **verbatim from the owner-approved test script**. The IDs T01–T05 alone do not define the tests; do not infer or recreate their intent from memory.
- Default every new record to **NOT RUN**. Change it only after the described session actually occurs. Missing criteria, missing observations, or missing evidence cannot be marked PASS.
- Use only the owner-approved non-production environment and synthetic/non-sensitive records. Do not create hosted fixtures or perform database writes under this template.
- Never include credentials, access tokens, cookies, session identifiers, unredacted personal data, customer records, or secret-bearing logs. Refer to restricted evidence by an access-controlled artifact identifier and sanitized hash where appropriate.
- Record the exact app/deployment/build identity and UTC times. A result does not transfer to a different candidate SHA or materially different build.
- Keep the accountable owner's acceptance and the independent QA review separate. This template is not an independent review, an authorization to deploy, or a GO decision.

## Session metadata

- Session ID:
- Candidate full Git SHA (40 hex characters):
- App/deployment artifact ID and source SHA:
- Environment and URL (non-production only):
- Test script/source and version or commit:
- Tester role (avoid unnecessary personal data):
- Independent observer, if present:
- Start time UTC:
- End time UTC:
- Browser/device/OS and relevant accessibility configuration:
- Synthetic test-account/data identifiers (non-secret, non-personal):
- Known deviations from the approved procedure:

## Test records

For each test, copy its exact title, steps, and acceptance criterion from the approved source before execution. Record what actually happened, including unexpected behavior; do not rewrite observations to fit the expected result.

### T01

- Exact approved title/scenario:
- Approved acceptance criterion and source reference:
- Preconditions:
- Steps actually performed:
- Expected result (from the approved source):
- Actual observed result (specific, factual):
- Outcome: **NOT RUN** / PASS / FAIL / BLOCKED
- Evidence artifact/reference (sanitized):
- Evidence SHA-256, if a file was retained:
- Related defect/issue:
- Tester and observation time (UTC):
- Rerun/version notes:

### T02

- Exact approved title/scenario:
- Approved acceptance criterion and source reference:
- Preconditions:
- Steps actually performed:
- Expected result (from the approved source):
- Actual observed result (specific, factual):
- Outcome: **NOT RUN** / PASS / FAIL / BLOCKED
- Evidence artifact/reference (sanitized):
- Evidence SHA-256, if a file was retained:
- Related defect/issue:
- Tester and observation time (UTC):
- Rerun/version notes:

### T03

- Exact approved title/scenario:
- Approved acceptance criterion and source reference:
- Preconditions:
- Steps actually performed:
- Expected result (from the approved source):
- Actual observed result (specific, factual):
- Outcome: **NOT RUN** / PASS / FAIL / BLOCKED
- Evidence artifact/reference (sanitized):
- Evidence SHA-256, if a file was retained:
- Related defect/issue:
- Tester and observation time (UTC):
- Rerun/version notes:

### T04

- Exact approved title/scenario:
- Approved acceptance criterion and source reference:
- Preconditions:
- Steps actually performed:
- Expected result (from the approved source):
- Actual observed result (specific, factual):
- Outcome: **NOT RUN** / PASS / FAIL / BLOCKED
- Evidence artifact/reference (sanitized):
- Evidence SHA-256, if a file was retained:
- Related defect/issue:
- Tester and observation time (UTC):
- Rerun/version notes:

### T05

- Exact approved title/scenario:
- Approved acceptance criterion and source reference:
- Preconditions:
- Steps actually performed:
- Expected result (from the approved source):
- Actual observed result (specific, factual):
- Outcome: **NOT RUN** / PASS / FAIL / BLOCKED
- Evidence artifact/reference (sanitized):
- Evidence SHA-256, if a file was retained:
- Related defect/issue:
- Tester and observation time (UTC):
- Rerun/version notes:

## Review and disposition

- Missing/ambiguous test definitions or acceptance criteria:
- Defects and required follow-up:
- Accountable product owner's decision and date (UTC):
- Independent QA reviewer's name/role and conflict statement:
- Independent reviewer findings, evidence references, and date (UTC):
- Final acceptance disposition: **BLOCKED** until all five records have verifiable observations and evidence, required defects are dispositioned, and both owner acceptance and independent review are recorded.

## Release-gate interpretation

This template only improves evidence capture. It does not mean T01–T05 were performed, does not convert historical PASS labels into evidenced acceptance, and cannot close Gate I or the overall launch gate by itself. Keep public production **NO-GO** while any mandatory gate remains open.

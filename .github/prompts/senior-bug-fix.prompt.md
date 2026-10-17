---
description: Apply the assessed remediation, scoped to the assessment's named files, with a deviations log
phase: bug-fix
requires: .senior/bugs/<slug>/assessment.md with verdict valid
produces: .senior/bugs/<slug>/fix.md + code
---

## Arguments

```text
${input:arguments}
```

Resolves `slug=<slug>` from arguments; if absent and exactly one bug directory exists
under `.senior/bugs/`, use it; if several, ask.

## What this stage is

The only stage in the bug path that may edit source. It implements the assessment's
*preferred remediation* — not the assessment author's mood at 2am, not a rewrite. Output:
`.senior/bugs/<slug>/fix.md`.

## Execution steps

1. **Prerequisites**: `assessment.md` must exist with verdict `valid` (or `likely valid`
   with the user's explicit go) and a remediation plan. Missing or invalid → STOP and name
   the missing step (`/senior.bug-assess slug=<slug>`).
2. **Re-baseline**: run the tests around the affected area first and record the state.
   If a test currently covers this area and passes, note it — the fix must not break it.
3. **Reproduce for regression-lock**: before touching code, add the regression test the
   assessment's test plan names (or a minimal one from the reproduction steps), confirm it
   fails against current code — for the right reason. If the environment can't run tests,
   record that in fix.md and proceed with maximal caution (this weakens verification and
   will be reflected in the final verdict).
4. **Implement the fix**:
   - scope: the files named in the assessment. Reaching beyond them requires a reason —
     log it under **Deviations from Assessment** (what + why + how verified). Silent scope
     creep fails this stage.
   - fix the root cause, not the symptom: if the minimal change happens to be symptom-level
     (e.g. a guard papering over a serialization bug), say so explicitly and choose the
     root-cause fix unless there's a written reason not to.
   - apply the senior checks in passing: error path handled, edge inputs considered, no new
     logs/debug debris.
5. **Clean as you go**: no debug prints, no commented-out code, no stray TODOs.
6. **Verify the fix locally**: regression test green; affected tests green; typecheck and
   lint green. Full-suite green for anything non-trivial (state the suite used).
7. **Write `.senior/bugs/<slug>/fix.md`**:

   ```markdown
   # Bug Fix: <slug>

   - **Fixed**: <date> | **Branch/commit**: <where the change lives>

   ## What was wrong

   <one paragraph, root cause per assessment>

   ## What changed

   - `path:area` — <the fix, and why it addresses the root cause>

   ## Deviations from Assessment

   - <scoped additions with rationale, or "none">

   ## Local verification

   - regression test: <name + fail-first confirmed? result>
   - affected suites: <results>
   - typecheck/lint: <results>

   ## Honest limits

   <what was NOT verified end-to-end — deferred to /senior.bug-test>
   ```

8. Report: root cause fixed, files changed (with deviations highlighted), local test
   results, and next step: `/senior.bug-test slug=<slug>`.

## Rules

- Do not "improve" adjacent code. Improvements go to `.senior/backlog.md` unless they are
  required by the root cause.
- Never weaken existing tests to make the fix land; changing an assertion needs a written
  reason in fix.md.
- The fix's commits are conventional and scoped (`fix: <area>: <what went wrong, briefly>`).

## Done When

- [ ] fix.md complete: root cause, changes, deviations, local verification, honest limits
- [ ] Regression test added and confirmed failing first (or deviation recorded)
- [ ] Affected tests + typecheck + lint green
- [ ] Source changes confined to assessment scope (or deviations logged)
- [ ] User told: fix ready, next `/senior.bug-test slug=<slug>`

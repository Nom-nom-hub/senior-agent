---
description: Independently validate the fix against the original symptom; record an honest verdict — verified, partial, or failed
phase: bug-test
requires: .senior/bugs/<slug>/fix.md
produces: .senior/bugs/<slug>/test.md
---

## Arguments

```text
${input:arguments}
```

Resolves `slug=<slug>` like `/senior.bug-fix` (single directory auto-resolves).

## What this stage is

The senior closes the loop: re-run the ORIGINAL reproduction, through the outfit the user
would experience it through, and grade what actually happened. This stage never edits
source code. It exists because "the fix commit exists" is not evidence that the bug is
fixed. Output: `.senior/bugs/<slug>/test.md`.

## Execution steps

1. **Prerequisites**: `fix.md` must exist. Read `assessment.md` + `fix.md` for: original
   reproduction steps, verdict, deviations from assessment, "honest limits" section.
2. **Re-run the original reproduction** — the exact steps/scenario from assessment.md, not
   the fix's own new test. Use the reproduction method closest to the user's experience
   (CLI invocation, real endpoint call, UI flow). Record every command run and the real
   observed output verbatim.
3. **Cross-checks** beyond the symptom:
   - the regression test from the fix fails against the pre-fix code if that can be
     arranged cheaply (revert-in-branch/cherry-pick check) — confirming it locks the bug
     out permanently, not just today;
   - affected tests + typecheck + lint + full suite (report what was run and what was
     skipped, separately);
   - deviations from fix.md get honestly re-checked (each deviation is a place where the
     fix differs from the plan — re-verify those paths specifically).
4. **Write `.senior/bugs/<slug>/test.md`**:

   ```markdown
   # Bug Verification: <slug>

   - **Verified**: <date> | **Verdict**: verified | partial | failed | not-run

   ## Original reproduction (re-run)

   | Step | Expected | Observed | Run? |
   |---|---|---|---|

   <Verbatim commands + output snippets>

   ## Suite results

   - regression test: <name, result>
   - affected tests / full suite / typecheck / lint: <results>

   ## Unverified remainder

   <what could not be exercised (environment gaps, flaky infra, prod-only conditions) and
   how much risk that leaves>

   ## Verdict rationale

   <one paragraph: why graded this way>
   ```

5. **Grade**:
   - `verified`: original reproduction now behaves correctly by the direct method, and all
     locally-runnable suites are green.
   - `partial`: fixed in the paths tested, but some reproduction internals (or deviation
     paths, or environment-dependent steps) were not directly exercised.
   - `failed`: reproduction still misbehaves on any run-through — a `failed` verdict
     routes BACK to `/senior.bug-fix` (or re-assessment if the hypothesis was wrong); it
     never ships with a "passes for now" note.
   - `not-run`: could not execute at all (environment). Unverified ≠ verified. The user
     must be told plainly, with the exact gap preventing the run.

## Rules

- Read-only on source. Writes only in `.senior/bugs/<slug>/`.
- Never manufacture observed outputs; every row is either a real run or an explicit `Run?`
  no-entry with the reason.
- The test stage is independent: its opinion is formed from what it observed, not from what
  fix.md claims.

## Done When

- [ ] test.md written with reproduction table, suite results, unverified remainder
- [ ] Verdict justified against the grading criteria
- [ ] On `failed`: user given an explicit routing decision (re-fix or re-assess)
- [ ] User told the final verdict plainly — including partial and not-run, in so many words

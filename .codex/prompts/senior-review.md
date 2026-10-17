---
description: Adversarially self-review the produced diff as a skeptical staff engineer — every finding must be answered before passing
phase: review
requires: tasks.md complete
produces: review.md
---

## Arguments

```text
$ARGUMENTS
```

You MUST consider the user input before proceeding (if not empty).

## What this stage is

The stage most agents are missing. Once the diff exists, the agent switches seats from
author to **skeptical staff engineer reviewing someone else's PR**, and reviews its own
work with the same hostility it would apply to a stranger's. Output:
`.senior/work/<slug>/review.md`. The review is adversarial: the objective is to find the
sev-1 this work will cause in three months, not to certify it.

## Execution steps

1. **State check**: `senior state --json`. Requires complete `tasks.md`. Get the diff scope:
   `git diff` of the work (staged+unstaged+commits on the work branch, per the state script's
   `diff_base`). If the diff is empty, STOP — nothing to review.
2. **Write `.senior/work/<slug>/review.md`** with sections as findings come in:

   ```markdown
   # Self-Review: <slug>

   - **Created**: <date> | **Diff**: <range summary / +lines/-lines / files touched>

   ## Findings

   | ID | Severity | Area | Finding | Evidence | Verdict |
   |---|---|---|---|---|---|

   ## Fixes applied

   <what changed in response to which finding>

   ## Residual risks accepted

   <explicit list of what is knowingly imperfect and why that is the right call now>
   ```

3. **Review the diff across every pass** (each pass is a separate read-through):
   - **Correctness**: logic errors, off-by-ones, wrong variable use, false assumptions
     about inputs, no-op branches, races, resource/leak lifecycle (connections, handles,
     files, listeners).
   - **Edge & failure paths**: empty input, max input, malformed input, concurrent access,
     network/storage failures, timeouts, retries — does the code behave as design.md's
     edge-case table promised? Any designed failure mode unimplemented is a finding.
   - **Error handling**: errors swallowed, logged-but-ignored, or reported with a message
     users can't act on. Wrong exception types. Missing cleanup on error paths.
   - **Security**: injection surfaces, over-broad permissions, secrets in logs/code,
     unsafe deserialization, path traversal, CSRF/authz gaps, dependency risk in any new
     package.
   - **Performance**: accidental O(n²), N+1 queries, unbounded memory, hot-path logging,
     serial awaits that could parallelize. Uncertain → measure; "probably fine" is not a
     review verdict.
   - **API/design shape**: does the interface match the codebase's established patterns?
     Naming consistent with neighbors? Leaky internals? Uniformity-vs-novelty checked
     against `.senior/principles.md`.
   - **Test honesty**: coverage gaps against each acceptance scenario, assertions too weak
     (checking no-crash instead of behavior), tests coupled to implementation detail.
   - **The diff could be smaller**: dead code, comment leftovers, over-generalization,
     "while I was here" creep — trim it.
4. **Severity scale**: CRITICAL (would break in production or security issue) / HIGH
   (correct behavior at risk in a realistic scenario) / MEDIUM (maintainability, small
   behavior gaps) / LOW (style-adjacent). Honest bar: a finding you'd leave as an
   approving comment if you wrote it later is LOW; you are reviewing a stranger's PR.
5. **Act, don't annotate**: CRITICAL and HIGH findings are fixed in code and re-verified
   (affected tests re-run) before this stage can pass. MEDIUM/LOW are fixed or explicitly
   moved to "Residual risks accepted" with a one-line reason. Findings named in the table
   but left unaddressed with no row under "Residual risks accepted" fail the stage.
6. **Re-review the fixes**: any fix you made gets at least one pass of the same scrutiny —
   fixes regularly introduce their own bugs. Then final full suite + typecheck + lint run.
7. Report: findings table, fixes applied, residual risks, and next command
   `/senior.verify <slug>`.

## Rules

- The reviewer persona outranks the author persona: if the author disagrees with the
  reviewer, the disagreement is written as an explicit residual risk, not resolved by
  silently ignoring the finding.
- No code changes outside the diff's declared scope (new findings needing scope expansion
  are logged as backlog entries unless they're CRITICAL fixes to this work).

## Done When

- [ ] review.md written with findings across all eight passes
- [ ] All CRITICAL/HIGH findings fixed and re-verified
- [ ] Nothing sits as an unresolved row in the findings table
- [ ] At least one fix got re-reviewed
- [ ] Final full suite + typecheck + lint green (or honestly blocked with reason)
- [ ] User told: stage complete, next `/senior.verify <slug>`

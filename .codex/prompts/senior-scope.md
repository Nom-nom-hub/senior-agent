---
description: Size the work, define the smallest shippable slice, name risks and rollback — before any design
phase: scope
requires: recon.md
produces: scope.md
---

## Arguments

```text
$ARGUMENTS
```

You MUST consider the user input before proceeding (if not empty).

## What this stage is

Senior devs don't implement asks; they implement *the smallest thing that delivers the
value*. This stage reads `recon.md` and the ask, decides what is actually in scope, sizes
it honestly, and names what could go wrong. Output: `.senior/work/<slug>/scope.md`.

## Thinking like the senior

- Split the ask into the problem worth solving and everything it could grow into. Only the
  former is in scope; the latter is listed and parked.
- Size in terms the user can act on: **walk** (< 1 focused session), **t-shirt** (1–3
  sessions), **bag** (needs decomposition into multiple slices). If it's a bag, do NOT
  swallow it: split into slices and select slice 1.
- Every scope has a rollback story: "this is how we undo it" must exist before code does.

## Execution steps

1. **State check**: `senior state --json`. Requires `WORK_DIR/recon.md` to exist and be
   complete; if missing, STOP and name `/senior.recon` as the prerequisite command.
2. **Extract the problem statement**: one paragraph: for whom, what value, what does
   "done" mean in user-visible behavior.
3. **Candidate approaches**: from recon's candidates + your judgment, sketch 2–3 approaches
   and pick one with a one-paragraph trade-off rationale (chosen vs rejected). Bias hard
   toward the simplest approach that fully satisfies the P1 slice. If the chosen approach
   adds an abstraction, new dependency, or new component beyond the obvious, that must be
   justified here — "we might need it later" is not a justification.
4. **Slice & prioritize**: split work into independently shippable slices; assign P1 / P2 /
   P3. Define P1 as the smallest increment that delivers real value end-to-end.
5. **Estimate honestly**: sessions × area (backend / frontend / data / pipeline), flag
   which parts are unpredictable and why. Uncertainty is stated, not hidden.
6. **Risks & rollback**: table of risks with likelihood × impact and mitigations; write the
   rollback plan (revert boundary, data compatibility, feature flag if applicable).
7. **Scope boundaries**: explicit "Out of scope" list — including things a lesser agent
   would sneak in (refactors, framework swaps, "while we're here" fixes). If adjacent work
   is genuinely needed, record it in `.senior/backlog.md` instead of expanding this scope.
8. **Write `.senior/work/<slug>/scope.md`**:

   ```markdown
   # Scope: <slug>

   - **Created**: <date> | **Size**: walk | t-shirt | bag → sliced

   ## Problem statement

   <paragraph>

   ## Approach

   **Chosen**: <approach + what makes it smallest-that-delivers-p1>
   **Rejected alternatives**: <each + why>
   **Complexity justifications**: <none | table: addition → why simpler alternative fails>

   ## Slices

   | Slice | Priority | Description | Size | Depends on |
   |---|---|---|---|---|

   ## Risks

   | Risk | L×I | Mitigation |
   |---|---|---|

   ## Rollback plan

   <how to fully undo this work at any point>

   ## Out of scope

   - <explicitly not doing, and parked-where>
   ```

## Rules

- Git operations allowed: read-only (log/blame/diff scouting). No code changes.
- If the problem statement can't be written without guessing at user intent, that is a
  finding: write it into scope.md as `[NEEDS CLARIFICATION: …]` and list it as the first
  question for `/senior.decide`.

## Done When

- [ ] scope.md written, all sections filled
- [ ] One approach chosen with a written trade-off rationale
- [ ] P1 slice is defined as an independently shippable increment
- [ ] Rollback plan exists and is executable without heroics
- [ ] Out-of-scope list is explicit (empty list must be justified, not asserted)
- [ ] User told: stage complete, next command `/senior.decide <slug>`

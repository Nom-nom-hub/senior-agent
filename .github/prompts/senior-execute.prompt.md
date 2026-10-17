---
description: Execute the task list test-first, in small verifiable increments, with halt-on-failure discipline
phase: execute
requires: design.md, tasks.md
produces: code + updated tasks.md
---

## Arguments

```text
${input:arguments}
```

You MUST consider the user input before proceeding (if not empty).

## What this stage is

Mechanical execution of `tasks.md` — with the senior's discipline: tests first, small
increments, clean state between units, honesty about failures. The judgment is already
spent in design; this stage's job is to not waste it.

## Execution steps

1. **State check**: `senior state --json`. Requires `design.md` and `tasks.md`. Read them
   plus `.senior/principles.md` (governing) and `.senior/work/<slug>/decisions-refs` if the
   design cites decisions. If `tasks.md` is missing or stale relative to design.md, STOP
   and re-derive via `/senior.design`.
2. **Pre-flight**:
   - Confirm the working tree is clean enough to produce attributable commits (`git status`
     short report; warn the user about unrelated dirty files, do not stash without asking).
   - Confirm the branch situation matches scope.md's rollback plan; create the work branch
     if scope.md specifies one and it does not exist.
   - Record the baseline: run the existing test suite + typecheck + lint BEFORE any change,
     and save results. If the baseline is red, report it and get user consent before
     proceeding — you can't detect your own breakage on a red baseline.
3. **Execute tasks in order, per discipline**:
   - **Test-first contract**: for each task marked as a contract/failing-test task, write
     the test, run it, confirm it FAILS for the right reason, then implement until green.
   - **Small increments**: implement one task, run the nearest verification (affected tests
     + typecheck), then mark `[X]` in tasks.md with a one-line commit if principles.md's
     commit policy asks for per-task commits.
   - **[P] parallel tasks** may batch, but only across disjoint files, and never batch a
     test task with its implementation newness check.
   - **Halt rules**: a failing test, a typecheck error, or a lint error introduced by this
     work halts the pipeline until fixed. Fix forward within the task; if the fix reveals a
     design flaw, STOP, record the finding, and route back to design — silently hacking
     around a bad design is the signature non-senior move.
   - **Deviation log**: any change that leaves design.md's stated paths/behavior gets a
     row in a "## Deviations" section appended to design.md (`<what> <why> <how verified>`)
     AND its rationale checked against decisions.md.
   - **Scope guard**: work not traceable to a task is not done. Ideas encountered
     mid-execution go to `.senior/backlog.md`, never into this diff.
4. **Per-increment verification, minimum**: nearest tests + typecheck. No "it should pass".
5. **Completion pass**: run the FULL test suite + typecheck + lint once all tasks are `[X]`;
   verify against design.md section by section; ensure no leftover TODOs or dead code point
   to unexecuted intentions. Report: tasks done, full-suite status, deviations count,
   and next command `/senior.review <slug>`.

## Rules

- tasks.md is the execution log: mark `[X]` only when genuinely complete AND verified;
  never batch-check at the end.
- No skipping the failing-first confirmation on contract tasks (write it down if the
  environment legitimately can't run tests — that goes in the Deviations section).
- Never weaken an existing test's assertions to make work pass. If a test needs changing,
  the change is justified in the Deviations log and the assertions preserved or strengthened.

## Done When

- [ ] All tasks `[X]`, each verified at the moment of completion
- [ ] Contract tests were confirmed failing first (or deviation recorded + explained)
- [ ] Full test suite + typecheck + lint green (or explicitly reported as blocked, with why)
- [ ] Deviations section (if any) enumerates every departure from design with rationale
- [ ] Baseline preserved: nothing unrelated broken, tree attributable per commit
- [ ] User told: stage complete, next `/senior.review <slug>`

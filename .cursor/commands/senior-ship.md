---
description: Ship it — conventional commits that tell the story, changelog, PR description with the why, handoff notes and open items
phase: ship
requires: verify.md verdict verified or partial-per user
produces: ship.md + git history + changelog
---

## Arguments

```text
$ARGUMENTS
```

You MUST consider the user input before proceeding (if not empty).

## What this stage is

The work is verified; now make it land in a form the team can trust: history that reads,
PR that argues, notes that hand off. A senior's last mile is as engineered as the first
mile. Output: `.senior/work/<slug>/ship.md` plus the actual commits/changelog/PR.

## Execution steps

1. **State check**: `senior state --json`. Requires `verify.md` with overall verdict
   `verified`. A `partial` verdict ships only with the user's explicit go (ask, show the
   table of what's unverified). Any `failed`/`blocked` row on P1 → STOP, ship is off the
   table until fixed.
2. **Pre-ship sweep** (small, real checks — not vibes):
   - tree clean of debris: no debug prints, commented-out blocks, stray logs, heartwarming
     TODOs that shouldn't ship
   - `.gitignore` covers what must never land (artifacts of this tool are project-owned:
     `.senior/` stays untracked unless the user says otherwise)
   - versioning/docs: apply the project's convention for bumping, `docs/`, `CHANGELOG.md`
     entry drafted as a real changelog sentence (why it matters, not "misc fixes")
   - principles.md's shipping gates (if any) re-confirmed done
3. **Commit plan**: split the diff into logical units (setup, contracts+tests, feature
   work, integration, polish/docs). Story-check: `git log` proposed order should read as a
   coherent feature narrative where any single commit is individually sane. Conventional
   commits (`feat:|fix:|refactor:|docs:|test:|chore:`), scopes matching the repo's existing
   style (`git log --oneline -20` is the style guide). Each commit message explains WHY,
   one line. Batch staging so `git status` never shows stray files invited into the commit.
4. **PR body** (skip if the project's flow is local-only; user steer accepted):

   ```markdown
   ## Why

   <the problem in a sentence a stakeholder can read, from scope.md>

   ## What

   <bullets of actual behavior changes — concrete, no abstraction soup>

   ## How tested

   - Conformance to design: <summary>
   - Self-review: findings fixed, residual risks accepted: <list>
   - End-to-end verification: <row summary from verify.md + re-run instructions>
   ```

   Risk notes (migrations, flags, rollout order) required if applicable. No boilerplate
   checklist filler; every line should carry information.
5. **Write `.senior/work/<slug>/ship.md`** (the handoff artifact):

   ```markdown
   # Shipment: <slug>

   - **Date**: … | **PR**: <link or "local only"> | **Verdict shipped under**: verified / partial(user-approved)

   ## Commits

   <hash + subject per commit in the story order>

   ## Changelog entry

   <text>

   ## Handoff notes

   - <anything unusual a maintainer should know: deviations accepted, gotchas, decisions
     pointers (.senior/decisions.md D-NNNs), docs touched>

   ## Open items

   - <backlog entries created during this work, each with its reason and pointer>
   ```

6. **Report**: commit list, PR link (if any), handoff-artifact pointer, and the work's
   closing status. If discrepancies between the plan and what got built exist, the report
   names them plainly — shipping silently different than designed is forbidden.

## Rules

- Push/PR creation only when the user has authorized it this session or principles.md says
  so; local commits + prepared body otherwise (print the exact push/PR command for them).
- Never rewrite history that others may have based on; amend/rebase only unpushed work.
- changelog/PR wording must match verify.md's reality: partial items are named partial
  there too.

## Done When

- [ ] Pre-ship sweep passed (debris, ignore files, changelog draft, checks)
- [ ] Commits structured per plan, conventional, each individually sane
- [ ] PR body (or local-ship report) written with real content
- [ ] ship.md handoff artifact complete with open items
- [ ] User told: shipped, links, and where the knowledge lives

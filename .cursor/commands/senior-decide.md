---
description: Resolve ambiguity like a senior — ask only what cannot be decided, document the rest as decisions with rationale
phase: decide
requires: scope.md
produces: decisions.md (appended)
---

## Arguments

```text
$ARGUMENTS
```

You MUST consider the user input before proceeding (if not empty).

## What this stage is

The senior habit this stage exists for: **secretaries ask questions; senior devs make
decisions and document them**. A user should never be asked things a senior dev would know
to decide alone. This stage sweeps recon + scope for open questions and `[NEEDS
CLARIFICATION]` markers, then disposes of each one in exactly one of two ways:

1. **Decide** it (default), and append a decision record to `.senior/decisions.md`;
2. **Ask** the user — only if the question is high-impact (materially changes architecture,
   data model, task breakdown, test design, UX behavior, ops readiness, or compliance) AND
   genuinely undecidable from context.

Output: updated `.senior/decisions.md` (appended, never rewritten) and a decisions summary
in chat.

## Execution steps

1. **State check**: `senior state --json`. Requires `WORK_DIR/scope.md`.
2. **Collect open items**: scan `recon.md` + `scope.md` for every `[NEEDS CLARIFICATION]`
   marker, flagged assumption, and ambiguity you can still detect by rereading the ask.
   Build an internal list; do not dump it on the user.
3. **Decide everything you can, first**. For each item, decide using: this project's
   principles (`.senior/principles.md`), strongest existing convention in the codebase,
   simplest-thing-that-satisfies-the-P1-slice, and standard practice for this stack.
   For each decided item append to `.senior/decisions.md`:

   ```markdown
   ### D-NNN: <imperative decision title> (<date>, <slug>)

   - **Decision**: <what was decided, one sentence>
   - **Rationale**: <why, including evidence/prior art>
   - **Considered and rejected**: <the obvious alternative(s) and why not>
   - **Consequence**: <what this makes easier; what it forecloses>
   ```

4. **Filter before asking**: would the answer change what gets built, alter the data model,
   break a contract, or force rework of acceptance tests? If no → it was not a question;
   decide it (step 3). If yes → it is a candidate question. Hard cap: **5 questions**,
   ranked by impact × uncertainty; drop low-impact ones even if real.
5. **Ask one question at a time** and wait for the answer before the next. Question
   quality rules:
   - Lead with `**Question:**` + a full interrogative ending in `?`.
   - One sentence "Why it matters" right after.
   - Prefer 2–5 mutually exclusive multiple-choice options; state your recommended option
     and why, so a busy user can just say "recommended".
6. **Encode answers**: each user answer is recorded as a `D-NNN` decision with
   `Decider: user` in the rationale, and the corresponding `[NEEDS CLARIFICATION]` markers
   in recon.md/scope.md are replaced with the resolved statement (edit those artifacts;
   this is the one allowed modification of them, replacing markers only).
7. **Report**: print the decisions summary table (ID, title, decider: me/user) and list any
   decisions that preempt future stages.

## Rules

- `.senior/decisions.md` is append-only: never edit or delete past decisions.
- Asking zero questions and deciding everything is a GOOD outcome when the calls were
  reasonable and documented; asking five questions is a warning sign you skipped step 3.
- If the user overrides a project principle, record it verbatim as a user decision, do not
  silently comply.

## Done When

- [ ] Zero un-disposed `[NEEDS CLARIFICATION]` markers remain in the work's artifacts
- [ ] Every decided item has a D-NNN record with rationale and rejected alternatives
- [ ] User answered ≤5 questions, one at a time, each with a stated recommendation
- [ ] decisions.md remains valid append-only history
- [ ] User told: stage complete, next command `/senior.design <slug>`

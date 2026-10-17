---
description: Produce the spec — data model, contracts, edge cases, failure modes, test scenarios, and a task list a senior could execute blindfolded
phase: design
requires: scope.md, decisions.md current
produces: design.md, tasks.md
---

## Arguments

```text
${input:arguments}
```

You MUST consider the user input before proceeding (if not empty).

## What this stage is

Turn the scope into a build-ready design: precise enough that implementation is mechanical,
small enough to stay readable. Two artifacts: `.senior/work/<slug>/design.md` and
`.senior/work/<slug>/tasks.md`. This stage does not write application code.

## Thinking like the senior

- The design's job is to keep the implementer from making decisions mid-code. Every choice
  left open here becomes drift there.
- Edge cases and failure modes are design content, not "polish". A senior designs for the
  bad path first: empty, too big, concurrent, offline, malformed.
- YAGNI is enforced, not vibes: any component, abstraction, or dependency that doesn't serve
  the P1 slice must be justified in writing or removed.

## Execution steps

1. **State check**: `senior state --json`. Requires `scope.md` + no unresolved
   `D-…/NEEDS CLARIFICATION` items (the state script reports `decisions_pending`).
2. **Write `design.md`**:

   ```markdown
   # Design: <slug>

   - **Created**: <date> | **Spec source**: scope.md + decisions.md

   ## Behavior spec

   <per slice: user-visible behavior as Given/When/Then acceptance scenarios>

   ## Data model

   - <entity>: fields, types, constraints, uniqueness, lifecycle states
   - <migrations / compatibility notes if touching existing data>

   ## Interfaces & contracts

   - <each exposed interface: API/endpoint/CLI/UI contract with request/response shapes,
     error responses, and versioning stance> (skip section if internal-only work)

   ## Edge cases & failure modes

   | Trigger | Expected behavior | How the spec guarantees it |
   |---|---|---|

   ## Test scenarios (behavior-linked)

   - <test scenario per acceptance criterion; note contract vs integration vs unit>

   ## Guards

   - **Simplicity**: components added: <list or none> — justification table ONLY if >0
   - **Anti-abstraction**: direct framework use where possible: <yes/no + note>
   - **Dependency additions**: <none approved / list + one-line each>
   - **Complexity register**: <violations, each with "simpler alternative rejected because">
   ```

   Rules: keep design.md high-level and readable; push detail (schemas, protocol tables)
   into clearly named subsections rather than prose walls. No code bodies — contract
   shapes only.
3. **Derive `tasks.md`** from design.md. Strict format — every task:

   ```text
   - [ ] T<NNN> [P?] [Slice?] <imperative action with exact file path(s)>
   ```

   - `[P]` only where tasks touch disjoint files with no dependency on unfinished tasks.
   - Order: foundational/shared → contract & failing tests → implementation → integration →
     polish. **Tests come before the code that satisfies them** in task order.
   - Group by slice (P1 first). Each slice's tasks must be independently testable.
   - Constraints from design (validation rules, error shapes) are quoted verbatim into the
     task text so nothing is left to implementation-time discretion.
   - Final section: polish/cross-cutting (docs, changelog entry placeholder, cleanup of
     anything the work makes dead).
4. **Cross-check**: every acceptance scenario maps to ≥1 test task AND ≥1 implementation
   task; every task traces to a design element (`(per B-x / FR-x)`) — tasks that trace to
   nothing get deleted.
5. Report: design summary, guard verdict (violations listed in the complexity register),
   task count + slice breakdown, and next command `/senior.execute <slug>`.

## Rules

- If a needed decision does not exist in `.senior/decisions.md`, STOP and route back to
  `/senior.decide` rather than inventing one mid-design.
- Over-engineering caught in self-check (abstract factory for one implementation, config
  layer for two values, "future" options) must be removed, not flagged and kept.

## Done When

- [ ] design.md complete: behavior, data, interfaces, edge cases, test scenarios, guards
- [ ] Complexity register empty or every row justified against a named simpler alternative
- [ ] tasks.md follows the strict checklist format with traced, ordered tasks
- [ ] Tests ordered before implementation for every behavior
- [ ] User told: stage complete, next `/senior.execute <slug>`

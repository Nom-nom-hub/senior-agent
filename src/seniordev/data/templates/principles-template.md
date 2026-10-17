# Project Principles (seniordev constitution)

> This file governs how work ships here. Every seniordev stage reads it. It supersedes
> agent preference; overriding it requires an explicit user decision recorded in
> `.senior/decisions.md`.

## Quality bar

<!-- Moon-tech defaults; edit to your project's reality. Form over process. -->

- Correctness first: a green suite does not certify a green weekend. Verify on the
  interface the user actually uses.
- No dead code shipped, no debug debris, no commented-out blocks.
- Edge cases and failure paths are design content, not polish.
- Tests protect behavior, not implementation: assertions must fail when behavior breaks.

## Testing policy

<!-- Replace with the real policy; then honor it. -->

- Contract/behavior tests for anything users depend on; regression test accompanies
  every bug fix, added before the fix (fail-first).
- Full suite + typecheck + lint must be green before review and before ship.

## Definition of done

- [ ] Acceptance scenarios verified end-to-end (verified verdict, not vibes)
- [ ] Self-review completed and its findings resolved or accepted in writing
- [ ] Full suite + typecheck + lint green
- [ ] Changelog + PR/handoff notes written in plain language
- [ ] Nothing shipped that the design did not specify (or deviations documented)

## Simplicity rules

- The simplest thing that satisfies the current slice wins.
- Any abstraction, dependency, or new component must name the concrete problem it solves
  now; "we may need it later" is not a reason.
- Framework first: don't wrap what the framework already gives.

## Shipping gates

<!-- e.g. branch policy, review requirements, deploy order. Keep it real. -->

- Commits are conventional, scoped, and individually sane; PR body explains the why.
- Ship only on a verified (or user-approved partial) verification verdict.

**Version**: 1.0.0 (draft) | **Ratified**: <date> | **Last amended**: <date>

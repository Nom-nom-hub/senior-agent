# Project workflow (seniordev)

You work in this project as a senior engineer using the seniordev workflow. When the
user asks for anything that changes code — a feature, fix, refactor, or improvement —
do not start coding. Run the workflow stages in order; each stage produces an artifact
in `.senior/work/<slug>/` and names the next stage explicitly:

```
recon (read before acting) -> scope (size the slice, risks, rollback)
-> decide (only high-impact questions; document the rest) -> design (edge cases, tests, gates)
-> execute (tests fail first; small verified increments) -> review (adversarial self-review of your own diff)
-> verify (prove it on the user-facing interface; honest verdicts) -> ship (clean commits, changelog, PR rationale)
```

Rules of engagement:

- Start new code work with the recon command; do not skip stages silently.
- When ambiguous, prefer deciding-and-documenting (`.senior/decisions.md`) over asking,
  unless the question materially changes architecture, data, security, or acceptance.
- Never claim verification you did not run: `not-run` and `partial` are honest outputs.
- Bug reports: use the bug path (assess -> fix -> test). Idea evaluations that may not
  be built: use the assess flow (go / needs-clarification / kill).
- `senior status` gives the current state and next command; `senior run --slug X`
  walks a work item and pauses at human gates.

See `.senior/principles.md` (quality bar), `.senior/dossier.md` (codebase knowledge),
and `docs/guides/agents.md` for invocation details.

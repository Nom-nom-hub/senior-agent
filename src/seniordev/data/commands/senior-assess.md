---
description: Evaluate whether an idea deserves work before creating any work — evidence-backed go / needs-clarification / kill decision
phase: pre-work
produces: .senior/assessments/<slug>/assessment.md
---

## Arguments

```text
$ARGUMENTS
```

The input is an idea description (any size) and optionally `slug=<slug>`.

## What this stage is

Ideas are cheap; misinvested engineering is not. This stage gathers evidence about an
idea *before* a work slug exists — codebase fit, prior art, blast radius, unknowns —
and issues exactly one verdict: **`go`** (worth building), **`needs-clarification`**
(only named open questions stand between you and a go), or **`kill`** (with a written
reason that stands without you). Killing an idea cleanly is a success, not a failure of
ambition. Output: `.senior/assessments/<slug>/assessment.md`. No code is written.

## Execution steps

1. **Slug resolution**: explicit `slug=` wins; else derive 2–4 kebab-case words from
   the idea. If `.senior/assessments/<slug>/` exists, ask for a new slug in interactive
   use; in automated use append `-2`, `-3`… Never overwrite an existing assessment.
2. **Restate the idea** honestly in one sentence, then decompose: what it claims, what
   it implies, what it silently assumes (mark each assumption `[NEEDS CLARIFICATION]`
   rather than silently building on it).
3. **Gather evidence** (read-only):
   - **Fit**: does anything in the codebase already do this, partially or adjacent?
     (search concepts, docs, `.senior/backlog.md` for parked related items)
   - **Cost shape**: sketch, in sessions (walk / t-shirt / bag), what building the
     smallest valuable version would take — backend / frontend / data / infra split.
   - **Constraints**: does `.senior/principles.md` or the dossier rule anything out
     (technology, security posture, simplicity rules)?
   - **Users**: who benefits, how do we know they want it (evidence, not assertion)?
4. **Pressure-test**: state the strongest argument AGAINST doing this idea. Steelman
   the kill case before the go case; a verdict that never heard the other side is not
   an assessment.
5. **Decide** on the evidence:
   - `go` — fit is real, cost is acceptable, no load-bearing unknowns.
   - `needs-clarification` — the idea stands only if named questions get answers;
     list the questions (each answerable short — like the decide stage's rules) that
     block the decision, and nothing else.
   - `kill` — no fit, no users, cheaper alternative exists, or it contradicts the
     principles. Write the reason plainly; record a D-NNN decision in
     `.senior/decisions.md` so a future conversation doesn't re-litigate it.
6. **Write assessment.md** into `.senior/assessments/<slug>/`:

   ```markdown
   # Idea Assessment: <title>

   - **Assessed**: <date> | **Decision**: go | needs-clarification | kill

   ## The idea (restated + decomposition)

   <one sentence + implied/silent assumptions>

   ## Evidence

   - Fit: <prior art / adjacent work / `[NEEDS CLARIFICATION: …]` markers>
   - Cost: <smallest valuable version + size + area split>
   - Constraints: <principles/dossier influences>
   - Users: <who + what proportion + why>

   ## The case against (steelmanned)

   <strongest kill argument>

   ## Open questions blocking the verdict

   <numbered, each short-answerable; state which resolution flips the decision>

   ## Next step

   - go → run `/senior-recon slug=<slug>` to start real work
   - needs-clarification → answer the listed questions, then re-assess
   - kill → stopped, decision recorded in .senior/decisions.md (D-NNN)
   ```

7. **Report**: the verdict, the strongest opposing argument you heard, and next step.

## Rules

- Read-only on source; writes only inside `.senior/assessments/<slug>/` (+ the D-NNN
  append for kill decisions).
- Spending hours to save days is the point — but an honest `needs-clarification`
  after focused evidence beats exhaustive research theater.
- The user's enthusiasm is evidence of DEMAND only if users other than them exist;
  name that distinction explicitly when relevant.

## Done When

- [ ] assessment.md exists with exactly one decision, evidence-cited
- [ ] The case-against section steelmans the kill argument
- [ ] needs-clarification verdicts list only decision-blocking questions
- [ ] kill verdicts have a recorded D-NNN in .senior/decisions.md
- [ ] User told the verdict + next step + strongest opposing argument

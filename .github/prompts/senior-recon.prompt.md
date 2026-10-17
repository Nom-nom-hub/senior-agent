---
description: Investigate before acting — build a credibility-checked understanding of the work, the codebase, and the risks
phase: recon
produces: recon.md
---

## Arguments

```text
${input:arguments}
```

You MUST consider the user input before proceeding (if not empty).

## What this stage is

A junior starts coding. A senior starts reading. This stage turns a one-line ask into a
*credible understanding* of: what the user probably actually means, what exists in the
codebase today, where the real work will be, and what will bite. It writes exactly one
artifact: `.senior/work/<slug>/recon.md`. It MUST NOT write application code, fix anything,
or move on to solutions — that discipline belongs to later stages.

## Thinking like the senior

- Assume the stated problem is a symptom until evidence says otherwise.
- Assumptions are not knowledge: anything you cannot show in the codebase is written down
  as an assumption or a `[NEEDS CLARIFICATION: …]` marker — never silently believed.
- The best result of recon is sometimes "the user's framing is wrong, here is the actual
  issue." Surfacing that now is the cheapest win available.

## Execution steps

1. **State check**: run `senior state --json` (fallback: `python -m seniordev state --json`).
   Parse `SLUG` and `WORK_DIR`. If no slug is given, derive a short kebab-case one from the
   ask and use it consistently everywhere. Create `WORK_DIR/recon.md` fresh; refuse to
   silently overwrite a non-empty existing `recon.md` (ask the user first).
2. **Break down the ask**: restate the request in one sentence, then list what it implies
   and what it does NOT cover. Distinguish: asked / implied / not asked / assumed.
3. **Investigate the codebase** until you can answer, with file-level pointers:
   - Where does the relevant behavior live today? (search symbols, strings, routes, schemas)
   - What conventions does this project follow? (naming, layering, error handling, test
     style — read real examples, not guesses; cite them)
   - Are there docs/READMEs/AGENTS/CONTRIBUTING files that constrain how it wants work done?
     (If they exist, they are governing: note their requirements verbatim.)
   - Git history of the affected areas: recent fixes, revert churn, authors' patterns.
   - Prior art: was this tried, partially built, discussed in TODOs or issues?
4. **Check the user's framing**: is the described symptom consistent with what the code can
   do? If the framing looks wrong (e.g., "the bug" is actually expected behavior, or the ask
   duplicates an existing feature), SAY SO in `recon.md` under "Framing assessment".
5. **Write `.senior/work/<slug>/recon.md`** exactly in this structure:

   ```markdown
   # Recon: <slug>

   - **Created**: <ISO date> | **Status**: complete | partial

   ## The ask (restated)

   <one sentence + what it implies / does not cover>

   ## How it works today

   - `path/to/file.ext` — <what it does, why it matters>
   - <entry points, data flow in 3–6 bullets>

   ## Conventions this work must follow

   - <convention> — evidence: `<example file:line>`

   ## Framing assessment

   - <Does the user's framing hold? If not, what is the real issue?>
   - Prior art: <existing feature / recent commits / TODOs relevant here>

   ## Risks & unknowns

   | Risk / unknown | Impact | Evidence or [NEEDS CLARIFICATION: …] |
   |---|---|---|

   ## Handoff to scope

   - <the 2–4 things the next stage must size and decide>
   ```

6. Nothing in recon may be marked `complete` if any **load-bearing** unknown (one that
   changes what gets built) is still marked `[NEEDS CLARIFICATION]` and reasonably
   answerable by looking harder. Look harder first; ask next.

## Rules

- READ-ONLY on source. Writes only inside `.senior/work/<slug>/`.
- Every factual claim in recon.md cites evidence (`file:line`) — claims without evidence
  must be demoted to explicit assumptions instead.
- Do not propose solutions here; capture them only as one-line "candidate approaches" for
  the scope stage to evaluate.

## Done When

- [ ] recon.md written with all six sections filled
- [ ] Conventions section cites at least 2 real files from this codebase
- [ ] Every claim has evidence or is marked as assumption / `[NEEDS CLARIFICATION]`
- [ ] Framing assessment gives an explicit verdict on the user's framing
- [ ] User told: stage complete, and `/senior.scope <slug>` is the next command

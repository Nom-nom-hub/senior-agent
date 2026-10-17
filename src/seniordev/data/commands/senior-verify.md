---
description: Prove the work on the interface a real user would touch, with honest evidence-graded verdicts
phase: verify
requires: review.md complete
produces: verify.md
---

## Arguments

```text
$ARGUMENTS
```

You MUST consider the user input before proceeding (if not empty).

## What this stage is

"Tests pass" is not proof the feature works. This stage exercises the change end-to-end
through the interface the actual user would use — the CLI command, the HTTP call, the UI
flow, the library API — and records evidence that can be checked later. Output:
`.senior/work/<slug>/verify.md`. The cardinal rule comes from the senior ethics:
**an assertion you did not actually run is `not-run`, not `verified`.**

## Execution steps

1. **State check**: `senior state --json`. Requires `review.md` complete. Read design.md's
   acceptance scenarios + test scenarios to build the verification checklist — every
   P1 acceptance scenario is a row; P2/P3 may be limited to smoke-level unless user asks.
2. **Build the verification plan**: for each scenario, identify:
   - the **user-level way to trigger it** (real command invocation, real endpoint call via
     an actual server/client, real UI interaction, real import+call of the library — chosen
     by how the project is consumed, never "I called the function in a REPL" if users use
     the CLI);
   - the **expected observable** (output, response, state change, side effect);
   - whether it can be run in the current environment at all (DB up? network allowed?
     secrets available?). Environment gaps are reported as `blocked`, never papered over.
3. **Execute**: actually run it. Capture the real outputs verbatim (command lines run,
   response bodies/snippets, screenshots where UI, log lines relevant). Where automation is
   possible, prefer an automated script saved to `.senior/work/<slug>/verify.sh` (or
   `.py`), so verification is re-runnable.
4. **Write `.senior/work/<slug>/verify.md`**:

   ```markdown
   # Verification: <slug>

   - **Created**: <date> | **Overall verdict**: verified | partial | blocked

   | Scenario | Method | Expected | Observed | Verdict |
   |---|---|---|---|---|
   | (per design acceptance scenario ID) | run-outside-in (cli/endpoint/script) | … | real output | verified / partial / failed / blocked / not-run |

   ## Evidence

   - Commands/scripts executed (verbatim)
   - Captured outputs (trimmed to what matters)
   - Re-run instructions: <how to reproduce any row>

   ## Environment gaps

   <anything that could not be exercised in this environment, and its impact on the verdict>
   ```

5. **Grade honestly, per row**:
   - `verified` — scenario executed by the exact means stated, observed behavior matched.
   - `partial` — the core path ran, coverage of the scenario was incomplete (edges stubbed,
     mocked where real is required, timing partially checked). Migrating complexity away
     from the described scenario requires this verdict.
   - `failed` — executed and mismatched. A `failed` row → stop pipeline: debug or route
     back to review; `failed` never "passes for now".
   - `blocked` / `not-run` — could not execute / did not execute. State why plainly. These
     do not fail the pipeline but cap the overall verdict at `partial` at best.
6. **Overall verdict**: `verified` only if every P1 acceptance scenario row is `verified`
   via a non-stubbed method and no `failed` rows exist anywhere. `partial` otherwise.
   `blocked` if everything material is blocked. The verdict line and the table must agree —
   an overall `verified` with a `partial` row inside it is invalid output.
7. Report: verdict table, evidence highlights, environment gaps, and next command:
   on `verified` → `/senior.ship <slug>`; else what is missing and who decides.

## Rules

- Never fabricate outputs. If you didn't run it, the row says `not-run` with the reason.
- No new behavior changes in this stage (that's review's job); fixes found here loop back
  via `/senior.review` rather than being patched silently.
- A re-run that flips a verdict supersedes the old one: append the re-run row, never edit
  history rows.

## Done When

- [ ] Every P1 acceptance scenario has a row with a real method and real observation
- [ ] Overall verdict consistent with row verdicts
- [ ] Evidence verbatim captured + re-run instructions present
- [ ] No code changed inside the verify stage
- [ ] User told: verdict + next command (`/senior.ship` or what's missing)

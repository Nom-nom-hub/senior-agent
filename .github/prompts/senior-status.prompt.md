---
description: Dashboard — read current workflow state and tell the user exactly what exists, what's missing, and the next command to run
phase: meta
---

## Arguments

```text
${input:arguments}
```

## What this stage is

The router a senior team lead would run every morning. It reads deterministic state and
answers: where is each piece of work, what's blocked, and what is the next correct command.
No judgment calls of its own — the state script owns counting; this stage owns the plain-
language interpretation.

## Execution steps

1. Run `senior state --json` for the full picture (all work slugs + all bug slugs; if
   arguments provide a slug, also request that slug's detail).
2. If `.senior/` does not exist, say precisely: this project has no seniordev workspace,
   and tell the user to run `senior init --agent <their-agent>` (or to pick an agent from
   `senior sync --list-agents` if unspecified).
3. Otherwise render a dashboard:

   ```text
   seniordev status
   ─ Workspace: .senior (initialized <date>, agent: <key>)

   Work:
     <slug> — phase <recon|scope|decide|design|execute|review|verify|ship>
             artifacts: <what exists> / <gaps>
             checks: <passing/failing from the state script>
             → next: /senior.<command> <slug>   <or "nothing left; shipped on <date>">

   Bugs:
     <slug> — assess ✓ | fix ✓/✗ | test ✓/✗   verdict: …
             → next: /senior.bug-… slug=<slug>

   Principles: <versioned/ratified or draft>
   Decisions: <date span of D-NNN records>
   Backlog: <N items — top 3 by note>
   ```

4. On top: exactly one **recommendation** (start here if unsure) — the highest-priority
   unfinished thing: an unshipped `verified` work item before new work, a `failed` bug
   before new work, then newest unfinished work, then the incomplete stage least advanced.
5. If the user passes a slug, include that work's per-artifact readiness detail (missing
   inputs for the next command, and what to do about each).

## Rules

- The status stage never fixes or progresses anything itself; it reads and routes.
- Its numbers come from the state script, not from its own recounting.

## Done When

- [ ] Dashboard rendered with per-item phases and gaps
- [ ] One clear single recommendation named
- [ ] All `→ next` entries are real commands with correct prerequisites

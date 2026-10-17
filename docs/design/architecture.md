# seniordev — architecture & design

Working name: **seniordev**. Tagline: *agents that ship like senior devs.*

## Thesis

Users shouldn't have to tell an agent *what a senior dev would know to do*. Spec-kit governs
**what is built** (spec-driven). seniordev governs **how the work is done** (evidence-driven
shipping): investigate before acting, size the slice, decide-and-document, test-first
execution, adversarial self-review, honest verification, and disciplined shipping.

A senior dev handed a vague ticket produces, unprompted: context, sizing, decisions with
rationale, a plan with tests first, small commits, a self-review that finds their own bugs,
proof the thing actually works, and clean handoff material. seniordev encodes that as a
state machine with named artifacts.

## Form factor (user decisions, 2026-10-17)

- **CLI + scaffolding** (like spec-kit, but leaner): `senior init` scaffolds `.senior/` and
  renders commands into the agent's native prompt/command directory.
- **Portable from day one**: agent-agnostic command templates + thin per-agent adapters.
  MVP adapters: `claude`, `copilot`, `cursor`, `codex`, `generic`.
- **Full pipeline MVP**: all 8 stages end-to-end with real artifacts.
- Python 3.11+, stdlib-only CLI (no runtime deps, unlike spec-kit's rich-typer stack).

## Pipeline (the state machine)

```
/senior.recon → /senior.scope → /senior.decide → /senior.design → /senior.execute
                → /senior.review → /senior.verify → /senior.ship   (× loop as needed)
```

Side entry points: `/senior.bug-assess` → `/senior.bug-fix` → `/senior.bug-test`, and the
`/senior.status` dashboard that reads state and names the next command.

| Stage | Senior behavior it encodes | Artifact in `.senior/work/<slug>/` |
|---|---|---|
| recon | Read before acting: codebase, conventions, history, prior art; credibility-check the user's framing | `recon.md` |
| scope | Find the real problem, size the slice (walk/T-shirt/bag), P1/P2/P3, risks + rollback, what's explicitly out | `scope.md` |
| decide | Ask only high-impact questions (impact×uncertainty, ≤5, one at a time); everything else becomes a written decision with rejected alternatives | `decisions.md` (appended) |
| design | Spec: data model, contracts, edge cases, failure modes, test scenarios; complexity gates with written justifications | `design.md`, `tasks.md` |
| execute | Strict task loop, tests-first order, small verifiable increments, halt-on-failure rules | appended `tasks.md` + code |
| review | Adversarial self-review of own diff as a skeptical staff engineer; every finding answered before pass | `review.md` |
| verify | Prove it on the interface a user would use; honest verdicts: `verified / partial / blocked` | `verify.md` |
| ship | Conventional commits per logical unit, changelog, PR why-description, handoff notes, open items | `ship.md` |

Bug path: `bug-assess` (never edits source) → `bug-fix` (only stage allowed to edit, scoped
to assessment-listed files + deviations log) → `bug-test` (re-run reproduction; verdicts
`verified / partial / failed`, and **"invalid / not a bug" is a valid assess outcome**).

## Layout

```
seniordev/
├── docs/{research,design}/
├── src/seniordev/
│   ├── cli.py            # stdlib argparse CLI: init, sync, state
│   ├── integrations.py   # adapter registry (dir, ext, arg token, invocation syntax)
│   └── data/
│       ├── commands/*.md        # agent-agnostic pipeline templates (the product)
│       ├── templates/*.md       # principles.md, dossier.md, artifact skeletons
│       └── procedural/         # reserved for deterministic scripts
└── pyproject.toml        # stdlib-only; `senior` console script
```

## On-disk contract of an initialized project

```
.senior/
├── config.json           # which integrations were rendered, version
├── principles.md         # project constitution: quality bar, DoD, testing policy
├── dossier.md            # codebase dossier the recon step maintains
├── decisions.md          # append-only global decisions log
├── commands/             # generic (adapter-inherited) copies of all commands
└── work/<slug>/          # per-work artifacts (recon.md … ship.md)
```

## Borrowed mechanisms (from spec-kit, adapted)

- Markdown command templates as behavior prompts: frontmatter (`description`, `phase`,
  `scripts`), `$ARGUMENTS` in input section, exact output formats, STOP-and-ask gates,
  "Done When" checklists.
- `senior state --json`: deterministic state (which artifacts exist, checklist completeness,
  recommended next command). The CLI owns counting; templates own judgment.
- `[NEEDS CLARIFICATION]` markers, append-only logs, honest verdicts, deviations logs.
- Gates: complexity/abstraction violations must be justified in writing or the stage fails.

## Non-goals for MVP

- Runtime hook/extension system (spec-kit's extensions.yml) — the state machine itself is
  the hook: each command checks state before acting.
- Multi-language procedural scripts (bash+pwsh parity) — CLI subcommands replace platform
  scripts outright, which is simpler than spec-kit's tripled script set.
- Idea-assessment flow (map it later onto scope+decide artifacts).
- Interactive workflow runner with approve/reject gates (roadmap).

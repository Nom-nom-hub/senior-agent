# seniordev

**Agents that ship like senior devs.** `seniordev` installs a senior engineering
workflow into any project: your coding agent stops waiting to be told what a senior
dev would already know, and starts producing what a senior dev produces unprompted —
context, sizing, documented decisions, test-first execution, adversarial self-review,
honest end-to-end verification, clean commits and handoff notes.

Where spec-driven approaches ([spec-kit](https://github.com/github/spec-kit)) govern
*what* gets built, seniordev governs *how the work is done*: an evidence-driven
shipping pipeline where every stage leaves a named, checkable artifact.

## The pipeline

```
/senior-recon → /senior-scope → /senior-decide → /senior-design → /senior-execute
                 → /senior-review → /senior-verify → /senior-ship
```

Side entries: `/senior-bug-assess` → `/senior-bug-fix` → `/senior-bug-test`, and
the `/senior-status` dashboard (also `senior status` in a terminal).

| Command | The senior behavior it encodes | Artifact |
|---|---|---|
| recon | Read before acting; check the user's framing against the code; cite evidence for every claim | `work/<slug>/recon.md` |
| scope | Find the real problem; size the smallest shippable slice; name risks + rollback; park scope creep explicitly | `scope.md` |
| decide | Decide-and-document instead of asking what a senior should decide; ask users ≤5 high-impact questions, one at a time | `.senior/decisions.md` (append-only) |
| design | Edge cases and failure modes are design content; complexity must justify itself in writing | `design.md`, `tasks.md` |
| execute | Tests fail first, then code; halt on red; document deviations from design; never creep scope | code + updated `tasks.md` |
| review | Switch seats: review your own diff like a skeptical staff engineer; fix CRITICAL/HIGH, accept the rest in writing | `review.md` |
| verify | Prove it on the interface a real user uses; verdicts `verified / partial / blocked` — never fabricate evidence | `verify.md` |
| ship | Conventional commits that tell a story; PR that argues the why; changelog; handoff notes | `ship.md`, git history |

Honest-verdict rules run through everything: a bug nobody can reproduce is graded, not
fixed; a verification not actually run is `not-run`; "`invalid` — not a bug" is a
complete and correct outcome of the bug assess stage.

## Quickstart

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/) (no other runtime
dependencies — the CLI is stdlib-only).

```bash
uv tool install .                  # from this repo (or: uv tool install seniordev for releases)

cd your-project
senior init --agent claude          # also: copilot, cursor, codex, generic (comma-separate for several)
senior status                       # see where things stand
```

`uv tool` keeps seniordev in its own isolated environment and puts the `senior`
executable on your PATH as uv installs it (~/.local/bin normally — `uv tool install` prints the exact directory if PATH needs a nudge). Run
`uv tool install --force .` to upgrade after pulling changes; add `--editable`
during development so template edits apply immediately.

Then launch your coding agent in the project and start with the recon command
(`/senior-recon …` in Claude Code / Cursor / Codex; `#file:senior-recon.prompt.md …`
for Copilot agent mode; anywhere else, point your agent at `.senior/commands/`).

`senior sync` re-renders agent command files after updating this tool; `.senior/`
itself (principles, dossier, decisions, backlog, work artifacts) stays yours.

After init the agent also **knows the workflow ambiently**: `init`/`sync` write a
managed section into the agent's project-context file — `CLAUDE.md` (Claude Code),
`AGENTS.md` (Codex), `.github/copilot-instructions.md` (Copilot),
`.cursor/rules/seniordev.mdc` (Cursor). Those files stay human-owned: seniordev only
replaces its own marked block, your content is never touched. So after init you can
just talk to your agent — it starts with recon, uses the decide-and-document rule,
and refuses to fake verification without being handed a command. To refresh the
block after changing principles or upgrading the tool: `senior sync`.

## How it works

- **Templates as behavior prompts**: every command is an agent-agnostic markdown file
  with strict execution steps, STOP-and-ask gates, exact artifact formats, and a
  "Done When" checklist — the agent must satisfy the checklist before reporting done.
- **Deterministic state**: `senior state --json` parses the workspace from disk
  (which stages exist, checklist completeness, verdicts) and names the next command.
  The CLI owns counting; the commands own judgment.
- **`.senior/` workspace**: `principles.md` (your quality bar, read by every stage),
  `dossier.md` (codebase knowledge recon keeps current), `decisions.md`
  (append-only rationale log), `backlog.md` (parked ideas), plus per-slug work and
  bug artifact directories.

## Design docs

- [Research: how spec-kit works under the hood](docs/research/spec-kit-analysis.md)
- [Architecture & design decisions](docs/design/architecture.md)

## Development

```bash
uv venv
uv pip install -e .                 # editable install of the CLI + templates
uv run python -m unittest discover -s tests -v
```

(`python -m venv` + `pip install -e .` works identically if you prefer plain pip.)

Stdlib-only by policy: no runtime dependencies, so `init` stays trustworthy.

## Commands reference

| CLI command | What it does |
|---|---|
| `senior init [dir] --agent <keys>` | Scaffold `.senior/` and render commands for the agent(s) |
| `senior sync` | Re-render agent command files after updating this tool |
| `senior run --slug X [--yes]` | Interactive gates runner: walks a work slug, pauses at the design and ship gates |
| `senior state [--json]` | Deterministic workspace state (JSON for agents) |
| `senior status` | Dashboard: phases, gaps, assessment verdicts, and the next command |
| `senior agents` | Per-agent adapters with chained invocation examples |

Per-agent walkthrough: [docs/guides/agents.md](docs/guides/agents.md).

## Status

Alpha (v0.1.0+). Shipped: the full work pipeline (recon → ship), the bug path
(assess → fix → test), the idea-assessment flow (go / needs-clarification / kill), the
interactive gates runner (`senior run`), and a per-agent invocation guide. Known
follow-ups live in `.senior/backlog.md` (the project dogfoods itself — see
`.senior/work/v01-roadmap/` for a real worked example).

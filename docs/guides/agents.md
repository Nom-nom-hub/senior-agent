# Per-agent invocation walkthrough

`senior agents` (in the CLI) prints the same registry data shown below — treat the CLI
output as the source of truth; this guide adds nuance the registry cannot carry.

Every adapter is generated from the same agent-agnostic templates in
`src/seniordev/data/commands/`. The only differences between agents are: where the
command files land, their file extension, how user arguments are passed, and how the
command is invoked. If you are on an agent that is not listed, use `--agent generic`
and point your agent at `.senior/commands/`.

The pipeline in every agent is the same order:

```
recon -> scope -> decide -> design -> [gate] -> execute -> review -> verify -> [gate] -> ship
```

Alternatively let the CLI drive: `senior run --slug <slug>` walks your work item and
pauses at the gates for your approval (see "Gate-assisted flow" below).

## Claude Code

- **Where**: `.claude/commands/senior-*.md` (rendered by `senior init --agent claude`)
- **Argument token**: `$ARGUMENTS` (native; no rewriting)
- **Chained example**:

  ```text
  /senior-recon Add retries to the webhook fan-out
  /senior-scope            # evidence lands in .senior/work/<slug>/scope.md
  /senior-decide, /senior-design, /senior-execute, /senior-review
  /senior-verify, then /senior-ship when verification is approved
  ```

Claude Code resolves these as slash commands in the session; pass your ask as the
suffix ($ARGUMENTS substitutes into the template's Arguments block).

## GitHub Copilot (agent mode)

- **Where**: `.github/prompts/senior-*.prompt.md`
- **Argument token**: `${input:arguments}` (substituted automatically by `senior sync`)
- **Chained example**:

  ```text
  #file:senior-recon.prompt.md Track download errors in agent mode
  #file:senior-scope.prompt.md, ... continuing through the stages:
  scope, decide, design, execute, review, verify, ship
  ```

Run each prompt file in agent mode (`#file:` reference). The `${input:arguments}`
token must be supplied after the file reference; check VS Code's prompt-file help
if your Copilot version differs.

## Cursor

- **Where**: `.cursor/commands/senior-*.md`
- **Argument token**: `$ARGUMENTS`
- **Chained example**:

  ```text
  /senior-recon Add caching headers to static responses
  /senior-scope, /senior-decide, /senior-design, /senior-execute
  /senior-review, /senior-verify, /senior-ship
  ```

## OpenAI Codex CLI

- **Where**: `.codex/prompts/senior-*.md`
- **Argument token**: `$ARGUMENTS`
- **Chained example**:

  ```text
  /senior-recon Fix the flaky cart-total rounding
  /senior-scope -> /senior-decide -> /senior-design -> /senior-execute
  /senior-review -> /senior-verify -> /senior-ship
  ```

## Generic (any agent)

- **Where**: `.senior/commands/senior-*.md` (always rendered, even when other
  adapters are requested)
- **Argument token**: none special — the command file embeds its instructions; paste
  the ask where the file's Arguments block sits.

Point any agent at `.senior/commands/senior-recon.md` to begin, and keep a terminal
open for `senior status` / `senior run` between stages.

## Gate-assisted flow (with `senior run`)

For a more human-in-the-loop run, do the investigation commands in your agent as
usual, but let the CLI route and enforce gates:

```bash
senior run --slug my-feature       # interactive walk; pauses at design and ship gates
senior run --slug my-feature --yes # skip prompts (CI/scripts; gates auto-approve)
```

Exit codes: `0` = walked cleanly or paused at your request; `1` = gate rejected or
missing input/non-interactive without `--yes`. The runner prints exactly which command
to paste into your agent next for each unfinished stage.

## Adding a new agent adapter

1. Open `src/seniordev/integrations.py`.
2. Add an `Integration(...)` entry to `INTEGRATIONS` with: key, label, project-relative
   `directory`, rendered file `extension`, `arguments_token` (the token that replaces
   `$ARGUMENTS`; use `$ARGUMENTS` itself if your agent is native), one-line
   `invocation`, and a multi-line chained `example` mentioning at least two stages.
3. Add a registry test in `tests/test_integrations.py`, run
   `uv run python -m unittest discover -s tests`, then run `senior sync` in a sample
   project to confirm the render lands in your agent's native location.

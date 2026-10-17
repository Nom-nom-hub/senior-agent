# Spec-Kit Analysis (source study)

Source studied: https://github.com/github/spec-kit (cloned to `_research/spec-kit/`, shallow `main`).
Method: direct source analysis of docs, templates, command prompts, CLI modules and bundled
extensions. (REA was not needed: this is a complete, public source repository, so binary
reconstruction tooling would add nothing.)

## 1. Architecture — three layers

| Layer | Where | What it does |
|---|---|---|
| CLI plumbing | `src/specify_cli/` (Python, `uv` installable) | `specify init <project> --integration <agent>` scaffolds `.specify/`, copies templates, registers an "integration" (a per-agent render of the command files). Covers ~40 integrations (claude, copilot, cursor, codex, gemini, opencode, …). |
| Command templates | `templates/commands/*.md` | The actual product: long structured *prompts* per slash-command (`constitution`, `specify`, `clarify`, `plan`, `tasks`, `analyze`, `implement`, `converge`). Each dictates mandatory pre-checks, exact output formats, stop-and-ask gates, and a "Done When" checklist. |
| Deterministic scripts | `scripts/bash|powershell|python/` | State the LLM must not guess: `check-prerequisites.sh --json` emits absolute paths (`FEATURE_DIR`, `AVAILABLE_DOCS`). Per-platform parity (bash, PS 5.1, python) is a hard repo rule. |

Plus packaged extensions/presets/workflows/bundles:

- **Extensions** (`extensions/bug`, `extensions/assess`, `extensions/git`, …) install extra commands + hook events (`hooks.before_implement` etc.) configured in `.specify/extensions.yml`; mandatory hooks must be executed and awaited by the agent, optional ones surfaced.
- **Workflows** (`workflows/speckit/workflow.yml`) chain commands with human **review gates** (`type: gate`, `options: [approve, reject]`) — an automated pipeline is possible without losing human sign-off.
- **Presets** adapt templates/terminology; **bundles** install role-based sets.

## 2. The core SDD loop

`/constitution` → `/specify` → `/clarify` → `/plan` → `/tasks` → `/implement` → `/converge`
(loop implement→converge until **"✅ Converged"**). Independent entry points: bugfix
(assess → fix → test) and idea assessment (int intake → research → define → shape → decide →
go / needs-clarification / kill).

Per-feature artifacts live in `specs/<NNNN-branch-name>/`:
`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`,
`tasks.md`, `checklists/`.

## 3. Techniques worth stealing (the "template-as-behavior-prompt" canon)

1. **Banned guessing** — templates force `[NEEDS CLARIFICATION: question]` markers instead of
   plausible assumptions; the clarifier later converts them into max-5 questions, one at a
   time, prioritized by *impact × uncertainty*, each answerable MC or ≤5 words.
2. **Checklists as unit tests for documents** — every generated artifact ends with a
   checklist it must satisfy; implement re-scans them as a pass/fail gate before starting.
3. **Written justifications for complexity** — plan template has "Phase -1 gates"
   (Simplicity Gate ≤3 projects, Anti-Abstraction, Integration-First) and a Complexity
   Tracking table: any violation must be *written down with the rejected alternative*.
4. **Append-only convergence** — `/converge` reads spec/plan/tasks as the sole intent
   source, classifies every gap as `missing | partial | contradicts | unrequested`, assigns
   CRITICAL/HIGH/MEDIUM/LOW severity, and appends traceable tasks (`T042 … per FR-003
   (missing)`). Never rewrites history; byte-for-byte no-op when nothing remains.
5. **Honest verdicts** — the bug extension's guardrail: "a reproduction that was not
   actually performed is reported as `partial` or `not-run`, not `verified`." Fix scope is
   constrained to assessment-listed files; deviations get logged in a
   **Deviations from Assessment** section.
6. **Explicit scope surfacing** — code doing things the spec never asked for is reported as
   `unrequested`, not silently ignored or deleted.
7. **Links/handoffs** — commands declare `handoffs:` to chain into each other, and
   workflow.yml adds machine-runnable chains with human gates.
8. **Scripts over vibes** — anything countable (checklist totals, prerequisites, paths) is
   computed by script JSON, never by the model.

## 4. Its gap (our opening)

Spec-kit's quality gates are **spec-side**. Once you reach `/speckit.implement`:

- there is no adversarial **self-review** of the produced diff;
- verification is "tests pass", not "prove it on the interface a user would use";
- nothing owns commit hygiene, PR rationale, changelog, handoff notes;
- it doesn't model the senior-dev judgment loop: size the slice, decide-and-document on
  low-impact ambiguities instead of asking, declare risks/rollback, know when something is
  *not a bug* or an idea should die.

That is exactly the space `seniordev` targets.

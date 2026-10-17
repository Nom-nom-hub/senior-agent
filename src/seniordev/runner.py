"""Interactive gates runner (senior run).

Walks a work slug through the pipeline, printing which agent command to run for the
next unfinished stage and pausing at fixed human gates. The runner guides humans; it
never drives an agent. Stdlib-only; fixed gates with no per-project config in MVP
(D-003, D-004).

Gate placement (from design.md):
- gate A: approving design.md -> guidance for `execute`
- gate B: approving verify.md -> guidance for `ship`

Exit codes: 0 = walked to completion (or slug already complete / user paused cleanly),
1 = stopped at a gate or bad input or non-interactive run without --yes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import integrations as integ
from . import state as st

# Gate semantics: gate A (design.md approval) precedes execute guidance; gate B
# (verify.md evidence approval) precedes ship guidance. Matches design.md S2.
GATES = (
    ("execute", "Gate: you are about to start executing. Review design.md once more (scope, guards, edge cases). Approve?"),
    ("ship", "Gate: you are about to ship. Review verify.md evidence (verdict, unrun rows). Approve?"),
)

GATE_BEFORE = {"execute": "design", "ship": "verify"}
ANSWERS_YES = ("y", "yes")


def is_interactive() -> bool:
    return sys.stdin.isatty()


def ask_gate(prompt: str) -> bool:
    """Ask; anything not an affirmative is a rejection. EOF/abort counts as no."""
    try:
        answer = input(prompt + " [y/N] ").strip().lower()
    except EOFError:
        print()
        return False
    return answer in ANSWERS_YES


def parse_project(args: argparse.Namespace) -> Path:
    return Path(getattr(args, "project", None) or ".").resolve()


def read_config(project_root: Path) -> dict:
    config_path = st.workspace_root(project_root) / "config.json"
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def primary_agent(project_root: Path) -> str:
    """Last agent key in config is the primary; generic is never primary."""
    agents = [key for key in read_config(project_root).get("agents", []) if key != "generic"]
    return agents[-1] if agents else "generic"


def command_hint(command: str, agent_key: str) -> str:
    integration = integ.INTEGRATIONS.get(agent_key, integ.INTEGRATIONS["generic"])
    return f"{command}   # in {integration.directory}/  ({integration.invocation})"


def check_gates(next_stage: str, slug: str) -> bool:
    """Return True if any applicable gate was approved. False = rejected/aborted."""
    gate = next(
        (before_stage, prompt) for before_stage, prompt in GATES if before_stage == next_stage
    )
    if gate is None:
        return True
    _before, prompt = gate
    if ask_gate(prompt):
        print("approved - continuing")
        return True
    print(f"stopped at the gate before '{next_stage}'. Resume anytime: senior run {slug}")
    return False


def run(args: argparse.Namespace) -> int:
    project_root = parse_project(args)
    gathered = st.gather(project_root)
    if not gathered.get("initialized"):
        print(
            f"This project has no {st.WORKSPACE}/ workspace yet.\n"
            "Run: senior init --agent <key>   (see `senior agents` for valid keys)",
            file=sys.stderr,
        )
        return 1

    existing = [item["slug"] for item in gathered.get("work", [])]
    if args.slug is None:
        if existing:
            print("no --slug given; pick one of: " + ", ".join(existing))
        else:
            print(
                "no work slugs yet - start with the senior-recon command in your agent"
            )
        return 1
    if args.slug not in existing:
        suffix = f" existing: {', '.join(existing)}" if existing else " (none exist)"
        print(f"unknown work slug '{args.slug}'." + suffix, file=sys.stderr)
        return 1

    item = next(part for part in gathered["work"] if part["slug"] == args.slug)
    agent_key = primary_agent(project_root)

    if item["complete"]:
        print(f"'{args.slug}' is complete (shipped). Nothing to walk.")
        return 0

    if not args.yes and not is_interactive():
        print(
            "interactive gates need a terminal; rerun with --yes to skip gates",
            file=sys.stderr,
        )
        return 1

    print(f"senior run - {args.slug}")
    for name, command in st.PIPELINE:
        if item["artifacts"][name]["exists"]:
            continue
        if not args.yes and not check_gates(name, args.slug):
            return 1
        print("Next agent command:")
        print(f"  {command_hint(command, agent_key)}")
        if not args.yes:
            try:
                answer = input(
                    f"Mark '{name}' done once your agent finished it? [y/N] "
                ).strip().lower()
            except EOFError:
                answer = ""
            if answer not in ANSWERS_YES:
                print("paused. Resume: senior run " + args.slug)
                return 0
        else:
            print(f"  (auto-advancing past '{name}'; --yes)")
    print(f"walked '{args.slug}' end to end.")
    return 0

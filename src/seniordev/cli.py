"""seniordev CLI (stdlib-only).

Commands:
  senior init [dir] --agent key[,key…]   Scaffold .senior/ and render agent commands
  senior sync [--agent key…]             (Re-)render command files from templates
  senior state [--json]                  Deterministic workspace state for agents  senior run --slug X [--yes]           Interactive gates runner over a work slug
  senior status                          Human-readable dashboard
  senior agents                         List supported agent adapters
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import state as st
from . import integrations as integ
from . import runner
from . import __version__

DATA = Path(__file__).resolve().parent / "data"
COMMANDS_DIR = DATA / "commands"
TEMPLATES_DIR = DATA / "templates"

REPO_INTEGRATION = "generic"  # always rendered so any agent can read .senior/commands

SECTION_BEGIN = "<!-- seniordev:begin v1 -->"
SECTION_END = "<!-- seniordev:end -->"


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def parse_agents(spec: str) -> list[str]:
    keys = [key.strip() for key in spec.split(",") if key.strip()]
    if not keys:
        keys = [REPO_INTEGRATION]
    for key in keys:
        if key not in integ.INTEGRATIONS:
            raise SystemExit(
                f"unknown agent '{key}'. Valid keys: {integ.UNKNOWN_AGENT_HINT}"
            )
    if REPO_INTEGRATION not in keys:
        keys = [REPO_INTEGRATION, *keys]
    return keys


def render_commands(project_root: Path, keys: list[str]) -> list[Path]:
    rendered: list[Path] = []
    for key in keys:
        integration = integ.INTEGRATIONS[key]
        target_dir = project_root / integration.directory
        target_dir.mkdir(parents=True, exist_ok=True)
        for source_path in sorted(COMMANDS_DIR.glob("*.md")):
            source = source_path.read_text(encoding="utf-8")
            stem = source_path.name.removesuffix(".md")
            destination = target_dir / integ.command_file_name(stem, integration)
            destination.write_text(
                integ.render_command(source, integration), encoding="utf-8"
            )
            rendered.append(destination)
    return rendered


def write_workspace_scaffold(project_root: Path) -> list[Path]:
    root = project_root / ".senior"
    root.mkdir(parents=True, exist_ok=True)
    made: list[Path] = []

    def write_if_missing(destination: Path, content: str) -> None:
        if not destination.exists():
            destination.write_text(content, encoding="utf-8")
            made.append(destination)

    write_if_missing(
        root / "principles.md",
        (TEMPLATES_DIR / "principles-template.md").read_text(encoding="utf-8"),
    )
    write_if_missing(
        root / "dossier.md",
        (TEMPLATES_DIR / "dossier-template.md").read_text(encoding="utf-8"),
    )
    write_if_missing(
        root / "decisions.md",
        "# Decisions Log (append-only)\n\n"
        "> Senior discipline: decide and document. Never rewrite decisions here.\n",
    )
    write_if_missing(
        root / "backlog.md",
        "# Backlog\n\n"
        "One checkbox item per parked idea or out-of-scope finding:\n\n"
        "- [ ] (example item until the first real backlog entry lands)\n",
    )
    write_if_missing(
        root / "README.md",
        "# seniordev workspace\n\n"
        "This directory is how agents ship work here.\n\n"
        "- principles.md — the quality bar every stage reads (edit it, make it yours)\n"
        "- dossier.md — what the agent learned about this codebase (recon keeps it current)\n"
        "- decisions.md — append-only log of decisions made with rationale\n"
        "- backlog.md — parked ideas and out-of-scope finds\n"
        "- work/<slug>/ — one folder per piece of work (recon → ship artifacts)\n"
        "- bugs/<slug>/ — one folder per bug (assess → fix → test artifacts)\n\n"
        "Run `senior status` for where things stand.\n",
    )
    return made


def resolve_root(args: argparse.Namespace) -> Path:
    return Path(getattr(args, "project", None) or ".").resolve()


def project_arg(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "-C",
        "--project",
        default=None,
        help="project root (default: current directory)",
    )
    return parser


def write_managed_instructions(project_root: Path, keys: list[str]) -> dict[str, str]:
    """Write the managed seniordev workflow section into each agent's ambient
    instructions file (CLAUDE.md, AGENTS.md, Copilot instructions, Cursor rules).

    Merge policy: the file stays human-owned; seniordev replaces only the text
    between its BEGIN/END markers. Human content above/below is untouched; no file
    is created empty — if creating fresh, a small header is added above the section.
    Idempotent: re-running replaces the same block (config stripping versions).
    """
    body = (TEMPLATES_DIR / "agent-instructions.md").read_text(encoding="utf-8")
    section = f"{SECTION_BEGIN}\n\n{body}"
    results: dict[str, str] = {}
    for key in keys:
        integration = integ.INTEGRATIONS[key]
        if not integration.instructions_file:
            continue
        if key == "generic" and "generic" not in _explicit_agents(project_root):
            continue
        target = project_root / integration.instructions_file
        existing = ""
        if target.is_file():
            existing = target.read_text(encoding="utf-8", errors="replace")
        if SECTION_BEGIN in existing and SECTION_END in existing:
            pre, rest = existing.split(SECTION_BEGIN, 1)
            _, post = rest.split(SECTION_END, 1)
            merged = pre + section + SECTION_END + post
            action = "replaced section"
        else:
            if existing.strip():
                merged = existing.rstrip() + "\n\n" + section + SECTION_END + "\n"
            else:
                header = (
                    f"# {integration.instructions_file.split('/')[-1]}\n\n"
                )
                merged = header + section + SECTION_END + "\n"
            action = "appended section"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(merged, encoding="utf-8")
        rendered = results[integration.instructions_file] = action
        results[integration.instructions_file] = (
            f"{action} in {integration.instructions_file} ({key})"
        )
        results[integration.instructions_file] = (
            f"{action} in {integration.instructions_file} ({key})"
        )
        _ = rendered
    return results


def write_managed_instructions(
    project_root: Path, keys: list[str], repo_always: bool = False
) -> list[str]:
    """Write the managed seniordev workflow section into each agent's ambient
    instructions file (CLAUDE.md, AGENTS.md, Copilot instructions, Cursor rules).

    Merge policy: the file stays human-owned; seniordev replaces only the text
    between its BEGIN/END markers. Human content above/below is untouched. If the
    file does not exist, it is created with a small header plus the section.
    Idempotent: re-running replaces the same block.
    """
    body = (TEMPLATES_DIR / "agent-instructions.md").read_text(encoding="utf-8")
    section = f"{SECTION_BEGIN}\n\n{body}"
    actions: list[str] = []
    seen_files: set[str] = set()
    for key in keys:
        integration = integ.INTEGRATIONS[key]
        instructions_file = integration.instructions_file
        if not instructions_file or instructions_file in seen_files:
            continue
        # generic's AGENTS.md is only rendered when explicitly requested.
        if key == REPO_INTEGRATION and not repo_always:
            continue
        seen_files.add(instructions_file)
        target = project_root / instructions_file
        existing = ""
        if target.is_file():
            existing = target.read_text(encoding="utf-8", errors="replace")
        if SECTION_BEGIN in existing and SECTION_END in existing:
            pre, rest = existing.split(SECTION_BEGIN, 1)
            _, post = rest.split(SECTION_END, 1)
            merged = pre + section + SECTION_END + post
            action = "replaced section"
        elif existing.strip():
            merged = existing.rstrip() + "\n\n" + section + SECTION_END + "\n"
            action = "appended section"
        else:
            header = f"# {instructions_file.rsplit('/', 1)[-1]}\n\n"
            merged = (
                integration.instructions_frontmatter + header + section
                + SECTION_END + "\n"
            )
            action = "created"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(merged, encoding="utf-8")
        actions.append(f"{action}: {instructions_file} ({key})")
    return actions


def cmd_init(args: argparse.Namespace) -> int:
    # init takes an optional positional directory; -C is honored otherwise
    directory = getattr(args, "directory", None)
    target = Path(directory).resolve() if directory else resolve_root(args)
    target.mkdir(parents=True, exist_ok=True)
    workspace = target / ".senior"
    if (workspace / "config.json").is_file() and not args.force:
        eprint(f"already initialized: {workspace} (use --force to re-render)")
        return 1

    agents = parse_agents(args.agent)
    made = write_workspace_scaffold(target)
    rendered = render_commands(target, agents)
    instructions = write_managed_instructions(target, agents)
    config = {
        "tool": "seniordev",
        "version": __version__,
        "agents": agents,
        "initialized_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (workspace / "config.json").write_text(
        json.dumps(config, indent=2) + "\n", encoding="utf-8"
    )

    primary = integ.INTEGRATIONS[agents[-1]]
    print(f"Initialized .senior/ in {target}")
    for path in made:
        print(f"  + {path.relative_to(target)}")
    print(f"  rendered {len(rendered)} command files for: {', '.join(agents)}")
    for item in instructions:
        print(f"  {item}")
    print("Next:")
    print("  1. Edit .senior/principles.md and .senior/dossier.md to match reality")
    first_example_line = primary.example.splitlines()[0].strip()
    print(f"  2. Launch your agent in this project and start with: senior-recon")
    print(f"     example in {primary.directory}/: {first_example_line}")
    print(f"     (full per-agent walkthrough: docs/guides/agents.md)")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    project_root = resolve_root(args)
    config_path = project_root / ".senior" / "config.json"
    if args.agent:
        agents = parse_agents(args.agent)
    elif config_path.is_file():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        agents = [key for key in config.get("agents", []) if key in integ.INTEGRATIONS]
        if REPO_INTEGRATION not in agents:
            agents = [REPO_INTEGRATION, *agents]
    else:
        eprint("no .senior/config.json — run senior init first")
        return 1
    rendered = render_commands(project_root, agents)
    print(f"rendered {len(rendered)} command files:")
    for destination in rendered:
        print(f"  {destination.relative_to(project_root)}")
    repo_always = any(key == REPO_INTEGRATION for key in agents)
    for item in write_managed_instructions(project_root, agents, repo_always):
        print(f"  {item}")
    return 0


def cmd_state(args: argparse.Namespace) -> int:
    project_root = resolve_root(args)
    collected = st.gather(project_root)
    if args.json:
        print(st.to_json(collected))
    else:
        print(st.status_text(collected))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    project_root = resolve_root(args)
    print(st.status_text(st.gather(project_root)))
    return 0


def cmd_agents(_args: argparse.Namespace) -> int:
    print("supported agent integrations:\n")
    for key, integration in integ.INTEGRATIONS.items():
        print(f"  {key:8} {integration.label}")
        print(f"           dir: {integration.directory}/  invoke: {integration.invocation}")
        for line in integration.example.splitlines():
            print(f"           {line}")
        print()
    print("not listed? use --agent generic and point your agent at .senior/commands/")
    print("see docs/guides/agents.md for the full walkthrough (senior agents is the source of truth)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="senior",
        description="seniordev - agents that ship like senior devs",
    )
    parser.add_argument("--version", action="version", version=f"senior {__version__}")
    sub = parser.add_subparsers(dest="command")

    init_p = project_arg(sub.add_parser("init", help="scaffold .senior/ and render agent commands"))
    init_p.add_argument("directory", nargs="?", default=None)
    init_p.add_argument(
        "--agent", default=REPO_INTEGRATION,
        help="comma-separated agent keys (see: senior agents)",
    )
    init_p.add_argument("--force", action="store_true", help="re-render even if initialized")

    sync_p = project_arg(sub.add_parser("sync", help="re-render agent command files from templates"))
    sync_p.add_argument("--agent", default=None, help="override agents from config.json")

    state_p = project_arg(sub.add_parser("state", help="project state (add --json for agents)"))
    state_p.add_argument("--json", action="store_true", help="emit JSON")

    status_p = project_arg(sub.add_parser("status", help="human dashboard with next-command advice"))
    ag_p = sub.add_parser("agents", help="list supported agent integrations")

    run_p = project_arg(
        sub.add_parser("run", help="walk a work slug through the pipeline with human gates")
    )
    run_p.add_argument("--slug", default=None, help="work slug to walk (required)")
    run_p.add_argument(
        "--yes", action="store_true", help="skip interactive gates and pauses (for CI)"
    )

    init_p.set_defaults(func=cmd_init)
    sync_p.set_defaults(func=cmd_sync)
    state_p.set_defaults(func=cmd_state)
    status_p.set_defaults(func=cmd_status)
    ag_p.set_defaults(func=cmd_agents)
    run_p.set_defaults(func=runner.run)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

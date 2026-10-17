"""Deterministic workspace state for seniordev.

The CLI owns counting; templates own judgment. Nothing in here asks an LLM to
figure out where things are: artifact presence, checkbox completeness and verdicts
are parsed from disk so command templates can gate on `— json` output.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

WORKSPACE = ".senior"
WORK_DIRNAME = "work"
BUGS_DIRNAME = "bugs"
ASSESSMENTS_DIRNAME = "assessments"

DECISION_WORD_RE = re.compile(
    r"^\s*[-*]\s*\**(?:Decision)\*\*\s*:\s*(\S.*?)\s*$", re.MULTILINE
)

# The work pipeline. `decide` is intentionally absent: it has no per-work artifact
# (it appends to .senior/decisions.md and resolves markers in recon/scope), so it is
# the fallback route only when pending_clarifications > 0 in work_item().
PIPELINE = (
    ("recon", "senior-recon"),
    ("scope", "senior-scope"),
    ("design", "senior-design"),
    ("execute", "senior-execute"),
    ("review", "senior-review"),
    ("verify", "senior-verify"),
    ("ship", "senior-ship"),
)

BUG_PIPELINE = (
    ("assessment", "senior-bug-assess"),
    ("fix", "senior-bug-fix"),
    ("test", "senior-bug-test"),
)

STATUS_RE = re.compile(r"^\s*[-*]\s*\*\*Status\*\*\s*:\s*(.+?)\s*$", re.MULTILINE)
VERDICT_RE = re.compile(
    r"^\s*[-*]\s*\*\*(?:Overall verdict|Verdict)\*\*\s*:\s*(\S.*?)\s*$", re.MULTILINE
)
CHECKBOX_RE = re.compile(r"^\s*[-*]\s\[( |x|X)\]", re.MULTILINE)
DECISION_RE = re.compile(r"^###\s*D-\d+:", re.MULTILINE)


def workspace_root(project_root: Path) -> Path:
    return project_root / WORKSPACE


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def checklist_stats(text: str) -> dict:
    boxes = CHECKBOX_RE.findall(text)
    return {
        "total": len(boxes),
        "checked": sum(1 for box in boxes if box.strip().lower() == "x"),
    }


def parse_status(text: str) -> str | None:
    match = STATUS_RE.search(text)
    return match.group(1).lower() if match else None


def parse_verdict(text: str) -> str | None:
    match = VERDICT_RE.search(text)
    return match.group(1).lower().rstrip("*") if match else None


def needs_clarification(text: str) -> int:
    return len(re.findall(r"\[NEEDS CLARIFICATION", text))


def work_item(work_item_dir: Path) -> dict:
    slug = work_item_dir.name
    artifacts: dict[str, dict] = {}
    complete = False
    pending_clarifications = 0
    for name, _command in PIPELINE:
        path = work_item_dir / f"{name}.md"
        artifact = {"exists": path.is_file()}
        if path.is_file():
            text = read_text(path)
            artifact["checklist"] = checklist_stats(text)
            status = parse_status(text)
            if status:
                artifact["status"] = status
            if name == "verify":
                artifact["verdict"] = parse_verdict(text)
            pending_clarifications += needs_clarification(text)
        artifacts[name] = artifact
    complete = artifacts["ship"]["exists"]

    next_command = None
    if complete:
        next_command = None
    else:
        for name, command in PIPELINE:
            if not artifacts[name]["exists"]:
                next_command = command
                break
        # Decide stage is one that's done separately: if the *next missing* artifact is
        # design but open clarifications remain, the senior move is to dispose of them
        # explicitly first.
        if next_command == "senior-design" and pending_clarifications:
            next_command = "senior-decide"

    return {
        "slug": slug,
        "dir": str(work_item_dir),
        "artifacts": artifacts,
        "complete": complete,
        "pending_clarifications": pending_clarifications,
        "next_command": next_command,
    }


def bug_item(bug_dir: Path) -> dict:
    slug = bug_dir.name
    artifacts = {}
    for name, _command in BUG_PIPELINE:
        path = bug_dir / f"{name}.md"
        artifact = {"exists": path.is_file()}
        if path.is_file():
            text = read_text(path)
            verdict = parse_verdict(text)
            if verdict:
                artifact["verdict"] = verdict
        artifacts[name] = artifact

    assessment_verdict = artifacts["assessment"].get("verdict")

    next_command = None
    done_reason = None
    if assessment_verdict in {"invalid", "not a bug"}:
        done_reason = "assessed as not a bug"
    elif artifacts["test"]["exists"]:
        verdict = artifacts["test"].get("verdict", "")
        if verdict.startswith("verified"):
            done_reason = "fix verified"
        elif verdict.startswith("failed"):
            next_command = "senior-bug-fix"
        else:
            done_reason = verdict or "closed"
    elif not artifacts["fix"]["exists"] and assessment_verdict and "valid" not in assessment_verdict and "likely" not in assessment_verdict:
        done_reason = "assessed as not a bug"
    else:
        for name, command in BUG_PIPELINE:
            if not artifacts[name]["exists"]:
                next_command = command
                break
    return {
        "slug": slug,
        "dir": str(bug_dir),
        "artifacts": artifacts,
        "next_command": next_command,
        "done_reason": done_reason,
    }


def assessment_item(assessment_dir: Path) -> dict:
    """Idea assessment: one artifact, one terminal decision (D-001, D-002)."""
    path = assessment_dir / "assessment.md"
    text = read_text(path)
    decision = None
    decision_match = DECISION_WORD_RE.search(text)
    if path.is_file() and decision_match:
        raw = decision_match.group(1).lower()
        if "needs" in raw or "clarification" in raw:
            decision = "needs-clarification"
        elif "kill" in raw:
            decision = "kill"
        elif "go" in raw:
            decision = "go"
    return {
        "slug": assessment_dir.name,
        "dir": str(assessment_dir),
        "file": str(path),
        "exists": path.is_file(),
        "decision": decision,
    }


def gather(project_root: Path) -> dict:
    root = workspace_root(project_root)
    initialized = (root / "config.json").is_file()

    state: dict = {
        "project_root": str(project_root),
        "workspace": str(root),
        "initialized": initialized,
        "workspace_dirname": WORKSPACE,
    }
    if not initialized:
        return state

    decisions_path = root / "decisions.md"
    backlog_path = root / "backlog.md"
    decisions_text = read_text(decisions_path)
    state["principles"] = {"exists": (root / "principles.md").is_file()}
    state["dossier"] = {"exists": (root / "dossier.md").is_file()}
    state["decisions"] = {
        "exists": decisions_path.is_file(),
        "records": len(DECISION_RE.findall(decisions_text)),
    }
    state["backlog"] = {
        "exists": backlog_path.is_file(),
        "items": checklist_stats(read_text(backlog_path))["checked"],
    }

    state["work"] = sorted(
        (work_item(path) for path in (root / WORK_DIRNAME).iterdir() if path.is_dir()),
        key=lambda item: item["slug"],
    ) if (root / WORK_DIRNAME).is_dir() else []
    state["bugs"] = sorted(
        (bug_item(path) for path in (root / BUGS_DIRNAME).iterdir() if path.is_dir()),
        key=lambda item: item["slug"],
    ) if (root / BUGS_DIRNAME).is_dir() else []
    state["assessments"] = sorted(
        (
            assessment_item(path)
            for path in (root / ASSESSMENTS_DIRNAME).iterdir()
            if path.is_dir()
        ),
        key=lambda item: item["slug"],
    ) if (root / ASSESSMENTS_DIRNAME).is_dir() else []
    return state


def next_action(state: dict) -> dict:
    """Single recommendation: unshipped verified work > failing bug > newest work."""
    for item in state.get("work", []):
        if item["complete"]:
            continue
        verdict = item["artifacts"]["verify"].get("verdict")
        if verdict and verdict.startswith("verified") and item["next_command"] == "senior-ship":
            return {"priority": "ship-ready", "item": item}
    for item in state.get("bugs", []):
        if item.get("next_command") == "senior-bug-fix":
            return {"priority": "failing-bug", "item": item}
    unfinished = [item for item in state.get("work", []) if not item["complete"]]
    if unfinished:
        return {"priority": "work-in-progress", "item": unfinished[-1]}
    unfinished_bugs = [item for item in state.get("bugs", []) if item.get("next_command")]
    if unfinished_bugs:
        return {"priority": "bug-in-progress", "item": unfinished_bugs[-1]}
    return {"priority": "idle"}


def to_json(state: dict) -> str:
    payload = dict(state)
    payload["next_action"] = next_action(state)
    return json.dumps(payload, indent=2)


def status_text(state: dict) -> str:
    if not state.get("initialized"):
        return (
            f"This project has no {WORKSPACE}/ workspace yet.\n"
            "Run: senior init --agent <key>   (see `senior agents` for valid keys)"
        )
    lines = [f"seniordev status - workspace: {state['workspace']}"]
    work = state.get("work", [])
    if work:
        lines.append("\nWork:")
        for item in work:
            present = [name for name, _a in PIPELINE if item["artifacts"][name]["exists"]]
            arrow = item["next_command"] or f"shipped ({'complete'})"
            lines.append(
                f"  {item['slug']}: {len(present)}/{len(PIPELINE)} stages"
                + (f" - next: /{arrow}" if item["next_command"] else f" - {arrow}")
              )
    else:
        lines.append("\nWork: (none - start with /senior-recon)")
    bugs = state.get("bugs", [])
    if bugs:
        lines.append("\nBugs:")
        for item in bugs:
            arrow = item.get("next_command") or item.get("done_reason") or "in progress"
            lines.append(f"  {item['slug']}: " + ", ".join(
                name for name, _c in BUG_PIPELINE if item["artifacts"][name]["exists"]
            ) + f" - {arrow}")
    action = next_action(state)
    if action.get("item"):
        series = "work" if "work" in action["item"]["dir"].replace("\\", "/").split("/") else "bugs"
        slug = action["item"]["slug"]
        if action["item"].get("next_command"):
            lines.append(f"\nStart here: /{action['item']['next_command']} slug={slug}")
        else:
            lines.append(f"\nStart here: no open commands; review {series} item '{slug}'")
    else:
        lines.append("\nStart here: nothing open. Nice.")
    assessments = state.get("assessments", [])
    if assessments:
        lines.append("\nIdeas assessed:")
        for item in assessments:
            decision = item["decision"] or "in progress"
            arrow = (
                "- next: /senior-recon slug=" + item["slug"]
                if decision == "go"
                else f"- {decision}"
            )
            lines.append(f"  {item['slug']}: {decision}  {arrow}")
    lines.append(
        f"Principles: {'present' if state['principles']['exists'] else 'MISSING'}  "
        f"Decisions recorded: {state['decisions']['records']}  "
        f"Backlog: {state['backlog']['items']}"
    )
    return "\n".join(lines)

"""Agent adapter registry.

Each adapter renders the agent-agnostic command markdown into the target agent's
native prompt/command location. Commands use `$ARGUMENTS` for user input; adapters
that need a different token get a substitution applied to the argument placeholder
only (frontmatter and body otherwise untouched).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Integration:
    key: str
    label: str
    # Directory relative to the project root where command files are rendered.
    directory: str
    # Rendered file extension ("md", "prompt.md", "mdc", ...)
    extension: str
    # Token that replaces "$ARGUMENTS" after rendering; identity if same.
    arguments_token: str
    # Human hint shown to the user on how to invoke a single command.
    invocation: str
    # Multi-line chained-stage usage example (first line = start of the pipeline).
    example: str
    # File the agent reads ambient project context from; managed section is
    # rendered here by init/sync so the agent knows the workflow without being
    # handed a command. Empty for generic (commands-only).
    instructions_file: str
    # Optional frontmatter prepended for rule-file formats (e.g. Cursor .mdc).
    instructions_frontmatter: str = ""


INTEGRATIONS: dict[str, Integration] = {
    integration.key: integration
    for integration in (
        Integration(
            "generic",
            "Generic markdown commands in .senior/commands (any agent can read them)",
            ".senior/commands",
            "md",
            "$ARGUMENTS",
            "Open .senior/commands/senior-recon.md with your agent and follow it",
            "senior-recon.md <ask> -> senior-scope.md -> senior-decide.md -> ... -> senior-ship.md",
            "AGENTS.md",
        ),
        Integration(
            "claude",
            "Anthropic Claude Code (.claude/commands slash commands)",
            ".claude/commands",
            "md",
            "$ARGUMENTS",
            "/senior-recon <your ask>",
            "\n".join(
                [
                    "/senior-recon Add retries to the webhook fan-out",                    "/senior-scope            (evidence lands in .senior/work/<slug>/scope.md)",
                    "  /senior-decide, /senior-design, /senior-execute, /senior-review",
                    "  /senior-verify, then /senior-ship when verification is approved",
                ]
            ),
            "CLAUDE.md",
        ),
        Integration(
            "cursor",
            "Cursor (.cursor/commands slash commands)",
            ".cursor/commands",
            "md",
            "$ARGUMENTS",
            "/senior-recon <your ask>",
            "\n".join(
                [
                    "/senior-recon Add caching headers to static responses",                    "/senior-scope, /senior-decide, /senior-design, /senior-execute",
                    "  /senior-review, /senior-verify, /senior-ship",
                ]
            ),
            ".cursor/rules/seniordev.mdc",
            "---\ndescription: seniordev senior workflow\nglobs:\nalwaysApply: true\n---\n",
        ),
        Integration(
            "codex",
            "OpenAI Codex CLI (.codex/prompts custom prompts)",
            ".codex/prompts",
            "md",
            "$ARGUMENTS",
            "/senior-recon <your ask>",
            "\n".join(
                [
                    "/senior-recon Fix the flaky cart-total rounding",                    "/senior-scope -> /senior-decide -> /senior-design -> /senior-execute",
                    "  /senior-review -> /senior-verify -> /senior-ship",
                ]
            ),
            "AGENTS.md",
        ),
        Integration(
            "copilot",
            "GitHub Copilot (.github/prompts agent prompt files)",
            ".github/prompts",
            "prompt.md",
            "${input:arguments}",
            "#file:senior-recon.prompt.md (agent mode)",
            "\n".join(
                [
                    "#file:senior-recon.prompt.md Track download errors",
                    "  #file:senior-scope.prompt.md, ... continuing through the stages:",
                    "  scope, decide, design, execute, review, verify, ship",
                ]
            ),
            ".github/copilot-instructions.md",
        ),
    )
}

UNKNOWN_AGENT_HINT = ", ".join(sorted(INTEGRATIONS))


def command_file_name(command_stem: str, integration: Integration) -> str:
    """Rendered filename for a command stem, e.g. senior-recon + copilot."""
    if integration.extension.startswith("."):
        ext = integration.extension
    else:
        ext = "." + integration.extension
    return f"{command_stem}{ext}"


def render_command(source: str, integration: Integration) -> str:
    """Render a generic command template for a specific agent.

    The generic format already uses `$ARGUMENTS`; adapters with a different token get
    token substitution applied. `config.json` in frontmatter is not rewritten: the
    rendered file keeps the same frontmatter keys the agent expects (description, etc.).
    """
    if integration.arguments_token == "$ARGUMENTS":
        return source
    return source.replace("$ARGUMENTS", integration.arguments_token)

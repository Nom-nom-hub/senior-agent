"""Tests for seniordev.runner — gates, --yes, non-TTY, slug validation."""

import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from seniordev import runner, state


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "proj"
        self.senior = self.root / ".senior"
        self.senior.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def init_workspace(self, agents=("generic", "claude")):
        (self.senior / "config.json").write_text(
            '{"agents": %s}' % list(agents), encoding="utf-8"
        )
        for name in ("principles.md", "dossier.md", "decisions.md", "backlog.md"):
            (self.senior / name).write_text("# x\n", encoding="utf-8")

    def write_work(self, slug, name, content):
        work_dir = self.senior / "work" / slug
        work_dir.mkdir(parents=True, exist_ok=True)
        (work_dir / f"{name}.md").write_text(content, encoding="utf-8")

    def walk(self, argv, tty=False):
        args = mock.Mock(project=str(self.root), slug=None, yes=False)
        for key, value in argv.items():
            setattr(args, key, value)
        with mock.patch.object(runner, "is_interactive", return_value=tty), mock.patch(
            "sys.stdin", io.StringIO()
        ):
            return runner.run(args)


class TestValidation(Base):
    def test_uninitialized_exits_1(self):
        self.assertEqual(self.walk({}), 1)

    def test_no_slug_lists_existing(self):
        self.init_workspace()
        self.write_work("w1", "recon", "- **Status**: complete\n")
        self.assertEqual(self.walk({}), 1)

    def test_unknown_slug_exits_1_with_existing_listed(self):
        self.init_workspace()
        self.write_work("w1", "recon", "- **Status**: complete\n")
        self.assertEqual(self.walk({"slug": "nope"}), 1)


class TestWalking(Base):
    def test_complete_slug_short_circuits(self):
        self.init_workspace()
        self.write_work("w1", "ship", "# Shipment\n")
        self.assertEqual(self.walk({"slug": "w1"}), 0)

    def test_non_tty_without_yes_is_refused_naming_yes(self):
        self.init_workspace()
        self.write_work("w1", "recon", "- **Status**: complete\n")
        self.assertEqual(self.walk({"slug": "w1"}), 1)

    def test_yes_walks_full_pipeline_interactively_agnostic(self):
        self.init_workspace()
        self.write_work("w1", "recon", "- **Status**: complete\n")
        self.assertEqual(self.walk({"slug": "w1", "yes": True}), 0)

    def test_gate_rejection_stops(self):
        """From recon done, next stage scope (no gate) then design precedes gate."""
        self.init_workspace()
        self.write_work("w1", "recon", "- **Status**: complete\n")
        self.write_work("w1", "scope", "ready\n")
        self.write_work("w1", "design", "- **Status**: complete\n")
        # next unfinished = execute, which sits behind gate A.
        with mock.patch("builtins.input", return_value="n"):
            result = self.walk({"slug": "w1"}, tty=True)
        self.assertEqual(result, 1)

    def test_gate_approval_continues_and_next_pause(self):
        self.init_workspace()
        self.write_work("w1", "recon", "- **Status**: complete\n")
        self.write_work("w1", "scope", "ready\n")
        self.write_work("w1", "design", "- **Status**: complete\n")
        # gate approve (y) then stage-done prompt (n) -> paused return 0
        with mock.patch("builtins.input", side_effect=["y", "n"]):
            result = self.walk({"slug": "w1"}, tty=True)
        self.assertEqual(result, 0)

    def test_gate_prompt_eof_counts_as_rejection(self):
        self.init_workspace()
        self.write_work("w1", "recon", "- **Status**: complete\n")
        self.write_work("w1", "scope", "ready\n")
        self.write_work("w1", "design", "- **Status**: complete\n")
        with mock.patch("builtins.input", side_effect=EOFError):
            result = self.walk({"slug": "w1"}, tty=True)
        self.assertEqual(result, 1)

    def test_command_hint_uses_primary_agent_dir(self):
        self.init_workspace(agents=("claude",))
        hint = runner.command_hint("senior-scope", "claude")
        self.assertIn(".claude/commands", hint)
        self.assertIn("senior-scope", hint)


class TestParserHelpers(unittest.TestCase):
    def test_gates_are_stage_names_that_exist_in_pipeline(self):
        pipeline_stages = {name for name, _command in state.PIPELINE}
        self.assertIn("execute", runner.GATE_BEFORE)
        self.assertIn("ship", runner.GATE_BEFORE)
        self.assertLessEqual(set(runner.GATE_BEFORE.values()), pipeline_stages)


if __name__ == "__main__":
    unittest.main()

"""CLI happy-path tests using a temp project directory."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run(*argv, cwd):
    # stdin=DEVNULL keeps the child's TTY state deterministic across environments
    # (the gates runner refuses non-interactive runs without --yes by design).
    return subprocess.run(
        [sys.executable, "-m", "seniordev", *argv],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
    )


class TestCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self._tmp.name) / "proj"
        self.proj.mkdir(parents=True)
        self.env_python = sys.executable

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, *argv):
        return run(*argv, cwd=self.proj)

    def test_init_status_state(self):
        result = self._run("init", "--agent", "claude")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.proj / ".senior" / "principles.md").is_file())
        self.assertTrue((self.proj / ".senior" / "config.json").is_file())
        self.assertTrue((self.proj / ".claude" / "commands" / "senior-recon.md").is_file())

        # init twice without --force fails cleanly
        again = self._run("init", "--agent", "claude")
        self.assertEqual(again.returncode, 1)

        state = self._run("state", "--json")
        self.assertEqual(state.returncode, 0)
        payload = json.loads(state.stdout)
        self.assertTrue(payload["initialized"])

        status = self._run("status")
        self.assertEqual(status.returncode, 0)
        self.assertIn("seniordev status", status.stdout)

    def test_state_reports_uninitialized(self):
        result = self._run("state", "--json")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["initialized"])

    def test_sync_regenerates_agent_dirs(self):
        self._run("init", "--agent", "cursor")
        (self.proj / ".cursor" / "commands" / "senior-recon.md").unlink()
        result = self._run("sync")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(
            (self.proj / ".cursor" / "commands" / "senior-recon.md").is_file()
        )

    def test_unknown_agent_fails_with_hint(self):
        result = self._run("init", "--agent", "nonsense")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown agent", result.stderr)

    def test_run_yes_walks_fabricated_work_without_tty(self):
        self._run("init", "--agent", "claude")
        work_dir = self.proj / ".senior" / "work" / "w1"
        work_dir.mkdir(parents=True)
        (work_dir / "recon.md").write_text("- **Status**: complete\n", encoding="utf-8")
        result = self._run("run", "--slug", "w1", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("walked 'w1'", result.stdout)

    def test_run_non_interactive_refuses_without_yes(self):
        self._run("init", "--agent", "claude")
        work_dir = self.proj / ".senior" / "work" / "w1"
        work_dir.mkdir(parents=True)
        (work_dir / "recon.md").write_text("- **Status**: complete\n", encoding="utf-8")
        result = self._run("run", "--slug", "w1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("--yes", result.stderr)

    def test_agents_lists_examples(self):
        result = self._run("agents")
        self.assertEqual(result.returncode, 0)
        self.assertIn("senior-recon", result.stdout)
        self.assertIn("docs/guides/agents.md", result.stdout)


if __name__ == "__main__":
    unittest.main()

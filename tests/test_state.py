"""Tests for seniordev.state — deterministic pipeline routing."""

import tempfile
import unittest
from pathlib import Path

from seniordev import state


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "proj"
        self.senior = self.root / ".senior"
        self.senior.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def init_workspace(self):
        (self.senior / "config.json").write_text("{}", encoding="utf-8")
        for name in ("principles.md", "dossier.md", "decisions.md", "backlog.md"):
            (self.senior / name).write_text("# x\n", encoding="utf-8")

    def write_work(self, slug, name, content):
        work_dir = self.senior / "work" / slug
        work_dir.mkdir(parents=True, exist_ok=True)
        (work_dir / f"{name}.md").write_text(content, encoding="utf-8")


class TestNotInitialized(Base):
    def test_reports_uninitialized(self):
        gathered = state.gather(self.root)
        self.assertFalse(gathered["initialized"])


class TestWorkPipeline(Base):
    def test_next_command_follows_missing_artifacts(self):
        self.init_workspace()
        self.write_work("w1", "recon", "- **Status**: complete\n")
        item = state.gather(self.root)["work"][0]
        self.assertEqual(item["next_command"], "senior-scope")

    def test_pending_clarifications_route_to_decide(self):
        self.init_workspace()
        self.write_work("w1", "recon", "- **Status**: complete\n")
        self.write_work(
            "w1", "scope", "body with [NEEDS CLARIFICATION: auth method]\n"
        )
        item = state.gather(self.root)["work"][0]
        self.assertEqual(item["next_command"], "senior-decide")
        self.assertEqual(item["pending_clarifications"], 1)

    def test_clean_scope_routes_to_design(self):
        self.init_workspace()
        self.write_work("w1", "recon", "- **Status**: complete\n")
        self.write_work("w1", "scope", "nothing pending here\n")
        item = state.gather(self.root)["work"][0]
        self.assertEqual(item["next_command"], "senior-design")

    def test_ship_exists_means_complete(self):
        self.init_workspace()
        self.write_work("w1", "ship", "# Shipment\n")
        item = state.gather(self.root)["work"][0]
        self.assertTrue(item["complete"])
        self.assertIsNone(item["next_command"])


class TestBugPipeline(Base):
    def test_invalid_assessment_is_a_terminal_ok(self):
        self.init_workspace()
        bug_dir = self.senior / "bugs" / "b1"
        bug_dir.mkdir(parents=True)
        (bug_dir / "assessment.md").write_text(
            "- **Verdict**: invalid\n- **Severity**: low\n", encoding="utf-8"
        )
        item = state.gather(self.root)["bugs"][0]
        self.assertIsNone(item["next_command"])
        self.assertEqual(item["done_reason"], "assessed as not a bug")

    def test_valid_assessment_routes_to_fix(self):
        self.init_workspace()
        bug_dir = self.senior / "bugs" / "b1"
        bug_dir.mkdir(parents=True)
        (bug_dir / "assessment.md").write_text(
            "- **Verdict**: valid\n", encoding="utf-8"
        )
        item = state.gather(self.root)["bugs"][0]
        self.assertEqual(item["next_command"], "senior-bug-fix")

    def test_failed_test_routes_back_to_fix(self):
        self.init_workspace()
        bug_dir = self.senior / "bugs" / "b1"
        bug_dir.mkdir(parents=True)
        (bug_dir / "assessment.md").write_text("- **Verdict**: valid\n", encoding="utf-8")
        (bug_dir / "fix.md").write_text("# Bug Fix\n", encoding="utf-8")
        (bug_dir / "test.md").write_text(
            "- **Verdict**: failed\n", encoding="utf-8"
        )
        item = state.gather(self.root)["bugs"][0]
        self.assertEqual(item["next_command"], "senior-bug-fix")

    def test_verified_test_is_done(self):
        self.init_workspace()
        bug_dir = self.senior / "bugs" / "b1"
        bug_dir.mkdir(parents=True)
        (bug_dir / "assessment.md").write_text("- **Verdict**: valid\n", encoding="utf-8")
        (bug_dir / "fix.md").write_text("# Bug Fix\n", encoding="utf-8")
        (bug_dir / "test.md").write_text("- **Verdict**: verified\n", encoding="utf-8")
        item = state.gather(self.root)["bugs"][0]
        self.assertIsNone(item["next_command"])
        self.assertEqual(item["done_reason"], "fix verified")


class TestRecommendation(Base):
    def test_failing_bug_beats_open_work(self):
        self.init_workspace()
        self.write_work("w1", "recon", "- **Status**: complete\n")
        bug_dir = self.senior / "bugs" / "b1"
        bug_dir.mkdir(parents=True)
        (bug_dir / "assessment.md").write_text("- **Verdict**: valid\n", encoding="utf-8")
        action = state.next_action(state.gather(self.root))
        self.assertEqual(action["priority"], "failing-bug")
        self.assertEqual(action["item"]["slug"], "b1")


class TestChecklists(Base):
    def test_checklist_stats_count_checked_boxes(self):
        text = "- [ ] a\n- [x] b\n- [X] c\nplain line\n- [d not a checkbox"
        stats = state.checklist_stats(text)
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["checked"], 2)


if __name__ == "__main__":
    unittest.main()

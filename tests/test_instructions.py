"""Tests for write_managed_instructions — ambient agent workflow knowledge."""

import tempfile
import unittest
from pathlib import Path

from seniordev.cli import SECTION_BEGIN, SECTION_END, write_managed_instructions
from seniordev import integrations as integ


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "proj"
        self.root.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def read(self, rel):
        return (self.root / rel).read_text(encoding="utf-8")


class TestFreshCreation(Base):
    def test_claude_instructions_created(self):
        actions = write_managed_instructions(self.root, ["claude"])
        self.assertIn("created: CLAUDE.md (claude)", actions[0])
        text = self.read("CLAUDE.md")
        self.assertIn(SECTION_BEGIN, text)
        self.assertIn(SECTION_END, text)
        self.assertIn("recon (read before acting)", text)

    def test_cursor_rules_carry_frontmatter(self):
        write_managed_instructions(self.root, ["cursor"])
        text = self.read(".cursor/rules/seniordev.mdc")
        self.assertIn("alwaysApply: true", text)
        self.assertTrue(text.startswith("---"))

    def test_each_adapter_writes_its_own_ambient_file(self):
        write_managed_instructions(self.root, ["claude", "copilot", "cursor", "codex"])
        for rel, marker in (
            ("CLAUDE.md", "CLAUDE.md"),
            (".github/copilot-instructions.md", "copilot-instructions.md"),
            (".cursor/rules/seniordev.mdc", "seniordev.mdc"),
            ("AGENTS.md", "AGENTS.md"),
        ):
            self.assertTrue((self.root / rel).is_file(), rel)
            self.assertIn(SECTION_BEGIN, self.read(rel))
            _ = marker


class TestMerge(Base):
    def test_existing_human_content_preserved_and_section_appended(self):
        target = self.root / "CLAUDE.md"
        target.write_text("# My own rules\n\nKeep tests fast.\n", encoding="utf-8")
        write_managed_instructions(self.root, ["claude"])
        text = self.read("CLAUDE.md")
        self.assertIn("# My own rules", text)
        self.assertIn("Keep tests fast.", text)
        self.assertIn(SECTION_BEGIN, text)
        self.assertLess(text.index("# My own rules"), text.index(SECTION_BEGIN))

    def test_section_replaced_idempotently(self):
        write_managed_instructions(self.root, ["claude"])
        first = self.read("CLAUDE.md")
        # user adds their own note inside? above; then re-render
        self.root.joinpath("CLAUDE.md").write_text(
            first + "\nHuman note added later.\n", encoding="utf-8"
        )
        write_managed_instructions(self.root, ["claude"])
        text = self.read("CLAUDE.md")
        self.assertEqual(text.count(SECTION_BEGIN), 1)
        self.assertIn("Human note added later.", text)

    def test_sync_does_not_touch_generic_agents_md_unless_requested(self):
        write_managed_instructions(self.root, ["claude"])
        self.assertFalse((self.root / "AGENTS.md").is_file())


if __name__ == "__main__":
    unittest.main()

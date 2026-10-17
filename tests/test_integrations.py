"""Tests for seniordev.integrations rendering."""

import unittest

from seniordev import integrations


class TestRender(unittest.TestCase):
    def test_every_adapter_has_unique_key_and_required_fields(self):
        for key, integration in integrations.INTEGRATIONS.items():
            self.assertEqual(key, integration.key)
            self.assertTrue(integration.directory)
            self.assertTrue(integration.invocation)

    def test_command_file_name_uses_extension(self):
        copilot = integrations.INTEGRATIONS["copilot"]
        name = integrations.command_file_name("senior-recon", copilot)
        self.assertEqual(name, "senior-recon.prompt.md")
        claude = integrations.INTEGRATIONS["claude"]
        self.assertEqual(
            integrations.command_file_name("senior-recon", claude), "senior-recon.md"
        )

    def test_every_adapter_has_example_mentioning_two_or_more_stages(self):
        self.maxDiff = None
        for key, integration in integrations.INTEGRATIONS.items():
            self.assertTrue(
                integration.example.strip(), f"{key} has an empty example"
            )
            stages = sum(
                1
                for token in (
                    "recon", "scope", "decide", "design", "execute",
                    "review", "verify", "ship",
                )
                if token in integration.example
            )
            self.assertGreaterEqual(
                stages, 2, f"{key} example should chain at least two stages"
            )

    def test_identity_render_keeps_dollar_arguments(self):
        generic = integrations.INTEGRATIONS["generic"]
        source = "## Arguments\n\n```text\n$ARGUMENTS\n```"
        self.assertEqual(integrations.render_command(source, generic), source)

    def test_copilot_substitutes_argument_token_only(self):
        copilot = integrations.INTEGRATIONS["copilot"]
        source = (
            "---\ndescription: recon\n---\n\n## Arguments\n\n```text\n$ARGUMENTS\n```\n"
        )
        rendered = integrations.render_command(source, copilot)
        self.assertNotIn("$ARGUMENTS", rendered)
        self.assertIn("${input:arguments}", rendered)
        self.assertIn("description: recon", rendered)


if __name__ == "__main__":
    unittest.main()

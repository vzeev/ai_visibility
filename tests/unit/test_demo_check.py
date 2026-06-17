from __future__ import annotations

import contextlib
import io
import unittest

from scripts.ai_visibility_tools import demo_check


class DemoCheckTests(unittest.TestCase):
    def test_demo_check_files_are_present(self) -> None:
        self.assertEqual([], demo_check._validate_files())

    def test_demo_check_commands_only_prints_walkthrough(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = demo_check.main(("--commands-only",))

        self.assertEqual(0, result)
        self.assertIn("Brandlight demo walkthrough commands", output.getvalue())
        self.assertIn("docs/demo/main-flow.md", output.getvalue())


if __name__ == "__main__":
    unittest.main()

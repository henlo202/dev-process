"""Conformance checker: configurable requirement ID prefixes (v0.5.0).

    python -m unittest discover -s tooling/tests
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIREMENTS = """---
artefact: requirements
status: approved
version: 1.0.0
owner: Analyst agent
updated: 2026-10-19
---
# Requirements: core

### SYS-001 — Runs locally
- **Status:** Approved

### API-002: Health endpoint
- **Status:** approved

### REQ-003: Classic ID
- **Status:** approved
"""

TESTS = """import pytest

@pytest.mark.req("SYS-001")
def test_runs_locally():
    assert "SHA-256" and "[API-002] in a title" and "UI-099"
"""


# Angle brackets inside inline code and fenced blocks are syntax, not template placeholders.
CODE_SNIPPETS = """
Run `garmin-sync --player <name or id> recent`.

```
auth.py --player <player id>
```
"""


class RequirementPrefixes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "proj"
        subprocess.run([sys.executable, str(ROOT / "tooling" / "scaffold.py"), str(self.repo), "--tier", "T2"],
                       capture_output=True, check=True)
        (self.repo / "docs" / "requirements" / "core.md").write_text(REQUIREMENTS, encoding="utf-8")
        (self.repo / "tests").mkdir(exist_ok=True)
        (self.repo / "tests" / "test_core.py").write_text(TESTS, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def set_prefixes(self, value: str):
        path = self.repo / ".process" / "config.yaml"
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if not l.startswith("requirement_id_prefixes")]
        lines.append(f"requirement_id_prefixes: {value}")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def report(self) -> str:
        r = subprocess.run([sys.executable, str(self.repo / ".process" / "check.py"), "--project", str(self.repo)],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_default_prefixes_are_req_and_nfr(self):
        text = self.report()
        self.assertIn("`REQ-003`", text)
        self.assertNotIn("`SYS-001`", text)
        self.assertNotIn("SHA-256", text)

    def test_configured_prefixes_define_and_trace_requirements(self):
        self.set_prefixes("[SYS, API, UI]")
        text = self.report()
        self.assertRegex(text, r"\| `SYS-001` \| approved \| ✅ 1 \|")
        self.assertRegex(text, r"\| `API-002` \| approved \| ✅ 1 \|")  # reference inside a title
        self.assertNotIn("`REQ-003`", text)  # REQ is not configured for this project
        self.assertIn("unknown-requirement:UI-099", text)  # configured prefix, undefined ID
        self.assertNotIn("SHA-256", text)  # not a configured prefix, so never an ID

    def test_placeholders_in_code_are_not_template_placeholders(self):
        brief = self.repo / "docs" / "brief.md"
        brief.write_text(brief.read_text(encoding="utf-8") + CODE_SNIPPETS, encoding="utf-8")
        text = self.report()
        self.assertIn("placeholder:docs/brief.md", text)  # the template's own placeholders remain
        self.assertNotIn("<name or id>", text)
        self.assertNotIn("<player id>", text)

    def test_invalid_prefixes_fall_back_to_the_default(self):
        self.set_prefixes("[sys, 'A-B']")
        text = self.report()
        self.assertIn("config-invalid:requirement_id_prefixes", text)
        self.assertIn("`REQ-003`", text)


if __name__ == "__main__":
    unittest.main()

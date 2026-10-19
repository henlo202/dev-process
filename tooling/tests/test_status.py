"""Walks a scaffolded project through the whole loop with .process/status.py.

    python -m unittest discover -s tooling/tests
"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class StatusLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "proj"
        subprocess.run([sys.executable, str(ROOT / "tooling" / "scaffold.py"), str(self.repo), "--tier", "T2"],
                       capture_output=True, check=True)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        self.commit_all("chore: adopt")

    def tearDown(self):
        self.tmp.cleanup()

    # helpers
    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, text=True, check=True)

    def commit_all(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", msg)

    def status(self):
        out = subprocess.run([sys.executable, ".process/status.py", "--json"], cwd=self.repo,
                             capture_output=True, text=True, check=True).stdout
        return json.loads(out)

    def record(self, *args):
        return subprocess.run([sys.executable, ".process/status.py", "record-gate", *args], cwd=self.repo,
                              capture_output=True, text=True)

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def edit(self, rel, old, new):
        path = self.repo / rel
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))

    def fill_placeholders(self, rel):
        path = self.repo / rel
        path.write_text(re.sub(r"<(?!!--)[A-Za-z][^<>=\"`\n]*\s[^<>=\"`\n]*>", "filled", path.read_text()))

    def review(self, name):
        self.write(f"docs/reviews/{name}.md", "---\nartefact: reviewer-summary\nstatus: done\nupdated: 2026-10-19\n---\n"
                                              "# Review\nReady.\n")

    def assertStep(self, actor, phase, contains, **fields):
        s = self.status()
        self.assertEqual((s["actor"], s["phase"]), (actor, phase), s)
        self.assertIn(contains, s["action"], s)
        for k, v in fields.items():
            self.assertEqual(s[k], v, s)
        return s

    def test_full_loop(self):
        # P0
        self.assertStep("agent", "P0", "Complete P0", skill="dev-process-analyst")
        for f in ("docs/brief.md", "AGENTS.md", "docs/standards.md"):
            self.fill_placeholders(f)
        self.edit("docs/brief.md", "status: draft", "status: in-review")
        self.assertStep("agent", "P0", "Review the brief", skill="dev-process-reviewer")
        self.review("G0")
        self.assertStep("owner", "P0", "go / no-go", gate="G0")
        self.assertNotEqual(self.record("G1", "--increment", "INC-001", "--decision", "approved",
                                        "--statement", "yes").returncode, 0, "only the pending gate may be recorded")
        r = self.record("G0", "--decision", "approved", "--statement", "Go for it.")
        self.assertEqual(r.returncode, 0, r.stdout)
        gate = next((self.repo / "docs" / "gates").glob("G0-*.md")).read_text()
        self.assertIn("owner_statement: Go for it.", gate)
        self.assertIn("recorded_by: agent", gate)

        # P1: the scaffolded INC-001 is a draft
        self.assertStep("agent", "P1", "Shape INC-001", skill="dev-process-shape-increment")
        inc = "docs/increments/INC-001-walking-skeleton.md"
        self.fill_placeholders(inc)
        self.edit(inc, "status: draft", "status: in-review")
        self.edit(inc, "- [ ] S1: filled (REQ-)", "- [ ] S1: core path (REQ-001)\n- [ ] S2: docs (REQ-001)")
        self.assertStep("agent", "P1", "Review INC-001", skill="dev-process-reviewer")
        self.review("G1-INC-001")
        self.assertStep("owner", "P1", "shape of INC-001", gate="G1", increment="INC-001")
        r = self.record("G1", "--increment", "INC-001", "--decision", "approved", "--statement", "Approved.")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("status: approved", (self.repo / inc).read_text())
        self.commit_all("docs: shape INC-001")

        # P2: slices one by one, on feature branches
        self.assertStep("agent", "P2", "Build slice S1", skill="dev-process-implementer")
        self.git("switch", "-q", "-c", "task/INC-001-S1-core")
        self.edit(inc, "- [ ] S1:", "- [x] S1:")
        self.commit_all("feat: core path (REQ-001)")
        self.assertStep("agent", "P2", "Build slice S2")
        self.edit(inc, "- [ ] S2:", "- [x] S2:")
        self.write("CHANGELOG.md", "# Changelog\n\n## [Unreleased]\n### Added\n- Core path (REQ-001)\n")
        self.commit_all("docs: user docs (REQ-001)")

        # P3: demo, then the Owner merges (G2)
        self.assertStep("agent", "P3", "Record the demo", skill="dev-process-demo")
        self.edit(inc, "## Demo\n", "## Demo\n```\n$ app run\nHello, world! (exit 0)\n```\n")
        self.commit_all("docs: demo for INC-001")
        s = self.assertStep("owner", "P3", "merge the pull request", gate="G2", increment="INC-001")
        self.assertIn("task/INC-001-S1-core", s["evidence"])
        self.assertNotEqual(self.record("G2", "--decision", "approved", "--statement", "x").returncode, 0)
        self.git("switch", "-q", "main")
        self.git("merge", "-q", "--no-ff", "-m", "Merge INC-001", "task/INC-001-S1-core")
        self.assertStep("agent", "P3", "Set INC-001 to status `done`")
        self.edit(inc, "status: approved", "status: done")
        self.commit_all("docs: INC-001 done")

        # P4: release
        self.assertStep("agent", "P4", "Prepare a release", skill="dev-process-documenter")
        self.write("CHANGELOG.md", "# Changelog\n\n## [Unreleased]\n\n## [0.1.0] - 2026-10-19\n### Added\n- Core path\n")
        self.commit_all("docs: release 0.1.0")
        self.assertStep("agent", "P4", "Review release 0.1.0", release="0.1.0")
        self.review("G3-0.1.0")
        self.assertStep("owner", "P4", "releasing 0.1.0", gate="G3", release="0.1.0")
        self.assertEqual(self.record("G3", "--release", "0.1.0", "--decision", "approved",
                                     "--statement", "Ship it.").returncode, 0)
        self.assertStep("agent", "P4", "Tag and publish release 0.1.0")
        self.commit_all("docs: G3 for 0.1.0")
        self.git("tag", "-a", "v0.1.0", "-m", "v0.1.0")

        # P5: learnings, then back to the Owner for the next outcome
        self.assertStep("agent", "P5", "Draft the Learnings for INC-001")
        self.edit(inc, "## Learnings\n", "## Learnings\n- The walking skeleton was quick.\n")
        self.assertStep("owner", "P1", "outcome you want next")

    def test_rejected_shape_goes_back_to_draft(self):
        for f in ("docs/brief.md", "AGENTS.md", "docs/standards.md"):
            self.fill_placeholders(f)
        self.edit("docs/brief.md", "status: draft", "status: in-review")
        self.review("G0")
        self.record("G0", "--decision", "approved", "--statement", "Go.")
        inc = "docs/increments/INC-001-walking-skeleton.md"
        self.fill_placeholders(inc)
        self.edit(inc, "status: draft", "status: in-review")
        self.review("G1-INC-001")
        r = self.record("G1", "--increment", "INC-001", "--decision", "rejected", "--statement", "Too big, split it.")
        self.assertEqual(r.returncode, 0)
        self.assertIn("status: draft", (self.repo / inc).read_text())
        self.assertStep("agent", "P1", "Shape INC-001")


if __name__ == "__main__":
    unittest.main()

"""Tests for tooling/workbench.py: the live, read-only web view of a project."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("workbench", ROOT / "tooling" / "workbench.py")
wb = importlib.util.module_from_spec(spec)
sys.modules["workbench"] = wb
spec.loader.exec_module(wb)


class MarkdownTest(unittest.TestCase):
    def test_html_is_escaped(self):
        out = wb.render_markdown("# T <script>alert(1)</script>\n\nhello <img src=x onerror=y> `<b>`")
        self.assertNotIn("<script>", out)
        self.assertNotIn("<img", out)
        self.assertIn("&lt;script&gt;", out)

    def test_blocks(self):
        out = wb.render_markdown("---\nstatus: draft\n---\n# Title\n\n- a\n  - b\n- [x] done\n\n| h1 | h2 |\n|---|---|\n| 1 | 2 |\n\n```py\nx<1\n```\n")
        for part in ("<h1", "<ul>", "<li class=\"task\">", "<table>", "<th>h1</th>", "x&lt;1"):
            self.assertIn(part, out)
        self.assertNotIn("status: draft", out)

    def test_requirement_heading_gets_anchor(self):
        self.assertIn('<a id="req-016"></a>', wb.render_markdown("### REQ-016: Hours"))


class SafePathTest(unittest.TestCase):
    def test_only_markdown_and_images_inside_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "p"
            (root / "docs").mkdir(parents=True)
            (root / ".process").mkdir()
            (root / "docs" / "a.md").write_text("# a", encoding="utf-8")
            (root / "docs" / "secrets.md").write_text("x", encoding="utf-8")
            (root / "docs" / "run.py").write_text("x", encoding="utf-8")
            (root / ".process" / "n.md").write_text("x", encoding="utf-8")
            (Path(tmp) / "outside.md").write_text("x", encoding="utf-8")
            self.assertIsNotNone(wb.safe_path(root, "docs/a.md"))
            for bad in ("docs/secrets.md", "docs/run.py", ".process/n.md", "../outside.md", "docs/../../outside.md", "docs", ""):
                self.assertIsNone(wb.safe_path(root, bad), bad)


class FullProjectTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name) / "proj"
        subprocess.run([sys.executable, str(ROOT / "tooling" / "scaffold.py"), str(cls.root), "--tier", "T2"],
                       capture_output=True, check=True)
        (cls.root / "docs" / "adr").mkdir(parents=True, exist_ok=True)
        (cls.root / "docs" / "adr" / "0001-x.md").write_text(
            "---\nartefact: adr\nstatus: approved\nupdated: 2026-01-01\n---\n# ADR-0001: Use SQLite\n", encoding="utf-8")
        cls.site = wb.Site([wb.detect(cls.root)])
        cls.slug = next(iter(cls.site.models))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        (self.root / "docs" / "requirements").mkdir(parents=True, exist_ok=True)
        (self.root / "docs" / "requirements" / "core.md").write_text(
            "# Reqs\n\n### REQ-001: Export CSV\n- **Priority:** must\n- **Status:** draft\n", encoding="utf-8")

    def get(self, rest):
        code, ctype, body = self.site.route(f"/p/{self.slug}/{rest}")
        return code, body.decode("utf-8", "replace")

    def test_pages_render_from_files(self):
        code, page = self.get("")
        self.assertEqual(code, 200)
        self.assertIn("P0 Initiate", page)
        self.assertIn("Complete P0", page)  # the same next step status.py reports
        self.assertIn("REQ-001", self.get("requirements")[1])
        self.assertIn("Use SQLite", self.get("decisions")[1])
        self.assertEqual(self.get("increments")[0], 200)
        self.assertEqual(self.get("docs")[0], 200)
        self.assertIn("Export CSV", self.get("doc/docs/requirements/core.md")[1])

    def test_live_not_cached(self):
        before = self.site.models[self.slug].fingerprint()
        (self.root / "docs" / "requirements" / "core.md").write_text("# Reqs\n\n### REQ-002: New one\n", encoding="utf-8")
        self.assertIn("REQ-002", self.get("requirements")[1])
        self.assertNotEqual(before, self.site.models[self.slug].fingerprint())

    def test_status_json_matches_status_py(self):
        out = subprocess.run([sys.executable, ".process/status.py", "--json"], cwd=self.root, capture_output=True, text=True, check=True).stdout
        data = json.loads(self.get("api/status")[1])
        self.assertEqual(data["next"]["action"], json.loads(out)["action"])

    def test_refuses_outside_files(self):
        for rest in ("doc/.process/config.yaml", "raw/.git/config", "doc/..%2f..%2fx.md", "nope"):
            self.assertEqual(self.get(rest)[0], 404, rest)

    def test_http_is_read_only(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), wb.make_handler(self.site))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        base = f"http://127.0.0.1:{server.server_address[1]}"
        self.assertEqual(urllib.request.urlopen(f"{base}/p/{self.slug}/").status, 200)
        req = urllib.request.Request(f"{base}/p/{self.slug}/", data=b"x", method="POST")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 405)


class ExampleProjectTest(unittest.TestCase):
    def test_worked_example_renders(self):
        example = ROOT / "examples" / "greeter-cli"
        site = wb.Site([wb.detect(example)])
        slug = next(iter(site.models))
        for rest in ("", "requirements", "decisions", "increments", "docs"):
            self.assertEqual(site.route(f"/p/{slug}/{rest}")[0], 200, rest)


if __name__ == "__main__":
    unittest.main()

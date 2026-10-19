import ast
import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from greeter.cli import main  # noqa: E402


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


class GreetTests(unittest.TestCase):
    def test_REQ_001_greets_by_name(self):  # AC-001.1
        self.assertEqual(run("Ada"), (0, "Hello, Ada!\n", ""))

    def test_REQ_002_greets_in_swedish(self):  # AC-002.1
        self.assertEqual(run("Ada", "--lang", "sv"), (0, "Hej, Ada!\n", ""))

    def test_REQ_003_rejects_empty_name(self):  # AC-003.1
        for name in ("", "   "):
            code, out, err = run(name)
            self.assertEqual(code, 2)
            self.assertEqual(out, "")
            self.assertIn("must not be empty", err)


class DependencyTests(unittest.TestCase):
    def test_NFR_001_standard_library_only(self):  # AC-NFR-001.1
        src = Path(__file__).resolve().parent.parent / "src" / "greeter"
        allowed = set(sys.stdlib_module_names) | {"greeter"}
        for py in src.glob("*.py"):
            for node in ast.walk(ast.parse(py.read_text())):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                for n in names:
                    self.assertIn(n.split(".")[0], allowed, f"{py.name} imports {n}")


if __name__ == "__main__":
    unittest.main()

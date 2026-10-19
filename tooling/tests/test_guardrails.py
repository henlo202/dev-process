"""End-to-end tests for the guardrails, run against a real temporary git repository.

    python -m unittest discover -s tooling/tests
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tooling" / "guardrails"))

import guard  # noqa: E402


def git(repo, *args, env=None, check=False):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          env={**os.environ, **(env or {})}, check=check)


class GuardrailsInRepo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.remote = base / "remote.git"
        self.repo = base / "project"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.remote)], check=True)
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.repo)], check=True)
        git(self.repo, "config", "user.name", "Test", check=True)
        git(self.repo, "config", "user.email", "test@example.com", check=True)
        git(self.repo, "remote", "add", "origin", str(self.remote), check=True)
        subprocess.run([sys.executable, str(ROOT / "tooling" / "scaffold.py"), str(self.repo), "--tier", "T2",
                        "--guardrails", "block", "--adapter", "claude"], capture_output=True, check=True)
        # Seed main without hooks, as an existing project would have.
        git(self.repo, "add", "-A", check=True)
        git(self.repo, "commit", "-q", "-m", "chore: adopt dev-process", check=True)
        git(self.repo, "push", "-q", "origin", "main", check=True)
        git(self.repo, "config", "core.hooksPath", ".process/guardrails/git-hooks", check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def set_config(self, **guardrails):
        path = self.repo / ".process" / "config.yaml"
        text = path.read_text()
        for key, value in guardrails.items():
            lines = [l if not l.lstrip().startswith(f"{key}:") else f"  {key}: {value}" for l in text.splitlines()]
            text = "\n".join(lines) + "\n"
        path.write_text(text)

    def commit(self, message, env=None):
        (self.repo / "file.txt").write_text(message)
        git(self.repo, "add", "file.txt")
        return git(self.repo, "commit", "-m", message, env=env)

    def test_commit_on_protected_branch_is_refused(self):
        r = self.commit("feat: on main")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("protected branch `main`", r.stderr)

    def test_commit_message_convention(self):
        git(self.repo, "switch", "-q", "-c", "task/INC-001-S1-x", check=True)
        bad = self.commit("did some stuff")
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("does not follow the convention", bad.stderr)
        self.assertEqual(self.commit("feat: greet by name (REQ-001)").returncode, 0)

    def test_push_rules(self):
        git(self.repo, "switch", "-q", "-c", "task/INC-001-S1-x", check=True)
        self.assertEqual(self.commit("feat: something").returncode, 0)
        self.assertEqual(git(self.repo, "push", "-q", "origin", "task/INC-001-S1-x").returncode, 0)
        to_main = git(self.repo, "push", "origin", "HEAD:main")
        self.assertNotEqual(to_main.returncode, 0)
        self.assertIn("protected branch `main`", to_main.stderr)
        badly_named = git(self.repo, "push", "origin", "HEAD:my-branch")
        self.assertNotEqual(badly_named.returncode, 0)
        self.assertIn("does not match", badly_named.stderr)

    def test_lint_command_blocks_commit(self):
        git(self.repo, "switch", "-q", "-c", "task/INC-001-S1-x", check=True)
        self.set_config(lint_command='"exit 1"')
        r = self.commit("feat: lint fails")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("lint/format check failed", r.stderr)

    def test_warn_mode_allows_but_reports(self):
        self.set_config(mode="warn")
        r = self.commit("not conventional, on main")
        self.assertEqual(r.returncode, 0)
        self.assertIn("warning for commit", r.stderr)

    def test_owner_override(self):
        r = self.commit("chore: hotfix on main", env={"DEV_PROCESS_OWNER_OVERRIDE": "1"})
        self.assertEqual(r.returncode, 0)
        self.assertIn("Owner override active", r.stderr)

    def test_ci_checks_commit_range(self):
        git(self.repo, "switch", "-q", "-c", "task/INC-001-S1-x", check=True)
        self.commit("feat: fine")
        self.commit("wip", env={"DEV_PROCESS_OWNER_OVERRIDE": "1"})
        r = subprocess.run(["sh", ".process/guardrails/ci-guardrails.sh", "main"], cwd=self.repo,
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('"wip"', r.stderr)

    def test_claude_adapter_blocks_agent_commands(self):
        hook = self.repo / ".process" / "adapters" / "claude" / "pre_tool_use.py"
        settings = json.loads((self.repo / ".claude" / "settings.json").read_text())
        self.assertIn("pre_tool_use.py", json.dumps(settings))
        self.assertTrue((self.repo / ".claude" / "skills" / "dev-process-implementer" / "SKILL.md").is_file())

        def run(command):
            event = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
            return subprocess.run([sys.executable, str(hook)], input=event, capture_output=True, text=True,
                                  cwd=self.repo)

        for blocked in ["git push origin main", "git push -f origin HEAD:main", "git commit --no-verify -m x",
                        "git -c core.hooksPath=/dev/null commit -m x", "gh pr merge 3 --squash",
                        "DEV_PROCESS_OWNER_OVERRIDE=1 git push origin main"]:
            r = run(blocked)
            self.assertEqual(r.returncode, 2, blocked)
            self.assertIn("Blocked by dev-process guardrails", r.stderr)
        for allowed in ["git push -u origin task/INC-001-S1-x", "pytest -q",
                        "git config core.hooksPath .process/guardrails/git-hooks",
                        "cd app && git config core.hooksPath .process/guardrails/git-hooks && git status"]:
            self.assertEqual(run(allowed).returncode, 0, allowed)


class CheckCommandUnit(unittest.TestCase):
    cfg = {**guard.DEFAULTS, "agent_blocked_commands": [r"\bterraform\s+apply\b"]}

    def test_project_blocked_patterns(self):
        self.assertTrue(guard.check_command("cd infra && terraform apply -auto-approve", self.cfg))
        self.assertFalse(guard.check_command("terraform plan", self.cfg))

    def test_push_targets(self):
        self.assertTrue(guard.check_command("git push origin +task/x:main", self.cfg))
        self.assertTrue(guard.check_command("git push origin refs/heads/master", self.cfg))
        self.assertFalse(guard.check_command("git push origin task/main-menu", self.cfg))


if __name__ == "__main__":
    unittest.main()

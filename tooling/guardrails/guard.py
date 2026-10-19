#!/usr/bin/env python3
"""dev-process guardrails: hard enforcement of a project's engineering rules.

Copied into projects as .process/guardrails/guard.py and called from the git
hooks in .process/guardrails/git-hooks/, from CI, and from agent-tool adapters.
Rules are configured in the `guardrails` section of .process/config.yaml.

    guard.py commit-msg FILE      # commit message convention
    guard.py pre-commit           # no commits on protected branches; lint
    guard.py pre-push             # no pushes to protected branches; branch naming (refs on stdin)
    guard.py ci [--base REF]      # lint + commit messages since REF (for CI)
    guard.py check-command CMD    # is this shell command allowed for an agent? (adapters)

mode: block -> violations exit 1 (the action is refused).
mode: warn  -> violations are printed, exit 0.
The Owner can bypass hooks for one command with DEV_PROCESS_OWNER_OVERRIDE=1.
Agents must never do so; agent adapters refuse commands that try.

Requires: Python 3.9+, PyYAML (if PyYAML is missing, guardrails warn and allow).
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

DEFAULTS = {
    "mode": "warn",
    "protected_branches": ["main", "master"],
    "branch_pattern": r"^(task|fix|spike|docs|chore|release)/[A-Za-z0-9._/-]+$",
    "commit_pattern": r"^(feat|fix|docs|test|refactor|perf|build|ci|chore|style|revert|spike)(\([^)]+\))?!?: .+",
    "lint_command": "",
    "agent_blocked_commands": [],
}
ALWAYS_ALLOWED_SUBJECTS = re.compile(r"^(Merge |Revert \"|fixup! |squash! |amend! )")
ZERO_SHA = re.compile(r"^0+$")
# Commands an agent may never run, whatever the mode (see guides/agent-autonomy.md).
AGENT_NEVER = [
    (r"--no-verify\b", "bypasses git hooks"),
    (r"\bcore\.hooksPath\b(?!\s+\.process/guardrails/git-hooks/?(?:\s|;|&|\||$))", "changes where git hooks are loaded from"),
    (r"\bDEV_PROCESS_OWNER_OVERRIDE\b", "uses the Owner-only override"),
    (r"\bgh\s+pr\s+merge\b", "merges a pull request (Owner only, gate G2)"),
    (r"\bgh\s+pr\s+review\b.*--approve", "approves a pull request (Owner only)"),
]


def utf8_stdio() -> None:
    """Print UTF-8 even where the console or pipe encoding cannot (e.g. cp1252 on Windows)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def repo_root() -> Path:
    """The nearest directory (from cwd upwards) with .process/config.yaml, else the git top level."""
    for d in [Path.cwd(), *Path.cwd().parents]:
        if (d / ".process" / "config.yaml").is_file():
            return d
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def load_config(root: Path) -> dict:
    cfg = dict(DEFAULTS)
    path = root / ".process" / "config.yaml"
    try:
        import yaml
    except ImportError:
        print("dev-process guardrails: PyYAML missing (pip install pyyaml); using warn mode.", file=sys.stderr)
        return cfg
    if path.is_file():
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        cfg.update({k: v for k, v in (data.get("guardrails") or {}).items() if v is not None})
    if cfg["mode"] not in ("warn", "block"):
        cfg["mode"] = "warn"
    return cfg


def current_branch() -> str:
    out = subprocess.run(["git", "symbolic-ref", "--quiet", "--short", "HEAD"], capture_output=True, text=True)
    return out.stdout.strip()


def finish(violations: list[str], cfg: dict, action: str) -> int:
    if not violations:
        return 0
    if os.environ.get("DEV_PROCESS_OWNER_OVERRIDE") == "1":
        print(f"dev-process guardrails: Owner override active, allowing {action} despite:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 0
    blocking = cfg["mode"] == "block"
    print(f"dev-process guardrails: {'refusing' if blocking else 'warning for'} {action}:", file=sys.stderr)
    for v in violations:
        print(f"  ✖ {v}", file=sys.stderr)
    print("  Rules: docs/standards.md · config: .process/config.yaml (guardrails)", file=sys.stderr)
    return 1 if blocking else 0


def check_subject(subject: str, cfg: dict) -> str | None:
    if ALWAYS_ALLOWED_SUBJECTS.match(subject) or re.match(cfg["commit_pattern"], subject):
        return None
    return f"commit message \"{subject}\" does not follow the convention (pattern: {cfg['commit_pattern']})"


def run_lint(cfg: dict, root: Path) -> list[str]:
    cmd = (cfg.get("lint_command") or "").strip()
    if not cmd:
        return []
    result = subprocess.run(cmd, shell=True, cwd=root)
    return [] if result.returncode == 0 else [f"lint/format check failed: `{cmd}`"]


def cmd_commit_msg(path: str, cfg: dict) -> int:
    lines = [l for l in Path(path).read_text(encoding="utf-8").splitlines() if not l.startswith("#")]
    subject = next((l for l in lines if l.strip()), "")
    problem = check_subject(subject, cfg)
    return finish([problem] if problem else [], cfg, "commit")


def cmd_pre_commit(cfg: dict, root: Path) -> int:
    violations = []
    branch = current_branch()
    if branch in cfg["protected_branches"]:
        violations.append(f"committing directly on protected branch `{branch}`; use a feature branch")
    violations += run_lint(cfg, root)
    return finish(violations, cfg, "commit")


def cmd_pre_push(cfg: dict, stdin_lines: list[str]) -> int:
    violations = []
    for line in stdin_lines:
        parts = line.split()
        if len(parts) != 4:
            continue
        _local_ref, local_sha, remote_ref, _remote_sha = parts
        if ZERO_SHA.match(local_sha) or not remote_ref.startswith("refs/heads/"):
            continue  # deletions and tags are not checked
        branch = remote_ref[len("refs/heads/"):]
        if branch in cfg["protected_branches"]:
            violations.append(f"pushing to protected branch `{branch}`; push a feature branch and open a pull request")
        elif not re.match(cfg["branch_pattern"], branch):
            violations.append(f"branch name `{branch}` does not match {cfg['branch_pattern']}")
    return finish(violations, cfg, "push")


def cmd_ci(cfg: dict, root: Path, base: str | None) -> int:
    violations = run_lint(cfg, root)
    if base:
        out = subprocess.run(["git", "log", "--no-merges", "--format=%s", f"{base}..HEAD"],
                             capture_output=True, text=True, cwd=root)
        for subject in out.stdout.splitlines():
            problem = check_subject(subject, cfg)
            if problem:
                violations.append(problem)
    return finish(violations, cfg, "this change")


def check_command(command: str, cfg: dict) -> list[str]:
    """Violations for a shell command an agent wants to run. Used by agent adapters."""
    violations = [f"`{command}` {why}" for pattern, why in AGENT_NEVER if re.search(pattern, command)]
    for pattern in cfg.get("agent_blocked_commands") or []:
        if re.search(pattern, command):
            violations.append(f"`{command}` matches the project's blocked pattern `{pattern}`")
    for segment in re.split(r"&&|\|\||;|\n", command):
        try:
            words = shlex.split(segment)
        except ValueError:
            words = segment.split()
        if len(words) >= 2 and words[0] == "git" and "push" in words[1:3]:
            targets = [w.split(":")[-1].removeprefix("refs/heads/").lstrip("+") for w in words[2:] if not w.startswith("-")]
            force = any(w in ("-f", "--force") or w.startswith("--force-with-lease") or w.startswith("+") for w in words)
            for branch in cfg["protected_branches"]:
                if branch in targets[1:] or (len(targets) == 1 and targets[0] == branch):
                    violations.append(f"`{segment.strip()}` pushes to protected branch `{branch}`")
                    break
            else:
                if force and not targets[1:] and current_branch() in cfg["protected_branches"]:
                    violations.append(f"`{segment.strip()}` force-pushes a protected branch")
    return violations


def main(argv=None) -> int:
    utf8_stdio()
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 0
    root = repo_root()
    cfg = load_config(root)
    sub, args = argv[0], argv[1:]
    if sub == "commit-msg" and args:
        return cmd_commit_msg(args[0], cfg)
    if sub == "pre-commit":
        return cmd_pre_commit(cfg, root)
    if sub == "pre-push":
        return cmd_pre_push(cfg, sys.stdin.read().splitlines())
    if sub == "ci":
        base = args[args.index("--base") + 1] if "--base" in args else None
        return cmd_ci(cfg, root, base)
    if sub == "check-command" and args:
        problems = check_command(" ".join(args), cfg)
        for p in problems:
            print(f"✖ {p}")
        return 1 if problems else 0
    print(f"unknown or incomplete command: {' '.join(argv)}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

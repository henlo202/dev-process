#!/usr/bin/env python3
"""Adopt (or upgrade) dev-process in a project.

New project / adoption:
    python tooling/scaffold.py PATH --name "My project" --tier T2 \
        [--guardrails warn|block] [--adapter claude] [--github] [--install-hooks]

Upgrade an adopted project to this checkout's process version:
    python tooling/scaffold.py PATH --upgrade [--adapter claude] [--install-hooks]

Never overwrites existing artefacts; it reports them as skipped. Everything in
.process/ except config.yaml, and installed adapter skill copies, are managed
and refreshed on every run.
Requires: Python 3.9+, PyYAML.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ADAPTERS = ("claude",)

# Where to put the first file when an artefact's path is a folder.
FOLDER_SEEDS = {
    "increment": "INC-001-walking-skeleton.md",
    "requirements": "core.md",
    "user-docs": "index.md",
}


def load_process() -> dict:
    return yaml.safe_load((ROOT / "process.yaml").read_text(encoding="utf-8"))


def render(template: Path, values: dict) -> str:
    text = template.read_text(encoding="utf-8")
    for key, val in values.items():
        text = text.replace("{{" + key + "}}", val)
    return text


def write_new(path: Path, content: str, created: list, skipped: list, root: Path):
    rel = path.relative_to(root).as_posix()
    if path.exists():
        skipped.append(rel)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(rel)


def copy_tree(src: Path, dest: Path):
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def install_skills(process: dict, dest: Path):
    """Copy every dev-process skill folder, plus its bundled templates, into dest/."""
    dest.mkdir(parents=True, exist_ok=True)
    for old in dest.glob("dev-process-*"):
        shutil.rmtree(old)
    for skill in process["skills"]:
        src_dir = ROOT / Path(skill["doc"]).parent
        target = dest / skill["id"]
        shutil.copytree(src_dir, target)
        for bundled in skill["bundle"]:
            shutil.copy2(ROOT / bundled, target / Path(bundled).name)


def refresh_process_dir(project: Path, process: dict):
    """Copy the version-pinned parts of the process into .process/ (always overwritten)."""
    dot = project / ".process"
    dot.mkdir(exist_ok=True)
    shutil.copy2(ROOT / "process.yaml", dot / "process.yaml")
    shutil.copy2(ROOT / "tooling" / "check.py", dot / "check.py")
    shutil.copy2(ROOT / "tooling" / "status.py", dot / "status.py")
    shutil.copy2(ROOT / "tooling" / "ci" / "process-check.sh", dot / "process-check.sh")
    copy_tree(ROOT / "artefacts" / "templates", dot / "templates")
    copy_tree(ROOT / "tooling" / "guardrails", dot / "guardrails")
    copy_tree(ROOT / "adapters", dot / "adapters")
    if (dot / "playbooks").exists():  # replaced by skills in v0.3.0
        shutil.rmtree(dot / "playbooks")
    install_skills(process, dot / "skills")
    for pycache in dot.rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)
    (dot / "README.md").write_text(
        "# .process\n\nManaged by dev-process `tooling/scaffold.py`. Everything here except "
        "`config.yaml` is overwritten on upgrade, so do not edit it by hand.\n\n"
        "- `config.yaml`: this project's tier, limits, guardrails and waivers (yours to edit)\n"
        "- `process.yaml`: snapshot of the pinned process version\n"
        "- `check.py`: conformance checker (`python .process/check.py`, warns only)\n"
        "- `status.py`: current phase and next step (`python .process/status.py`)\n"
        "- `skills/`: agent skills (`<name>/SKILL.md`)\n"
        "- `guardrails/`: enforcement (`git config core.hooksPath .process/guardrails/git-hooks`)\n"
        "- `adapters/`: optional agent-tool integrations\n"
        "- `templates/`: artefact templates\n",
        encoding="utf-8",
    )


def install_claude_subagents(process: dict, dest: Path):
    """One Claude Code subagent per role skill, so each role runs in its own context."""
    dest.mkdir(parents=True, exist_ok=True)
    for old in dest.glob("dev-process-*.md"):
        old.unlink()
    for skill in process["skills"]:
        if skill["kind"] != "role" or skill["role"] == "orchestrator":
            continue  # the orchestrator runs in the main session and delegates to these
        text = (ROOT / skill["doc"]).read_text(encoding="utf-8")
        description = yaml.safe_load(text.split("\n---", 1)[0].lstrip("-"))["description"]
        role = skill["role"].capitalize()
        (dest / f"{skill['id']}.md").write_text(
            "---\n" + yaml.safe_dump({"name": skill["id"], "description": description}, sort_keys=False, width=1000)
            + "---\n"
            f"You are the dev-process {role} agent for this project.\n\n"
            f"1. Read `AGENTS.md` and `docs/standards.md`.\n"
            f"2. Follow `.claude/skills/{skill['id']}/SKILL.md` exactly for the step you were given.\n"
            "3. Respect the guardrails: feature branches only, the commit convention, lint before commit, "
            "and never bypass hooks.\n"
            "4. Do only the step you were given. Never approve a gate or merge.\n"
            "5. Report back briefly: what you did, the files and commits you changed, and anything that needs "
            "the Owner.\n",
            encoding="utf-8")


def install_adapter(name: str, project: Path, process: dict, created: list, skipped: list):
    if name == "claude":
        src = ROOT / "adapters" / "claude"
        install_skills(process, project / ".claude" / "skills")
        created.append(".claude/skills/dev-process-* (refreshed)")
        write_new(project / "CLAUDE.md", (src / "CLAUDE.md").read_text(encoding="utf-8"), created, skipped, project)
        install_claude_subagents(process, project / ".claude" / "agents")
        created.append(".claude/agents/dev-process-* (refreshed)")
        settings = project / ".claude" / "settings.json"
        if settings.exists():
            current = json.loads(settings.read_text(encoding="utf-8") or "{}")
            if "pre_tool_use.py" not in json.dumps(current):
                skipped.append(".claude/settings.json (exists: add the PreToolUse hook from "
                               ".process/adapters/claude/settings.json by hand)")
        else:
            write_new(settings, (src / "settings.json").read_text(encoding="utf-8"), created, skipped, project)


def record_adapters(project: Path, adapters: list[str]):
    """Remember installed adapters in config.yaml, so upgrades refresh them."""
    path = project / ".process" / "config.yaml"
    text = path.read_text(encoding="utf-8")
    known = set((yaml.safe_load(text) or {}).get("adapters") or [])
    wanted = sorted(known | set(adapters))
    if not adapters or set(wanted) == known:
        return wanted
    line = f"adapters: [{', '.join(wanted)}]   # agent-tool integrations, refreshed on upgrade"
    if re.search(r"^adapters:.*$", text, re.MULTILINE):
        text = re.sub(r"^adapters:.*$", line, text, count=1, flags=re.MULTILINE)
    else:
        text = text.rstrip("\n") + "\n" + line + "\n"
    path.write_text(text, encoding="utf-8")
    return wanted


def ensure_guardrails_config(project: Path, mode: str = "warn") -> bool:
    """Add a guardrails section to an existing config.yaml that predates v0.3.0."""
    path = project / ".process" / "config.yaml"
    text = path.read_text(encoding="utf-8")
    if (yaml.safe_load(text) or {}).get("guardrails") is not None:
        return False
    template = (ROOT / "artefacts" / "templates" / "process-config.yaml").read_text(encoding="utf-8")
    block = re.search(r"^guardrails:.*?(?=^waivers:)", template, re.MULTILINE | re.DOTALL).group(0)
    block = block.replace("{{guardrails_mode}}", mode)
    text = re.sub(r"^waivers:", block + "waivers:", text, count=1, flags=re.MULTILINE) \
        if re.search(r"^waivers:", text, re.MULTILINE) else text.rstrip("\n") + "\n" + block
    path.write_text(text, encoding="utf-8")
    return True


def install_hooks(project: Path):
    if not (project / ".git").exists():
        print("  (not a git repository yet: run `git init`, then "
              "`git config core.hooksPath .process/guardrails/git-hooks`)")
        return
    subprocess.run(["git", "-C", str(project), "config", "core.hooksPath", ".process/guardrails/git-hooks"], check=True)
    print("  git hooks installed (core.hooksPath = .process/guardrails/git-hooks)")


def adopt(project: Path, name: str, tier: str, guardrails: str, adapters: list[str], github: bool, hooks: bool):
    process = load_process()
    version = process["process"]["version"]
    values = {"project": name, "tier": tier, "date": dt.date.today().isoformat(),
              "process_version": version, "guardrails_mode": guardrails}
    created, skipped = [], []

    project.mkdir(parents=True, exist_ok=True)
    refresh_process_dir(project, process)

    for art in process["artefacts"]:
        path, template = art.get("path"), art.get("template")
        if not path:
            continue
        if tier not in art["required_tiers"] and art["id"] not in ("adr", "gate-record", "spike-report", "reviewer-summary"):
            continue
        target = project / path
        if path.endswith("/"):
            target.mkdir(parents=True, exist_ok=True)
            seed = FOLDER_SEEDS.get(art["id"])
            if seed and template:
                write_new(target / seed, render(ROOT / template, values), created, skipped, project)
            elif not any(target.iterdir()):
                (target / ".gitkeep").touch()
                created.append(f"{path}.gitkeep")
        elif template:
            write_new(target, render(ROOT / template, values), created, skipped, project)

    for adapter in adapters:
        install_adapter(adapter, project, process, created, skipped)
    record_adapters(project, adapters)

    if github:
        pr = ROOT / "artefacts" / "templates" / "pull-request.md"
        write_new(project / ".github" / "pull_request_template.md", render(pr, values), created, skipped, project)
        wf = ROOT / "tooling" / "ci" / "github-actions-process-check.yml"
        write_new(project / ".github" / "workflows" / "process-check.yml", wf.read_text(encoding="utf-8"),
                  created, skipped, project)

    print(f"dev-process v{version} adopted in {project} (tier {tier}, guardrails: {guardrails})\n")
    for rel in created:
        print(f"  + {rel}")
    for rel in skipped:
        print(f"  = {rel} (exists, kept)")
    if hooks:
        install_hooks(project)
    print("\nNext: fill in docs/brief.md, docs/standards.md and AGENTS.md (phase P0); set "
          "guardrails.lint_command in .process/config.yaml; then run: python .process/check.py")


def upgrade(project: Path, adapters: list[str], hooks: bool):
    config_path = project / ".process" / "config.yaml"
    if not config_path.is_file():
        sys.exit(f"{config_path} not found. Adopt the process first (omit --upgrade).")
    process = load_process()
    version = process["process"]["version"]
    text = config_path.read_text(encoding="utf-8")
    old = (yaml.safe_load(text) or {}).get("process_version", "?")
    text = re.sub(r'^process_version:.*$', f'process_version: "{version}"', text, count=1, flags=re.MULTILINE)
    config_path.write_text(text, encoding="utf-8")
    refresh_process_dir(project, process)
    added = ensure_guardrails_config(project)
    created, skipped = [], []
    for adapter in record_adapters(project, adapters):
        install_adapter(adapter, project, process, created, skipped)
    print(f"Upgraded {project} from dev-process v{old} to v{version}.")
    if added:
        print("  + guardrails section added to .process/config.yaml (mode: warn)")
    for rel in created:
        print(f"  + {rel}")
    for rel in skipped:
        print(f"  = {rel} (exists, kept)")
    if hooks:
        install_hooks(project)
    print("Read the 'Upgrade' notes in the dev-process CHANGELOG, then run: python .process/check.py")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Adopt or upgrade dev-process in a project")
    ap.add_argument("project", help="path to the project root")
    ap.add_argument("--name", help="project name (default: folder name)")
    ap.add_argument("--tier", choices=["T1", "T2", "T3"], default="T2", help="highest expected tier (default T2)")
    ap.add_argument("--guardrails", choices=["warn", "block"], default="warn",
                    help="guardrail mode for a new project (default warn; block refuses violations)")
    ap.add_argument("--adapter", action="append", choices=ADAPTERS, default=[],
                    help="install an agent-tool adapter (repeatable)")
    ap.add_argument("--github", action="store_true", help="also add a GitHub PR template and Actions workflow")
    ap.add_argument("--install-hooks", action="store_true", help="set core.hooksPath to the guardrail hooks")
    ap.add_argument("--upgrade", action="store_true", help="upgrade an adopted project to this process version")
    args = ap.parse_args(argv)
    project = Path(args.project).resolve()
    if args.upgrade:
        upgrade(project, args.adapter, args.install_hooks)
    else:
        adopt(project, args.name or project.name, args.tier, args.guardrails, args.adapter, args.github,
              args.install_hooks)


if __name__ == "__main__":
    main()

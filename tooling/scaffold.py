#!/usr/bin/env python3
"""Adopt (or upgrade) dev-process in a project.

New project / adoption:
    python tooling/scaffold.py PATH --name "My project" --tier T2 [--github]

Upgrade an adopted project to this checkout's process version:
    python tooling/scaffold.py PATH --upgrade

Never overwrites existing artefacts; it reports them as skipped.
Requires: Python 3.9+, PyYAML.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# Where to put the first file when an artefact's path is a folder.
FOLDER_SEEDS = {
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


def refresh_process_dir(project: Path):
    """Copy the version-pinned parts of the process into .process/ (always overwritten)."""
    dot = project / ".process"
    dot.mkdir(exist_ok=True)
    shutil.copy2(ROOT / "process.yaml", dot / "process.yaml")
    shutil.copy2(ROOT / "tooling" / "check.py", dot / "check.py")
    shutil.copy2(ROOT / "tooling" / "ci" / "process-check.sh", dot / "process-check.sh")
    for sub, src in (("playbooks", ROOT / "agents" / "playbooks"), ("templates", ROOT / "artefacts" / "templates")):
        if (dot / sub).exists():
            shutil.rmtree(dot / sub)
        shutil.copytree(src, dot / sub)
    (dot / "README.md").write_text(
        "# .process\n\nManaged by dev-process `tooling/scaffold.py`. Everything here except "
        "`config.yaml` is overwritten on upgrade, so do not edit it by hand.\n\n"
        "- `config.yaml`: this project's tier, test paths and waivers (yours to edit)\n"
        "- `process.yaml`: snapshot of the pinned process version\n"
        "- `check.py`: conformance checker (`python .process/check.py`)\n"
        "- `playbooks/`: agent role playbooks\n"
        "- `templates/`: artefact templates\n",
        encoding="utf-8",
    )


def adopt(project: Path, name: str, tier: str, github: bool) -> None:
    process = load_process()
    version = process["process"]["version"]
    values = {"project": name, "tier": tier, "date": dt.date.today().isoformat(), "process_version": version}
    created, skipped = [], []

    project.mkdir(parents=True, exist_ok=True)
    refresh_process_dir(project)

    for art in process["artefacts"]:
        path, template = art.get("path"), art.get("template")
        if not path:
            continue
        if tier not in art["required_tiers"] and art["id"] not in ("adr", "gate-record"):
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

    if github:
        pr = ROOT / "artefacts" / "templates" / "pull-request.md"
        write_new(project / ".github" / "pull_request_template.md", render(pr, values), created, skipped, project)
        wf = ROOT / "tooling" / "ci" / "github-actions-process-check.yml"
        write_new(project / ".github" / "workflows" / "process-check.yml", wf.read_text(encoding="utf-8"),
                  created, skipped, project)

    print(f"dev-process v{version} adopted in {project} (tier {tier})\n")
    for rel in created:
        print(f"  + {rel}")
    for rel in skipped:
        print(f"  = {rel} (exists, kept)")
    print("\nNext: fill in docs/brief.md and AGENTS.md (phase P0), then run: python .process/check.py")


def upgrade(project: Path) -> None:
    config_path = project / ".process" / "config.yaml"
    if not config_path.is_file():
        sys.exit(f"{config_path} not found. Adopt the process first (omit --upgrade).")
    version = load_process()["process"]["version"]
    text = config_path.read_text(encoding="utf-8")
    old = (yaml.safe_load(text) or {}).get("process_version", "?")
    text = re.sub(r'^process_version:.*$', f'process_version: "{version}"', text, count=1, flags=re.MULTILINE)
    config_path.write_text(text, encoding="utf-8")
    refresh_process_dir(project)
    print(f"Upgraded {project} from dev-process v{old} to v{version}.")
    print("Read the 'Upgrade' notes in the dev-process CHANGELOG, then run: python .process/check.py")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Adopt or upgrade dev-process in a project")
    ap.add_argument("project", help="path to the project root")
    ap.add_argument("--name", help="project name (default: folder name)")
    ap.add_argument("--tier", choices=["T1", "T2", "T3"], default="T2", help="highest expected tier (default T2)")
    ap.add_argument("--github", action="store_true", help="also add a GitHub PR template and Actions workflow")
    ap.add_argument("--upgrade", action="store_true", help="upgrade an adopted project to this process version")
    args = ap.parse_args(argv)
    project = Path(args.project).resolve()
    if args.upgrade:
        upgrade(project)
    else:
        adopt(project, args.name or project.name, args.tier, args.github)


if __name__ == "__main__":
    main()

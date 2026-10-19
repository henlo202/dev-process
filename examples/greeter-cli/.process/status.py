#!/usr/bin/env python3
"""dev-process status: where is this project in the process, and what happens next?

Derives the state deterministically from the repository (gate records, increment
briefs, reviews, CHANGELOG, git branches and tags), so any agent session, or
the Owner, can resume at any time. Copied into projects as .process/status.py.

    python .process/status.py [--json] [--fetch]
    python .process/status.py record-gate G1 --increment INC-002 --decision approved \
        --statement "Approved, go ahead." [--conditions "..."]
    python .process/status.py record-gate G3 --release 0.2.0 --decision approved --statement "Ship it."

record-gate writes the Owner's decision, quoted verbatim, as a gate record. It
refuses unless that exact gate is the one currently awaiting the Owner. Agents
may run it only to record a decision the Owner has explicitly stated (PDR-0008).

Requires: Python 3.9+, PyYAML.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

PLACEHOLDER = re.compile(r"<(?!!--)[A-Za-z][^<>=\"`\n]*\s[^<>=\"`\n]*>")
FENCE = re.compile(r"```.*?```", re.DOTALL)
SLICE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(S\d+)\b[:\s]*(.*)$", re.MULTILINE)
VERSION_HEADING = re.compile(r"^## \[(\d+\.\d+\.\d+)\]", re.MULTILINE)
GATE_NAMES = {"G0": "Go / No-go", "G1": "Shape approved", "G2": "Merge approved", "G3": "Release approved"}
PHASE_NAMES = {"P0": "Initiate", "P1": "Shape", "P2": "Build", "P3": "Verify", "P4": "Release", "P5": "Learn"}


@dataclass
class Step:
    phase: str
    actor: str                      # "agent" or "owner"
    action: str
    skill: str | None = None
    gate: str | None = None
    increment: str | None = None
    release: str | None = None
    detail: str = ""
    evidence: list[str] = field(default_factory=list)


# ------------------------------------------------------------------ reading

def frontmatter(path: Path) -> dict:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    try:
        data = yaml.safe_load(text.split("\n---", 1)[0].lstrip("-"))
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def has_placeholders(*paths: Path) -> list[str]:
    return [p.name for p in paths if p.is_file() and PLACEHOLDER.search(FENCE.sub("", p.read_text(encoding="utf-8")))]


def section(text: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    return re.sub(r"<!--.*?-->", "", m.group(1), flags=re.DOTALL).strip() if m else ""


def git(root: Path, *args) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    except OSError:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


class Project:
    def __init__(self, root: Path):
        self.root = root
        self.config = yaml.safe_load((root / ".process" / "config.yaml").read_text(encoding="utf-8")) or {}
        self.gates = []
        gate_dir = root / "docs" / "gates"
        if gate_dir.is_dir():
            self.gates = [frontmatter(p) for p in sorted(gate_dir.glob("*.md"))]
        self.increments = []
        inc_dir = root / "docs" / "increments"
        if inc_dir.is_dir():
            for p in inc_dir.glob("*.md"):
                fm = frontmatter(p)
                if fm.get("artefact") == "increment" and fm.get("status") != "superseded":
                    self.increments.append({**fm, "_path": p, "_text": p.read_text(encoding="utf-8")})
        self.increments.sort(key=lambda i: int(re.sub(r"\D", "", str(i.get("increment", "0"))) or 0))
        self.is_git = git(root, "rev-parse", "--is-inside-work-tree") == "true"

    def gate_approved(self, gate: str, increment: str | None = None, release: str | None = None) -> bool:
        return any(g.get("gate") == gate and g.get("decision") in ("approved", "approved-with-conditions")
                   and (increment is None or g.get("increment") == increment)
                   and (release is None or str(g.get("release")) == release) for g in self.gates)

    def review(self, name: str) -> Path:
        return self.root / "docs" / "reviews" / f"{name}.md"

    def main_ref(self) -> str:
        main = (self.config.get("guardrails") or {}).get("protected_branches", ["main"])[0]
        return f"origin/{main}" if git(self.root, "rev-parse", "--verify", "-q", f"origin/{main}") else main

    def unmerged_branches(self, inc_id: str) -> list[str]:
        out = git(self.root, "branch", "-a", "--no-merged", self.main_ref(), "--format=%(refname:short)")
        return [b for b in (out or "").splitlines() if f"/{inc_id}-" in f"/{b.split('/', 1)[-1]}"
                and not b.startswith(("spike/", "origin/spike/"))]

    def tagged(self, version: str) -> bool:
        return bool(git(self.root, "tag", "-l", version, f"v{version}"))


# ------------------------------------------------------------------ deciding

def increment_build_step(p: Project, inc: dict) -> Step:
    iid = str(inc["increment"])
    slices = SLICE.findall(section(inc["_text"], "Task slices"))
    open_slices = [(s, text) for mark, s, text in slices if mark == " "]
    if open_slices:
        s, text = open_slices[0]
        return Step("P2", "agent", f"Build slice {s} of {iid}: {text}".rstrip(": "), "dev-process-implementer",
                    increment=iid, detail=f"{len(open_slices)} of {len(slices)} slices left. Tick the slice in the "
                                          "increment brief when its PR is open.")
    if len(section(inc["_text"], "Demo")) < 20:
        return Step("P3", "agent", f"Record the demo for {iid}", "dev-process-demo", increment=iid)
    if not p.is_git:
        return Step("P3", "owner", f"Merge the pull request(s) for {iid}", gate="G2", increment=iid,
                    detail="Not a git repository, so merges cannot be detected. Set the increment to done when merged.")
    unmerged = p.unmerged_branches(iid)
    if unmerged:
        return Step("P3", "owner", f"Review the demo and merge the pull request(s) for {iid}", gate="G2",
                    increment=iid, evidence=unmerged,
                    detail="The merged PR with its ticked checklist is the G2 record.")
    return Step("P3", "agent", f"Set {iid} to status `done`: all its branches are merged", increment=iid)


def release_step(p: Project) -> Step | None:
    changelog = p.root / "CHANGELOG.md"
    if not changelog.is_file():
        return None
    text = changelog.read_text(encoding="utf-8")
    m = VERSION_HEADING.search(text)
    if m and p.is_git and not p.tagged(m.group(1)):
        v = m.group(1)
        if p.gate_approved("G3", release=v):
            return Step("P4", "agent", f"Tag and publish release {v} (annotated tag v{v}), then deploy per the runbook",
                        "dev-process-documenter", release=v)
        if not p.review(f"G3-{v}").is_file():
            return Step("P4", "agent", f"Review release {v} for G3; write docs/reviews/G3-{v}.md",
                        "dev-process-reviewer", release=v, detail="Use a fresh session or subagent.")
        return Step("P4", "owner", f"Decide on releasing {v}", gate="G3", release=v,
                    evidence=["CHANGELOG.md", f"docs/reviews/G3-{v}.md", "docs/ops/runbook.md"])
    unreleased = section(text, "[Unreleased]")
    if re.search(r"^\s*[-*]\s+\S", unreleased, re.MULTILINE):
        return Step("P4", "agent", "Prepare a release: move the Unreleased entries under a new version, write "
                    "release notes, check the runbook and user docs", "dev-process-documenter")
    return None


def next_step(p: Project) -> Step:
    root = p.root
    # P0: once per initiative
    if not p.gate_approved("G0"):
        brief = root / "docs" / "brief.md"
        pending = has_placeholders(brief, root / "AGENTS.md", root / "docs" / "standards.md")
        if not brief.is_file() or pending or frontmatter(brief).get("status") == "draft":
            return Step("P0", "agent", "Complete P0: the brief, AGENTS.md and docs/standards.md; set the brief's "
                        "status to in-review", "dev-process-analyst",
                        detail=f"Unfilled placeholders in: {', '.join(pending)}" if pending else "")
        if not p.review("G0").is_file():
            return Step("P0", "agent", "Review the brief for G0; write docs/reviews/G0.md", "dev-process-reviewer",
                        detail="Use a fresh session or subagent.")
        return Step("P0", "owner", "Decide go / no-go for the initiative", gate="G0",
                    evidence=["docs/brief.md", "docs/reviews/G0.md"])
    # 1. finish increments that are being built
    for inc in p.increments:
        if inc.get("status") in ("approved", "in-progress"):
            return increment_build_step(p, inc)
    # 2. release what is merged
    step = release_step(p)
    if step:
        return step
    # 3. learn from finished increments
    for inc in reversed(p.increments):
        if inc.get("status") == "done" and not section(inc["_text"], "Learnings"):
            iid = str(inc["increment"])
            return Step("P5", "agent", f"Draft the Learnings for {iid} from its PRs and demo, then ask the Owner "
                        "to confirm or edit them", increment=iid)
    # 4. shape the next increment
    for inc in p.increments:
        iid = str(inc["increment"])
        if inc.get("status") == "draft":
            return Step("P1", "agent", f"Shape {iid}; set its status to in-review when the brief is complete",
                        "dev-process-shape-increment", increment=iid,
                        detail=", ".join(has_placeholders(inc["_path"])) and "The brief still has placeholders.")
        if inc.get("status") == "in-review":
            if not p.review(f"G1-{iid}").is_file():
                return Step("P1", "agent", f"Review {iid} for G1; write docs/reviews/G1-{iid}.md",
                            "dev-process-reviewer", increment=iid, detail="Use a fresh session or subagent.")
            return Step("P1", "owner", f"Decide on the shape of {iid}", gate="G1", increment=iid,
                        evidence=[inc["_path"].relative_to(root).as_posix(), f"docs/reviews/G1-{iid}.md"])
    return Step("P1", "owner", "Say what outcome you want next (a new increment), or describe a T1 fix")


# ------------------------------------------------------------------ recording

def record_gate(p: Project, args) -> int:
    gate = args.gate.upper()
    if gate == "G2":
        print("G2 is recorded by merging the pull request with its ticked checklist; nothing to write.")
        return 1
    step = next_step(p)
    key_ok = (gate != "G1" or step.increment == args.increment) and (gate != "G3" or step.release == args.release)
    if step.actor != "owner" or step.gate != gate or not key_ok:
        print(f"Refusing: {gate} is not awaiting a decision. Current step: [{step.actor}] {step.action}")
        return 1
    if not args.statement.strip():
        print("Refusing: --statement must quote the Owner's decision verbatim.")
        return 1
    today = dt.date.today().isoformat()
    key = {"G0": today, "G1": args.increment, "G3": args.release}[gate]
    target = p.root / "docs" / "gates" / f"{gate}-{key}.md"
    n = 2
    while target.exists():
        target = target.with_name(f"{gate}-{key}-{n}.md")
        n += 1
    fm = {"artefact": "gate-record", "gate": gate, "decision": args.decision,
          "tier": str(p.config.get("tier", "T2")), "status": "done", "updated": today,
          "recorded_by": "agent", "owner_statement": args.statement.strip()}
    if gate == "G1":
        fm["increment"] = args.increment
    if gate == "G3":
        fm["release"] = args.release
    evidence = "\n".join(f"- {e}" for e in step.evidence) or "- (see the step's artefacts)"
    body = (f"# Gate {gate}: {GATE_NAMES[gate]}, {key}\n\n"
            f"**Approver:** Owner (decision stated in conversation and recorded verbatim by an agent)\n"
            f"**Process version:** {p.config.get('process_version', '?')}\n\n"
            f"**Owner's decision:**\n> {args.statement.strip()}\n\n**Evidence reviewed:**\n{evidence}\n\n"
            f"## Conditions\n{args.conditions or 'None.'}\n")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + body,
                      encoding="utf-8")
    print(f"Recorded {gate} ({args.decision}) in {target.relative_to(p.root).as_posix()}")
    if gate == "G1":
        inc = next(i for i in p.increments if str(i.get("increment")) == args.increment)
        new_status = "draft" if args.decision == "rejected" else "approved"
        text = re.sub(r"^status:.*$", f"status: {new_status}", inc["_text"], count=1, flags=re.MULTILINE)
        text = re.sub(r"^updated:.*$", f"updated: {today}", text, count=1, flags=re.MULTILINE)
        inc["_path"].write_text(text, encoding="utf-8")
        print(f"Set {args.increment} status to {new_status}")
    return 0


# ------------------------------------------------------------------ output

def utf8_stdio() -> None:
    """Print UTF-8 even where the console or pipe encoding cannot (e.g. cp1252 on Windows)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv=None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(description="Where is this project in dev-process, and what is next?")
    ap.add_argument("--project", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fetch", action="store_true", help="git fetch first, so merges are seen")
    sub = ap.add_subparsers(dest="command")
    rg = sub.add_parser("record-gate", help="record the Owner's stated gate decision")
    rg.add_argument("gate", choices=["G0", "G1", "G2", "G3", "g0", "g1", "g2", "g3"])
    rg.add_argument("--decision", required=True, choices=["approved", "approved-with-conditions", "rejected"])
    rg.add_argument("--statement", required=True, help="the Owner's words, verbatim")
    rg.add_argument("--increment")
    rg.add_argument("--release")
    rg.add_argument("--conditions")
    args = ap.parse_args(argv)

    root = Path(args.project).resolve()
    if not (root / ".process" / "config.yaml").is_file():
        print("Not a dev-process project: run tooling/scaffold.py from the dev-process repository.")
        return 1
    if args.fetch:
        git(root, "fetch", "--quiet", "--tags")
    project = Project(root)
    if args.command == "record-gate":
        return record_gate(project, args)

    step = next_step(project)
    if args.json:
        print(json.dumps(asdict(step), indent=2))
        return 0
    who = (f"Owner: decision needed at {step.gate} · {GATE_NAMES[step.gate]}" if step.gate
           else "Owner" if step.actor == "owner" else f"agent (skill: {step.skill})" if step.skill else "agent")
    print(f"dev-process status: {project.config.get('project', root.name)} "
          f"(tier {project.config.get('tier', '?')}, process v{project.config.get('process_version', '?')})\n")
    print(f"  Phase:  {step.phase} · {PHASE_NAMES[step.phase]}")
    print(f"  Next:   {step.action}")
    print(f"  Who:    {who}")
    if step.detail:
        print(f"  Note:   {step.detail}")
    for e in step.evidence:
        print(f"  See:    {e}")
    if project.increments:
        print("\n  Increments: " + ", ".join(f"{i['increment']} ({i.get('status')})" for i in project.increments))
    return 0


if __name__ == "__main__":
    sys.exit(main())

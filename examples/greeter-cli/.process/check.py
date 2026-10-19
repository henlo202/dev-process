#!/usr/bin/env python3
"""dev-process conformance checker.

Checks a project against the dev-process rules for its tier and prints a
Markdown report (conformance + traceability). It is copied into each project
as .process/check.py by tooling/scaffold.py.

The checker WARNS and never blocks: it always exits 0 unless --strict is given
(reserved for future compliance profiles). See PDR-0003.

Usage:
    python .process/check.py [--project PATH] [--output report.md] [--strict]

Requires: Python 3.9+, PyYAML.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import glob
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("dev-process check: PyYAML is required (pip install pyyaml). Skipping check.")
    sys.exit(0)

ERROR, WARNING, INFO = "error", "warning", "info"
ICONS = {ERROR: "❌", WARNING: "⚠️", INFO: "ℹ️"}
SEVERITY_ORDER = {ERROR: 0, WARNING: 1, INFO: 2}

# Files that are artefacts but intentionally have no YAML frontmatter.
NO_FRONTMATTER = {"AGENTS.md", "CHANGELOG.md", ".process/config.yaml"}
STATUSES = {"draft", "in-review", "approved", "in-progress", "done", "superseded"}
DECISIONS = {"approved", "approved-with-conditions", "rejected"}

REQ_DEF = re.compile(r"^#{2,4}\s+((?:REQ|NFR)-\d+)\b", re.MULTILINE)
REQ_REF = re.compile(r"(?<![A-Za-z0-9])(REQ|NFR)[-_](\d+)(?![0-9])")
STATUS_LINE = re.compile(r"\*\*Status:\*\*\s*([a-z-]+)", re.IGNORECASE)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLICE = re.compile(r"^\s*[-*]\s+(?:\[[ xX]\]\s+)?S\d+\b", re.MULTILINE)
DEFAULT_LIMITS = {"max_requirements": 5, "max_slices": 8}
# Template placeholders such as "<short title>" (contain a space, no attributes).
PLACEHOLDER = re.compile(r"<(?!!--)[A-Za-z][^<>=\"`\n]*\s[^<>=\"`\n]*>")
FENCE = re.compile(r"```.*?```", re.DOTALL)


@dataclass
class Finding:
    rule: str
    severity: str
    message: str
    fix: str = ""
    ref: str = ""  # process doc that explains the rule
    waived_by: dict | None = None


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    trace: dict[str, dict] = field(default_factory=dict)
    unknown_refs: dict[str, list[str]] = field(default_factory=dict)

    def add(self, rule, severity, message, fix="", ref=""):
        self.findings.append(Finding(rule, severity, message, fix, ref))


def read_frontmatter(path: Path):
    """Return (frontmatter dict or None, error string or None)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return None, "missing"
    parts = text.split("\n---", 1)
    if len(parts) < 2:
        return None, "unterminated"
    try:
        data = yaml.safe_load(parts[0].lstrip("-").strip()) or {}
    except yaml.YAMLError as exc:
        return None, f"invalid YAML: {exc}".splitlines()[0]
    if not isinstance(data, dict):
        return None, "not a mapping"
    return data, None


def validate_frontmatter(rel: str, fm: dict, expected: str, report: Report):
    problems = []
    for key in ("artefact", "status", "updated"):
        if key not in fm:
            problems.append(f"missing `{key}`")
    if fm.get("artefact") not in (None, expected):
        problems.append(f"`artefact` is `{fm.get('artefact')}`, expected `{expected}`")
    if "status" in fm and fm["status"] not in STATUSES:
        problems.append(f"`status` must be one of {sorted(STATUSES)}")
    updated = fm.get("updated")
    if updated is not None and not DATE.match(str(updated)):
        problems.append("`updated` must be YYYY-MM-DD (placeholder not filled in?)")
    if expected == "gate-record":
        for key in ("gate", "decision", "tier"):
            if key not in fm:
                problems.append(f"missing `{key}`")
        if "decision" in fm and fm["decision"] not in DECISIONS:
            problems.append(f"`decision` must be one of {sorted(DECISIONS)}")
    if expected == "increment":
        if not re.match(r"^INC-\d+$", str(fm.get("increment", ""))):
            problems.append("`increment` must be an ID like `INC-001`")
        if not isinstance(fm.get("requirements"), list):
            problems.append("`requirements` must be a list of requirement IDs (may be empty)")
    if problems:
        report.add(
            f"frontmatter-invalid:{rel}", WARNING,
            f"`{rel}` has invalid frontmatter: " + "; ".join(problems) + ".",
            "Fix the YAML block at the top of the file.",
            "schema/artefact-frontmatter.schema.json",
        )


def check_placeholders(md: Path, rel: str, report: Report):
    text = FENCE.sub("", md.read_text(encoding="utf-8", errors="replace"))
    found = PLACEHOLDER.findall(text)
    if found:
        sample = ", ".join(f"`{p}`" for p in dict.fromkeys(found[:3]))
        report.add(
            f"placeholder:{rel}", WARNING,
            f"`{rel}` still contains {len(found)} template placeholder(s), e.g. {sample}.",
            "Replace them with real content, or remove the section if it does not apply.",
            "artefacts/",
        )


def markdown_files(target: Path):
    if target.is_file():
        return [target]
    return sorted(p for p in target.rglob("*.md") if p.is_file())


def check_artefacts(root: Path, process: dict, tier: str, report: Report):
    for art in process["artefacts"]:
        path = art.get("path")
        if not path:
            continue
        required = tier in art.get("required_tiers", [])
        target = root / path
        is_dir = path.endswith("/")
        exists = target.is_dir() if is_dir else target.is_file()
        if is_dir and exists and art["scope"] != "increment" and not markdown_files(target):
            exists = False  # initiative-level folders must contain content
        if not exists:
            if required:
                report.add(
                    f"artefact-missing:{art['id']}", ERROR,
                    f"Required artefact **{art['name']}** not found at `{path}` (tier {tier}).",
                    f"Create it from the template `.process/templates/{Path(art['template']).name}`"
                    if art.get("template") else "Create it.",
                    art["doc"],
                )
            continue
        if path in NO_FRONTMATTER:
            if target.suffix == ".md":
                check_placeholders(target, path, report)
            continue
        for md in markdown_files(target):
            rel = md.relative_to(root).as_posix()
            check_placeholders(md, rel, report)
            fm, err = read_frontmatter(md)
            if err:
                report.add(
                    f"frontmatter-missing:{rel}", WARNING,
                    f"`{rel}` has no valid frontmatter ({err}).",
                    "Add a YAML block with at least `artefact`, `status` and `updated`.",
                    "schema/artefact-frontmatter.schema.json",
                )
                continue
            validate_frontmatter(rel, fm, art["id"], report)


def parse_requirements(root: Path, report: Report) -> dict[str, dict]:
    reqs: dict[str, dict] = {}
    req_dir = root / "docs" / "requirements"
    if not req_dir.is_dir():
        return reqs
    for md in markdown_files(req_dir):
        text = md.read_text(encoding="utf-8", errors="replace")
        matches = list(REQ_DEF.finditer(text))
        for i, m in enumerate(matches):
            rid = m.group(1)
            section = text[m.end(): matches[i + 1].start() if i + 1 < len(matches) else len(text)]
            status = STATUS_LINE.search(section)
            rel = md.relative_to(root).as_posix()
            if rid in reqs:
                report.add(
                    f"duplicate-requirement:{rid}", ERROR,
                    f"`{rid}` is defined in both `{reqs[rid]['file']}` and `{rel}`.",
                    "Requirement IDs must be unique. Renumber the newer one.",
                    "guides/requirements.md",
                )
                continue
            reqs[rid] = {"file": rel, "status": status.group(1).lower() if status else "unknown"}
    return reqs


def iter_test_files(root: Path, test_paths: list[str]):
    seen = set()
    for entry in test_paths:
        for match in glob.glob(str(root / entry), recursive=True):
            p = Path(match)
            files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file()]
            for f in files:
                if f in seen or f.stat().st_size > 1_000_000:
                    continue
                seen.add(f)
                yield f


def check_traceability(root: Path, config: dict, report: Report) -> dict[str, dict]:
    reqs = parse_requirements(root, report)
    if not reqs:
        return reqs
    refs: dict[str, list[str]] = {}
    for f in iter_test_files(root, config.get("test_paths") or ["tests"]):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = f.relative_to(root).as_posix()
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in REQ_REF.finditer(line):
                rid = f"{m.group(1)}-{m.group(2)}"
                loc = f"{rel}:{lineno}"
                if loc not in refs.setdefault(rid, []):
                    refs[rid].append(loc)
    for rid, info in sorted(reqs.items()):
        locations = refs.get(rid, [])
        report.trace[rid] = {**info, "tests": locations}
        if locations or info["status"] in ("retired", "superseded"):
            continue
        if info["status"] == "approved":
            report.add(
                f"untested-requirement:{rid}", WARNING,
                f"Approved requirement `{rid}` ({info['file']}) is not referenced by any test.",
                f"Add a test that proves its acceptance criteria and mention `{rid}` in its name or a comment.",
                "guides/requirements.md",
            )
        else:
            report.add(
                f"untested-requirement:{rid}", INFO,
                f"Requirement `{rid}` (status `{info['status']}`) has no test yet.",
                "Expected while it is not approved.",
                "guides/requirements.md",
            )
    for rid, locations in sorted(refs.items()):
        if rid not in reqs:
            report.unknown_refs[rid] = locations
            report.add(
                f"unknown-requirement:{rid}", WARNING,
                f"Tests reference `{rid}`, which is not defined in `docs/requirements/` ({locations[0]}).",
                "Fix the ID in the test or add the missing requirement.",
                "guides/requirements.md",
            )
    return reqs


def section(text: str, heading: str) -> str:
    """Body of the first `## heading` section, without HTML comments."""
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    return re.sub(r"<!--.*?-->", "", m.group(1), flags=re.DOTALL).strip() if m else ""


def load_increments(root: Path) -> list[dict]:
    inc_dir = root / "docs" / "increments"
    increments = []
    if inc_dir.is_dir():
        for md in markdown_files(inc_dir):
            fm, err = read_frontmatter(md)
            if fm and fm.get("artefact") == "increment":
                increments.append({**fm, "_file": md.relative_to(root).as_posix(),
                                   "_text": md.read_text(encoding="utf-8", errors="replace")})
    return increments


def check_increments(increments: list[dict], reqs: dict, config: dict, report: Report):
    limits = {**DEFAULT_LIMITS, **(config.get("increment_limits") or {})}
    seen = {}
    for inc in increments:
        iid, rel = str(inc.get("increment", "?")), inc["_file"]
        if iid in seen:
            report.add(f"duplicate-increment:{iid}", WARNING,
                       f"`{iid}` is used by both `{seen[iid]}` and `{rel}`.",
                       "Give each increment a unique INC- ID.", "artefacts/increment.md")
        seen[iid] = rel
        in_scope = inc.get("requirements") or []
        slices = len(SLICE.findall(section(inc["_text"], "Task slices")))
        over = []
        if len(in_scope) > limits["max_requirements"]:
            over.append(f"{len(in_scope)} requirements (limit {limits['max_requirements']})")
        if slices > limits["max_slices"]:
            over.append(f"{slices} task slices (limit {limits['max_slices']})")
        if over:
            report.add(f"increment-too-large:{iid}", WARNING,
                       f"Increment `{iid}` ({rel}) exceeds the size limit: {', '.join(over)}.",
                       "Split it into smaller increments, each with one outcome, or waive it if the overrun is deliberate.",
                       "guides/increments.md")
        for rid in in_scope:
            if reqs and rid not in reqs:
                report.add(f"unknown-requirement:{rid}", WARNING,
                           f"Increment `{iid}` lists `{rid}`, which is not defined in `docs/requirements/`.",
                           "Fix the ID or add the requirement.", "guides/requirements.md")
        if inc.get("status") == "done" and len(section(inc["_text"], "Demo")) < 20:
            report.add(f"demo-missing:{iid}", WARNING,
                       f"Increment `{iid}` is `done` but its Demo section has no evidence.",
                       "Link or paste the demo that shows each acceptance criterion working.",
                       "artefacts/demo.md")


def check_gates(root: Path, tier: str, increments: list[dict], report: Report):
    if tier == "T1":
        return
    gate_dir = root / "docs" / "gates"
    records = {}
    if gate_dir.is_dir():
        for md in markdown_files(gate_dir):
            fm, err = read_frontmatter(md)
            if fm and fm.get("gate"):
                records.setdefault(str(fm["gate"]), []).append(fm)

    def approved(gate, increment=None):
        return any(r.get("decision") in ("approved", "approved-with-conditions")
                   and (increment is None or r.get("increment") == increment)
                   for r in records.get(gate, []))

    if not approved("G0"):
        report.add(
            "gate-record-missing:G0", WARNING,
            "No approved G0 (Go / No-go) gate record found in `docs/gates/`.",
            "Hold G0 and record it with `.process/templates/gate-record.md`.",
            "gates/G0-go-no-go.md",
        )
    for inc in increments:
        iid = str(inc.get("increment", "?"))
        if inc.get("status") in ("approved", "in-progress", "done") and not approved("G1", iid):
            report.add(
                f"gate-record-missing:G1:{iid}", WARNING,
                f"Increment `{iid}` is `{inc.get('status')}` but has no approved G1 (Shape) gate record.",
                f"Record the G1 decision in `docs/gates/` with `increment: {iid}` in its frontmatter.",
                "gates/G1-shape.md",
            )


def apply_waivers(config: dict, report: Report, today: dt.date):
    for w in config.get("waivers") or []:
        if not isinstance(w, dict) or not w.get("rule"):
            report.add("waiver-invalid", WARNING, f"Waiver entry `{w}` has no `rule`.", "", "governance/waivers.md")
            continue
        missing = [k for k in ("reason", "expires") if not w.get(k)]
        if missing:
            report.add(
                f"waiver-invalid:{w['rule']}", WARNING,
                f"Waiver for `{w['rule']}` is missing {', '.join(missing)}.",
                "Every waiver needs a reason and an expiry date.",
                "governance/waivers.md",
            )
            continue
        try:
            expires = dt.date.fromisoformat(str(w["expires"]))
        except ValueError:
            report.add(f"waiver-invalid:{w['rule']}", WARNING,
                       f"Waiver for `{w['rule']}` has an invalid expiry date `{w['expires']}`.",
                       "Use YYYY-MM-DD.", "governance/waivers.md")
            continue
        if expires < today:
            report.add(
                f"waiver-expired:{w['rule']}", WARNING,
                f"Waiver for `{w['rule']}` expired on {expires}.",
                "Fix the underlying finding, or renew the waiver with a fresh reason.",
                "governance/waivers.md",
            )
            continue
        for f in report.findings:
            if f.waived_by is None and fnmatch.fnmatchcase(f.rule, w["rule"]):
                f.waived_by = w


def render(report: Report, project: str, tier: str, version: str, snapshot_version: str) -> str:
    active = [f for f in report.findings if not f.waived_by]
    waived = [f for f in report.findings if f.waived_by]
    counts = {s: sum(1 for f in active if f.severity == s) for s in (ERROR, WARNING, INFO)}
    lines = [
        f"# dev-process conformance report: {project}",
        "",
        f"Tier **{tier}** · process v{version} · checked {dt.date.today().isoformat()}",
        "",
        f"{ICONS[ERROR]} {counts[ERROR]} errors · {ICONS[WARNING]} {counts[WARNING]} warnings · "
        f"{ICONS[INFO]} {counts[INFO]} info · {len(waived)} waived",
        "",
        "_This check never blocks. Fix each finding or add a waiver in `.process/config.yaml`._",
        "",
    ]
    if snapshot_version != version:
        lines += [f"> ⚠️ `.process/config.yaml` pins v{version} but the snapshot is v{snapshot_version}.", ""]
    if active:
        lines += ["## Findings", "", "| | Rule | Finding | How to fix |", "|---|---|---|---|"]
        for f in sorted(active, key=lambda f: (SEVERITY_ORDER[f.severity], f.rule)):
            fix = f.fix + (f" (see dev-process `{f.ref}`)" if f.ref else "")
            lines.append(f"| {ICONS[f.severity]} | `{f.rule}` | {f.message} | {fix} |")
        lines.append("")
    else:
        lines += ["## Findings", "", "No findings. 🎉", ""]
    if waived:
        lines += ["## Waived", "", "| Rule | Reason | Expires |", "|---|---|---|"]
        for f in waived:
            lines.append(f"| `{f.rule}` | {f.waived_by['reason']} | {f.waived_by['expires']} |")
        lines.append("")
    lines += ["## Traceability", ""]
    if report.trace:
        lines += ["| Requirement | Status | Tests | Where |", "|---|---|---|---|"]
        for rid, t in report.trace.items():
            where = ", ".join(f"`{loc}`" for loc in t["tests"][:3]) + (" …" if len(t["tests"]) > 3 else "")
            mark = "✅" if t["tests"] else ("—" if t["status"] in ("retired", "superseded") else "❌")
            lines.append(f"| `{rid}` | {t['status']} | {mark} {len(t['tests'])} | {where} |")
        covered = sum(1 for t in report.trace.values() if t["tests"])
        lines += ["", f"{covered} of {len(report.trace)} requirements referenced by tests."]
    else:
        lines.append("No requirements found in `docs/requirements/`.")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="dev-process conformance checker (warn-only)")
    ap.add_argument("--project", default=".", help="project root (default: current directory)")
    ap.add_argument("--output", help="also write the report to this file")
    ap.add_argument("--strict", action="store_true", help="exit 1 if unwaived errors exist (future compliance profiles)")
    args = ap.parse_args(argv)

    root = Path(args.project).resolve()
    report = Report()
    config_path = root / ".process" / "config.yaml"
    snapshot_path = root / ".process" / "process.yaml"
    if not config_path.is_file() or not snapshot_path.is_file():
        print("# dev-process conformance report\n\n❌ `.process/config.yaml` or `.process/process.yaml` not found. "
              "Run `tooling/scaffold.py` from the dev-process repository to adopt the process.")
        return 0
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        process = yaml.safe_load(snapshot_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"# dev-process conformance report\n\n❌ Could not parse process configuration: {exc}")
        return 0

    tier = str(config.get("tier", "T2"))
    if tier not in ("T1", "T2", "T3"):
        report.add("config-invalid:tier", ERROR, f"`tier` is `{tier}`; must be T1, T2 or T3. Assuming T2.",
                   "Fix `.process/config.yaml`.", "artefacts/process-config.md")
        tier = "T2"

    check_artefacts(root, process, tier, report)
    reqs = check_traceability(root, config, report)
    increments = load_increments(root)
    check_increments(increments, reqs, config, report)
    check_gates(root, tier, increments, report)
    apply_waivers(config, report, dt.date.today())

    text = render(report, config.get("project", root.name), tier,
                  str(config.get("process_version", "?")), process["process"]["version"])
    print(text)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    if args.strict and any(f.severity == ERROR and not f.waived_by for f in report.findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

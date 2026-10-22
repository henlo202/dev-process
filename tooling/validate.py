#!/usr/bin/env python3
"""Validate the dev-process repository itself (not projects; use check.py for those).

Checks: process.yaml against its schema, cross-references between phases,
gates, artefacts and roles, that every referenced file exists, that no process
document is orphaned, that relative Markdown links resolve, and that the
process version matches the latest CHANGELOG entry, and that no private
project term appears anywhere (PDR-0009).

Exits 1 on any error. This strictness applies to the process repository only;
project conformance remains warn-only (PDR-0003).

Requires: PyYAML, jsonschema.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CONTENT_DIRS = ["phases", "gates", "artefacts", "roles", "guides", "governance", "agents", "adapters"]


def utf8_stdio() -> None:
    """Print UTF-8 even where the console or pipe encoding cannot (e.g. cp1252 on Windows)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main() -> int:
    utf8_stdio()
    errors: list[str] = []
    process = yaml.safe_load((ROOT / "process.yaml").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schema" / "process.schema.json").read_text(encoding="utf-8"))
    for err in jsonschema.Draft202012Validator(schema).iter_errors(process):
        errors.append(f"process.yaml: {'/'.join(map(str, err.path))}: {err.message}")
    if errors:
        return report(errors)

    ids = {k: {e["id"] for e in process[k]} for k in ("tiers", "roles", "phases", "gates", "artefacts")}
    for kind in ("tiers", "roles", "phases", "gates", "artefacts", "guides", "governance"):
        seen = set()
        for e in process[kind]:
            if e["id"] in seen:
                errors.append(f"duplicate {kind} id: {e['id']}")
            seen.add(e["id"])

    for ph in process["phases"]:
        for r in ph["roles"]:
            if r not in ids["roles"]:
                errors.append(f"phase {ph['id']}: unknown role {r}")
        for a in ph["inputs"] + ph["outputs"]:
            if a not in ids["artefacts"]:
                errors.append(f"phase {ph['id']}: unknown artefact {a}")
        if ph["gate"] and ph["gate"] not in ids["gates"]:
            errors.append(f"phase {ph['id']}: unknown gate {ph['gate']}")
    for g in process["gates"]:
        if g["after"] not in ids["phases"]:
            errors.append(f"gate {g['id']}: unknown phase {g['after']}")
        else:
            phase = next(p for p in process["phases"] if p["id"] == g["after"])
            if phase["gate"] != g["id"]:
                errors.append(f"gate {g['id']}: phase {g['after']} does not point back to it")
        if g["approver"] not in ids["roles"]:
            errors.append(f"gate {g['id']}: unknown approver {g['approver']}")
        for a in g["evidence"] + [x for xs in (g.get("tier_evidence") or {}).values() for x in xs]:
            if a not in ids["artefacts"]:
                errors.append(f"gate {g['id']}: unknown evidence artefact {a}")
    for a in process["artefacts"]:
        if a["owner"] not in ids["roles"]:
            errors.append(f"artefact {a['id']}: unknown owner {a['owner']}")
        if a["template"] and not (ROOT / a["template"]).is_file():
            errors.append(f"artefact {a['id']}: template {a['template']} not found")

    errors += validate_skills(process, ids)

    referenced = set()
    for kind in ("tiers", "roles", "phases", "gates", "artefacts", "guides", "governance", "skills"):
        for e in process[kind]:
            if not (ROOT / e["doc"]).is_file():
                errors.append(f"{kind} {e['id']}: doc {e['doc']} not found")
            referenced.add(e["doc"])

    md_files = [p for d in CONTENT_DIRS for p in (ROOT / d).rglob("*.md")]
    md_files += [ROOT / "README.md", ROOT / "CHANGELOG.md"]
    for p in md_files:
        rel = p.relative_to(ROOT).as_posix()
        in_auto_dir = rel.startswith(("artefacts/templates/", "agents/README.md", "governance/decisions/", "adapters/"))
        if rel not in referenced and not in_auto_dir and p.parent != ROOT:
            errors.append(f"orphan document (not in process.yaml): {rel}")
        if rel.startswith("artefacts/templates/"):
            continue  # templates contain placeholder links meant for projects
        for target in LINK.findall(p.read_text(encoding="utf-8")):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            path = target.split("#", 1)[0]
            if path and not (p.parent / path).resolve().exists():
                errors.append(f"{rel}: broken link -> {target}")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", changelog, re.MULTILINE)
    if not m or m.group(1) != process["process"]["version"]:
        errors.append(f"CHANGELOG.md latest release {m.group(1) if m else 'none'} "
                      f"!= process.yaml version {process['process']['version']}")
    errors += check_project_neutral()
    return report(errors)


def private_terms() -> list[str]:
    """Terms of consuming projects that must never appear here (PDR-0009); never committed."""
    terms = os.environ.get("DEV_PROCESS_PRIVATE_TERMS", "").split(",")
    path = ROOT / ".private-terms"
    if path.is_file():
        terms += path.read_text(encoding="utf-8").splitlines()
    return sorted({t.strip().lower() for t in terms if t.strip() and not t.strip().startswith("#")})


def check_project_neutral() -> list[str]:
    terms = private_terms()
    if not terms:
        return []
    files = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                           cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    errors = []
    for rel in files:
        try:
            lines = (ROOT / rel).read_text(encoding="utf-8").lower().splitlines()
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable
        for n, line in enumerate(lines, 1):
            for t in terms:
                if t in line:
                    errors.append(f"{rel}:{n}: private project term '{t}' (PDR-0009)")
    return errors


def validate_skills(process: dict, ids: dict) -> list[str]:
    """Check SKILL.md files against the Agent Skills format and process.yaml."""
    errors = []
    covered_roles = set()
    for sk in process["skills"]:
        path = ROOT / sk["doc"]
        if not path.is_file():
            continue  # reported as a missing doc
        text = path.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        fm = yaml.safe_load(m.group(1)) if m else None
        if not isinstance(fm, dict):
            errors.append(f"skill {sk['id']}: SKILL.md has no YAML frontmatter")
            continue
        if fm.get("name") != sk["id"] or path.parent.name != sk["id"]:
            errors.append(f"skill {sk['id']}: frontmatter name and folder must both equal the skill id")
        if not re.match(r"^[a-z0-9-]{1,64}$", str(fm.get("name", ""))):
            errors.append(f"skill {sk['id']}: name must be 1-64 lowercase letters, digits or hyphens")
        desc = str(fm.get("description", "")).strip()
        if not desc or len(desc) > 1024:
            errors.append(f"skill {sk['id']}: description must be 1-1024 characters (is {len(desc)})")
        elif not re.search(r"\buse (when|for|before|after|on)\b", desc, re.IGNORECASE):
            errors.append(f"skill {sk['id']}: description should say when to use it (\"Use when/for/before ...\")")
        if sk["role"] is not None:
            if sk["role"] not in ids["roles"]:
                errors.append(f"skill {sk['id']}: unknown role {sk['role']}")
            covered_roles.add(sk["role"])
        for ph in sk["phases"]:
            if ph not in ids["phases"]:
                errors.append(f"skill {sk['id']}: unknown phase {ph}")
        for b in sk["bundle"]:
            if not (ROOT / b).is_file():
                errors.append(f"skill {sk['id']}: bundled file {b} not found")
    for role in process["roles"]:
        if role["kind"] == "agent" and role["id"] not in covered_roles:
            errors.append(f"agent role {role['id']} has no role skill")
    return errors


def report(errors: list[str]) -> int:
    if errors:
        print(f"✖ {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("✔ dev-process repository is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())

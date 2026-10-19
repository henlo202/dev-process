#!/usr/bin/env python3
"""Validate the dev-process repository itself (not projects; use check.py for those).

Checks: process.yaml against its schema, cross-references between phases,
gates, artefacts and roles, that every referenced file exists, that no process
document is orphaned, that relative Markdown links resolve, and that the
process version matches the latest CHANGELOG entry.

Exits 1 on any error. This strictness applies to the process repository only;
project conformance remains warn-only (PDR-0003).

Requires: PyYAML, jsonschema.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CONTENT_DIRS = ["phases", "gates", "artefacts", "roles", "guides", "governance", "agents"]


def main() -> int:
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
        for a in g["evidence"]:
            if a not in ids["artefacts"]:
                errors.append(f"gate {g['id']}: unknown evidence artefact {a}")
    for a in process["artefacts"]:
        if a["owner"] not in ids["roles"]:
            errors.append(f"artefact {a['id']}: unknown owner {a['owner']}")
        if a["template"] and not (ROOT / a["template"]).is_file():
            errors.append(f"artefact {a['id']}: template {a['template']} not found")

    referenced = set()
    for kind in ("tiers", "roles", "phases", "gates", "artefacts", "guides", "governance"):
        for e in process[kind]:
            if not (ROOT / e["doc"]).is_file():
                errors.append(f"{kind} {e['id']}: doc {e['doc']} not found")
            referenced.add(e["doc"])

    md_files = [p for d in CONTENT_DIRS for p in (ROOT / d).rglob("*.md")]
    md_files += [ROOT / "README.md", ROOT / "CHANGELOG.md"]
    for p in md_files:
        rel = p.relative_to(ROOT).as_posix()
        in_auto_dir = rel.startswith(("artefacts/templates/", "agents/", "governance/decisions/"))
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
    return report(errors)


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

#!/usr/bin/env python3
"""Generate the dev-process HTML site from process.yaml and the Markdown sources.

    python site/build.py [--out _site]

The site is fully static and uses relative links, so it works from the file
system, GitHub Pages or any web server. Structural information (inputs,
outputs, gates, tiers, backlinks) comes from process.yaml, so pages are
never maintained by hand (PDR-0004).

Requires: PyYAML, Markdown.
"""
from __future__ import annotations

import argparse
import html
import posixpath
import re
import shutil
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
TIERS = ["T1", "T2", "T3"]


# ---------------------------------------------------------------- helpers

def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("\n---", 1)
        if len(parts) == 2:
            return parts[1].lstrip("-").lstrip("\n")
    return text


def page_path(src: str) -> str:
    """Map a source path (relative to ROOT) to its output HTML path."""
    p = Path(src)
    return (p.parent / (p.stem + ".html")).as_posix()


def rel(from_page: str, to_page: str) -> str:
    return posixpath.relpath(to_page, posixpath.dirname(from_page) or ".")


def esc(s) -> str:
    return html.escape(str(s))


class Site:
    def __init__(self, out: Path):
        self.out = out
        self.p = yaml.safe_load((ROOT / "process.yaml").read_text(encoding="utf-8"))
        self.by_id = {}
        for kind in ("tiers", "roles", "phases", "gates", "artefacts", "guides", "governance"):
            for e in self.p[kind]:
                self.by_id[(kind, e["id"])] = e
        self.decisions = sorted((ROOT / "governance" / "decisions").glob("*.md"))
        self.skills = self.p["skills"]
        self.templates = sorted(p for p in (ROOT / "artefacts" / "templates").iterdir() if p.is_file())
        self.md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"])

    # ------------------------------------------------------------ linking

    def link(self, here: str, kind: str, id_: str, label: str | None = None) -> str:
        e = self.by_id.get((kind, id_))
        if not e:
            return esc(label or id_)
        text = label or (f"{e['id']} · {e['name']}" if kind in ("phases", "gates") else e["name"])
        return f'<a href="{rel(here, page_path(e["doc"]))}">{esc(text)}</a>'

    def links(self, here, kind, ids):
        return ", ".join(self.link(here, kind, i) for i in ids) or "—"

    def tier_badges(self, tiers):
        return "".join(f'<span class="badge tier-{t}">{t}</span>' for t in tiers) or '<span class="muted">—</span>'

    # ----------------------------------------------------------- markdown

    def render_md(self, src: Path, here: str) -> str:
        self.md.reset()
        body = self.md.convert(strip_frontmatter(src.read_text(encoding="utf-8")))

        def fix_href(m):
            href = m.group(1)
            if re.match(r"^[a-z]+:", href) or href.startswith("#"):
                return m.group(0)
            path, _, frag = href.partition("#")
            target = (src.parent / path).resolve()
            try:
                target_rel = target.relative_to(ROOT).as_posix()
            except ValueError:
                return m.group(0)
            if target.is_dir():
                index = self.dir_index(target_rel)
                if index:
                    return f'href="{rel(here, index)}"'
                return m.group(0)
            if target.suffix == ".md" or target_rel.startswith("artefacts/templates/"):
                new = rel(here, page_path(target_rel))
            else:
                new = rel(here, target_rel)  # raw file copied into the site
            return f'href="{new}{"#" + frag if frag else ""}"'

        body = re.sub(r'href="([^"]+)"', fix_href, body)
        body = re.sub(r"<li>\[ \]\s*", '<li class="task"><input type="checkbox"> ', body)
        body = re.sub(r"<li>\[x\]\s*", '<li class="task"><input type="checkbox" checked> ', body)
        return body

    def dir_index(self, d: str) -> str | None:
        return {
            "phases": "index.html#flow", "gates": "index.html#gates", "artefacts": "index.html#artefacts",
            "artefacts/templates": "templates.html", "guides": "index.html#guides",
            "governance": page_path("governance/ownership.md"), "agents": page_path("agents/README.md"),
            "roles": page_path("roles/roles.md"), "tooling": "index.html#tooling",
            "examples": "index.html#tooling", "site": "index.html",
        }.get(d.rstrip("/"))

    # ------------------------------------------------------------- panels

    def phase_panel(self, ph, here):
        rows = [
            ("Applies to", self.tier_badges(ph["tiers"]) + (' <span class="muted">· once per initiative</span>'
                                                            if ph.get("once_per_initiative") else "")),
            ("Roles", self.links(here, "roles", ph["roles"])),
            ("Inputs", self.links(here, "artefacts", ph["inputs"])),
            ("Outputs", self.links(here, "artefacts", ph["outputs"])),
            ("Gate", self.link(here, "gates", ph["gate"]) if ph["gate"] else '<span class="muted">none: flows on</span>'),
        ]
        phases = self.p["phases"]
        i = phases.index(ph)
        nav = '<nav class="pager">'
        if i > 0:
            nav += f'<a href="{rel(here, page_path(phases[i-1]["doc"]))}">← {esc(phases[i-1]["id"])} {esc(phases[i-1]["name"])}</a>'
        nav += "<span></span>"
        if i < len(phases) - 1:
            nav += f'<a href="{rel(here, page_path(phases[i+1]["doc"]))}">{esc(phases[i+1]["id"])} {esc(phases[i+1]["name"])} →</a>'
        else:
            first = next(p for p in phases if p.get("loop"))
            nav += (f'<a href="{rel(here, page_path(first["doc"]))}">↻ next increment: '
                    f'{esc(first["id"])} {esc(first["name"])}</a>')
        nav += "</nav>"
        return self.panel(rows), nav

    def gate_panel(self, g, here):
        rows = [
            ("After phase", self.link(here, "phases", g["after"])),
            ("Approver", self.link(here, "roles", g["approver"])),
            ("Applies to", self.tier_badges(g["tiers"]) + (' <span class="muted">· once per initiative</span>'
                                                           if g.get("once_per_initiative") else "")),
            ("Evidence", self.links(here, "artefacts", g["evidence"])),
        ]
        for tier, extra in (g.get("tier_evidence") or {}).items():
            rows.append((f"Also for {tier}", self.links(here, "artefacts", extra)))
        return self.panel(rows), ""

    def artefact_panel(self, arts, here):
        out = []
        for a in arts:
            produced = [ph["id"] for ph in self.p["phases"] if a["id"] in ph["outputs"]]
            used = [ph["id"] for ph in self.p["phases"] if a["id"] in ph["inputs"]]
            gates = [g["id"] for g in self.p["gates"] if a["id"] in g["evidence"]]
            tmpl = (f'<a href="{rel(here, page_path(a["template"]))}">{esc(Path(a["template"]).name)}</a>'
                    if a["template"] else '<span class="muted">—</span>')
            rows = [
                ("In project", f"<code>{esc(a['path'])}</code>" if a["path"] else '<span class="muted">not a file in the repo</span>'),
                ("Scope", esc(a["scope"])),
                ("Owner", self.link(here, "roles", a["owner"])),
                ("Required for", self.tier_badges(a["required_tiers"])),
                ("Template", tmpl),
                ("Produced in", self.links(here, "phases", produced)),
                ("Used in", self.links(here, "phases", used)),
                ("Evidence at", self.links(here, "gates", gates)),
            ]
            title = f'<div class="panel-title">{esc(a["name"])}</div>' if len(arts) > 1 else ""
            out.append(self.panel(rows, title))
        return "".join(out), ""

    def model_class_html(self, entry) -> str:
        if not entry.get("model_class"):
            return '<span class="muted">—</span>'
        out = f'<code>{esc(entry["model_class"])}</code>'
        for tier, cls in (entry.get("tier_model_class") or {}).items():
            out += f' <span class="muted">· {esc(tier)}:</span> <code>{esc(cls)}</code>'
        return out

    def roles_panel(self, here):
        guide = rel(here, page_path("guides/resource-economy.md"))
        rows = [(r["name"], self.model_class_html(r)) for r in self.p["roles"] if r["kind"] == "agent"]
        title = f'<div class="panel-title"><a href="{guide}">Model classes</a></div>'
        return self.panel(rows, title)

    def skill_panel(self, sk, here):
        text = (ROOT / sk["doc"]).read_text(encoding="utf-8")
        fm = yaml.safe_load(text.split("\n---", 1)[0].lstrip("-")) or {}
        bundle = ", ".join(f'<a href="{rel(here, page_path(b))}">{esc(Path(b).name)}</a>' for b in sk["bundle"])
        rows = [
            ("Skill name", f"<code>{esc(fm.get('name', sk['id']))}</code>"),
            ("Use when", esc(fm.get("description", ""))),
            ("Kind", "role skill" if sk["kind"] == "role" else "task skill"),
            ("Role", self.link(here, "roles", sk["role"]) if sk["role"] else '<span class="muted">any</span>'),
            ("Phases", self.links(here, "phases", sk["phases"])),
            ("Model class", self.model_class_html(
                next(r for r in self.p["roles"] if r["id"] == sk["role"]) if sk["role"] else sk)),
            ("Bundled", bundle or '<span class="muted">—</span>'),
            ("In a project", f"<code>.process/skills/{esc(sk['id'])}/SKILL.md</code>"),
        ]
        return self.panel(rows)

    @staticmethod
    def panel(rows, title=""):
        cells = "".join(f"<dt>{esc(k)}</dt><dd>{v}</dd>" for k, v in rows)
        return f'<aside class="panel">{title}<dl>{cells}</dl></aside>'

    # ---------------------------------------------------------------- nav

    def nav(self, here: str) -> str:
        def item(href, label, sub=""):
            cur = ' aria-current="page"' if href == here else ""
            sub_html = f'<span class="nav-id">{esc(sub)}</span>' if sub else ""
            return f'<li><a href="{rel(here, href)}"{cur}>{sub_html}{esc(label)}</a></li>'

        def section(title, items, open_=True):
            return (f'<details class="nav-sec"{" open" if open_ else ""}><summary>{esc(title)}</summary>'
                    f'<ul>{"".join(items)}</ul></details>')

        p = self.p
        parts = [
            '<ul class="nav-top">' + item("index.html", "Overview") + "</ul>",
            section("Phases", [item(page_path(x["doc"]), x["name"], x["id"]) for x in p["phases"]]),
            section("Gates", [item(page_path(x["doc"]), x["name"], x["id"]) for x in p["gates"]]),
            section("Artefacts", [item(page_path(d), n) for d, n in self.artefact_docs()], False),
            section("Roles & agents", [item(page_path("roles/roles.md"), "Roles"),
                                       item(page_path("agents/README.md"), "Agent skills")]
                    + [item(page_path(sk["doc"]), sk["id"].removeprefix("dev-process-"), "▸")
                       for sk in self.skills], False),
            section("Guides", [item(page_path(x["doc"]), x["name"]) for x in p["guides"]], False),
            section("Governance", [item(page_path(x["doc"]), x["name"]) for x in p["governance"]]
                    + [item(page_path(f"governance/decisions/{d.name}"), self.title_of(d).split(":")[0], "▸")
                       for d in self.decisions], False),
            '<ul class="nav-top">' + item("templates.html", "Templates") + "</ul>",
        ]
        return "".join(parts)

    def artefact_docs(self):
        seen = {}
        for a in self.p["artefacts"]:
            seen.setdefault(a["doc"], []).append(a["name"])
        return [(d, " & ".join(n) if len(n) < 3 else n[0]) for d, n in seen.items()]

    @staticmethod
    def title_of(path: Path) -> str:
        for line in strip_frontmatter(path.read_text(encoding="utf-8")).splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return path.stem

    # -------------------------------------------------------------- pages

    def write(self, here: str, title: str, body: str):
        out = self.out / here
        out.parent.mkdir(parents=True, exist_ok=True)
        css = rel(here, "assets/style.css")
        js = rel(here, "assets/site.js")
        version = esc(self.p["process"]["version"])
        out.write_text(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · dev-process</title>
<link rel="stylesheet" href="{css}">
</head>
<body>
<header class="top">
  <button class="menu" aria-label="Toggle navigation" aria-expanded="false">☰</button>
  <a class="brand" href="{rel(here, 'index.html')}">dev-process</a>
  <span class="version">v{version}</span>
  <a class="raw" href="{rel(here, 'process.yaml')}">process.yaml</a>
</header>
<div class="layout">
  <nav class="side" aria-label="Process navigation">
    <input class="filter" type="search" placeholder="Filter…" aria-label="Filter navigation">
    {self.nav(here)}
  </nav>
  <main class="content">
{body}
  </main>
</div>
<script src="{js}"></script>
</body>
</html>
""", encoding="utf-8")

    def doc_page(self, src: str, panel_html: str = "", footer: str = ""):
        here = page_path(src)
        body = self.render_md(ROOT / src, here)
        # Put the structural panel directly after the H1.
        if panel_html:
            body = re.sub(r"</h1>", lambda m: m.group(0) + panel_html, body, count=1)
        self.write(here, self.title_of(ROOT / src), body + footer)

    def template_page(self, path: Path):
        src = path.relative_to(ROOT).as_posix()
        here = page_path(src)
        users = [a["name"] for a in self.p["artefacts"] if a["template"] == src]
        used_for = f'<p>Template for: <strong>{esc(", ".join(users))}</strong></p>' if users else ""
        body = (f'<h1>Template: <code>{esc(path.name)}</code></h1>{used_for}'
                f'<p class="muted">The scaffolder copies this into projects and replaces <code>{{{{placeholders}}}}</code>. '
                f'It is also available in each project at <code>.process/templates/{esc(path.name)}</code>.</p>'
                f'<div class="code-wrap"><button class="copy">Copy</button>'
                f'<pre><code>{esc(path.read_text(encoding="utf-8"))}</code></pre></div>')
        self.write(here, f"Template {path.name}", body)

    def templates_index(self):
        here = "templates.html"
        rows = []
        for t in self.templates:
            src = t.relative_to(ROOT).as_posix()
            users = ", ".join(a["name"] for a in self.p["artefacts"] if a["template"] == src) or "Pull-request description (G2)"
            rows.append(f'<tr><td><a href="{rel(here, page_path(src))}"><code>{esc(t.name)}</code></a></td><td>{esc(users)}</td></tr>')
        self.write(here, "Templates", "<h1>Templates</h1><table><thead><tr><th>File</th><th>Used for</th></tr></thead>"
                   f"<tbody>{''.join(rows)}</tbody></table>")

    def index(self):
        here = "index.html"
        p = self.p
        def steps(phases):
            out = []
            for ph in phases:
                out.append(
                    f'<a class="step phase" data-tiers="{" ".join(ph["tiers"])}" href="{rel(here, page_path(ph["doc"]))}">'
                    f'<span class="step-id">{esc(ph["id"])}</span><span class="step-name">{esc(ph["name"])}</span>'
                    f'<span class="step-tiers">{self.tier_badges(ph["tiers"])}</span></a>')
                if ph["gate"]:
                    g = self.by_id[("gates", ph["gate"])]
                    out.append(
                        f'<a class="step gate" data-tiers="{" ".join(g["tiers"])}" href="{rel(here, page_path(g["doc"]))}" '
                        f'title="{esc(g["name"])}: approved by the Owner"><span class="diamond"><span>{esc(g["id"])}</span></span>'
                        f'<span class="gate-name">{esc(g["name"])}</span></a>')
                else:
                    out.append('<span class="step arrow" aria-hidden="true">→</span>')
            return out

        setup = steps([ph for ph in p["phases"] if not ph.get("loop")])
        loop = steps([ph for ph in p["phases"] if ph.get("loop")])
        loop.pop()  # the loop's last phase connects back to its first
        flow = (f'<div class="flow">{"".join(setup)}'
                f'<div class="loop"><span class="loop-label">Increment loop: repeat for every increment</span>'
                f'<div class="loop-steps">{"".join(loop)}</div>'
                f'<span class="loop-back" aria-hidden="true">↻ back to {esc(p["phases"][1]["id"])} for the next increment</span>'
                f'</div></div>')

        tier_cards = "".join(
            f'<div class="tier-card"><span class="badge tier-{t["id"]}">{t["id"]}</span> '
            f'<strong>{esc(t["name"])}</strong><p>{esc(t["summary"])}</p></div>' for t in p["tiers"])

        gate_rows = "".join(
            f'<tr><td>{self.link(here, "gates", g["id"])}</td><td>{self.link(here, "phases", g["after"])}</td>'
            + "".join(f'<td class="c">{"●" if t in g["tiers"] else ""}</td>' for t in TIERS) + "</tr>"
            for g in p["gates"])

        art_rows = "".join(
            f'<tr><td>{self.link(here, "artefacts", a["id"])}</td>'
            f'<td>{"<code>" + esc(a["path"]) + "</code>" if a["path"] else "<span class=muted>—</span>"}</td>'
            f'<td>{self.link(here, "roles", a["owner"])}</td>'
            + "".join(f'<td class="c">{"●" if t in a["required_tiers"] else ""}</td>' for t in TIERS) + "</tr>"
            for a in p["artefacts"])

        guides = "".join(f'<li>{self.link(here, "guides", g["id"])}</li>' for g in p["guides"])
        gov = "".join(f'<li>{self.link(here, "governance", g["id"])}</li>' for g in p["governance"])
        skills = "".join(
            f'<li><a href="{rel(here, page_path(sk["doc"]))}"><code>{esc(sk["id"])}</code></a>'
            f' <span class="muted small">{"role" if sk["kind"] == "role" else "task"}</span></li>'
            for sk in self.skills)

        body = f"""
<h1>dev-process</h1>
<p class="lead">{esc(p["process"]["summary"])}</p>

<h2 id="flow">The loop</h2>
<div class="tier-filter" role="group" aria-label="Show flow for tier">
  <span class="muted">Show for:</span>
  <button data-tier="all" aria-pressed="true">All</button>
  <button data-tier="T1" aria-pressed="false">T1 Trivial</button>
  <button data-tier="T2" aria-pressed="false">T2 Standard</button>
  <button data-tier="T3" aria-pressed="false">T3 Major</button>
</div>
{flow}
<p class="muted small">Phases are boxes; ◆ diamonds are human gates approved by the Owner.
P0 runs once per initiative. Then every increment goes round the loop, and T1 changes enter at P2.
See <a href="{rel(here, page_path("guides/increments.md"))}">Increments &amp; the loop</a>.</p>

<h2 id="tiers">Risk tiers</h2>
<div class="tiers">{tier_cards}</div>
<p>{self.link(here, "guides", "risk-tiers", "How to choose a tier →")}</p>

<h2 id="gates">Gates</h2>
<div class="table-wrap"><table>
<thead><tr><th>Gate</th><th>After</th><th class="c">T1</th><th class="c">T2</th><th class="c">T3</th></tr></thead>
<tbody>{gate_rows}</tbody></table></div>

<h2 id="artefacts">Standard artefacts</h2>
<p class="muted">● = required by the conformance check for that tier.</p>
<div class="table-wrap"><table>
<thead><tr><th>Artefact</th><th>In project</th><th>Owner</th><th class="c">T1</th><th class="c">T2</th><th class="c">T3</th></tr></thead>
<tbody>{art_rows}</tbody></table></div>

<div class="cols">
<section><h2 id="guides">Guides</h2><ul>{guides}</ul></section>
<section><h2 id="governance">Governance</h2><ul>{gov}</ul></section>
<section><h2 id="skills">Agent skills</h2><ul>{skills}</ul></section>
</div>

<h2 id="tooling">Tooling</h2>
<pre><code># adopt in a project (never overwrites existing files)
python tooling/scaffold.py ../my-project --name "My project" --tier T2 \
    --guardrails block --adapter claude --github --install-hooks
# check conformance (warns, never blocks)
python .process/check.py
# upgrade a project to a newer process version
python tooling/scaffold.py ../my-project --upgrade</code></pre>
<p>A worked example lives in <code>examples/greeter-cli</code> in the repository.</p>
"""
        self.write(here, "Overview", body)

    # -------------------------------------------------------------- build

    def build(self):
        if self.out.exists():
            shutil.rmtree(self.out)
        (self.out / "assets").mkdir(parents=True)
        shutil.copy2(ROOT / "site" / "assets" / "style.css", self.out / "assets" / "style.css")
        shutil.copy2(ROOT / "site" / "assets" / "site.js", self.out / "assets" / "site.js")
        shutil.copy2(ROOT / "process.yaml", self.out / "process.yaml")
        shutil.copytree(ROOT / "schema", self.out / "schema")

        self.index()
        for ph in self.p["phases"]:
            panel, nav = self.phase_panel(ph, page_path(ph["doc"]))
            self.doc_page(ph["doc"], panel, nav)
        for g in self.p["gates"]:
            panel, _ = self.gate_panel(g, page_path(g["doc"]))
            self.doc_page(g["doc"], panel)
        docs: dict[str, list] = {}
        for a in self.p["artefacts"]:
            docs.setdefault(a["doc"], []).append(a)
        for doc, arts in docs.items():
            panel, _ = self.artefact_panel(arts, page_path(doc))
            self.doc_page(doc, panel)
        for kind in ("guides", "governance"):
            for e in self.p[kind]:
                self.doc_page(e["doc"])
        self.doc_page("roles/roles.md", self.roles_panel(page_path("roles/roles.md")))
        self.doc_page("agents/README.md")
        for sk in self.skills:
            here = page_path(sk["doc"])
            self.doc_page(sk["doc"], self.skill_panel(sk, here))
        for f in self.decisions:
            self.doc_page(f.relative_to(ROOT).as_posix())
        for t in self.templates:
            self.template_page(t)
        self.templates_index()
        (self.out / ".nojekyll").touch()
        count = len(list(self.out.rglob("*.html")))
        print(f"Built {count} pages into {self.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(ROOT / "_site"))
    args = ap.parse_args()
    Site(Path(args.out).resolve()).build()


if __name__ == "__main__":
    main()

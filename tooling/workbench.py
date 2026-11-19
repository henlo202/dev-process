#!/usr/bin/env python3
"""dev-process workbench: a live, read-only web view of a project's process state.

The repository is the single source of truth. Every page is rendered from the
files and git state at request time, so nothing is built, cached or synced and
the Owner never has to open a Markdown file to see where the project stands.

    python .process/workbench.py                      # this project, http://127.0.0.1:8765
    python .process/workbench.py --lan                # reachable from the local network
    python .process/workbench.py --root C:\\dev       # every project found one level below
    python .process/workbench.py --project A --project B --port 9000

Works for both dev-process (.process/) and dev-process-lite (.lite/); the same file
ships in both. Stdlib only. dev-process projects reuse .process/status.py for the
phase and next step (which needs PyYAML, as status.py does).

Safety: GET only; serves only Markdown and images inside the project, never
dot-folders, secrets or anything outside it. There is no login: use it on a
network you trust (see --lan).
"""
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import mimetypes
import re
import socket
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
SECRET_NAME = re.compile(r"(secret|\.env$|\.pem$|\.key$|credential|token)", re.I)
PLACEHOLDER = re.compile(r"<(?!!--)[A-Za-z][^<>=\"`\n]*\s[^<>=\"`\n]*>")
FENCE = re.compile(r"```.*?```|`[^`\n]+`", re.DOTALL)
PHASES = [("P0", "Initiate"), ("P1", "Shape"), ("P2", "Build"), ("P3", "Verify"), ("P4", "Release"), ("P5", "Learn")]
GATES = [("G0", "Go / no-go"), ("G1", "Shape approved"), ("G2", "Merge approved"), ("G3", "Release approved")]
LITE_STAGES = ["Ask", "Branch", "Build", "Check", "PR", "Merge"]
esc = html.escape


# ------------------------------------------------------------------ reading files

def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Frontmatter as a flat dict (strings, lists of strings) and the body. No YAML needed."""
    if not text.startswith("---"):
        return {}, text
    head, sep, body = text[3:].partition("\n---")
    if not sep:
        return {}, text
    data: dict = {}
    for line in head.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$", line)
        if not m:
            continue
        key, val = m.group(1), re.sub(r"\s+#.*$", "", m.group(2)).strip()
        if val.startswith("[") and val.endswith("]"):
            data[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
        else:
            data[key] = val.strip("'\"")
    return data, body.split("\n", 1)[1] if "\n" in body else ""


def title_of(text: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+?)\s*$", split_frontmatter(text)[1], re.MULTILINE)
    return m.group(1) if m else fallback


def has_placeholders(text: str) -> bool:
    return bool(PLACEHOLDER.search(FENCE.sub("", text)))


def git(root: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def md_files(root: Path, *subdirs: str) -> list[Path]:
    out: list[Path] = []
    for sub in subdirs:
        base = root / sub
        if base.is_file():
            out.append(base)
        elif base.is_dir():
            out += sorted(p for p in base.rglob("*.md") if not any(part.startswith(".") for part in p.relative_to(root).parts))
    return out


# ------------------------------------------------------------------ markdown

def _inline(text: str, link) -> str:
    """Inline Markdown on raw text. Everything is HTML-escaped; only known constructs become tags."""
    codes: list[str] = []

    def stash(m):
        codes.append(f"<code>{esc(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`\n]+)`", stash, text)
    text = esc(text, quote=False)
    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", lambda m: link(m.group(2), m.group(1), True), text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: link(m.group(2), m.group(1), False), text)
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w_])_([^_\n]+)_(?![\w_])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def slugify(text: str) -> str:
    return re.sub(r"[^\w]+", "-", re.sub(r"[`*_]", "", text).lower()).strip("-")


def render_markdown(text: str, link=None) -> str:
    """Small, safe Markdown to HTML: headings, lists, tasks, tables, quotes, code, rules."""
    link = link or (lambda href, label, image: f'<a href="{esc(href)}">{label}</a>')
    text = re.sub(r"<!--.*?-->", "", split_frontmatter(text)[1].replace("\r\n", "\n"), flags=re.DOTALL)
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    inline = lambda s: _inline(s, link)  # noqa: E731

    def is_block_start(s: str) -> bool:
        return bool(re.match(r"^(#{1,6}\s|```|>|\s*([-*+]|\d+\.)\s|\s*\|.*\||(-{3,}|\*{3,})\s*$)", s))

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("```"):
            lang = esc(line[3:].strip())
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append(f'<pre data-lang="{lang}"><code>{esc(chr(10).join(buf))}</code></pre>')
        elif m := re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line):
            level, content = len(m.group(1)), m.group(2)
            ident = re.match(r"^\W*((?:[A-Z]{2,5}|[A-Z])-\d+[a-z]?)\b", content)
            anchor = f'<a id="{esc(ident.group(1).lower())}"></a>' if ident else ""
            out.append(f'{anchor}<h{level} id="{esc(slugify(content))}">{inline(content)}</h{level}>')
            i += 1
        elif re.match(r"^(-{3,}|\*{3,})\s*$", line):
            out.append("<hr>")
            i += 1
        elif line.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            out.append(f"<blockquote>{render_markdown(chr(10).join(buf), link)}</blockquote>")
        elif "|" in line and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$", lines[i + 1]):
            cells = lambda s: [c.strip() for c in s.strip().strip("|").split("|")]  # noqa: E731
            head = cells(line)
            i += 2
            rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(cells(lines[i]))
                i += 1
            out.append("<div class=\"scroll\"><table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head)
                       + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                                                          for r in rows) + "</tbody></table></div>")
        elif re.match(r"^\s*([-*+]|\d+\.)\s+", line):
            items = []  # (indent, ordered, text)
            while i < len(lines) and lines[i].strip() and (re.match(r"^\s*([-*+]|\d+\.)\s+", lines[i]) or
                                                          (lines[i].startswith((" ", "\t")) and items)):
                m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", lines[i])
                if m:
                    items.append([len(m.group(1).replace("\t", "    ")), m.group(2)[0].isdigit(), m.group(3)])
                else:
                    items[-1][2] += " " + lines[i].strip()
                i += 1
            out.append(_render_list(items, inline))
        else:
            buf = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not is_block_start(lines[i]):
                buf.append(lines[i])
                i += 1
            out.append(f"<p>{inline(' '.join(s.strip() for s in buf))}</p>")
    return "\n".join(out)


def _render_list(items, inline) -> str:
    html_out: list[str] = []
    stack: list[tuple[int, str]] = []
    for indent, ordered, content in items:
        tag = "ol" if ordered else "ul"
        while stack and indent < stack[-1][0]:
            html_out.append(f"</li></{stack.pop()[1]}>")
        if stack and indent == stack[-1][0]:
            html_out.append("</li>")
        elif not stack or indent > stack[-1][0]:
            html_out.append(f"<{tag}>")
            stack.append((indent, tag))
        task = re.match(r"^\[([ xX])\]\s+(.*)$", content)
        if task:
            box = "&#9745;" if task.group(1) != " " else "&#9744;"
            html_out.append(f'<li class="task">{box} {inline(task.group(2))}')
        else:
            html_out.append(f"<li>{inline(content)}")
    while stack:
        html_out.append(f"</li></{stack.pop()[1]}>")
    return "".join(html_out)


# ------------------------------------------------------------------ project models

def _doc_row(root: Path, path: Path) -> dict:
    text = read(path)
    fm, _ = split_frontmatter(text)
    rel = path.relative_to(root).as_posix()
    return {"path": rel, "title": title_of(text, path.stem), "status": fm.get("status", ""),
            "updated": fm.get("updated", ""), "fm": fm, "stub": has_placeholders(text), "text": text}


def parse_requirements(root: Path) -> list[dict]:
    rows = []
    for path in md_files(root, "docs/requirements"):
        rel = path.relative_to(root).as_posix()
        text = split_frontmatter(read(path))[1]
        for m in re.finditer(r"^###\s+([A-Z][A-Z0-9]*-\d+)[ 	]*(?::|—|–|-)[ 	]*(.+?)\s*$(.*?)(?=^#{1,3}\s|\Z)", text, re.MULTILINE | re.DOTALL):
            body = m.group(3)
            field = lambda name: (re.search(rf"\*\*{name}:\*\*\s*(.+)", body) or [None, ""])[1].strip()  # noqa: E731
            rows.append({"id": m.group(1), "title": m.group(2), "priority": field("Priority"),
                         "status": field("Status"), "impl": field("Implementation"), "file": rel,
                         "kind": m.group(1).split("-")[0]})
    return rows


class Model:
    """What a project looks like to the workbench. Subclasses add the process-specific parts."""
    kind = ""

    def __init__(self, root: Path):
        self.root = root
        self.name = root.name

    def docs(self) -> list[dict]:
        rows = [_doc_row(self.root, p) for p in md_files(self.root, "docs", "README.md", "AGENTS.md", "CHANGELOG.md")]
        return rows

    def fingerprint(self) -> str:
        h = hashlib.sha1()
        paths = md_files(self.root, "docs", "README.md", "AGENTS.md", "CHANGELOG.md")
        git_dir = self.root / ".git"
        if git_dir.is_dir():
            paths += [git_dir / "HEAD", git_dir / "index", git_dir / "packed-refs"]
            paths += [p for p in (git_dir / "refs").rglob("*") if p.is_file()]
        for p in paths:
            try:
                st = p.stat()
                h.update(f"{p}{st.st_mtime_ns}{st.st_size}".encode())
            except OSError:
                pass
        return h.hexdigest()[:16]


class FullModel(Model):
    kind = "dev-process"

    def __init__(self, root: Path):
        super().__init__(root)
        self.status = self._load_status()
        self.project = self.status.Project(root) if self.status else None
        self.config = self.project.config if self.project else {}
        self.name = self.config.get("project") or root.name

    def _load_status(self):
        path = self.root / ".process" / "status.py"
        if not path.is_file():
            return None
        try:
            spec = importlib.util.spec_from_file_location(f"_status_{abs(hash(path))}", path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod  # dataclasses needs the module registered
            spec.loader.exec_module(mod)
            return mod
        except Exception:  # missing PyYAML, broken file: the workbench still shows the documents
            return None

    def step(self):
        return self.status.next_step(self.project) if self.project else None

    def increments(self) -> list[dict]:
        rows = []
        for p in self.project.increments if self.project else []:
            text = p["_text"]
            slices = self.status.SLICE.findall(self.status.section(text, "Task slices"))
            budget = self.project.budget(p)
            rows.append({"id": str(p.get("increment")), "title": title_of(text, ""), "status": p.get("status", ""),
                         "tier": p.get("tier", ""), "path": p["_path"].relative_to(self.root).as_posix(),
                         "slices": [(mark.lower() == "x", s, t) for mark, s, t in slices],
                         "budget": budget, "reqs": p.get("requirements") or [],
                         "outcome": self.status.section(text, "Outcome")})
        return rows

    def gates(self) -> list[dict]:
        rows = []
        for p in md_files(self.root, "docs/gates"):
            fm, _ = split_frontmatter(read(p))
            if fm.get("artefact") == "gate-record":
                rows.append({**fm, "path": p.relative_to(self.root).as_posix()})
        return rows

    def adrs(self) -> list[dict]:
        rows = []
        for p in md_files(self.root, "docs/adr"):
            d = _doc_row(self.root, p)
            if d["fm"].get("artefact") == "adr":
                rows.append(d)
        return rows


class LiteModel(Model):
    kind = "dev-process-lite"

    def __init__(self, root: Path):
        super().__init__(root)
        self.version = read(root / ".lite" / "VERSION").strip() or "?"
        m = re.search(r"^# Spec:\s*(.+)$", read(root / "docs" / "spec.md"), re.MULTILINE)
        self.name = m.group(1).strip() if m and "<" not in m.group(1) else root.name
        self.is_git = git(root, "rev-parse", "--is-inside-work-tree") == "true"

    def base(self) -> str:
        for b in ("main", "master"):
            if git(self.root, "rev-parse", "--verify", "-q", b):
                return b
        return "main"

    def git_state(self) -> dict:
        if not self.is_git:
            return {"is_git": False}
        base = self.base()
        branch = git(self.root, "rev-parse", "--abbrev-ref", "HEAD") or "?"
        dirty = len([l for l in (git(self.root, "status", "--porcelain") or "").splitlines() if l.strip()])
        branches = []
        for b in (git(self.root, "for-each-ref", "refs/heads", "--format=%(refname:short)") or "").splitlines():
            if b == base:
                continue
            ahead = int(git(self.root, "rev-list", "--count", f"{base}..{b}") or 0)
            if ahead:
                last = git(self.root, "log", "-1", "--format=%s|%cr", b) or "|"
                branches.append({"name": b, "ahead": ahead, "last": last.split("|")[0], "when": last.split("|")[-1]})
        log = []
        for row in (git(self.root, "log", base, "-12", "--format=%h|%cs|%s") or "").splitlines():
            h, d, s = (row.split("|", 2) + ["", ""])[:3]
            log.append({"hash": h, "date": d, "subject": s})
        ahead_here = int(git(self.root, "rev-list", "--count", f"{base}..HEAD") or 0) if branch != base else 0
        return {"is_git": True, "base": base, "branch": branch, "dirty": dirty, "branches": branches, "log": log,
                "ahead_here": ahead_here, "tag": git(self.root, "describe", "--tags", "--abbrev=0")}

    def stage(self, g: dict) -> tuple[int, str]:
        """Where the change in flight is, inferred from git alone: (index into LITE_STAGES, explanation)."""
        if not g.get("is_git"):
            return 0, "Not a git repository, so progress cannot be inferred."
        if g["branch"] == g["base"]:
            if g["branches"]:
                names = ", ".join(b["name"] for b in g["branches"])
                return 5, f"Waiting for the Owner to merge: {names}"
            return 0, "Idle. Tell the agent what to change."
        if g["dirty"]:
            return 2, f"Building on {g['branch']}: {g['ahead_here']} commit(s), {g['dirty']} uncommitted change(s)."
        if g["ahead_here"] == 0:
            return 1, f"Branch {g['branch']} started, no commits yet."
        return 4, f"{g['branch']} is {g['ahead_here']} commit(s) ahead of {g['base']} and clean: ready for a PR or merge."

    def features(self) -> list[tuple[str, str]]:
        text = FENCE.sub("", split_frontmatter(read(self.root / "docs" / "spec.md"))[1])
        found = [(m.group(1), m.group(2).strip()) for m in re.finditer(r"^-[ 	]+(F\d+):[ 	]*(.*)$", text, re.MULTILINE)]
        return [(i, t) for i, t in found if t and not has_placeholders(t)]  # skip empty and template-stub lines

    def outline(self, rel: str) -> list[tuple[str, bool]]:
        """Second-level sections of a file and whether each has real content."""
        text = re.sub(r"<!--.*?-->", "", read(self.root / rel), flags=re.DOTALL)
        out = []
        for m in re.finditer(r"^##\s+(.+?)\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL):
            body = m.group(2).strip()
            out.append((m.group(1), bool(body) and not has_placeholders(body)))
        return out


def detect(root: Path) -> Model | None:
    if (root / ".process" / "config.yaml").is_file():
        return FullModel(root)
    if (root / ".lite").is_dir():
        return LiteModel(root)
    return None


# ------------------------------------------------------------------ pages

CSS = """
:root{--bg:#f6f7f9;--fg:#1c2230;--mut:#5d6778;--card:#fff;--line:#dfe3ea;--acc:#2f6fed;--ok:#1f8a4c;--warn:#b7791f;--bad:#c53030;--okbg:#e3f4ea;--warnbg:#fbf0d9;--badbg:#fbe4e4;--accbg:#e6eefd;--code:#eef0f4}
@media (prefers-color-scheme:dark){:root{--bg:#10131a;--fg:#e4e8f0;--mut:#98a2b5;--card:#181c26;--line:#2a3040;--acc:#6b9bff;--ok:#5fcf8b;--warn:#e8b15a;--bad:#f07a7a;--okbg:#17301f;--warnbg:#33290f;--badbg:#3a1a1a;--accbg:#1b2a4a;--code:#222838}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
header{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.bar{max-width:1100px;margin:0 auto;padding:10px 16px;display:flex;flex-wrap:wrap;gap:6px 18px;align-items:center}
.bar h1{font-size:16px;margin:0 8px 0 0}.bar nav{display:flex;flex-wrap:wrap;gap:4px}
.bar nav a{padding:4px 10px;border-radius:6px;color:var(--mut)}.bar nav a.on{background:var(--accbg);color:var(--acc);font-weight:600}
.live{margin-left:auto;font-size:12px;color:var(--mut)}.live i{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--ok);margin-right:5px}
main{max-width:1100px;margin:0 auto;padding:18px 16px 60px}
h2{font-size:15px;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);margin:26px 0 10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.tile b{display:block;font-size:26px;line-height:1.1}.tile span{color:var(--mut);font-size:13px}
.track{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0 10px}
.pill{padding:5px 12px;border-radius:999px;border:1px solid var(--line);color:var(--mut);font-size:13px}
.pill.done{background:var(--okbg);color:var(--ok);border-color:transparent}
.pill.now{background:var(--acc);color:#fff;border-color:transparent;font-weight:600}
.badge{display:inline-block;padding:1px 9px;border-radius:999px;font-size:12px;background:var(--code);color:var(--mut)}
.badge.ok{background:var(--okbg);color:var(--ok)}.badge.warn{background:var(--warnbg);color:var(--warn)}.badge.bad{background:var(--badbg);color:var(--bad)}.badge.acc{background:var(--accbg);color:var(--acc)}
.next{border-left:4px solid var(--acc)}.next.owner{border-left-color:var(--warn);background:var(--warnbg)}
.next h3{margin:0 0 4px;font-size:18px}.mut{color:var(--mut)}.small{font-size:13px}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
.scroll{overflow-x:auto}.meter{height:7px;border-radius:4px;background:var(--code);overflow:hidden;min-width:90px}.meter i{display:block;height:100%;background:var(--acc)}
.meter.over i{background:var(--bad)}ul.clean{list-style:none;padding:0;margin:0}ul.clean li{padding:3px 0}
input.filter{width:100%;padding:9px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);font:inherit;margin-bottom:10px}
.doc{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 24px 24px}
.doc h1{font-size:26px}.doc h2{text-transform:none;letter-spacing:0;font-size:20px;color:var(--fg)}.doc h3{font-size:17px}
.doc pre{background:var(--code);padding:12px;border-radius:8px;overflow-x:auto;font-size:13px}.doc code{background:var(--code);padding:1px 5px;border-radius:4px;font-size:.92em}.doc pre code{background:none;padding:0}
.doc blockquote{margin:10px 0;padding:2px 14px;border-left:3px solid var(--line);color:var(--mut)}.doc img{max-width:100%}
.doc li.task{list-style:none;margin-left:-1.2em}.fm{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0 0}.crumbs{margin:14px 0 6px;font-size:13px;color:var(--mut)}
@media (max-width:600px){.doc{padding:4px 14px 16px}main{padding:12px 10px 50px}}
"""

JS = """
(function(){var fp=null;function tick(){fetch('api/fingerprint',{cache:'no-store'}).then(r=>r.json()).then(function(d){
if(fp===null)fp=d.fingerprint;else if(d.fingerprint!==fp)location.reload();
document.getElementById('live').lastChild.nodeValue='live';}).catch(function(){document.getElementById('live').lastChild.nodeValue='offline'});}
setInterval(tick,3000);tick();
var f=document.querySelector('input.filter');if(f)f.addEventListener('input',function(){var q=f.value.toLowerCase();
document.querySelectorAll('[data-s]').forEach(function(e){e.hidden=q&&e.dataset.s.indexOf(q)<0})});})();
"""

STATUS_CLASS = {"done": "ok", "approved": "ok", "accepted": "ok", "merged": "ok", "released": "ok", "must": "bad",
                "in-progress": "acc", "in-review": "warn", "draft": "warn", "proposed": "warn", "should": "warn",
                "superseded": "", "rejected": "bad", "could": "", "wont": ""}


def badge(text, cls=None) -> str:
    text = str(text or "")
    if not text:
        return ""
    cls = STATUS_CLASS.get(text.lower().split()[0], "") if cls is None else cls
    return f'<span class="badge {cls}">{esc(text)}</span>'


class Site:
    """Routes and HTML for one or more projects."""

    def __init__(self, models: list[Model]):
        used: dict[str, int] = {}
        self.models: dict[str, Model] = {}
        for m in models:
            slug = slugify(m.root.name) or "project"
            used[slug] = used.get(slug, 0) + 1
            self.models[slug if used[slug] == 1 else f"{slug}-{used[slug]}"] = m

    # --- helpers
    def page(self, slug: str, m: Model, active: str, title: str, body: str) -> str:
        base = f"/p/{slug}/"
        tabs = [("", "Overview")]
        if isinstance(m, FullModel):
            tabs += [("requirements", "Requirements"), ("decisions", "Decisions"), ("increments", "Increments")]
        else:
            tabs += [("spec", "Spec")]
        tabs += [("docs", "Documents")]
        nav = "".join(f'<a class="{"on" if k == active else ""}" href="{base}{k}">{label}</a>' for k, label in tabs)
        back = '<a href="/">All projects</a> · ' if len(self.models) > 1 else ""
        return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                f"<title>{esc(title)} · {esc(m.name)}</title><style>{CSS}</style></head><body>"
                f'<header><div class="bar"><h1>{back}{esc(m.name)} <span class="badge">{esc(m.kind)}</span></h1><nav>{nav}</nav>'
                f'<span class="live" id="live"><i></i>live</span></div></header><main>{body}</main>'
                f'<script>{JS}</script></body></html>')

    def linker(self, slug: str, m: Model, current: str):
        base = Path(current).parent

        def link(href: str, label: str, image: bool) -> str:
            href = html.unescape(href)
            if re.match(r"^(https?:|mailto:)", href):
                return f'<a href="{esc(href)}" rel="noopener noreferrer" target="_blank">{label}</a>'
            if href.startswith("#"):
                return f'<a href="{esc(href)}">{label}</a>'
            target, _, frag = href.partition("#")
            rel = (base / unquote(target)).as_posix()
            parts: list[str] = []
            for part in rel.split("/"):
                if part == "..":
                    if parts:
                        parts.pop()
                elif part not in ("", "."):
                    parts.append(part)
            rel = "/".join(parts)
            path = safe_path(m.root, rel)
            if path is None:
                return f'<span class="mut" title="not available in the workbench">{label}</span>'
            if image:
                return f'<img alt="{label}" src="/p/{slug}/raw/{quote(rel)}">'
            if path.suffix == ".md":
                return f'<a href="/p/{slug}/doc/{quote(rel)}{"#" + esc(frag) if frag else ""}">{label}</a>'
            return f'<a href="/p/{slug}/raw/{quote(rel)}">{label}</a>'
        return link

    def doc_href(self, slug: str, rel: str) -> str:
        return f"/p/{slug}/doc/{quote(rel)}"

    # --- routing
    def route(self, path: str) -> tuple[int, str, bytes]:
        path = unquote(urlsplit(path).path)
        if path == "/":
            if len(self.models) == 1:
                return 302, "text/plain", f"/p/{next(iter(self.models))}/".encode()
            return 200, "text/html", self.index().encode()
        m = re.match(r"^/p/([^/]+)/(.*)$", path)
        if not m or m.group(1) not in self.models:
            return 404, "text/html", self.simple_page("Not found", "No such project or page.").encode()
        slug, rest = m.group(1), m.group(2)
        model = self.models[slug]
        if rest == "api/fingerprint":
            return 200, "application/json", json.dumps({"fingerprint": model.fingerprint()}).encode()
        if rest == "api/status":
            return 200, "application/json", json.dumps(self.status_json(model), indent=2, default=str).encode()
        if rest.startswith("raw/"):
            return self.raw(model, rest[4:])
        if rest.startswith("doc/"):
            return self.doc(slug, model, rest[4:])
        pages = {"": self.overview, "requirements": self.requirements, "decisions": self.decisions,
                 "increments": self.increments, "docs": self.docs_page, "spec": self.spec_page}
        if rest in pages:
            if rest in ("requirements", "decisions", "increments") and not isinstance(model, FullModel):
                return 404, "text/html", self.simple_page("Not found", "This page is for dev-process projects.").encode()
            if rest == "spec" and not isinstance(model, LiteModel):
                return 404, "text/html", self.simple_page("Not found", "This page is for dev-process-lite projects.").encode()
            return 200, "text/html", pages[rest](slug, model).encode()
        return 404, "text/html", self.simple_page("Not found", "No such page.").encode()

    def simple_page(self, title: str, msg: str) -> str:
        return (f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                f"<style>{CSS}</style><main><h1>{esc(title)}</h1><p>{esc(msg)}</p><p><a href=\"/\">Home</a></p></main>")

    def index(self) -> str:
        rows = []
        for slug, m in self.models.items():
            if isinstance(m, FullModel) and (step := m.step()):
                state = f"{step.phase} · {esc(step.action)}"
                who = badge("Owner decides" if step.actor == "owner" else "agent works", "warn" if step.actor == "owner" else "acc")
            elif isinstance(m, LiteModel):
                g = m.git_state()
                state = esc(m.stage(g)[1])
                who = ""
            else:
                state, who = "(status unavailable)", ""
            rows.append(f'<tr><td><a href="/p/{slug}/"><b>{esc(m.name)}</b></a><br><span class="mut small">{esc(str(m.root))}</span></td>'
                        f"<td>{badge(m.kind, '')}</td><td>{state} {who}</td></tr>")
        return (f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                f"<title>Workbench</title><style>{CSS}</style></head><body><header><div class=\"bar\"><h1>Workbench</h1></div></header>"
                f'<main><div class="card scroll"><table><thead><tr><th>Project</th><th>Process</th><th>Now</th></tr></thead>'
                f"<tbody>{''.join(rows)}</tbody></table></div></main></body></html>")

    def status_json(self, m: Model) -> dict:
        if isinstance(m, FullModel):
            step = m.step()
            return {"kind": m.kind, "project": m.name, "next": step.__dict__ if step else None,
                    "increments": [{k: v for k, v in i.items() if k != "outcome"} for i in m.increments()],
                    "gates": m.gates(), "requirements": parse_requirements(m.root)}
        g = m.git_state()
        return {"kind": m.kind, "project": m.name, "stage": m.stage(g)[1], "git": g, "features": m.features()}

    # --- files
    def raw(self, m: Model, rel: str) -> tuple[int, str, bytes]:
        p = safe_path(m.root, unquote(rel))
        if p is None or p.suffix.lower() not in IMAGE_EXT | {".md"}:
            return 404, "text/plain", b"Not found"
        ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        if p.suffix.lower() == ".svg":  # served as an image only; scripts in it never run in <img>, and CSP blocks direct views
            ctype = "image/svg+xml"
        return 200, ctype, p.read_bytes()

    def doc(self, slug: str, m: Model, rel: str) -> tuple[int, str, bytes]:
        rel = unquote(rel)
        p = safe_path(m.root, rel)
        if p is None or p.suffix != ".md":
            return 404, "text/html", self.simple_page("Not found", "That document is not available.").encode()
        text = read(p)
        fm, _ = split_frontmatter(text)
        chips = "".join(badge(f"{k}: {', '.join(v) if isinstance(v, list) else v}", "")
                        for k, v in fm.items() if k not in ("artefact", "owner_statement") and v)
        body = (f'<div class="crumbs"><a href="/p/{slug}/docs">Documents</a> / {esc(rel)}</div>'
                f'<div class="doc">{"<div class=fm>" + chips + "</div>" if chips else ""}'
                f"{render_markdown(text, self.linker(slug, m, rel))}</div>")
        return 200, "text/html", self.page(slug, m, "docs", title_of(text, p.stem), body).encode()

    # --- shared sections
    def docs_page(self, slug: str, m: Model) -> str:
        groups: dict[str, list[dict]] = {}
        for d in m.docs():
            parts = d["path"].split("/")
            groups.setdefault(parts[1] if len(parts) > 2 and parts[0] == "docs" else ("docs" if parts[0] == "docs" else "project"), []).append(d)
        out = ['<input class="filter" placeholder="Filter documents…" autofocus>']
        for g in sorted(groups, key=lambda x: (x != "project", x)):
            rows = "".join(
                f'<tr data-s="{esc((d["path"] + " " + d["title"]).lower())}"><td><a href="{self.doc_href(slug, d["path"])}">{esc(d["title"])}</a>'
                f'<br><span class="mut small">{esc(d["path"])}</span></td><td>{badge(d["status"])}{badge("template stub", "warn") if d["stub"] else ""}</td>'
                f'<td class="mut small">{esc(d["updated"])}</td></tr>' for d in groups[g])
            out.append(f'<h2>{esc(g)}</h2><div class="card scroll"><table><tbody>{rows}</tbody></table></div>')
        return self.page(slug, m, "docs", "Documents", "".join(out))

    # --- dev-process pages
    def overview(self, slug: str, m: Model) -> str:
        return self.full_overview(slug, m) if isinstance(m, FullModel) else self.lite_overview(slug, m)

    def full_overview(self, slug: str, m: FullModel) -> str:
        if not m.project:
            return self.page(slug, m, "", "Overview", '<div class="card">Could not read <code>.process/status.py</code> '
                             "(is PyYAML installed?). Documents are still available under Documents.</div>")
        step = m.step()
        done_gates = {g.get("gate") for g in m.gates() if g.get("decision") in ("approved", "approved-with-conditions")}
        cur = step.phase
        track = "".join(f'<span class="pill {"now" if k == cur else ""}">{k} {esc(n)}</span>' for k, n in PHASES)
        gate_pills = "".join(
            f'<span class="pill {"now" if step.gate == k else "done" if k in done_gates else ""}">{k} {esc(n)}'
            f'{" ✓" if k in done_gates and step.gate != k else ""}</span>' for k, n in GATES)
        owner = step.actor == "owner"
        who = ("Owner: decision needed" + (f" at {step.gate}" if step.gate else "")) if owner else \
            f"Agent{' · skill ' + step.skill if step.skill else ''}"
        meta = []
        if step.model_class:
            meta.append(f"model {esc(step.model_class)}" + (f" → {esc(step.model)}" if step.model else ""))
        if step.budget:
            meta.append(esc(step.budget))
        evidence = "".join(f'<li>{self._evidence_link(slug, m, e)}</li>' for e in step.evidence)
        detail = f'<div class="small">{esc(step.detail)}</div>' if step.detail else ""
        meta_html = f'<div class="mut small">{" · ".join(meta)}</div>' if meta else ""
        evidence_html = f'<ul class="clean">{evidence}</ul>' if evidence else ""
        nxt = (f'<div class="card next {"owner" if owner else ""}"><div class="mut small">NEXT · {esc(who)}</div>'
               f"<h3>{esc(step.action)}</h3>{detail}{meta_html}{evidence_html}</div>")
        reqs, incs, adrs = parse_requirements(m.root), m.increments(), m.adrs()
        by = lambda rows, key: {k: sum(1 for r in rows if r.get(key) == k) for k in sorted({r.get(key) for r in rows if r.get(key)})}  # noqa: E731
        tile = lambda n, label, sub="": f'<div class="card tile"><b>{n}</b><span>{label}</span><div class="small mut">{sub}</div></div>'  # noqa: E731
        join = lambda d: ", ".join(f"{v} {k}" for k, v in d.items())  # noqa: E731
        tiles = ('<div class="grid">' + tile(len(reqs), f'<a href="/p/{slug}/requirements">Requirements</a>', esc(join(by(reqs, "status"))))
                 + tile(len(adrs), f'<a href="/p/{slug}/decisions">Decisions (ADR)</a>', esc(join(by(adrs, "status"))))
                 + tile(len(incs), f'<a href="/p/{slug}/increments">Increments</a>', esc(join(by(incs, "status"))))
                 + tile(len(m.gates()), "Gate records", f"{len(done_gates)} of 4 gates passed") + "</div>")
        active = [i for i in incs if i["status"] in ("approved", "in-progress", "in-review", "draft")]
        act_html = "".join(self.increment_card(slug, i) for i in active) or '<div class="card mut">No increment in flight.</div>'
        return self.page(slug, m, "", "Overview",
                         f'<h2>Where we are</h2><div class="track">{track}</div><div class="track">{gate_pills}</div>{nxt}'
                         f"{tiles}<h2>In flight</h2>{act_html}<h2>Core documents</h2>{self.core_docs(slug, m)}"
                         f'<h2>Recent gate decisions</h2>{self.gate_table(slug, m, 6)}')

    def _evidence_link(self, slug: str, m: Model, rel: str) -> str:
        return f'<a href="{self.doc_href(slug, rel)}">{esc(rel)}</a>' if safe_path(m.root, rel) else esc(rel)

    def core_docs(self, slug: str, m: FullModel) -> str:
        wanted = [("docs/brief.md", "Brief"), ("docs/architecture.md", "Architecture"), ("docs/standards.md", "Standards"),
                  ("docs/test-strategy.md", "Test strategy"), ("docs/ops/runbook.md", "Runbook"), ("docs/user/index.md", "User docs"),
                  ("docs/risk-register.md", "Risk register"), ("CHANGELOG.md", "Changelog")]
        rows = []
        for rel, label in wanted:
            p = m.root / rel
            if not p.is_file():
                rows.append(f"<tr><td>{label}</td><td>{badge('missing', 'warn')}</td><td></td></tr>")
                continue
            d = _doc_row(m.root, p)
            rows.append(f'<tr><td><a href="{self.doc_href(slug, rel)}">{label}</a></td>'
                        f'<td>{badge(d["status"])}{badge("template stub", "warn") if d["stub"] else ""}</td><td class="mut small">{esc(d["updated"])}</td></tr>')
        return f'<div class="card scroll"><table><tbody>{"".join(rows)}</tbody></table></div>'

    def gate_table(self, slug: str, m: FullModel, limit: int | None = None) -> str:
        gates = sorted(m.gates(), key=lambda g: str(g.get("updated", "")), reverse=True)[:limit]
        if not gates:
            return '<div class="card mut">No gate decisions recorded yet.</div>'
        rows = "".join(
            f'<tr><td><a href="{self.doc_href(slug, g["path"])}">{esc(g.get("gate", ""))}</a> {esc(g.get("increment") or g.get("release") or "")}</td>'
            f'<td>{badge(g.get("decision"))}</td><td class="small">{esc(g.get("owner_statement", ""))}</td><td class="mut small">{esc(g.get("updated", ""))}</td></tr>'
            for g in gates)
        return f'<div class="card scroll"><table><tbody>{rows}</tbody></table></div>'

    def increment_card(self, slug: str, i: dict) -> str:
        done = sum(1 for d, _, _ in i["slices"] if d)
        total = len(i["slices"])
        meter = f'<div class="meter" title="{done}/{total} slices"><i style="width:{100 * done // total}%"></i></div>' if total else ""
        bud = ""
        if i["budget"]:
            spent, limit, label = i["budget"]
            over = " over" if spent >= limit else ""
            bud = (f'<div class="small mut">Budget: {spent} of {limit} agent steps{esc(label)}</div>'
                   f'<div class="meter{over}"><i style="width:{min(100, 100 * spent // max(limit, 1))}%"></i></div>')
        slices = "".join(f'<li class="task">{"&#9745;" if d else "&#9744;"} {esc(s)} {esc(t)}</li>' for d, s, t in i["slices"])
        outcome = esc(i["outcome"][:300] + ("…" if len(i["outcome"]) > 300 else ""))
        heading = esc(re.sub(r"^INC-\d+:\s*", "", i["title"]))
        slice_html = f'<details><summary class="small">Slices</summary><ul class="clean">{slices}</ul></details>' if slices else ""
        return (f'<div class="card"><div><a href="{self.doc_href(slug, i["path"])}"><b>{esc(i["id"])}</b> {heading}</a> '
                f'{badge(i["status"])} {badge(i["tier"], "")}</div><p class="small">{outcome}</p>{meter}'
                f'<div class="small mut">{done} of {total} slices</div>{bud}{slice_html}</div>')

    def requirements(self, slug: str, m: FullModel) -> str:
        reqs = parse_requirements(m.root)
        covered: dict[str, list[str]] = {}
        for inc in m.increments():
            for r in inc["reqs"]:
                covered.setdefault(r, []).append(inc["id"])
        if not reqs:
            return self.page(slug, m, "requirements", "Requirements", '<div class="card mut">No requirements written yet (docs/requirements/).</div>')
        has_impl = any(r["impl"] for r in reqs)
        rows = "".join(
            f'<tr data-s="{esc((r["id"] + " " + r["title"] + " " + r["status"]).lower())}"><td><a href="{self.doc_href(slug, r["file"])}#{r["id"].lower()}"><b>{esc(r["id"])}</b></a></td>'
            f'<td>{esc(r["title"])}</td><td>{badge(r["priority"])}</td><td>{badge(r["status"])}</td>'
            + (f'<td>{badge(r["impl"])}</td>' if has_impl else "")
            + f'<td class="small">{esc(", ".join(covered.get(r["id"], [])) or "–")}</td></tr>' for r in reqs)
        impl_head = "<th>Implementation</th>" if has_impl else ""
        return self.page(slug, m, "requirements", "Requirements",
                         '<input class="filter" placeholder="Filter requirements…"><div class="card scroll"><table><thead><tr><th>ID</th><th>Requirement</th>'
                         f"<th>Priority</th><th>Status</th>{impl_head}<th>In increment</th></tr></thead><tbody>{rows}</tbody></table></div>")

    def decisions(self, slug: str, m: FullModel) -> str:
        adrs = m.adrs()
        if not adrs:
            return self.page(slug, m, "decisions", "Decisions", '<div class="card mut">No ADRs yet (docs/adr/).</div>')
        rows = "".join(
            f'<tr data-s="{esc((d["title"] + " " + d["status"]).lower())}"><td><a href="{self.doc_href(slug, d["path"])}">{esc(d["title"])}</a></td>'
            f'<td>{badge(d["status"])}</td><td class="mut small">{esc(d["updated"])}</td></tr>' for d in adrs)
        return self.page(slug, m, "decisions", "Decisions",
                         f'<input class="filter" placeholder="Filter decisions…"><div class="card scroll"><table><thead><tr><th>Architecture decision</th><th>Status</th><th>Updated</th></tr></thead><tbody>{rows}</tbody></table></div>')

    def increments(self, slug: str, m: FullModel) -> str:
        incs = m.increments()
        order = {"in-progress": 0, "approved": 1, "in-review": 2, "draft": 3, "done": 4}
        incs.sort(key=lambda i: (order.get(i["status"], 5), i["id"]))
        body = "".join(self.increment_card(slug, i) for i in incs) or '<div class="card mut">No increments yet.</div>'
        return self.page(slug, m, "increments", "Increments", body + "<h2>Gate decisions</h2>" + self.gate_table(slug, m))

    # --- dev-process-lite pages
    def lite_overview(self, slug: str, m: LiteModel) -> str:
        g = m.git_state()
        idx, why = m.stage(g)
        track = "".join(f'<span class="pill {"now" if n == idx else "done" if n < idx else ""}">{s}</span>' for n, s in enumerate(LITE_STAGES))
        feats = m.features()
        spec_stub = has_placeholders(read(m.root / "docs" / "spec.md")) or not (m.root / "docs" / "spec.md").is_file()
        readme_stub = has_placeholders(read(m.root / "README.md")) or not (m.root / "README.md").is_file()
        tile = lambda n, label, sub="": f'<div class="card tile"><b>{n}</b><span>{label}</span><div class="small mut">{sub}</div></div>'  # noqa: E731
        tiles = ('<div class="grid">' + tile(len(feats), f'<a href="/p/{slug}/spec">Features in spec</a>', "template stub" if spec_stub else "documented")
                 + tile(len(g.get("branches", [])), "Branches awaiting merge", "")
                 + tile(g.get("dirty", 0), "Uncommitted changes", f'on {esc(g.get("branch", "?"))}')
                 + tile(esc(g.get("tag") or "–"), "Latest tag", f"process v{esc(m.version)}") + "</div>")
        branches = "".join(f'<tr><td><b>{esc(b["name"])}</b></td><td>{b["ahead"]} commit(s)</td><td>{esc(b["last"])}</td><td class="mut small">{esc(b["when"])}</td></tr>'
                           for b in g.get("branches", [])) or '<tr><td class="mut">Nothing waiting.</td></tr>'
        log = "".join(f'<tr><td><code>{esc(c["hash"])}</code></td><td class="mut small">{esc(c["date"])}</td><td>{esc(c["subject"])}</td></tr>' for c in g.get("log", []))
        health = (f'<div class="card"><ul class="clean"><li>docs/spec.md {badge("template stub", "warn") if spec_stub else badge("filled in", "ok")}'
                  f'</li><li>README.md {badge("template stub", "warn") if readme_stub else badge("filled in", "ok")}</li></ul></div>')
        return self.page(slug, m, "", "Overview",
                         f'<h2>Where we are</h2><div class="track">{track}</div><div class="card next"><h3>{esc(why)}</h3>'
                         f'<div class="mut small">Inferred from git: branch {esc(g.get("branch", "?"))}. Lite has no gates; the Owner merging is the release.</div></div>'
                         f'{tiles}<h2>Docs health</h2>{health}<h2>Branches ahead of {esc(g.get("base", "main"))}</h2><div class="card scroll"><table><tbody>{branches}</tbody></table></div>'
                         f'<h2>Recent changes on {esc(g.get("base", "main"))}</h2><div class="card scroll"><table><tbody>{log}</tbody></table></div>')

    def spec_page(self, slug: str, m: LiteModel) -> str:
        feats = m.features()
        frows = "".join(f'<tr data-s="{esc((i + " " + t).lower())}"><td><a href="{self.doc_href(slug, "docs/spec.md")}#{i.lower()}"><b>{i}</b></a></td><td>{esc(t)}</td></tr>'
                        for i, t in feats if t and not has_placeholders(t)) or '<tr><td class="mut">No features written yet.</td></tr>'
        def outline(rel, label):
            items = "".join(f'<li>{badge("ok", "ok") if ok else badge("empty", "warn")} {esc(name)}</li>' for name, ok in m.outline(rel))
            link = f'<a href="{self.doc_href(slug, rel)}">{label}</a>' if (m.root / rel).is_file() else label + " (missing)"
            return f'<div class="card"><b>{link}</b><ul class="clean">{items}</ul></div>'
        return self.page(slug, m, "spec", "Spec",
                         f'<input class="filter" placeholder="Filter features…"><div class="card scroll"><table><thead><tr><th>ID</th><th>Feature</th></tr></thead><tbody>{frows}</tbody></table></div>'
                         f'<h2>Sections</h2><div class="grid">{outline("docs/spec.md", "Spec")}{outline("README.md", "README")}</div>')


def safe_path(root: Path, rel: str) -> Path | None:
    """A file inside the project that the workbench may serve, else None."""
    if not rel or "\x00" in rel:
        return None
    try:
        base = root.resolve()
        p = (base / rel).resolve()
        parts = p.relative_to(base).parts
    except (ValueError, OSError):
        return None
    if not p.is_file() or any(part.startswith(".") for part in parts) or SECRET_NAME.search(p.name):
        return None
    if p.suffix.lower() not in IMAGE_EXT | {".md"}:
        return None
    return p


# ------------------------------------------------------------------ server

def make_handler(site: Site):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            try:
                code, ctype, body = site.route(self.path)
            except Exception as exc:  # never crash the server on one bad page
                code, ctype, body = 500, "text/html", site.simple_page("Error", f"{type(exc).__name__}: {exc}").encode()
            self.send_response(code)
            if code == 302:
                self.send_header("Location", body.decode())
                body = b""
            else:
                self.send_header("Content-Type", f"{ctype}; charset=utf-8" if ctype.startswith(("text", "application/json")) else ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
                                                        "img-src 'self' data:; connect-src 'self'")
            self.end_headers()
            self.wfile.write(body)

        def _refuse(self):
            self.send_error(405, "The workbench is read-only")

        do_POST = do_PUT = do_DELETE = do_PATCH = _refuse  # noqa: N815

        def log_message(self, fmt, *args):  # quiet: one line per page, not per poll
            if "fingerprint" not in str(args[0] if args else ""):
                sys.stderr.write(f"{self.address_string()} {fmt % args}\n")
    return Handler


def lan_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))  # no packet is sent; picks the outgoing interface
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def find_projects(args) -> list[Model]:
    roots = [Path(p).resolve() for p in args.project]
    for r in args.root:
        base = Path(r).resolve()
        roots += sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not args.project and not args.root:
        roots = [Path.cwd()]
    models, seen = [], set()
    for r in roots:
        if r in seen:
            continue
        seen.add(r)
        if m := detect(r):
            models.append(m)
        elif args.project or not args.root:
            print(f"Not a dev-process or dev-process-lite project: {r}", file=sys.stderr)
    return models


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Live, read-only web view of a project's process state.")
    ap.add_argument("--project", action="append", default=[], help="a project folder (repeatable; default: current folder)")
    ap.add_argument("--root", action="append", default=[], help="a folder whose sub-folders are scanned for projects")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default=None, help="address to bind (default 127.0.0.1)")
    ap.add_argument("--lan", action="store_true", help="listen on all interfaces so other devices on the local network can connect")
    args = ap.parse_args(argv)

    models = find_projects(args)
    if not models:
        print("No projects found. Run it inside a project, or pass --project / --root.", file=sys.stderr)
        return 1
    host = args.host or ("0.0.0.0" if args.lan else "127.0.0.1")
    try:
        server = ThreadingHTTPServer((host, args.port), make_handler(Site(models)))
    except OSError as exc:
        print(f"Cannot listen on {host}:{args.port}: {exc}. Try --port.", file=sys.stderr)
        return 1
    print(f"Workbench for: {', '.join(m.name for m in models)}")
    print(f"  This computer:  http://127.0.0.1:{args.port}/")
    if host == "0.0.0.0":
        print(f"  On the network: http://{lan_ip()}:{args.port}/   (no login: trusted networks only)")
        print("  If other devices cannot connect, allow this port in Windows Defender Firewall (private networks).")
    elif host != "127.0.0.1":
        print(f"  Listening on:   http://{host}:{args.port}/   (no login: trusted networks only)")
    print("Read-only. Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

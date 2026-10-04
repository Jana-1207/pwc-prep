#!/usr/bin/env python3
"""
Build the PwC Modern Data Systems Interview Handbook (PDF).

    content/*.md --> custom pre-processing --> Markdown --> HTML --> WeasyPrint --> PDF

Custom syntax (on top of normal Markdown)
-----------------------------------------
::: kind Optional title           A styled box. Kinds: explain, trap, tip, pwc, extension,
...markdown...                    prereq, analogy, remember, note, project, coverage,
:::                               practice, answers, questions, summary, checklist,
                                  example, concept, source, compare. Boxes can nest.

Q: question text                  An interview question with its model answer. The answer
A: answer text                    runs until the next "Q:", a heading, or a box fence.

```sql run [keep] [quiet] [error] [plan] [all] [max=N] [label="..."]
Runs the block against the sample PostgreSQL database (sql/sample_db.sql) and prints the
real output under the code.  Without "keep" the block is rolled back afterwards, so every
example sees the same data.  "error" means the block is expected to fail (the PostgreSQL
error is shown).  A run block that fails unexpectedly stops the build.

[[fig:name | Caption | width]]    Inserts diagrams/svg/name.svg as a numbered figure.

[DEFINITION] [WHY] [SCENARIO] ... Coloured label pills (see LABELS).
- [ ] item                        Checklist item with an empty tick box.

Usage
-----
    python3 build.py              # full build (needs PostgreSQL, see scripts/start_postgres.sh)
    python3 build.py --html-only  # stop after writing build/handbook.html
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown
import psycopg
from bs4 import BeautifulSoup
from psycopg.adapt import Loader
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name

ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
SVG_DIR = ROOT / "diagrams" / "svg"
SEED_SQL = ROOT / "sql" / "sample_db.sql"
BUILD_DIR = ROOT / "build"
FONT_DIR = ROOT / "fonts"
OUT_PDF = ROOT.parent / "PwC_Modern_Data_Systems_Interview_Handbook.pdf"
DSN = os.environ.get("HANDBOOK_PG_DSN", "host=localhost port=54329 user=postgres dbname=handbook")

MD_EXTENSIONS = ["extra", "sane_lists"]

BOX_TITLES = {
    "explain": "How I Would Explain This in an Interview",
    "trap": "Common Traps & Mistakes",
    "tip": "Interview Tip",
    "pwc": "PwC Interview Angle",
    "extension": "Interview Extension",
    "prereq": "Recommended Prerequisite",
    "analogy": "Simple Analogy",
    "remember": "Remember This",
    "note": "Note",
    "project": "Project Connection",
    "coverage": "Course Coverage",
    "practice": "Practice Questions",
    "answers": "Answer / Explanation",
    "questions": "Interview Questions",
    "summary": "Module Summary",
    "checklist": "Rapid Revision Checklist",
    "example": "Worked Example",
    "concept": "Concept at a Glance",
    "source": "Sources",
    "compare": "Comparison",
    "pattern": "Interview Pattern",
    "linebyline": "Line by Line",
    "plain": "",
    "covmap": "",
}

LABELS = [
    "DEFINITION", "WHY", "HOW", "COMPARISON", "SCENARIO", "SQL PROBLEM",
    "DESIGN QUESTION", "TRAP QUESTION", "EASY", "MEDIUM", "HARD",
    "HIGH PRIORITY", "MEDIUM PRIORITY", "LOWER PRIORITY", "INTERVIEW EXTENSION",
    "COURSE", "MUST KNOW", "REPORTED", "LIKELY", "RECOMMENDED", "GENERAL",
    "PROJECT", "BEHAVIOURAL", "CODING",
]
LABEL_RE = re.compile(r"\[(" + "|".join(re.escape(l) for l in LABELS) + r")\]")

LANG_LABELS = {
    "sql": "SQL · PostgreSQL",
    "javascript": "MongoDB Shell (mongosh)",
    "js": "JavaScript",
    "json": "JSON",
    "http": "HTTP",
    "bash": "Shell",
    "sh": "Shell",
    "python": "Python",
    "java": "Java",
    "text": "",
    "yaml": "YAML",
    "xml": "XML",
    "csv": "CSV",
}

NUMERIC_OIDS = {20, 21, 23, 26, 700, 701, 1700}
BOOL_OID = 16


class BuildError(Exception):
    pass


# ---------------------------------------------------------------------------
# PostgreSQL runner
# ---------------------------------------------------------------------------
class _AsText(Loader):
    """Load every value as the exact text PostgreSQL prints (like psql does)."""

    def load(self, data):
        return bytes(data).decode("utf-8")


TEXT_TYPES = [
    "bool", "int2", "int4", "int8", "numeric", "float4", "float8", "oid",
    "date", "time", "timetz", "timestamp", "timestamptz", "interval",
    "json", "jsonb", "uuid", "text", "varchar", "bpchar", "name", "char",
    "_bool", "_int2", "_int4", "_int8", "_numeric", "_text", "_varchar",
    "_date", "_timestamp", "_float8",
]


class SqlRunner:
    def __init__(self, dsn: str, seed: str):
        self.dsn = dsn
        self.seed = seed
        self.conn = None
        self.kept: list[str] = []
        self.blocks_run = 0

    def _connect(self):
        if self.conn is not None:
            self.conn.close()
        self.conn = psycopg.connect(self.dsn, autocommit=True)
        for t in TEXT_TYPES:
            try:
                self.conn.adapters.register_loader(t, _AsText)
            except Exception:  # type not present on this server
                pass

    def reset(self, replay_kept: bool = False):
        self._connect()
        with self.conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;")
            cur.execute(self.seed)
            if replay_kept:
                for sql in self.kept:
                    cur.execute(sql)
            else:
                self.kept = []
        self.conn.autocommit = False

    @staticmethod
    def _collect(cur):
        results = []
        while True:
            if cur.description:
                cols = [(d.name, d.type_code) for d in cur.description]
                results.append((cur.statusmessage, cols, cur.fetchall()))
            else:
                results.append((cur.statusmessage, None, None))
            if not cur.nextset():
                break
        return results

    def run(self, sql: str, keep: bool, expect_error: bool):
        self.blocks_run += 1
        explicit_tx = re.search(r"^\s*(BEGIN|COMMIT|ROLLBACK|START\s+TRANSACTION|SAVEPOINT)\b",
                                sql, re.I | re.M) is not None
        if explicit_tx:
            # Let the block's own BEGIN/COMMIT/ROLLBACK work exactly as written.
            self.conn.autocommit = True
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            results = self._collect(cur)
            error = None
        except psycopg.Error as exc:
            results, error = None, exc
        finally:
            cur.close()

        if explicit_tx:
            if keep and error is None:
                self.kept.append(sql)
            self.reset(replay_kept=True)       # restore a clean state
        else:
            if error is None and keep:
                self.conn.commit()
                self.kept.append(sql)
            else:
                self.conn.rollback()

        if error is not None and not expect_error:
            raise BuildError(f"SQL block failed: {error}\n----\n{sql}\n----")
        if error is None and expect_error:
            raise BuildError(f"SQL block was expected to fail but succeeded:\n{sql}")
        return results, error


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
class Renderer:
    def __init__(self, runner: SqlRunner | None):
        self.runner = runner
        self.stash: dict[str, str] = {}
        self.counter = 0
        self.fig_no = 0
        self.formatter = HtmlFormatter(nowrap=True)
        self.formatter_ln = HtmlFormatter(linenos="inline", wrapcode=False)

    # -- placeholders -------------------------------------------------------
    def put(self, html_text: str) -> str:
        self.counter += 1
        key = f"ZZBLOCK{self.counter}ZZ"
        self.stash[key] = html_text
        return key

    def resolve(self, text: str) -> str:
        pat = re.compile(r"<p>\s*(ZZBLOCK\d+ZZ)\s*</p>|(ZZBLOCK\d+ZZ)")
        for _ in range(30):
            if "ZZBLOCK" not in text:
                return text
            text = pat.sub(lambda m: self.stash[m.group(1) or m.group(2)], text)
        raise BuildError("placeholder resolution did not converge")

    # -- code ---------------------------------------------------------------
    def code_block(self, lang: str, opts: str, code: str) -> str:
        lang = (lang or "text").lower()
        options = parse_opts(opts)
        try:
            lexer = get_lexer_by_name(lang) if lang not in ("text", "csv") else TextLexer()
        except Exception:
            lexer = TextLexer()
        if "lines" in options:
            out = highlight(code, lexer, self.formatter_ln)
            m = re.search(r"<pre[^>]*>(.*)</pre>", out, re.S)
            body = m.group(1) if m else html.escape(code)
        else:
            body = highlight(code, lexer, self.formatter)
        label = options.get("label", LANG_LABELS.get(lang, lang.upper()))
        label_html = f'<div class="codelabel">{html.escape(label)}</div>' if label else ""
        title = options.get("title")
        title_html = f'<div class="codetitle">{html.escape(title)}</div>' if title else ""
        out_html = f'<div class="codeblock lang-{lang}">{title_html}{label_html}<pre class="code">{body.rstrip()}</pre></div>'

        if lang == "sql" and "run" in options:
            if self.runner is None:
                raise BuildError("SQL run block found but no database runner configured")
            results, error = self.runner.run(code, keep="keep" in options,
                                             expect_error="error" in options)
            out_html += self.sql_output(results, error, options)
        # long blocks may break across pages; short ones are kept in one piece
        n_lines = code.count("\n") + 1 + out_html.count("<tr>")
        cls = "codegroup long" if n_lines > 26 else "codegroup"
        return f'<div class="{cls}">{out_html}</div>'

    def sql_output(self, results, error, options) -> str:
        if error is not None:
            d = error.diag
            parts = [f'<span class="err-label">{html.escape(d.severity or "ERROR")}</span> '
                     f'{html.escape(d.message_primary or str(error))}']
            if d.message_detail:
                parts.append(f'<div class="err-extra">DETAIL: {html.escape(d.message_detail)}</div>')
            if d.message_hint:
                parts.append(f'<div class="err-extra">HINT: {html.escape(d.message_hint)}</div>')
            return f'<div class="sql-error"><div class="out-head">PostgreSQL says</div>{"".join(parts)}</div>'
        if "quiet" in options:
            return ""
        with_rows = [r for r in results if r[1] is not None]
        if "plan" in options:
            status, cols, rows = with_rows[-1]
            text = "\n".join(r[0] for r in rows)
            return (f'<div class="sql-output plan"><div class="out-head">Query plan (EXPLAIN)</div>'
                    f'<pre class="plan">{html.escape(text)}</pre></div>')
        if not with_rows:
            status = results[-1][0] if results else ""
            return (f'<div class="sql-output status"><span class="out-head">Result</span> '
                    f'<code>{html.escape(status or "OK")}</code></div>')
        shown = with_rows if "all" in options else [with_rows[-1]]
        max_rows = int(options.get("max", 25))
        tables = []
        for status, cols, rows in shown:
            head = "".join(f"<th>{html.escape(c[0])}</th>" for c in cols)
            body = []
            for row in rows[:max_rows]:
                cells = []
                for (name, oid), v in zip(cols, row):
                    cls = ' class="num"' if oid in NUMERIC_OIDS else ""
                    if v is None:
                        cells.append(f'<td{cls}><span class="null">NULL</span></td>')
                    else:
                        if oid == BOOL_OID:
                            v = {"t": "true", "f": "false"}.get(v, v)
                        cells.append(f"<td{cls}>{html.escape(str(v))}</td>")
                body.append("<tr>" + "".join(cells) + "</tr>")
            n = len(rows)
            more = f" · first {max_rows} shown" if n > max_rows else ""
            foot = f'{n} row{"s" if n != 1 else ""}{more}'
            tcls = "result wide7" if len(cols) >= 7 else ("result wide5" if len(cols) >= 5 else "result")
            tables.append(f'<table class="{tcls}"><thead><tr>{head}</tr></thead>'
                          f'<tbody>{"".join(body)}</tbody></table><div class="out-foot">{foot}</div>')
        return f'<div class="sql-output"><div class="out-head">Output</div>{"".join(tables)}</div>'

    # -- figures ------------------------------------------------------------
    def figure(self, name: str, caption: str, width: str | None) -> str:
        path = SVG_DIR / f"{name}.svg"
        if not path.exists():
            raise BuildError(f"diagram not found: {path}")
        svg = path.read_text(encoding="utf-8")
        svg = re.sub(r"<\?xml[^>]*\?>", "", svg).strip()
        self.fig_no += 1
        style = f' style="width:{width}"' if width else ""
        cap = md_inline(caption)
        # the number is filled in later, in document order (boxes are rendered before their surroundings)
        return (f'<figure class="diagram"><div class="svgwrap"{style}>{svg}</div>'
                f'<figcaption><span class="fignum">Figure FIGNUM.</span> {cap}</figcaption></figure>')

    # -- main entry -----------------------------------------------------------
    def render(self, text: str) -> str:
        text = self.extract_code(text)
        return self.resolve(self.render_inner(text))

    def render_inner(self, text: str) -> str:
        """Render text whose code blocks are already replaced by placeholders."""
        text = self.extract_boxes(text)
        text = self.extract_qa(text)
        text = self.extract_figures(text)
        text = LABEL_RE.sub(lambda m: label_html(m.group(1)), text)
        out = markdown.markdown(text, extensions=MD_EXTENSIONS, output_format="html")
        return out

    # -- passes ---------------------------------------------------------------
    def extract_code(self, text: str) -> str:
        lines = text.split("\n")
        out, i = [], 0
        fence_re = re.compile(r"^(\s*)```\s*([\w+-]*)\s*(.*)$")
        while i < len(lines):
            m = fence_re.match(lines[i])
            if not m:
                out.append(lines[i])
                i += 1
                continue
            indent, lang, opts = m.group(1), m.group(2), m.group(3)
            j = i + 1
            body = []
            while j < len(lines) and not re.match(r"^\s*```\s*$", lines[j]):
                ln = lines[j]
                body.append(ln[len(indent):] if ln.startswith(indent) else ln.lstrip())
                j += 1
            if j >= len(lines):
                raise BuildError(f"unclosed code fence starting: {lines[i]!r}")
            key = self.put(self.code_block(lang, opts, "\n".join(body)))
            out.extend(["", indent + key, ""])
            i = j + 1
        return "\n".join(out)

    def extract_boxes(self, text: str) -> str:
        lines = text.split("\n")
        out, i = [], 0
        open_re = re.compile(r"^:::\s*([\w-]+)\s*(.*)$")
        while i < len(lines):
            m = open_re.match(lines[i])
            if not m:
                out.append(lines[i])
                i += 1
                continue
            kind, title = m.group(1), m.group(2).strip()
            depth, j, inner = 1, i + 1, []
            while j < len(lines):
                if open_re.match(lines[j]):
                    depth += 1
                elif re.match(r"^:::\s*$", lines[j]):
                    depth -= 1
                    if depth == 0:
                        break
                inner.append(lines[j])
                j += 1
            if depth != 0:
                raise BuildError(f"unclosed box ::: {kind} {title}")
            body = self.render_inner("\n".join(inner))
            if title == "-":
                title = ""
            elif not title:
                title = BOX_TITLES.get(kind, kind.title())
            title_html = f'<div class="box-title">{md_inline(title)}</div>' if title else ""
            out.extend(["", self.put(f'<div class="box box-{kind}">{title_html}<div class="box-body">{body}</div></div>'), ""])
            i = j + 1
        return "\n".join(out)

    def extract_qa(self, text: str) -> str:
        lines = text.split("\n")
        out, i = [], 0
        stop_re = re.compile(r"^(Q:|#{1,6}\s|:::)")
        while i < len(lines):
            if not lines[i].startswith("Q:"):
                out.append(lines[i])
                i += 1
                continue
            q = [lines[i][2:].strip()]
            j = i + 1
            while j < len(lines) and not lines[j].startswith("A:") and not stop_re.match(lines[j]):
                q.append(lines[j])
                j += 1
            a = []
            if j < len(lines) and lines[j].startswith("A:"):
                a.append(lines[j][2:].strip())
                j += 1
                while j < len(lines) and not stop_re.match(lines[j]):
                    a.append(lines[j])
                    j += 1
            qhtml = markdown.markdown("\n".join(q).strip(), extensions=MD_EXTENSIONS)
            ahtml = markdown.markdown("\n".join(a).strip(), extensions=MD_EXTENSIONS) if a else ""
            block = (f'<div class="qa"><div class="q"><span class="qmark"></span>'
                     f'<div class="qtext">{qhtml}</div></div>')
            if ahtml:
                block += f'<div class="a"><span class="amark">A</span><div class="atext">{ahtml}</div></div>'
            block += "</div>"
            out.extend(["", self.put(LABEL_RE.sub(lambda m: label_html(m.group(1)), block)), ""])
            i = j
        return "\n".join(out)

    def extract_figures(self, text: str) -> str:
        def repl(m):
            parts = [p.strip() for p in m.group(1).split("|")]
            name = parts[0]
            caption = parts[1] if len(parts) > 1 else ""
            width = parts[2] if len(parts) > 2 else None
            return "\n\n" + self.put(self.figure(name, caption, width)) + "\n\n"
        return re.sub(r"^\[\[fig:(.+?)\]\]\s*$", repl, text, flags=re.M)


def label_html(label: str) -> str:
    cls = re.sub(r"[^a-z]+", "-", label.lower()).strip("-")
    return f'<span class="tag tag-{cls}">{label}</span>'


def md_inline(text: str) -> str:
    out = markdown.markdown(text, extensions=MD_EXTENSIONS)
    return re.sub(r"^<p>(.*)</p>$", r"\1", out.strip(), flags=re.S)


def parse_opts(opts: str) -> dict:
    result = {}
    for m in re.finditer(r'(\w+)(?:=("([^"]*)"|\S+))?', opts or ""):
        key = m.group(1)
        if m.group(2) is None:
            result[key] = True
        else:
            result[key] = m.group(3) if m.group(3) is not None else m.group(2)
    return result


# ---------------------------------------------------------------------------
# Document assembly
# ---------------------------------------------------------------------------
def postprocess(soup: BeautifulSoup):
    # checklist items
    for li in soup.find_all("li"):
        first = li.contents[0] if li.contents else None
        target = li
        if first is not None and getattr(first, "name", None) == "p":
            target = first
            first = first.contents[0] if first.contents else None
        if isinstance(first, str) and re.match(r"^\[( |x)\]\s", first):
            done = first.startswith("[x]")
            first.replace_with(first[4:])
            li["class"] = li.get("class", []) + ["todo"]
            box = soup.new_tag("span", attrs={"class": "cb" + (" done" if done else "")})
            target.insert(0, box)

    # a short lead-in paragraph ("P3.", "Now try this:") stays on the same page as its code block
    for cg in soup.find_all("div", class_="codegroup"):
        prev = cg.find_previous_sibling()
        if prev is not None and prev.name in ("p", "h4", "h5") and len(prev.get_text()) < 400:
            prev["class"] = (prev.get("class") or []) + ["keepwith"]

    # number headings and build ids
    n = 0
    for h in soup.find_all(["h1", "h2", "h3"]):
        n += 1
        if not h.get("id"):
            h["id"] = f"sec-{n}"

    # tables written with an empty Markdown header row (| | |) render without a header
    for thead in soup.find_all("thead"):
        if all(not th.get_text(strip=True) for th in thead.find_all("th")):
            thead.decompose()

    # wide tables get a class so CSS can shrink the font
    for t in soup.find_all("table"):
        if "result" in (t.get("class") or []):
            continue
        cols = len(t.find("tr").find_all(["th", "td"])) if t.find("tr") else 0
        if cols >= 5:
            t["class"] = (t.get("class") or []) + ["wide"]


def build_toc(soup: BeautifulSoup) -> str:
    items = []
    for h in soup.find_all(["h1", "h2", "h3"]):
        classes = h.get("class") or []
        if "notoc" in classes:
            continue
        if h.name == "h3" and "intoc" not in classes:
            continue
        label = h.get("data-label")
        text = h.get_text(" ", strip=True)
        level = {"h1": 1, "h2": 2, "h3": 3}[h.name]
        prefix = f'<span class="toc-label">{html.escape(label)}</span>' if label and level == 1 else ""
        items.append(f'<li class="toc-l{level}"><a href="#{h["id"]}">{prefix}'
                     f'<span class="toc-text">{html.escape(text)}</span></a></li>')
    return "<ul class=\"toc-list\">" + "\n".join(items) + "</ul>"


def check_javascript(files) -> int:
    """Syntax-check every ```javascript (mongosh) block with Node, if Node is installed.

    MongoDB examples cannot be executed here, but they can at least be parsed.
    Shell helpers such as `use shop` are commented out first; a bare document is
    checked as an expression."""
    node = shutil.which("node")
    if node is None:
        print("node not found: skipping MongoDB shell syntax check")
        return 0
    checked = 0
    work = BUILD_DIR / "jscheck"
    work.mkdir(parents=True, exist_ok=True)
    for f in files:
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r"^(\s*)```javascript\s*\n(.*?)^\s*```\s*$", text, re.S | re.M):
            indent = m.group(1)
            lines = [l[len(indent):] if l.startswith(indent) else l for l in m.group(2).split("\n")]
            lines = [("// " + l) if re.match(r"^\s*(use|show)\s+\w+", l) else l for l in lines]
            body = "\n".join(lines)
            src = f"async function _check(db, ISODate, ObjectId) {{\n{body}\n}}\n"
            if body.strip().startswith("{") and "db." not in body:
                src = f"const _doc = (\n{body}\n);\n"
            checked += 1
            js = work / f"block_{checked:03d}.js"
            js.write_text(src, encoding="utf-8")
            res = subprocess.run([node, "--check", str(js)], capture_output=True, text=True)
            if res.returncode != 0:
                raise BuildError(f"[{f.name}] MongoDB shell block has a syntax error:\n{body}\n{res.stderr}")
    return checked


def check_python(files) -> int:
    """Compile every ```python block (syntax only; the examples are not executed)."""
    checked = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r"^(\s*)```python\s*\n(.*?)^\s*```\s*$", text, re.S | re.M):
            indent = m.group(1)
            body = "\n".join(l[len(indent):] if l.startswith(indent) else l
                             for l in m.group(2).split("\n"))
            try:
                compile(body, f"{f.name}:python-block", "exec")
            except SyntaxError as exc:
                raise BuildError(f"[{f.name}] Python block has a syntax error: {exc}\n{body}")
            checked += 1
    return checked


def ensure_fonts():
    """Make the bundled fonts visible to fontconfig (used for SVG text)."""
    target = Path.home() / ".local" / "share" / "fonts" / "handbook"
    target.mkdir(parents=True, exist_ok=True)
    changed = False
    for f in FONT_DIR.glob("*.ttf"):
        dest = target / f.name
        if not dest.exists():
            shutil.copy(f, dest)
            changed = True
    if changed:
        subprocess.run(["fc-cache", "-f", str(target)], check=False, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html-only", action="store_true")
    ap.add_argument("--no-sql", action="store_true", help="do not execute SQL blocks (draft mode)")
    args = ap.parse_args()

    ensure_fonts()
    BUILD_DIR.mkdir(exist_ok=True)

    runner = None
    if not args.no_sql:
        runner = SqlRunner(DSN, SEED_SQL.read_text(encoding="utf-8"))

    renderer = Renderer(runner)
    files = sorted(CONTENT_DIR.glob("*.md"))
    try:
        js_checked = check_javascript(files)
    except BuildError as exc:
        sys.exit(str(exc))
    print(f"syntax-checked {js_checked} MongoDB shell blocks")
    try:
        py_checked = check_python(files)
    except BuildError as exc:
        sys.exit(str(exc))
    print(f"syntax-checked {py_checked} Python blocks")
    parts = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        if runner is not None and re.search(r"^\s*```sql[^\n]*\brun\b", text, re.M):
            runner.reset()
        if args.no_sql:
            text = re.sub(r"^(\s*```sql)[^\n]*$", r"\1", text, flags=re.M)
        try:
            body = renderer.render(text)
        except BuildError as exc:
            sys.exit(f"[{f.name}] {exc}")
        parts.append(f'<div class="chapter" data-file="{f.stem}">{body}</div>')
        print(f"rendered {f.name}")

    body_html = "".join(parts)
    fig_counter = iter(range(1, 10000))
    body_html = re.sub(r"Figure FIGNUM\.", lambda m: f"Figure {next(fig_counter)}.", body_html)
    pg_version = "16"
    if runner is not None and runner.conn is not None:
        with runner.conn.cursor() as cur:
            cur.execute("SHOW server_version")
            pg_version = cur.fetchone()[0].split()[0]
        runner.conn.rollback()
    practice_count = 0
    for box in re.findall(r'<div class="box box-practice">(.*?)<div class="box box-answers">', body_html, re.S):
        practice_count += len(re.findall(r"<strong>P\d+\.?</strong>", box))
    stats = {
        "{{EDITION}}": dt.date.today().strftime("%B %Y"),
        "{{QA_COUNT}}": str(body_html.count('<div class="qa">')),
        "{{SQL_COUNT}}": str(runner.blocks_run if runner else 0),
        "{{FIG_COUNT}}": str(renderer.fig_no),
        "{{PRACTICE_COUNT}}": str(practice_count),
        "{{PG_VERSION}}": pg_version,
    }
    cover = (ROOT / "cover.html").read_text(encoding="utf-8")
    for k, v in stats.items():
        cover = cover.replace(k, v)
    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>PwC Technology Interview Preparation — Modern Data Systems Handbook</title>
<meta name="author" content="Independent interview-preparation handbook">
<meta name="description" content="Modern Data Systems, SQL, Databases, APIs and Data Integration — interview handbook">
<meta name="keywords" content="SQL, PostgreSQL, data modeling, normalization, MongoDB, NoSQL, REST API, ETL, data mesh, interview">
<meta name="dcterms.created" content="{dt.date.today().isoformat()}">
</head><body>
{cover}
<nav class="toc" id="toc"><h1 class="toc-title notoc">Contents</h1>TOC_PLACEHOLDER</nav>
<main>{body_html}</main>
</body></html>"""
    soup = BeautifulSoup(doc, "lxml")
    postprocess(soup)
    toc = build_toc(soup)
    final_html = str(soup).replace("TOC_PLACEHOLDER", toc)
    (BUILD_DIR / "handbook.html").write_text(final_html, encoding="utf-8")
    if runner is not None:
        print(f"executed {runner.blocks_run} SQL blocks against PostgreSQL")
    print(f"figures: {renderer.fig_no}")
    if args.html_only:
        return

    from weasyprint import CSS, HTML
    from weasyprint.text.fonts import FontConfiguration
    fc = FontConfiguration()
    css = CSS(filename=str(ROOT / "style.css"), font_config=fc)
    HTML(string=final_html, base_url=str(ROOT)).write_pdf(
        str(OUT_PDF), stylesheets=[css], font_config=fc)
    print(f"wrote {OUT_PDF}")


if __name__ == "__main__":
    main()

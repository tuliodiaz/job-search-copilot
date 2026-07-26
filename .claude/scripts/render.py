#!/usr/bin/env python3
"""Document renderer — tailored markdown -> PDF (the engine's second deterministic script).

Why this is a script and not a recipe: a resume/cover letter is a high-stakes artifact the client
SENDS to an employer, so its output must be **identical every run and inspectable** — never a
surprise that differs from what was reviewed. That is the determinism/safety line (not "it uses a
browser"). The markdown -> HTML transform here is pure and deterministic; the HTML is written next to
the PDF so exactly what was rendered can be inspected.

Dependency policy (the answer, recorded so no future session re-derives it):
  - The ONLY external dependency is a Chromium-family browser used to print HTML -> PDF.
  - It is DECLARED, not bundled. This script discovers a browser among common install paths at
    runtime. If none is found it exits with a clear message + install hint — the agent's environment
    check then offers to install it ("offer, never silently"). We pin the render logic + template;
    the machine's browser install stays adaptive.

Deterministic subset: markdown -> HTML covers what resumes/cover letters need — headings, bold,
italic, inline code, links, unordered/ordered lists, horizontal rules, paragraphs. (Tables/nested
lists are intentionally out of scope; keep documents ATS-parseable and single-column.)

Usage:
    python3 render.py <input.md> <output.pdf> [--template default] [--html-only]

Exit codes:
    0  rendered (or wrote HTML with --html-only)
    2  bad usage / input missing / unknown template
    3  no Chromium-family browser found (declared dependency absent) -> caller offers to install
    4  the browser ran but produced no/empty PDF (fail visibly; never pass off a partial doc)
"""
from __future__ import annotations
import os
import re
import subprocess
import sys

RENDERER_VERSION = "1"

# Pinned, versioned, inspectable templates. ATS-friendly: standard fonts, single column, selectable
# text, no images. Add a new key to offer another look; never mutate output non-deterministically.
TEMPLATES = {
    "default": """
@page { size: Letter; margin: 0.6in 0.7in; }
* { box-sizing: border-box; }
body { font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif; font-size: 10.5pt;
       line-height: 1.42; color: #1a1a1a; margin: 0; }
h1 { font-size: 20pt; margin: 0 0 2pt; }
h2 { font-size: 12pt; margin: 14pt 0 6pt; padding-bottom: 2pt; border-bottom: 1px solid #999;
     text-transform: uppercase; letter-spacing: .04em; }
h3 { font-size: 11pt; margin: 10pt 0 2pt; }
p { margin: 4pt 0; }
ul, ol { margin: 4pt 0; padding-left: 18pt; }
li { margin: 2pt 0; }
a { color: #1a1a1a; text-decoration: none; }
hr { border: none; border-top: 1px solid #ccc; margin: 8pt 0; }
strong { font-weight: 600; }
em { font-style: italic; }
code { font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size: 9.5pt; }
""",
}

CHROME_CANDIDATES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
]


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _inline(text: str) -> str:
    text = _esc(text)
    codes: list[str] = []

    def _grab_code(m: re.Match) -> str:
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", _grab_code, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\s)([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!_)_(?!\s)([^_]+?)_(?!_)", r"<em>\1</em>", text)
    for i, c in enumerate(codes):
        text = text.replace(f"\x00{i}\x00", f"<code>{c}</code>")
    return text


_HR = re.compile(r"^\s*([-*_])\1\1+\s*$")
_H = re.compile(r"^(#{1,6})\s+(.*)$")
_UL = re.compile(r"^\s*[-*]\s+(.*)$")
_OL = re.compile(r"^\s*\d+\.\s+(.*)$")


def _is_block_start(line: str) -> bool:
    return (not line.strip()) or bool(_HR.match(line) or _H.match(line)
                                       or _UL.match(line) or _OL.match(line))


def markdown_to_html(md: str) -> str:
    """Deterministic markdown-subset -> HTML body. Same input always yields the same output."""
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    list_type: str | None = None
    i = 0

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            close_list(); i += 1; continue
        if _HR.match(line):
            close_list(); out.append("<hr>"); i += 1; continue
        m = _H.match(line)
        if m:
            close_list()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{_inline(m.group(2).strip())}</h{lvl}>"); i += 1; continue
        m = _UL.match(line)
        if m:
            if list_type != "ul":
                close_list(); out.append("<ul>"); list_type = "ul"
            out.append(f"<li>{_inline(m.group(1))}</li>"); i += 1; continue
        m = _OL.match(line)
        if m:
            if list_type != "ol":
                close_list(); out.append("<ol>"); list_type = "ol"
            out.append(f"<li>{_inline(m.group(1))}</li>"); i += 1; continue
        close_list()
        para = [line]
        j = i + 1
        while j < len(lines) and not _is_block_start(lines[j]):
            para.append(lines[j].rstrip()); j += 1
        out.append(f"<p>{_inline(' '.join(p.strip() for p in para))}</p>")
        i = j

    close_list()
    return "\n".join(out)


def build_html(md: str, template: str) -> str:
    css = TEMPLATES[template]
    title = "Document"
    m = re.search(r"^#\s+(.*)$", md, re.MULTILINE)
    if m:
        title = _esc(m.group(1).strip())
    body = markdown_to_html(md)
    return (f"<!doctype html>\n<html><head><meta charset=\"utf-8\">\n"
            f"<title>{title}</title>\n<style>{css}</style>\n</head>\n<body>\n{body}\n</body></html>\n")


def find_chrome() -> str | None:
    from shutil import which
    for c in CHROME_CANDIDATES:
        if os.path.isabs(c):
            if os.path.exists(c) and os.access(c, os.X_OK):
                return c
        elif which(c):
            return which(c)
    return None


def render_pdf(html_path: str, pdf_path: str, chrome: str) -> None:
    subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf_path}", f"file://{os.path.abspath(html_path)}"],
        check=True, capture_output=True, timeout=120,
    )


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    opts = [a for a in argv[1:] if a.startswith("--")]
    html_only = "--html-only" in opts
    template = "default"
    for o in opts:
        if o.startswith("--template"):
            template = o.split("=", 1)[1] if "=" in o else "default"
    if len(args) != 2:
        print("usage: render.py <input.md> <output.pdf> [--template NAME] [--html-only]",
              file=sys.stderr)
        return 2
    md_path, pdf_path = args
    if not os.path.isfile(md_path):
        print(f"error: input not found: {md_path}", file=sys.stderr)
        return 2
    if template not in TEMPLATES:
        print(f"error: unknown template '{template}' (have: {', '.join(TEMPLATES)})", file=sys.stderr)
        return 2

    with open(md_path, encoding="utf-8") as f:
        md = f.read()
    html = build_html(md, template)
    html_path = os.path.splitext(pdf_path)[0] + ".html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    if html_only:
        print(html_path)
        return 0

    chrome = find_chrome()
    if not chrome:
        print("error: no Chromium-family browser found (declared dependency).\n"
              "  Install Google Chrome or Chromium, then re-run. The inspectable HTML was written to:\n"
              f"  {html_path}", file=sys.stderr)
        return 3
    try:
        render_pdf(html_path, pdf_path, chrome)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"error: renderer failed to produce a PDF: {e}", file=sys.stderr)
        return 4
    if not os.path.isfile(pdf_path) or os.path.getsize(pdf_path) == 0:
        print("error: renderer produced no/empty PDF — not presenting a partial document as final.",
              file=sys.stderr)
        return 4
    print(pdf_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

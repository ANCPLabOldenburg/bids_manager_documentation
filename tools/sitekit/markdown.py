"""Markdown to HTML for the documentation pages.

CommonMark plus tables, with a few blocks the pages need:

    ::: step Open the BIDS preview          a numbered step (numbered per page)
    ::: note | tip | important | warning    a callout
    ::: check                               "Check that"
    ::: before                              "Before you start"
    ::: recap                               what changed
    ::: different                           "If something looks different"
    ::: details Summary text                a closed disclosure
    :::: os  /  ::: macos | windows | linux tabs per operating system
    ::: cards                               a grid of link cards (a list of links)

``[[term]]`` and ``[[term|shown text]]`` link a glossary entry. Headings get
ids; h2 and h3 are collected for "On this page".
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Callable, Optional

from markdown_it import MarkdownIt
from mdit_py_plugins.container import container_plugin
from mdit_py_plugins.deflist import deflist_plugin


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).lower()
    text = re.sub(r"[`'\"]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "section"


CALLOUTS = {
    "note": "Note",
    "tip": "Tip",
    "important": "Important",
    "warning": "Warning",
    "check": "Check that",
    "before": "Before you start",
    "recap": "What changed",
    "different": "If something looks different",
}

OS_NAMES = {"macos": "macOS", "windows": "Windows", "linux": "Linux"}


@dataclass
class Rendered:
    html: str
    toc: list = field(default_factory=list)  # [(level, id, text)]
    ids: set = field(default_factory=set)
    steps: int = 0


class PageRenderer:
    """One renderer per page: step numbers and heading ids are per page."""

    def __init__(self, glossary: dict, link: Callable[[str], str]) -> None:
        self.glossary = glossary
        self.link = link
        self.step_no = 0
        self.os_no = 0
        self.md = self._make()

    # -- markdown-it set-up ------------------------------------------------
    def _make(self) -> MarkdownIt:
        md = MarkdownIt("commonmark", {"html": True, "typographer": False})
        md.enable("table")
        md.enable("strikethrough")
        deflist_plugin(md)
        for name in CALLOUTS:
            container_plugin(md, name, render=self._callout(name))
        container_plugin(md, "step", render=self._step)
        container_plugin(md, "details", render=self._details)
        container_plugin(md, "os", render=self._os)
        for name in OS_NAMES:
            container_plugin(md, name, render=self._os_panel(name))
        container_plugin(md, "cards", render=self._cards)
        container_plugin(md, "columns", render=self._columns)
        container_plugin(md, "release", render=self._release)
        return md

    def _callout(self, name: str):
        label = CALLOUTS[name]

        def render(_r, tokens, idx, _options, _env):
            tok = tokens[idx]
            if tok.nesting == 1:
                extra = tok.info.strip()[len(name):].strip()
                title = html.escape(extra) if extra else label
                return (f'<aside class="callout callout--{name}">'
                        f'<p class="callout-label">{title}</p><div class="callout-body">\n')
            return "</div></aside>\n"
        return render

    def _step(self, tokens, idx, _options, _env):
        tok = tokens[idx]
        if tok.nesting == 1:
            self.step_no += 1
            title = tok.info.strip()[len("step"):].strip()
            title_html = self.md.renderInline(title)
            sid = "step-" + slugify(title)
            self._step_ids = getattr(self, "_step_ids", set())
            base, n = sid, 2
            while sid in self._step_ids:
                sid = f"{base}-{n}"
                n += 1
            self._step_ids.add(sid)
            return (f'<section class="step" id="{sid}"><div class="step-no" aria-hidden="true">'
                    f'{self.step_no}</div><div class="step-main"><h3 class="step-title">'
                    f'<span class="visually-hidden">Step {self.step_no}. </span>{title_html}</h3>\n')
        return "</div></section>\n"

    def _details(self, tokens, idx, _options, _env):
        tok = tokens[idx]
        if tok.nesting == 1:
            summary = tok.info.strip()[len("details"):].strip() or "More"
            return (f'<details class="disclosure"><summary>{self.md.renderInline(summary)}'
                    f'</summary><div class="disclosure-body">\n')
        return "</div></details>\n"

    def _os(self, tokens, idx, _options, _env):
        tok = tokens[idx]
        if tok.nesting == 1:
            self.os_no += 1
            # The tab bar is written by the script from the panels present.
            return f'<div class="os-tabs" data-os-group="{self.os_no}">\n'
        return "</div>\n"

    def _os_panel(self, name: str):
        def render(_r, tokens, idx, _options, _env):
            tok = tokens[idx]
            if tok.nesting == 1:
                return (f'<div class="os-panel" data-os="{name}" '
                        f'data-label="{OS_NAMES[name]}">\n')
            return "</div>\n"
        return render

    def _cards(self, tokens, idx, _options, _env):
        tok = tokens[idx]
        if tok.nesting == 1:
            cols = tok.info.strip()[len("cards"):].strip()
            return f'<div class="cards" data-cols="{cols or "auto"}">\n'
        return "</div>\n"

    def _columns(self, tokens, idx, _options, _env):
        tok = tokens[idx]
        if tok.nesting == 1:
            return '<div class="columns">\n'
        return "</div>\n"

    def _release(self, tokens, idx, _options, _env):
        """``::: release 1.4.1 | September 2026 | v141 | Major release``"""
        tok = tokens[idx]
        if tok.nesting == 1:
            parts = [p.strip() for p in tok.info.strip()[len("release"):].split("|")]
            version = parts[0]
            date = parts[1] if len(parts) > 1 else ""
            rid = parts[2] if len(parts) > 2 and parts[2] else "v" + version.replace(".", "")
            badge = parts[3] if len(parts) > 3 else ""
            cls = "release is-landmark" if badge else "release"
            head = f'<h2 id="{rid}">{html.escape(version)}</h2>'
            if date:
                head += f'<span class="release-date">{html.escape(date)}</span>'
            if badge:
                head += f'<span class="release-badge">{html.escape(badge)}</span>'
            return f'<section class="{cls}"><div class="release-head">{head}</div>\n'
        return "</section>\n"

    # -- the page --------------------------------------------------------
    def render(self, source: str) -> Rendered:
        source = self._glossary_links(source)
        body = self.md.render(source)
        body, toc, ids = self._heading_ids(body)
        body = self._tables(body)
        body = self._code_blocks(body)
        body = self._inline_code(body)
        return Rendered(html=body, toc=toc, ids=ids, steps=self.step_no)

    _TERM = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")

    def _glossary_links(self, source: str) -> str:
        out = []
        in_fence = False
        for line in source.split("\n"):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
            if not in_fence and "[[" in line:
                line = self._TERM.sub(self._term, line)
            out.append(line)
        return "\n".join(out)

    def _term(self, m: re.Match) -> str:
        key = m.group(1).strip()
        shown = (m.group(2) or key).strip()
        entry = self.glossary.get(slugify(key))
        if entry is None:
            raise KeyError(f"glossary term not defined: {key!r}")
        href = self.link(f"/reference/glossary/#{slugify(key)}")
        tip = html.escape(entry["short"], quote=True)
        return (f'<a class="term" href="{href}" data-tip="{tip}">'
                f'{html.escape(shown)}</a>')

    _HEADING = re.compile(r"<h([1-6])(\s[^>]*)?>(.*?)</h\1>", re.S)

    def _heading_ids(self, body: str):
        toc, ids = [], set()

        def repl(m: re.Match) -> str:
            level, attrs, inner = int(m.group(1)), m.group(2) or "", m.group(3)
            # Step titles carry their id on the section.
            if 'class="step-title"' in attrs:
                text = re.sub(r'<span class="visually-hidden">.*?</span>', "", inner)
                sid = step_ids.pop(0) if step_ids else "step-" + slugify(text)
                ids.add(sid)
                if level in (2, 3):
                    toc.append((3, sid, re.sub(r"<[^>]+>", "", text).strip()))
                return m.group(0)
            given = re.search(r'\bid="([^"]+)"', attrs)
            explicit = re.search(r'\{#([a-z0-9-]+)\}\s*$', inner)
            if given:
                hid = given.group(1)
                attrs = attrs.replace(given.group(0), "").rstrip()
            elif explicit:
                hid = explicit.group(1)
                inner = inner[:explicit.start()].rstrip()
            else:
                hid = slugify(inner)
            base, n = hid, 2
            while hid in ids:
                hid = f"{base}-{n}"
                n += 1
            ids.add(hid)
            text = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
            if level in (2, 3):
                toc.append((level, hid, text))
            anchor = (f'<a class="h-anchor" href="#{hid}" aria-label="Link to this section">'
                      '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6.5 9.5l3-3M7 4.6'
                      'l1-1a2.6 2.6 0 013.7 3.7l-1 1M9 11.4l-1 1A2.6 2.6 0 014.3 8.7l1-1"/></svg></a>')
            return f'<h{level} id="{hid}"{attrs}>{inner}{anchor if level in (2, 3) else ""}</h{level}>'

        # Section ids on the step sections are added by the renderer.
        step_ids = re.findall(r'<section class="step" id="([^"]+)"', body)
        for sid in step_ids:
            ids.add(sid)
        step_ids = list(step_ids)
        body = self._HEADING.sub(repl, body)
        for sid in re.findall(r'\sid="([^"]+)"', body):
            ids.add(sid)
        return body, toc, ids

    @staticmethod
    def _inline_code(body: str) -> str:
        def repl(m: re.Match) -> str:
            inner = m.group(1)
            if len(html.unescape(re.sub(r"<[^>]+>", "", inner))) <= 30:
                return m.group(0)
            broken = re.sub(r"([/_])(?=[^<]*(?:<|$))", r"\1<wbr>", inner)
            return f'<code class="long">{broken}</code>'
        parts = re.split(r"(<pre>.*?</pre>)", body, flags=re.S)
        return "".join(p if p.startswith("<pre>") else re.sub(r"<code>(.*?)</code>", repl, p, flags=re.S)
                       for p in parts)

    @staticmethod
    def _tables(body: str) -> str:
        def wrap(m: re.Match) -> str:
            inner = m.group(1)
            # A table written with an empty header row (``| | |``) is a list of
            # label and value: it gets no header.
            head = re.search(r"<thead>(.*?)</thead>", inner, flags=re.S)
            if head and not re.sub(r"<[^>]+>|\s", "", head.group(1)):
                inner = inner.replace(head.group(0), "")
                return f'<div class="table-wrap is-list"><table>{inner}</table></div>'
            # The first column stays on one line when it holds names and
            # values; when it holds sentences it wraps like the others.
            firsts = re.findall(r"<tr>\s*<td[^>]*>(.*?)</td>", inner, flags=re.S)
            longest = max((len(re.sub(r"<[^>]+>", "", c).strip()) for c in firsts), default=0)
            cls = "table-wrap wrap-first" if longest > 34 else "table-wrap"
            return f'<div class="{cls}"><table>{inner}</table></div>'
        return re.sub(r"<table>(.*?)</table>", wrap, body, flags=re.S)

    @staticmethod
    def _code_blocks(body: str) -> str:
        def repl(m: re.Match) -> str:
            lang = m.group(1) or ""
            code = m.group(2)
            if lang in ("console", "shell-session"):
                lines = []
                for line in code.split("\n"):
                    if line.startswith("$ "):
                        lines.append('<span class="prompt" aria-hidden="true">$ </span>'
                                     f'<span class="cmd">{line[2:]}</span>')
                    elif line.startswith("&gt; "):
                        lines.append('<span class="prompt" aria-hidden="true">&gt; </span>'
                                     f'<span class="cmd">{line[5:]}</span>')
                    elif line:
                        lines.append(f'<span class="out">{line}</span>')
                    else:
                        lines.append("")
                code = "\n".join(lines)
            label = {"console": "Terminal", "powershell": "PowerShell", "json": "JSON",
                     "tsv": "TSV", "text": "", "python": "Python", "bash": "Shell",
                     "yaml": "YAML"}.get(lang, lang)
            head = f'<span class="code-lang">{label}</span>' if label else ""
            return (f'<div class="code" data-lang="{lang}">{head}<button class="code-copy" '
                    f'type="button" aria-label="Copy to the clipboard">Copy</button>'
                    f'<pre><code>{code}</code></pre></div>')
        return re.sub(r'<pre><code(?: class="language-([\w-]+)")?>(.*?)</code></pre>',
                      repl, body, flags=re.S)


def inline(text: str) -> str:
    """Inline Markdown (for captions, labels, ledes)."""
    return _INLINE.renderInline(text or "")


_INLINE = MarkdownIt("commonmark", {"html": True})

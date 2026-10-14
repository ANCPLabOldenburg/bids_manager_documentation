"""Checks run on every build, on the written HTML.

Links and anchors, assets, alt text, image sizes, heading order, words the
site does not use, dashes and emoji, personal paths, and well-formed markup.
A problem fails the build; a warning is printed.
"""

from __future__ import annotations

import html as _html
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

# Words and phrases that sell rather than teach (plan 7.2), plus product rules.
BANNED = [
    (r"\bseamless(ly)?\b", "seamless"),
    (r"\beffortless(ly)?\b", "effortless"),
    (r"\bpowerful\b", "powerful"),
    (r"\bsimply\b", "simply"),
    (r"\bjust\b", "just"),
    (r"\bone workflow\b", "one workflow"),
    (r"\b(two|three|four|five|six|seven|eight|nine|ten|\d+) modalities\b", "x modalities"),
    (r"\bblazing\b|\bcutting-edge\b|\bstate-of-the-art\b|\bgame-chang", "marketing"),
    (r"\bBIDSvue\b", "BIDSvue"),
    (r"\biEEG\b", "iEEG"),
    (r"\bScene \d", "Scene (say Step)"),
]
DASHES = re.compile("[\u2013\u2014\u2015]")
# Pictographs, not the symbols the application itself draws in its badges (✓ ✕ ✔).
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000026FF\U0001F000-\U0001F2FF"
                   "\u2700-\u2712\u2717-\u27BF]")


def _private_names() -> list:
    """Names that must never be published: the name of the home folder of the
    account doing the work, and any listed (comma-separated) in the environment
    variable BM_DOCS_PRIVATE_NAMES. Read at run time, so the source that guards
    against them does not publish them either."""
    import os as _os
    names = {n.strip() for n in _os.environ.get("BM_DOCS_PRIVATE_NAMES", "").split(",") if n.strip()}
    if not _os.environ.get("CI"):
        home = Path.home().name
        if len(home) >= 4:
            names.add(home)
    return sorted(names)


_NAMES = "".join("|" + re.escape(n) for n in _private_names())

PERSONAL = re.compile(r"/Users/(?!<you>|you\b|Shared)\w+|C:\\\\Users\\\\(?!<you>)\w+" + _NAMES, re.I)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source",
        "track", "wbr", "path", "circle", "rect", "line", "polyline", "polygon", "use", "stop"}


@dataclass
class Report:
    problems: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


class _Doc(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.assets: list[str] = []
        self.imgs: list[dict] = []
        self.headings: list[int] = []
        self.text: list[str] = []
        self.skip = 0  # inside code/pre/script/style
        self.quoted: list[str] = []
        self.quote_depth = None  # stack depth of a data-generated element

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in VOID:
            self.stack.append(tag)
            if "data-generated" in a and self.quote_depth is None:
                self.quote_depth = len(self.stack)
        if "id" in a:
            if a["id"] in self.ids:
                self.errors.append(f"duplicate id {a['id']!r}")
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        for key in ("src", "poster"):
            if a.get(key):
                self.assets.append(a[key])
        if a.get("srcset"):
            for part in a["srcset"].split(","):
                self.assets.append(part.strip().split(" ")[0])
        if tag == "link" and a.get("rel") in ("stylesheet", "preload", "icon", "apple-touch-icon"):
            self.assets.append(a.get("href", ""))
        if tag == "img":
            self.imgs.append(a)
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if tag in ("code", "pre", "script", "style", "kbd", "svg"):
            self.skip += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag in ("code", "pre", "script", "style", "kbd", "svg"):
            self.skip = max(0, self.skip - 1)
        if not self.stack:
            self.errors.append(f"closing </{tag}> with nothing open")
            return
        if self.quote_depth is not None and len(self.stack) <= self.quote_depth:
            self.quote_depth = None
        if self.stack[-1] != tag:
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.errors.append(f"<{self.stack.pop()}> not closed before </{tag}>")
                self.stack.pop()
            else:
                self.errors.append(f"stray </{tag}>")
            return
        self.stack.pop()

    def handle_data(self, data):
        if self.skip:
            return
        if self.quote_depth is not None:
            self.quoted.append(data)
        else:
            self.text.append(data)


def visible_text(fragment: str) -> str:
    d = _Doc()
    d.feed(fragment)
    return " ".join(" ".join(d.text).split())


def sections(fragment: str):
    """Split a page body at h2/h3 headings for the search index."""
    parts = re.split(r'(<h[23][^>]*\bid="[^"]+"[^>]*>.*?</h[23]>|<section class="step" id="[^"]+")',
                     fragment, flags=re.S)
    current = {"id": "", "heading": "", "text": ""}
    out = [current]
    for part in parts:
        m = re.match(r'<h[23][^>]*\bid="([^"]+)"[^>]*>(.*?)</h[23]>', part, re.S)
        s = re.match(r'<section class="step" id="([^"]+)"', part)
        if m:
            current = {"id": m.group(1), "heading": visible_text(m.group(2)), "text": ""}
            out.append(current)
        elif s:
            title = re.search(r'class="step-title">(.*?)</h3>', fragment[fragment.find(part):], re.S)
            heading = visible_text(title.group(1)) if title else ""
            heading = re.sub(r"^Step \d+\.\s*", "", heading)
            current = {"id": s.group(1), "heading": heading, "text": ""}
            out.append(current)
        else:
            current["text"] += " " + visible_text(part)
    return [c for c in out if c["text"].strip() or c["heading"]]


def run(site, out: Path, media) -> Report:
    rep = Report()
    pages = {}
    for p in out.rglob("*.html"):
        rel = p.relative_to(out).as_posix()
        pages[rel] = p.read_text(encoding="utf-8")
    parsed = {}
    for rel, text in pages.items():
        d = _Doc()
        d.feed(text)
        parsed[rel] = d
        for err in d.errors[:5]:
            rep.problems.append(f"{rel}: markup: {err}")
        if d.stack and d.stack != ["html"]:
            rep.problems.append(f"{rel}: markup: left open {d.stack[-4:]}")
    # The 404 page is served at whatever depth was asked for, so it links from
    # the site's root path ("/bids_manager_documentation/..."): check those
    # links as root-relative.
    prefix = "/" + site.cfg["base_url"].split("/", 3)[3]
    for rel, d in parsed.items():
        if "http-equiv=\"refresh\"" in pages[rel]:
            continue
        base = Path(rel).parent.as_posix()
        if rel == "404.html":
            d.links = [h[len(prefix):] if h.startswith(prefix) else h for h in d.links]
            d.assets = [h[len(prefix):] if h.startswith(prefix) else h for h in d.assets]
        for href in d.links:
            _check_link(rep, rel, base, href, parsed, out)
        for src in d.assets:
            if src.startswith(("http", "data:", "//")) or not src:
                continue
            target = _resolve(base, src)
            if not (out / target).exists():
                rep.problems.append(f"{rel}: missing asset {src}")
        for img in d.imgs:
            if "alt" not in img:
                rep.problems.append(f"{rel}: <img> without alt: {img.get('src')}")
            elif not img["alt"].strip() and img.get("aria-hidden") != "true" and img.get("role") != "presentation":
                rep.problems.append(f"{rel}: <img> with empty alt and not marked decorative: {img.get('src')}")
            if not img.get("width") or not img.get("height"):
                rep.problems.append(f"{rel}: <img> without width/height: {img.get('src')}")
        last = 0
        for level in d.headings:
            if last and level > last + 1:
                rep.problems.append(f"{rel}: heading jumps from h{last} to h{level}")
            last = level
        text = " ".join(d.text)
        everything = text + " " + " ".join(d.quoted)
        if rel.startswith("_styleguide"):
            continue
        for m in DASHES.finditer(everything):
            ctx = everything[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
            rep.problems.append(f"{rel}: dash in text: ...{ctx}...")
        for m in EMOJI.finditer(everything):
            rep.problems.append(f"{rel}: emoji in text: {m.group(0)!r}")
        for pattern, name in BANNED:
            for m in re.finditer(pattern, text, flags=re.I if name not in ("iEEG", "BIDSvue") else 0):
                ctx = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
                rep.problems.append(f"{rel}: banned word ({name}): ...{ctx}...")
    # A rule left open swallows every rule after it, silently: count braces.
    for css in sorted((out / "static").rglob("*.css")):
        src = re.sub(r"/\*.*?\*/", "", css.read_text(encoding="utf-8"), flags=re.S)
        src = re.sub(r'"[^"\n]*"|\'[^\'\n]*\'', '""', src)
        depth = 0
        for n, line in enumerate(src.split("\n"), 1):
            depth += line.count("{") - line.count("}")
            if depth < 0:
                rep.problems.append(f"{css.relative_to(out).as_posix()}:{n}: a closing brace with no rule open")
                depth = 0
        if depth:
            rep.problems.append(f"{css.relative_to(out).as_posix()}: {depth} rule(s) left open")
    for rel, text in pages.items():
        for m in PERSONAL.finditer(text):
            rep.problems.append(f"{rel}: personal path or name: {m.group(0)}")
    return rep


def _resolve(base: str, href: str) -> str:
    path = unquote(urlsplit(href).path)
    import posixpath
    joined = posixpath.normpath(posixpath.join(base, path)) if base not in ("", ".") else posixpath.normpath(path)
    if href.endswith("/") or path == "":
        joined = (joined + "/index.html") if joined not in (".", "") else "index.html"
    return joined.lstrip("./") if joined.startswith("./") else joined


def _check_link(rep, rel, base, href, parsed, out):
    if href.startswith(("http://", "https://", "mailto:", "//")):
        return
    parts = urlsplit(href)
    if not parts.path:
        target = rel
    else:
        target = _resolve(base, href)
        if (out / target).is_dir():
            target = target.rstrip("/") + "/index.html"
    if target.endswith("/"):
        target += "index.html"
    if target not in parsed and not (out / target).exists():
        rep.problems.append(f"{rel}: broken link {href}")
        return
    frag = parts.fragment
    if frag and target in parsed and frag not in parsed[target].ids:
        rep.problems.append(f"{rel}: missing anchor {href}")

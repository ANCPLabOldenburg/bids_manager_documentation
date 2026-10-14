"""Reference tables rendered from data the application itself produced.

``tools/reference/extract.py`` reads the installed BIDS Manager (argument
parsers, the Settings dialog's widgets, the inventory's column descriptions,
the quality-check explanations, the viewer keymap, the classifier settings,
the themes) and writes ``data/*.json``. The pages render those, so a flag or
a setting cannot drift from the code. A page asking for something the data
does not contain is a build problem.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Callable, Optional

from .markdown import inline, slugify


def load(folder: Path) -> dict:
    import yaml
    out = {}
    for p in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        out[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    for p in sorted(folder.glob("*.yml")) if folder.is_dir() else []:
        out.setdefault(p.stem, yaml.safe_load(p.read_text(encoding="utf-8")))
    return out


# -- keys, written the way each platform names them ------------------------
# A Mac names Command (⌘), Option (⌥), Control (⌃), Shift (⇧), Return and
# Delete; Windows and Linux name Ctrl, Alt, Shift, Enter and Backspace. Qt
# binds Ctrl to Command on a Mac, so a shortcut written ``Ctrl+Z`` is ⌘Z there.
# The modifiers show as the symbols BIDS Manager itself prints on a Mac; each
# key carries its spelled name for screen readers and as a tooltip.
_MAC = {"ctrl": "⌘", "meta": "⌃", "alt": "⌥", "shift": "⇧", "cmd": "⌘", "command": "⌘",
        "option": "⌥", "control": "⌃"}
_MAC_ORDER = ["⌃", "⌥", "⇧", "⌘"]
_MAC_NAMES = {"⌃": "Control", "⌥": "Option", "⇧": "Shift", "⌘": "Command"}
_NAMED = {"left": "←", "right": "→", "up": "↑", "down": "↓", "return": "Return", "enter": "Return",
          "esc": "Esc", "escape": "Esc", "space": "Space", "del": "Forward Delete", "delete": "Forward Delete",
          "backspace": "Delete", "tab": "Tab", "pgup": "Page Up", "pgdown": "Page Down"}
_OTHER = {"ctrl": "Ctrl", "shift": "Shift", "alt": "Alt", "meta": "Meta", "esc": "Esc", "escape": "Esc",
          "left": "←", "right": "→", "up": "↑", "down": "↓", "return": "Enter", "enter": "Enter",
          "del": "Delete", "delete": "Delete", "backspace": "Backspace", "pgup": "Page Up", "pgdown": "Page Down"}


def mac_key(spec: str) -> str:
    """``Ctrl+Shift+Z`` -> ``⇧⌘Z``; ``Enter`` -> ``Return``; ``Backspace`` -> ``Delete``."""
    parts = [p.strip() for p in spec.split("+") if p.strip()]
    mods, key = [], parts[-1] if parts else ""
    for p in parts[:-1]:
        sym = _MAC.get(p.lower())
        if sym:
            mods.append(sym)
    mods.sort(key=_MAC_ORDER.index)
    key = _NAMED.get(key.lower(), key)
    return "".join(mods) + key


def mac_spelled(display: str) -> str:
    """``⇧⌘Z`` -> ``Shift-Command-Z``, for screen readers and tooltips."""
    mods, rest = [], display
    while rest and rest[0] in _MAC_NAMES:
        mods.append(_MAC_NAMES[rest[0]]); rest = rest[1:]
    rest = rest.strip()
    rest = {"⌫": "Delete", "⌦": "Forward Delete", "↩": "Return"}.get(rest, rest)
    return "-".join(mods + [rest]) if rest else "-".join(mods)


def mac_display(display: str) -> str:
    """The keymap the app writes (``⌫``, ``⌦``) with Delete keys spelled."""
    return display.replace("⌫", "Delete").replace("⌦", "Forward Delete")


def other_key(spec: str) -> str:
    parts = [p.strip() for p in spec.split("+") if p.strip()]
    return "+".join(_OTHER.get(p.lower(), p) for p in parts)


_MOUSE = ("click", "double-click", "drag", "scroll", "right-click", "wheel")


def keys_html(mac: str, other: str) -> str:
    """One key or shortcut. The same on every system: one key. Otherwise both,
    "⌘Z on macOS, Ctrl+Z on Windows and Linux"; the page's script keeps only
    the reader's (the system it detects, or the one chosen in an OS tab)."""
    mac = mac_display(mac)
    spelled = mac_spelled(mac)
    if mac == other:
        return f'<kbd class="key" title="{html.escape(spelled)}">{html.escape(other)}</kbd>'
    return (f'<span class="keys" data-mac="{html.escape(mac)}" data-mac-name="{html.escape(spelled)}" '
            f'data-other="{html.escape(other)}"><kbd class="key" title="{html.escape(spelled)}">{html.escape(mac)}</kbd> on macOS, '
            f'<kbd class="key">{html.escape(other)}</kbd> on Windows and Linux</span>')


def kbd(spec: str) -> str:
    parts = [p.strip() for p in spec.split("+") if p.strip()]
    if parts and parts[-1].lower() in _MOUSE:
        mods = "+".join(parts[:-1])
        mouse = parts[-1][0].upper() + parts[-1][1:]
        mac = (mac_key(mods + "+X")[:-1] + " + " + mouse) if mods else mouse
        other = (other_key(mods) + " + " + mouse) if mods else mouse
        return keys_html(mac, other)
    return keys_html(mac_key(spec), other_key(spec))


def _md(text: str) -> str:
    return inline(text or "")


def _esc(text) -> str:
    return html.escape(str(text if text is not None else ""))


class Macros:
    """What a page can ask the reference data for: ``ref.cli("bidsmgr-scan")``."""

    def __init__(self, data: dict, link: Callable[[str], str], page: str, problems: list,
                 glossary: dict) -> None:
        self.data, self.link, self.page, self.problems, self.glossary = data, link, page, problems, glossary

    def _need(self, name: str):
        if name not in self.data:
            self.problems.append(f"{self.page}: reference data missing: data/{name}.json")
            return None
        return self.data[name]

    # -- command line --------------------------------------------------------
    def cli_verbs(self) -> list:
        d = self._need("cli")
        return [] if d is None else [v["prog"] for v in d["verbs"]]

    def _verb(self, prog: str):
        d = self._need("cli")
        if d is None:
            return None
        for v in d["verbs"]:
            if v["prog"] == prog:
                return v
        self.problems.append(f"{self.page}: unknown command {prog}")
        return None

    def flag(self, prog: str, flag: str) -> str:
        """``--probe-convert``, checked against the parser."""
        v = self._verb(prog)
        if v is not None and not any(flag in a["flags"] for a in v["arguments"]):
            self.problems.append(f"{self.page}: {prog} has no flag {flag}")
        return f"<code>{_esc(flag)}</code>"

    def usage(self, prog: str) -> str:
        v = self._verb(prog)
        if v is None:
            return ""
        return (f'<div class="code" data-lang="text" data-generated><pre><code>{_esc(v["usage"])}'
                f'</code></pre></div>')

    def cli(self, prog: str) -> str:
        v = self._verb(prog)
        if v is None:
            return ""
        rows = []
        for a in v["arguments"]:
            if a["flags"] == ["-h", "--help"]:
                continue
            names = ", ".join(f"<code>{_esc(f)}</code>" for f in a["flags"]) or f"<code>{_esc(a['metavar'] or a['dest'])}</code>"
            extra = []
            if a.get("choices"):
                extra.append("One of " + ", ".join(f"<code>{_esc(c)}</code>" for c in a["choices"]) + ".")
            if a.get("default") not in (None, "", False, [], "==SUPPRESS==") and not a.get("positional"):
                extra.append(f"Default <code>{_esc(a['default'])}</code>.")
            if a.get("required") and not a.get("positional"):
                extra.append("Required.")
            value = f'<code class="metavar">{_esc(a["metavar"])}</code>' if a.get("metavar") and a["flags"] else ""
            rows.append(f'<tr id="{prog}.{slugify(a["flags"][-1] if a["flags"] else a["dest"])}">'
                        f'<td>{names} {value}</td><td class="wrap">{_esc(a.get("help") or "")} '
                        f'{" ".join(extra)}</td></tr>')
        return ('<div class="table-wrap" data-generated><table><thead><tr><th>Argument</th><th>What it does</th>'
                f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')

    # -- settings ------------------------------------------------------------
    def _settings_page(self, title: str):
        d = self._need("settings")
        if d is None:
            return None
        for p in d["pages"]:
            if p["title"] == title:
                return p
        self.problems.append(f"{self.page}: no Settings page {title!r}")
        return None

    def setting(self, page: str, label: str) -> str:
        """A setting's label in bold, checked to exist on that page."""
        p = self._settings_page(page)
        if p is not None:
            labels = [it.get("label", "") for g in p["groups"] for it in g["items"]]
            if label not in labels:
                self.problems.append(f"{self.page}: Settings > {page} has no {label!r}")
        return f"<strong>{_esc(label)}</strong>"

    def settings(self, title: str) -> str:
        p = self._settings_page(title)
        if p is None:
            return ""
        out = []
        for g in p["groups"]:
            if g.get("title"):
                out.append(f'<h3 id="{slugify(title)}-{slugify(g["title"])}">{_esc(g["title"])}</h3>')
            if g.get("hint"):
                out.append(f'<p class="muted" data-generated>{_esc(g["hint"])}</p>')
            rows = []
            for it in g["items"]:
                if it.get("table"):
                    # A table the user fills: say what its columns are.
                    cols = [c.strip() for c in re.sub(r"^Columns:\s*", "", it.get("tip", "")).split(", ") if c.strip()]
                    if cols:
                        listed = ", ".join(f"<strong>{_esc(c)}</strong>" for c in cols[:-1])
                        listed = f"{listed} and <strong>{_esc(cols[-1])}</strong>" if listed else f"<strong>{_esc(cols[-1])}</strong>"
                        out.append(f'<p data-generated>A table with the columns {listed}.</p>')
                    continue
                default = it.get("default")
                dtext = "" if default in (None, "") else _esc(default)
                ctl = f'<br><span class="muted">{_esc(it["control"])}</span>' if it.get("control") else ""
                rows.append(f'<tr><td class="wrap"><strong>{_esc(it["label"])}</strong>{ctl}</td>'
                            f'<td class="wrap">{_esc(it.get("tip", ""))}'
                            f'{" Choices: " + ", ".join(_esc(c) for c in it["choices"]) + "." if it.get("choices") and len(it["choices"]) <= 12 else ""}'
                            f'</td><td class="wrap">{dtext}</td></tr>')
            if rows:
                out.append('<div class="table-wrap" data-generated><table><thead><tr><th>Setting</th>'
                           f'<th>What it does</th><th>Default</th></tr></thead><tbody>{"".join(rows)}'
                           '</tbody></table></div>')
        return "\n".join(out)

    # -- the Editor's Tools menu --------------------------------------------
    def tool(self, label: str) -> str:
        d = self._need("tools")
        if d is not None:
            names = [t["label"] for g in d["groups"] for t in g["items"]]
            if label not in names:
                self.problems.append(f"{self.page}: the Tools menu has no {label!r}")
        return f"<strong>{_esc(label)}</strong>"

    # -- generic data tables --------------------------------------------------
    def table(self, name: str, columns: list, *, key: str = "rows", first_code: bool = False,
              under: Optional[dict] = None) -> str:
        """``under`` maps a column's key to another key whose value is shown
        beneath it in code type (and gets no column of its own)."""
        d = self._need(name)
        if d is None:
            return ""
        rows = d[key] if isinstance(d, dict) else d

        def text(r, k):
            v = r.get(k, "")
            return ", ".join(str(x) for x in v) if isinstance(v, list) else str(v)
        # A column of short values (names, yes and no) keeps to one line and
        # takes only the width it needs; the prose columns share the rest.
        tight = [max((len(text(r, k)) for r in rows), default=0) <= 22 for k, _l in columns]
        head = "".join(f'<th{" class=tight" if t else ""}>{_esc(label)}</th>'
                       for (_k, label), t in zip(columns, tight))
        body = []
        for r in rows:
            cells = []
            for i, (k, _label) in enumerate(columns):
                v = text(r, k)
                cell = f"<code>{_esc(v)}</code>" if (i == 0 and first_code) else _esc(v)
                if under and k in under and text(r, under[k]) and text(r, under[k]) != v:
                    cell += f'<br><code class="under">{_esc(text(r, under[k]))}</code>'
                cls = "tight" if tight[i] else ("wrap" if i else "")
                cells.append(f'<td class="{cls}">{cell}</td>' if cls else f"<td>{cell}</td>")
            body.append(f"<tr>{''.join(cells)}</tr>")
        return (f'<div class="table-wrap" data-generated><table><thead><tr>{head}</tr></thead>'
                f'<tbody>{"".join(body)}</tbody></table></div>')


def _themes(self) -> str:
    """The application's themes in their groups, each with its colours."""
    d = self._need("themes")
    if d is None:
        return ""
    groups: dict = {}
    for t in d["themes"]:
        groups.setdefault(t["group"], []).append(t)
    out = ['<div class="theme-grid" data-generated>']
    for group, items in groups.items():
        out.append(f'<div class="theme-group"><p class="theme-group-title">{_esc(group)}</p><ul>')
        for t in items:
            chips = "".join(f'<i style="background:{_esc(c)}"></i>' for c in t.get("swatch", [])[:5])
            kind = "dark" if t.get("dark") else "light"
            out.append(f'<li><span class="swatches swatches--{kind}" aria-hidden="true">{chips}</span>'
                       f'<span><b>{_esc(t["label"])}</b> <span class="theme-desc">{_esc(t.get("description", ""))}</span></span></li>')
        out.append("</ul></div>")
    out.append("</div>")
    return "".join(out)


Macros.themes = _themes


def _kbd_pair(mac: str, other: str) -> str:
    return keys_html(mac, other)


def _keys(self, kind: str) -> str:
    """Every keyboard shortcut of one kind of viewer, by category."""
    d = self._need("keys")
    if d is None:
        return ""
    cats: dict = {}
    for a in d["actions"]:
        if kind not in a["kinds"] or not a["keys_other"]:
            continue
        cats.setdefault(a["category"], []).append(a)
    rows = []
    for cat, items in cats.items():
        rows.append(f'<tr class="group-row"><th colspan="2" scope="rowgroup">{_esc(cat)}</th></tr>')
        for a in items:
            ks = " or ".join(_kbd_pair(m, o) for m, o in zip(a["keys_mac"], a["keys_other"]))
            rows.append(f'<tr><td class="wrap">{_esc(a["title"])}</td><td class="nowrap">{ks}</td></tr>')
    return ('<p class="key-legend" data-generated>On a Mac, ⌘ is Command, ⌥ Option, ⌃ Control and ⇧ Shift. '
            'Keys are shown for the system this page was opened on; where it cannot tell, for both.</p>'
            '<div class="table-wrap" data-generated><table class="keys-table"><thead><tr><th>Action</th>'
            f'<th>Key</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def _gestures(self, canvas: str) -> str:
    d = self._need("keys")
    if d is None:
        return ""
    rows = [f'<tr><td class="nowrap">{_kbd_pair(g["mac"], g["other"])}</td><td class="wrap">{_esc(g["does"])}</td></tr>'
            for g in d["gestures"].get(canvas, [])]
    if not rows:
        self.problems.append(f"{self.page}: no gestures for {canvas!r}")
    return ('<div class="table-wrap" data-generated><table><thead><tr><th>Mouse</th><th>Does</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def _tool_tip(self, label: str) -> str:
    d = self._need("tools")
    if d is None:
        return ""
    for g in d["groups"]:
        for t in g["items"]:
            if t["label"] == label:
                return _esc(t["tip"])
    self.problems.append(f"{self.page}: the Tools menu has no {label!r}")
    return ""


def _count_actions(self, kind: str = "") -> int:
    d = self._need("keys")
    if d is None:
        return 0
    return sum(1 for a in d["actions"] if (not kind or kind in a["kinds"]))


Macros.keys = _keys
Macros.gestures = _gestures
Macros.tool_tip = _tool_tip
Macros.count_actions = _count_actions


def _glossary(self) -> str:
    """Every glossary term, alphabetically, each with its own anchor."""
    entries = sorted(self.glossary.values(), key=lambda e: e["term"].lower())
    out, letter = ['<dl class="glossary" data-generated>'], ""
    for e in entries:
        first = e["term"][0].upper()
        if first != letter:
            letter = first
        body = _md(e.get("long") or e["short"])
        see = ""
        if e.get("see"):
            see = f' <a href="{self.link(e["see"])}">More</a>'
        out.append(f'<dt id="{slugify(e["term"])}">{_esc(e["term"])}</dt><dd>{body}{see}</dd>')
    out.append("</dl>")
    return "".join(out)


Macros.glossary_list = _glossary


_QC_PARTS = (("measures", "What it measures"), ("computed", "How it is computed"),
             ("reading", "How to read it"), ("causes", "What raises or lowers it"),
             ("caveats", "Caveats"), ("mriqc", "Compared with MRIQC"))


def _qc_group(self, group: str, heading: int = 4) -> str:
    """The quality measures of one group, each with its full explanation."""
    d = self._need("qc")
    if d is None:
        return ""
    items = [e for e in d["entries"] if e["group"] == group]
    if not items:
        self.problems.append(f"{self.page}: no quality measures in group {group!r}")
        return ""
    out = []
    for e in items:
        hid = "qc-" + slugify(e["key"].replace("*", "").replace(".", "-"))
        out.append(f'<div class="measure" data-generated><h{heading} id="{hid}">{_esc(e["title"])}</h{heading}>'
                   f'<p>{_esc(e["short"])}</p>')
        parts = [(label, e.get(k)) for k, label in _QC_PARTS if e.get(k)]
        if parts or e.get("references"):
            rows = "".join(f"<dt>{_esc(label)}</dt><dd>{_esc(text)}</dd>" for label, text in parts)
            if e.get("references"):
                rows += "<dt>References</dt><dd>" + "; ".join(_esc(r) for r in e["references"]) + "</dd>"
            out.append(f'<details class="disclosure measure-more"><summary>In detail</summary>'
                       f'<div class="disclosure-body"><dl class="measure-dl">{rows}</dl></div></details>')
        out.append("</div>")
    return "\n".join(out)


def _qc_intro(self, key: str) -> str:
    d = self._need("qc")
    if d is None:
        return ""
    for e in d["entries"]:
        if e["key"] == key:
            return _esc(e["short"]) + (" " + _esc(e["measures"]) if e.get("measures") else "")
    self.problems.append(f"{self.page}: no quality entry {key!r}")
    return ""


Macros.qc_group = _qc_group
Macros.qc_intro = _qc_intro


_SOURCE = {"parameters": "Parameters", "names": "Series name", "context": "Neighbouring series"}


def _rulebook(self) -> str:
    """The classifier's evidence, name by name."""
    d = self._need("classifier")
    if d is None:
        return ""
    out = []
    for c in d["candidates"]:
        title = c["label"] or c["name"]
        hid = "rule-" + slugify(c["name"].replace("/", "-"))
        out.append(f'<div class="measure" data-generated><h4 id="{hid}">{_esc(title)} '
                   f'<code>{_esc(c["name"])}</code></h4>')
        rows = []
        for e in c["evidence"]:
            w = e.get("weight")
            sign = "for" if (w or 0) > 0 else "against"
            wtxt = f"{w:+g}" if isinstance(w, (int, float)) else ""
            rows.append(f'<tr><td class="wrap">{_esc(e["why"])}</td><td>{_esc(_SOURCE.get(e["source"], e["source"]))}</td>'
                        f'<td class="num ev-{sign}">{_esc(wtxt)}</td></tr>')
        out.append('<div class="table-wrap"><table class="rule-table"><thead><tr><th>Evidence</th><th>From</th>'
                   f'<th>Weight</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></div>')
    return "\n".join(out)


Macros.rulebook = _rulebook


# -- the home page's dataset, as text ---------------------------------------
_SRC = {"file": "read from the recording", "bm": "written by BIDS Manager", "you": "your answer", "todo": "to answer"}


def _fmt(v) -> str:
    if isinstance(v, list):
        parts = [json.dumps(x, ensure_ascii=False) for x in v[:3]]
        return "[" + ", ".join(parts) + (", …" if len(v) > 3 else "") + "]"
    return json.dumps(v, ensure_ascii=False)


def _hero_card(cd: dict) -> str:
    rows = "".join(
        f'<div class="hc-row is-in"><span class="hc-kv"><span class="hc-key">"{_esc(r["key"])}":</span> '
        f'<span class="hc-val src-{r["src"]}">{_esc(_fmt(r["value"]))}</span></span>'
        f'<i class="hc-src src-{r["src"]}">{_SRC[r["src"]]}</i></div>' for r in cd["rows"])
    return (f'<div class="hero-card"><p class="hc-file"><span>{_esc(cd["file"])}</span></p>'
            f'<div class="hc-body">{{{rows}}}</div></div>')


def _hero_dataset(self, card: str = "bold") -> str:
    """The dataset the hero assembles, with one sidecar, for readers who see
    no animation."""
    d = self._need("hero")
    if d is None:
        return ""
    lines = []
    for ln in d["tree"]:
        folder = (ln["folder"] + "      ")[:6] if ln["folder"] else ("      " if "│" in ln["branch"] else "")
        name = f'<span class="tl-file" style="--kc:var(--k-{["mri", "mrs", "pet", "eeg", "meg", "physio", "eye"][ln["k"]]})">{_esc(ln["name"])}</span>' \
            if ln["k"] < 7 else _esc(ln["name"])
        more = f'<span class="tl-more">  {_esc(ln["more"])}</span>' if ln.get("more") else ""
        js = '<span class="tl-json">  .json</span>' if ln.get("json") else ""
        lines.append(f'<span class="tl-branch">{_esc(ln["branch"] + folder)}</span>{name}{more}{js}')
    tree = '<div class="code"><pre><code>' + "\n".join(lines) + "</code></pre></div>"
    return (f'<div class="hero-result" data-generated>{tree}{_hero_card(d["cards"][card])}</div>')


Macros.hero_dataset = _hero_dataset


# -- naming: one series judged three ways -----------------------------------
_DECIDED = {
    "agreement": "The parameters and dcm2niix's guess agree, so that name is used and confirmed.",
    "parameters": "The parameters are sure (at or above 0.8) and dcm2niix's guess says something else: the parameters win, and the row notes what dcm2niix suggested.",
    "dcm2niix": "The parameters are unsure, and the series name agrees with dcm2niix: dcm2niix's guess is used, and the row is marked to check.",
    "names": "The parameters are unsure and there is no dcm2niix guess: the series name decides, and the row is marked to check.",
}


def _naming_demo(self) -> str:
    """Real series of the advanced MRI sample, each judged by its name, by
    dcm2niix and by its acquisition parameters; with JavaScript, a stepper."""
    d = self._need("naming")
    if d is None:
        return ""
    tabs, panels = [], []
    for i, e in enumerate(d["examples"]):
        pid = f"judge-{i}"
        wrong = e["by_name"] != e["chosen"]
        tabs.append(f'<button type="button" role="tab" id="{pid}-tab" aria-controls="{pid}" aria-selected="{"true" if i == 0 else "false"}">'
                    f'<code>{_esc(e["series"])}</code></button>')
        params = "".join(f"<dt>{_esc(k)}</dt><dd>{_esc(v)}</dd>" for k, v in e["parameters"].items() if v)
        top = max([x["points"] for x in e["evidence"] + e["runner_up"]] + [1])
        def bars(items, cls):
            return "".join(
                f'<li class="{cls}"><span class="ev-bar" style="--w:{x["points"] / top * 100:.0f}%"></span>'
                f'<span class="ev-text">{_esc(x["text"])}{"" if cls == "ev-for" else " (for " + _esc(x["for"]) + ")"}</span><span class="ev-src">{_esc(x["source"])}</span>'
                f'<span class="ev-pts">+{x["points"]:g}</span></li>' for x in items)
        verdict = lambda v, good: f'<b class="verdict {"is-right" if good else "is-wrong"}">{_esc(v) or "no guess"}</b>'  # noqa: E731
        panels.append(f'''<div class="judge-panel" role="tabpanel" id="{pid}" aria-labelledby="{pid}-tab"{"" if i == 0 else " data-hidden"}>
<p class="judge-series"><span>Series name, as typed at the scanner</span><code>{_esc(e["series"])}</code></p>
<ol class="judge-steps">
<li class="judge-step"><p class="judge-h">1. The name alone</p><p>Matching the name against common sequence names, as a converter that trusts names would.</p>{verdict(e["by_name"], e["by_name"] == e["chosen"])}</li>
<li class="judge-step"><p class="judge-h">2. dcm2niix's guess</p><p>From a few strings in the DICOM header, such as the scanning sequence and the protocol.</p>{verdict(e["by_dcm2niix"], e["by_dcm2niix"] == e["chosen"])}</li>
<li class="judge-step"><p class="judge-h">3. The acquisition parameters</p><p>What the scanner recorded about how it acquired the series:</p><dl class="judge-params">{params}</dl>
<p>The evidence the classifier counted for its name, and for the next best:</p><ul class="judge-ev">{bars(e["evidence"], "ev-for")}{bars(e["runner_up"], "ev-alt")}</ul>{verdict(e["by_parameters"] + f' · confidence {e["confidence"]:.2f}', True)}</li>
<li class="judge-step judge-decision"><p class="judge-h">4. The decision</p><p>{_esc(_DECIDED.get(e["decided_by"], ""))}{" The name typed at the scanner is not used: it is wrong." if wrong else ""}</p><b class="verdict is-final"><code>{_esc(e["bids_name"])}</code></b></li>
</ol>
</div>''')
    return (f'<div class="judge" data-judge data-generated><div class="judge-tabs" role="tablist" aria-label="Example series">{"".join(tabs)}</div>'
            f'{"".join(panels)}</div>')


Macros.naming_demo = _naming_demo


# -- interactive exercises of the BIDS chapter -------------------------------
def _teach_builder(self) -> str:
    """Build a file name from its entities. The facts (which entities, in which
    order, required or not, label or index) are the schema's; JavaScript makes
    it interactive, and without it a table gives the same facts."""
    d = self._need("teach")
    if d is None:
        return ""
    data = json.dumps({"kinds": d["kinds"]}, ensure_ascii=False).replace("</", "<\\/")
    rows = []
    for k in d["kinds"]:
        ents = ", ".join(("<b>" + _esc(e["key"]) + "</b>" if e["required"] else _esc(e["key"])) for e in k["entities"])
        rows.append(f"<tr><td><code>{_esc(k['datatype'])}/</code></td><td><code>{_esc(k['suffix'])}</code></td><td>{ents}</td></tr>")
    static = ('<div class="teach-static table-wrap"><table><thead><tr><th>Folder</th><th>Suffix</th>'
              '<th>Entities it may carry, in order (required in bold)</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")
    return (f'<div class="teach teach-builder" data-teach="builder" data-generated>'
            f'<script type="application/json">{data}</script>'
            f'<p class="teach-kicker">Try it: build a file name</p>{static}</div>')


def _teach_quiz(self) -> str:
    d = self._need("teach")
    if d is None:
        return ""
    items = []
    for i, q in enumerate(d["quiz"]):
        verdict = "Valid" if q["ok"] else "Not valid"
        why = _esc(q["explain"])
        schema_says = ("" if q["ok"] else '<span class="tq-schema">The schema check says: ' +
                       _esc("; ".join(q["problems"])) + "</span>")
        items.append(f'<li class="tq-item" data-ok="{"1" if q["ok"] else "0"}"><code class="tq-name">{_esc(q["name"])}</code>'
                     f'<span class="tq-in">in <code>{_esc(q["datatype"])}/</code></span>'
                     f'<span class="tq-buttons" hidden><button type="button" data-answer="1">Valid</button>'
                     f'<button type="button" data-answer="0">Not valid</button></span>'
                     f'<details class="tq-answer"><summary>Answer</summary><p><b>{verdict}.</b> {why} {schema_says}</p></details></li>')
    return (f'<div class="teach teach-quiz" data-teach="quiz" data-generated><p class="teach-kicker">Try it: valid or not?</p>'
            f'<ol class="tq-list">{"".join(items)}</ol><p class="tq-score" aria-live="polite" hidden></p></div>')


def _teach_place(self) -> str:
    d = self._need("teach")
    if d is None:
        return ""
    data = json.dumps({"place": d["place"], "folders": d["folders"]}, ensure_ascii=False).replace("</", "<\\/")
    rows = "".join(f"<tr><td><code>{_esc(p['name'])}</code></td><td><code>{_esc(p['folder'][0])}/</code></td></tr>" for p in d["place"])
    static = ('<div class="teach-static table-wrap"><table><thead><tr><th>File</th><th>Folder</th></tr></thead><tbody>'
              + rows + "</tbody></table></div>")
    return (f'<div class="teach teach-place" data-teach="place" data-generated><script type="application/json">{data}</script>'
            f'<p class="teach-kicker">Try it: which folder?</p>{static}</div>')


def _teach_inherit(self) -> str:
    """Two BOLD runs and the sidecars that apply to each: the inheritance rule
    shown on one small dataset."""
    files = {
        "top": ("task-rest_bold.json", {"TaskName": "rest", "RepetitionTime": 2.0, "EchoTime": 0.03}),
        "sub01": ("sub-01/func/sub-01_task-rest_bold.json", {"RepetitionTime": 2.5}),
    }
    def table(rows):
        return ('<table><thead><tr><th>Field</th><th>Value</th><th>From</th></tr></thead><tbody>' +
                "".join(f"<tr><td><code>{_esc(k)}</code></td><td><code>{_esc(json.dumps(v))}</code></td><td>{_esc(src)}</td></tr>"
                        for k, v, src in rows) + "</tbody></table>")
    top, sub = files["top"][1], files["sub01"][1]
    eff01 = [(k, sub.get(k, v), "its own sidecar (wins)" if k in sub else "the top-level sidecar") for k, v in top.items()]
    eff02 = [(k, v, "the top-level sidecar") for k, v in top.items()]
    tree = ('<pre class="ti-tree"><span class="ti-code"><span class="ti-file" data-ti="top">task-rest_bold.json</span>   {"TaskName": "rest", "RepetitionTime": 2.0, "EchoTime": 0.03}\n'
            'sub-01/func/\n  <button type="button" class="ti-run" data-ti="r01">sub-01_task-rest_bold.nii.gz</button>\n'
            '  <span class="ti-file" data-ti="sub01">sub-01_task-rest_bold.json</span>   {"RepetitionTime": 2.5}\n'
            'sub-02/func/\n  <button type="button" class="ti-run" data-ti="r02">sub-02_task-rest_bold.nii.gz</button>   (no sidecar of its own)</span></pre>')
    return (f'<div class="teach teach-inherit" data-teach="inherit" data-generated><p class="teach-kicker">Try it: which values apply?</p>'
            f'{tree}<div class="ti-panels"><div class="ti-panel" data-for="r01"><p>For <code>sub-01_task-rest_bold.nii.gz</code>:</p>{table(eff01)}</div>'
            f'<div class="ti-panel" data-for="r02"><p>For <code>sub-02_task-rest_bold.nii.gz</code>:</p>{table(eff02)}</div></div></div>')


Macros.teach_builder = _teach_builder
Macros.teach_quiz = _teach_quiz
Macros.teach_place = _teach_place
Macros.teach_inherit = _teach_inherit


# -- the workflow, and what runs it ------------------------------------------
def _workflow(self) -> str:
    """The stages of BIDS Manager and the tools each drives. Without
    JavaScript it reads as a list of stages; with it, picking a kind of
    recording lights the path that kind takes."""
    d = self._need("workflow")
    if d is None:
        return ""
    names = {k["id"]: k["name"] for k in d["kinds"]}
    kinds = "".join(f'<button type="button" data-kind="{k["id"]}" style="--kc: var(--k-{k["id"]})" aria-pressed="false">{_esc(k["name"])}</button>'
                    for k in d["kinds"])
    stages = []
    for i, st in enumerate(d["stages"]):
        steps = "".join(
            f'<li class="wf-step{" is-own" if s.get("own") else ""}" data-kinds="{" ".join(s["kinds"])}">'
            f'<b>{_esc(s["name"])}</b><span>{_esc(s["does"])}</span>'
            f'<i class="wf-for">{_esc(", ".join(names[k] for k in s["kinds"])) if len(s["kinds"]) < len(names) else "every kind"}</i></li>'
            for s in st["steps"])
        stages.append(f'<li class="wf-stage" data-stage="{st["id"]}"><p class="wf-num">{i + 1:02d}</p>'
                      f'<h3 class="wf-title"><a href="{self.link(st["link"])}">{_esc(st["title"])}</a></h3>'
                      f'<p class="wf-what">{_esc(st["what"])}</p><ul class="wf-steps">{steps}</ul></li>')
    legend = ('<p class="wf-legend"><span class="wf-key is-own"></span> done by BIDS Manager itself '
              '<span class="wf-key"></span> an established tool it installs and drives</p>')
    return (f'<div class="workflow" data-workflow data-generated><div class="wf-kinds" role="group" aria-label="Follow one kind of recording">'
            f'<span class="wf-kinds-label">Follow</span>{kinds}<button type="button" data-kind="" aria-pressed="true">everything</button></div>'
            f'<ol class="wf-stages">{"".join(stages)}</ol>{legend}</div>')


Macros.workflow = _workflow


# -- what the installer does --------------------------------------------------
def _installer_steps(self) -> str:
    """The installers' steps, per system: a list without JavaScript; with it,
    a row of steps that fill in one after the other, and a switch of system."""
    d = self._need("installer")
    if d is None:
        return ""
    oses = [("macos", "macOS"), ("windows", "Windows"), ("linux", "Linux")]
    sw = "".join(f'<button type="button" data-os="{o}" aria-pressed="{"true" if i == 0 else "false"}">{n}</button>'
                 for i, (o, n) in enumerate(oses))
    items = []
    for i, st in enumerate(d["steps"]):
        texts = ""
        for o, _n in oses:
            t = st.get(o) or st.get("all", "")
            extra = st.get(f"{o}_extra", "")
            texts += f'<p class="is-steps-text" data-os="{o}">{_md(t)}{(" " + _md(extra)) if extra else ""}</p>'
        items.append(f'<li class="is-step"><span class="is-n">{i + 1}</span><p class="is-title">{_esc(st["title"])}</p>{texts}</li>')
    return (f'<div class="installer-steps" data-installer data-generated><div class="is-os" role="group" aria-label="Your system">{sw}</div>'
            f'<ol class="is-list">{"".join(items)}</ol></div>')


Macros.installer_steps = _installer_steps


# -- the About page's comparison --------------------------------------------
def _compare(self) -> str:
    d = self._need("compare")
    if d is None:
        return ""
    cards = "".join(
        f'<li class="cmp-case"><p class="cmp-title">{_esc(c["title"])}</p>'
        f'<p class="cmp-side cmp-alone"><b>With a converter alone</b>{_esc(c["alone"])}</p>'
        f'<p class="cmp-side cmp-bm"><b>With BIDS Manager</b>{_esc(c["bm"])} <a href="{self.link(c["link"])}">See it</a></p></li>'
        for c in d["cases"])
    return ('<div class="compare" data-compare data-generated>'
            '<div class="cmp-switch" role="group" aria-label="Show"><button type="button" data-side="alone" aria-pressed="true">With a converter alone</button>'
            '<button type="button" data-side="bm" aria-pressed="false">With BIDS Manager</button></div>'
            f'<ul class="cmp-cases">{cards}</ul></div>')


Macros.compare = _compare

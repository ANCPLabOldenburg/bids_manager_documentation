"""Read the installed BIDS Manager and write the reference data the pages render.

    environments/bids-manager/bin/python bids_manager_documentation/tools/reference/extract.py

Writes ``data/*.json``:

- ``cli.json``         every ``bidsmgr-*`` argument parser: usage, arguments, choices, defaults, help;
- ``settings.json``    every page of the Settings dialog, read from the dialog's own widgets
                       (the hand-built pages) or from the settings models it draws (the generated ones);
- ``columns.json``     the inspection table's columns and the descriptions Manage columns shows;
- ``qc.json``          every entry of ``bidsmgr.qc.explain``;
- ``classifier.json``  the classifier's settings and the names its rulebook can give;
- ``themes.json``      the nineteen themes with their swatches;
- ``keys.json``        the viewer actions with their keys and gestures;
- ``tools.json``       the Editor's Tools menu, as the menu itself lists it;
- ``version.json``     the version and commit this was read from.

Text is quoted as the application writes it, with two exceptions recorded in
``notes``: an em or en dash becomes a colon or a comma (the site uses none),
and the tables do not mention iEEG, which the documentation does not cover.
Settings are isolated (guard 8f): nothing here touches the user's own.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["BIDSMGR_NO_UPDATE_CHECK"] = "1"

SITE = Path(__file__).resolve().parent.parent.parent
DATA = SITE / "data"
SETTINGS_DIR = "/private/tmp/bm_docs/settings/reference"
NOTES: list[str] = []


_TM = None


def clean(text) -> str:
    """The site's punctuation rules applied to quoted text (see module doc)."""
    if text is None:
        return ""
    s = re.sub(r"<br\s*/?>|</p>|</li>", " ", str(text))
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s*[—―]\s*", ": ", s)
    s = re.sub(r"\s+–\s+", ", ", s)
    s = s.replace("–", "-")
    s = re.sub(r"EEG\s*/\s*iEEG", "EEG", s)
    s = re.sub(r"EEG, iEEG", "EEG", s)
    s = re.sub(r"\s*/\s*iEEG\b", "", s)
    s = re.sub(r",?\s*\biEEG\b,?", "", s)
    return " ".join(s.split())


def write(name: str, data) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / f"{name}.json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
    print(f"data/{name}.json")


# --------------------------------------------------------------------- cli
VERBS = [
    ("bidsmgr", "bidsmgr.main", "Open the application."),
    ("bidsmgr-create", "bidsmgr.cli.create", ""),
    ("bidsmgr-adopt", "bidsmgr.cli.adopt", ""),
    ("bidsmgr-project", "bidsmgr.cli.project", ""),
    ("bidsmgr-scan", "bidsmgr.cli.scan", ""),
    ("bidsmgr-classify", "bidsmgr.cli.classify", ""),
    ("bidsmgr-rebuild", "bidsmgr.cli.rebuild", ""),
    ("bidsmgr-convert", "bidsmgr.cli.convert", ""),
    ("bidsmgr-metadata", "bidsmgr.cli.metadata", ""),
    ("bidsmgr-validate", "bidsmgr.cli.validate", ""),
    ("bidsmgr-deface", "bidsmgr.cli.deface", ""),
    ("bidsmgr-anonymise", "bidsmgr.cli.anonymise", ""),
    ("bidsmgr-sidecars", "bidsmgr.cli.sidecars", ""),
    ("bidsmgr-qc", "bidsmgr.cli.qc", ""),
    ("bidsmgr-view", "bidsmgr.cli.view", ""),
]


class _Captured(Exception):
    def __init__(self, parser):
        self.parser = parser


def cli() -> dict:
    import importlib

    orig = argparse.ArgumentParser.parse_args
    orig_known = argparse.ArgumentParser.parse_known_args

    def grab(self, *a, **kw):
        raise _Captured(self)

    argparse.ArgumentParser.parse_args = grab
    argparse.ArgumentParser.parse_known_args = grab
    verbs = []
    try:
        for prog, module, fallback in VERBS:
            mod = importlib.import_module(module)
            parser = None
            if hasattr(mod, "build_parser"):
                parser = mod.build_parser()
            else:
                try:
                    mod.main([])
                except _Captured as c:
                    parser = c.parser
                except SystemExit:
                    pass
            if parser is None:
                raise SystemExit(f"could not read the parser of {prog}")
            parser.prog = prog
            verbs.append(_parser_data(prog, parser, fallback))
    finally:
        argparse.ArgumentParser.parse_args = orig
        argparse.ArgumentParser.parse_known_args = orig_known
    return {"verbs": verbs}


def _parser_data(prog, parser, fallback) -> dict:
    fmt = parser._get_formatter()
    usage = parser.format_usage().replace("usage: ", "").strip()
    args = []
    for action in parser._actions:
        if isinstance(action, argparse._HelpAction):
            args.append({"flags": ["-h", "--help"], "dest": "help", "help": "Show the help and stop.",
                         "positional": False})
            continue
        if action.help == argparse.SUPPRESS:
            continue
        help_text = action.help or ""
        if "%(" in help_text:
            try:
                help_text = fmt._expand_help(action)
            except Exception:  # noqa: BLE001
                pass
        default = action.default
        if default is argparse.SUPPRESS or isinstance(action, (argparse._StoreTrueAction,
                                                                argparse._StoreFalseAction)):
            default = None
        if isinstance(default, Path):
            default = str(default)
        if not isinstance(default, (str, int, float, bool, type(None), list)):
            default = str(default)
        metavar = action.metavar
        if isinstance(metavar, tuple):
            metavar = " ".join(metavar)
        if metavar is None and action.option_strings and action.nargs != 0:
            metavar = action.dest.upper()
        args.append({
            "flags": list(action.option_strings),
            "dest": action.dest,
            "positional": not action.option_strings,
            "metavar": metavar,
            "nargs": action.nargs if isinstance(action.nargs, (int, str, type(None))) else str(action.nargs),
            "choices": [str(c) for c in action.choices] if action.choices else None,
            "default": default,
            "required": bool(getattr(action, "required", False)),
            "help": clean(help_text),
        })
    desc = clean(parser.description or fallback)
    return {"prog": prog, "usage": " ".join(usage.split()), "description": desc,
            "epilog": clean(parser.epilog or ""), "arguments": args}


# ---------------------------------------------------------------- settings
def _model_fields(model_cls, instance) -> list:
    import typing

    items = []
    for name, info in model_cls.model_fields.items():
        extra = info.json_schema_extra or {}
        value = getattr(instance, name)
        if hasattr(value, "model_fields"):
            continue
        if not info.title:
            continue
        ann = info.annotation
        choices = None
        if typing.get_origin(ann) is typing.Literal:
            labels = extra.get("labels") or {}
            choices = [labels.get(c, str(c)) for c in typing.get_args(ann)]
            value = labels.get(value, value)
        if isinstance(value, bool):
            value = "On" if value else "Off"
        unit = extra.get("unit", "")
        if isinstance(value, float):
            value = f"{value:g}"
        default = f"{value} {unit}".strip() if value not in ("", None, [], {}) else ""
        if extra.get("zero") and str(getattr(instance, name)) in ("0", "0.0"):
            default = extra["zero"]
        rng = extra.get("range")
        tip = clean(info.description or "")
        if rng and not choices:
            tip = (tip + f" Range {rng[0]:g} to {rng[1]:g}{(' ' + unit) if unit else ''}.").strip()
        items.append({"label": clean(info.title), "tip": tip, "default": clean(default),
                      "choices": choices, "key": name})
    return items


def _model_page(title, description, sections) -> dict:
    groups = []
    for sec_cls, inst in sections:
        cfg = getattr(sec_cls, "model_config", {}) or {}
        groups.append({"title": clean(cfg.get("title", "")), "hint": clean(sec_cls.__doc__ or ""),
                       "items": _model_fields(sec_cls, inst)})
    return {"title": title, "description": clean(description), "groups": groups}


def settings(app) -> dict:
    from PyQt6.QtWidgets import (QAbstractButton, QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout,
                                 QGroupBox, QLabel, QLineEdit, QListWidget, QPushButton, QRadioButton,
                                 QSpinBox, QTableWidget, QWidget)

    from bidsmgr.gui.app_settings import AppSettings
    from bidsmgr.gui.settings_dialog import SettingsDialog

    dlg = SettingsDialog(AppSettings.load())
    stack = dlg._stack
    pages = []
    for i, title in enumerate(dlg.page_titles()):
        desc = dlg._nav.item(i).data(0x0101) or ""
        page = stack.widget(i)
        if title in ("Classification", "Quality control", "Viewer", "Viewer shortcuts"):
            pages.append({"title": title, "description": clean(desc), "groups": [], "generated": True})
            continue
        groups = [{"title": "", "hint": "", "items": []}]
        seen = set()

        def field_item(label_text, w):
            tip = clean(w.toolTip())
            if isinstance(w, QComboBox):
                choices = [clean(w.itemText(k)) for k in range(w.count())]
                return {"label": clean(label_text), "tip": tip, "default": clean(w.currentText()),
                        "choices": choices}
            if isinstance(w, (QSpinBox, QDoubleSpinBox)):
                return {"label": clean(label_text), "tip": tip,
                        "default": clean(w.text()), "choices": None}
            if isinstance(w, QLineEdit):
                return {"label": clean(label_text), "tip": tip,
                        "default": clean(w.text() or w.placeholderText()), "choices": None}
            if isinstance(w, (QCheckBox, QRadioButton)):
                item = {"label": clean(label_text or w.text()), "tip": tip,
                        "default": "On" if w.isChecked() else "Off", "choices": None}
                if label_text and w.text() and clean(w.text()) != clean(label_text):
                    item["control"] = clean(w.text())
                return item
            return None

        def visit(widget, form_label=None):
            if widget is None or id(widget) in seen:
                return
            seen.add(id(widget))
            if isinstance(widget, QGroupBox):
                groups.append({"title": clean(widget.title()), "hint": "", "items": []})
                if widget.isCheckable():
                    groups[-1]["items"].append({"label": clean(widget.title()), "tip": clean(widget.toolTip()),
                                                "default": "On" if widget.isChecked() else "Off",
                                                "choices": None})
                lay = widget.layout()
                if lay:
                    visit_layout(lay)
                # Rows after the box belong to the page again, not to the box.
                groups.append({"title": "", "hint": "", "items": []})
                return
            if isinstance(widget, (QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox, QRadioButton)):
                it = field_item(form_label or "", widget)
                if it and it["label"]:
                    groups[-1]["items"].append(it)
                return
            if isinstance(widget, QTableWidget):
                cols = [clean(widget.horizontalHeaderItem(c).text()) for c in range(widget.columnCount())
                        if widget.horizontalHeaderItem(c)]
                groups[-1]["items"].append({"label": clean(form_label or "Table"), "tip": "Columns: " + ", ".join(cols),
                                            "default": "", "choices": None, "table": True})
                return
            if isinstance(widget, QLabel):
                name = widget.objectName()
                text = clean(widget.text())
                if name in ("settings-section", "dlg-section", "settings-group-title", "section-title") and text:
                    groups.append({"title": text, "hint": "", "items": []})
                elif name in ("dlg-hint", "settings-hint", "hint") and text and not groups[-1]["items"]:
                    groups[-1]["hint"] = (groups[-1]["hint"] + " " + text).strip()
                return
            if isinstance(widget, (QPushButton, QListWidget)):
                return
            lay = widget.layout()
            if lay is not None:
                visit_layout(lay)
            else:
                for child in widget.findChildren(QWidget, options=Qt_direct()):
                    visit(child)

        def visit_layout(lay):
            if isinstance(lay, QFormLayout):
                for r in range(lay.rowCount()):
                    li = lay.itemAt(r, QFormLayout.ItemRole.LabelRole)
                    fi = lay.itemAt(r, QFormLayout.ItemRole.FieldRole)
                    si = lay.itemAt(r, QFormLayout.ItemRole.SpanningRole)
                    label = li.widget().text() if li and li.widget() and isinstance(li.widget(), QLabel) else None
                    if label:
                        label = label.rstrip(":")
                    for item in (fi, si):
                        if item is None:
                            continue
                        if item.widget():
                            visit(item.widget(), label)
                        elif item.layout():
                            sub = item.layout()
                            first = True
                            for k in range(sub.count()):
                                w = sub.itemAt(k).widget()
                                if w is not None:
                                    visit(w, label if first else None)
                                    if isinstance(w, (QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox)):
                                        first = False
                                elif sub.itemAt(k).layout():
                                    visit_layout(sub.itemAt(k).layout())
                return
            for k in range(lay.count()):
                item = lay.itemAt(k)
                if item.widget():
                    visit(item.widget())
                elif item.layout():
                    visit_layout(item.layout())

        visit(page)
        groups = [g for g in groups if g["items"] or g["title"]]
        for g in groups:
            if g["title"] == clean(title):
                g["title"] = ""
        pages.append({"title": title, "description": clean(desc), "groups": groups})

    # The generated pages, from the models they draw.
    from bidsmgr.classifier.acquisition.config import ClassifierConfig
    from bidsmgr.viz.settings import QC_SECTIONS, VIEWER_SECTIONS, VizSettings

    cc = ClassifierConfig()
    vs = VizSettings()
    for p in pages:
        if p["title"] == "Classification":
            p["groups"] = _model_page("", "", [(type(getattr(cc, n)), getattr(cc, n)) for n in
                                               ("general", "weights", "anatomy", "gradient_echo", "echoes",
                                                "series", "contrast")])["groups"]
        elif p["title"] == "Quality control":
            p["groups"] = _model_page("", "", [(type(getattr(vs, n)), getattr(vs, n)) for n in QC_SECTIONS])["groups"]
        elif p["title"] == "Viewer":
            p["groups"] = _model_page("", "", [(type(getattr(vs, n)), getattr(vs, n)) for n in VIEWER_SECTIONS])["groups"]
        elif p["title"] == "Viewer shortcuts":
            p["groups"] = []
    dlg.deleteLater()
    return {"pages": pages}


def Qt_direct():
    from PyQt6.QtCore import Qt
    return Qt.FindChildOption.FindDirectChildrenOnly


# ------------------------------------------------------------- the others
def columns() -> dict:
    from bidsmgr.gui.models import COLUMN_DESCRIPTIONS, COLUMNS, MANDATORY_COLUMN_KEYS

    rows = []
    for c in COLUMNS:
        rows.append({"key": c.key, "header": c.header or {"include": "(tick)", "status": "(state)"}.get(c.key, ""),
                     "tsv": c.df_column or "", "editable": "Yes" if c.editable else "No",
                     "shown": "Always" if c.key in MANDATORY_COLUMN_KEYS else ("Yes" if c.default_visible else "No"),
                     "description": clean(COLUMN_DESCRIPTIONS.get(c.key, ""))})
    return {"rows": rows}


def tsv_columns() -> dict:
    """The full inventory TSV's columns, in order, from a real scan."""
    from bidsmgr.cli import scan as S
    order = getattr(S, "_unified_column_order", None)
    out = []
    try:
        cols = order(None) if callable(order) else []
    except Exception:  # noqa: BLE001
        cols = []
    return {"columns": out or list(cols)}


def qc() -> dict:
    from bidsmgr.qc import explain as E

    entries = []
    for name in dir(E):
        if not name.startswith("_") or not name.isupper() and not name[1:].isupper():
            continue
        table = getattr(E, name)
        if not isinstance(table, dict):
            continue
        group = name.strip("_").lower()
        for key, ex in table.items():
            if not hasattr(ex, "title"):
                continue
            entries.append({"group": group, "key": key, "title": clean(ex.title), "short": clean(ex.short),
                            "measures": clean(ex.measures), "computed": clean(ex.computed),
                            "reading": clean(ex.reading), "causes": clean(ex.causes),
                            "caveats": clean(ex.caveats), "mriqc": clean(ex.mriqc),
                            "references": [clean(r) for r in ex.references]})
    return {"entries": entries}


def classifier() -> dict:
    from bidsmgr.classifier.acquisition.config import ClassifierConfig

    cc = ClassifierConfig()
    page = _model_page("", "", [(type(getattr(cc, n)), getattr(cc, n)) for n in
                                ("general", "weights", "anatomy", "gradient_echo", "echoes", "series", "contrast")])
    rb_path = Path(sys.modules["bidsmgr.classifier.acquisition.config"].__file__).parent / "rulebook.json"
    rb = json.loads(rb_path.read_text())
    cands = []
    for name, c in (rb.get("candidates") or {}).items():
        datatype, _, suffix = name.partition("/")
        ev = []
        for e in c.get("evidence", []):
            test = ""
            if "is" in e:
                test = "is" if e["is"] else "is not"
            for k in ("in", "range", "min", "max", "matches", "any", "equals"):
                if k in e:
                    test = f"{k} {e[k]}"
            ev.append({"source": e.get("source", ""), "feature": e.get("feature", e.get("pattern", "")),
                       "test": clean(test), "weight": e.get("weight"), "why": clean(e.get("why", ""))})
        cands.append({"name": name, "datatype": datatype, "suffix": suffix,
                      "label": clean(c.get("label", "")), "evidence": ev})
    count = sum(len(g["items"]) for g in page["groups"])
    return {"groups": page["groups"], "settings": count, "rulebook_about": clean(rb.get("about", "")),
            "rulebook_version": rb.get("version"), "candidates": cands}


def themes() -> dict:
    from bidsmgr.gui.theme_manager import PALETTES, THEMES

    out = []
    for t in THEMES:
        p = PALETTES[t.id]
        out.append({"id": t.id, "label": t.label, "group": t.group, "dark": t.dark, "partner": t.partner,
                    "description": clean(t.description),
                    "swatch": [p["bg"], p["surface"], p["text"], p["accent"], p["success"], p["warning"], p["error"]]})
    return {"themes": out}


def version() -> dict:
    import bidsmgr
    repo = Path(bidsmgr.__file__).resolve().parent.parent
    try:
        commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], text=True).strip()
        dirty = bool(subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain", "--", "bidsmgr"],
                                             text=True).strip())
    except Exception:  # noqa: BLE001
        commit, dirty = "", False
    return {"version": bidsmgr.__version__, "commit": commit, "dirty": dirty}



def tools(app) -> dict:
    """The Editor's Tools menu: its groups and items, with their tooltips."""
    from bidsmgr.gui.main_window import MainWindow
    from bidsmgr.gui.theme_manager import ThemeManager  # noqa: F401
    win = MainWindow(_TM)
    menu = win.editor._tools_menu
    groups, cur = [], None
    for act in menu.actions():
        if act.isSeparator():
            continue
        text = act.text()
        if not act.isEnabled() and text.isupper():
            cur = {"title": text.capitalize(), "items": []}
            groups.append(cur)
            continue
        if cur is None:
            cur = {"title": "", "items": []}
            groups.append(cur)
        cur["items"].append({"label": clean(text.replace("&", "")), "tip": clean(act.toolTip())})
    win.close()
    return {"groups": groups}


def _kinds(A, a) -> set:
    """The viewers an action belongs to. ``kinds_of`` gives one viewer for a
    condition such as ``volume || traces || spectrum``; each alternative of
    the condition is judged on its own here, and the answers joined."""
    import dataclasses
    if "||" not in (a.when or ""):
        return set(A.kinds_of(a))
    out = set()
    for alt in a.when.split("||"):
        out |= set(A.kinds_of(dataclasses.replace(a, when=alt.strip(), shown="", checked="")))
    return out


def keys() -> dict:
    """The viewers' actions with their keys, as each system writes them,
    and the mouse gestures of each kind of canvas."""
    from bidsmgr.viz import actions as A, inputmap as I, keynames as K
    rows = []
    for a in A.ACTIONS:
        rows.append({
            "id": a.id, "title": clean(a.title), "label": clean(a.label), "category": a.category,
            "help": clean(a.help), "keys_mac": K.keys(a.keys, mac=True),
            "keys_other": K.keys(a.keys, mac=False),
            "kinds": sorted(_kinds(A, a)),
        })
    tool_names = {"slice": I.SLICE_TOOLS, "render": I.RENDER_TOOLS, "traces": I.TRACES_TOOLS}
    gestures = {}
    for canvas, all_g in I.GESTURES.items():
        out = []
        for g in all_g:
            tool = I.binding(canvas, g)
            if tool == "none":
                continue
            out.append({"gesture": g, "mac": K.gesture(g, mac=True), "other": K.gesture(g, mac=False),
                        "tool": tool, "does": clean(tool_names[canvas].get(tool, tool))})
        gestures[canvas] = out
    return {"actions": rows, "gestures": gestures}

def main() -> int:
    from PyQt6.QtCore import QLocale, QSettings
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, SETTINGS_DIR)
    QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedKingdom))
    import shutil
    shutil.rmtree(SETTINGS_DIR, ignore_errors=True)
    from bidsmgr.gui.bootstrap import create_application
    app, _tm = create_application("dark")
    global _TM
    _TM = _tm
    v = version()
    if v["version"] != "1.5.2":
        raise SystemExit(f"BIDS Manager reports {v['version']}, not 1.5.2: stopping")
    write("version", v)
    write("cli", cli())
    write("settings", settings(app))
    write("columns", columns())
    write("qc", qc())
    write("classifier", classifier())
    write("themes", themes())
    write("keys", keys())
    write("tools", tools(app))
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    raise SystemExit(main())

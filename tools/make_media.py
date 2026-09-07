"""Render documentation screenshots and clips from the real application.

Every asset this produces is the actual Qt widget drawn by the actual code,
using real inventory data. Nothing here is a mock-up, and nothing is drawn by
hand: if a control is renamed in the application, the next run of this script
shows the new name, which is the whole point of generating rather than
photographing.

    ../environments/bids-manager/bin/python tools/make_media.py --list
    ../environments/bids-manager/bin/python tools/make_media.py inventory-multimodal
    ../environments/bids-manager/bin/python tools/make_media.py --all

Images are written for both themes as ``<id>_dark.png`` and ``<id>_light.png``,
which is the pair the site's ``themed-img`` component expects.

Video is optional and needs an encoder. There is none on this machine by
default, so ``--ffmpeg PATH`` takes one; the self-contained binary inside the
``imageio-ffmpeg`` wheel works without installing anything:

    pip download imageio-ffmpeg -d /tmp/w --no-deps
    unzip -q /tmp/w/*.whl -d /tmp/ff
    chmod +x /tmp/ff/imageio_ffmpeg/binaries/ffmpeg-*

Clips are assembled from rendered frames rather than captured from a screen, so
they show a sequence of real states with no cursor. For anything where the
pointer itself is the subject, record the screen instead.

Qt runs under the offscreen platform, so this needs no display. The one thing
it cannot draw is the 3-D view, which needs a real OpenGL context.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# Render at 2x by default. Qt scales the whole widget tree, fonts included, so
# the result is a true high-resolution image rather than an upscaled one, and
# it stays sharp on the displays most people read documentation on. Set
# --scale 1 for the logical size.
os.environ.setdefault("QT_SCALE_FACTOR", os.environ.get("DOCS_MEDIA_SCALE", "2"))

import pandas as pd  # noqa: E402
from PyQt6.QtWidgets import (  # noqa: E402
    QAbstractItemView, QApplication, QHeaderView, QTableView,
)

DOCS = Path(__file__).resolve().parent.parent
OUT = DOCS / "assets" / "features"

# Inventories produced by real scans of the sample data. Regenerate them with
# bidsmgr-scan if they are missing; the paths are the test outputs the project
# already keeps.
DATA = Path("/Users/karelo/Development/datasets/BIDS_Manager/bids_manager_outputs")
# Converted BIDS datasets, used for the Editor and validation shots. Real
# output from real runs, so the findings on them are real findings.
BIDS = DATA / "testing"

# ``ds_structural_demo`` is the one fixture that is deliberately broken, and it
# is broken by hand rather than by the software, because that is how structural
# errors actually happen. Rebuild it from the converted multimodal dataset:
#
#   cp -R  <DATA>/multimodal_tutorial  <DATA>/ds_structural_demo
#   rm -rf <DATA>/ds_structural_demo/.bidsmgr
#   cd     <DATA>/ds_structural_demo/sub-001/ses-01
#   mv anat anatt                       # a typo in a datatype folder
#   mv func funce                       # and another, on a second modality
#   for e in edf json; do               # an entity that EEG may not carry
#     mv eeg/sub-001_ses-01_task-rest_eeg.$e \
#        eeg/sub-001_ses-01_task-rest_echo-1_eeg.$e
#   done
#
# That yields 4 INVALID_LOCATION, 2 ENTITY_NOT_IN_RULE and, as a consequence
# nobody expects, 1 SCANS_FILENAME_NOT_MATCH_DATASET.
#
# ``ds_events_demo`` is the same dataset with one companion file removed, for
# the figure about a missing events table:
#
#   cp -R  <DATA>/multimodal_tutorial  <DATA>/ds_events_demo
#   rm -rf <DATA>/ds_events_demo/.bidsmgr
#   rm     <DATA>/ds_events_demo/sub-001/ses-01/eeg/*task-motorimagery_events.*
#
# 0 errors, 1 EVENTS_TSV_MISSING. A figure about one finding should contain
# one finding.
INVENTORIES = {
    "multimodal": DATA / "testing_multimodal_collide" / "inv.tsv",
    "pet": DATA / "testing_pet_full" / "inv.tsv",
    # The one-scan download the PET tutorial hands the reader. Figures on that
    # page have to come from this, not from the larger phantom collection, or
    # the screenshots show entities and warnings the reader will never see.
    "pet-sample": DATA / "testing_pet_sample" / "inv.tsv",
    # The ECAT half of the same download.
    "pet-ecat-sample": DATA / "testing_pet_ecat_sample" / "inv.tsv",
    # The multimodal download, before and after the two reconciling edits.
    "mm-raw": DATA / "testing_multimodal_sample_media" / "raw.tsv",
    "mm-fixed": DATA / "testing_multimodal_sample_media" / "fixed.tsv",
    "collisions": DATA / "testing_collisions" / "collided.tsv",
}


# ----------------------------------------------------------------------
# Qt plumbing
# ----------------------------------------------------------------------

def _app():
    app = QApplication.instance() or QApplication(sys.argv[:1])
    return app


_CURRENT_THEME = ["dark"]


def _theme(app, theme: str):
    from bidsmgr.gui.theme_manager import ThemeManager
    _CURRENT_THEME[0] = theme
    ThemeManager(app).apply(theme)


def _show(path: Path) -> str:
    try:
        return str(path.relative_to(DOCS))
    except ValueError:
        return str(path)


def _grab(app, widget, path: Path, width: int, height: int, *,
          expand: bool = False, scroll: float | None = None,
          scroll_to: str | None = None) -> None:
    """Draw one widget at a given size and save it.

    ``expand`` opens every collapsible section, which is where most of a form
    lives. ``scroll`` moves the view down by a fraction of its range, since the
    part worth showing is rarely the top, and ``scroll_to`` finds a label by its
    text and brings it to the top instead, which survives the form growing.
    """
    widget.resize(width, height)
    widget.show()
    app.processEvents()
    if expand:
        from bidsmgr.gui.widgets.template_form import CollapsibleSection
        for section in widget.findChildren(CollapsibleSection):
            section.set_expanded(True)
        app.processEvents()
        app.processEvents()
    from PyQt6.QtWidgets import QLabel, QScrollArea
    area = widget.findChild(QScrollArea)
    if scroll_to is not None and area is not None:
        target = next(
            (lb for lb in widget.findChildren(QLabel)
             if scroll_to.lower() in lb.text().lower()), None)
        if target is None:
            print(f"  (no label matching {scroll_to!r}; leaving at top)")
        else:
            area.ensureWidgetVisible(target, 0, 0)
            app.processEvents()
            # ensureWidgetVisible only guarantees visibility; nudge the label to
            # the top of the viewport so the section reads as the subject.
            bar = area.verticalScrollBar()
            top = target.mapTo(area.widget(), target.rect().topLeft()).y()
            bar.setValue(max(0, min(bar.maximum(), top - 12)))
            app.processEvents()
    elif scroll is not None and area is not None:
        bar = area.verticalScrollBar()
        bar.setValue(int(bar.maximum() * scroll))
        app.processEvents()
    app.processEvents()
    path.parent.mkdir(parents=True, exist_ok=True)
    shot = widget.grab()
    shot.save(str(path))
    print(f"  {_show(path)}  {shot.width()}x{shot.height()} px "
          f"({widget.width()}x{widget.height()} logical)")


def _inventory_table(df: pd.DataFrame, columns: list[str], widths=None):
    """The Converter's inspection table, built the way the panel builds it.

    Mirrors ``ConverterPanel._build_table`` rather than reimplementing it, so
    the delegates, the row tinting and the status badges are the real ones.
    """
    from bidsmgr.gui.delegates import (
        CellTextDelegate, CheckboxDelegate, StatusDelegate,
    )
    from bidsmgr.gui.models.inventory import COLUMNS, InventoryTableModel

    view = QTableView()
    view.setObjectName("inv-table")
    view.setShowGrid(False)
    view.setAlternatingRowColors(False)
    view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    view.verticalHeader().setVisible(False)
    view.verticalHeader().setDefaultSectionSize(26)
    header = view.horizontalHeader()
    header.setHighlightSections(False)
    header.setStretchLastSection(True)
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

    for col, spec in enumerate(COLUMNS):
        if spec.role == "checkbox":
            view.setItemDelegateForColumn(col, CheckboxDelegate(view))
        elif spec.role == "status":
            view.setItemDelegateForColumn(col, StatusDelegate(view))
        else:
            view.setItemDelegateForColumn(col, CellTextDelegate(spec.role, view))

    view.setModel(InventoryTableModel(df))
    widths = widths or {}
    for col, spec in enumerate(COLUMNS):
        view.setColumnHidden(col, spec.key not in columns)
        view.setColumnWidth(col, widths.get(spec.key, spec.width))
    return view


def _read(name: str) -> pd.DataFrame:
    path = INVENTORIES[name]
    if not path.exists():
        raise SystemExit(
            f"no inventory at {path}.\n"
            f"Run a scan first, or point INVENTORIES at one you have."
        )
    return pd.read_csv(path, sep="\t", dtype=str).fillna("")


# ----------------------------------------------------------------------
# The assets
# ----------------------------------------------------------------------

def inventory_multimodal(app, theme: str) -> None:
    """Placeholder 08: MRI, PET, EEG and MEG rows in one table."""
    df = _read("multimodal")
    # One frame has to show the mix, so take a slice that spans the modalities
    # rather than the first N rows, which are all PET.
    picks = []
    for mod in ("pet", "func", "anat", "dwi", "fmap", "eeg", "meg"):
        hit = df[df["proposed_datatype"] == mod]
        picks.extend(hit.head(2).index.tolist())
    sub = df.loc[sorted(set(picks))].reset_index(drop=True)
    cols = ["include", "status", "id", "ses", "mod", "datatype", "suffix",
            "task", "conf", "format", "sequence", "basename"]
    wide = {"mod": 72, "datatype": 72, "suffix": 92, "sequence": 230,
            "basename": 330}
    _grab(app, _inventory_table(sub, cols, wide),
          OUT / f"multimodal_inventory_{theme}.png", 1280, 26 * (len(sub) + 2))


def inventory_mm_raw(app, theme: str) -> None:
    """The multimodal download as it comes off the scan, before any edit."""
    df = _read("mm-raw")
    cols = ["include", "status", "id", "ses", "mod", "datatype", "suffix",
            "task", "conf", "format", "source_folder", "sequence", "basename"]
    wide = {"mod": 86, "task": 112, "source_folder": 118, "sequence": 172,
            "basename": 270}
    _grab(app, _inventory_table(df, cols, wide),
          OUT / f"mm_inventory_raw_{theme}.png", 1400, 26 * (len(df) + 2))


def inventory_mm_fixed(app, theme: str) -> None:
    """The same table after one subject and one session are set on every row."""
    df = _read("mm-fixed")
    cols = ["include", "status", "id", "ses", "mod", "datatype", "suffix",
            "task", "conf", "format", "source_folder", "sequence", "basename"]
    wide = {"mod": 86, "task": 112, "source_folder": 118, "sequence": 172,
            "basename": 270}
    _grab(app, _inventory_table(df, cols, wide),
          OUT / f"mm_inventory_fixed_{theme}.png", 1400, 26 * (len(df) + 2))


def inventory_pet_formats(app, theme: str) -> None:
    """The two PET formats, both rows from the tutorial's own download."""
    df = pd.concat([_read("pet-sample"), _read("pet-ecat-sample")])
    df = df.reset_index(drop=True)
    cols = ["include", "status", "id", "datatype", "suffix", "conf",
            "source_folder", "format", "n_files", "sequence", "basename"]
    wide = {"source_folder": 170, "sequence": 230, "basename": 150}
    _grab(app, _inventory_table(df, cols, wide),
          OUT / f"ecat_scan_{theme}.png", 1120, 26 * (len(df) + 2))


def inventory_collisions(app, theme: str) -> None:
    """Placeholder 01, still frame: two rows resolving to the same name."""
    df = _read("collisions")
    names = df["proposed_basename"]
    dupes = names[names.duplicated(keep=False) & (names != "")]
    if dupes.empty:
        print("  (no colliding names in that inventory; skipping)")
        return
    keep = df.loc[dupes.index].head(4)
    others = df.drop(index=dupes.index).head(3)
    sub = pd.concat([keep, others]).reset_index(drop=True)
    cols = ["include", "status", "id", "ses", "datatype", "suffix",
            "task", "run", "sequence", "basename"]
    _grab(app, _inventory_table(sub, cols),
          OUT / f"name_collision_red_{theme}.png", 1080, 26 * (len(sub) + 2))


def _dialog(modalities, pairs, counts, examples):
    from bidsmgr.gui.recording_meta_dialog import RecordingMetaDialog
    scratch = Path(tempfile.mkdtemp())
    return RecordingMetaDialog(
        scratch / "meta.recording_meta.json", modalities, None,
        present_pairs=pairs, pair_counts=counts, example_paths=examples,
    )


def _panel(df):
    from bidsmgr.gui.models.inventory import InventoryTableModel
    from bidsmgr.gui.properties_panel import PropertiesPanel
    panel = PropertiesPanel()
    panel.bind_model(InventoryTableModel(df.reset_index(drop=True)))
    panel.set_selected_row(0)
    return panel


def template_agnostic(app, theme: str) -> None:
    """The metadata template, top: the questions every modality shares."""
    d = _dialog(
        {"mri", "eeg", "pet"},
        [("anat", "T1w"), ("func", "bold"), ("eeg", "eeg"), ("pet", "pet")],
        {("anat", "T1w"): 4, ("func", "bold"): 61, ("eeg", "eeg"): 12,
         ("pet", "pet"): 3},
        {("anat", "T1w"): "sub-001/anat/sub-001_T1w.json",
         ("func", "bold"): "sub-003/func/sub-003_task-rest_bold.json",
         ("eeg", "eeg"): "sub-001/eeg/sub-001_task-rest_eeg.json",
         ("pet", "pet"): "sub-001/pet/sub-001_pet.json"},
    )
    _grab(app, d, OUT / f"template_walkthrough_{theme}.png", 760, 940,
          expand=True)


def template_eeg(app, theme: str) -> None:
    """The EEG section of the metadata template."""
    d = _dialog({"eeg"}, [("eeg", "eeg")], {("eeg", "eeg"): 28},
                {("eeg", "eeg"): "sub-001/eeg/sub-001_task-rest_eeg.json"})
    _grab(app, d, OUT / f"template_eeg_{theme}.png", 760, 880,
          expand=True, scroll_to="EEGReference")


def template_meg(app, theme: str) -> None:
    """The MEG section of the metadata template."""
    d = _dialog({"meg"}, [("meg", "meg")], {("meg", "meg"): 23},
                {("meg", "meg"): "sub-001/meg/sub-001_task-rest_meg.json"})
    _grab(app, d, OUT / f"template_meg_{theme}.png", 760, 880,
          expand=True, scroll_to="DewarPosition")


def template_mri(app, theme: str) -> None:
    """The MRI sections: mostly answered by the conversion already."""
    d = _dialog({"mri"}, [("anat", "T1w"), ("func", "bold")],
                {("anat", "T1w"): 4, ("func", "bold"): 61},
                {("anat", "T1w"): "sub-001/anat/sub-001_T1w.json",
                 ("func", "bold"): "sub-001/func/sub-001_task-rest_bold.json"})
    _grab(app, d, OUT / f"template_mri_{theme}.png", 760, 880,
          expand=True, scroll_to="Already answered")


def template_pet(app, theme: str) -> None:
    """Placeholder 11: the PET groups of the dataset metadata dialog."""
    d = _dialog({"pet"}, [("pet", "pet")], {("pet", "pet"): 3},
                {("pet", "pet"): "sub-001/pet/sub-001_pet.json"})
    _grab(app, d, OUT / f"pet_template_groups_{theme}.png", 780, 860,
          expand=True, scroll_to="AcquisitionMode")


def inventory_pet_sample(app, theme: str) -> None:
    """The PET tutorial's own download: one scan, one row."""
    df = _read("pet-sample")
    cols = ["include", "status", "id", "datatype", "suffix", "conf",
            "source_folder", "format", "n_files", "sequence", "basename"]
    wide = {"source_folder": 170, "sequence": 170, "basename": 190}
    _grab(app, _inventory_table(df, cols, wide),
          OUT / f"pet_sample_inventory_{theme}.png", 1090, 26 * (len(df) + 2))


def properties_pet(app, theme: str) -> None:
    """The per-row PET panel, where a dataset answer is overridden."""
    df = _read("pet-sample")
    row = df[df["proposed_datatype"] == "pet"].head(1)
    _grab(app, _panel(row), OUT / f"pet_properties_{theme}.png", 460, 940,
          expand=True, scroll_to="PREDICTED PATH")


def properties_blood(app, theme: str) -> None:
    """Placeholder 04 and 12: the blood-sampling section of a PET row."""
    df = _read("pet-sample")
    row = df[df["proposed_datatype"] == "pet"].head(1)
    _grab(app, _panel(row), OUT / f"pet_blood_linking_{theme}.png", 470, 330,
          expand=True, scroll_to="BLOOD SAMPLING")


def properties_eeg(app, theme: str) -> None:
    """The per-row panel on an EEG recording: reference, ground, montage."""
    df = _read("multimodal")
    row = df[df["proposed_datatype"] == "eeg"].head(1)
    if row.empty:
        print("  (no eeg row in that inventory; skipping)")
        return
    _grab(app, _panel(row), OUT / f"eeg_properties_{theme}.png", 460, 800,
          expand=True, scroll_to="REFERENCE")


def inventory_eeg(app, theme: str) -> None:
    """The EEG inventory: task placeholders taken from the filenames."""
    df = _read("multimodal")
    sub = df[df["proposed_datatype"] == "eeg"].head(8)
    if sub.empty:
        print("  (no eeg rows; skipping)")
        return
    cols = ["include", "status", "id", "ses", "task", "run", "conf",
            "format", "sequence", "basename"]
    _grab(app, _inventory_table(sub, cols, {"basename": 340}),
          OUT / f"eeg_inventory_{theme}.png", 1060, 26 * (len(sub) + 2))


def inventory_meg(app, theme: str) -> None:
    """The MEG inventory: sessions inferred from date-named folders."""
    df = _read("multimodal")
    sub = df[df["proposed_datatype"] == "meg"].head(8)
    if sub.empty:
        print("  (no meg rows; skipping)")
        return
    cols = ["include", "status", "id", "ses", "task", "run", "conf",
            "format", "sequence", "basename"]
    _grab(app, _inventory_table(sub, cols, {"basename": 340}),
          OUT / f"meg_inventory_{theme}.png", 1060, 26 * (len(sub) + 2))


def inventory_skipped(app, theme: str) -> None:
    """Rows the scan set aside, each with a reason: the row states in one frame.

    A dimmed row is excluded, a teal one carries no image data at all. Both
    matter, because an unconvertible object otherwise looks exactly like a
    failed conversion of something you wanted.
    """
    df = _read("multimodal")
    skipped = df[df["include"].astype(str) == "0"]
    kept = df[(df["include"].astype(str) == "1")
              & (df["proposed_datatype"].isin(["anat", "func", "dwi", "fmap"]))]
    sub = pd.concat([skipped.head(5), kept.head(4)]).reset_index(drop=True)
    cols = ["include", "status", "id", "ses", "datatype", "suffix",
            "conf", "sequence", "basename", "proposed_issues"]
    _grab(app, _inventory_table(sub, cols, {"sequence": 250, "proposed_issues": 230}),
          OUT / f"inventory_skipped_{theme}.png", 1320, 26 * (len(sub) + 2))


def editor_tree(app, theme: str) -> None:
    """The Editor's BIDS tree with a status dot on every file.

    Deliberately a CLEAN dataset. This figure introduces the tree in the
    walkthrough, and it used to be rendered on a dataset with two mistyped
    datatype folders in it, so the reader met the structural-error lesson three
    steps before the section that teaches it.
    """
    from bidsmgr.gui.widgets.bids_tree_pane import BidsTreePane
    root = DATA / "multimodal_tutorial"
    if not root.exists():
        print(f"  (no dataset at {root}; skipping)")
        return
    report = _report(root)
    tree = BidsTreePane()
    tree.set_root(root)
    app.processEvents()
    badges = {}
    for f in report.files:
        worst = "ok"
        for i in f.issues:
            v = i.severity.value
            if v == "err":
                worst = "err"
                break
            if v == "warn":
                worst = "warn"
        badges[root / f.path] = worst
    tree.set_badges(badges)
    app.processEvents()
    # open the tree so the dots are visible rather than collapsed away
    from PyQt6.QtWidgets import QTreeWidget
    inner = tree.findChild(QTreeWidget)
    if inner is not None:
        inner.expandToDepth(2)
        app.processEvents()
    _grab(app, tree, OUT / f"editor_tree_{theme}.png", 380, 350)


def editor_tree_mm(app, theme: str) -> None:
    """The converted multimodal dataset: six datatypes under one subject."""
    from bidsmgr.gui.widgets.bids_tree_pane import BidsTreePane
    from PyQt6.QtWidgets import QTreeWidget
    root = DATA / "multimodal_tutorial"
    if not root.exists():
        print(f"  (no dataset at {root}; skipping)")
        return
    report = _report(root)
    tree = BidsTreePane()
    tree.set_root(root)
    app.processEvents()
    badges = {}
    for f in report.files:
        worst = "ok"
        for i in f.issues:
            if i.severity.value == "err":
                worst = "err"
                break
            if i.severity.value == "warn":
                worst = "warn"
        badges[root / f.path] = worst
    tree.set_badges(badges)
    app.processEvents()
    inner = tree.findChild(QTreeWidget)
    if inner is not None:
        inner.expandToDepth(3)
        app.processEvents()
    _grab(app, tree, OUT / f"mm_editor_tree_{theme}.png", 420, 900)


def editor_window(app, theme: str) -> None:
    """The whole Editor: tree, viewer and validation pane, on a real dataset.

    The published screenshot of this window still shows the toolbar toggle
    labelled "Strict BIDS", which is now "Deep checks". Rendering it rather
    than keeping the old file is the point of this tool.

    On the clean multimodal dataset, so the figure that introduces the Editor
    shows what a finished dataset looks like rather than a broken one.
    """
    from bidsmgr.gui.editor_panel import EditorPanel
    root = DATA / "multimodal_tutorial"
    if not root.exists():
        print(f"  (no dataset at {root}; skipping)")
        return
    ed = EditorPanel()
    ed.resize(1680, 880)
    ed.show()
    app.processEvents()
    ed._set_root(root, persist=False)
    app.processEvents()
    report = _report(root)
    ed._on_report_ready(report, root)
    app.processEvents()
    # Select a file that actually carries findings, so all three panes are
    # populated rather than showing their empty-state text.
    target = next((f for f in report.files
                   if str(f.path).endswith(".json") and f.issues), None)
    if target is not None:
        ed._on_file_selected(root / target.path)
        for _ in range(4):
            app.processEvents()
    _grab(app, ed, OUT / f"editor_window_{theme}.png", 1680, 880)



# ----------------------------------------------------------------------
# Whole-window shots, for the interactive numbered tours
# ----------------------------------------------------------------------

def _main_window(app, view: str, project_root=None):
    """The real MainWindow, on a scratch settings scope.

    The settings scope matters: on a developer's machine the Home tab's recent
    projects list is full of temporary test folders, which is neither
    presentable nor true of a fresh install. Pointing QSettings at a throwaway
    organisation gives the window a first-run state.
    """
    from PyQt6.QtCore import QCoreApplication
    from bidsmgr.gui.main_window import MainWindow
    from bidsmgr.gui.theme_manager import ThemeManager

    QCoreApplication.setOrganizationName("bidsmgr-docs-shot")
    QCoreApplication.setApplicationName("bidsmgr-docs-shot")

    tm = ThemeManager(app)
    tm.apply("dark" if _CURRENT_THEME[0] == "dark" else "light")
    win = MainWindow(tm)
    win.resize(1480, 900)
    win.show()
    for _ in range(4):
        app.processEvents()
    win._apply_active_view(view, persist=False)
    for _ in range(6):
        app.processEvents()
    return win


def window_home(app, theme: str) -> None:
    """The Home tab of the real window, in its first-run state."""
    win = _main_window(app, "welcome")
    _grab(app, win, OUT / f"window_home_{theme}.png", 1480, 900)


def window_editor(app, theme: str) -> None:
    """The Editor view inside the window, so the tab strip is visible.

    On the clean multimodal dataset. It used to be rendered on ``ds_MRI``,
    whose tree carries two mistyped datatype folders, so a figure whose job is
    to show where the Editor lives was showing red dots and a lesson that
    belongs three steps later.
    """
    from bidsmgr.editor.validator import validate
    root = DATA / "multimodal_tutorial"
    win = _main_window(app, "editor")
    if root.exists():
        ed = win.stack.widget(1)
        ed._set_root(root, persist=False)
        app.processEvents()
        report = validate(root)
        ed._on_report_ready(report, root)
        app.processEvents()
        target = next((f for f in report.files
                       if str(f.path).endswith(".json") and f.issues), None)
        if target is not None:
            ed._on_file_selected(root / target.path)
        for _ in range(4):
            app.processEvents()
    _grab(app, win, OUT / f"window_editor_{theme}.png", 1480, 900)



def sidecar_form(app, theme: str) -> None:
    """A JSON sidecar as the schema-aware form, colour-coded by level."""
    from bidsmgr.gui.widgets.sidecar_form_pane import SidecarFormPane
    root = DATA / "multimodal_tutorial"
    target = next(root.rglob("*_bold.json"), None) or next(root.rglob("*.json"), None)
    if target is None:
        print("  (no sidecar found; skipping)")
        return
    report = _report(root)
    pane = SidecarFormPane()
    pane.set_file(target, root, report)
    _grab(app, pane, OUT / f"sidecar_form_{theme}.png", 640, 760)


def sidecar_form_pet(app, theme: str) -> None:
    """The finished PET sidecar, on the tutorial's own sample dataset.

    The state the tutorial reaches at its last step: converted, dose sheet
    answered, blood attached, nothing left to fix. An earlier version of this
    asset showed the sidecar BEFORE the template was filled, which put an
    Editor screenshot of a converted file into a step that runs before the
    conversion.
    """
    from bidsmgr.gui.widgets.sidecar_form_pane import SidecarFormPane
    root = DATA / "testing_pet_sample" / "pet_tutorial"
    target = root / "sub-001" / "pet" / "sub-001_pet.json"
    if not target.exists():
        print("  (no converted PET sample; skipping)")
        return
    pane = SidecarFormPane()
    pane.set_file(target, root, _report(root))
    _grab(app, pane, OUT / f"pet_sidecar_form_{theme}.png", 640, 780,
          scroll_to="InjectedMass")


# ----------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------

# tab label -> (output name, width, height). Heights are tuned so each tab
# ends just below its own content rather than showing a field of empty panel.
SETTINGS_TABS = {
    "bids-version": ("BIDS version", "settings_bids_version", 620, 300),
    "display":      ("Display", "settings_display", 620, 300),
    "system":       ("System", "settings_system_info", 620, 330),
    "scan":         ("Scan", "settings_scan_defaults", 620, 430),
    "scan-rules":   ("Scan rules", "settings_scan_rules_tab", 700, 600),
    "convert":      ("Convert + post-convert", "settings_convert_tab", 700, 640),
    "validation":   ("Validation", "settings_validation", 660, 320),
}


def _settings_tab(app, theme, key):
    """Open the Settings dialog on one tab and render it.

    The dialog is the real one, built from the real AppSettings defaults, so a
    control added or renamed in the application shows up here on the next run.
    """
    from PyQt6.QtWidgets import QTabWidget
    from bidsmgr.gui.app_settings import AppSettings
    from bidsmgr.gui.settings_dialog import SettingsDialog

    label, out_name, w, h = SETTINGS_TABS[key]
    dlg = SettingsDialog(AppSettings())
    tabs = dlg.findChild(QTabWidget)
    if tabs is None:
        print("  (no tab widget found; skipping)")
        return
    index = next((i for i in range(tabs.count()) if tabs.tabText(i) == label), None)
    if index is None:
        print(f"  (no tab called {label!r}; the dialog may have been "
              f"restructured: {[tabs.tabText(i) for i in range(tabs.count())]})")
        return
    tabs.setCurrentIndex(index)
    app.processEvents()
    _grab(app, dlg, OUT / f"{out_name}_{theme}.png", w, h)


def settings_all(app, theme: str) -> None:
    """Every tab of the Settings dialog, one image each."""
    for key in SETTINGS_TABS:
        _settings_tab(app, theme, key)



# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------

def _report(root: Path, *, flag_todos: bool = True):
    from bidsmgr.editor.validator import validate
    return validate(root, flag_todos=flag_todos)


def _pane(report, root: Path, rel: str | None = None):
    from bidsmgr.gui.widgets.validation_pane import ValidationPane
    pane = ValidationPane()
    pane.set_report(report)
    if rel is not None:
        pane.set_current_file(root / rel, root)
    return pane


def _first_with(report, severity: str, name_contains: str = ""):
    """The first file carrying an issue of this severity."""
    for f in report.files:
        if name_contains and name_contains not in str(f.path):
            continue
        if any(i.severity.value == severity for i in f.issues):
            return f
    return None


def _file_with_rule(report, rule_id: str):
    """The first file carrying a finding with this rule id."""
    for f in report.files:
        if any(i.rule_id == rule_id for i in f.issues):
            return f
    return None


def _pane_shot(app, theme, dataset, out_name, *, rule=None, rel=None,
               width=520, height=520, base=None, flag_todos=True):
    """Render the validation pane on a real dataset, at a chosen file.

    ``flag_todos=False`` drops the TODO-placeholder warnings, which is how a
    figure about one KIND of finding shows that kind rather than a wall of
    unfinished metadata underneath it.
    """
    root = (base or BIDS) / dataset
    if not root.exists():
        print(f"  (no dataset at {root}; skipping)")
        return
    report = _report(root, flag_todos=flag_todos)
    target = rel
    if rule is not None:
        hit = _file_with_rule(report, rule)
        if hit is None:
            print(f"  ({rule} not present in {dataset}; skipping)")
            return
        target = hit.path
    _grab(app, _pane(report, root, target),
          OUT / f"{out_name}_{theme}.png", width, height)


def validation_dataset(app, theme: str) -> None:
    """The three scopes, on a dataset whose findings are dataset-level."""
    root = BIDS / "ds_pet"
    if not root.exists():
        print("  (ds_pet missing; skipping)")
        return
    report = _report(root)
    _grab(app, _pane(report, root), OUT / f"validation_dataset_scope_{theme}.png",
          520, 560)


def validation_error(app, theme: str) -> None:
    """A value inside a table that is the wrong type."""
    _pane_shot(app, theme, "ds_MRI", "validation_provenance",
               rule="TSV_VALUE_INCORRECT_TYPE", height=430)


def validation_warnings(app, theme: str) -> None:
    """Recommended fields nobody has answered, on the dataset description."""
    _pane_shot(app, theme, "ds_MRI", "validation_warnings",
               rel="dataset_description.json", height=600)


def validation_sidecar_error(app, theme: str) -> None:
    """An error inside a sidecar: a field holding the wrong kind of value."""
    _pane_shot(app, theme, "ds_eeg", "validation_sidecar_error",
               rule="JSON_SCHEMA_VALIDATION_ERROR", height=560)


def validation_invalid_location(app, theme: str) -> None:
    """A mistyped datatype folder, on the multimodal dataset.

    ``ds_structural_demo`` is the converted multimodal sample with three things
    broken on purpose, each the kind of mistake a person makes by hand:
    ``anat`` renamed to ``anatt``, ``func`` to ``funce``, and an ``echo``
    entity added to an EEG filename. TODO warnings are turned off so the figure
    shows the structural finding rather than a column of unfinished metadata.
    """
    _pane_shot(app, theme, "ds_structural_demo", "invalid_location",
               rel="sub-001/ses-01/anatt/sub-001_ses-01_acq-tfl3p2_T1w.nii.gz",
               base=DATA, flag_todos=False, width=560, height=350)


def validation_bad_entity(app, theme: str) -> None:
    """An entity the standard does not allow on this kind of file."""
    _pane_shot(app, theme, "ds_structural_demo", "validation_bad_entity",
               rel="sub-001/ses-01/eeg/sub-001_ses-01_task-rest_echo-1_eeg.edf",
               base=DATA, flag_todos=False, width=560, height=360)


def validation_broken_manifest(app, theme: str) -> None:
    """The knock-on effect: scans.tsv still lists the paths that moved."""
    _pane_shot(app, theme, "ds_structural_demo", "validation_broken_manifest",
               rel="sub-001/ses-01/sub-001_ses-01_scans.tsv",
               base=DATA, flag_todos=False, width=560, height=350)


def validation_mm(app, theme: str) -> None:
    """The Editor's validation pane on the converted multimodal dataset.

    A whole four-modality dataset with nothing wrong in it, which is worth a
    figure of its own: every other validation image on the site is a failure.
    """
    _pane_shot(app, theme, "multimodal_tutorial", "mm_validation",
               rel="sub-001/ses-01/meg/sub-001_ses-01_task-rest_meg.fif",
               base=DATA, flag_todos=False, width=560, height=360)


def validation_missing_companion(app, theme: str) -> None:
    """A cross-file warning: a task run with no events table beside it.

    On ``ds_events_demo``, the converted multimodal dataset with one
    ``events.tsv`` deleted, so the figure shows this warning and nothing else.
    It used to be rendered on ``ds_MRI``, which carries structural errors of
    its own, and they appeared stacked above the warning the caption was
    talking about.
    """
    _pane_shot(app, theme, "ds_events_demo", "validation_missing_events",
               rel="sub-001/ses-01/eeg/sub-001_ses-01_task-motorimagery_eeg.edf",
               base=DATA, flag_todos=False, width=560, height=335)


def validation_pet_checks(app, theme: str) -> None:
    """A PET cross-field check: numbers in a sidecar that disagree.

    Picks the file where such a finding is the *only* one, so the image shows
    the check rather than a wall of unrelated type errors.
    """
    PET_RULES = ("PET_FRAME_CONSISTENCY", "bidsmgr.pet.time_zero_format",
                 "bidsmgr.pet.recon_parameter_length_mismatch")
    for ds in ("ds_pets", "ds_pet3"):
        root = BIDS / ds
        if not root.exists():
            continue
        report = _report(root)
        best = None
        for f in report.files:
            ids = [i.rule_id for i in f.issues]
            if any(r in ids for r in PET_RULES):
                if best is None or len(ids) < len(best.issues):
                    best = f
        if best is None:
            continue
        _grab(app, _pane(report, root, best.path),
              OUT / f"validation_pet_checks_{theme}.png", 520, 430)
        return
    print("  (no PET-specific findings found; skipping)")


# ----------------------------------------------------------------------
# Signals
# ----------------------------------------------------------------------

def psd(app, theme: str) -> None:
    """The power spectrum of a real EEG recording.

    The mains peak is the point: it is how you check that the power-line
    frequency you declared is the one actually in the data.
    """
    import numpy as np
    import mne
    from bidsmgr.gui.widgets.recording_viewer_pane import _PsdDialog

    rec = next((BIDS / "ds_eeg").rglob("*_eeg.edf"), None)
    if rec is None:
        print("  (no EEG recording found; skipping)")
        return
    raw = mne.io.read_raw_edf(rec, preload=True, verbose=False)
    spectrum = raw.compute_psd(fmin=0.1, fmax=min(raw.info["sfreq"] / 2.0, 150.0),
                               verbose=False)
    names = list(spectrum.ch_names)
    raw_names = list(raw.ch_names)
    types = []
    for ch in names:
        try:
            types.append(mne.channel_type(raw.info, raw_names.index(ch)))
        except ValueError:
            types.append("misc")
    data = np.asarray(spectrum.get_data())
    n = min(data.shape[0], len(names), len(types))
    result = {"freqs": np.asarray(spectrum.freqs), "data": data[:n],
              "ch_names": names[:n], "ch_types": types[:n]}

    dlg = _PsdDialog(result)
    _grab(app, dlg, OUT / f"psd_line_frequency_{theme}.png", 900, 560)



ASSETS = {
    "inventory-multimodal": inventory_multimodal,
    "inventory-pet-formats": inventory_pet_formats,
    "inventory-pet-sample": inventory_pet_sample,
    "inventory-mm-raw": inventory_mm_raw,
    "inventory-mm-fixed": inventory_mm_fixed,
    "inventory-collisions": inventory_collisions,
    "template-agnostic": template_agnostic,
    "template-eeg": template_eeg,
    "template-meg": template_meg,
    "template-mri": template_mri,
    "template-pet": template_pet,
    "properties-pet": properties_pet,
    "properties-blood": properties_blood,
    "properties-eeg": properties_eeg,
    "inventory-eeg": inventory_eeg,
    "inventory-meg": inventory_meg,
    "inventory-skipped": inventory_skipped,
    "settings": settings_all,
    "editor-tree": editor_tree,
    "editor-tree-mm": editor_tree_mm,
    "editor-window": editor_window,
    "window-home": window_home,
    "window-editor": window_editor,
    "sidecar-form": sidecar_form,
    "sidecar-form-pet": sidecar_form_pet,
    "validation-dataset": validation_dataset,
    "validation-error": validation_error,
    "validation-warnings": validation_warnings,
    "validation-invalid-location": validation_invalid_location,
    "validation-bad-entity": validation_bad_entity,
    "validation-mm": validation_mm,
    "validation-broken-manifest": validation_broken_manifest,
    "validation-sidecar-error": validation_sidecar_error,
    "validation-missing-companion": validation_missing_companion,
    "validation-pet-checks": validation_pet_checks,
    "psd": psd,
}


# ----------------------------------------------------------------------

def encode(frames: list[Path], out: Path, ffmpeg: str, fps: int = 2) -> None:
    """Turn a frame sequence into an mp4 the site can play."""
    listing = out.with_suffix(".txt")
    listing.write_text(
        "".join(f"file '{f}'\nduration {1 / fps:.3f}\n" for f in frames)
        + f"file '{frames[-1]}'\n"
    )
    subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(listing), "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)],
        check=True,
    )
    listing.unlink()
    print(f"  {_show(out)}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("asset", nargs="*", help="which assets to render")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--out", default=None, help="write here instead of assets/features")
    parser.add_argument("--theme", choices=("dark", "light", "both"), default="both")
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    parser.add_argument("--scale", type=float, default=None,
                        help="render scale (default 2, for high-resolution output)")
    args = parser.parse_args(argv)

    if args.scale is not None and QApplication.instance() is None:
        os.environ["QT_SCALE_FACTOR"] = str(args.scale)

    if args.list:
        for name, fn in ASSETS.items():
            print(f"{name:24s} {(fn.__doc__ or '').splitlines()[0]}")
        return 0

    global OUT
    if args.out:
        OUT = Path(args.out)

    names = list(ASSETS) if args.all else args.asset
    if not names:
        parser.error("name an asset, or pass --all or --list")
    unknown = [n for n in names if n not in ASSETS]
    if unknown:
        parser.error(f"unknown asset(s): {', '.join(unknown)}")

    themes = ("dark", "light") if args.theme == "both" else (args.theme,)
    app = _app()
    for theme in themes:
        _theme(app, theme)
        print(f"{theme} theme")
        for name in names:
            ASSETS[name](app, theme)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

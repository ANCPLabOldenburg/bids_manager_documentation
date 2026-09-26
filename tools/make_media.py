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
    # Numbers in the figures are read by an English-language audience, so they
    # are drawn in an English locale whatever the machine rendering them uses.
    # Left to the system, a German desktop writes a 1 Hz high-pass as "1,000",
    # which a reader of this site takes for one thousand. Set before any widget
    # exists, because a spin box takes its locale when it is built.
    from PyQt6.QtCore import QLocale
    QLocale.setDefault(QLocale(QLocale.Language.English,
                               QLocale.Country.UnitedStates))
    app = QApplication.instance() or QApplication(sys.argv[:1])
    return app


_CURRENT_THEME = ["dark"]


# The application's own font scale, the one in Settings -> Display, applied to
# every rendered figure. Slightly larger than the default: a screenshot is read
# scaled down inside a column of prose, where 1.0 lands below comfortable
# reading size. Overridable with DOCS_MEDIA_FONT_SCALE.
FONT_SCALE = float(os.environ.get("DOCS_MEDIA_FONT_SCALE", "1.15"))


def _theme(app, theme: str):
    from bidsmgr.gui.theme_manager import ThemeManager
    _CURRENT_THEME[0] = theme
    ThemeManager(app, font_scale=FONT_SCALE).apply(theme)


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
        # Twice. Expanding an outer section BUILDS the sections nested inside
        # it, so a single pass opens the parents and leaves every child folded,
        # which is how a figure of the "already answered" block ended up
        # showing its collapsed header and the next section's empty fields.
        for _ in range(3):
            found = [x for x in widget.findChildren(CollapsibleSection)
                     if not x.is_expanded()] if hasattr(
                         CollapsibleSection, "is_expanded") else \
                    widget.findChildren(CollapsibleSection)
            if not found:
                break
            for section in found:
                section.set_expanded(True)
            app.processEvents()
            app.processEvents()
    from PyQt6.QtWidgets import QAbstractButton, QLabel, QScrollArea
    area = widget.findChild(QScrollArea)
    if scroll_to is not None and area is not None:
        # Labels AND buttons: a collapsible section's title is a button, so
        # searching only labels silently left the view at the top.
        candidates = widget.findChildren(QLabel) + widget.findChildren(QAbstractButton)
        target = next(
            (w for w in candidates
             if scroll_to.lower() in (w.text() or "").lower()), None)
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
        hit = df[df["datatype"] == mod]
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
    names = df["bids_name"]
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


# The scaffold a real scan writes beside its inventory. It carries the
# ``converter_preview`` block, which is what the template shows folded away as
# "Already answered by the conversion". Built from a scratch file the dialog
# has nothing to show there, and a figure about that block shows an empty one.
SCAFFOLD = INVENTORIES["multimodal"].with_suffix(".tsv.recording_meta.json")


def _dialog(modalities, pairs, counts, examples, *, scaffold=True):
    """The dataset metadata dialog, on a copy of a real scan's scaffold.

    The copy matters: the dialog writes to the path it is given on Save, and
    a figure should never be one keystroke away from editing the test data.
    """
    from bidsmgr.gui.recording_meta_dialog import RecordingMetaDialog
    import shutil
    scratch = Path(tempfile.mkdtemp()) / "meta.recording_meta.json"
    if scaffold and SCAFFOLD.exists():
        shutil.copyfile(SCAFFOLD, scratch)
    return RecordingMetaDialog(
        scratch, modalities, None,
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


def properties_pet(app, theme: str) -> None:
    """The per-row PET panel, where a dataset answer is overridden."""
    df = _read("pet-sample")
    row = df[df["datatype"] == "pet"].head(1)
    _grab(app, _panel(row), OUT / f"pet_properties_{theme}.png", 460, 940,
          expand=True, scroll_to="PREDICTED PATH")


def properties_blood(app, theme: str) -> None:
    """Placeholder 04 and 12: the blood-sampling section of a PET row."""
    df = _read("pet-sample")
    row = df[df["datatype"] == "pet"].head(1)
    _grab(app, _panel(row), OUT / f"pet_blood_linking_{theme}.png", 470, 330,
          expand=True, scroll_to="BLOOD SAMPLING")


def properties_eeg(app, theme: str) -> None:
    """The per-row panel on an EEG recording: reference, ground, montage."""
    df = _read("multimodal")
    row = df[df["datatype"] == "eeg"].head(1)
    if row.empty:
        print("  (no eeg row in that inventory; skipping)")
        return
    _grab(app, _panel(row), OUT / f"eeg_properties_{theme}.png", 460, 800,
          expand=True, scroll_to="REFERENCE")


def properties_mri(app, theme: str) -> None:
    """The per-row panel on an MRI run: entities first, then the sidecar.

    The per-file level of the template, on the modality where most of it is
    already answered. What the panel asks for here is the naming, not the
    metadata, which is the opposite of the EEG case beside it.
    """
    df = _read("multimodal")
    row = df[df["datatype"] == "anat"].head(1)
    if row.empty:
        print("  (no anat row; skipping)")
        return
    _grab(app, _panel(row), OUT / f"mri_properties_{theme}.png", 470, 780,
          expand=True)


def properties_meg(app, theme: str) -> None:
    """The per-row panel on a MEG recording."""
    df = _read("multimodal")
    row = df[df["datatype"] == "meg"].head(1)
    if row.empty:
        print("  (no meg row; skipping)")
        return
    _grab(app, _panel(row), OUT / f"meg_properties_{theme}.png", 470, 800,
          expand=True, scroll_to="ACQUISITION")


def properties_companions(app, theme: str) -> None:
    """The companion-file section, which is on EVERY row, not just EEG or PET.

    The tutorial used to present companions through a PET tab and an EEG tab,
    which reads as though they were a feature of those two modalities. The
    section is modality-agnostic and offers six kinds, and the dropdown is the
    quickest way to show that.
    """
    from PyQt6.QtWidgets import QComboBox
    df = _read("multimodal")
    row = df[df["datatype"] == "func"].head(1)
    if row.empty:
        row = df.head(1)
    panel = _panel(row)
    panel.resize(470, 900)
    panel.show()
    app.processEvents()
    # Open the suffix dropdown so the six kinds are on screen. A closed combo
    # shows one word and teaches nothing.
    combo = getattr(panel, "_companion_suffix", None)
    if isinstance(combo, QComboBox):
        combo.showPopup()
        for _ in range(4):
            app.processEvents()
    _grab(app, panel, OUT / f"companion_files_{theme}.png", 470, 300,
          scroll_to="COMPANION")


def inventory_eeg(app, theme: str) -> None:
    """The EEG inventory: task placeholders taken from the filenames."""
    df = _read("multimodal")
    sub = df[df["datatype"] == "eeg"].head(8)
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
    sub = df[df["datatype"] == "meg"].head(8)
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
              & (df["datatype"].isin(["anat", "func", "dwi", "fmap"]))]
    sub = pd.concat([skipped.head(5), kept.head(4)]).reset_index(drop=True)
    cols = ["include", "status", "id", "ses", "datatype", "suffix",
            "conf", "sequence", "basename", "issues"]
    _grab(app, _inventory_table(sub, cols, {"sequence": 250, "issues": 230}),
          OUT / f"inventory_skipped_{theme}.png", 1320, 25 * (len(sub) + 2))


def inventory_include(app, theme: str) -> None:
    """The include column, with the decision half made.

    The curation step is where a reader decides what converts, and the page
    described it in prose with no picture of the control. This is that column,
    on a mix of rows: two localisers the user has just unticked, and the
    recordings that are staying. The row state follows the tick, so the answer
    is visible without reading the column.
    """
    df = _read("multimodal")
    kept = df[(df["include"].astype(str) == "1")].head(5)
    off = df[(df["include"].astype(str) == "0")].head(4)
    sub = pd.concat([kept, off]).reset_index(drop=True)
    cols = ["include", "status", "id", "ses", "datatype", "suffix",
            "sequence", "basename"]
    _grab(app, _inventory_table(sub, cols, {"sequence": 270, "basename": 300}),
          OUT / f"inventory_include_{theme}.png", 1180, 25 * (len(sub) + 2))


def _badges(root: Path, report):
    """Severities AND counts, exactly as the Editor stamps them.

    The tree stopped carrying a bare dot several releases ago; it carries how
    many errors and how many warnings each row holds. Passing only the
    severities renders the OLD figure from the NEW application, which is the
    one failure this generator exists to prevent. Mirrored findings are the
    same finding shown twice, on the data file and on its editable sidecar,
    so counting both would double every number in the tree.
    """
    severities: dict[Path, str] = {}
    counts: dict[Path, tuple[int, int]] = {}
    for f in report.files:
        countable = [i for i in f.issues if not getattr(i, "mirrored", False)]
        n_err = sum(1 for i in countable if i.severity.value == "err")
        n_warn = sum(1 for i in countable if i.severity.value == "warn")
        worst = "ok"
        if any(i.severity.value == "err" for i in f.issues):
            worst = "err"
        elif any(i.severity.value == "warn" for i in f.issues):
            worst = "warn"
        absolute = root / f.path
        severities[absolute] = worst
        if n_err or n_warn:
            counts[absolute] = (n_err, n_warn)
    return severities, counts


def editor_tree(app, theme: str) -> None:
    """The Editor's BIDS tree, with what each row holds counted on it.

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
    tree.set_badges(*_badges(root, report))
    app.processEvents()
    # open the tree so the dots are visible rather than collapsed away
    from PyQt6.QtWidgets import QTreeWidget
    inner = tree.findChild(QTreeWidget)
    if inner is not None:
        inner.expandToDepth(2)
        app.processEvents()
    # Wide enough that the folder rollups ("3 ses, 33 files") and the count
    # pills sit side by side instead of the rollup being elided, and tall
    # enough to end on a whole row.
    _grab(app, tree, OUT / f"editor_tree_{theme}.png", 430, 402)


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
    tree.set_badges(*_badges(root, report))
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
    from PyQt6.QtWidgets import QTreeWidget
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    # This window PRINTS ITS DATASET PATH across the top, so rendering it from
    # the author's own output folder publishes their home directory and
    # username in the site's flagship Editor figure.
    root = _demo_copy("multimodal_tutorial")
    ed = EditorPanel()
    ed.resize(1680, 880)
    ed.show()
    app.processEvents()
    ed._set_root(root, persist=False)
    app.processEvents()
    report = _report(root)
    ed._on_report_ready(report, root)
    app.processEvents()
    # A sidecar INSIDE a subject, not dataset_description.json. The dataset
    # description holds four fields, so the form reads as mostly empty space,
    # and the figure has to show what a populated schema-aware form looks like.
    target = next((f for f in report.files
                   if str(f.path).startswith("sub-")
                   and str(f.path).endswith(".json") and f.issues), None)
    if target is not None:
        ed._on_file_selected(root / target.path)
        for _ in range(4):
            app.processEvents()
    # An unexpanded tree shows two rows and teaches nothing about the layout.
    inner = ed._tree_pane.findChild(QTreeWidget)
    if inner is not None:
        inner.expandToDepth(2)
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

    tm = ThemeManager(app, font_scale=FONT_SCALE)
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
    from PyQt6.QtWidgets import QLineEdit
    win = _main_window(app, "welcome")
    # The location field is prefilled with the home directory, which publishes
    # the author's username in a figure six markers point at.
    for edit in win.findChildren(QLineEdit):
        if edit.objectName() == "welcome-input" and edit.isReadOnly():
            edit.setText("/data/bids")
    app.processEvents()
    _grab(app, win, OUT / f"window_home_{theme}.png", 1480, 900)


def window_converter(app, theme: str) -> None:
    """The Converter view inside the window, with a real scan loaded.

    Replaces a hand-taken screenshot that still showed v1.2.1 in the status
    bar and the author's home directory in both path bars.
    """
    tsv = INVENTORIES["multimodal"]
    win = _main_window(app, "converter")
    if tsv.exists():
        # Open a project first. Without one the header carries no project
        # switcher, and the tutorial's marker overlay has a numbered marker
        # pointing at a control that is not there.
        if (DATA / "multimodal_tutorial").exists():
            try:
                win.welcome.open_project(_demo_copy("multimodal_sample"))
                for _ in range(6):
                    app.processEvents()
            except Exception as exc:
                print(f"  (could not open the demo project: {exc})")
        conv = win.stack.widget(0)
        df = _read("multimodal")
        # The raw folder this was scanned from is misspelt, and its name
        # becomes the dataset slug, so the typo would appear on every row of a
        # published figure as if the tool had made it.
        if "dataset" in df.columns:
            df["dataset"] = "multimodal_sample"
        conv.load_inventory(df, output_tsv=tsv)
        # The raw tree reads the folder, so it has to be the real one. The
        # PATH BARS do not: they are the widest text on screen, and a real one
        # publishes a home directory and elides everything useful.
        # Through a symlink, so the tree's root row agrees with the path bar
        # above it. The real folder's name is misspelt, and a figure whose two
        # halves disagree is the kind of detail a careful reader trusts less.
        real = DATA.parent / "raw_data" / "mutilmodal"
        raw = DEMO_ROOT / "raw" / "multimodal_study"
        if real.exists():
            raw.parent.mkdir(parents=True, exist_ok=True)
            if raw.is_symlink() or raw.exists():
                raw.unlink()
            raw.symlink_to(real, target_is_directory=True)
            conv._raw_root = raw
            conv._raw_pane.set_root(raw)
        conv._raw_pathbar.set_value(str(raw), ok=True)
        conv._bids_pathbar.set_value(str(DEMO_ROOT / "multimodal_sample"), ok=True)
        app.processEvents()
        # An INCLUDED row, so the Properties panel shows a recording that is
        # going to be converted rather than one the scan set aside.
        model = conv._table.model()
        row = 0
        if model is not None:
            for i in range(model.rowCount()):
                if str(df.iloc[i].get("suffix", "")) == "bold":
                    row = i
                    break
            conv._table.selectRow(row)
        for _ in range(4):
            app.processEvents()
    _grab(app, win, OUT / f"window_converter_{theme}.png", 1480, 900)


def window_editor(app, theme: str) -> None:
    """The Editor view inside the window, so the tab strip is visible.

    On the clean multimodal dataset. It used to be rendered on ``ds_MRI``,
    whose tree carries two mistyped datatype folders, so a figure whose job is
    to show where the Editor lives was showing red dots and a lesson that
    belongs three steps later.
    """
    from bidsmgr.editor.validator import validate
    from PyQt6.QtWidgets import QTreeWidget
    win = _main_window(app, "editor")
    # Same reason as editor_window: the path bar is on screen.
    if (DATA / "multimodal_tutorial").exists():
        root = _demo_copy("multimodal_tutorial")
        ed = win.stack.widget(1)
        ed._set_root(root, persist=False)
        app.processEvents()
        report = validate(root)
        ed._on_report_ready(report, root)
        app.processEvents()
        target = next((f for f in report.files
                       if str(f.path).startswith("sub-")
                       and str(f.path).endswith(".json") and f.issues), None)
        if target is not None:
            ed._on_file_selected(root / target.path)
        for _ in range(4):
            app.processEvents()
        inner = ed._tree_pane.findChild(QTreeWidget)
        if inner is not None:
            inner.expandToDepth(2)
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
    root = DATA / "pet_tutorial_dicom"
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
               width=520, height=520, base=None, flag_todos=True,
               scroll_to="FILE \u00b7"):
    """Render the validation pane on a real dataset, at a chosen file.

    ``flag_todos=False`` drops the TODO-placeholder warnings, which is how a
    figure about one KIND of finding shows that kind rather than a wall of
    unfinished metadata underneath it.

    ``scroll_to`` defaults to the FILE section because the pane opens on the
    dataset and folder sections, and a figure about a finding in a file
    otherwise shows two other sections and not the finding. Pass ``None`` for a
    figure that is genuinely about the top of the pane.
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
          OUT / f"{out_name}_{theme}.png", width, height, scroll_to=scroll_to)


def _file_with_provenance(report, *, severity=None, folder_only=False):
    """A file carrying a finding that NAMES the schema rule it came from.

    Not every finding has one. The structural checks (a sidecar describing no
    data file, a file in a folder that is not a datatype) are bidsval's own
    rules and have no path into the standard to print, so a figure about
    provenance rendered on the first finding it found showed one with no
    provenance line at all. This picks a finding that actually has one.
    """
    for f in report.files:
        if folder_only and "/" not in str(f.path):
            continue
        for i in f.issues:
            if getattr(i, "mirrored", False):
                continue
            if not getattr(i, "schema_rule", None):
                continue
            if severity and i.severity.value != severity:
                continue
            return f, i
    return None, None


def validation_provenance_pet(app, theme: str) -> None:
    """The same idea on a PET sidecar, where the rule paths earn their keep.

    PET has around forty sidecar fields and the rules for units and timing are
    easy to misread, so the PET page needs a PET rule path rather than an EEG
    one borrowed from another chapter.
    """
    root = DATA / "pet_tutorial_dicom"
    if not root.exists():
        print("  (no converted PET sample; skipping)")
        return
    report = _report(root, flag_todos=False)
    hit, issue = _file_with_provenance(report, folder_only=True)
    if hit is None:
        print("  (no PET finding carries a schema rule; skipping)")
        return
    print(f"    (showing {issue.rule_id} from {issue.schema_rule})")
    _grab(app, _pane(report, root, hit.path),
          OUT / f"validation_provenance_pet_{theme}.png", 560, 470,
          scroll_to="FILE \u00b7")


def validation_scopes(app, theme: str) -> None:
    """The pane's three sections, with the dataset one actually populated."""
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root = _scopes_demo()
    report = _report(root, flag_todos=False)
    hit, _ = _file_with_provenance(report, folder_only=True)
    if hit is None:
        print("  (no nested file with findings; skipping)")
        return
    _grab(app, _pane(report, root, hit.path),
          OUT / f"validation_scopes_{theme}.png", 560, 900)


def _bad_scans_demo():
    """A copy whose scans table holds one malformed timestamp.

    Broken by hand, because that is how it happens: a spreadsheet, an export,
    a careless edit. Every filename stays valid, so no naming check can see it,
    which is the whole point of the figure.
    """
    root = _demo_copy("bad_scans_demo")
    for tsv in sorted(root.rglob("*_scans.tsv")):
        lines = tsv.read_text().splitlines()
        if len(lines) < 2 or "acq_time" not in lines[0].split("\t"):
            continue
        col = lines[0].split("\t").index("acq_time")
        cells = lines[1].split("\t")
        if len(cells) <= col:
            continue
        # A real timestamp with the seconds left unpadded, which reads as a
        # time to a person and is not a valid date-time to the standard.
        cells[col] = "2009-10-02T08:50:3"
        lines[1] = "\t".join(cells)
        tsv.write_text("\n".join(lines) + "\n")
        return root
    return root


def validation_error(app, theme: str) -> None:
    """A value inside a table that is the wrong type, with its rule path.

    Five pages caption this asset as "the rule in the BIDS schema the
    requirement is drawn from", so it has to be a finding that HAS one, AND it
    has to be scrolled to that finding: rendered at the top of the pane it
    showed a dataset-level error with no rule path, which is the opposite of
    what every one of those captions claims.
    """
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root = _bad_scans_demo()
    report = _report(root, flag_todos=False)
    hit = _file_with_rule(report, "TSV_VALUE_INCORRECT_TYPE")
    if hit is None:
        print("  (no malformed table value; skipping)")
        return
    _grab(app, _pane(report, root, hit.path),
          OUT / f"validation_provenance_{theme}.png", 560, 470,
          scroll_to="FILE \u00b7")


def _structural_demo():
    """A copy with three structural mistakes in it, made the way people make
    them: a datatype folder mistyped, a second one mistyped, and an entity
    added to a filename that may not carry it.

    Built here rather than kept as a folder on disk, because a hand-made
    fixture goes missing and its builders then skip in silence, which is how
    four figures on this site ended up years out of date.
    """
    root = _demo_copy("structural_demo")
    ses = next((p for p in sorted(root.glob("sub-001/ses-*")) if (p / "anat").is_dir()), None)
    if ses is None:
        return root, None
    (ses / "anat").rename(ses / "anatt")
    if (ses / "func").is_dir():
        (ses / "func").rename(ses / "funce")
    return root, ses


def _bad_entity_demo():
    """A copy where an EEG recording carries an entity EEG may not have."""
    root = _demo_copy("bad_entity_demo")
    target = None
    for rec in sorted(root.rglob("*_eeg.*")):
        if rec.suffix in (".json", ".tsv"):
            continue
        stem = rec.name.rsplit("_eeg", 1)[0]
        for sib in sorted(rec.parent.glob(stem + "_eeg.*")):
            new = sib.with_name(sib.name.replace("_eeg", "_echo-1_eeg"))
            sib.rename(new)
            if sib is rec:
                target = new
        target = target or rec.parent / (stem + "_echo-1_eeg" + rec.suffix)
        break
    return root, target


def _events_demo():
    """A copy with one events table removed, so its recording has none."""
    root = _demo_copy("events_demo")
    target = None
    for ev in sorted(root.rglob("*_events.tsv")):
        stem = ev.name.rsplit("_events", 1)[0]
        rec = next((p for p in sorted(ev.parent.glob(stem + "_*"))
                    if p.suffix not in (".json", ".tsv")), None)
        if rec is None:
            continue
        ev.unlink()
        (ev.with_suffix(".json")).unlink(missing_ok=True)
        target = rec
        break
    return root, target


def _rel(root, path):
    return str(path.relative_to(root)) if path else None


def validation_warnings(app, theme: str) -> None:
    """Recommended fields nobody has answered, on the dataset description."""
    _pane_shot(app, theme, "multimodal_tutorial", "validation_warnings",
               rel="dataset_description.json", base=DATA, flag_todos=False,
               width=560, height=600)


def validation_sidecar_error(app, theme: str) -> None:
    """An error inside a sidecar: a field holding the wrong kind of value."""
    import json
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root = _demo_copy("sidecar_error_demo")
    sc = next((p for p in sorted(root.rglob("*_eeg.json"))), None)
    if sc is None:
        print("  (no EEG sidecar; skipping)")
        return
    doc = json.loads(sc.read_text())
    # A sampling rate typed as text. Reads correctly to a person and is the
    # wrong type to the standard, which is the point of the figure.
    doc["SamplingFrequency"] = "160 Hz"
    sc.write_text(json.dumps(doc, indent=2))
    report = _report(root, flag_todos=False)
    hit = _file_with_rule(report, "JSON_SCHEMA_VALIDATION_ERROR") or \
        _file_with_rule(report, "SIDECAR_VALUE_INCORRECT_TYPE")
    if hit is None:
        print("  (no sidecar type error; skipping)")
        return
    _grab(app, _pane(report, root, hit.path),
          OUT / f"validation_sidecar_error_{theme}.png", 560, 470,
          scroll_to="FILE \u00b7")


def validation_invalid_location(app, theme: str) -> None:
    """A mistyped datatype folder, on the multimodal dataset.

    ``ds_structural_demo`` is the converted multimodal sample with three things
    broken on purpose, each the kind of mistake a person makes by hand:
    ``anat`` renamed to ``anatt``, ``func`` to ``funce``, and an ``echo``
    entity added to an EEG filename. TODO warnings are turned off so the figure
    shows the structural finding rather than a column of unfinished metadata.
    """
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root, ses = _structural_demo()
    if ses is None:
        print("  (no anat folder to mistype; skipping)")
        return
    report = _report(root, flag_todos=False)
    hit = _file_with_rule(report, "INVALID_LOCATION")
    if hit is None:
        print("  (no INVALID_LOCATION; skipping)")
        return
    _grab(app, _pane(report, root, hit.path),
          OUT / f"invalid_location_{theme}.png", 560, 470,
          scroll_to="FILE \u00b7")


def validation_bad_entity(app, theme: str) -> None:
    """An entity the standard does not allow on this kind of file."""
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root, target = _bad_entity_demo()
    report = _report(root, flag_todos=False)
    hit = _file_with_rule(report, "ENTITY_NOT_IN_RULE")
    if hit is None:
        print("  (no ENTITY_NOT_IN_RULE; skipping)")
        return
    _grab(app, _pane(report, root, hit.path),
          OUT / f"validation_bad_entity_{theme}.png", 560, 470,
          scroll_to="FILE \u00b7")


def validation_broken_manifest(app, theme: str) -> None:
    """The knock-on effect: scans.tsv still lists the paths that moved."""
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root, ses = _structural_demo()
    report = _report(root, flag_todos=False)
    hit = _file_with_rule(report, "SCANS_FILENAME_NOT_MATCH_DATASET")
    if hit is None:
        print("  (no scans mismatch; skipping)")
        return
    _grab(app, _pane(report, root, hit.path),
          OUT / f"validation_broken_manifest_{theme}.png", 560, 470,
          scroll_to="FILE \u00b7")


def validation_mm(app, theme: str) -> None:
    """The Editor's validation pane on the converted multimodal dataset.

    A whole four-modality dataset with nothing wrong in it, which is worth a
    figure of its own: every other validation image on the site is a failure.
    """
    root = DATA / "multimodal_tutorial"
    if not root.exists():
        print("  (no tutorial dataset; skipping)")
        return
    report = _report(root, flag_todos=False)
    hit = next((f for f in report.files
                if str(f.path).endswith(".fif")), None)
    _pane_shot(app, theme, "multimodal_tutorial", "mm_validation",
               rel=str(hit.path) if hit else None,
               base=DATA, flag_todos=False, width=560, height=470)


def validation_missing_companion(app, theme: str) -> None:
    """A cross-file warning: a task run with no events table beside it.

    On ``ds_events_demo``, the converted multimodal dataset with one
    ``events.tsv`` deleted, so the figure shows this warning and nothing else.
    It used to be rendered on ``ds_MRI``, which carries structural errors of
    its own, and they appeared stacked above the warning the caption was
    talking about.
    """
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root, target = _events_demo()
    report = _report(root, flag_todos=False)
    hit = _file_with_rule(report, "EVENTS_TSV_MISSING")
    if hit is None:
        print("  (no EVENTS_TSV_MISSING; skipping)")
        return
    _grab(app, _pane(report, root, hit.path),
          OUT / f"validation_missing_events_{theme}.png", 560, 470,
          scroll_to="FILE \u00b7")


def validation_pet_checks(app, theme: str) -> None:
    """A PET cross-field check: numbers in a sidecar that disagree.

    Picks the file where such a finding is the *only* one, so the image shows
    the check rather than a wall of unrelated type errors.
    """
    PET_RULES = ("PET_FRAME_CONSISTENCY", "bidsmgr.pet.time_zero_format",
                 "bidsmgr.pet.recon_parameter_length_mismatch")
    for ds in ("pet_tutorial_dicom", "pet_tutorial_ecat"):
        root = DATA / ds
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

# A recording from the EEG tutorial's own download, pinned rather than globbed
# for the same reason as ``MEG_FIF`` below. This subject is chosen because its
# 100 Hz harmonic stands clear of the noise, which the caption points out.
PSD_EEG = Path(
    "/Users/karelo/Development/datasets/BIDS_Manager/raw_data/EEG"
    "/Raw_workshop-2/sub-003/CLV005.set"
)
# The empty-room recording taken before the session in the MEG download.
MEG_EMPTY_ROOM = Path(
    "/Users/karelo/Development/datasets/BIDS_Manager/raw_data/MEG"
    "/MEG_Elekta_sample_data/sub_ye07us06/220221/task_emptypre.fif"
)


def _psd_dialog(raw, picks=None):
    """The application's own PSD dialog over ``raw``, computed the way the
    viewer computes it."""
    import numpy as np
    import mne
    from bidsmgr.gui.widgets.psd_dialog import PsdDialog

    spectrum = raw.compute_psd(fmin=0.1, fmax=min(raw.info["sfreq"] / 2.0, 150.0),
                               picks=picks, verbose=False)
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
    return PsdDialog(result)


def psd(app, theme: str) -> None:
    """The power spectrum of a real EEG recording.

    The mains peak is the point: it is how you check that the power-line
    frequency you declared is the one actually in the data.
    """
    import mne

    if not PSD_EEG.exists():
        print(f"  (no EEG recording at {PSD_EEG}; skipping)")
        return
    raw = mne.io.read_raw(PSD_EEG, preload=True, verbose=False)
    dlg = _psd_dialog(raw)
    _grab(app, dlg, OUT / f"psd_line_frequency_{theme}.png", 900, 560)


def psd_meg(app, theme: str) -> None:
    """The same dialog on the MEG sample's empty-room recording, on the
    per-type average, because that is the recording the MEG tutorial tells
    the reader to check.

    The MEG tutorial needs its own figure, not the EEG one: on these
    magnetometers the tallest mains spike is the 100 Hz harmonic and the
    50 Hz fundamental barely rises, which is the opposite of what the EEG
    figure teaches and exactly what somebody reading an MEG spectrum meets.
    """
    import mne

    if not MEG_EMPTY_ROOM.exists():
        print(f"  (no empty-room recording at {MEG_EMPTY_ROOM}; skipping)")
        return
    raw = mne.io.read_raw_fif(str(MEG_EMPTY_ROOM), preload=True, verbose="ERROR")
    dlg = _psd_dialog(raw, picks=["mag", "grad"])
    dlg._tabs.setCurrentIndex(1)
    _grab(app, dlg, OUT / f"psd_meg_{theme}.png", 900, 560)



# ----------------------------------------------------------------------
# 1.3.0: restructuring, and the parts of the Editor the site never showed
# ----------------------------------------------------------------------


# Where the figures below stage their dataset.
#
# NOT the real one under ``DATA``, for two reasons. Every dialog here would
# CHANGE a dataset if it were applied, and although none of them apply
# anything, a delete dialog aimed at the data every other figure on the site
# renders from is one stray click from a bad afternoon.
#
# And these dialogs PRINT THEIR PATH. Rendering from ``DATA`` puts the author's
# home directory, including their username, into a published screenshot. A
# neutral staging path shows a reader something anonymous and short instead.
DEMO_ROOT = Path("/tmp/bids")


def _demo_copy(name: str = "multimodal_demo"):
    """A throwaway copy of the tutorial dataset, at a neutral path."""
    import json
    import shutil
    dst = DEMO_ROOT / name
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(DATA / "multimodal_tutorial", dst)
    # The test dataset is titled "raw", after the folder it was scanned from.
    # Anything that prints the dataset TITLE, the Dashboard header for one,
    # then reads as if the tool got it wrong. Retitle the throwaway copy.
    desc = dst / "dataset_description.json"
    try:
        doc = json.loads(desc.read_text())
        if doc.get("Name") in (None, "", "raw"):
            doc["Name"] = "Multimodal sample"
            desc.write_text(json.dumps(doc, indent=2) + "\n")
    except (OSError, ValueError):
        pass
    return dst


def editor_dashboard(app, theme: str) -> None:
    """What is in this dataset, counted.

    Rendered on the tutorial dataset precisely because it is UNEVEN: one
    subject has three sessions and four modalities, the other a single PET
    scan. Bars of differing length are the whole argument for the figure, and
    a tidy dataset produces a screenshot that argues against it.
    """
    from bidsmgr.gui.dashboard_dialog import DashboardDialog
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root = _demo_copy()
    dlg = DashboardDialog(root, _report(root))
    _grab(app, dlg, OUT / f"editor_dashboard_{theme}.png", 800, 1125)


def editor_entities(app, theme: str) -> None:
    """Adding an entity, with the plan already made.

    An empty dialog shows nothing, so this one has a value typed and a
    preview populated. What the reader should notice is how SHORT the entity
    list is: it holds only what the standard permits for this kind of file,
    which is the feature, and no amount of prose demonstrates it as quickly.
    """
    from bidsmgr.gui.edit_entities_dialog import EditEntitiesDialog
    root = _demo_copy()
    # A functional run, which carries NO acq- yet. The anatomy in this dataset
    # already has one, so adding it there reads as "2 of 2 would be changed",
    # which demonstrates the wrong half of the feature: this figure is about
    # giving a recording a label it lacks.
    target = next(root.rglob("*_bold.nii.gz"), None)
    if target is None:
        print("  (no functional run; skipping)")
        return
    dlg = EditEntitiesDialog(root, [target])
    at = dlg._entity.findData("acq")
    if at >= 0:
        dlg._entity.setCurrentIndex(at)
    dlg._value.setCurrentText("highres")
    dlg.plan_now()
    app.processEvents()
    _grab(app, dlg, OUT / f"editor_entities_{theme}.png", 1020, 780)


def editor_sessions(app, theme: str) -> None:
    """Creating a session, showing that the FOLDER moves too.

    The second column carries the whole destination path rather than just the
    new name, which is the only way a still image can show that the recordings
    change folder and not merely filename.
    """
    from bidsmgr.gui.edit_entities_dialog import EditEntitiesDialog
    root = _demo_copy()
    # A subject that has NO session yet, so this is a genuine creation. Run it
    # on one that already has sessions and the dialog truthfully reports that
    # every file would be changed, which teaches the wrong thing: this figure
    # is about recordings gaining a session they did not have. It is also
    # short, so no destination path is truncated.
    subject = next((p for p in sorted(root.glob("sub-*"))
                    if p.is_dir() and not any(p.glob("ses-*"))), None)
    if subject is None:
        print("  (every subject already has a session; skipping)")
        return
    dlg = EditEntitiesDialog(root, [subject], session_mode=True)
    dlg._value.setCurrentText("baseline")
    dlg.plan_now()
    app.processEvents()
    _grab(app, dlg, OUT / f"editor_sessions_{theme}.png", 1020, 760)


def editor_delete(app, theme: str) -> None:
    """A deletion, with the repairs visible.

    "Follows automatically" is expanded on purpose. Collapsed, the figure
    shows a list of files being removed, which is the unremarkable half. The
    repairs underneath, the scans rows and the references, are the argument
    for the feature existing at all.
    """
    from bidsmgr.gui.delete_dialog import DeleteDialog
    root = _demo_copy()
    # An ANATOMY folder, not a whole session. A session deletes a dozen files,
    # and the file list then fills the preview and pushes the repairs out of
    # sight, which is the one thing this figure has to show. Anatomy is small
    # AND well connected: the fieldmap points at it, so the repairs include a
    # scans row and an IntendedFor entry rather than only an emptied folder.
    target = next((p for p in sorted(root.rglob("anat")) if p.is_dir()), None)
    if target is None:
        print("  (no anat folder; skipping)")
        return
    dlg = DeleteDialog(root, [target])
    dlg._preview.expandAll()
    app.processEvents()
    _grab(app, dlg, OUT / f"editor_delete_{theme}.png", 1000, 720)


def editor_move_preview(app, theme: str) -> None:
    """The preview tree, nested, with one file deliberately unticked.

    Every restructuring action previews into this same widget, so the figure
    is about the WIDGET rather than about renaming: per-file choice and the
    part-ticked folder above it, which no amount of prose conveys as fast.
    Rendered from Rename because a rename reaches across sessions, so the tree
    has more than one level of nesting to show.
    """
    from bidsmgr.gui.rename_entity_dialog import RenameEntityDialog
    from PyQt6.QtCore import Qt
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root = _demo_copy()
    dlg = RenameEntityDialog(root, entity="task", value="rest")
    dlg._new.setText("restingstate")
    dlg.plan_now()
    app.processEvents()
    dlg._preview.expandAll()
    app.processEvents()
    # Untick ONE file. A fully ticked tree looks like a list of what is about
    # to happen; a part-ticked one is visibly a choice, and the folder above
    # it goes half-checked, which is the behaviour worth showing.
    it = dlg._preview.topLevelItem(0)
    while it is not None and it.childCount():
        it = it.child(0)
    if it is not None:
        it.setCheckState(0, Qt.CheckState.Unchecked)
        app.processEvents()
    _grab(app, dlg, OUT / f"editor_move_preview_{theme}.png", 1020, 780)


def editor_deface(app, theme: str) -> None:
    """Removing faces, with the skipped images visible.

    The skipped list is the half that has to be on screen: an image quietly
    passed over is a face quietly kept. So this frame is taken on a dataset
    that HAS something to skip.
    """
    from bidsmgr.gui.deface_dialog import DefaceDialog
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root = _demo_copy("deface_demo")
    dlg = DefaceDialog(root)
    app.processEvents()
    _grab(app, dlg, OUT / f"editor_deface_{theme}.png", 900, 760)


def editor_strip(app, theme: str) -> None:
    """Keeping only the brain, and where the result goes.

    The sentence that matters is in the status line: the output is a
    DERIVATIVE, and the original scan is untouched. A frame that cropped it
    out would document the wrong mental model.
    """
    from bidsmgr.deface import engines
    from bidsmgr.gui.deface_dialog import DefaceDialog
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root = _demo_copy("strip_demo")
    dlg = DefaceDialog(root, kind=engines.KIND_STRIP)
    app.processEvents()
    _grab(app, dlg, OUT / f"editor_strip_{theme}.png", 900, 760)


def _defaced_demo(name: str):
    """A dataset with one image defaced and its original kept.

    Built by running the real engine, not by faking a sidecar: the restore
    dialog lists what it can actually restore, so a fake would either show
    nothing or show a row that does not work.
    """
    from bidsmgr.deface.apply import deface_dataset
    root = _demo_copy(name)
    deface_dataset(root, keep_original_in_sourcedata=True)
    return root


def editor_deface_revert(app, theme: str) -> None:
    """Putting the face back, and saying where each copy comes from."""
    from bidsmgr.gui.deface_revert_dialog import DefaceRevertDialog
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root = _defaced_demo("revert_demo")
    dlg = DefaceRevertDialog(root)
    app.processEvents()
    _grab(app, dlg, OUT / f"editor_deface_revert_{theme}.png", 860, 620)


def editor_compare_picker(app, theme: str) -> None:
    """Choosing the second image from the dataset, with the filter working.

    Rendered WITH a filter typed. An empty picker looks like a file dialog;
    the point is that two words narrow the whole dataset to one image.
    """
    from bidsmgr.gui.widgets.nifti_picker import NiftiPickerDialog
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root = _demo_copy("picker_demo")
    dlg = NiftiPickerDialog(root, title="Choose the right image")
    dlg._filter.setText("001 t1")
    app.processEvents()
    _grab(app, dlg, OUT / f"editor_compare_picker_{theme}.png", 680, 560)


def editor_tree_menu(app, theme: str) -> None:
    """The right-click on an image, where all four actions are reachable."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QMenu, QTreeWidgetItemIterator
    from bidsmgr.gui.widgets.bids_tree_pane import PATH_ROLE, BidsTreePane
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root = _demo_copy("tree_menu_demo")
    pane = BidsTreePane()
    pane.set_root(root)
    # Repeatedly, because the tree fills a folder's children only when it is
    # expanded: one pass opens the subjects and leaves every datatype folder
    # empty, so the iterator below finds no files at all.
    for _ in range(6):
        pane._tree.expandAll()
        app.processEvents()
    app.processEvents()

    target = None
    it = QTreeWidgetItemIterator(pane._tree)
    while it.value():
        value = it.value().data(0, PATH_ROLE)
        if value and str(value).endswith("T1w.nii.gz"):
            target = it.value()
            break
        it += 1
    if target is None:
        print("  (no anatomical image in the demo dataset; skipping)")
        return

    # The menu is built and shown rather than exec'd: exec spins its own
    # event loop and would never return here.
    captured = {}

    def _capture(self, *a, **k):
        captured["menu"] = self
        return None

    original = QMenu.exec
    QMenu.exec = _capture
    try:
        pane._tree.setCurrentItem(target)
        pane._tree.itemAt = lambda _pos: target
        from PyQt6.QtCore import QPoint
        pane._on_show_context_menu(QPoint(1, 1))
    finally:
        QMenu.exec = original

    menu = captured.get("menu")
    if menu is None:
        print("  (no context menu; skipping)")
        return
    menu.adjustSize()
    app.processEvents()
    # The menu's OWN size, not a guessed box. Too small and Qt wraps it into
    # two columns, which is not what anybody sees when they right-click; too
    # large and the frame is mostly empty background. Render this one with
    # QT_QPA_PLATFORM=cocoa: the offscreen platform reports a short screen,
    # and a menu taller than the screen is exactly what Qt splits.
    hint = menu.sizeHint()
    _grab(app, menu, OUT / f"editor_tree_menu_{theme}.png",
          hint.width(), hint.height())


def editor_fixups(app, theme: str) -> None:
    """The repairs the dataset can be given, with what each would do.

    Rendered on a COPY, because two of the three buttons in it write files,
    and because the dialog prints the dataset path in its own header.
    """
    from bidsmgr.gui.fixups_dialog import FixupsDialog
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root = _demo_copy()
    dlg = FixupsDialog(root, report=_report(root))
    app.processEvents()
    # Tall enough for all FIVE cards. At the dialog's own default height the
    # last ones are below the scroll, and a reader would never learn they exist.
    _grab(app, dlg, OUT / f"editor_fixups_{theme}.png", 860, 1570)


def editor_fix_all(app, theme: str) -> None:
    """One finding, and every file it fired on, each with its current value.

    The figure has to show the LIST, not the count. "12 files" says how many
    and nothing else; what makes the feature safe to use is that every
    candidate is named, shows what it says now, and is ticked only where the
    value would actually change.
    """
    from bidsmgr.editor import bulk_edit as be
    from bidsmgr.editor.grouping import group_report
    from bidsmgr.gui.bulk_field_dialog import BulkFieldDialog
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    root = _demo_copy()
    report = _report(root)
    # The best frame is the finding that fired on the MOST files: a group of
    # two demonstrates nothing that one file would not.
    best, cands = None, []
    for grp in sorted(group_report(report), key=lambda g: -g.count):
        if not grp.field:
            continue
        found = be.candidates(root, grp.field,
                              paths=[root / p for p in grp.files])
        if len(found) > len(cands):
            best, cands = grp, found
    if best is None or not cands:
        print("  (no grouped finding with a field; skipping)")
        return
    dlg = BulkFieldDialog(
        root, best.field, candidates=cands,
        title=f"Fix {best.field} in {len(cands)} file(s)",
    )
    # With no value typed the "becomes" column is empty, and the figure then
    # shows only half of what it is for. Type one so each row reads
    # "now: not set, becomes: ...".
    from PyQt6.QtWidgets import QLineEdit
    if isinstance(dlg._value_edit, QLineEdit):
        dlg._value_edit.setText("Department of Psychology")
    app.processEvents()
    _grab(app, dlg, OUT / f"editor_fix_all_{theme}.png", 1000, 700)


# ----------------------------------------------------------------------
# The signal viewers
# ----------------------------------------------------------------------

# Real recordings, from the outputs the project already keeps. Named here
# rather than found by glob so a figure is reproducible: if one of these moves,
# the target says so instead of quietly shooting a different recording.
MEG_FIF = Path(
    "/Users/karelo/Development/datasets/BIDS_Manager/raw_data/MEG"
    "/MEG_Elekta_sample_data/sub_ye07us06/220221/task_driving_run_02.fif"
)
# One run of a real study, split by the ``recording`` entity the way BIDS
# splits physio: a cardiac trace, a respiratory belt, an ECG and a trigger,
# four files describing one acquisition. Chosen because all four carry signal
# over the same stretch, which is what makes a combined figure show anything.
PHYSIO_ECG = BIDS / ("multimodal_physio/bids/mutilmodal/sub-003/ses-pre/func/"
                     "sub-003_ses-pre_task-rest_recording-ecg_physio.tsv.gz")
PHYSIO_GAPPY = BIDS / ("ds_4/sub-001/func/sub-001_task-dmaging_run-03"
                       "_recording-externalTrigger_physio.tsv.gz")
MRS_SVS = BIDS / "ds_8/sub-002/mrs/sub-002_run-01_svs.nii.gz"


def _meeg_view(app, *, window: float = 10.0, shown: int = 8,
               ch_type: str = "mag", band=(1.0, 40.0),
               start: float = 40.0):
    """The shared time-series view with a real MEG recording loaded.

    Loaded synchronously rather than through the worker: a screenshot has no
    event loop to wait in, and the worker exists for the GUI's sake, not the
    reader's.

    ``ch_type`` defaults to the magnetometers rather than ``all``. A MEGIN
    file's first twenty channels are the internal active shielding and the
    system status, whose amplitudes swamp the plot: a figure of them is a
    figure of the scanner's housekeeping, not of anybody's data.
    """
    import mne
    from bidsmgr.gui.widgets.time_series_view import TimeSeriesView

    raw = mne.io.read_raw_fif(str(MEG_FIF), preload=True, verbose="ERROR")
    view = TimeSeriesView()
    view.load_raw(raw)
    if ch_type:
        index = view.cmb_ch_type.findText(ch_type)
        if index >= 0:
            view.cmb_ch_type.blockSignals(True)
            view.cmb_ch_type.setCurrentIndex(index)
            view.cmb_ch_type.blockSignals(False)
            view._active_ch_type = ch_type
    view._time_window = window
    view._visible_channels = shown
    # A few seconds in, NOT at sample zero. A filter has no data beyond the
    # first sample, so the very start of any recording carries a transient
    # that is inherent rather than a fault. It is worth explaining in prose
    # and it is not what a figure of the viewer should be showing.
    view._time_start = min(start, max(0.0, view._duration - window))
    view.spn_window.blockSignals(True)
    view.spn_window.setValue(window)
    view.spn_window.blockSignals(False)
    view.spn_n.blockSignals(True)
    view.spn_n.setValue(shown)
    view.spn_n.blockSignals(False)
    # Band-passed, because that is how MEG is read. Raw, the mains and the
    # drift are most of the amplitude and twenty traces overlap into one
    # band: a figure of unfiltered MEG shows the viewer working and the data
    # unreadable, which teaches the reader the wrong thing about both.
    if band:
        view._current_filter = band
        view.spn_hp.blockSignals(True)
        view.spn_hp.setValue(band[0] or 0.0)
        view.spn_hp.blockSignals(False)
        view.spn_lp.blockSignals(True)
        view.spn_lp.setValue(band[1] or 0.0)
        view.spn_lp.blockSignals(False)
    view._update_display_indices()
    view._update_channel_scrollbar()
    view._redraw()
    app.processEvents()
    return view


def _physio_view(app, path: Path, *, together: bool = False):
    """The same view on a physio recording, optionally with its relatives."""
    from bidsmgr.gui.widgets.physio_viewer import (
        build_combined_raw, build_raw, read_columns, read_timing,
        related_recordings,
    )
    from bidsmgr.gui.widgets.time_series_view import TimeSeriesView

    if together:
        raw, gaps = build_combined_raw(related_recordings(path))
    else:
        columns, _total, step = read_columns(path)
        raw, gaps = build_raw(columns, read_timing(path), step)
    view = TimeSeriesView()
    # Physio is the one consumer that offers Fit all: a channel or four fits in
    # a window whole, where a 323-channel MEG recording does not.
    view.enable_fit_all(True)
    view.load_raw(raw, gaps=gaps)
    app.processEvents()
    return view


def viewer_meeg(app, theme: str) -> None:
    """The shared viewer on real MEG: the controls, wrapped, over real traces."""
    if not MEG_FIF.exists():
        print("  (no MEG sample; skipping)")
        return
    view = _meeg_view(app)
    _grab(app, view, OUT / f"viewer_meeg_{theme}.png", 1180, 760)


def viewer_physio(app, theme: str) -> None:
    """One physio channel. The channel controls are gone, because they would
    each have one answer."""
    if not PHYSIO_ECG.exists():
        print("  (no physio sample; skipping)")
        return
    view = _physio_view(app, PHYSIO_ECG)
    view._time_window = min(8.0, view._duration)
    view._time_start = min(30.0, max(0.0, view._duration - view._time_window))
    view.spn_window.blockSignals(True)
    view.spn_window.setValue(view._time_window)
    view.spn_window.blockSignals(False)
    view._redraw()
    app.processEvents()
    _grab(app, view, OUT / f"viewer_physio_{theme}.png", 1180, 620)


def viewer_physio_together(app, theme: str) -> None:
    """All of this run: the cardiac trace, the belt and the trigger on one
    grid, which is the only way to see whether they line up."""
    if not PHYSIO_ECG.exists():
        print("  (no physio sample; skipping)")
        return
    view = _physio_view(app, PHYSIO_ECG, together=True)
    view._time_window = 12.0
    # Into the recording, where all four are present. At sample zero some of
    # them have not started and the figure would be flat lines illustrating
    # nothing.
    view._time_start = 30.0
    view.spn_window.blockSignals(True)
    view.spn_window.setValue(view._time_window)
    view.spn_window.blockSignals(False)
    view._redraw()
    app.processEvents()
    _grab(app, view, OUT / f"viewer_physio_together_{theme}.png", 1180, 620)


def viewer_physio_gaps(app, theme: str) -> None:
    """A trace whose dropped samples are drawn as breaks. This file is 99.7 per
    cent absent, which is what makes the point visible at all."""
    if not PHYSIO_GAPPY.exists():
        print("  (no gappy physio sample; skipping)")
        return
    view = _physio_view(app, PHYSIO_GAPPY)
    view._fit_all()
    app.processEvents()
    _grab(app, view, OUT / f"viewer_physio_gaps_{theme}.png", 1180, 560)


def _mrs_pane(app, path: Path):
    """The MRS pane with a spectrum read and drawn, synchronously."""
    from bidsmgr.gui.widgets.mrs_spectrum import read_mrs
    from bidsmgr.gui.widgets.mrs_viewer_pane import MrsViewerPane

    pane = MrsViewerPane()
    pane._path = path
    pane._on_read((path, read_mrs(path)))
    app.processEvents()
    return pane


def viewer_mrs(app, theme: str) -> None:
    """The spectrum, with the metabolite names staggered so none covers
    another."""
    if not MRS_SVS.exists():
        print("  (no MRS sample; skipping)")
        return
    pane = _mrs_pane(app, MRS_SVS)
    pane._reset_view()
    app.processEvents()
    _grab(app, pane, OUT / f"viewer_mrs_{theme}.png", 1120, 640)


def viewer_mrs_fid(app, theme: str) -> None:
    """The FID page, so the second page is discoverable at all."""
    if not MRS_SVS.exists():
        print("  (no MRS sample; skipping)")
        return
    pane = _mrs_pane(app, MRS_SVS)
    pane._domain.setCurrentIndex(1)
    app.processEvents()
    _grab(app, pane, OUT / f"viewer_mrs_fid_{theme}.png", 1120, 620)


def line_dialog(app, theme: str) -> None:
    """The Line popup with a swatch per channel type and Reset defaults."""
    from bidsmgr.gui.widgets.line_style_dialog import MAX_WIDTH, LineStyleDialog

    types = ["mag", "grad", "eeg", "eog", "ecg", "stim"]
    dlg = LineStyleDialog(0, None, channel_types=types,
                          max_width=MAX_WIDTH, traces_shown=2)
    app.processEvents()
    _grab(app, dlg, OUT / f"line_dialog_{theme}.png",
          max(dlg.sizeHint().width(), 460), dlg.sizeHint().height())


def line_dialog_capped(app, theme: str) -> None:
    """The same popup on a many-channel view: the slider is disabled and says
    why, rather than offering a width that would be capped on the way out."""
    from bidsmgr.gui.widgets.line_style_dialog import LineStyleDialog

    types = ["mag", "grad", "stim"]
    dlg = LineStyleDialog(0, None, channel_types=types,
                          max_width=1, traces_shown=20)
    app.processEvents()
    _grab(app, dlg, OUT / f"line_dialog_capped_{theme}.png",
          max(dlg.sizeHint().width(), 460), dlg.sizeHint().height())


def bulk_edit_entities(app, theme: str) -> None:
    """Bulk edit on the WHOLE inventory, removing the acquisition label.

    The case the per-row rule exists for: select everything, ask for ``acq``
    to go, and it comes off only the rows that have one. A selection where
    every row qualifies shows the dialog working and hides the point.
    """
    from bidsmgr.gui.bulk_edit_dialog import BulkEditDialog
    from bidsmgr.gui.models import InventoryTableModel

    df = _read("multimodal")
    model = InventoryTableModel(df)
    rows = list(range(len(df)))
    dlg = BulkEditDialog(model, rows)
    for i in range(dlg._col_combo.count()):
        if dlg._col_combo.itemText(i).lower().startswith("acq"):
            dlg._col_combo.setCurrentIndex(i)
            break
    app.processEvents()
    dlg._remove_check.setChecked(True)
    app.processEvents()
    _grab(app, dlg, OUT / f"bulk_edit_entities_{theme}.png", 760, 620)

def manage_columns(app, theme: str) -> None:
    """The Manage columns dialog, with Reset defaults."""
    from bidsmgr.gui.column_manager_dialog import ColumnManagerDialog
    from bidsmgr.gui.models import COLUMNS

    dlg = ColumnManagerDialog({c.key: c.default_visible for c in COLUMNS})
    app.processEvents()
    _grab(app, dlg, OUT / f"manage_columns_{theme}.png", 640, 720)


def properties_pet_dose(app, theme: str) -> None:
    """The DOSE FILE section, in place inside the PET region of a PET row."""
    df = _read("pet")
    panel = _panel(df)
    # Cropped to the two sections this figure is about. Taller, it runs on
    # into "Already answered by the conversion", which on a row that has NOT
    # been converted yet is a column of empty fields under a heading saying
    # they are answered: true of the finished dataset, a contradiction here.
    _grab(app, panel, OUT / f"properties_pet_dose_{theme}.png", 520, 330,
          expand=True, scroll_to="dose file")


def editor_tools_menu(app, theme: str) -> None:
    """Where all of this lives. People cannot use what they cannot find."""
    from bidsmgr.gui.editor_panel import EditorPanel
    if not (DATA / "multimodal_tutorial").exists():
        print("  (no tutorial dataset; skipping)")
        return
    panel = EditorPanel()
    panel._set_root(_demo_copy(), persist=False)
    app.processEvents()
    menu = panel._tools_menu
    menu.adjustSize()
    app.processEvents()
    # The menu's own size: it has grown, and a fixed box either clips the
    # bottom entries or pads the frame with empty background.
    hint = menu.sizeHint()
    _grab(app, menu, OUT / f"editor_tools_menu_{theme}.png",
          hint.width(), hint.height())


ASSETS = {
    "inventory-multimodal": inventory_multimodal,
    "inventory-pet-formats": inventory_pet_formats,
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
    "properties-mri": properties_mri,
    "properties-meg": properties_meg,
    "properties-companions": properties_companions,
    "inventory-eeg": inventory_eeg,
    "inventory-meg": inventory_meg,
    "inventory-skipped": inventory_skipped,
    "inventory-include": inventory_include,
    "settings": settings_all,
    "editor-tree": editor_tree,
    "editor-tree-mm": editor_tree_mm,
    "editor-window": editor_window,
    "window-home": window_home,
    "window-converter": window_converter,
    "window-editor": window_editor,
    "sidecar-form": sidecar_form,
    "sidecar-form-pet": sidecar_form_pet,
    "validation-scopes": validation_scopes,
    "validation-provenance-pet": validation_provenance_pet,
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
    "psd-meg": psd_meg,
    "editor-dashboard": editor_dashboard,
    "editor-entities": editor_entities,
    "editor-sessions": editor_sessions,
    "editor-delete": editor_delete,
    "viewer-meeg": viewer_meeg,
    "viewer-physio": viewer_physio,
    "viewer-physio-together": viewer_physio_together,
    "viewer-physio-gaps": viewer_physio_gaps,
    "viewer-mrs": viewer_mrs,
    "viewer-mrs-fid": viewer_mrs_fid,
    "line-dialog": line_dialog,
    "line-dialog-capped": line_dialog_capped,
    "bulk-edit-entities": bulk_edit_entities,
    "manage-columns": manage_columns,
    "properties-pet-dose": properties_pet_dose,
    "editor-tools-menu": editor_tools_menu,
    "editor-deface": editor_deface,
    "editor-strip": editor_strip,
    "editor-deface-revert": editor_deface_revert,
    "editor-compare-picker": editor_compare_picker,
    "editor-tree-menu": editor_tree_menu,
    "editor-fixups": editor_fixups,
    "editor-move-preview": editor_move_preview,
    "editor-fix-all": editor_fix_all,
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

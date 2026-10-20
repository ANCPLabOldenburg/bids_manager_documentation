"""The Editor: validation, sidecars and tables, the tools that change a dataset."""

from __future__ import annotations

from pathlib import Path

import harness as H
from harness import Region, Shot

SUB = "sub-001/ses-01"


#: The Editor's three panels at the 1.15 font scale want more room than
#: 1440 px leaves the Validation panel (a finding's rule name is cut short).
SIZE = (1600, 1000)


def _editor(state: str = "converted", validate: bool = True, size=SIZE):
    root = H.restore(state)
    win = H.main_window("welcome", size)
    H.open_project(win, root, "editor")
    ed = win.editor
    H.pump(settle=40)
    report = None
    if validate:
        from bidsmgr.editor import validate as run_validate
        schema, max_rows, todos = ed._validation_engine_opts()
        # As Validate dataset does, Deep checks as the toolbar has them (on).
        report = run_validate(root, strict=ed._strict_btn.isChecked(), schema=schema,
                              max_rows=max_rows, flag_todos=todos)
        ed._on_report_ready(report, root)
        H.pump(settle=40)
    return win, ed, root, report


def _select(ed, root, rel: str, wait: float = 0.6):
    ed.select_file_in_tree(Path(root) / rel)
    H.pump(settle=30)
    if wait:
        H.wait(wait)
        H.pump(settle=30)


def _expand(ed, depth: int = 3):
    from PyQt6.QtWidgets import QTreeWidget
    tree = ed._tree_pane.findChild(QTreeWidget)
    tree.expandToDepth(depth)
    H.pump(settle=20)
    return tree


def _show(dlg, size=None):
    from PyQt6.QtCore import Qt
    dlg.setWindowModality(Qt.WindowModality.NonModal)
    if size:
        dlg.resize(*size)
    dlg.show()
    H.pump(settle=50)
    return dlg


def _close(dlg):
    try:
        dlg.done(0)
    except Exception:  # noqa: BLE001
        dlg.close()
    H.pump(settle=10)


def _splitter_sizes(ed, sizes):
    from PyQt6.QtWidgets import QSplitter
    for sp in ed.findChildren(QSplitter):
        names = [getattr(sp.widget(i), "_title", None) for i in range(sp.count())]
        if "Viewer" in names and "BIDS tree" in names:
            sp.setSizes(list(sizes))
            H.pump(settle=20)
            return sp


# ------------------------------------------------------------ chapter 1 and 9
def editor_map():
    win, ed, root, report = _editor()
    _expand(ed, 3)
    _select(ed, root, f"{SUB}/func/sub-001_ses-01_task-rest_bold.json")
    _splitter_sizes(ed, [290, 750, 540])
    H.take(Shot("editor-map", "The Editor on the converted sample: the toolbar, the dataset's path, the BIDS "
                "tree with its validation marks, the BOLD run's sidecar as a form, and its findings.",
                win, window=True,
                regions=[Region("toolbar", "The toolbar: open, undo, validate, deep checks, tools, the counts",
                                ed._open_btn.parentWidget(), anchor="l"),
                         Region("path", "The dataset and how it is open", ed._path_bar, anchor="l"),
                         Region("tree", "The BIDS tree", ed._tree_frame),
                         Region("viewer", "The viewer: a form, a table, an image, a signal", ed._center_frame),
                         Region("validation", "Validation", ed._validation_frame)],
                allow_elided=("QTreeWidget",)))
    H.take(Shot("l01-tree", "The converted sample in the Editor's BIDS tree: one subject, one session, "
                "nine datatype folders, each with how many files it holds.", win, crop_to=ed._tree_frame,
                allow_elided=("QTreeWidget",)))


def validating():
    win, ed, root, report = _editor()
    tree = _expand(ed, 3)
    x, y, w, h = H._rect_in(ed._open_btn.parentWidget(), win)
    H.take(Shot("l09-toolbar", "The Editor's toolbar after validating the dataset: 27 files clean, 112 "
                "warnings and 1 error.", win, crop=(x, y, w, h)))
    H.take(Shot("l09-tree-badges", "The BIDS tree after validation: each file marked clean, with warnings or "
                "with errors, and each folder with its counts.", win, crop_to=ed._tree_frame,
                allow_elided=("QTreeWidget",)))
    _select(ed, root, f"{SUB}/func/sub-001_ses-01_task-rest_bold.json")
    _splitter_sizes(ed, [290, 750, 540])
    H.take(Shot("l09-validation-file", "The Validation panel for the BOLD sidecar: the dataset's, the "
                "folder's and the file's findings, and the schema audit.", win, crop_to=ed._validation_frame))
    vp = ed._validation_pane
    vp._group_mode_btn.click()
    _splitter_sizes(ed, [250, 650, 680])
    H.pump(settle=30)
    H.take(Shot("l09-validation-dataset", "The Validation panel's Whole dataset view: every kind of finding "
                "once, with the number of files it fired on.", win, crop_to=ed._validation_frame))
    H.button(vp, "This file").click()
    H.pump(settle=20)
    # The errors: the PET sidecar's reconstruction units, then the eye tracker's screen.
    _splitter_sizes(ed, [250, 820, 510])
    _select(ed, root, f"{SUB}/pet/sub-001_ses-01_pet.json", wait=1.0)
    ed._sidecar_form.focus_field("ReconMethodParameterUnits")
    H.pump(settle=30)
    x, y, w, h = H._rect_in(ed._center_frame, win)
    x2, y2, w2, h2 = H._rect_in(ed._validation_frame, win)
    H.take(Shot("l09-error", "The PET sidecar with ReconMethodParameterUnits marked, and its error in the "
                "Validation panel: a field the standard requires and no TODO can stand in for.", win,
                crop=(x, y, x2 + w2 - x, h), allow_elided=("QTableView",)))
    _splitter_sizes(ed, [250, 680, 650])
    _select(ed, root, f"{SUB}/beh/sub-001_ses-01_task-rest_recording-eye1_physio.tsv.gz", wait=1.0)
    tv = ed._tsv_viewer
    H.pump(lambda: getattr(tv, "_loader", None) is None, timeout=30, settle=30)
    # The recording as a recording (the table shows its first row as a header).
    H.button(tv, "Visualize").click()
    H.pump(settle=40)
    H.wait(2.5)
    H.pump(settle=40)
    x, y, w, h = H._rect_in(ed._center_frame, win)
    x2, y2, w2, h2 = H._rect_in(ed._validation_frame, win)
    H.take(Shot("l09-eye-error", "The first eye's recording, its gaze and pupil size plotted, and its error: "
                "the events file of the run it was recorded during must say how the stimuli were shown on "
                "the screen.", win,
                crop=(x, y, x2 + w2 - x, h), allow_elided=("QTableView", "QTreeWidget")))


def fixups():
    win, ed, root, report = _editor()
    from bidsmgr.gui.fixups_dialog import FixupsDialog
    d = _show(FixupsDialog(root, ed, report=report), (760, 820))
    H.take(Shot("l09-fixups", "Fix up this dataset: readiness to share, missing companion files, the citation "
                "file, repeated metadata and unanswered fields.", d))
    _close(d)


# ------------------------------------------------------------- chapter 10
def editing():
    win, ed, root, report = _editor("fixed")
    _expand(ed, 3)
    _select(ed, root, f"{SUB}/func/sub-001_ses-01_task-rest_bold.json")
    _splitter_sizes(ed, [300, 840, 440])
    form = ed._sidecar_form
    H.take(Shot("l10-sidecar-bids", "The BOLD run's sidecar in the BIDS view: its fields grouped by level, each "
                "with the standard's description, findings marked.", win, crop_to=ed._center_frame))
    form._apply_view_mode("tree", persist=False)
    H.pump(settle=30)
    H.take(Shot("l10-sidecar-tree", "The same sidecar in the Tree view: keys and values as the file holds them.",
                win, crop_to=ed._center_frame, allow_elided=("QTreeWidget",)))
    form._apply_view_mode("bids", persist=False)
    H.pump(settle=20)
    search = getattr(form, "_search", None) or H.find(form, cls=None, name="search-field")
    from PyQt6.QtWidgets import QLineEdit
    field = search if isinstance(search, QLineEdit) else (search.findChild(QLineEdit) if search else None)
    if field is not None:
        field.setText("Task")
        H.pump(settle=40)
        H.take(Shot("l10-search", "Searching the sidecar for Task: only the fields whose name, value or "
                    "description match stay, with the count.", win, crop_to=ed._center_frame))
        field.clear()
        H.pump(settle=20)
    _select(ed, root, "participants.tsv", wait=1.0)
    H.pump(lambda: getattr(ed._tsv_viewer, "_loader", None) is None, timeout=20, settle=40)
    H.take(Shot("l10-tsv", "participants.tsv in the table viewer: one row, with the columns the participants "
                "spreadsheet and the DICOM headers gave.", win, crop_to=ed._center_frame,
                allow_elided=("QTableView",)))


# ------------------------------------------------------------- chapter 11
def tools_menu():
    win, ed, root, report = _editor("edited")
    _expand(ed, 2)
    from PyQt6.QtCore import QPoint
    btn = ed._tools_btn
    ed._tools_menu.popup(btn.mapToGlobal(QPoint(0, btn.height() + 2)))
    H.pump(settle=40)
    x, y, w, h = H._rect_in(btn, win)
    mx, my, mw, mh = H._global_rect_in(ed._tools_menu, win)
    H.take(Shot("l11-tools-menu", "The Editor's Tools menu: look at the dataset, check and repair, names and "
                "structure, identifiable data, remove.", win,
                crop=(0, 0, min(win.width(), max(x + 640, mx + mw + 24)), min(win.height(), my + mh + 16)),
                popups=[ed._tools_menu], allow_elided=("QTreeWidget",)))
    ed._tools_menu.hide()


def tree_menu():
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import QApplication, QTreeWidget
    win, ed, root, report = _editor("edited", size=(1600, 1240))
    tree = _expand(ed, 3)
    target = Path(root) / f"{SUB}/eeg/sub-001_ses-01_task-rest_eeg.edf"
    ed.select_file_in_tree(target)
    H.pump(settle=10)
    item = tree.currentItem()
    # Select its sidecar, so the Viewer shows a form, then right-click the recording.
    ed.select_file_in_tree(Path(root) / f"{SUB}/eeg/sub-001_ses-01_task-rest_eeg.json")
    H.pump(settle=40)
    got = {}

    def grab():
        pop = QApplication.activePopupWidget()
        if pop is None:
            QTimer.singleShot(100, grab)
            return
        H.pump(settle=20)
        x, y, w, h = H._global_rect_in(pop, win)
        try:
            H.take(Shot("l11-tree-menu", "The BIDS tree's right-click menu on the resting EEG recording: "
                        "references, rename its entities, add or remove one, take it out of its session, "
                        "remove a face, delete it, and copy its path.",
                        win, crop=(0, 60, min(win.width(), x + w + 24), min(win.height() - 60, y + h + 16 - 60)),
                        popups=[pop], allow_elided=("QTreeWidget",)))
            got["ok"] = True
        except H.ShotFailed as exc:
            got["error"] = exc
        pop.close()
    QTimer.singleShot(400, grab)
    tp = ed._tree_pane
    tp._on_show_context_menu(tree.visualItemRect(item).center())
    if "error" in got:
        raise got["error"]


def shape_dialogs():
    win, ed, root, report = _editor("edited")
    from bidsmgr.gui.rename_entity_dialog import RenameEntityDialog
    d = _show(RenameEntityDialog(root, ed, entity="task", value="motorimagery"), (980, 720))
    d._new.setText("imagery")
    d.plan_now()
    H.pump(settle=60)
    H.wait(0.8)
    H.pump(settle=40)
    H.take(Shot("l11-rename", "Rename an entity: the task motorimagery renamed to imagery, with every file "
                "that moves and every reference that follows.", d, allow_elided=("QTreeWidget", "MovePreviewTree")))
    _close(d)
    from bidsmgr.gui.edit_entities_dialog import EditEntitiesDialog
    d = _show(EditEntitiesDialog(root, [], ed, session_mode=True), (980, 760))
    d._mode.setCurrentIndex(d._mode.findText("Remove the session"))
    H.pump(settle=20)
    d.plan_now()
    H.pump(settle=60)
    H.wait(0.8)
    H.pump(settle=40)
    H.take(Shot("l11-sessions", "Sessions, set to remove the session: every file of ses-01 moves up to the "
                "subject's folder and loses ses-01 from its name.", d,
                allow_elided=("QTreeWidget", "MovePreviewTree")))
    _close(d)
    from bidsmgr.gui.delete_dialog import DeleteDialog
    d = _show(DeleteDialog(root, [Path(root) / f"{SUB}/beh"], ed), (980, 720))
    H.pump(settle=40)
    H.take(Shot("l11-delete", "Delete from the dataset: the eye-tracking folder, with the scans rows that go "
                "with it.", d, allow_elided=("QTreeWidget", "MovePreviewTree")))
    _close(d)
    from bidsmgr.gui.linkage_dialog import LinkageDialog
    d = _show(LinkageDialog(root, Path(root) / f"{SUB}/fmap/sub-001_ses-01_acq-fm2_magnitude1.json", ed),
              (1100, 720))
    H.pump(settle=40)
    H.take(Shot("l11-references", "References between files: the fieldmap and the run its IntendedFor "
                "names.", d, allow_elided=("QTreeWidget",)))
    _close(d)
    from bidsmgr.gui.coherence_dialog import CoherenceDialog
    d = _show(CoherenceDialog(root, ed), (980, 720))
    H.pump(lambda: not d.checking(), timeout=120, settle=40)
    H.wait(0.4)
    H.pump(settle=30)
    H.take(Shot("l11-coherence", "Check coherence on the edited sample: the events file written by hand in chapter 9 has no row in the scans table.", d,
                allow_elided=("QTreeWidget",)))
    _close(d)


def editing_typed():
    """A task description typed in, before Save (a fresh window)."""
    import states
    win, ed, root, report = _editor("fixed")
    _expand(ed, 3)
    _select(ed, root, f"{SUB}/func/sub-001_ses-01_task-rest_bold.json")
    _splitter_sizes(ed, [300, 840, 440])
    form = ed._sidecar_form
    form.focus_field("TaskDescription")
    H.pump(settle=20)
    for row in form._rows:
        rk = row.key() if callable(row.key) else row.key
        if rk == "TaskDescription":
            w = row.editor() if callable(row.editor) else row.editor
            w.setText(states.TASK["TaskDescription"])
            row._on_schema_committed()
            H.pump(settle=30)
            break
    H.take(Shot("l10-edit", "The task description typed into the BOLD run's sidecar: the toolbar says there "
                "is an unsaved change until Save.", win, crop_to=ed._center_frame))


GROUPS = {
    "l10-edit": editing_typed,
    "editor-map": editor_map,
    "l09-validating": validating,
    "l09-fixups": fixups,
    "l10-editing": editing,
    "l11-tools-menu": tools_menu,
    "l11-tree-menu": tree_menu,
    "l11-shape": shape_dialogs,
}


# ------------------------------------------------------------- chapter 14
def sharing():
    win, ed, root, report = _editor("edited")
    from bidsmgr.gui.dashboard_dialog import DashboardDialog
    d = _show(DashboardDialog(root, report=report, parent=ed), (1100, 860))
    H.take(Shot("l14-dashboard", "The Dashboard of the edited sample: what it holds by datatype and suffix, its "
                "subject, where the findings are, and whether it is ready to share.", d))
    _close(d)
    _expand(ed, 1)
    _select(ed, root, "participants.tsv", wait=1.0)
    H.pump(lambda: getattr(ed._tsv_viewer, "_loader", None) is None, timeout=20, settle=30)
    tv = ed._tsv_viewer
    table = tv._table
    m = tv._model
    cols = [str(m.headerData(c, __import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.Orientation.Horizontal))
            for c in range(m.columnCount())]
    if "given_name" in cols:
        table.selectColumn(cols.index("given_name"))
        H.pump(settle=20)
    _splitter_sizes(ed, [300, 900, 380])
    H.take(Shot("l14-participants", "participants.tsv with the given_name column selected: given_name, "
                "family_name and patient_id came from the DICOM header and identify the participant.",
                win, crop_to=ed._center_frame, allow_elided=("QTableView",)))
    _select(ed, root, "README", wait=0.8)
    H.take(Shot("l14-readme", "The README in the Editor's document viewer, rendered.", win, crop_to=ed._center_frame))
    from bidsmgr.gui.deface_dialog import DefaceDialog
    d = _show(DefaceDialog(root, None, ed), (980, 760))
    H.pump(settle=60)
    H.wait(1.0)
    H.pump(settle=30)
    H.take(Shot("l14-deface", "Remove faces: the dataset's anatomical images, the engine, and what would "
                "happen to each.", d, allow_elided=("QTreeWidget",)))
    _close(d)


def deface_compare():
    """Deface the T1w with the command line, then compare before and after."""
    import subprocess
    import sys as _sys
    root = H.restore("edited")
    t1 = "sub-001/ses-01/anat/sub-001_ses-01_acq-tfl3p2_T1w.nii.gz"
    subprocess.run([_sys.executable, "-m", "bidsmgr.cli.deface", str(H.STUDIES_REAL / "multimodal_study"),
                    "--target", str(H.STUDIES_REAL / "multimodal_study" / t1), "-q"], check=True)
    win = H.main_window("welcome", SIZE)
    H.open_project(win, root, "editor")
    ed = win.editor
    from bidsmgr.gui.deface_compare import DefaceCompareDialog
    d = _show(DefaceCompareDialog(root, t1, ed), (1300, 800))
    H.wait(3.0)
    H.pump(settle=60)
    H.take(Shot("l14-deface-compare", "Before and after: the T1w as converted on the left and defaced on the "
                "right, in one viewer.", d, anatomy_ok=True, sample="multimodal v2 (OL_3844, consented)"))
    _close(d)


GROUPS.update({"l14-sharing": sharing, "l14-deface-compare": deface_compare})

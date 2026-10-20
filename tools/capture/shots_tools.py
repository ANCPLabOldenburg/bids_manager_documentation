"""The task guides for the Editor's tools: anonymising, the ignore list, the
history, keeping a dataset consistent; and the scan's leave-out setting.

Every figure is the real dialog on a copy of a prepared state: the course's
edited multimodal sample (one subject, one session) or the converted MRI
guide sample (two subjects, the first in two sessions), which is what a
scope or a pattern across subjects needs.
"""

from __future__ import annotations

import json
from pathlib import Path

import harness as H
import shots_editor as SE
from harness import Shot

SUB = "sub-001/ses-01"
MRI = "mri_study"


def _wait_dialog(d, busy, timeout: float = 60.0) -> None:
    """Until the dialog's thread has answered, then the paint settles."""
    H.pump(lambda: not busy(), timeout=timeout, settle=40)
    H.wait(0.4)
    H.pump(settle=30)


def _context_menu(ed, paths, shot_fn, *, submenu: str | None = None) -> None:
    """Right-click the first of ``paths`` in the BIDS tree with all of them
    selected; ``shot_fn(win, menu, sub)`` takes the picture while the menu
    is open (and the submenu called ``submenu``, opened beside it)."""
    from PyQt6.QtCore import QItemSelectionModel, QPoint, QTimer
    from PyQt6.QtWidgets import QApplication, QTreeWidget

    tp = ed._tree_pane
    tree = tp.findChild(QTreeWidget)
    items = []
    for p in paths:
        ed.select_file_in_tree(Path(p))
        H.pump(settle=10)
        items.append(tree.currentItem())
    tree.clearSelection()
    for it in items:
        tree.selectionModel().select(tree.indexFromItem(it), QItemSelectionModel.SelectionFlag.Select)
    tree.setCurrentItem(items[0], 0, QItemSelectionModel.SelectionFlag.NoUpdate)
    tree.scrollToItem(items[0], QTreeWidget.ScrollHint.PositionAtCenter)
    H.pump(settle=30)
    got = {}

    def grab():
        pop = QApplication.activePopupWidget()
        if pop is None:
            QTimer.singleShot(100, grab)
            return
        H.pump(settle=20)
        sub = None
        try:
            if submenu is not None:
                action = next((a for a in pop.actions() if a.menu() is not None
                               and a.text().replace("&", "") == submenu), None)
                if action is None:
                    raise H.ShotFailed(f"no submenu {submenu!r} in the tree's menu")
                pop.setActiveAction(action)
                sub = action.menu()
                r = pop.actionGeometry(action)
                sub.popup(pop.mapToGlobal(QPoint(r.right() - 4, r.top() - 6)))
                H.pump(settle=40)
            shot_fn(ed.window(), pop, sub)
            got["ok"] = True
        except H.ShotFailed as exc:
            got["error"] = exc
        if sub is not None:
            sub.close()
        pop.close()

    QTimer.singleShot(400, grab)
    tp._on_show_context_menu(tree.visualItemRect(items[0]).center())
    if "error" in got:
        raise got["error"]
    if "ok" not in got:
        raise H.ShotFailed("the tree's menu never opened")


def _menu_crop(win, menus, *, top: int = 60, pad: int = 20):
    """A crop from the window's left edge to just past the open menus."""
    right = bottom = 0
    for m in menus:
        if m is None:
            continue
        x, y, w, h = H._global_rect_in(m, win)
        right = max(right, x + w)
        bottom = max(bottom, y + h)
    return (0, top, min(win.width(), right + pad), min(win.height() - top, bottom + pad - top))


# ------------------------------------------------------------- anonymising
def anonymise():
    win, ed, root, report = SE._editor("edited")
    from bidsmgr.gui.anonymise_dialog import AnonymiseDialog
    d = SE._show(AnonymiseDialog(root, ed), (1320, 900))
    _wait_dialog(d, d.busy)
    H.take(Shot("g-anon-dialog", "Anonymise metadata on the course's sample: Recommended, the whole dataset, and "
                "every change by kind before anything is written.", d,
                allow_elided=("QTreeWidget", "ChangeList", "QListView")))
    d._view.buttons["review"].click()
    H.pump(settle=40)
    H.take(Shot("g-anon-review", "To read by hand: free text that may name someone, such as a protocol or study "
                "description, listed once per value with the files it is in. Nothing here is changed.", d,
                allow_elided=("QTreeWidget", "ChangeList", "QListView")))
    d._view.buttons["file"].click()
    H.pump(settle=40)
    H.take(Shot("g-anon-file", "By file: every file the run would rewrite, and what changes in it. A file can be "
                "left out of the run.", d, allow_elided=("QTreeWidget", "ChangeList", "QListView")))
    d._view.buttons["kind"].click()
    d._preset.buttons["strict"].click()
    H.wait(0.6)
    _wait_dialog(d, d.busy)
    H.take(Shot("g-anon-strict", "Strict: times of day set to midnight, the site's name removed too, and ages "
                "in five-year bins.", d, allow_elided=("QTreeWidget", "ChangeList", "QListView")))
    SE._close(d)
    # The tree's right-click on the subject: Identifiable data.
    def take_menu(w, menu, sub):
        H.take(Shot("g-anon-menu", "The BIDS tree's right-click on a subject: under Identifiable data, "
                    "Anonymise metadata..., for this subject only.", w, crop=_menu_crop(w, [menu]),
                    popups=[menu], allow_elided=("QTreeWidget",)))
    SE._expand(ed, 1)
    _context_menu(ed, [Path(root) / "sub-001"], take_menu)


def anonymise_scope():
    """The MRI guide's sample: two subjects, the first in two sessions."""
    root = H.restore("guide-mri", MRI)
    win = H.main_window("welcome", SE.SIZE)
    H.open_project(win, root, "editor")
    ed = win.editor
    H.pump(settle=40)
    from bidsmgr.anonymise import Scope
    from bidsmgr.gui.anonymise_dialog import AnonymiseDialog
    scope = Scope(top=True, subjects=frozenset({"sub-001"}), sessions=frozenset({"sub-001/ses-post"}))
    d = SE._show(AnonymiseDialog(root, ed, scope=scope), (1320, 900))
    _wait_dialog(d, d.busy)
    H.take(Shot("g-anon-scope", "Where, on a dataset of two subjects: only the second session of sub-001, and "
                "its row of the dataset's files. The first session can be anonymised later with the same "
                "shift of dates.", d, allow_elided=("QTreeWidget", "ChangeList", "QListView"),
                sample="MRI sample 1"))
    SE._close(d)


def _scroll_to(dlg, text: str) -> bool:
    """Scroll the settings page so the first widget whose text starts with
    ``text`` sits near the top."""
    from PyQt6.QtWidgets import QAbstractButton, QGroupBox, QLabel, QScrollArea
    for sa in dlg.findChildren(QScrollArea):
        if not sa.isVisible():
            continue
        for w in sa.widget().findChildren((QAbstractButton, QLabel, QGroupBox)):
            t = w.title() if isinstance(w, QGroupBox) else w.text()
            if t and t.replace("&", "").startswith(text) and w.isVisible():
                y = w.mapTo(sa.widget(), w.rect().topLeft()).y()
                sa.verticalScrollBar().setValue(max(0, y - 160))
                H.pump(settle=30)
                return True
    return False


# ----------------------------------------------------------------- history
def history():
    """Four steps on the edited sample, then the Undo button's list."""
    win, ed, root, report = SE._editor("edited", validate=False)
    real = H.STUDIES_REAL / "multimodal_study"
    from bidsmgr.editor import bidsignore as bi
    from bidsmgr.editor.rename import apply_rename, plan_rename
    plan = plan_rename(real, "task", "motorimagery", "imagery")
    _n, errors = apply_rename(real, plan)
    if errors:
        raise H.ShotFailed(f"rename failed: {errors}")
    (real / "notes").mkdir(exist_ok=True)
    (real / "notes" / "session_log.txt").write_text("Session notes.\n")
    listing = bi.list_dataset(real)
    choice = next(c for c in bi.choices_for(["notes/"], listing.paths) if c.key == "exact")
    bi.apply_choice(real, choice)
    from bidsmgr.anonymise import PRESETS, plan_anonymise
    from bidsmgr.gui.anonymise_dialog import _apply_job
    aplan = plan_anonymise(real, PRESETS["recommended"])
    _apply_job(real, aplan, "Anonymise metadata (Recommended)", False)
    ed._tree_pane.set_root(root)
    ed._sync_undo_redo()
    H.pump(settle=40)
    from PyQt6.QtCore import QPoint
    btn = ed._undo_btn
    ed._show_history_menu("undo", btn.mapToGlobal(QPoint(0, btn.height() + 2)))
    H.pump(settle=40)
    menu = ed._history_menu
    x, y, w, h = H._global_rect_in(menu, win)
    bx, by, bw, bh = H._rect_in(btn.parentWidget(), win)
    H.take(Shot("g-history-menu", "Right-click on Undo: the dataset's history, newest first, each step with "
                "when it was made: the two sidecars edited in chapters 9 and 10, then a task renamed, a folder "
                "of notes ignored and the anonymisation.", win,
                crop=(0, by - 8, min(win.width(), x + w + 40), y + h + 20 - (by - 8)),
                popups=[menu], allow_elided=("QTreeWidget",)))
    menu.close()


# ------------------------------------------------------- ignoring files
def _mri_with_extras():
    """The MRI guide's dataset with what labs keep beside the data: notes
    per session, the scanner's physiological logs, a folder of notes."""
    root = H.restore("guide-mri", MRI)
    real = H.STUDIES_REAL / MRI
    for folder in ("sub-001/ses-pre", "sub-001/ses-post", "sub-002"):
        name = folder.replace("/", "_")
        (real / folder / f"{name}_notes.txt").write_text("Participant arrived on time; no remarks.\n")
    for folder, stem in (("sub-001/ses-pre/func", "sub-001_ses-pre_task-rest"),
                         ("sub-002/func", "sub-002_task-rest")):
        if (real / folder).is_dir():
            (real / folder / f"{stem}_physio.log").write_text("PMU log\n")
    (real / "notes").mkdir(exist_ok=True)
    (real / "notes" / "scanning_protocol.txt").write_text("Protocol.\n")
    (real / "notes" / "booking.txt").write_text("Bookings.\n")
    return root, real


def ignoring():
    root, real = _mri_with_extras()
    win = H.main_window("welcome", (1600, 1300))
    H.open_project(win, root, "editor")
    ed = win.editor
    H.pump(settle=40)
    from bidsmgr.editor import validate as run_validate
    schema, max_rows, todos = ed._validation_engine_opts()
    rep = run_validate(root, strict=ed._strict_btn.isChecked(), schema=schema, max_rows=max_rows,
                       flag_todos=todos)
    ed._on_report_ready(rep, root)
    H.pump(settle=40)
    SE._expand(ed, 4)
    SE._splitter_sizes(ed, [430, 700, 450])
    notes = Path(root) / "sub-001/ses-pre/sub-001_ses-pre_notes.txt"

    def take_menu(w, menu, sub):
        H.take(Shot("g-ignore-menu", "Right-click on one session's notes: Ignore in validation offers this "
                    "file, its folder, or the same name in every subject and session, each with how many "
                    "files it covers.", w, crop=_menu_crop(w, [menu, sub]), popups=[menu, sub],
                    allow_elided=("QTreeWidget",), sample="MRI sample 1"))
    _context_menu(ed, [notes], take_menu, submenu="Ignore in validation")
    from bidsmgr.editor import bidsignore as bi
    listing = bi.list_dataset(real)
    rel = "sub-001/ses-pre/sub-001_ses-pre_notes.txt"
    every = next(c for c in bi.choices_for([rel], listing.paths) if c.key == "everywhere")
    log = "sub-001/ses-pre/func/sub-001_ses-pre_task-rest_physio.log"

    def idle():
        w = ed._report_worker
        return w is None or not w.isRunning()
    ed._apply_ignore_choice(every)
    H.pump(idle, timeout=90, settle=40)
    ext = next(c for c in bi.choices_for([log], bi.list_dataset(real).paths) if c.key == "extension")
    ed._apply_ignore_choice(ext)
    H.pump(idle, timeout=90, settle=40)
    folder = next(c for c in bi.choices_for(["notes/"], bi.list_dataset(real).paths) if c.key == "exact")
    ed._apply_ignore_choice(folder)
    H.pump(idle, timeout=90, settle=40)
    H.wait(1.0)
    H.pump(settle=40)
    SE._expand(ed, 4)
    H.take(Shot("g-ignore-tree", "The tree after three lines in .bidsignore: the notes, the physiological logs "
                "and the notes folder are drawn dimmed and in italics, and validation no longer reports them.",
                win, crop_to=ed._tree_frame, allow_elided=("QTreeWidget",), sample="MRI sample 1"))
    ed._on_ignore_list()
    H.pump(settle=60)
    H.wait(0.6)
    H.pump(settle=30)
    SE._splitter_sizes(ed, [300, 900, 380])
    H.take(Shot("g-ignore-list", "The ignore list: each line of .bidsignore with how many files it hides, and "
                "every file of the dataset, ignored or validated.", win, crop_to=ed._center_frame,
                allow_elided=("QTreeWidget", "QTableView"), sample="MRI sample 1"))
    # Two ignored files at once: Stop ignoring. Only the two logs' folders
    # open, so both are on screen beside the menu.
    picks = [Path(root) / "sub-001/ses-pre/func/sub-001_ses-pre_task-rest_physio.log",
             Path(root) / "sub-002/func/sub-002_task-rest_physio.log"]
    from PyQt6.QtWidgets import QTreeWidget
    tree = ed._tree_pane.findChild(QTreeWidget)
    tree.collapseAll()
    SE._splitter_sizes(ed, [520, 700, 360])
    H.pump(settle=30)

    def take_stop(w, menu, sub):
        action = next(a for a in menu.actions() if a.text().startswith("Stop ignoring"))
        r = menu.actionGeometry(action)
        bottom = menu.mapTo(menu, r.bottomLeft()).y()
        mx, my, mw, mh = H._global_rect_in(menu, w)
        ty = H._rect_in(tree, w)[1]
        crop = (0, ty - 40, mx + mw + 20, (my + bottom + 24) - (ty - 40))
        last = max(H._rect_in(tree, w)[1] + tree.visualItemRect(it).bottom() for it in tree.selectedItems())
        crop = (crop[0], crop[1], crop[2], max(crop[3], last + 20 - crop[1]))
        H.take(Shot("g-ignore-stop", "Right-click on the two physiological logs, both ignored by *.log: Stop "
                    "ignoring these 2 files, in one step.", w, crop=crop, popups=[menu],
                    allow_elided=("QTreeWidget",), sample="MRI sample 1"))
    _context_menu(ed, picks, take_stop)


# ------------------------------------------------ keeping it consistent
def _damage(real: Path) -> None:
    """What happens outside the app: the T1w renamed in the file manager
    (image and sidecar), the sessions table deleted, a TaskName typed by
    hand. The events file chapter 9 wrote in beh/ already has no scans row."""
    import json as _json
    anat = real / SUB / "anat"
    for ext in (".nii.gz", ".json"):
        (anat / f"sub-001_ses-01_acq-tfl3p2_T1w{ext}").rename(anat / f"sub-001_ses-01_acq-mprage_T1w{ext}")
    (real / "sub-001" / "sub-001_sessions.tsv").unlink()
    bold = real / SUB / "func" / "sub-001_ses-01_task-rest_bold.json"
    data = _json.loads(bold.read_text())
    data["TaskName"] = "resting state"
    bold.write_text(_json.dumps(data, indent=4) + "\n")


def consistency():
    root = H.restore("edited")
    real = H.STUDIES_REAL / "multimodal_study"
    _damage(real)
    win = H.main_window("welcome", SE.SIZE)
    H.open_project(win, root, "editor")
    ed = win.editor
    H.pump(settle=40)
    from bidsmgr.gui.coherence_dialog import CoherenceDialog
    d = SE._show(CoherenceDialog(root, ed), (1100, 820))
    _wait_dialog(d, d.checking)
    from PyQt6.QtWidgets import QTreeWidget
    tree = d._tree
    if tree.topLevelItemCount():
        first = tree.topLevelItem(0)
        tree.setCurrentItem(first.child(0) if first.childCount() else first)
        H.pump(settle=30)
    H.take(Shot("g-coherence", "Check coherence after the T1w was renamed in the file manager, the sessions "
                "table deleted and a TaskName typed by hand: four problems, what would repair each, and the "
                "three safe repairs ticked.", d,
                allow_elided=("QTreeWidget",)))
    SE._close(d)
    from bidsmgr.gui.tables_dialog import TablesDialog
    d = SE._show(TablesDialog(root, ed), (1100, 640))
    _wait_dialog(d, d.planning)
    H.take(Shot("g-tables", "Scans and sessions tables: every table the dataset should have, with the rows it "
                "would add, keep or remove, before anything is written.", d, allow_elided=("QTreeWidget",)))
    SE._close(d)


# --------------------------------------------------- chapter 3: leave out
def leave_out():
    win = H.main_window("welcome")
    from bidsmgr.gui.app_settings import AppSettings
    from bidsmgr.gui.settings_dialog import SettingsDialog
    d = SettingsDialog(AppSettings.load(), win)
    d.resize(1040, 780)
    d.show_page("Scan")
    d.show()
    H.pump(settle=40)
    box = d._drop_entities.get("acq")
    if box is None:
        raise H.ShotFailed("no acq- in Leave out of proposed names")
    box.setChecked(True)
    if not _scroll_to(d, "Leave out of proposed names"):
        raise H.ShotFailed("no Leave out of proposed names box")
    H.take(Shot("l03-leave-out", "Settings, Scan page: Leave out of proposed names, with Acquisition (acq-) "
                "ticked: the next scan proposes names without it wherever the standard allows.", d))
    d.close()


# --------------------------------------------------- names and structure
def names():
    """MRI sample 1: the follow-up of sub-001 was registered under a new ID
    and converted as sub-002. Make it a session, then merge the subjects."""
    root = H.restore("guide-mri", MRI)
    real = H.STUDIES_REAL / MRI
    win = H.main_window("welcome", SE.SIZE)
    H.open_project(win, root, "editor")
    ed = win.editor
    H.pump(settle=40)
    from bidsmgr.gui.edit_entities_dialog import EditEntitiesDialog
    d = SE._show(EditEntitiesDialog(root, [Path(root) / "sub-002"], ed, session_mode=True), (1000, 780))
    d._mode.setCurrentIndex(d._mode.findText("Create a session"))
    H.pump(settle=20)
    d._value.setCurrentText("followup")
    d.plan_now()
    H.pump(settle=60)
    H.wait(0.8)
    H.pump(settle=40)
    H.take(Shot("g-names-session", "Sessions, Create a session, for sub-002: every file moves into ses-followup "
                "and takes the label in its name; the scans table follows.", d,
                allow_elided=("QTreeWidget", "MovePreviewTree"), sample="MRI sample 1"))
    SE._close(d)
    from bidsmgr.editor.rename import apply_rename
    from bidsmgr.editor.restructure import plan_add_session
    plan = plan_add_session(real, "followup", [real / "sub-002"])
    _n, errors = apply_rename(real, plan)
    if errors:
        raise H.ShotFailed(f"session: {errors}")
    ed._tree_pane.set_root(root)
    H.pump(settle=30)
    from bidsmgr.gui.rename_entity_dialog import RenameEntityDialog
    d = SE._show(RenameEntityDialog(root, ed, entity="sub", value="002"), (1000, 800))
    d._new.setText("001")
    d.plan_now()
    H.pump(settle=60)
    H.wait(0.6)
    if not d._fuse.isVisible():
        raise H.ShotFailed("no merge offered for sub-002 -> sub-001")
    d._fuse.setChecked(True)
    H.pump(settle=60)
    H.wait(0.8)
    H.pump(settle=40)
    H.take(Shot("g-names-merge", "Rename subject sub-002 to sub-001, which exists: Merge them into one subject "
                "moves the follow-up session under sub-001 and folds the two participants rows into one.", d,
                allow_elided=("QTreeWidget", "MovePreviewTree"), sample="MRI sample 1"))
    SE._close(d)
    from bidsmgr.editor.rename import plan_rename
    plan = plan_rename(real, "sub", "002", "001", fuse=True)
    _n, errors = apply_rename(real, plan)
    if errors:
        raise H.ShotFailed(f"merge: {errors}")
    ed._tree_pane.set_root(root)
    H.pump(settle=40)
    SE._expand(ed, 1)
    x, y, w, _h = H._rect_in(ed._tree_frame, win)
    H.take(Shot("g-names-merged", "After the merge: one subject with three sessions, pre, post and followup.",
                win, crop=(x, y, w, 330), allow_elided=("QTreeWidget",), sample="MRI sample 1"))


GROUPS = {
    "g-anonymise": anonymise,
    "g-anonymise-scope": anonymise_scope,
    "g-history": history,
    "g-ignoring": ignoring,
    "g-consistency": consistency,
    "l03-leave-out": leave_out,
    "g-names": names,
}

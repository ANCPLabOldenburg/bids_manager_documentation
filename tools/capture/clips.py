"""The clips: short scripted timelines on the real window."""

from __future__ import annotations

import harness as H
import shots_converter as SC
from clip import Clip


def scan_clip():
    """Chapter 3: choose nothing new (the raw folder is set), press Scan, watch the rows arrive."""
    import states
    win, conv = SC._converter("project")
    SC._set_raw(conv)
    SC._expand_raw(conv, 1)
    c = Clip("l03-scan", win, alt="Pressing Scan in the Converter: the spinner turns while the headers are "
             "read, then the table fills with 19 rows and the counts appear in the toolbar.",
             start=(760, 520))
    c.hold(0.6)
    c.click(conv._scan_btn, conv._on_scan_clicked, move=0.9)
    c.wait_until(lambda: conv._scan_worker is None or not conv._scan_worker.isRunning(), timeout=300,
                 every=0.2, speed=2.0)
    c.wait_until(lambda: conv.model() is not None and conv.model().rowCount() > 0, timeout=30, every=0.1)
    c.do(lambda: None, settle=0.6)
    c.move_to(conv._chip_warn, 0.8)
    c.hold(2.5)
    c.finish()


def bulk_clip():
    """Chapter 4: select the rows to convert, Bulk edit, subject 001, Apply."""
    win, conv = SC._converter("scanned")
    SC.layout(conv)
    m = conv.model()
    df = m.dataframe()
    rows = [r for r in range(len(df)) if str(df.iloc[r]["include"]) in ("1", "True", "true")]
    c = Clip("l04-bulk-subject", win, alt="Selecting the 15 rows to convert, opening Bulk edit, choosing the "
             "subject column and typing 001: the four rows that said 002, 003 and 004 now say 001.",
             start=(900, 700))
    c.hold(0.5)
    first = SC._header_rects(conv, ["id"])["id"]
    table = conv._table
    rh = table.verticalHeader().defaultSectionSize()
    from PyQt6.QtCore import QPoint
    vp = table.viewport()
    def row_point(r):
        y = table.rowViewportPosition(r) + rh // 2
        p = vp.mapTo(win, QPoint(first[0] - vp.mapTo(win, QPoint(0, 0)).x() + 30, y))
        return (p.x(), p.y())
    c.move_to(row_point(rows[0]), 0.7)
    c.click(row_point(rows[0]), lambda: conv.select_rows([rows[0]]), move=0)
    c.move_to(row_point(rows[-1]), 0.8)
    c.click(row_point(rows[-1]), lambda: conv.select_rows(rows), move=0)
    c.hold(0.6)
    from bidsmgr.gui.bulk_edit_dialog import BulkEditDialog
    holder = {}

    def open_dialog():
        d = BulkEditDialog(m, rows, parent=conv)
        d.resize(620, 600)
        d.show()
        H.pump(settle=20)
        geo = win.geometry()
        d.move(geo.x() + (geo.width() - d.width()) // 2, geo.y() + (geo.height() - d.height()) // 2)
        holder["d"] = d
    c.click(conv._bulk_btn, open_dialog)
    d = holder["d"]
    c.hold(0.8)
    c.click(d._col_combo, lambda: (d._col_combo.setCurrentIndex(d._col_combo.findData("id")), H.pump(settle=10)))
    c.hold(0.6)
    field = d._value_edit if d._value_edit.isVisible() else d._value_combo.lineEdit()
    c.click(field, lambda: field.setFocus())
    c.type(field, "001")
    c.do(lambda: d._replan(), settle=0.4)
    c.hold(1.6)
    apply_btn = d._apply_btn if hasattr(d, "_apply_btn") else H.button(d, "Apply")

    def apply():
        with m.edit_group():
            d._on_apply()
        H.pump(settle=20)
    c.click(apply_btn, apply)
    c.hold(2.2)
    c.finish()


GROUPS = {"clip-l03-scan": scan_clip, "clip-l04-bulk": bulk_clip}


def convert_clip():
    """Chapter 8: Run conversion from the described state; the Log fills; the output tree grows."""
    from PyQt6.QtWidgets import QMessageBox
    win, conv = SC._converter("described")
    SC.layout(conv, log=260)
    shown = {}
    orig_exec = QMessageBox.exec

    def show_instead(box):
        box.show()
        H.pump(settle=10)
        geo = win.geometry()
        box.move(geo.x() + (geo.width() - box.width()) // 2, geo.y() + (geo.height() - box.height()) // 3)
        shown["box"] = box
        return 0
    QMessageBox.exec = show_instead
    conv.confirm_sourcedata = lambda _t: True
    try:
        c = Clip("l08-convert", win, alt="Pressing Run conversion: the Log reports each step, the output tree "
                 "fills with the dataset, metadata and validation run after it, and a message says where the "
                 "output was written.", start=(1200, 640))
        c.hold(0.5)
        # The Log is folded while it runs: its first line names the folder the
        # package runs from, which is a home directory on any real install.
        conv._log_frame.set_collapsed(True)
        H.pump(settle=20)
        c.refresh()
        c.chapter("Run conversion")
        c.click(conv._run_btn, conv._on_run_clicked, move=0.9)
        c.chapter("The conversion")
        c.wait_until(lambda: "box" in shown, timeout=900, every=0.25, speed=3.0)
        c.chapter("Done")
        conv._log_frame.set_collapsed(False)
        H.pump(settle=20)
        conv._log_view.verticalScrollBar().setValue(conv._log_view.verticalScrollBar().maximum())
        c.hold(2.5)
        box = shown["box"]
        ok = box.buttons()[0] if box.buttons() else None
        if ok is not None:
            c.click(ok, box.accept)
        c.hold(1.5)
        c.finish()
    finally:
        QMessageBox.exec = orig_exec


def convert_log():
    """The Log after the conversion and its chain (a still)."""
    from PyQt6.QtWidgets import QMessageBox
    win, conv = SC._converter("described")
    SC.layout(conv, log=190)
    done = {}
    conv.confirm_sourcedata = lambda _t: True
    conv._show_convert_dialog = lambda rc, p: done.setdefault("rc", rc)
    conv._on_run_clicked()
    H.pump(lambda: "rc" in done, timeout=900, settle=60)
    bar = conv._log_view.verticalScrollBar()
    bar.setValue(bar.maximum())
    H.pump(settle=20)
    H.take(H.Shot("l08-log", "The end of the Log after the conversion: the conversion's summary, then the "
                  "Metadata and Validation runs, each under its own heading.", win, crop_to=conv._log_frame,
                  allow_elided=("RunLog",)))


GROUPS.update({"clip-l08-convert": convert_clip, "l08-log": convert_log})


def validate_clip():
    """Chapter 9: Validate dataset in the Editor; the marks and counts arrive."""
    import shots_editor as SE
    win, ed, root, _rep = SE._editor(validate=False)
    SE._expand(ed, 3)
    SE._splitter_sizes(ed, [300, 760, 520])
    btn = H.button(ed, "Validate dataset")
    c = Clip("l09-validate", win, alt="Pressing Validate dataset in the Editor: each file in the tree gets its "
             "mark, each folder its counts, and the toolbar the totals.", start=(900, 560))
    c.hold(0.6)
    c.click(btn, btn.click, move=0.9)
    c.wait_until(lambda: ed.current_report() is not None and not ed._spinner.is_busy()
                 if hasattr(ed._spinner, "is_busy") else ed.current_report() is not None,
                 timeout=300, every=0.2, speed=1.5)
    c.do(lambda: None, settle=0.5)
    c.move_to(ed._chip_err if hasattr(ed, "_chip_err") else btn, 0.8)
    c.hold(2.5)
    c.finish()


GROUPS.update({"clip-l09-validate": validate_clip})


def fix_clip():
    """Chapter 9: the PET error from its finding: Fix, the entries, Save, validate again."""
    import shots_editor as SE
    from pathlib import Path
    from PyQt6.QtCore import QPoint
    from PyQt6.QtWidgets import QLineEdit, QPushButton, QTreeWidget

    from bidsmgr.gui.widgets.val_message import ValMessage

    win, ed, root, _rep = SE._editor("converted")
    SE._expand(ed, 3)
    SE._splitter_sizes(ed, [280, 800, 520])
    pet = Path(root) / "sub-001/ses-01/pet/sub-001_ses-01_pet.json"
    tree = ed._tree_pane.findChild(QTreeWidget)
    ed.select_file_in_tree(pet)
    H.pump(settle=10)
    rect = tree.visualItemRect(tree.currentItem())
    pt = tree.viewport().mapTo(win, rect.center())
    ed.select_file_in_tree(Path(root) / "README")
    H.pump(settle=20)
    c = Clip("l09-fix", win, alt="Selecting the PET sidecar, clicking Fix on its error, adding none as the "
             "reconstruction parameters' unit and label, saving, and validating again: one error less, "
             "the two left are the eye tracker's.", start=(700, 700))
    c.hold(0.5)
    c.click((pt.x(), pt.y()), lambda: ed.select_file_in_tree(pet))
    H.wait(0.6)
    c.hold(0.6)
    vp = ed._validation_pane
    card = next(m for m in vp.findChildren(ValMessage)
                if m.isVisible() and m._field_name == "ReconMethodParameterUnits")
    fix = next(b for b in card.findChildren(QPushButton) if b.objectName() == "val-fix")
    c.click(fix, fix.click, move=0.9)
    H.wait(0.4)
    c.hold(0.6)
    form = ed._sidecar_form

    def row_for(key):
        return next(r for r in form._rows if (r.key() if callable(r.key) else r.key) == key)

    def list_entry(key, add: bool):
        row = row_for(key)
        w = row.editor() if callable(row.editor) else row.editor
        edits = [e for e in w.findChildren(QLineEdit) if e.isVisible()]
        empty = [e for e in edits if not e.text().strip()]
        if add and not empty:
            btn = next(b for b in w.findChildren(QPushButton) if b.text().strip() == "Add entry")
            c.click(btn, btn.click, move=0.6)
            edits = [e for e in w.findChildren(QLineEdit) if e.isVisible()]
            empty = [e for e in edits if not e.text().strip()]
        edit = empty[0] if empty else edits[-1]
        c.click(edit, lambda: (edit.setFocus(), edit.selectAll()), move=0.5)
        c.type(edit, "none", cps=10, clear=True)
        c.do(row._on_schema_committed, settle=0.2)

    list_entry("ReconMethodParameterUnits", add=True)
    c.hold(0.4)
    form.focus_field("ReconMethodParameterLabels")
    H.pump(settle=20)
    c.hold(0.4)
    list_entry("ReconMethodParameterLabels", add=False)
    c.hold(0.5)
    save = H.button(form, "Save")
    c.click(save, form.save)
    c.hold(0.6)
    btn = H.button(ed, "Validate dataset")
    c.click(btn, btn.click)
    c.wait_until(lambda: not ed._spinner.is_busy(), timeout=120, every=0.2, speed=1.5)
    c.do(lambda: None, settle=0.4)
    c.move_to(ed._chip_err, 0.7)
    c.hold(2.4)
    c.finish()


def edit_save_clip():
    """Chapter 10: find TaskDescription, type it, Save."""
    import shots_editor as SE
    import states
    win, ed, root, _rep = SE._editor("fixed")
    SE._expand(ed, 3)
    SE._splitter_sizes(ed, [300, 840, 440])
    from pathlib import Path
    SE._select(ed, root, "sub-001/ses-01/func/sub-001_ses-01_task-rest_bold.json")
    SE._splitter_sizes(ed, [260, 760, 560])
    form = ed._sidecar_form
    c = Clip("l10-edit-save", win, alt="Searching the BOLD run's sidecar for TaskDescription, typing a "
             "description, and saving.", start=(800, 600))
    c.hold(0.5)
    search = form.search.findChild(type(form.search)) if False else None
    from PyQt6.QtWidgets import QLineEdit
    field = form.search if isinstance(form.search, QLineEdit) else form.search.findChild(QLineEdit)
    c.click(field, field.setFocus)
    c.type(field, "TaskDesc", cps=12)
    c.hold(0.6)
    row = next(r for r in form._rows if (r.key() if callable(r.key) else r.key) == "TaskDescription")
    w = row.editor() if callable(row.editor) else row.editor
    c.click(w, lambda: (w.setFocus(), w.selectAll()))
    c.type(w, states.TASK["TaskDescription"], cps=24, clear=True)
    c.do(row._on_schema_committed, settle=0.3)
    c.hold(0.8)
    save = H.button(form, "Save")
    c.click(save, form.save)
    c.do(lambda: field.clear(), settle=0.3)
    c.hold(2.0)
    c.finish()


GROUPS.update({"clip-l09-fix": fix_clip, "clip-l10-edit-save": edit_save_clip})


def guide_clip():
    """Start > First launch: the guide switched on in the Converter, a task
    chosen, and its first three steps."""
    from PyQt6.QtCore import QPoint

    from bidsmgr.gui.guide import _ChoiceRow
    win, conv = SC._converter("scanned")
    SC.layout(conv)
    g = win.guide
    c = Clip("s-guide", win, alt="Switching the Guide on in the Converter: it asks what to do; choosing "
             "Check and edit the table rings the table; a click on a row moves the card to Properties; "
             "Next moves it to Structure.", start=(1150, 640))
    c.hold(0.6)
    sw = win._header.guide_switch

    def turn_on():
        sw.set_on(True)
        win._on_guide_toggled(True)
    c.chapter("Switch it on")
    c.click(sw, turn_on, move=0.9)
    c.wait_until(lambda: g.question.isVisible(), timeout=15, every=0.1, speed=1.0)
    c.hold(2.2)
    row = next(r for r in g.question._rows_widget.findChildren(_ChoiceRow) if r.key == "review")
    c.chapter("Choose a task")
    c.click(row, lambda: g._on_chosen("review"), move=0.9)
    c.wait_until(lambda: g.card.isVisible(), timeout=15, every=0.1, speed=1.0)
    c.hold(2.8)
    df = conv.model().dataframe()
    r = next(i for i in range(len(df)) if str(df.iloc[i]["bids_name"]).endswith("_bold"))
    table = conv._table
    rh = table.verticalHeader().defaultSectionSize()
    vp = table.viewport()
    p = vp.mapTo(win, QPoint(260, table.rowViewportPosition(r) + rh // 2))
    c.chapter("Do what it says")
    c.click((p.x(), p.y()), lambda: (conv.select_rows([r]), conv._on_guide_row_click(), g.refresh()),
            move=1.0)
    c.wait_until(lambda: g.run("converter") == ("review", 1), timeout=15, every=0.1, speed=1.0)
    c.do(g.refresh, settle=0.4)
    c.hold(3.0)
    c.chapter("Next")
    c.click(g.card._next_btn, g._on_next, move=0.9)
    c.do(g.refresh, settle=0.4)
    c.hold(3.0)
    c.finish()


def whats_new_clip():
    """Updates: the What's new window of 1.5.2, playing, then a feature picked."""
    from bidsmgr.gui import whats_new as wn

    win = H.main_window("welcome")
    d = wn.WhatsNewDialog(win)
    d.resize(1100, 660)
    d.show()
    H.pump(settle=40)
    page = d.page()
    stage = page.stage
    keys = [s.key for s in stage.scenes]
    c = Clip("u-whats-new", d, alt="The What's new window of BIDS Manager 1.5.2 playing its animations: the "
             "guide, then the physiology of a CMRR log, then Sidecars written from the recordings, picked "
             "from the list.", start=(860, 560), popups=False)
    c.show_cursor = False

    def play(key: str, seconds: float, by_user: bool) -> None:
        stage.set_scene(keys.index(key), by_user=by_user)
        for k in range(int(seconds * c.fps)):
            stage.set_time(k / c.fps)
            c.refresh()
            c.frame()

    play("guide", stage.scenes[keys.index("guide")].duration, False)
    play("physio", stage.scenes[keys.index("physio")].duration, False)
    c.show_cursor = True
    button = page.feature_buttons[keys.index("sidecars")]
    c.move_to(button, 0.9)
    c.rings.append((c.cursor, c.t))
    # The picked scene to just before it would fade, then held there: the
    # clip ends, and its poster shows, on the sidecar fully written.
    sidecars = stage.scenes[keys.index("sidecars")]
    play("sidecars", sidecars.duration - wn.FADE - 0.1, True)
    c.poster_at = c.t
    c.hold(1.8)
    c.finish()


GROUPS.update({"clip-s-guide": guide_clip, "clip-u-whats-new": whats_new_clip})

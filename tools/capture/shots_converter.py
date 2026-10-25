"""The Converter: the window map, the scan, the table, Filter, Overview, Properties."""

from __future__ import annotations

import harness as H
from harness import Region, Shot


#: The Converter at the 1.15 font scale needs about 1440 px for its panels'
#: minimum widths alone, so at 1440 nothing can be widened; its pictures are
#: taken a little larger so the Properties panel shows its fields whole.
SIZE = (1600, 1000)


def _converter(state: str = "scanned", size=SIZE):
    root = H.restore(state)
    win = H.main_window("welcome", size)
    H.open_project(win, root, "converter")
    conv = win.converter
    H.pump(lambda: conv.model() is not None and conv.model().rowCount() > 0, timeout=30, settle=40)
    return win, conv


def _splitters(conv):
    from PyQt6.QtWidgets import QSplitter
    out = {}
    for sp in conv.findChildren(QSplitter):
        names = [getattr(sp.widget(i), "_title", None) for i in range(sp.count())]
        if "Inspection" in names:
            out["columns"] = sp
        elif "Log" in names:
            out["log"] = sp
        elif "Properties" in names:
            out["props"] = sp
        elif "Raw data tree" in names:
            out["trees"] = sp
    return out


def layout(conv, *, columns=(250, 300, 1018), props=330, log=None, fold_trees=False):
    """Splitter sizes a user would drag to: Properties wide enough for its
    fields at the 1.15 font scale (at the default sizes it is not).
    ``fold_trees`` folds the raw and output trees away, as their strip does."""
    sp = _splitters(conv)
    if fold_trees:
        conv._col1_frame.set_collapsed(True)
        H.pump(settle=20)
        total = sum(sp["columns"].sizes())
        first = sp["columns"].sizes()[0]
        columns = (first, columns[1], total - first - columns[1])
    sp["columns"].setSizes(list(columns))
    H.pump(settle=10)
    total = sum(sp["props"].sizes())
    sp["props"].setSizes([total - props, props])
    if log is not None:
        t = sum(sp["log"].sizes())
        sp["log"].setSizes([t - log, log])
    H.pump(settle=30)


def _row(conv, **match) -> int:
    df = conv.model().dataframe()
    for i in range(len(df)):
        if all(str(df.iloc[i].get(k, "")) == v for k, v in match.items()):
            return i
    raise H.ShotFailed(f"no row matching {match}")


def _properties(conv, row: int) -> None:
    conv.select_rows([row])
    p = conv._properties
    p.request_row(row)
    p.flush()
    H.pump(lambda: not p._pending and p._rendered_row == row, timeout=10, settle=30)


def _wait_overview(conv) -> None:
    ov = conv._overview
    H.pump(lambda: ov.overview() is not None and not ov.is_counting() and not ov._settle.isActive()
           and ov._stack.currentIndex() == 2, timeout=60, settle=40)


def _wait_preview(conv) -> None:
    pv = conv._filter_pane.preview
    H.pump(lambda: pv.plan() is not None and not pv.is_planning(), timeout=60, settle=20)
    H.pump(lambda: not pv._jobs.running("file"), timeout=60, settle=40)


def window_map():
    """The Converter after the scan: every area of the window, numbered."""
    win, conv = _converter("scanned")
    layout(conv)
    row = _row(conv, sequence="ses-pre_task-rest_bold")
    _properties(conv, row)
    H.take(Shot(
        "converter-map", "The Converter after scanning the multimodal sample: the toolbar, the raw input "
        "and BIDS output bars, the raw and output trees, the Structure panel beside the table, the scan table in the Table view with one "
        "row selected, the Properties panel and the Log.",
        win, window=True,
        regions=[
            Region("toolbar", "The toolbar: Scan, the scan table, Undo and Redo, the counts, Run conversion",
                   conv._scan_btn.parentWidget(), anchor="l"),
            Region("paths", "Raw input and BIDS output", conv._raw_pathbar, anchor="l"),
            Region("trees", "The raw data tree and the output data tree", conv._col1_frame),
            Region("filter", "Structure: the subjects, sessions and recordings the scan found", conv._filter_frame),
            Region("inspection", "Inspection: the table of recordings, or the Overview", conv._inspection_unit),
            Region("properties", "Properties of the selected row", conv._properties_frame),
            Region("log", "The Log", conv._log_frame),
            Region("run", "Run conversion", conv._run_btn),
        ],
        allow_elided=("QTreeView", "QTreeWidget")))
    win.close()



# ---------------------------------------------------------------- helpers
def _section(widget, top, bottom, root):
    """A crop from ``top`` to ``bottom`` widgets, full width of ``widget``."""
    x, y, w, _h = H._rect_in(widget, root)
    _x2, y2, _w2, h2 = H._rect_in(bottom, root)
    _x1, y1, _w1, _h1 = H._rect_in(top, root)
    return (x, y1, w, y2 + h2 - y1)


def _header_rects(conv, keys):
    """Region rectangles of table columns (header + visible cells), in window coordinates."""
    from PyQt6.QtCore import QPoint
    table = conv._table
    hh = table.horizontalHeader()
    m = conv.model()
    out = {}
    win = conv.window()
    for key in keys:
        col = [c.key for c in m.COLUMNS].index(key)
        x = hh.sectionViewportPosition(col)
        w = hh.sectionSize(col)
        top = hh.mapTo(win, QPoint(x, 0))
        out[key] = (top.x(), top.y(), w, hh.height() + table.viewport().height())
    return out


def _set_raw(conv, raw=None):
    import states
    raw = raw or states.RAW
    conv._raw_root = raw
    conv._raw_pane.set_root(raw)
    conv._show_source_state()
    H.pump(settle=20)


def _expand_raw(conv, depth=1):
    tree = conv._raw_pane._tree
    tree.expandToDepth(depth)
    H.pump(settle=20)


def _dialog(dlg, size=None, near=None):
    if size:
        dlg.resize(*size)
    dlg.show()
    H.pump(settle=40)
    return dlg



def _scroll_to_widget(dlg, widget, pad: int = 8) -> None:
    """Scroll the settings page holding ``widget`` so it sits near the top."""
    from PyQt6.QtWidgets import QScrollArea
    area = next(a for a in dlg.findChildren(QScrollArea)
                if a.isVisible() and a.widget() is not None and a.widget().isAncestorOf(widget))
    top = widget.mapTo(area.widget(), widget.rect().topLeft()).y()
    area.verticalScrollBar().setValue(max(0, top - pad))
    H.pump(settle=20)

# ------------------------------------------------------- chapter 3: scanning
def scanning():
    win, conv = _converter("project")
    _set_raw(conv)
    _expand_raw(conv, 1)
    H.take(Shot(
        "l03-raw-bar", "The Converter's toolbar and its two path bars: Raw input names the sample's raw "
        "folder, which has not been scanned yet; BIDS output is the project.",
        win, crop=_section(conv, conv._scan_btn.parentWidget(), conv._bids_pathbar, win),
        regions=[Region("scan", "Scan…", conv._scan_btn),
                 Region("raw", "Raw input", conv._raw_pathbar, anchor="l"),
                 Region("bids", "BIDS output", conv._bids_pathbar, anchor="l")]))
    H.take(Shot(
        "l03-raw-tree", "The raw data tree with the sample's folders: eeg, eyetracking, meg, mri, mrs and pet.",
        win, crop_to=conv._col1_frame, allow_elided=("QTreeWidget",)))
    # The scan itself, as the button does it.
    import states
    states.scan(win)
    layout(conv)
    H.take(Shot(
        "l03-after-scan", "The Converter after the scan: 19 rows in the table, the Structure panel's tree, "
        "and the counts in the toolbar.", win, window=True,
        regions=[Region("chips", "The counts", conv._chip_valid.parentWidget(), rect=None)] if False else
        [Region("table", "One row per recording", conv._inspection_unit),
         Region("structure", "The structure the scan found", conv._filter_frame),
         Region("chips", "4 valid, 12 warnings, 0 error, 3 skipped", conv._chip_valid, anchor="l")],
        allow_elided=("QTreeWidget", "QTreeView")))
    bar = conv._scan_btn.parentWidget()
    x, y, w, h = H._rect_in(bar, win)
    x2 = H._rect_in(conv._revalidate_btn, win)
    H.take(Shot(
        "l03-chips", "The toolbar after the scan: the scan table 0001__raw, Undo and Redo, and the counts "
        "4 valid, 12 warnings, 0 error and 3 skipped.",
        win, crop=(x, y, x2[0] + x2[2] + 12 - x, h),
        regions=[Region("table", "The scan table", conv._scans_combo),
                 Region("valid", "Valid", conv._chip_valid), Region("warn", "Warnings", conv._chip_warn),
                 Region("err", "Errors", conv._chip_err), Region("skip", "Skipped", conv._chip_skip)]))
    H.take(Shot(
        "l03-log", "The Log after the scan, with the scan's own lines.", win, crop_to=conv._log_frame,
        allow_elided=("RunLog",)))
    from bidsmgr.gui.issues_dialog import IssuesDialog
    for sev, sid, alt in (("skip", "l03-skipped", "The Skipped list: three scout reconstructions and the "
                           "PhoenixZIPReport, each with the reason it is left out."),
                          ("warn", "l03-warnings", "The Warnings list: every MRI, MRS and PET row carries the "
                           "note that the scan holds more than one study.")):
        d = _dialog(IssuesDialog(conv.model(), sev, parent=conv), (560, 620))
        H.take(Shot(sid, alt, d))
        d.close()


def scan_settings():
    win, conv = _converter("scanned")
    from bidsmgr.gui.app_settings import AppSettings
    from bidsmgr.gui.settings_dialog import SettingsDialog
    d = SettingsDialog(AppSettings.load(), win)
    d.resize(1040, 760)
    d.show_page("Scan")
    _dialog(d)
    H.take(Shot("l03-settings-scan", "Settings, Scan page: parallel workers, probe conversion, converter "
                "fields, the classifier switch and the index widths.", d))
    # 1.5.2: where subject labels come from, and the entities the sequence name decides.
    from harness import Region
    from PyQt6.QtWidgets import QGroupBox
    combo = d._scan_subject_from
    defaults = next(b for b in d.findChildren(QGroupBox) if b.isAncestorOf(combo))
    # Only this box is in the picture: the boxes under it are hidden while the
    # list is open, so the list does not sit on half-cut lines of their text.
    below = [b for b in d.findChildren(QGroupBox)
             if b is not defaults and b.isVisible() and b.parentWidget() is defaults.parentWidget()
             and b.y() > defaults.y()]
    for b in below:
        b.hide()
    H.pump(settle=20)
    combo.showPopup()
    H.pump(settle=40)
    popup = combo.view().window()
    x, y, w, h = H._rect_in(defaults, d)
    px, py, pw, ph = H._global_rect_in(popup, d)
    bottom = py + ph + 8
    top = y - 2
    H.take(Shot("l03-settings-subjects", "Settings, Scan page, Subject labels opened: numbers by default, or "
                "the patient ID, the given name or the family name from the DICOM header.", d,
                crop=(x - 12, top, w + 24, bottom - top), popups=[popup]))
    combo.hidePopup()
    for b in below:
        b.show()
    H.pump(settle=20)
    box = next(b for b in d.findChildren(QGroupBox) if b.isAncestorOf(d._name_entities["acq"]))
    _scroll_to_widget(d, box, pad=40)
    H.take(Shot("l03-settings-name-entities", "Settings, Scan page, at the bottom: the entities whose value "
                "the sequence name decides when the operator wrote it there, such as acq- or run-.", d,
                crop_to=box, margin=12))
    d.show_page("Scan rules")
    H.pump(settle=20)
    H.take(Shot("l03-settings-rules", "Settings, Scan rules page: series to leave out, your own naming "
                "hints, and the built-in criteria.", d))
    d.close()


# --------------------------------------------------- chapter 4: the table
def table():
    win, conv = _converter("scanned")
    layout(conv)
    m = conv.model()
    row = _row(conv, sequence="ses-pre_T1w")
    _properties(conv, row)
    rects = _header_rects(conv, ["include", "status", "id", "ses", "datatype", "suffix", "basename"])
    labels = {"include": "Include", "status": "State", "id": "Subject", "ses": "Session",
              "datatype": "Datatype", "suffix": "Suffix", "basename": "BIDS name"}
    H.take(Shot(
        "l04-table", "The scan table after the scan, with the T1w row selected.",
        win, crop_to=conv._inspection_unit,
        regions=[Region(k, labels[k], rect=rects[k], anchor="t") for k in rects] +
                [Region("footer", "Highlight aborts, Dataset metadata, Manage columns, Bulk edit",
                        H.find(conv, name="inspection-footer"), anchor="l")],
        allow_elided=("QTableView",)))
    # Editing one cell: the session of the T1w row.
    ci = [c.key for c in m.COLUMNS].index("ses")
    idx = m.index(row, ci)
    conv._table.setCurrentIndex(idx)
    conv._table.edit(idx)
    H.pump(settle=30)
    H.take(Shot("l04-edit-cell", "Editing the session of one row in the table: the cell becomes a field.",
                win, crop=_table_crop(conv, win, rows=8), allow_elided=("QTableView",)))
    conv._table.closePersistentEditor(idx)
    H.pump(settle=10)
    # Bulk edit: every included row to subject 001.
    df = m.dataframe()
    rows = [r for r in range(len(df)) if str(df.iloc[r]["include"]) in ("1", "True", "true")]
    conv.select_rows(rows)
    H.pump(settle=20)
    from bidsmgr.gui.bulk_edit_dialog import BulkEditDialog
    d = BulkEditDialog(m, rows, parent=conv)
    _dialog(d, (640, 640))
    d._col_combo.setCurrentIndex(d._col_combo.findData("id"))
    H.pump(settle=10)
    if d._value_edit.isVisible():
        d._value_edit.setText("001")
    else:
        d._value_combo.setCurrentText("001")
    d._replan()
    H.pump(settle=30)
    H.take(Shot("l04-bulk-dialog", "Bulk edit with 15 rows selected: the subject column set to 001, and "
                "the four rows it would change listed with their names now and after.", d))
    d.close()
    from bidsmgr.gui.column_manager_dialog import ColumnManagerDialog
    c = _dialog(ColumnManagerDialog(dict(conv._column_visible), conv), (600, 680))
    H.take(Shot("l04-columns", "Manage columns: every column of the table with a note on what it holds.", c))
    c.close()


def _table_crop(conv, win, rows=10):
    x, y, w, h = H._rect_in(conv._inspection_unit, win)
    rh = conv._table.verticalHeader().defaultSectionSize() or 26
    hh = conv._table.horizontalHeader().height()
    tx, ty, tw, th = H._rect_in(conv._table, win)
    return (x, y, w, ty - y + hh + rows * rh + 6)


GROUPS = {
    "converter-map": window_map,
    "l03-scanning": scanning,
    "l03-settings": scan_settings,
    "l04-table": table,
}


# ------------------------------------------------------ chapter 5: naming
def naming():
    win, conv = _converter("scanned")
    layout(conv, fold_trees=True, props=430)
    p = conv._properties
    flair = _row(conv, sequence="ses-pre_T2w")
    _properties(conv, flair)
    sec = getattr(p, "why_box", None)
    if sec is not None:
        _splitters(conv)["props"].setSizes([680, 560])
        H.pump(settle=30)
        sec.set_expanded(True)
        H.pump(settle=30)
        p_frame = conv._properties_frame
        # Bring the box into view inside the panel's scroll area.
        from PyQt6.QtWidgets import QScrollArea
        area = p.findChild(QScrollArea)
        if area is not None:
            area.ensureWidgetVisible(sec, 0, 40)
            bar = area.verticalScrollBar()
            top = sec.mapTo(area.widget(), sec.rect().topLeft()).y()
            bar.setValue(max(0, top - 12))
            H.pump(settle=20)
        H.take(Shot("l05-why", "The Properties panel of the FLAIR row, scrolled to Why this name: the "
                    "evidence the classifier weighed, its confidence, and the other names it considered.",
                    win, crop_to=p_frame))
        if area is not None:
            area.verticalScrollBar().setValue(0)
            H.pump(settle=20)
    _splitters(conv)["props"].setSizes([810, 430])
    H.pump(settle=20)
    t1 = _row(conv, sequence="ses-pre_T1w")
    _properties(conv, t1)
    pf = conv._properties_frame
    regions = [Region("names", "Datatype and suffix", p.findChild(type(conv._scans_combo)) or pf, anchor="l")]
    H.take(Shot("l05-properties", "The Properties panel of the T1w row: datatype and suffix, the entities "
                "the standard allows for it, and the entity values that build its name.", win, crop_to=pf))
    # The table's right-click menu on the FLAIR row.
    _properties(conv, flair)
    H.pump(settle=20)
    menu = conv._row_menu(conv._table, [flair])
    from PyQt6.QtCore import QPoint
    table = conv._table
    hh = table.horizontalHeader()
    col = [c.key for c in conv.model().COLUMNS].index("suffix")
    x = hh.sectionViewportPosition(col) + hh.sectionSize(col) // 2
    y = table.rowViewportPosition(flair) + table.rowHeight(flair) // 2
    menu.popup(table.viewport().mapToGlobal(QPoint(x, y)))
    H.pump(settle=30)
    sub = None
    for a in menu.actions():
        if a.menu() is not None and a.text().startswith("Name it instead"):
            sub = a.menu()
            ar = menu.actionGeometry(a)
            menu.setActiveAction(a)
            sub.popup(menu.mapToGlobal(QPoint(ar.right() - 4, ar.top() - 4)))
            H.pump(settle=30)
            break
    pops = [menu] + ([sub] if sub is not None else [])
    x, y, w, h = H._rect_in(conv._inspection_unit, win)
    H.take(Shot("l05-row-menu", "The table's right-click menu on the FLAIR row: preview the image, show the "
                "DICOM header, or give the person a new subject number.",
                win, crop=(x, y, w, h), popups=pops, allow_elided=("QTableView",)))
    if sub is not None:
        sub.hide()
    menu.hide()
    H.pump(settle=10)
    # The DICOM header of the T1w series.
    path = conv._first_dicom_of(t1)
    dw = conv.show_dicom_header(path)
    dw.resize(980, 700)
    H.pump(lambda: not dw.pane.is_loading() and dw.pane.header() is not None, timeout=30, settle=40)
    H.take(Shot("l05-dicom", "The DICOM header viewer of the T1w series: every element with its tag, and "
                "what BIDS Manager reads it for. Identifying values are hidden.", dw))
    dw.close()


def naming_curated():
    win, conv = _converter("curated")
    layout(conv, fold_trees=True, props=430)
    ref = _row(conv, bids_guess_suffix="mrsref")
    _properties(conv, ref)
    H.take(Shot("l05-mrsref", "Properties of the spectroscopy water reference after the change: suffix "
                "mrsref, no run, and the predicted path sub-001/ses-01/mrs/sub-001_ses-01_mrsref.",
                win, crop_to=conv._properties_frame))


# --------------------------------------- chapter 6: before you convert
def checking():
    win, conv = _converter("scanned")
    layout(conv)
    fp = conv._filter_pane
    H.take(Shot("l06-structure", "The Structure view beside the table after the scan: one branch per proposed "
                "subject and session, then datatypes and the BIDS names.", win, crop_to=conv._filter_frame,
                allow_elided=("QTreeWidget",)))
    fp.set_mode("recordings")
    H.pump(settle=30)
    H.take(Shot("l06-recordings", "The Recordings view beside the table: each kind of recording, and which "
                "subjects have it.", win, crop_to=conv._filter_frame, allow_elided=("QTreeWidget",)))
    fp.set_mode("structure")
    conv.set_inspection_view("overview", remember=False)
    _wait_overview(conv)
    H.take(Shot("l06-overview-before", "The Overview after the scan: 4 subjects, 3 sessions, 15 recordings "
                "to convert, and one finding: three subjects have no session while the other one has three.",
                win, crop_to=conv._inspection_unit))
    conv.set_inspection_view("table", remember=False)
    H.pump(settle=10)


def checking_curated():
    win, conv = _converter("curated")
    layout(conv)
    conv.set_inspection_view("overview", remember=False)
    _wait_overview(conv)
    H.take(Shot("l06-overview-after", "The Overview after one subject and one session were set on every row: "
                "1 subject, 1 session, 15 recordings to convert, nothing worth a look.",
                win, crop_to=conv._inspection_unit))
    conv.set_inspection_view("table", remember=False)
    fp = conv._filter_pane
    fp.set_mode("preview")
    _wait_preview(conv)
    pv = fp.preview
    pv.select_path("sub-001/ses-01/func/sub-001_ses-01_task-rest_bold.json")
    H.pump(settle=10)
    _wait_preview(conv)
    sp = _splitters(conv)
    sp["columns"].setSizes([200, 560, 808])
    H.pump(settle=30)
    H.take(Shot("l06-preview-json", "The BIDS preview with the BOLD run's sidecar selected: the file tree the "
                "conversion will write, and below it the predicted content, each value coloured by where it "
                "comes from.", win, crop_to=conv._filter_frame, allow_elided=("QTreeWidget",)))


GROUPS.update({
    "l05-naming": naming,
    "l05-naming-curated": naming_curated,
    "l06-checking": checking,
    "l06-checking-curated": checking_curated,
})


# ----------------------------------------------- chapter 7: metadata
def _meta_dialog(conv):
    from bidsmgr.gui.recording_meta_dialog import RecordingMetaDialog
    from bidsmgr.metadata.template_plan import blood_conditions, example_paths_for, pair_counts, present_pairs
    from bidsmgr.recording_meta import scaffold_sidecar_path
    df = conv._model.dataframe()
    dlg = RecordingMetaDialog(
        scaffold_sidecar_path(conv._output_tsv), conv._present_datatypes(), conv,
        montage_suggestions=conv._montage_suggestions(), scan_suggestions=conv._scan_suggestions(),
        present_pairs=present_pairs(df), example_paths=example_paths_for(df), pair_counts=pair_counts(df),
        also_ask={("pet", "blood"): blood_conditions(df)}, bids_root=conv._bids_root,
        eyetrack="modality" in df.columns and bool((df["modality"].astype(str) == "eyetrack").any()))
    dlg.resize(700, 820)
    dlg.show()
    H.pump(settle=40)
    return dlg


def _scroll_to(dlg, widget, offset=10):
    from PyQt6.QtWidgets import QScrollArea
    area = dlg.findChild(QScrollArea)
    top = widget.mapTo(area.widget(), widget.rect().topLeft()).y()
    area.verticalScrollBar().setValue(max(0, top - offset))
    H.pump(settle=20)


def metadata():
    win, conv = _converter("curated")
    layout(conv)
    dlg = _meta_dialog(conv)
    H.take(Shot("l07-dialog", "The Dataset metadata dialog: dataset_description.json first, then one "
                "section per kind of file, each saying how many questions it has.", dlg))
    import states
    from bidsmgr.gui.widgets import template_form
    w = dlg._template.widgets_for("dataset_description")
    for field, value in states.DESCRIPTION.items():
        if field in w:
            template_form.write_field_widget(w[field], value)
    H.pump(settle=20)
    sec = dlg._template.section_widget("dataset_description")
    sec.set_expanded(True)
    H.pump(settle=20)
    _scroll_to(dlg, sec)
    H.take(Shot("l07-description", "The dataset_description.json section with two authors, a licence, "
                "acknowledgements and how to acknowledge filled in.", dlg))
    sec.set_expanded(False)
    key = "func/bold"
    bold = dlg._template.section_widget(key)
    if bold is not None:
        parent = bold.parentWidget()
        while parent is not None and parent is not dlg:
            if hasattr(parent, "set_expanded"):
                parent.set_expanded(True)
            parent = parent.parentWidget()
        bold.set_expanded(True)
        H.pump(settle=30)
        _scroll_to(dlg, bold)
        H.take(Shot("l07-template-bold", "The section for every *_bold.json: the task's description and "
                    "instructions asked once, written into every BOLD run's sidecar.", dlg))
        bold.set_expanded(False)
    dlg._import_pet_dose(states.SAMPLE / "dose_sheet.csv")
    dlg._participants_file.setText(str(states.SAMPLE / "participants.csv"))
    H.pump(settle=30)
    from PyQt6.QtWidgets import QGroupBox
    box = next(b for b in dlg.findChildren(QGroupBox) if b.title() == "PET dose file")
    _scroll_to(dlg, box)
    H.take(Shot("l07-pet-dose", "The PET dose file group after importing dose_sheet.csv, and the "
                "participants spreadsheet below it.", dlg))
    dlg.close()


def metadata_properties():
    win, conv = _converter("described")
    layout(conv, props=380)
    eeg = _row(conv, bids_name="sub-001_ses-01_task-rest_eeg")
    _properties(conv, eeg)
    p = conv._properties
    from PyQt6.QtWidgets import QLabel, QScrollArea
    area = p.findChild(QScrollArea)
    lab = next((w for w in p.findChildren(QLabel) if w.text().strip().upper() == "MINIMAL METADATA"), None)
    if area is not None and lab is not None:
        top = lab.mapTo(area.widget(), lab.rect().topLeft()).y()
        area.verticalScrollBar().setValue(max(0, top - 8))
        H.pump(settle=20)
    H.take(Shot("l07-properties-minimal", "The Properties panel of the resting EEG row, scrolled to its "
                "minimal metadata: the participant, companion files, and the EEG acquisition fields.",
                win, crop_to=conv._properties_frame))


def dummy_volumes():
    """Chapter 7: a functional run's own number of dummy volumes, in Properties."""
    win, conv = _converter("described")
    layout(conv, props=380)
    bold = _row(conv, bids_name="sub-001_ses-01_task-rest_bold")
    # This run's own number, as typed in the field: its section opens with it.
    conv.model().set_drop_volumes(bold, 4)
    _properties(conv, bold)
    p = conv._properties
    spin = p.dummy_volumes_spin
    from bidsmgr.gui.widgets.template_form import CollapsibleSection
    from PyQt6.QtWidgets import QScrollArea
    box = H.ancestor_of_type(spin, CollapsibleSection) if hasattr(H, "ancestor_of_type") else None
    if box is None:
        box = spin
        while box is not None and not isinstance(box, CollapsibleSection):
            box = box.parentWidget()
    area = p.findChild(QScrollArea)
    top = box.mapTo(area.widget(), box.rect().topLeft()).y()
    area.verticalScrollBar().setValue(max(0, top - 52))
    H.pump(settle=20)
    from harness import Region
    # The marker in the free space right of "of 60 volumes", on the number's row: on the
    # field's edge it covered the "o" of "of".
    from PyQt6.QtCore import QPoint
    from PyQt6.QtWidgets import QLabel
    of = next(w for w in box.findChildren(QLabel) if w.text().startswith("of "))
    at = of.mapTo(win, QPoint(of.width() + 8, of.height() // 2 - 10))
    H.take(Shot("l07-dummy-volumes", "The Properties panel of the BOLD run, at Dummy volumes: 4 for this "
                "run, where Default would take the number in Settings, and the physiological log "
                "recorded with it.",
                win, crop_to=conv._properties_frame,
                regions=[Region("dummy", "This run's dummy volumes", rect=(at.x(), at.y(), 20, 20),
                                anchor="c")]))
    # The run's physiological log: read only, the number is the run's.
    log = _row(conv, bids_name="sub-001_ses-01_task-rest_physio")
    _properties(conv, log)
    box = p.physio_volumes_box
    box.set_expanded(True)
    H.pump(settle=20)
    top = box.mapTo(area.widget(), box.rect().topLeft()).y()
    area.verticalScrollBar().setValue(max(0, top - 52))
    H.pump(settle=20)
    H.take(Shot("l07-dummy-physio", "The Properties panel of the BOLD run's physiological log, at "
                "Dummy volumes: the 4 removed from the run it was recorded with, and that run.",
                win, crop_to=conv._properties_frame,
                regions=[Region("run", "The run it follows", p.physio_run_label, anchor="r")]))


# ------------------------------------------------- chapter 8: converting
def converting_settings():
    win, conv = _converter("described")
    from bidsmgr.gui.app_settings import AppSettings
    from bidsmgr.gui.settings_dialog import SettingsDialog
    d = SettingsDialog(AppSettings.load(), win)
    d.resize(900, 760)
    d.show_page("Convert")
    _dialog(d)
    H.take(Shot("l08-settings-convert", "Settings, Convert page: existing subjects, curated metadata, "
                "residuals, fieldmap links, EEG to EDF and defacing.", d))
    from PyQt6.QtWidgets import QGroupBox, QScrollArea
    box = next(b for b in d.findChildren(QGroupBox) if b.title().startswith("Post-convert"))
    area = next(a for a in d.findChildren(QScrollArea) if a.isVisible() and a.widget().isAncestorOf(box))
    top = box.mapTo(area.widget(), box.rect().topLeft()).y()
    area.verticalScrollBar().setValue(max(0, top - 8))
    H.pump(settle=20)
    H.take(Shot("l08-settings-chain", "Settings, Convert page, further down: source data and the "
                "post-convert chain that runs after every conversion.", d))
    # 1.5.2: dummy volumes, and how a physiological log is written.
    from harness import Region
    _scroll_to_widget(d, d._convert_drop_volumes, pad=110)
    H.take(Shot("l08-settings-physio", "Settings, Convert page: Dummy volumes to leave out at the start of "
                "every functional run, how a physiological log is written, and cropping it to the run.", d,
                regions=[Region("dummy", "Dummy volumes", d._convert_drop_volumes),
                         Region("physio", "One table per rate, or one table for the run",
                                d._convert_physio_layout),
                         Region("crop", "Crop to the run", d._convert_physio_align)]))
    d.close()


def converted():
    win, conv = _converter("converted")
    layout(conv)
    op = conv._output_pane
    H.pump(lambda: not op._scan_in_progress, timeout=30, settle=30)
    from PyQt6.QtWidgets import QTreeWidget, QTreeView
    tree = op.findChild(QTreeWidget) or op.findChild(QTreeView)
    if tree is not None:
        tree.expandToDepth(3)
        H.pump(settle=30)
    sp = _splitters(conv)
    sp["columns"].setSizes([420, 300, 848])
    H.pump(settle=20)
    H.take(Shot("l08-output-tree", "The output data tree after the conversion: the dataset's files under "
                "sub-001/ses-01, one folder per datatype.", win, crop_to=conv._col1_frame,
                allow_elided=("QTreeWidget", "QTreeView")))


GROUPS.update({
    "l07-metadata": metadata,
    "l07-properties": metadata_properties,
    "l07-dummy": dummy_volumes,
    "l08-settings": converting_settings,
    "l08-converted": converted,
})


def table_after():
    win, conv = _converter("curated")
    layout(conv)
    t1 = _row(conv, sequence="ses-pre_T1w")
    _properties(conv, t1)
    H.take(Shot("l04-table-after", "The table after the two bulk edits: every row to convert has subject 001 "
                "and session 01, and the BIDS names follow.", win, crop_to=conv._inspection_unit,
                allow_elided=("QTableView",)))


GROUPS.update({"l04-table-after": table_after})


def preview():
    """Preview the image: the T1w series converted on the side and shown."""
    win, conv = _converter("scanned")
    layout(conv, fold_trees=True, props=430)
    t1 = _row(conv, sequence="ses-pre_T1w")
    _properties(conv, t1)
    p = conv._properties
    p.preview(t1)
    H.pump(lambda: getattr(p, "preview_dialog", None) is not None, timeout=20, settle=10)
    d = p.preview_dialog
    d.resize(1000, 700)
    H.pump(lambda: not d.is_pending(), timeout=180, settle=40)
    H.wait(1.5)
    H.pump(settle=40)
    H.take(Shot("l05-preview", "Preview the image on the T1w row: the series converted aside and shown in "
                "the viewer before anything is written to the dataset.", d, anatomy_ok=True,
                sample="multimodal v2 (OL_3844, consented)"))
    d.close()


GROUPS.update({"l05-preview": preview})

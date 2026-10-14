"""The guides: each on its own sample, driven from an empty project to a
validated dataset, with the numbers its page prints written to
``content/_measured/<guide>.json`` (by the dark run).

No head is drawn from a sample whose participants did not consent to their
face being shown: the MRI guide (Oldenburg 2) shows tables, plots and trees,
never an anatomical rendering.
"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

import harness as H
import shots_converter as SC
import shots_editor as SE
from harness import Region, Shot

MEASURED = H.SITE / "content" / "_measured"


# ----------------------------------------------------------------- helpers
def project(name: str):
    root = H.STUDIES_REAL / name
    if root.exists():
        shutil.rmtree(root)
    win = H.main_window("welcome", SC.SIZE)
    win.welcome.create_project(H.STUDIES, name)
    H.pump(settle=40)
    return win


def scan(win, raw: Path) -> float:
    conv = win.converter
    conv._raw_root = raw
    conv._raw_pane.set_root(raw)
    conv._show_source_state()
    H.pump(settle=10)
    t0 = time.time()
    conv._on_scan_clicked()
    H.pump(lambda: conv._scan_worker is None or not conv._scan_worker.isRunning(), timeout=1800)
    H.pump(lambda: conv.model() is not None and conv.model().rowCount() > 0, timeout=120, settle=60)
    return round(time.time() - t0, 1)


def included(conv) -> list[int]:
    df = conv.model().dataframe()
    return [r for r in range(len(df)) if str(df.iloc[r]["include"]) in ("1", "True", "true")]


def chips(conv) -> dict:
    return {k: getattr(conv, f"_chip_{k}").text() for k in ("valid", "warn", "err", "skip")}


def scan_record(conv, seconds: float) -> dict:
    df = conv.model().dataframe()
    return {"rows": len(df), "included": len(included(conv)), "seconds": seconds,
            "subjects": sorted(set(df["participant_id"].astype(str)) - {""}),
            "sessions": sorted(set(df.loc[[i for i in included(conv)], "session"].astype(str)) - {""}),
            "chips": chips(conv)}


def describe(conv, *, description: dict, pet_dose: Path | None = None, participants: Path | None = None,
             fill=None) -> None:
    from bidsmgr.gui.widgets import template_form
    dlg = SC._meta_dialog(conv)
    w = dlg._template.widgets_for("dataset_description")
    for field, value in description.items():
        if field in w:
            template_form.write_field_widget(w[field], value)
    if pet_dose is not None:
        dlg._import_pet_dose(pet_dose)
    if participants is not None:
        dlg._participants_file.setText(str(participants))
    if fill is not None:
        fill(dlg)
    H.pump(settle=20)
    dlg._on_save()
    H.pump(settle=30)
    conv._model.set_global_spec(conv._load_global_spec())
    H.pump(settle=20)


def convert(win) -> dict:
    conv = win.converter
    done = {}
    conv.confirm_sourcedata = lambda _t: True
    conv._show_convert_dialog = lambda rc, parent: done.setdefault("rc", rc)
    t0 = time.time()
    conv.start_convert(conv._bids_root.parent)
    H.pump(lambda: "rc" in done, timeout=3600, settle=60)
    return {"rc": done["rc"], "seconds": round(time.time() - t0, 1)}


def measure(root: Path) -> dict:
    from bidsmgr.editor.validator import validate
    files = [p for p in Path(root).rglob("*") if p.is_file() and ".bidsmgr" not in p.parts]
    rep = validate(Path(root), strict=False)
    out = {"files": len(files), "validation": dict(rep.counts)}
    try:
        report = json.loads((Path(root) / ".bidsmgr" / "metadata_report.json").read_text())
        todo = report.get("todo_fills") or []
        out["todo"] = {"inserted": sum(len(t["fields"]) for t in todo), "files": len(todo)}
    except (OSError, ValueError):
        pass
    return out


def save(guide: str, record: dict) -> None:
    if H.theme() != "dark":
        return
    MEASURED.mkdir(parents=True, exist_ok=True)
    path = MEASURED / f"{guide}.json"
    old = json.loads(path.read_text()) if path.exists() else {}
    old.update(record)
    old["source"] = H.source_info()
    path.write_text(json.dumps(old, indent=1) + "\n")


def editor_on(win, root):
    ed = win.editor
    win._apply_active_view("editor", persist=False)
    H.pump(settle=30)
    from bidsmgr.editor import validate as run_validate
    schema, max_rows, todos = ed._validation_engine_opts()
    rep = run_validate(Path(root), strict=False, schema=schema, max_rows=max_rows, flag_todos=todos)
    ed._on_report_ready(rep, Path(root))
    H.pump(settle=40)
    return ed


def scroll_to_text(panel, text: str, offset: int = 8) -> bool:
    """Scroll a panel's scroll area so the widget showing ``text`` is at its top."""
    from PyQt6.QtWidgets import QScrollArea, QWidget
    area = panel.findChild(QScrollArea)
    for w in panel.findChildren(QWidget):
        t = getattr(w, "text", None)
        try:
            label = t() if callable(t) else ""
        except TypeError:
            label = ""
        if isinstance(label, str) and text in label and w.isVisibleTo(panel):
            top = w.mapTo(area.widget(), w.rect().topLeft()).y()
            area.verticalScrollBar().setValue(max(0, top - offset))
            H.pump(settle=20)
            return True
    print(f"  (no '{text}' found to scroll to)")
    return False


DESCRIPTION = {
    "Authors": ["Example, Ada", "Example, Ben"],
    "License": "CC-BY-4.0",
}


# --------------------------------------------------------------------- MRI
MRI_RAW = H.STUDIES / "MRI_sample_data_neuroimging_unit_oldenburg_2"


def guide_mri():
    win = project("mri_study")
    conv = win.converter
    secs = scan(win, MRI_RAW)
    rec = {"scan": scan_record(conv, secs)}
    SC.layout(conv, log=60)
    SC._properties(conv, SC._row(conv, sequence="ses-pre_T1w"))
    H.take(Shot("guide-mri-table", "The Converter after scanning the MRI sample: 33 rows, the scouts and "
                "scanner reports unticked, two subjects, the first in the sessions pre and post.",
                win, crop_to=conv._inspection_unit, allow_elided=("QTableView",)))
    conv.set_inspection_view("overview", remember=False)
    SC._wait_overview(conv)
    H.take(Shot("guide-mri-overview", "The Overview of the MRI sample: two subjects, one with two sessions and "
                "one without, which it points out.", win, crop_to=conv._inspection_unit))
    conv.set_inspection_view("table", remember=False)
    H.pump(settle=10)
    # The two fieldmaps of the first visit, and the runs each corrects.
    fm = SC._row(conv, sequence="ses-pre_run-02_fmap")
    SC.layout(conv, fold_trees=True, props=520, log=60)
    SC._properties(conv, fm)
    scroll_to_text(conv._properties, "Corrects these runs")
    H.take(Shot("guide-mri-fmap", "Properties of the second fieldmap of session pre: Corrects these runs, with "
                "the resting run ticked, because it was acquired just before it.", win,
                crop_to=conv._properties_frame))
    describe(conv, description=DESCRIPTION)
    rec["convert"] = convert(win)
    root = H.STUDIES_REAL / "mri_study"
    rec["converted"] = measure(root)
    H.snapshot("guide-mri", "mri_study")
    ed = editor_on(win, H.STUDIES / "mri_study")
    SE._expand(ed, 3)
    SE._splitter_sizes(ed, [250, 790, 560])
    SE._select(ed, root, "sub-002/fmap/sub-002_acq-epse2_dir-PA_epi.json", wait=0.8)
    H.take(Shot("guide-mri-editor", "The converted MRI sample in the Editor, validated: the sidecar of the "
                "diffusion run's reversed-phase reference, with IntendedFor and B0FieldIdentifier.", win, window=True,
                allow_elided=("QTreeView", "QTreeWidget", "QTableView")))
    save("mri", rec)
    win.close()


GROUPS = {"guide-mri": guide_mri}


# --------------------------------------------------------------------- EEG
EEG_RAW = H.STUDIES / "EEG_motor_imagery_sample_data"
#: The PhysioNet protocol: what each run of every participant was.
EEG_TASKS = {
    1: ("eyesopen", ""), 2: ("eyesclosed", ""),
    3: ("fist", "1"), 7: ("fist", "2"), 11: ("fist", "3"),
    4: ("fistimagined", "1"), 8: ("fistimagined", "2"), 12: ("fistimagined", "3"),
    5: ("fistsfeet", "1"), 9: ("fistsfeet", "2"), 13: ("fistsfeet", "3"),
    6: ("fistsfeetimagined", "1"), 10: ("fistsfeetimagined", "2"), 14: ("fistsfeetimagined", "3"),
}


def _eeg_run_of(df, r):
    import re
    m = re.search(r"R(\d+)", str(df.iloc[r]["source_file"]))
    return int(m.group(1)) if m else 0


def guide_eeg():
    win = project("eeg_study")
    conv = win.converter
    secs = scan(win, EEG_RAW)
    rec = {"scan": scan_record(conv, secs)}
    m = conv.model()
    df = m.dataframe()
    SC.layout(conv, log=60)
    SC._properties(conv, 2)
    H.take(Shot("guide-eeg-table", "The EEG sample after the scan: 28 recordings, each with the file name as its "
                "task (S001R01, S001R02, ...) and the run number from the file name.", win,
                crop_to=conv._inspection_unit, allow_elided=("QTableView",)))
    # Name one task with Bulk edit, as the page shows.
    rows = [r for r in range(len(df)) if _eeg_run_of(df, r) in (4, 8, 12)]
    conv.select_rows(rows)
    from bidsmgr.gui.bulk_edit_dialog import BulkEditDialog
    d = BulkEditDialog(m, rows, parent=conv)
    d.resize(640, 620)
    d.show()
    H.pump(settle=20)
    d._col_combo.setCurrentIndex(d._col_combo.findData("task"))
    H.pump(settle=20)
    field = d._value_edit if d._value_edit.isVisible() else d._value_combo.lineEdit()
    field.setText("fistimagined")
    d._replan()
    H.pump(settle=30)
    H.take(Shot("guide-eeg-bulk", "Bulk edit with the six recordings of the imagined fist task selected (runs 4, "
                "8 and 12 of both participants): the task set to fistimagined.", d))
    d.close()
    # Every task and run, as the protocol says.
    by = {}
    for r in range(len(df)):
        task, run = EEG_TASKS.get(_eeg_run_of(df, r), ("", ""))
        by.setdefault((task, run), []).append(r)
    with m.edit_group():
        for (task, run), rr in by.items():
            m.bulk_set(rr, "task", task)
    with m.edit_group():
        for (task, run), rr in by.items():
            m.bulk_set(rr, "run", run)
    H.pump(settle=30)
    conv._on_revalidate_clicked()
    H.pump(settle=30)
    df = m.dataframe()
    rec["names"] = sorted({str(x) for x in df["bids_name"] if str(x)})
    SC._properties(conv, 3)
    H.take(Shot("guide-eeg-table-after", "The EEG sample after naming the tasks and runs: fist, fistimagined, "
                "fistsfeet and fistsfeetimagined with runs 1 to 3, eyesopen and eyesclosed.", win,
                crop_to=conv._inspection_unit, allow_elided=("QTableView",)))
    # The metadata an EDF file does not hold.
    from bidsmgr.gui.widgets import template_form
    dlg = SC._meta_dialog(conv)
    w = dlg._template.widgets_for("dataset_description")
    for field_name, value in DESCRIPTION.items():
        if field_name in w:
            template_form.write_field_widget(w[field_name], value)
    found = None
    for key in list(getattr(dlg._template, "_widgets", {})):
        ww = dlg._template.widgets_for(key)
        if "PowerLineFrequency" in ww:
            template_form.write_field_widget(ww["PowerLineFrequency"], 60)
            found = key
    print("  eeg template:", found)
    ev = dlg._events
    for i in range(ev.rowCount()):
        code = ev.item(i, 0).text() if ev.item(i, 0) else ""
        label = {"T0": "rest", "T1": "movement or imagery: left fist, or both fists",
                 "T2": "movement or imagery: right fist, or both feet"}.get(code)
        if label:
            from PyQt6.QtWidgets import QTableWidgetItem
            ev.setItem(i, 1, QTableWidgetItem(label))
    H.pump(settle=20)
    SC._scroll_to(dlg, dlg._montage.parentWidget() if hasattr(dlg, "_montage") else ev.parentWidget(), offset=40)
    H.take(Shot("guide-eeg-meta", "Dataset metadata for the EEG sample: the montage the scan suggests, and the "
                "three event codes of the recordings, each given a label.", dlg))
    if hasattr(dlg, "_montage"):
        i = dlg._montage.findText("standard_1005")
        if i < 0:
            dlg._montage.addItem("standard_1005")
            i = dlg._montage.findText("standard_1005")
        dlg._montage.setCurrentIndex(i)
    dlg._on_save()
    H.pump(settle=30)
    conv._model.set_global_spec(conv._load_global_spec())
    H.pump(settle=20)
    rec["convert"] = convert(win)
    root = H.STUDIES_REAL / "eeg_study"
    rec["converted"] = measure(root)
    ed = editor_on(win, H.STUDIES / "eeg_study")
    SE._expand(ed, 2)
    SE._splitter_sizes(ed, [260, 1340, 0])
    ed._validation_frame.set_collapsed(True)
    H.pump(settle=20)
    v = ed._signal_viewer
    ed.select_file_in_tree(root / "sub-001" / "eeg" / "sub-001_task-fist_run-1_eeg.edf")
    H.pump(lambda: v.page() == "content", timeout=60, settle=30)
    p = v.presenter
    p.load_signal()
    H.pump(lambda: p.pages.currentWidget() is p.traces_page, timeout=120, settle=40)
    v.run("traces.count", n=20)
    v.run("events.show", value=True)
    v.run("traces.filter", hp=1.0, lp=40.0)
    v.qstore.flush()
    H.wait(1.2)
    H.pump(settle=40)
    H.take(Shot("guide-eeg-viewer", "The first run of the fist task, converted, in the signal viewer: 20 of the "
                "64 channels, filtered from 1 to 40 Hz, with the task's events drawn over them.", win,
                crop_to=ed._center_frame))
    save("eeg", rec)
    win.close()


GROUPS.update({"guide-eeg": guide_eeg})


# --------------------------------------------------------------------- MEG
MEG_RAW = H.STUDIES / "MEG_Elekta_sample_data_small"


def guide_meg():
    win = project("meg_study")
    conv = win.converter
    secs = scan(win, MEG_RAW)
    rec = {"scan": scan_record(conv, secs)}
    m = conv.model()
    SC.layout(conv, log=60)
    SC._properties(conv, 0)
    H.take(Shot("guide-meg-table", "The MEG sample after the scan: 23 recordings of two participants, the first "
                "in two sessions found from the dates of its folders, each recording's task and run read from "
                "its file name.", win, crop_to=conv._inspection_unit, allow_elided=("QTableView",)))
    conv.set_inspection_view("overview", remember=False)
    SC._wait_overview(conv)
    H.take(Shot("guide-meg-overview", "The Overview of the MEG sample: two subjects, one with two sessions and one "
                "without, the empty-room recordings counted as tasks.", win, crop_to=conv._inspection_unit))
    conv.set_inspection_view("table", remember=False)
    # The empty-room recordings: one task, noise, numbered before and after.
    df = m.dataframe()
    pre = [r for r in range(len(df)) if str(df.iloc[r]["task"]) == "emptypre"]
    post = [r for r in range(len(df)) if str(df.iloc[r]["task"]) == "emptypost"]
    with m.edit_group():
        m.bulk_set(pre + post, "task", "noise")
    with m.edit_group():
        m.bulk_set(pre, "run", "1")
        m.bulk_set(post, "run", "2")
    H.pump(settle=30)
    conv._on_revalidate_clicked()
    H.pump(settle=30)
    df = m.dataframe()
    rec["names"] = sorted({str(x) for x in df["bids_name"] if str(x)})
    row = pre[0]
    SC.layout(conv, fold_trees=True, props=520, log=60)
    SC._properties(conv, row)
    H.take(Shot("guide-meg-noise", "An empty-room recording after renaming: task noise, run 1 (before the "
                "session's recordings; run 2 is the one after).", win, crop_to=conv._properties_frame))
    describe(conv, description=DESCRIPTION)
    rec["convert"] = convert(win)
    root = H.STUDIES_REAL / "meg_study"
    rec["converted"] = measure(root)
    ed = editor_on(win, H.STUDIES / "meg_study")
    SE._expand(ed, 3)
    SE._splitter_sizes(ed, [300, 1300, 0])
    ed._validation_frame.set_collapsed(True)
    H.pump(settle=20)
    v = ed._signal_viewer
    ed.select_file_in_tree(root / "sub-001" / "ses-2" / "meg" / "sub-001_ses-2_task-driving_run-1_meg.fif")
    H.pump(lambda: v.page() == "content", timeout=60, settle=30)
    p = v.presenter
    p.load_signal()
    H.pump(lambda: p.pages.currentWidget() is p.traces_page, timeout=180, settle=40)
    v.run("traces.type", ch_type="mag")
    v.run("traces.count", n=24)
    v.run("traces.filter", hp=1.0, lp=40.0)
    v.run("traces.normalize", value=True)
    v.qstore.flush()
    H.wait(1.2)
    H.pump(settle=40)
    H.take(Shot("guide-meg-viewer", "The first driving run of the second session, converted: 24 of the "
                "magnetometers, filtered from 1 to 40 Hz, each scaled to itself.", win, crop_to=ed._center_frame))
    save("meg", rec)
    win.close()


# --------------------------------------------------------------------- PET
PET_SAMPLE = H.STUDIES / "BIDS_Manager_PET_sample"


def guide_pet():
    win = project("pet_study")
    conv = win.converter
    secs = scan(win, PET_SAMPLE / "raw")
    rec = {"scan": scan_record(conv, secs)}
    SC.layout(conv, fold_trees=True, props=520, log=60)
    dlg = SC._meta_dialog(conv)
    from bidsmgr.gui.widgets import template_form
    w = dlg._template.widgets_for("dataset_description")
    for field_name, value in DESCRIPTION.items():
        if field_name in w:
            template_form.write_field_widget(w[field_name], value)
    dlg._import_pet_dose(PET_SAMPLE / "dose_sheet.csv")
    H.pump(settle=30)
    from PyQt6.QtWidgets import QGroupBox
    box = [b for b in dlg.findChildren(QGroupBox) if b.title() == "PET dose file"]
    if box:
        SC._scroll_to(dlg, box[0], offset=30)
    H.take(Shot("guide-pet-dose", "Dataset metadata after importing the sample's dose sheet: the status line "
                "says how many fields it filled, and the PET fields below hold them.", dlg))
    dlg._on_save()
    H.pump(settle=30)
    conv._model.set_global_spec(conv._load_global_spec())
    H.pump(settle=20)
    # The blood curves, attached to the PET run.
    p = conv._properties
    blood = PET_SAMPLE / "raw" / "FDG_phantom_01" / "blood"
    p._set_blood(0, "wholeblood", "manual", str(blood / "whole_blood.bld"))
    p._set_blood(0, "plasma", "manual", str(blood / "plasma_parent.bld"))
    H.pump(settle=20)
    SC._properties(conv, 0)
    scroll_to_text(p, "BLOOD SAMPLING")
    H.take(Shot("guide-pet-blood", "The PET row's blood sampling: the whole-blood and plasma curves attached, both "
                "drawn by hand.", win, crop_to=conv._properties_frame))
    rec["convert"] = convert(win)
    root = H.STUDIES_REAL / "pet_study"
    rec["converted"] = measure(root)
    ed = editor_on(win, H.STUDIES / "pet_study")
    SE._expand(ed, 3)
    SE._splitter_sizes(ed, [320, 1280, 0])
    ed._validation_frame.set_collapsed(True)
    H.pump(settle=20)
    blood_tsv = sorted((root / "sub-001" / "pet").glob("*_blood.tsv"))
    if blood_tsv:
        SE._select(ed, root, str(blood_tsv[0].relative_to(root)), wait=1.0)
    H.take(Shot("guide-pet-editor", "The converted PET sample in the Editor: the PET image, its sidecar, and the "
                "blood tables, one per sampling.", win, window=True,
                allow_elided=("QTreeView", "QTreeWidget", "QTableView")))
    save("pet", rec)
    win.close()
    # The ECAT scan, in a project of its own.
    win = project("pet_ecat_study")
    conv = win.converter
    secs = scan(win, PET_SAMPLE / "extra_ecat")
    rec2 = {"scan": scan_record(conv, secs)}
    SC.layout(conv, log=60)
    SC._properties(conv, 0)
    H.take(Shot("guide-pet-ecat", "The ECAT scan of the PET sample: one row, its format ECAT, recognised from the "
                "file's contents.", win, crop_to=conv._inspection_unit, allow_elided=("QTableView",)))
    describe(conv, description=DESCRIPTION, pet_dose=PET_SAMPLE / "extra_ecat" / "dose_sheet_ecat.csv")
    rec2["convert"] = convert(win)
    rec2["converted"] = measure(H.STUDIES_REAL / "pet_ecat_study")
    save("pet", {"ecat": rec2})
    win.close()


# ------------------------------------------------------------ eye tracking
def guide_eye():
    win, conv = SC._converter("curated")
    m = conv.model()
    df = m.dataframe()
    eye = [r for r in range(len(df)) if str(df.iloc[r]["modality"]) == "eyetrack"][0]
    bold = SC._row(conv, bids_guess_suffix="bold")
    SC.layout(conv, fold_trees=True, props=520, log=60)
    SC._properties(conv, eye)
    scroll_to_text(conv._properties, "EYE TRACKING")
    H.take(Shot("guide-eye-props", "Properties of the eye-tracking row: the run it was recorded during (not chosen "
                "yet), and the screen and distances the standard asks for.", win, crop_to=conv._properties_frame))
    conv._properties.pair_with_run(eye, bold)
    H.pump(settle=30)
    conv._on_revalidate_clicked()
    H.pump(settle=30)
    SC.layout(conv, log=60)
    conv.select_rows([eye])
    H.pump(settle=20)
    H.take(Shot("guide-eye-paired", "The table after pairing the eye-tracking row with the resting BOLD run: the "
                "row now lands in func, named after the run.", win, crop_to=conv._inspection_unit,
                allow_elided=("QTableView",)))
    rec = {"paired_name": str(m.dataframe().iloc[eye]["bids_name"])}
    win.close()
    root = H.restore("converted")
    win = H.main_window("welcome", SC.SIZE)
    H.open_project(win, root, "editor")
    ed = win.editor
    H.pump(settle=40)
    SE._expand(ed, 4)
    SE._splitter_sizes(ed, [320, 1280, 0])
    ed._validation_frame.set_collapsed(True)
    H.pump(settle=20)
    rel = "sub-001/ses-01/beh/sub-001_ses-01_task-rest_recording-eye1_physio.tsv.gz"
    tsv = ed._tsv_viewer
    ed.select_file_in_tree(Path(root) / rel)
    H.pump(lambda: getattr(tsv, "_loader", None) is None or not tsv._loader.isRunning(), timeout=60, settle=40)
    H.wait(0.8)
    btn = H.button(tsv, "Visualize")
    if btn is not None:
        btn.click()
        H.wait(2.0)
        H.pump(settle=60)
    H.take(Shot("guide-eye-plot", "The first eye's recording of the sample, converted and drawn with Visualize: "
                "gaze position and pupil size on one time axis.", win, crop_to=ed._center_frame))
    files = sorted(p.name for p in (H.STUDIES_REAL / "multimodal_study" / "sub-001" / "ses-01" / "beh").iterdir())
    rec["files"] = files
    save("eye", rec)
    win.close()


# ------------------------------------------------------- defacing, adopting
def guide_deface():
    win, ed, root, _ = SE._editor("edited")
    from bidsmgr.gui.deface_dialog import DefaceDialog
    for cls_name, sid, alt in (("DefaceDialog", "guide-deface-dialog", "Deface, for the whole dataset: the images "
                                "that can be defaced, the engine, and what will happen to each."),):
        pass
    try:
        from bidsmgr.gui.deface_dialog import SkullStripDialog  # noqa: F401
    except ImportError:
        SkullStripDialog = None
    ed._on_tool("strip") if hasattr(ed, "_on_tool") else None
    win.close()


def guide_adopt():
    import subprocess
    src = H.STATES / "converted" / "multimodal_study"
    dst = H.STUDIES_REAL / "shared_dataset"
    if dst.exists():
        shutil.rmtree(dst)
    subprocess.run(["cp", "-c", "-R", str(src), str(dst)], check=True)
    shutil.rmtree(dst / ".bidsmgr", ignore_errors=True)
    win = H.main_window("welcome", SE.SIZE)
    win._on_view_folder(H.STUDIES / "shared_dataset")
    H.pump(settle=60)
    ed = win.editor
    SE._expand(ed, 2)
    SE._select(ed, H.STUDIES / "shared_dataset", "participants.tsv", wait=0.8)
    H.take(Shot("guide-adopt-view", "A BIDS dataset made elsewhere, open in the Editor to view only: the path bar "
                "says so, and offers Open as project.", win, window=True,
                allow_elided=("QTreeView", "QTreeWidget", "QTableView")))
    win._on_editor_open_project(H.STUDIES / "shared_dataset")
    H.pump(settle=60)
    win._apply_active_view("editor", persist=False)
    H.pump(settle=40)
    SE._expand(win.editor, 2)
    SE._select(win.editor, H.STUDIES / "shared_dataset", "dataset_description.json", wait=0.8)
    H.take(Shot("guide-adopt-project", "The same dataset opened as a project: BIDS Manager added its .bidsmgr "
                "folder, and every tool of the Editor is available.", win, window=True,
                allow_elided=("QTreeView", "QTreeWidget", "QTableView")))
    win.close()


GROUPS.update({"guide-meg": guide_meg, "guide-pet": guide_pet, "guide-eye": guide_eye,
               "guide-adopt": guide_adopt})


# ------------------------------------------------------------ MRI, advanced
ADV_RAW = H.STUDIES / "MRI_sample_data_neuroimging_unit_oldenburg_1"


def _why(conv, row, sid, alt):
    p = conv._properties
    SC._properties(conv, row)
    sec = getattr(p, "why_box", None)
    if sec is None:
        return
    sec.set_expanded(True)
    H.pump(settle=30)
    from PyQt6.QtWidgets import QScrollArea
    area = p.findChild(QScrollArea)
    top = sec.mapTo(area.widget(), sec.rect().topLeft()).y()
    area.verticalScrollBar().setValue(max(0, top - 12))
    H.pump(settle=20)
    H.take(Shot(sid, alt, conv.window(), crop_to=conv._properties_frame))


def guide_mri_advanced():
    win = project("mri_advanced_study")
    conv = win.converter
    secs = scan(win, ADV_RAW)
    rec = {"scan": scan_record(conv, secs)}
    m = conv.model()
    df = m.dataframe()
    rec["left_out"] = sorted({str(df.iloc[r]["sequence"]) for r in range(len(df))
                              if str(df.iloc[r]["include"]) not in ("1", "True", "true")})
    SC.layout(conv, log=60)
    table = conv._table
    tensor = SC._row(conv, sequence="ses-pre_dir-ap_dwi_TENSOR")
    table.scrollTo(m.index(tensor, 0))
    SC._properties(conv, SC._row(conv, sequence="ses-pre_dir-ap_dwi_FA"))
    H.take(Shot("guide-adv-table", "The advanced MRI sample after the scan, scrolled to the diffusion series: "
                "the scanner's FA, colour FA and trace maps kept as diffusion files, its tensor left out because "
                "it holds no image.", win, crop_to=conv._inspection_unit, allow_elided=("QTableView",)))
    SC.layout(conv, fold_trees=True, columns=(200, 420, 960), props=560, log=60)
    _why(conv, SC._row(conv, sequence="ses-post_acq-grenm2mm_run-01_T1w"), "guide-adv-why",
         "Why this name for the series the scanner called ses-post_acq-grenm2mm_run-01_T1w: the evidence for a "
         "T1-weighted magnitude image, and the alternatives.")
    # The spectroscopy water reference is a reference, not a second run.
    df = m.dataframe()
    for r in range(len(df)):
        if "type-ref" in str(df.iloc[r]["sequence"]):
            m.set_datatype_suffix(r, "mrs", "mrsref")
            m.set_entity(r, "run", "")
        elif str(df.iloc[r]["datatype"]) == "mrs":
            m.set_entity(r, "run", "")
    H.pump(settle=30)
    conv._on_revalidate_clicked()
    H.pump(settle=30)
    describe(conv, description=DESCRIPTION)
    rec["convert"] = convert(win)
    root = H.STUDIES_REAL / "mri_advanced_study"
    rec["converted"] = measure(root)
    ed = editor_on(win, H.STUDIES / "mri_advanced_study")
    SE._expand(ed, 4)
    SE._splitter_sizes(ed, [380, 1220, 0])
    ed._validation_frame.set_collapsed(True)
    H.pump(settle=20)
    bval = sorted((root / "sub-001" / "ses-pre" / "dwi").glob("*_dwi.bval"))
    if bval:
        ed.select_file_in_tree(bval[0])
        H.pump(settle=40)
        H.wait(0.8)
        H.pump(settle=30)
    H.take(Shot("guide-adv-dwi", "The diffusion folder of session pre in the Editor: the run with its gradient "
                "table, and the FA, colour FA and trace maps the scanner computed, each a file of its own.",
                win, window=True, allow_elided=("QTreeView", "QTreeWidget", "QTableView")))
    save("mri_advanced", rec)
    win.close()


GROUPS.update({"guide-mri-advanced": guide_mri_advanced})

"""The sample states the course walks through, built by driving the real GUI.

Each state is the multimodal sample's project folder at one point of the
course, made by the same calls a user's clicks make, then kept as an APFS
clone under ``/private/tmp/bm_docs/states/<state>/`` so a shot can start
from it in a second:

    project     the project created on Home (chapter 2)
    scanned     the raw folder scanned: 19 rows (chapter 3)
    curated     one subject and one session for every row, the water
                reference named as one (chapters 4 and 5)
    described   the dataset description, the PET dose sheet and the
                participants file entered in Dataset metadata (chapter 7)
    converted   converted, with the post-convert chain (chapter 8)

    environments/bids-manager/bin/python tools/capture/run.py --states
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import harness as H

SAMPLE = H.STUDIES / "BIDS_Manager_multimodal_sample_v3"
RAW = SAMPLE / "raw"
PROJECT = "multimodal_study"
SUBJECT = "001"
SESSION = "01"

MEASURED = H.SITE / "content" / "_measured" / "multimodal.json"


def _fresh_sample() -> None:
    src = H.WORK / "work" / "samples" / "multimodal"
    dst = H.STUDIES_REAL / "BIDS_Manager_multimodal_sample_v3"
    if not dst.exists():
        import subprocess
        subprocess.run(["cp", "-c", "-R", str(src), str(dst)], check=True)


def build_project(win) -> Path:
    root = H.STUDIES_REAL / PROJECT
    if root.exists():
        shutil.rmtree(root)
    win.welcome.create_project(H.STUDIES, PROJECT)
    H.pump(settle=40)
    H.snapshot("project")
    return H.STUDIES / PROJECT


def scan(win) -> None:
    conv = win.converter
    conv._raw_root = RAW
    conv._raw_pane.set_root(RAW)
    conv._show_source_state()
    H.pump(settle=10)
    conv._on_scan_clicked()
    H.pump(lambda: conv._scan_worker is None or not conv._scan_worker.isRunning(), timeout=600)
    H.pump(lambda: conv.model() is not None and conv.model().rowCount() > 0, timeout=60, settle=60)


def curate(win) -> dict:
    conv = win.converter
    m = conv.model()
    rows = list(range(m.rowCount()))
    df = m.dataframe()
    included = [r for r in rows if str(df.iloc[r]["include"]) in ("1", "True", "true")]
    changes = {}
    with m.edit_group():
        changes["subject"] = m.bulk_set(included, "id", SUBJECT)
    H.pump(settle=20)
    with m.edit_group():
        changes["session"] = m.bulk_set(included, "ses", SESSION)
    H.pump(settle=20)
    # The water reference of the spectroscopy: a reference, not a second run.
    df = m.dataframe()
    for r in rows:
        if "type-ref" in str(df.iloc[r]["sequence"]):
            m.set_datatype_suffix(r, "mrs", "mrsref")
            m.set_entity(r, "run", "")
        elif str(df.iloc[r]["datatype"]) == "mrs":
            m.set_entity(r, "run", "")
    H.pump(settle=30)
    conv._on_revalidate_clicked()
    H.pump(settle=30)
    return changes


def describe(win) -> None:
    """Dataset metadata: the description, the PET dose sheet, the participants file."""
    from bidsmgr.gui.recording_meta_dialog import RecordingMetaDialog
    from bidsmgr.gui.widgets import template_form
    from bidsmgr.metadata.template_plan import blood_conditions, example_paths_for, pair_counts, present_pairs
    from bidsmgr.recording_meta import scaffold_sidecar_path

    conv = win.converter
    df = conv._model.dataframe()
    dlg = RecordingMetaDialog(
        scaffold_sidecar_path(conv._output_tsv), conv._present_datatypes(), conv,
        montage_suggestions=conv._montage_suggestions(), scan_suggestions=conv._scan_suggestions(),
        present_pairs=present_pairs(df), example_paths=example_paths_for(df), pair_counts=pair_counts(df),
        also_ask={("pet", "blood"): blood_conditions(df)}, bids_root=conv._bids_root,
        eyetrack="modality" in df.columns and bool((df["modality"].astype(str) == "eyetrack").any()))
    dlg.show()
    H.pump(settle=30)
    w = dlg._template.widgets_for("dataset_description")
    for field, value in DESCRIPTION.items():
        if field in w:
            template_form.write_field_widget(w[field], value)
    dlg._import_pet_dose(SAMPLE / "dose_sheet.csv")
    dlg._participants_file.setText(str(SAMPLE / "participants.csv"))
    H.pump(settle=20)
    dlg._on_save()
    H.pump(settle=30)
    conv._model.set_global_spec(conv._load_global_spec())
    H.pump(settle=20)


#: What the course enters as the dataset description.
DESCRIPTION = {
    "Authors": ["Example, Ada", "Example, Ben"],
    "License": "CC-BY-4.0",
    "Acknowledgements": "We thank the participant and the imaging unit.",
    "HowToAcknowledge": "Please cite this dataset when you use it.",
}


def convert(win) -> int:
    conv = win.converter
    done = {}
    conv.confirm_sourcedata = lambda _t: True
    conv._show_convert_dialog = lambda rc, parent: done.setdefault("rc", rc)
    conv.start_convert(conv._bids_root.parent)
    H.pump(lambda: "rc" in done, timeout=1800, settle=60)
    return done["rc"]


def measure(win) -> dict:
    """The numbers the pages print, from the state on disk."""
    from bidsmgr.editor.validator import validate

    conv = win.converter
    m = conv.model()
    df = m.dataframe()
    root = H.STUDIES_REAL / PROJECT
    files = [p for p in root.rglob("*") if p.is_file() and ".bidsmgr" not in p.parts]
    rep = validate(root, strict=False)
    counts = dict(rep.counts)
    report = json.loads((root / ".bidsmgr" / "metadata_report.json").read_text())
    todo = report.get("todo_fills") or []
    return {
        "todo": {"inserted": sum(len(t["fields"]) for t in todo), "files": len(todo)},
        "rows": len(df),
        "included": int((df["include"].astype(str).isin(["1", "True", "true"])).sum()),
        "files": len(files),
        "validation": counts,
    }


def build_all(theme: str = "dark") -> None:
    H.app(theme)
    _fresh_sample()
    record = {"source": H.source_info()}
    win = H.main_window("welcome")
    build_project(win)
    H.pump(settle=20)
    scan(win)
    m = win.converter.model()
    df = m.dataframe()
    record["scan"] = {
        "rows": m.rowCount(),
        "included": int(df["include"].astype(str).isin(["1", "True", "true"]).sum()),
        "subjects": sorted(set(df["participant_id"].astype(str)) - {""}),
        "chips": {k: getattr(win.converter, f"_chip_{k}").text() for k in ("valid", "warn", "err", "skip")},
    }
    H.snapshot("scanned")
    record["curate"] = curate(win)
    df = win.converter.model().dataframe()
    record["curated"] = {
        "names": [str(x) for x in df["bids_name"] if str(x)],
        "chips": {k: getattr(win.converter, f"_chip_{k}").text() for k in ("valid", "warn", "err", "skip")},
    }
    H.snapshot("curated")
    describe(win)
    H.snapshot("described")
    rc = convert(win)
    record["convert"] = {"rc": rc}
    record["converted"] = measure(win)
    H.snapshot("converted")
    MEASURED.parent.mkdir(parents=True, exist_ok=True)
    old = json.loads(MEASURED.read_text()) if MEASURED.exists() else {}
    old.update(record)
    MEASURED.write_text(json.dumps(old, indent=1) + "\n")
    print(json.dumps(record, indent=1))


# ------------------------------------------------- after the conversion (Editor)
def _editor_on(win):
    ed = win.editor
    win._apply_active_view("editor", persist=False)
    H.pump(settle=30)
    return ed


def _validate(ed, root):
    """As Validate dataset does: with Deep checks as the toolbar has them
    (on by default since 1.5.1)."""
    from bidsmgr.editor import validate as run_validate
    schema, max_rows, todos = ed._validation_engine_opts()
    rep = run_validate(Path(root), strict=ed._strict_btn.isChecked(), schema=schema,
                       max_rows=max_rows, flag_todos=todos)
    ed._on_report_ready(rep, Path(root))
    H.pump(settle=30)
    return rep


#: The eye tracker's screen, as chapter 9 describes it: the events file of the
#: resting run in beh/, whose sidecar says how the stimuli were shown. The
#: standard asks for these four fields for gaze recorded on a screen.
SCREEN = {
    "StimulusPresentation": {
        "ScreenDistance": 0.6,
        "ScreenOrigin": ["top", "left"],
        "ScreenResolution": [1920, 1080],
        "ScreenSize": [0.53, 0.3],
    }
}
EYE_EVENTS = "onset\tduration\ttrial_type\n0\t199.6\trest\n"


def fix_errors(win, root) -> None:
    """Chapter 9: the PET sidecar's reconstruction fields, answered in the
    form (filtered back projection has no parameters: "none"), and the eye
    tracker's screen, written as the task's events file in beh/ (files the
    reader writes in a text editor: BIDS Manager cannot know the screen)."""
    import json as _json

    ed = _editor_on(win)
    form = ed._sidecar_form
    ed.select_file_in_tree(Path(root) / "sub-001/ses-01/pet/sub-001_ses-01_pet.json")
    H.pump(settle=40)
    form._apply_view_mode("bids", persist=False)
    H.pump(settle=20)
    for key in ("ReconMethodParameterLabels", "ReconMethodParameterUnits"):
        _set_field(form, key, ["none"])
    form.save()
    H.pump(settle=30)
    data = _json.loads((Path(root) / "sub-001/ses-01/pet/sub-001_ses-01_pet.json").read_text())
    if data.get("ReconMethodParameterUnits") != ["none"]:
        raise H.ShotFailed(f"PET edit did not land: {data.get('ReconMethodParameterUnits')!r}")
    beh = H.STUDIES_REAL / Path(root).name / "sub-001/ses-01/beh"
    (beh / "sub-001_ses-01_task-rest_events.tsv").write_text(EYE_EVENTS)
    (beh / "sub-001_ses-01_task-rest_events.json").write_text(_json.dumps(SCREEN, indent=4) + "\n")
    H.pump(settle=40)


def _set_field(form, key: str, value) -> None:
    """Type a value into the form's control for ``key`` and commit it, as
    leaving the field does."""
    from bidsmgr.gui.widgets.template_form import write_field_widget
    for row in form._rows:
        rk = row.key() if callable(row.key) else row.key
        if rk == key:
            w = row.editor() if callable(row.editor) else row.editor
            if getattr(row, "_schema_field", None) is not None:
                write_field_widget(w, value)
                row._on_schema_committed()
            else:
                w.setText(value if isinstance(value, str) else str(value))
                row._on_line_committed()
            H.pump(settle=10)
            return
    raise H.ShotFailed(f"no field {key}")


#: What chapter 10 types into the BOLD run's sidecar.
TASK = {
    "TaskDescription": "Resting state with the eyes open, looking at a fixation cross.",
    "Instructions": "Keep your eyes on the cross and let your mind wander.",
}


def edit_metadata(win, root) -> None:
    """Chapter 10: a task description in the BOLD sidecar."""
    ed = _editor_on(win)
    form = ed._sidecar_form
    ed.select_file_in_tree(Path(root) / "sub-001/ses-01/func/sub-001_ses-01_task-rest_bold.json")
    H.pump(settle=40)
    for k, v in TASK.items():
        _set_field(form, k, v)
    form.save()
    H.pump(settle=30)


def build_after(theme: str = "dark") -> None:
    """The states after the conversion, from `converted`."""
    H.app(theme)
    record = json.loads(MEASURED.read_text())
    root = H.restore("converted")
    win = H.main_window("welcome")
    H.open_project(win, root, "editor")
    fix_errors(win, root)
    rep = _validate(win.editor, root)
    record["fixed"] = {"validation": dict(rep.counts)}
    H.snapshot("fixed")
    edit_metadata(win, root)
    rep = _validate(win.editor, root)
    record["edited"] = {"validation": dict(rep.counts)}
    H.snapshot("edited")
    MEASURED.write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps({k: record[k] for k in ("fixed", "edited")}, indent=1))

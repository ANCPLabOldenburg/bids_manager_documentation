"""The viewer tour (every option, by kind of data) and worked examples.

Image clips are rendered on the native platform so the 3-D view is drawn by
the graphics card; every head is the multimodal sample's (OL_3844, whose
participant consented to the face being shown), and the 3-D view keeps a
corner cut at the crosshair with a camera that swings, never orbits. Signal,
spectrum and dialog figures are plain renders.

Run through ``tools/capture/run.py`` (groups ``t-...`` and ``w-...``).
"""

from __future__ import annotations

import glob
from pathlib import Path

import harness as H
import shots_editor as SE
import shots_viewers as SV
from clip import Clip
from clips_viewers import CONSENTED, Swing, _clip, _planes_3d, _room, _step
from harness import Shot


def _t1(ed, root):
    return SV._open_volume(ed, root, SV.T1)


# ------------------------------------------------------------------ images
def layouts():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _room(ed)
    v = _t1(ed, root)
    _planes_3d(v)
    c = _clip("t-mri-layouts", ed, "The layouts of the image viewer on the T1w, one after the other: one plane, "
              "three planes, a large view with two small ones, a mosaic of slices, the 3-D rendering, and Planes "
              "+ 3-D.", sample=CONSENTED)
    sw = Swing(v, 2.35)
    c.hold(0.6)
    for mode, title in (("single", "One plane"), ("multi", "Three planes"), ("hero", "A large view"),
                        ("mosaic", "Mosaic"), ("3d", "3-D"), ("combo", "Planes + 3-D")):
        c.chapter(title)
        c.do(lambda m=mode: v.run("view.mode", mode=m), settle=0.6)
        v.qstore.flush()
        H.pump(settle=20)
        _step(c, v, orbit=sw if mode in ("3d", "combo") else 0.0, frames=48)
    c.hold(0.6)
    c.poster_at = 9.5
    c.finish()


def effects():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _room(ed)
    v = _t1(ed, root)
    _planes_3d(v)
    c = _clip("t-mri-effects", ed, "The 3-D effects on the T1w in Planes + 3-D, one after the other, with the "
              "corner cut at the crosshair.", sample=CONSENTED)
    sw = Swing(v, 2.35)
    c.hold(0.6)
    for eff in ("Standard", "Matte", "Juicy shiny", "Realistic", "Glass", "X-ray", "MIP", "Edges", "Shell",
                "Topography"):
        c.chapter(eff)
        c.do(lambda e=eff: v.run("render.effect", effect=e), settle=0.4)
        v.qstore.flush()
        _step(c, v, orbit=sw, frames=34)
    c.do(lambda: v.run("render.effect", effect="Standard"), settle=0.3)
    c.hold(0.5)
    c.poster_at = 3.0
    c.finish()


def clipping():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _room(ed)
    v = _t1(ed, root)
    _planes_3d(v, cut=False)
    c = _clip("t-mri-clip", ed, "Clip planes on the T1w: an axial cut through the crosshair moving down, then a "
              "sagittal one, then the corner cut at the crosshair, while the camera swings.", sample=CONSENTED)
    sw = Swing(v, 2.35)
    c.hold(0.6)
    c.chapter("Axial cut through the crosshair")
    c.do(lambda: (v.run("clip.preset", preset="one"), v.run("clip.axis", plane="axial"),
                  v.run("clip.mode", cut_away=False, at_cursor=True)), settle=0.5)
    _step(c, v, orbit=sw, cmd=("cursor.step", {"plane": "axial", "n": -1}), frames=60, every=2)
    c.chapter("Sagittal cut")
    c.do(lambda: (v.run("clip.axis", plane="sagittal"), v.run("clip.invert", index=0)), settle=0.5)
    _step(c, v, orbit=sw, cmd=("cursor.step", {"plane": "sagittal", "n": -1}), frames=50, every=2)
    c.chapter("Corner cut at the crosshair")
    c.do(lambda: (v.run("clip.preset", preset="corner"), v.run("clip.mode", cut_away=True, at_cursor=True),
                  v.run("clip.invert", index=0), v.run("clip.invert", index=2)), settle=0.5)
    _step(c, v, orbit=sw, frames=60)
    c.hold(0.6)
    c.poster_at = 2.0
    c.finish()


def overlay():
    """Skull-strip the T1w with the atlas engine (no download), then lay the
    brain over the image as an overlay."""
    import subprocess
    import sys as _sys
    root = H.restore("edited")
    subprocess.run([_sys.executable, "-m", "bidsmgr.cli.deface", str(H.STUDIES_REAL / "multimodal_study"),
                    "--engine", "strip-atlas", "--target",
                    str(H.STUDIES_REAL / "multimodal_study" / SV.T1), "-q"], check=True)
    brain = sorted(glob.glob(str(Path(root) / "derivatives" / "bidsmgr-skullstrip" / "**" / "*_T1w.nii.gz"),
                             recursive=True))
    if not brain:
        raise H.ShotFailed("skull stripping wrote no brain image")
    win = H.main_window("welcome", SE.SIZE)
    if H.NATIVE:
        from PyQt6.QtCore import Qt
        win.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    H.open_project(win, root, "editor")
    ed = win.editor
    SE._expand(ed, 3)
    _room(ed)
    v = _t1(ed, root)
    _planes_3d(v)
    v.add_overlay(Path(brain[0]))
    H.pump(lambda: len(v.scene.layers) > 1, timeout=180, settle=60)
    lay = v.scene.layers[-1].id
    v.run("layer.set", layer=lay, colormap="warm", opacity=0.55)
    v.qstore.flush()
    v.presenter.set_inspector(True, remember=False)
    v.qstore.flush()
    H.wait(1.0)
    H.pump(settle=40)
    c = _clip("t-mri-overlay", ed, "The brain from skull stripping laid over the T1w as an overlay, in a warm "
              "colour map at half opacity, in the planes and the rendering; Advanced controls lists both layers.",
              sample=CONSENTED)
    sw = Swing(v, 2.35)
    c.hold(0.8)
    for op in (0.25, 0.55, 0.85, 0.55):
        c.do(lambda o=op: v.run("layer.set", layer=lay, opacity=o), settle=0.3)
        _step(c, v, orbit=sw, frames=30)
    c.hold(0.6)
    c.poster_at = 1.0
    c.finish()
    v.presenter.set_inspector(False, remember=False)


def mosaic_and_header():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    SV._viewer_room(ed)
    v = _t1(ed, root)
    v.run("view.mode", mode="mosaic")
    v.qstore.flush()
    H.wait(1.0)
    H.pump(settle=40)
    H.take(Shot("t-mri-mosaic", "The T1w as a mosaic of axial slices.", win, crop_to=ed._center_frame,
                anatomy_ok=True, sample=CONSENTED))
    v.run("view.mode", mode="multi")
    v.qstore.flush()
    H.pump(settle=20)
    v.trigger("header.show")
    H.pump(settle=40)
    H.wait(1.0)
    H.pump(settle=30)
    H.take(Shot("t-mri-header", "The header inspector: the NIfTI header beside the sidecar, field against field.",
                win, crop_to=ed._center_frame, anatomy_ok=True, sample=CONSENTED,
                allow_elided=("QTreeWidget", "QTableView", "QTableWidget")))


# --------------------------------------------------------------- spectrum
def spectrum():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    SV._viewer_room(ed)
    v = ed._spectrum_viewer
    ed.select_file_in_tree(Path(root) / SV.MRS)
    H.pump(lambda: v.page() == "content", timeout=60, settle=40)
    H.wait(1.0)
    c = Clip("t-mrs", ed.window(), crop_to=ed._center_frame, alt="The spectroscopy file in the spectrum viewer: "
             "the zero-order phase turned by hand and set back with Auto phase, line broadening raised, and the FID.", sample="multimodal v2")
    c.show_cursor = False
    c.hold(0.8)
    c.chapter("Phase")
    for ph in range(0, 91, 6):
        c.do(lambda p=ph: v.run("spectrum.set", phase0=float(p)), settle=0.02)
        c.refresh(); c.frame()
    c.do(lambda: v.run("spectrum.auto_phase"), settle=0.6)
    c.hold(0.8)
    c.chapter("Line broadening")
    for lb in (0, 2, 4, 6, 8):
        c.do(lambda x=lb: v.run("spectrum.set", lb_hz=float(x)), settle=0.25)
        c.hold(0.25)
    c.do(lambda: v.run("spectrum.set", lb_hz=0.0), settle=0.3)
    c.chapter("FID")
    c.do(lambda: v.run("spectrum.set", domain="fid"), settle=0.6)
    c.hold(1.4)
    c.do(lambda: v.run("spectrum.set", domain="spectrum"), settle=0.4)
    c.hold(0.5)
    c.poster_at = 0.5
    c.finish()


# ----------------------------------------------------------------- signals
def _signal(ed, root, rel, n=16, ch_type=None):
    v = ed._signal_viewer
    ed.select_file_in_tree(Path(root) / rel)
    H.pump(lambda: v.page() == "content", timeout=60, settle=30)
    p = v.presenter
    p.load_signal()
    H.pump(lambda: p.pages.currentWidget() is p.traces_page, timeout=180, settle=40)
    if ch_type:
        v.run("traces.type", ch_type=ch_type)
    v.run("traces.count", n=n)
    v.qstore.flush()
    H.wait(0.8)
    H.pump(settle=30)
    return v


def eeg_filters():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    SV._viewer_room(ed)
    v = _signal(ed, root, SV.EEG, n=16)
    c = Clip("t-eeg-filters", ed.window(), crop_to=ed._center_frame, alt="The motor-imagery EEG: unfiltered, then "
             "1 to 40 Hz, then 8 to 13 Hz (the alpha band), with the task's events drawn over the traces, and a "
             "page forward in time.", sample="multimodal v2 (PhysioNet EEG, ODC-By 1.0)")
    c.show_cursor = False
    c.hold(1.0)
    c.chapter("No filter")
    c.do(lambda: v.run("traces.reset_filters"), settle=0.6)
    c.hold(1.2)
    c.chapter("1 to 40 Hz")
    c.do(lambda: v.run("traces.filter", hp=1.0, lp=40.0), settle=0.8)
    c.hold(1.2)
    c.chapter("8 to 13 Hz")
    c.do(lambda: v.run("traces.filter", hp=8.0, lp=13.0), settle=0.8)
    c.hold(1.2)
    c.chapter("Events")
    c.do(lambda: (v.run("traces.filter", hp=1.0, lp=40.0), v.run("events.show", value=True)), settle=0.8)
    c.hold(1.2)
    c.chapter("Next page")
    c.do(lambda: v.run("time.page", n=1), settle=0.6)
    c.hold(1.2)
    c.poster_at = 4.0
    c.finish()


def eeg_annotate():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    SV._viewer_room(ed)
    v = _signal(ed, root, SV.EEG, n=16)
    v.run("traces.filter", hp=1.0, lp=40.0)
    v.qstore.flush()
    src = v.store.sources[list(v.store.sources)[0]]
    names = list(getattr(src, "ch_names", []))
    c = Clip("t-eeg-annotate", ed.window(), crop_to=ed._center_frame, alt="Annotate on the EEG: a channel "
             "clicked bad, and a stretch of time marked as a bad segment, ready for Save to dataset.",
             sample="multimodal v2 (PhysioNet EEG, ODC-By 1.0)")
    c.show_cursor = False
    c.hold(1.0)
    c.chapter("Annotate")
    c.do(lambda: v.run("annotate.mode", value=True), settle=0.6)
    c.hold(0.8)
    if len(names) > 3:
        c.chapter("A bad channel")
        c.do(lambda: v.run("channels.toggle_bad", name=names[3]), settle=0.6)
        c.hold(1.2)
    c.chapter("A bad segment")
    t0 = float(v.scene.traces.t0)
    c.do(lambda: v.run("annotate.add", onset=t0 + 2.0, duration=1.5), settle=0.6)
    c.hold(1.6)
    c.poster_at = 3.5
    c.finish()


def signal_stills():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    SV._viewer_room(ed)
    v = _signal(ed, root, SV.MEG, n=40, ch_type="mag")
    v.run("traces.filter", hp=1.0, lp=40.0)
    v.run("traces.option", field="butterfly", value=True)
    v.qstore.flush()
    H.wait(1.0)
    H.pump(settle=30)
    H.take(Shot("t-meg-butterfly", "The MEG magnetometers in butterfly mode: every channel drawn on one axis.",
                win, crop_to=ed._center_frame))
    v.run("traces.option", field="butterfly", value=False)
    v.qstore.flush()
    v = _signal(ed, root, SV.EEG, n=16)
    v.trigger("traces.psd")
    from PyQt6.QtWidgets import QApplication, QDialog
    H.pump(lambda: any(isinstance(w, QDialog) and w.isVisible() for w in QApplication.topLevelWidgets()),
           timeout=120, settle=60)
    H.wait(1.5)
    H.pump(settle=40)
    d = [w for w in QApplication.topLevelWidgets() if isinstance(w, QDialog) and w.isVisible()][-1]
    d.resize(1280, 760)
    H.pump(settle=40)
    H.take(Shot("t-eeg-psd", "The power spectrum of the EEG recording: each channel's spectrum, with a "
                "crosshair that reads out frequency and power.", d))
    SE._close(d)


# --------------------------------------------------------- worked examples
def examples_converter():
    """Bulk edit taking the acquisition label off every row that has one."""
    root = H.restore("described")
    win = H.main_window("welcome", (1600, 1000))
    H.open_project(win, root, "converter")
    conv = win.converter
    H.pump(settle=40)
    m = conv._model
    df = m.dataframe()
    rows = [r for r in range(len(df)) if str(df.iloc[r]["include"]) in ("1", "True", "true")
            and str(df.iloc[r].get("datatype", "")) in ("anat", "func", "dwi", "fmap")]
    conv.select_rows(rows)
    H.pump(settle=20)
    from bidsmgr.gui.bulk_edit_dialog import BulkEditDialog
    d = BulkEditDialog(m, rows, parent=conv)
    d.resize(680, 700)
    d.show()
    H.pump(settle=40)
    at = d._col_combo.findData("acq") if d._col_combo.findData("acq") >= 0 else d._col_combo.findText("acquisition")
    if at < 0:
        for i in range(d._col_combo.count()):
            if "acq" in (d._col_combo.itemText(i) or "").lower():
                at = i
                break
    d._col_combo.setCurrentIndex(at)
    H.pump(settle=20)
    d._remove_check.setChecked(True)
    d._replan()
    H.pump(settle=40)
    H.take(Shot("w-bulk-remove", "Bulk edit on the MRI rows: Remove this entity from the rows that have it, for "
                "the acquisition label. The list shows each name now and after; rows without the label are "
                "left alone.", d, allow_elided=("QTreeWidget",)))
    d.close()
    win.close()


def examples_editor():
    win, ed, root, _ = SE._editor("edited")
    from bidsmgr.gui.replace_value_dialog import ReplaceValueDialog
    d = SE._show(ReplaceValueDialog(root, entity="acq", parent=ed), (980, 700))
    H.pump(settle=30)
    for i in range(d._old.count()):
        if d._old.itemText(i).startswith("tfl3p2"):
            d._old.setCurrentIndex(i)
            break
    else:
        raise H.ShotFailed("no acq-tfl3p2 value offered")
    d._new.setText("mprage")
    d._replan()
    H.pump(settle=60)
    H.wait(0.6)
    H.pump(settle=30)
    H.take(Shot("w-find-replace", "Find and replace an entity value: every acq-tfl3p2 in the dataset becomes "
                "acq-mprage, files and references together.", d, allow_elided=("QTreeWidget", "MovePreviewTree")))
    SE._close(d)
    from bidsmgr.gui.pad_values_dialog import PadValuesDialog
    # The advanced MRI sample has runs to pad; the dialog only previews here.
    adv = H.STUDIES_REAL / "mri_advanced_study"
    d = SE._show(PadValuesDialog(adv, ed), (900, 640))
    for sp in list(d._widths.values())[:1]:
        sp.setValue(2)
    d._replan()
    H.pump(settle=60)
    H.take(Shot("w-index-widths", "Index widths on the advanced MRI sample: every run written with two digits "
                "(run-1 becomes run-01), files and references together.", d, allow_elided=("QTreeWidget", "QTableWidget"),
                sample="MRI sample (Oldenburg 1)"))
    SE._close(d)
    from bidsmgr.gui.edit_entities_dialog import EditEntitiesDialog
    d = SE._show(EditEntitiesDialog(root, [Path(root) / SV.SUB / "func"], ed, entity="acq"), (980, 760))
    d._value.setCurrentText("mb8")
    d.plan_now()
    H.pump(settle=60)
    H.wait(0.6)
    H.pump(settle=30)
    H.take(Shot("w-add-entity", "Add or remove an entity: acq-mb8 added to the functional runs, their "
                "sidecars and physiological recordings moving with them.", d,
                allow_elided=("QTreeWidget", "MovePreviewTree")))
    SE._close(d)


GROUPS = {
    "t-mri-layouts": layouts, "t-mri-effects": effects, "t-mri-clip": clipping, "t-mri-overlay": overlay,
    "t-mri-mosaic": mosaic_and_header, "t-mrs": spectrum, "t-eeg-filters": eeg_filters,
    "t-eeg-annotate": eeg_annotate, "t-signal-stills": signal_stills,
    "w-converter": examples_converter, "w-editor": examples_editor,
}
NATIVE = {"t-mri-layouts", "t-mri-effects", "t-mri-clip", "t-mri-overlay", "t-mri-mosaic"}

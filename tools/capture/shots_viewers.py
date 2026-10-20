"""The viewers in the Editor: images, the time course, signals, spectra, quality.

Every image of an anatomy here is the multimodal sample's, whose participant
(OL_3844) consented to the face being shown. The 3-D group runs on the native
platform (a real OpenGL context) with its window never shown on screen.
"""

from __future__ import annotations

from pathlib import Path

import harness as H
import shots_editor as SE
from harness import Region, Shot

SUB = "sub-001/ses-01"
T1 = f"{SUB}/anat/sub-001_ses-01_acq-tfl3p2_T1w.nii.gz"
FLAIR = f"{SUB}/anat/sub-001_ses-01_acq-spcir2p3_FLAIR.nii.gz"
BOLD = f"{SUB}/func/sub-001_ses-01_task-rest_bold.nii.gz"
DWI_BVAL = f"{SUB}/dwi/sub-001_ses-01_acq-epb0p2_dir-AP_dwi.bval"
PHYSIO = f"{SUB}/func/sub-001_ses-01_task-rest_recording-respiratory_physio.tsv.gz"
EEG = f"{SUB}/eeg/sub-001_ses-01_task-motorimagery_eeg.edf"
MEG = f"{SUB}/meg/sub-001_ses-01_task-rest_meg.fif"
MRS = f"{SUB}/mrs/sub-001_ses-01_svs.nii.gz"
PET = f"{SUB}/pet/sub-001_ses-01_pet.nii.gz"


def _open_volume(ed, root, rel):
    ed.select_file_in_tree(Path(root) / rel)
    v = ed._nifti_viewer
    H.pump(lambda: v.page() == "content" and v.is_loaded(), timeout=180, settle=40)
    v.presenter.set_inspector(False, remember=False)
    v.qstore.flush()
    H.wait(0.6)
    H.pump(settle=30)
    return v


def _viewer_room(ed):
    SE._splitter_sizes(ed, [250, 1290, 40])
    ed._validation_frame.set_collapsed(True)
    H.pump(settle=30)


def images():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _viewer_room(ed)
    v = _open_volume(ed, root, T1)
    v.run("view.mode", mode="multi")
    v.qstore.flush()
    H.wait(0.5)
    H.take(Shot("l12-t1", "The T1w image in the Editor's viewer: sagittal, coronal and axial planes sharing "
                "one crosshair, with the slice and volume controls above.", win, crop_to=ed._center_frame,
                anatomy_ok=True, sample="multimodal v2 (OL_3844, consented)",
                regions=[Region("layout", "Layout", v.button("view.layout") or v, anchor="c")]
                if v.button("view.layout") else []))
    v.presenter.set_inspector(True, remember=False)
    v.qstore.flush()
    H.wait(0.5)
    H.pump(settle=30)
    H.take(Shot("l12-t1-controls", "The same image with Advanced controls open: the layers, their colour map, "
                "window and opacity, and the slice views.", win, crop_to=ed._center_frame, anatomy_ok=True,
                sample="multimodal v2 (OL_3844, consented)"))
    v.presenter.set_inspector(False, remember=False)
    v.qstore.flush()
    # BOLD with its time course.
    v = _open_volume(ed, root, BOLD)
    v.run("view.mode", mode="multi")
    v.run("view.graph", value=True)
    v.run("graph.set", scaling="percent", x_axis="seconds", physio=True, qc=False, scope=1)
    v.qstore.flush()
    g = v.presenter.graph
    H.pump(lambda: g._physio_src is not None, timeout=60, settle=30)
    H.wait(0.8)
    H.take(Shot("l12-bold", "The BOLD run with its time course under the planes: the signal at the crosshair "
                "in per cent of its mean, against time in seconds, with the run's physiological recordings.",
                win, crop_to=ed._center_frame))
    # PET.
    v = _open_volume(ed, root, PET)
    v.run("view.mode", mode="multi")
    v.run("layer.set", colormap="hot")
    v.qstore.flush()
    H.wait(0.6)
    H.take(Shot("l12-pet", "The PET phantom in the viewer, in the hot colour map.", win, crop_to=ed._center_frame))
    v.run("layer.set", colormap="gray")
    v.qstore.flush()


def gradients():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _viewer_room(ed)
    ed.select_file_in_tree(Path(root) / DWI_BVAL)
    H.pump(settle=40)
    H.wait(0.8)
    H.pump(settle=30)
    H.take(Shot("l12-gradients", "The diffusion run's gradient table: the directions on a hemisphere, the "
                "b-value of each volume, and the table of volumes.", win, crop_to=ed._center_frame))


def signals():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _viewer_room(ed)
    v = ed._signal_viewer
    ed.select_file_in_tree(Path(root) / EEG)
    H.pump(lambda: v.page() == "content", timeout=60, settle=30)
    p = v.presenter
    if hasattr(p, "load_signal"):
        p.load_signal()
        H.pump(lambda: p.pages.currentWidget() is p.traces_page, timeout=120, settle=40)
    v.run("traces.count", n=16)
    v.run("events.show", value=True)
    v.run("traces.filter", hp=1.0, lp=40.0)
    v.qstore.flush()
    H.wait(1.0)
    H.pump(settle=30)
    H.take(Shot("l12-eeg", "The motor-imagery EEG in the signal viewer: 16 channels filtered from 1 to 40 Hz, "
                "with the task's events drawn over the traces.", win, crop_to=ed._center_frame))
    # MEG.
    ed.select_file_in_tree(Path(root) / MEG)
    H.pump(lambda: v.page() == "content", timeout=60, settle=30)
    p = v.presenter
    if hasattr(p, "load_signal"):
        p.load_signal()
        H.pump(lambda: p.pages.currentWidget() is p.traces_page, timeout=180, settle=40)
    v.run("traces.type", ch_type="mag")
    v.run("traces.count", n=20)
    v.qstore.flush()
    H.wait(1.0)
    H.pump(settle=30)
    H.take(Shot("l12-meg", "The resting MEG recording, its magnetometers.", win, crop_to=ed._center_frame))


def physio():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _viewer_room(ed)
    ed.select_file_in_tree(Path(root) / PHYSIO)
    tv = ed._tsv_viewer
    H.pump(lambda: getattr(tv, "_loader", None) is None, timeout=30, settle=30)
    btn = H.button(tv, "Visualize")
    btn.click()
    H.pump(settle=40)
    H.wait(2.0)
    H.pump(settle=40)
    H.take(Shot("l12-physio", "The respiratory recording of the BOLD run, opened with Visualize in the table "
                "viewer.", win, crop_to=ed._center_frame))


def spectrum():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _viewer_room(ed)
    v = ed._spectrum_viewer
    ed.select_file_in_tree(Path(root) / MRS)
    H.pump(lambda: v.page() == "content", timeout=60, settle=40)
    H.wait(1.0)
    H.pump(settle=30)
    H.take(Shot("l12-mrs", "The spectroscopy file as a spectrum, with the chemical shift axis in ppm from "
                "right to left and the metabolites labelled.", win, crop_to=ed._center_frame))


def compare():
    win, ed, root, _ = SE._editor("edited")
    from bidsmgr.gui.compare_dialog import CompareDialog
    d = CompareDialog(Path(root) / T1, Path(root) / FLAIR, root=Path(root), parent=ed)
    SE._show(d, (1300, 760))
    H.wait(3.0)
    H.pump(settle=60)
    H.take(Shot("l12-compare", "Compare images: the T1w and the FLAIR side by side, their crosshairs and "
                "contrast kept together.", d, anatomy_ok=True, sample="multimodal v2 (OL_3844, consented)"))
    SE._close(d)


GROUPS = {
    "l12-images": images,
    "l12-gradients": gradients,
    "l12-signals": signals,
    "l12-physio": physio,
    "l12-mrs": spectrum,
    "l12-compare": compare,
}


# ------------------------------------------------------------- chapter 13
def quality_t1():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _viewer_room(ed)
    v = _open_volume(ed, root, T1)
    v.run("view.mode", mode="multi")
    v.qstore.flush()
    p = v.presenter
    p.check_quality()
    H.pump(lambda: p._quality_result is not None and not v.ctx.jobs.running("quality"), timeout=600, settle=60)
    H.wait(1.5)
    H.pump(settle=40)
    H.take(Shot("l13-qc-panel", "Check image quality on the T1w: the quality panel docked beside the planes, "
                "with its findings, the measures by group and the maps it can lay over the image.",
                win, crop_to=ed._center_frame, anatomy_ok=True, sample="multimodal v2 (OL_3844, consented)"))


def quality_bold():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _viewer_room(ed)
    v = _open_volume(ed, root, BOLD)
    v.run("view.mode", mode="multi")
    v.run("view.graph", value=True)
    rows = ["fd", "dvars", "outliers", "carpet"]
    v.run("graph.set", qc=True, qc_rows=rows, physio=False, scaling="percent", x_axis="seconds")
    v.qstore.flush()
    g = v.presenter.graph
    H.pump(lambda: g._qc_src is not None and set(rows) <= set(g._qc_src.get("rows", {})), timeout=600, settle=40)
    H.wait(1.5)
    H.pump(settle=40)
    H.take(Shot("l13-bold-qc", "The BOLD run's time course with QC plots under it: framewise displacement, "
                "DVARS, outlier voxels and the carpet plot, aligned in time.", win, crop_to=ed._center_frame))


def quality_dataset():
    win, ed, root, _ = SE._editor("edited")
    from bidsmgr.gui.quality_check_dialog import QualityCheckDialog
    d = QualityCheckDialog(root, parent=ed)
    SE._show(d, (1180, 760))
    btn = H.button(d, "Check")
    btn.click()
    H.pump(settle=20)
    stop = H.button(d, "Stop")
    H.pump(lambda: not stop.isEnabled(), timeout=1200, settle=60)
    H.wait(1.0)
    H.pump(settle=40)
    H.take(Shot("l13-qc-dialog", "Tools, Quality check over the whole dataset: each anatomical image with its "
                "findings.", d))
    SE._close(d)


def quality_settings():
    win, ed, root, _ = SE._editor("edited")
    from bidsmgr.gui.app_settings import AppSettings
    from bidsmgr.gui.settings_dialog import SettingsDialog
    d = SettingsDialog(AppSettings.load(), win)
    d.resize(960, 760)
    d.show_page("Quality control")
    SE._show(d)
    H.take(Shot("l13-settings-qc", "Settings, Quality control page: when QC runs, the methods, and the "
                "thresholds of every check.", d))
    d.close()


GROUPS.update({
    "l13-qc-t1": quality_t1,
    "l13-qc-bold": quality_bold,
    "l13-qc-dataset": quality_dataset,
    "l13-qc-settings": quality_settings,
})


# ------------------------------------------------------------------- 3-D
NATIVE = {"l12-3d"}


def three_d():
    """The T1w in 3-D (native GPU), with the front of the head cut away by the
    viewer's own clip plane: nothing of the face is drawn, consented or not."""
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _viewer_room(ed)
    v = _open_volume(ed, root, T1)
    print("  gpu", getattr(v.ctx, "gpu_ok", None))
    v.run("view.mode", mode="combo")
    v.run("render.effect", effect="Standard")
    v.run("clip.preset", preset="none")
    v.run("clip.mode", cut_away=False, at_cursor=False)
    v.run("clip.preset", preset="corner")
    v.run("clip.invert", index=0)
    v.run("clip.invert", index=2)
    v.run("render.camera", az=2.35, el=0.42, dist=1.3)
    v.qstore.flush()
    r = v.presenter.render_canvas
    H.pump(lambda: r.gl_ok() and r.has_volume(), timeout=120, settle=60)
    H.wait(1.5)
    H.pump(settle=40)
    rs = v.scene.render
    active = [c for c in v.scene.clips if c.active]
    if not active:
        raise H.ShotFailed("l12-3d: no clip plane active: refusing to render a head in 3-D")
    H.take(Shot("l12-3d", "The T1w in the Planes + 3-D layout: the three planes beside a rendering of the "
                "head with its back corner cut away at the crosshair.", win, crop_to=ed._center_frame,
                anatomy_ok=True, sample="multimodal v2 (OL_3844, consented)"))


GROUPS.update({"l12-3d": three_d})

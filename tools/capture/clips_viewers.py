"""Clips of the image viewer, always in the Planes + 3-D layout.

Rendered on the native platform, so the 3-D view is drawn by the graphics
card, frame by frame, with the window never shown on the screen. Every head
here is the multimodal sample's (OL_3844), whose participant consented to
the face being shown; the 3-D view still cuts a corner away at the
crosshair, which is what a reader learns to do. The PET image is a phantom.

Run through ``tools/capture/run.py`` (these groups are native).
"""

from __future__ import annotations

from pathlib import Path

import harness as H
import shots_editor as SE
import shots_viewers as SV
from clip import Clip
from harness import Shot

CONSENTED = "multimodal v2 (OL_3844, consented)"


def _room(ed, sizes=(240, 1360, 0)):
    SE._splitter_sizes(ed, list(sizes))
    ed._validation_frame.set_collapsed(True)
    H.pump(settle=30)


def _planes_3d(v, *, az=2.35, el=0.38, dist=1.35, cut=True):
    v.run("view.mode", mode="combo")
    v.run("render.effect", effect="Standard")
    v.run("clip.preset", preset="none")
    if cut:
        v.run("clip.preset", preset="corner")
        v.run("clip.mode", cut_away=True, at_cursor=True)
        v.run("clip.invert", index=0)
        v.run("clip.invert", index=2)
    v.run("render.camera", az=az, el=el, dist=dist)
    v.qstore.flush()
    r = v.presenter.render_canvas
    H.pump(lambda: r.gl_ok() and r.has_volume(), timeout=180, settle=60)
    if not r.gl_ok():
        raise H.ShotFailed("no OpenGL: the 3-D view cannot be drawn here")
    H.wait(1.2)
    H.pump(settle=40)


class Swing:
    """The camera swinging gently about a view, so a cut stays in sight."""

    def __init__(self, v, az: float, amp: float = 0.55, period: float = 7.0, fps: int = 30) -> None:
        self.v, self.az, self.amp, self.n, self.i = v, az, amp, period * fps, 0

    def __call__(self) -> None:
        import math
        self.i += 1
        self.v.run("render.camera", az=self.az + self.amp * math.sin(2 * math.pi * self.i / self.n))


def _step(c: Clip, v, *, orbit=0.0, cmd=None, frames=1, every=1):
    """Advance the picture: move the camera (an angle per frame, or a Swing),
    and every ``every`` frames run ``cmd`` (a viewer command and its arguments)."""
    for i in range(frames):
        if callable(orbit):
            orbit()
        elif orbit:
            v.run("render.orbit", d_az=orbit, d_el=0.0)
        if cmd is not None and i % every == 0:
            v.run(cmd[0], **cmd[1])
        v.qstore.flush()
        H.pump(settle=3)
        c.refresh()
        c.frame()


def _clip(cid, ed, alt, *, sample="multimodal v2"):
    c = Clip(cid, ed.window(), crop_to=ed._center_frame, alt=alt, sample=sample)
    c.show_cursor = False
    return c


def t1():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _room(ed)
    v = SV._open_volume(ed, root, SV.T1)
    _planes_3d(v)
    c = _clip("l12-t1", ed, "The T1w in the Planes + 3-D layout: the three planes and the rendering turn "
              "together as the crosshair moves down through the head, and the corner cut at the crosshair "
              "follows it.", sample=CONSENTED)
    sw = Swing(v, 2.35)
    c.hold(0.8)
    c.chapter("Turn the 3-D view")
    _step(c, v, orbit=sw, frames=60)
    c.chapter("Move the crosshair")
    _step(c, v, orbit=sw, cmd=("cursor.step", {"plane": "axial", "n": -1}), frames=72, every=2)
    _step(c, v, orbit=sw, cmd=("cursor.step", {"plane": "coronal", "n": 1}), frames=60, every=2)
    _step(c, v, orbit=sw, frames=40)
    c.hold(1.0)
    c.poster_at = 2.0
    c.finish()


def t1_controls():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _room(ed)
    v = SV._open_volume(ed, root, SV.T1)
    _planes_3d(v)
    v.presenter.set_inspector(True, remember=False)
    v.qstore.flush()
    H.wait(0.8)
    H.pump(settle=30)
    c = _clip("l12-t1-controls", ed, "The T1w with Advanced controls open beside the Planes + 3-D layout: "
              "changing the colour map and the window changes the planes and the rendering together.",
              sample=CONSENTED)
    sw = Swing(v, 2.35)
    c.hold(1.0)
    for cmap in ("viridis", "plasma", "gray"):
        c.do(lambda m=cmap: v.run("layer.set", colormap=m))
        _step(c, v, orbit=sw, frames=34)
    c.hold(0.8)
    v.presenter.set_inspector(False, remember=False)
    v.qstore.flush()
    c.finish()


def bold():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _room(ed)
    v = SV._open_volume(ed, root, SV.BOLD)
    _planes_3d(v, dist=1.45)
    v.run("view.graph", value=True)
    v.run("graph.set", scaling="percent", x_axis="seconds", physio=True, qc=False, scope=1)
    v.qstore.flush()
    g = v.presenter.graph
    H.pump(lambda: g._physio_src is not None, timeout=120, settle=30)
    H.wait(1.0)
    c = _clip("l12-bold", ed, "The BOLD run in the Planes + 3-D layout with its time course and physiological "
              "recordings beneath: the run plays volume by volume while the rendering turns.", sample=CONSENTED)
    c.hold(0.8)
    c.chapter("Play the run")
    sw = Swing(v, 2.35)
    for f in range(0, 60):
        v.run("frame.set", frame=f)
        _step(c, v, orbit=sw, frames=3)
    c.hold(1.0)
    c.poster_at = 3.0
    c.finish()


def pet():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _room(ed)
    v = SV._open_volume(ed, root, SV.PET)
    v.run("layer.set", colormap="hot")
    _planes_3d(v, cut=True, dist=1.6, el=0.5)
    c = _clip("l12-pet", ed, "The PET phantom in the Planes + 3-D layout, in the hot colour map, with a corner "
              "of the cylinder cut away at the crosshair.", sample="multimodal v2 (PET phantom)")
    sw = Swing(v, 2.35)
    c.hold(0.8)
    _step(c, v, orbit=sw, frames=60)
    _step(c, v, orbit=sw, cmd=("cursor.step", {"plane": "axial", "n": 1}), frames=48, every=2)
    c.hold(0.8)
    c.poster_at = 1.5
    c.finish()
    v.run("layer.set", colormap="gray")
    v.qstore.flush()


def qc_t1():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _room(ed)
    v = SV._open_volume(ed, root, SV.T1)
    _planes_3d(v)
    p = v.presenter
    p.check_quality()
    H.pump(lambda: p._quality_result is not None and not v.ctx.jobs.running("quality"), timeout=900, settle=60)
    H.wait(1.5)
    H.pump(settle=40)
    panel = p._quality_panel
    c = _clip("l13-qc-panel", ed, "The quality check of the T1w docked beside the Planes + 3-D layout: ticking "
              "the grey matter, the white matter and the face region lays each over the planes and the rendering.",
              sample=CONSENTED)
    sw = Swing(v, 2.35)
    c.hold(1.2)
    want = ("Grey matter", "White matter", "Face region")
    keys = [k for k, b in panel.map_boxes.items() if b.text() in want] or list(panel.map_boxes)[:3]
    for k in keys:
        c.do(lambda kk=k: panel.map_boxes[kk].setChecked(True))
        _step(c, v, orbit=sw, frames=40)
        c.do(lambda kk=k: panel.map_boxes[kk].setChecked(False))
    _step(c, v, orbit=sw, frames=20)
    c.hold(0.8)
    c.poster_at = 1.0
    c.finish()


def qc_bold():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    _room(ed)
    v = SV._open_volume(ed, root, SV.BOLD)
    _planes_3d(v, dist=1.45)
    v.run("view.graph", value=True)
    rows = ["fd", "dvars", "outliers", "carpet"]
    v.run("graph.set", qc=True, qc_rows=rows, physio=False, scaling="percent", x_axis="seconds")
    v.qstore.flush()
    g = v.presenter.graph
    H.pump(lambda: g._qc_src is not None and set(rows) <= set(g._qc_src.get("rows", {})), timeout=900, settle=40)
    H.wait(1.5)
    c = _clip("l13-bold-qc", ed, "The BOLD run in the Planes + 3-D layout with its QC plots under the time "
              "course: framewise displacement, DVARS, outlier voxels and the carpet plot, following the run as "
              "it plays.", sample=CONSENTED)
    sw = Swing(v, 2.35)
    c.hold(0.8)
    for f in range(0, 60, 2):
        v.run("frame.set", frame=f)
        _step(c, v, orbit=sw, frames=4)
    c.hold(1.0)
    c.poster_at = 2.5
    c.finish()


def compare():
    win, ed, root, _ = SE._editor("edited")
    from bidsmgr.gui.compare_dialog import CompareDialog
    d = CompareDialog(Path(root) / SV.T1, Path(root) / SV.FLAIR, root=Path(root), parent=ed)
    if H.NATIVE:
        from PyQt6.QtCore import Qt
        d.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    SE._show(d, (1400, 820))
    H.wait(3.0)
    H.pump(settle=60)
    viewers = [w for w in d.findChildren(type(ed._nifti_viewer))]
    for v in viewers:
        try:
            _planes_3d(v, dist=1.5)
        except H.ShotFailed:
            raise
    c = Clip("l12-compare", d, popups=False, alt="Compare images: the T1w and the FLAIR side by side, each in the Planes + 3-D "
             "layout, turning and moving together.", sample=CONSENTED)
    c.show_cursor = False
    c.hold(0.8)
    for i in range(90):
        for v in viewers:
            v.run("render.orbit", d_az=0.016, d_el=0.0)
            if i % 3 == 0 and 20 < i < 80:
                v.run("cursor.step", plane="axial", n=-1)
            v.qstore.flush()
        H.pump(settle=3)
        c.refresh()
        c.frame()
    c.hold(0.8)
    c.finish()
    SE._close(d)


def deface_compare():
    """Deface the T1w with the command line, then compare before and after."""
    import subprocess
    import sys as _sys
    root = H.restore("edited")
    t1 = SV.T1
    subprocess.run([_sys.executable, "-m", "bidsmgr.cli.deface", str(H.STUDIES_REAL / "multimodal_study"),
                    "--target", str(H.STUDIES_REAL / "multimodal_study" / t1), "-q"], check=True)
    win = H.main_window("welcome", SE.SIZE)
    if H.NATIVE:
        from PyQt6.QtCore import Qt
        win.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    H.open_project(win, root, "editor")
    ed = win.editor
    from bidsmgr.gui.deface_compare import DefaceCompareDialog
    d = DefaceCompareDialog(root, t1, ed)
    if H.NATIVE:
        from PyQt6.QtCore import Qt
        d.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    SE._show(d, (1400, 820))
    H.wait(3.0)
    H.pump(settle=60)
    viewers = [w for w in d.findChildren(type(ed._nifti_viewer))]
    print("  viewers in the comparison:", len(viewers))
    for v in viewers:
        _planes_3d(v, cut=False, az=-0.9, el=0.12, dist=1.6)
    c = Clip("l14-deface-compare", d, popups=False, alt="The T1w before and after defacing, in the Planes + 3-D layout, "
             "turning: the face is gone from the defaced image, the brain is not.", sample=CONSENTED)
    c.show_cursor = False
    c.hold(1.0)
    for i in range(110):
        for v in viewers:
            v.run("render.orbit", d_az=0.016, d_el=0.0)
            v.qstore.flush()
        H.pump(settle=3)
        c.refresh()
        c.frame()
    c.hold(0.8)
    c.finish()
    SE._close(d)


def home_editor():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    SE._splitter_sizes(ed, [230, 920, 450])
    v = SV._open_volume(ed, root, SV.BOLD)
    _planes_3d(v, dist=1.45)
    v.run("view.graph", value=True)
    v.run("graph.set", scaling="percent", x_axis="seconds", physio=True, qc=False, scope=1)
    v.qstore.flush()
    g = v.presenter.graph
    H.pump(lambda: g._physio_src is not None, timeout=120, settle=30)
    H.wait(1.0)
    H.take(Shot("home-editor", "The Editor on the converted sample: the BIDS tree with its validation marks, "
                "the BOLD run in the Planes + 3-D layout with its time course and physiological recordings, and "
                "the Validation panel.", win, window=True, anatomy_ok=True, sample=CONSENTED,
                allow_elided=("QTreeView", "QTreeWidget", "QTableView")))
    win.close()


GROUPS = {
    "v-l12-t1": t1, "v-l12-t1-controls": t1_controls, "v-l12-bold": bold, "v-l12-pet": pet,
    "v-l13-qc-panel": qc_t1, "v-l13-bold-qc": qc_bold, "v-l12-compare": compare,
    "v-l14-deface-compare": deface_compare, "v-home-editor": home_editor,
}
NATIVE = set(GROUPS)

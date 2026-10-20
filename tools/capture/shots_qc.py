"""The quality-control guide: a BOLD run with real head motion, and an MEG
recording whose QC flags more or less as its thresholds change.

Data (prepared by hand, see the 1.5.1 docs plan):

- ``/tmp/studies/motion_study``: one BOLD run of an Oldenburg study (Siemens
  Prisma, multiband 4, 48 slices, TR 0.85 s, 1,224 volumes) with clear
  motion spikes. Only EPI is shown: no face.
- ``/tmp/studies/mous_meg``: the resting MEG of MOUS participant A2004
  (Donders Institute, CTF 275, 1200 Hz, 328 s), the recording linked in
  place, never copied into the site.
"""

from __future__ import annotations

from pathlib import Path

import harness as H
import shots_editor as SE
import shots_viewers as SV
from clip import Clip
from harness import Shot

MOTION = "motion_study"
BOLD = "sub-002/func/sub-002_task-dmaging_run-1_bold.nii.gz"
MOTION_SAMPLE = "BOLD run with motion (Oldenburg)"
MOUS = "mous_meg"
MEG = "sub-A2004/meg/sub-A2004_task-rest_meg.ds"
MOUS_SAMPLE = "MOUS sub-A2004 (Donders Institute)"
#: Tall enough for the planes, the time course and four QC plots.
TALL = (1600, 1460)
ROWS = ["fd", "dvars", "spikes", "carpet"]


def _motion_viewer():
    root = H.STUDIES / MOTION
    win = H.main_window("welcome", TALL)
    H.open_project(win, root, "editor")
    ed = win.editor
    H.pump(settle=40)
    SE._expand(ed, 3)
    SV._viewer_room(ed)
    v = SV._open_volume(ed, root, BOLD)
    v.run("view.mode", mode="multi")
    v.run("view.graph", value=True)
    v.run("graph.set", qc=True, qc_rows=ROWS, physio=False, scaling="percent", x_axis="frames",
          tracks_mode="fit")
    v.qstore.flush()
    g = v.presenter.graph
    H.pump(lambda: g._qc_src is not None and set(ROWS) <= set(g._qc_src.get("rows", {})),
           timeout=1200, settle=40)
    H.wait(1.5)
    H.pump(settle=40)
    return win, ed, v, g


def _frame(v, f: int) -> None:
    v.run("frame.set", frame=f)
    v.qstore.flush()
    H.pump(settle=20)
    H.wait(0.3)
    H.pump(settle=20)


def bold_motion():
    win, ed, v, g = _motion_viewer()
    _frame(v, 141)
    H.take(Shot("g-qc-bold-run", "A BOLD run of 1,224 volumes with head motion, at volume 141: the planes show "
                "the slices of that volume out of line with each other, and the plots under the time course "
                "show the same moment as a spike in framewise displacement, DVARS and slice spikes, and a "
                "band in the carpet.", win, crop_to=ed._center_frame, sample=MOTION_SAMPLE))
    g.set_time_view((100.0, 200.0))
    H.pump(settle=30)
    _frame(v, 138)
    H.take(Shot("g-qc-bold-138", "Zoomed to volumes 100 to 200, at volume 138, three volumes before the "
                "movement: the planes are clean and every plot is at its baseline.", win,
                crop_to=ed._center_frame, sample=MOTION_SAMPLE))
    _frame(v, 141)
    H.take(Shot("g-qc-bold-141", "Volume 141: the head moved while the volume was being acquired, so the slices "
                "taken after the movement no longer line up with those taken before, a comb of stripes in the "
                "sagittal and coronal planes.", win, crop_to=ed._center_frame, sample=MOTION_SAMPLE))


def bold_motion_clip():
    win, ed, v, g = _motion_viewer()
    g.set_time_view((110.0, 180.0))
    _frame(v, 128)
    c = Clip("g-qc-bold-scrub", win, crop_to=ed._center_frame, sample=MOTION_SAMPLE,
             alt="Stepping through volumes 128 to 160 of the BOLD run with motion: at volumes 141 and 152 "
                 "the planes break into stripes and every plot under the time course spikes; at 146 and 147 "
                 "framewise displacement is high but the slices stay in line.")
    c.show_cursor = False
    c.hold(1.2)
    c.chapter("Volume by volume")
    for f in range(128, 161):
        _frame(v, f)
        c.refresh()
        c.frame(1.1 if f in (141, 147, 152) else 0.3)
    c.hold(1.0)
    c.chapter("The whole run")
    g.set_time_view(None)
    _frame(v, 394)
    c.refresh()
    c.frame(2.5)
    c.poster_at = 4.0
    c.finish()


# ------------------------------------------------------------------ MEG
#: Wide enough for the traces with the QC plots beside them.
WIDE = (1900, 1240)


def _mous_viewer(size=WIDE):
    root = H.STUDIES / MOUS
    win = H.main_window("welcome", size)
    H.open_project(win, root, "editor")
    ed = win.editor
    H.pump(settle=40)
    SE._expand(ed, 3)
    SV._viewer_room(ed)
    v = ed._signal_viewer
    ed.select_file_in_tree(Path(root) / MEG)
    H.pump(lambda: v.page() == "content", timeout=120, settle=30)
    p = v.presenter
    p.load_signal()
    H.pump(lambda: p.pages.currentWidget() is p.traces_page, timeout=300, settle=40)
    v.run("traces.type", ch_type="mag")
    v.run("traces.count", n=24)
    v.run("traces.filter", hp=1.0, lp=150.0)
    v.run("time.width", seconds=30.0)
    v.run("time.set", t0=258.0)
    # The QC plots to the right of the traces, as the user lays them out.
    v.run("traces.qc_view", beside=True)
    v.qstore.flush()
    H.pump(settle=20)
    return win, ed, v, p


def _qc_settings(v, **changes):
    from bidsmgr.viz.settings import MeegQcSettings
    new = MeegQcSettings(**{**v.ctx.settings.meeg_qc.model_dump(), **changes})
    v.ctx.settings_hub.update(lambda s: setattr(s, "meeg_qc", new))


def _wait_quality(v, p) -> None:
    H.pump(settle=20)
    H.wait(0.4)
    H.pump(lambda: p.quality_result() is not None, timeout=900, settle=40)
    H.wait(1.2)
    H.pump(settle=40)


def _clear_bad_segments(v) -> None:
    from bidsmgr.viz.commands.signal import bad_spans
    while bad_spans(v.ctx.store):
        v.run("annotate.remove", index=0)
    v.qstore.flush()
    H.pump(settle=20)


def _mark_flagged(v, p) -> int:
    """The flagged segments as bad segments: red bands across the traces."""
    n = p.mark_segments()
    v.qstore.flush()
    H.wait(0.6)
    H.pump(settle=40)
    if not n:
        raise H.ShotFailed("QC flagged no segment to mark")
    return n


def meg_thresholds():
    win, ed, v, p = _mous_viewer()
    _qc_settings(v, types=["mag"], segment_factor=4.0, muscle_z=4.0)
    v.trigger("traces.quality")
    _wait_quality(v, p)
    v.run("traces.qc_view", metrics=["off", "muscle", "ptp"], types=["mag"], beside=True)
    v.qstore.flush()
    H.wait(0.8)
    H.pump(settle=40)
    H.take(Shot("g-qc-meg-default", "The resting MEG of one MOUS participant, magnetometers 258 to 288 s, with "
                "the QC plots beside the traces and QC at its defaults: a channel is off in a segment beyond 4 "
                "times its usual level, and a segment is flagged when 20 % of a type are off. At most 11 % are "
                "off at 270 s: nothing is flagged.", win, crop_to=ed._center_frame, sample=MOUS_SAMPLE))
    _qc_settings(v, types=["mag"], segment_factor=2.5)
    p.recheck_quality()
    _wait_quality(v, p)
    _mark_flagged(v, p)
    H.take(Shot("g-qc-meg-2.5", "The same stretch with Channel off in a segment beyond lowered to 2.5: 44 % of "
                "the magnetometers are off at 270 s, the segments from 270 to 274 s are flagged, and Mark "
                "flagged segments bad lays them over the traces in red.", win, crop_to=ed._center_frame,
                sample=MOUS_SAMPLE))
    _clear_bad_segments(v)
    _qc_settings(v, types=["mag"], segment_factor=4.0, muscle_z=3.0)
    p.recheck_quality()
    _wait_quality(v, p)
    _mark_flagged(v, p)
    H.take(Shot("g-qc-meg-muscle", "Back to 4, and Muscle above lowered from 4 to 3: the stretches at 270 and "
                "280 s are flagged as muscle, and marked in red.", win, crop_to=ed._center_frame,
                sample=MOUS_SAMPLE))
    _clear_bad_segments(v)
    _qc_settings(v, types=[], segment_factor=4.0, muscle_z=4.0)


def meg_threshold_clip():
    win, ed, v, p = _mous_viewer()
    _qc_settings(v, types=["mag"], segment_factor=4.0, muscle_z=4.0)
    v.trigger("traces.quality")
    _wait_quality(v, p)
    v.run("traces.qc_view", metrics=["off", "ptp"], types=["mag"], beside=True)
    v.qstore.flush()
    H.wait(0.6)
    H.pump(settle=30)
    controls = p.controls
    c = Clip("g-qc-meg-threshold", win, crop_to=ed._center_frame, sample=MOUS_SAMPLE,
             alt="Lowering one QC threshold on the MOUS recording: Settings... opens the check's parameters, "
                 "Channel off in a segment beyond goes from 4 to 2.5, Check again flags the stretch at 270 s "
                 "that the default let through, and Mark flagged segments bad lays it over the traces in red.")
    c.hold(1.4)
    c.chapter("The parameters")
    btn = H.button(p.traces_page, "Settings...")
    c.click(btn, btn.click, after=0.8)
    box = controls._qc_controls["segment_factor"].widget
    c.click(box, lambda: (box.setFocus(), box.selectAll()), after=0.3)
    edit = box.lineEdit()
    edit.selectAll()
    edit.del_()
    c.refresh()
    c.frame(0.2)
    c.type(edit, "2.5", cps=6)
    box.interpretText()
    c.hold(0.6)
    c.chapter("Check again")
    c.click(controls.qc_apply, controls.qc_apply.click, after=0.2)
    c.wait_until(lambda: p.quality_result() is not None, timeout=600, every=0.4, speed=3.0)
    H.wait(1.0)
    c.hold(1.6)
    c.chapter("Mark them bad")
    mark = controls.qc_mark_segments
    c.click(mark, mark.click, after=0.4)
    H.wait(0.6)
    c.hold(1.0)
    # The traces given their room back, the red bands across them.
    c.do(lambda: p.set_inspector(False, remember=False), settle=0.6)
    c.hold(3.0)
    c.poster_at = c.t - 1.0
    c.finish()
    _clear_bad_segments(v)
    _qc_settings(v, types=[], segment_factor=4.0)


GROUPS = {
    "g-qc-bold": bold_motion,
    "g-qc-bold-clip": bold_motion_clip,
    "g-qc-meg": meg_thresholds,
    "g-qc-meg-clip": meg_threshold_clip,
}

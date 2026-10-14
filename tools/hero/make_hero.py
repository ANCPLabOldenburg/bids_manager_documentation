"""Precompute the home page hero: seven kinds of recording as particles, and
the emblem they pass through on their way into a BIDS dataset.

Every form is drawn from real data that may be shown:

- MRI: the MNI ICBM 2009c template BIDS Manager ships for its quality check,
  as a point cloud of the brain (an average brain: no face, no person);
- MR spectroscopy: the spectrum of the multimodal sample's single-voxel
  acquisition, phased as BIDS Manager's viewer phases it;
- PET: an axial slice of the sample's GE Advance FDG phantom (CC BY 4.0);
- EEG: eight channels of the sample's PhysioNet resting recording (ODC-By 1.0);
- MEG: the sensor helmet of the sample's Elekta Neuromag recording, in 3-D;
- physiology: the ECG, pulse and breathing recorded with the sample's BOLD run;
- eye tracking: the fixations and saccades of the eyelinkio test recording
  (BSD-3).

Each form is stored in its own unit box (x right, y down, z towards the
viewer, all in -1..1), so the page lays the forms out to fit any screen; the
page also computes where every particle lands in the dataset tree, from the
text itself. Writes ``static/hero/hero.bin``: a JSON header, then per particle
x, y as int16, z as int8, kind, seed and value as uint8, in random order (so
any prefix is a fair sample when a slow machine draws fewer). Also writes
``hero-light.svg`` and ``hero-dark.svg``, a still for pages without
JavaScript. Run with the BIDS Manager environment:

    environments/bids-manager/bin/python bids_manager_documentation/tools/hero/make_hero.py
"""

from __future__ import annotations

import gzip
import json
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent
OUT = SITE / "static" / "hero"
RNG = np.random.default_rng(11)

SAMPLE = Path("/private/tmp/bm_docs/work/samples/multimodal/raw/sub-001")
CONVERTED = Path("/private/tmp/bm_docs/states/edited/multimodal_study/sub-001/ses-01")

#: The kinds, in the order the page lays them out around the emblem.
KINDS = [
    {"id": "mri", "name": "MRI", "suffix": "T1w", "folder": "anat/",
     "file": "sub-001_ses-01_acq-tfl3p2_T1w.nii.gz", "n": 7600},
    {"id": "mrs", "name": "MR spectroscopy", "suffix": "svs", "folder": "mrs/",
     "file": "sub-001_ses-01_svs.nii.gz", "n": 2600},
    {"id": "pet", "name": "PET", "suffix": "pet", "folder": "pet/",
     "file": "sub-001_ses-01_pet.nii.gz", "n": 3200},
    {"id": "eeg", "name": "EEG", "suffix": "eeg", "folder": "eeg/",
     "file": "sub-001_ses-01_task-rest_eeg.edf", "n": 4400},
    {"id": "meg", "name": "MEG", "suffix": "meg", "folder": "meg/",
     "file": "sub-001_ses-01_task-rest_meg.fif", "n": 3600},
    {"id": "physio", "name": "Physiology", "suffix": "physio", "folder": "func/",
     "file": "sub-001_ses-01_task-rest_recording-ecg_physio.tsv.gz", "n": 3600},
    {"id": "eye", "name": "Eye tracking", "suffix": "physio", "folder": "beh/",
     "file": "sub-001_ses-01_task-rest_recording-eye1_physio.tsv.gz", "n": 2800},
]
EMBLEM_N = 3200


# ------------------------------------------------------------------ helpers
def unit(pts: np.ndarray, keep_aspect: bool = True) -> np.ndarray:
    """Scale points (n x 2 or n x 3) into -1..1 around their centre."""
    pts = np.asarray(pts, float)
    lo, hi = pts.min(0), pts.max(0)
    c = (lo + hi) / 2
    span = (hi - lo) / 2
    span[span == 0] = 1
    if keep_aspect:
        span[:] = span.max()
    return (pts - c) / span


def sample_image(img: np.ndarray, n: int, gamma: float = 1.0):
    p = np.clip(img.astype(float), 0, None) ** gamma
    p = p.ravel() / p.sum()
    idx = RNG.choice(p.size, size=n, replace=True, p=p)
    ys, xs = np.unravel_index(idx, img.shape)
    pts = np.stack([xs, ys], 1).astype(float) + RNG.random((n, 2))
    return pts, img.ravel()[idx]


def along_curve(x: np.ndarray, y: np.ndarray, n: int):
    """``n`` points evenly along a drawn curve, so peaks are not thinner than flats."""
    arc = np.concatenate([[0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    s = np.sort(RNG.random(n)) * arc[-1]
    return np.interp(s, arc, x), np.interp(s, arc, y), s / arc[-1]


# -------------------------------------------------------------------- forms
def form_mri(n: int):
    """The brain as a cloud: cortex and its outline weighted by intensity."""
    import nibabel as nib
    from bidsmgr.qc import templates as T

    folder = Path(T.__file__).parent
    vol = np.asarray(nib.load(folder / "mni2009c_2mm_T1w.nii.gz").dataobj, float)
    mask = np.asarray(nib.load(folder / "mni2009c_2mm_brain_mask.nii.gz").dataobj) > 0
    vol = vol / np.percentile(vol[mask], 99)
    # Grey matter: the band of intensities below white matter, inside the mask.
    gm = mask & (vol > 0.35) & (vol < 0.72)
    # The surface: mask voxels with a neighbour outside.
    from scipy import ndimage
    surf = mask & ~ndimage.binary_erosion(mask, iterations=1)
    w = np.where(surf, 3.0, 0.0) + np.where(gm, 1.0, 0.0)
    w = w.ravel() / w.sum()
    idx = RNG.choice(w.size, size=n, p=w)
    i, j, k = np.unravel_index(idx, vol.shape)
    pts = np.stack([i, j, k], 1).astype(float) + RNG.random((n, 3))
    # Voxel axes (x left to right, y back to front, z down to up) to the
    # page's unit box: x right, y down, z towards the viewer. Seen from the
    # side, nose to the left.
    xyz = np.stack([-pts[:, 1], -pts[:, 2], pts[:, 0]], 1)
    val = np.clip(vol[i, j, k], 0, 1)
    return unit(xyz), val


def form_mrs(n: int):
    from bidsmgr.viz.compute import mrs as M
    from bidsmgr.viz.data.spectrum import read_mrs

    src = read_mrs(CONVERTED / "mrs" / "sub-001_ses-01_svs.nii.gz", with_reference=False)
    fid = src.select()
    ppm, _hz, spec = M.spectrum(fid, src.dwell, src.spectrometer_mhz, src.nucleus, line_broadening_hz=4.0)
    ph = M.auto_phase0(ppm, spec)
    real = (spec * np.exp(1j * np.deg2rad(ph))).real
    keep = (ppm >= 0.6) & (ppm <= 4.1)
    x, y = ppm[keep], real[keep]
    order = np.argsort(x)
    x, y = x[order], y[order]
    y = y - np.percentile(y, 8)
    y = y / np.percentile(y, 99.7)
    y = np.clip(y, -0.1, 1.15)
    # Spectroscopists draw ppm from right to left.
    X = -x
    xs, ys, _ = along_curve(X * 1.0, -y * 0.9, int(n * 0.86))
    curve = np.stack([xs, ys], 1)
    # Dotted markers at the metabolites BIDS Manager's viewer labels.
    marks = []
    peaks = {"NAA": 2.01, "Cr": 3.03, "Cho": 3.22, "mI": 3.56}
    m = n - len(curve)
    per = m // len(peaks)
    for name, p in peaks.items():
        top = float(np.interp(-p, X, -y * 0.9))
        yy = np.linspace(0.12, top - 0.06, per)
        marks.append(np.stack([np.full(per, -p) + RNG.normal(0, 0.004, per), yy], 1))
    pts = np.concatenate([curve] + marks)
    val = np.concatenate([np.full(len(curve), 0.9), np.full(len(pts) - len(curve), 0.35)])
    pts = unit(pts, keep_aspect=False) * np.array([1.0, 0.62])
    labels = [{"text": k, "x": float(((-v) - (-4.1)) / (4.1 - 0.6) * 2 - 1)} for k, v in peaks.items()]
    return pts, val, labels


def form_pet(n: int):
    import pydicom

    files = sorted((SAMPLE / "pet").glob("*.dcm"))
    slices = []
    for f in files:
        d = pydicom.dcmread(f)
        slices.append((float(d.ImagePositionPatient[2]), d.pixel_array.astype(float)))
    slices.sort(key=lambda s: s[0])
    vol = np.stack([s[1] for s in slices])
    sl = vol[len(vol) // 2]
    sl = np.clip(sl / np.percentile(sl, 99.5), 0, 1)
    pts, val = sample_image(sl, n, gamma=1.6)
    return unit(pts), np.clip(val, 0, 1)


def form_eeg(n: int):
    import mne

    raw = mne.io.read_raw_edf(SAMPLE / "eeg" / "task-rest_eeg.edf", preload=True, verbose=False)
    raw.filter(1.0, 20.0, verbose=False)
    picks = ["Fp1.", "Fz..", "C3..", "Cz..", "C4..", "Pz..", "O1..", "O2.."]
    picks = [p for p in picks if p in raw.ch_names] or raw.ch_names[:8]
    sf = raw.info["sfreq"]
    seg = raw.get_data(picks=picks, start=int(10 * sf), stop=int(16 * sf))
    per = n // len(picks)
    pts, phase = [], []
    for r, trace in enumerate(seg):
        trace = trace - trace.mean()
        trace = trace / (np.percentile(np.abs(trace), 99) + 1e-12)
        t = np.linspace(0, 1, trace.size)
        xs, ys, s = along_curve(t * 6.0, trace * 0.26, per)
        pts.append(np.stack([xs / 6.0, r + ys], 1))
    pts = np.concatenate(pts)
    # x is the place along the trace (0..1): the page scrolls it.
    out = np.empty((len(pts), 2))
    out[:, 0] = pts[:, 0] * 2 - 1
    out[:, 1] = (pts[:, 1] - (len(picks) - 1) / 2) / (len(picks) / 2) * 0.9
    return out, np.full(len(out), 0.8)


def form_meg(n: int):
    import mne

    info = mne.io.read_info(SAMPLE / "meg" / "task-rest_meg.fif", verbose=False)
    chs = [c for c in info["chs"] if c["kind"] == 1]
    locs = np.array([c["loc"][:3] for c in chs])
    locs, first = np.unique(np.round(locs, 4), axis=0, return_index=True)
    centre = locs.mean(0)
    v = locs - centre
    # Each sensor: a small square in the plane of the helmet at that place.
    per = max(8, int(n * 0.78) // len(v))
    squares = []
    for p in v:
        nrm = p / np.linalg.norm(p)
        a = np.cross(nrm, [0, 0, 1.0])
        if np.linalg.norm(a) < 1e-6:
            a = np.array([1.0, 0, 0])
        a /= np.linalg.norm(a)
        b = np.cross(nrm, a)
        t = RNG.random(per) * 4
        side = t.astype(int)
        f = t - side
        h = 0.011
        u = np.where(side == 0, -h + 2 * h * f, np.where(side == 1, h, np.where(side == 2, h - 2 * h * f, -h)))
        w = np.where(side == 0, -h, np.where(side == 1, -h + 2 * h * f, np.where(side == 2, h, h - 2 * h * f)))
        squares.append(p + u[:, None] * a + w[:, None] * b)
    pts = np.concatenate(squares)
    # A faint helmet surface between them.
    m = n - len(pts)
    pick = RNG.integers(0, len(v), m)
    jitter = RNG.normal(0, 0.012, (m, 3))
    surf = v[pick] + jitter
    surf = surf / np.linalg.norm(surf, axis=1, keepdims=True) * np.linalg.norm(v[pick], axis=1, keepdims=True) * 0.985
    pts = np.concatenate([pts, surf])
    val = np.concatenate([np.full(n - m, 0.95), np.full(m, 0.25)])
    # Device axes: x right, y front, z up. Page: x right, y down, z to viewer.
    xyz = np.stack([pts[:, 0], -pts[:, 2], pts[:, 1]], 1)
    return unit(xyz), val


def form_physio(n: int):
    """The ECG and the breathing recorded with the BOLD run, band-passed the
    way the signal viewer's filter would show them."""
    import pandas as pd
    from scipy.signal import butter, filtfilt

    spec = [("ecg", 400.0, (1.0, 30.0), 30, 8.0, 0.6), ("respiratory", 50.0, (0.05, 1.0), 30, 20.0, 0.4)]
    pts = []
    for r, (name, sf, (lo, hi), start, span, share) in enumerate(spec):
        path = CONVERTED / "func" / f"sub-001_ses-01_task-rest_recording-{name}_physio.tsv.gz"
        y = pd.read_csv(path, sep="\t", header=None).iloc[:, 0].interpolate(limit_direction="both").to_numpy(float)
        b, a = butter(2, [lo / (sf / 2), hi / (sf / 2)], "band")
        y = filtfilt(b, a, y)[int(start * sf):int((start + span) * sf)]
        y = (y - np.median(y)) / (np.percentile(np.abs(y), 99.5) + 1e-12)
        t = np.linspace(0, 1, y.size)
        xs, ys, _ = along_curve(t * 8.0, y * 0.42, int(n * share))
        pts.append(np.stack([xs / 8.0, r * 1.25 + ys], 1))
    pts = np.concatenate(pts)
    out = np.empty((len(pts), 2))
    out[:, 0] = pts[:, 0] * 2 - 1
    out[:, 1] = (pts[:, 1] - 0.62) / 1.25
    return out, np.full(len(out), 0.85)


def form_eye(n: int):
    """A scanpath: fixations (by dispersion) sized by duration, joined by saccades."""
    import eyelinkio

    e = eyelinkio.read_edf(str(SAMPLE / "eyetracking" / "task-rest_eyetracking.edf"))
    names = e["info"]["sample_fields"]
    sf = e["info"]["sfreq"]
    x = e["samples"][names.index("xpos_right")].astype(float)
    y = e["samples"][names.index("ypos_right")].astype(float)
    ok = np.isfinite(x) & np.isfinite(y) & (x > 0) & (x < 1920) & (y > 0) & (y < 1080)
    t = np.arange(len(x)) / sf
    x, y, t = x[ok], y[ok], t[ok]
    # Fixations by dispersion, never across a gap in the valid samples.
    fix, i, win = [], 0, int(0.08 * sf)
    disp = lambda a_, b_: (np.ptp(x[a_:b_]) + np.ptp(y[a_:b_]))  # noqa: E731
    while i + win < len(x):
        j = i + win
        if t[j] - t[i] > 0.2:
            i += 1
            continue
        if disp(i, j) <= 80:
            while j < len(x) and disp(i, j + 1) <= 80 and t[j + 1] - t[j] < 0.05:
                j += 1
            fix.append([x[i:j].mean(), y[i:j].mean(), t[j - 1] - t[i]])
            i = j
        else:
            i += 1
    # Neighbouring fixations at one place are one.
    merged = []
    for fx in fix:
        if merged and np.hypot(fx[0] - merged[-1][0], fx[1] - merged[-1][1]) < 60:
            merged[-1][2] += fx[2]
        else:
            merged.append(list(fx))
    fix = np.array(merged[:16])
    dur = fix[:, 2] / fix[:, 2].sum()
    k_fix = int(n * 0.55)
    counts = np.maximum(6, np.round(dur * k_fix).astype(int))
    blobs, order = [], []
    for idx, ((fx, fy, d), c) in enumerate(zip(fix, counts)):
        rad = 10 + 34 * np.sqrt(d)
        ang = RNG.random(c) * 2 * np.pi
        rr = rad * np.sqrt(RNG.random(c))
        blobs.append(np.stack([fx + rr * np.cos(ang), fy + rr * np.sin(ang)], 1))
        order.append(np.full(c, idx / len(fix)))
    path = fix[:, :2]
    seg = np.diff(path, axis=0)
    lengths = np.hypot(seg[:, 0], seg[:, 1])
    cum = np.concatenate([[0], np.cumsum(lengths)])
    m = n - sum(len(bb) for bb in blobs)
    t = np.sort(RNG.random(max(m, 0))) * cum[-1]
    i = np.clip(np.searchsorted(cum, t, side="right") - 1, 0, len(seg) - 1)
    f = ((t - cum[i]) / lengths[i])[:, None]
    lines = path[i] + seg[i] * f
    pts = np.concatenate(blobs + [lines])[: int(n * 0.86)]
    val = np.concatenate(order + [(i + f[:, 0]) / len(fix)])[: len(pts)]
    # The edge of the screen the participant looked at, faint.
    k = n - len(pts)
    u = RNG.random(k) * 2 * (1920 + 1080)
    fx = np.where(u < 1920, u, np.where(u < 3000, 1920, np.where(u < 4920, 4920 - u, 0)))
    fy = np.where(u < 1920, 0, np.where(u < 3000, u - 1920, np.where(u < 4920, 1080, 6000 - u)))
    frame = np.stack([fx, fy], 1) + RNG.normal(0, 2, (k, 2))
    pts = np.concatenate([pts, frame])
    # The path's place in time (0 to 0.95) lights the gaze along it; 1 is the frame.
    val = np.concatenate([np.clip(val, 0, 1) * 0.95, np.full(k, 1.0)])
    return unit(pts), val


def _logo() -> Path:
    """BIDS Manager's own logo, from the installed package (run with the
    environment that has bidsmgr, as the capture tools are)."""
    import bidsmgr

    return Path(bidsmgr.__file__).resolve().parent / "gui" / "assets" / "logo.png"


def emblem(n: int):
    """BIDS Manager's own mark as particles: the folder's outline and the
    brain's folds, read from the application's logo. The value is the
    horizontal position, so the page can colour it like the app icon (violet
    on the left to green on the right)."""
    from PIL import Image
    im = np.asarray(Image.open(_logo()).convert("RGBA"), float) / 255
    alpha = im[..., 3]
    lum = im[..., :3].mean(-1)
    dark = (alpha > 0.5) & (lum < 0.5)          # the folder (black)
    light = (alpha > 0.5) & (lum >= 0.5)        # the brain (white, inside the folder)
    def edges(mask):
        m = mask.astype(np.int8)
        e = np.zeros_like(mask)
        e[1:, :] |= m[1:, :] != m[:-1, :]
        e[:, 1:] |= m[:, 1:] != m[:, :-1]
        return e & mask
    outline = edges(dark | light)               # the folder's silhouette
    folds = edges(light)                        # the brain and its folds
    w = outline.astype(float) * 1.0 + folds.astype(float) * 1.6
    pts, _ = sample_image(w, n)
    pts += RNG.normal(0, 0.35, pts.shape)
    pts = unit(pts)
    val = (pts[:, 0] - pts[:, 0].min()) / np.ptp(pts[:, 0])
    return pts, val


def card(path: Path, before: Path, rows):
    """A sidecar as the hero shows it: each field's value as the dataset holds
    it, where it came from, and the placeholder it replaced if it was answered."""
    now = json.loads(path.read_text())
    then = json.loads(before.read_text()) if before.is_file() else {}
    out = []
    for key, src in rows:
        v = now.get(key)
        if v is None:
            continue
        item = {"key": key, "value": v, "src": src}
        if src == "you" and then.get(key) == "TODO" and v != "TODO":
            item["was"] = "TODO"
        if v == "TODO":
            item["src"] = "todo"
        out.append(item)
    return {"file": path.name, "rows": out}


def dataset() -> dict:
    """The dataset the hero assembles: real names and real sidecar values from
    the course's sample, after its metadata was answered (chapters 7 and 10)."""
    edited = CONVERTED
    converted = Path("/private/tmp/bm_docs/states/converted/multimodal_study/sub-001/ses-01")
    p = "sub-001_ses-01_"
    tree = [
        {"k": 7, "branch": "", "folder": "", "name": "multimodal_study/", "cls": "root"},
        {"k": 7, "branch": "├── ", "folder": "", "name": "dataset_description.json", "more": "participants.tsv  README", "cls": "top"},
        {"k": 7, "branch": "└── ", "folder": "", "name": "sub-001/ses-01/", "cls": "top"},
        {"k": 0, "branch": "    ├── ", "folder": "anat/", "name": p + "acq-tfl3p2_T1w.nii.gz", "json": True, "card": "anat"},
        {"k": 0, "branch": "    ├── ", "folder": "func/", "name": p + "task-rest_bold.nii.gz", "json": True, "card": "bold"},
        {"k": 0, "branch": "    │   ", "folder": "", "name": p + "task-rest_sbref.nii.gz", "json": True},
        {"k": 5, "branch": "    │   ", "folder": "", "name": p + "task-rest_recording-ecg_physio.tsv.gz", "json": True},
        {"k": 0, "branch": "    ├── ", "folder": "fmap/", "name": p + "acq-fm2_phasediff.nii.gz", "json": True},
        {"k": 0, "branch": "    ├── ", "folder": "dwi/", "name": p + "acq-epb0p2_dir-AP_dwi.nii.gz", "more": ".bval .bvec", "json": True},
        {"k": 2, "branch": "    ├── ", "folder": "pet/", "name": p + "pet.nii.gz", "json": True, "card": "pet"},
        {"k": 1, "branch": "    ├── ", "folder": "mrs/", "name": p + "svs.nii.gz", "json": True},
        {"k": 3, "branch": "    ├── ", "folder": "eeg/", "name": p + "task-rest_eeg.edf", "more": "_channels.tsv _events.tsv", "json": True, "card": "eeg"},
        {"k": 4, "branch": "    ├── ", "folder": "meg/", "name": p + "task-rest_meg.fif", "more": "_channels.tsv", "json": True},
        {"k": 6, "branch": "    └── ", "folder": "beh/", "name": p + "task-rest_recording-eye1_physio.tsv.gz", "json": True, "card": "eye"},
    ]
    specs = {
        "bold": ("func/" + p + "task-rest_bold.json",
                 [("TaskName", "bm"), ("RepetitionTime", "file"), ("EchoTime", "file"), ("PhaseEncodingDirection", "file"),
                  ("B0FieldSource", "bm"), ("TaskDescription", "you"), ("Instructions", "you"), ("CogAtlasID", "you")]),
        "anat": ("anat/" + p + "acq-tfl3p2_T1w.json",
                 [("Manufacturer", "file"), ("ManufacturersModelName", "file"), ("MagneticFieldStrength", "file"),
                  ("RepetitionTime", "file"), ("InversionTime", "file"), ("EchoTime", "file"), ("FlipAngle", "file")]),
        "pet": ("pet/" + p + "pet.json",
                [("TracerName", "file"), ("TracerRadionuclide", "file"), ("InjectedRadioactivity", "file"),
                 ("InjectedMass", "you"), ("SpecificRadioactivity", "you"), ("ModeOfAdministration", "you"),
                 ("TimeZero", "bm"), ("FrameDuration", "file")]),
        "eeg": ("eeg/" + p + "task-rest_eeg.json",
                [("TaskName", "bm"), ("SamplingFrequency", "file"), ("EEGChannelCount", "file"),
                 ("RecordingDuration", "file"), ("CapManufacturer", "you")]),
        "eye": ("beh/" + p + "task-rest_recording-eye1_physio.json",
                [("PhysioType", "bm"), ("SamplingFrequency", "file"), ("Manufacturer", "file"), ("RecordedEye", "file"),
                 ("SampleCoordinateSystem", "bm"), ("Columns", "bm")]),
    }
    cards = {}
    for key, (rel, rows) in specs.items():
        cards[key] = card(edited / rel, converted / rel, rows)
    return {"root": "multimodal_study/", "tree": tree, "cards": cards, "order": ["bold", "anat", "pet", "eeg", "eye"]}


# ---------------------------------------------------------------------- main
def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    builders = {"mri": form_mri, "mrs": form_mrs, "pet": form_pet, "eeg": form_eeg,
                "meg": form_meg, "physio": form_physio, "eye": form_eye}
    xs, ys, zs, kinds, vals = [], [], [], [], []
    header_kinds = []
    for k, spec in enumerate(KINDS):
        res = builders[spec["id"]](spec["n"])
        labels = []
        if len(res) == 3:
            pts, val, labels = res
        else:
            pts, val = res
        pts = np.asarray(pts, float)
        z = pts[:, 2] if pts.shape[1] == 3 else np.zeros(len(pts))
        xs.append(pts[:, 0]); ys.append(pts[:, 1]); zs.append(z)
        kinds.append(np.full(len(pts), k)); vals.append(val)
        header_kinds.append({kk: spec[kk] for kk in ("id", "name", "suffix", "folder", "file")}
                            | {"n": int(len(pts)), "solid": bool(pts.shape[1] == 3), "labels": labels})
        print(f"{spec['id']:7s} {len(pts):6d} points")
    ep, ev = emblem(EMBLEM_N)
    xs.append(ep[:, 0]); ys.append(ep[:, 1]); zs.append(np.zeros(len(ep)))
    kinds.append(np.full(len(ep), len(KINDS))); vals.append(ev)
    x = np.concatenate(xs); y = np.concatenate(ys); z = np.concatenate(zs)
    kind = np.concatenate(kinds).astype(np.uint8)
    val = np.clip(np.concatenate(vals), 0, 1)
    perm = RNG.permutation(len(kind))
    x, y, z, kind, val = x[perm], y[perm], z[perm], kind[perm], val[perm]
    seed = RNG.integers(0, 256, len(kind), dtype=np.uint8)
    ds = dataset()
    header = {"version": 3, "n": int(len(kind)), "kinds": header_kinds,
              "emblem": {"n": EMBLEM_N}, "dataset": ds}
    (SITE / "data" / "hero.json").write_text(json.dumps(ds, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    blob = json.dumps(header, separators=(",", ":")).encode()
    pad = (-(4 + len(blob))) % 4
    i16 = lambda a: np.clip(np.round(a * 32000), -32767, 32767).astype("<i2")  # noqa: E731
    with open(OUT / "hero.bin", "wb") as fh:
        fh.write(struct.pack("<I", len(blob) + pad))
        fh.write(blob + b" " * pad)
        fh.write(i16(x).tobytes()); fh.write(i16(y).tobytes())
        fh.write(np.clip(np.round(z * 127), -127, 127).astype("i1").tobytes())
        fh.write(kind.tobytes()); fh.write(seed.tobytes())
        fh.write(np.round(val * 255).astype(np.uint8).tobytes())
    size = (OUT / "hero.bin").stat().st_size
    print(f"hero.bin {size // 1024} KB ({len(gzip.compress((OUT / 'hero.bin').read_bytes())) // 1024} KB gzipped), {len(kind)} points")
    write_stills(x, y, z, kind, val, header)


#: Layout of the still: the seven forms on an ellipse, the emblem in the
#: middle, as the page draws them before scrolling.
def layout(cx, cy, rx, ry):
    out = []
    for k in range(len(KINDS)):
        a = -np.pi / 2 + k / len(KINDS) * 2 * np.pi
        out.append((cx + rx * np.cos(a), cy + ry * np.sin(a)))
    return out


def write_stills(x, y, z, kind, val, header) -> None:
    W, H = 900.0, 640.0
    centres = layout(W / 2, H / 2 + 6, 318, 228)
    size = 74
    # One pastel palette, the same in both themes (static/css/site.css).
    pastel = ["#9db9ec", "#e6cc7c", "#f2b28a", "#86cfc6", "#bba8ec", "#f0a6a2", "#eeaacd"]
    colours = {"light": pastel, "dark": pastel}
    mark = {"light": ("#b3a6f2", "#a6d9a8"), "dark": ("#b3a6f2", "#a6d9a8")}

    def mix(a, b, t):
        a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
        return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))
    ink = {"light": "#15130f", "dark": "#efebe2"}
    for theme in ("light", "dark"):
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
                 'font-family="JetBrains Mono, ui-monospace, monospace" font-size="11">']
        for k in range(len(KINDS) + 1):
            sel = np.where(kind == k)[0][: 900 if k < len(KINDS) else 700]
            if k < len(KINDS):
                cx, cy = centres[k]
                s = size * (1.15 if header["kinds"][k]["solid"] else 1.0)
            else:
                cx, cy, s = W / 2, H / 2 + 6, 92
            px = cx + x[sel] * s
            py = cy + y[sel] * s
            if k < len(KINDS):
                groups = [(np.ones(len(sel), bool), colours[theme][k])]
            else:  # the app's mark, violet to green from left to right
                groups = [((val[sel] >= b / 4) & (val[sel] < (b + 1) / 4 + (b == 3)), mix(*mark[theme], (b + 0.5) / 4))
                          for b in range(4)]
            op = ".95" if theme == "light" else ".8"
            for m, colour in groups:
                d = "".join(f"M{a:.1f} {b:.1f}h.01" for a, b in zip(px[m], py[m]))
                parts.append(f'<path d="{d}" stroke="{colour}" stroke-opacity="{op}" stroke-width="2" '
                             'stroke-linecap="round" fill="none"/>')
            if k < len(KINDS):
                parts.append(f'<text x="{cx:.0f}" y="{cy + s + 22:.0f}" text-anchor="middle" fill="{ink[theme]}" '
                             f'fill-opacity=".75" letter-spacing="1.5">{KINDS[k]["name"].upper()}</text>')
        parts.append("</svg>")
        (OUT / f"hero-{theme}.svg").write_text("".join(parts), encoding="utf-8")
        print(f"hero-{theme}.svg {(OUT / f'hero-{theme}.svg').stat().st_size // 1024} KB")


if __name__ == "__main__":
    sys.exit(main())

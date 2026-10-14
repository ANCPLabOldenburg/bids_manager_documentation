"""Write ``data/teach.json``: the facts the interactive exercises of the BIDS
chapter use, read from the BIDS schema through BIDS Manager's own adapter.

    environments/bids-manager/bin/python bids_manager_documentation/tools/reference/teach_data.py

- ``kinds``: for a few kinds of file, the entities each may carry in the
  standard's order, which are required, whether each is a label or an index,
  and the folder and extension;
- ``quiz``: file names, each with what BIDS Manager's schema code says of it
  (and the order of its entities against the standard's order);
- ``place``: file names and the folder each belongs in.

Nothing here is written by hand except the choice of examples.
"""

from __future__ import annotations

import json
from pathlib import Path

from bidsmgr import schema

SITE = Path(__file__).resolve().parent.parent.parent

KINDS = [
    ("anat", "T1w", ".nii.gz", "An anatomical T1-weighted image"),
    ("func", "bold", ".nii.gz", "A BOLD run"),
    ("dwi", "dwi", ".nii.gz", "A diffusion run"),
    ("fmap", "epi", ".nii.gz", "A reversed-phase fieldmap"),
    ("pet", "pet", ".nii.gz", "A PET image"),
    ("mrs", "svs", ".nii.gz", "A single-voxel spectrum"),
    ("eeg", "eeg", ".edf", "An EEG recording"),
    ("meg", "meg", ".fif", "An MEG recording"),
]
# Entities the builder offers (the rarer ones the standard allows are left out
# of the exercise, not of the facts: ``allowed`` lists them all).
OFFER = ["subject", "session", "task", "acquisition", "ceagent", "tracer", "direction", "run", "echo", "part"]
EXAMPLE = {"subject": "01", "session": "pre", "task": "rest", "acquisition": "mprage", "ceagent": "gad",
           "tracer": "fdg", "direction": "AP", "run": "1", "echo": "1", "part": "mag"}

QUIZ = [
    ("anat", "sub-01_ses-pre_T1w.nii.gz"),
    ("func", "sub-01_bold.nii.gz"),
    ("anat", "sub-01_run-a_T1w.nii.gz"),
    ("func", "sub-01_run-1_task-rest_bold.nii.gz"),
    ("anat", "sub-01_acq-mp rage_T1w.nii.gz"),
    ("func", "sub-01_task-rest_acq-mb4_bold.nii.gz"),
    ("eeg", "sub-01_task-rest_echo-1_eeg.edf"),
    ("dwi", "sub-01_dir-AP_dwi.nii.gz"),
]
#: What each quiz name teaches, in plain words; the schema's own message is
#: shown beside it.
EXPLAIN = {
    "sub-01_ses-pre_T1w.nii.gz": "Valid: a subject, a session, and the suffix.",
    "sub-01_bold.nii.gz": "A BOLD run must say which task it was.",
    "sub-01_run-a_T1w.nii.gz": "run is an index: a number, not a letter.",
    "sub-01_run-1_task-rest_bold.nii.gz": "Every entity is there, but task must come before run.",
    "sub-01_acq-mp rage_T1w.nii.gz": "A label holds letters and digits only: no space, no underscore, no hyphen.",
    "sub-01_task-rest_acq-mb4_bold.nii.gz": "Valid: acq tells two kinds of BOLD acquisition apart.",
    "sub-01_task-rest_echo-1_eeg.edf": "An EEG recording has no echoes: echo is not allowed there.",
    "sub-01_dir-AP_dwi.nii.gz": "Valid: dir says the phase-encoding direction.",
}

PLACE = [
    ("sub-01_ses-pre_T1w.nii.gz", "T1w"),
    ("sub-01_ses-pre_task-rest_bold.nii.gz", "bold"),
    ("sub-01_ses-pre_dir-PA_epi.nii.gz", "epi"),
    ("sub-01_ses-pre_dwi.bval", "dwi"),
    ("sub-01_ses-pre_task-rest_eeg.edf", "eeg"),
    ("sub-01_ses-pre_trc-FDG_pet.nii.gz", "pet"),
    ("sub-01_ses-pre_svs.nii.gz", "svs"),
]

ORDER = [e for e in schema.entity_order()]


def short(entity: str) -> str:
    """The key as written in a file name (``sub``); the adapter calls it ``name``."""
    return schema.entity_info(entity).name


def verdict(datatype: str, name: str) -> dict:
    problems = [v.message for v in schema.validate_basename(name, datatype)]
    # Order: the standard writes entities in one order; the adapter's check
    # does not test it, so it is tested here against the schema's own order.
    ents = list(schema.name_entities(name).keys())
    keys = {short(e): e for e in ORDER}
    seen = [keys.get(k, k) for k in ents]
    pos = [ORDER.index(e) for e in seen if e in ORDER]
    if pos != sorted(pos):
        problems.append("The entities are not in the standard's order (" + ", ".join(
            short(e) for e in sorted(seen, key=ORDER.index)) + ").")
    return {"datatype": datatype, "name": name, "ok": not problems, "problems": problems,
            "explain": EXPLAIN.get(name, "")}


def main() -> None:
    kinds = []
    for datatype, suffix, ext, label in KINDS:
        allowed = schema.allowed_entities(datatype, suffix)
        required = schema.required_entities(datatype, suffix)
        ents = []
        for e in ORDER:
            if e in allowed:
                info = schema.entity_info(e)
                ents.append({"entity": e, "key": short(e), "name": info.display_name, "format": info.format.name,
                             "pattern": info.format.pattern, "required": e in required, "offer": e in OFFER,
                             "example": EXAMPLE.get(e, "")})
        kinds.append({"datatype": datatype, "suffix": suffix, "extension": ext, "label": label, "entities": ents})
    place = [{"name": n, "folder": list(schema.datatypes_with_suffix(s))} for n, s in PLACE]
    data = {"version": schema.bids_version(), "kinds": kinds, "quiz": [verdict(d, n) for d, n in QUIZ],
            "place": place, "folders": ["anat", "func", "fmap", "dwi", "pet", "mrs", "eeg", "meg", "beh"]}
    (SITE / "data" / "teach.json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for q in data["quiz"]:
        print(("ok   " if q["ok"] else "WRONG"), q["name"], "|", "; ".join(q["problems"]))
    for p in place:
        print(p["name"], "->", p["folder"])


if __name__ == "__main__":
    main()
